# app.py
import os
import sqlite3
import threading
from datetime import datetime, date, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, close_db
from ai_engine import rules, stats, ml_model
from ai_engine.trainer import train_for_user

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)

# Make sure DB connection closes at end of request
app.teardown_appcontext(close_db)


# ---------- Helpers ----------
def login_user(user_row):
    session['user_id'] = user_row['id']
    session['email'] = user_row['email']


def logout_user():
    session.pop('user_id', None)
    session.pop('email', None)


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    db = get_db()
    row = db.execute('SELECT id, email, created_at FROM users WHERE id = ?', (uid,)).fetchone()
    return row


def iso_today():
    return date.today().strftime('%Y-%m-%d')


def get_month_dates(year, month):
    first = date(year, month, 1)
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    dates = []
    d = first
    while d <= last:
        dates.append(d.strftime('%Y-%m-%d'))
        d += timedelta(days=1)
    return dates


# ------------------------------
# Snapshot helpers (month-isolated behavior)
# ------------------------------
def month_str_from_year_month(year, month):
    return f"{year}-{int(month):02d}"


def ensure_snapshot_for_month(user_id, year, month):
    """
    Ensure a snapshot record exists for (user, month).
    IMPORTANT: We purposely do NOT copy global habits into the new month.
    New months start empty by default. This function is idempotent.
    """
    db = get_db()
    mstr = month_str_from_year_month(year, month)
    row = db.execute('SELECT COUNT(1) as c FROM habit_snapshots WHERE user_id = ? AND month = ?', (user_id, mstr)).fetchone()
    if row and row['c'] > 0:
        return
    # Do NOT copy habits forward. Create no rows for a fresh empty month.
    return


def ensure_snapshot_for_date(user_id, dt_str):
    """
    Ensure snapshot exists for the month of dt_str (YYYY-MM-DD).
    We call this to check snapshot presence; it will not copy habits forward.
    """
    dt = datetime.strptime(dt_str, '%Y-%m-%d').date()
    ensure_snapshot_for_month(user_id, dt.year, dt.month)


# ------------------------------
# AUTH
# ------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pwd = request.form.get('password', '')
        if not email or not pwd:
            return render_template('register.html', error='Email and password required')
        db = get_db()
        exists = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if exists:
            return render_template('register.html', error='Email already registered')
        hashp = generate_password_hash(pwd)
        created = datetime.utcnow().isoformat()
        cur = db.execute('INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)', (email, hashp, created))
        db.commit()
        user_id = cur.lastrowid
        user = db.execute('SELECT id, email FROM users WHERE id = ?', (user_id,)).fetchone()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pwd = request.form.get('password', '')
        db = get_db()
        row = db.execute('SELECT id, email, password_hash FROM users WHERE email = ?', (email,)).fetchone()
        if not row or not check_password_hash(row['password_hash'], pwd):
            return render_template('login.html', error='Invalid credentials')
        login_user(row)
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------- UI routes ----------
@app.route('/')
def home():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = current_user()
    return render_template('dashboard.html', user=user)


# ---------- API endpoints (Habits) ----------
@app.route("/api/habits", methods=["POST"])
def api_add_habit():
    """
    Add a habit:
      - insert into global habits table (so habit_id is stable)
      - insert into current month's habit_snapshots so it shows immediately in this month
    """
    if not session.get("user_id"):
        return jsonify({"error": "unauthenticated"}), 401

    uid = session["user_id"]
    name = (request.json or {}).get("name")
    if not name:
        return jsonify({"error": "no name"}), 400

    db = get_db()

    # Insert into global habits
    cur = db.execute("INSERT INTO habits (user_id, name, created_at) VALUES (?, ?, DATE('now'))", (uid, name))
    hid = cur.lastrowid

    # Add to current month's snapshot only
    month_str = date.today().strftime("%Y-%m")
    db.execute("INSERT INTO habit_snapshots (user_id, habit_id, name_at_that_time, month) VALUES (?, ?, ?, ?)",
               (uid, hid, name, month_str))

    db.commit()
    return jsonify({"success": True, "habit_id": hid})


@app.route("/api/habits/<int:hid>", methods=["DELETE"])
def api_delete_habit(hid):
    """
    Delete a habit from the current month only.
    This DOES NOT delete the global habit row or affect previous months.
    """
    if not session.get("user_id"):
        return jsonify({"error": "unauthenticated"}), 401

    uid = session["user_id"]
    db = get_db()
    month_str = date.today().strftime("%Y-%m")

    db.execute("DELETE FROM habit_snapshots WHERE user_id = ? AND habit_id = ? AND month = ?", (uid, hid, month_str))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/habits/<int:hid>", methods=["PUT"])
def api_rename_habit(hid):
    """
    Rename habit for the current month only (update snapshot name_at_that_time).
    This does NOT alter the global habit name (so past months remain unchanged).
    """
    if not session.get("user_id"):
        return jsonify({"error": "unauthenticated"}), 401

    uid = session["user_id"]
    name = (request.json or {}).get("name")
    if not name:
        return jsonify({"error": "no name"}), 400

    db = get_db()
    month_str = date.today().strftime("%Y-%m")

    # Update only snapshot row for current month
    db.execute("UPDATE habit_snapshots SET name_at_that_time = ? WHERE user_id = ? AND habit_id = ? AND month = ?",
               (name, uid, hid, month_str))
    db.commit()
    return jsonify({"success": True})


# ---- COMPLETIONS API ----
@app.route('/api/completions/toggle', methods=['POST'])
def api_toggle_completion():
    """
    Toggle completion for a habit on a specific date.
    NOTE: This assumes the habit exists in the snapshot for that month. The UI should only display checkboxes for habits present in the month's snapshot.
    """
    if not session.get('user_id'):
        return jsonify({'error': 'unauthenticated'}), 401
    db = get_db()
    uid = session['user_id']
    data = request.get_json() or {}
    hid = data.get('habit_id')
    date_str = data.get('date')
    if not hid or not date_str:
        return jsonify({'error': 'habit_id & date required'}), 400

    # Ensure snapshot for that date's month exists (no copying)
    ensure_snapshot_for_date(uid, date_str)

    # Toggle
    row = db.execute('SELECT id FROM completions WHERE user_id = ? AND habit_id = ? AND date = ?', (uid, hid, date_str)).fetchone()
    if row:
        db.execute('DELETE FROM completions WHERE id = ?', (row['id'],))
        db.commit()
        return jsonify({'status': 'removed'})
    else:
        try:
            db.execute('INSERT INTO completions (user_id, habit_id, date) VALUES (?,?,?)', (uid, hid, date_str))
            db.commit()
        except sqlite3.IntegrityError:
            # Unique constraint may fail if duplicated concurrently
            pass
        # Optionally retrain ML periodically (asynchronous)
        threading.Thread(target=maybe_retrain, args=(uid,)).start()
        return jsonify({'status': 'added'})


def maybe_retrain(user_id):
    # Retrain model every N completions (simple heuristic)
    # Use a direct sqlite connection to avoid app context issues from background thread
    try:
        con = sqlite3.connect('habit_tracker.db')
        c = con.cursor()
        c.execute('SELECT COUNT(*) FROM completions WHERE user_id = ?', (user_id,))
        count = c.fetchone()[0]
        con.close()
        if count >= 20 and count % 20 == 0:
            try:
                train_for_user(user_id)
            except Exception as e:
                print("Retrain failed:", e)
    except Exception as e:
        print("Retrain check error:", e)


# ---- Get month data (habits + completions) using snapshots
@app.route("/api/month/<int:year>/<int:month>")
def api_month(year, month):
    if not session.get('user_id'):
        return jsonify({"error": "unauthenticated"}), 401

    uid = session["user_id"]
    db = get_db()
    month_str = month_str_from_year_month(year, month)

    # Ensure snapshot exists for the month (we intentionally keep it empty if no habits added)
    ensure_snapshot_for_month(uid, year, month)

    # Fetch habits for ONLY this month (from snapshots)
    habits = db.execute("""
        SELECT habit_id AS id, name_at_that_time AS name
        FROM habit_snapshots
        WHERE user_id = ? AND month = ?
        ORDER BY id
    """, (uid, month_str)).fetchall()

    # Fetch completions for ONLY this month
    rows = db.execute("""
        SELECT habit_id, date
        FROM completions
        WHERE user_id = ? AND substr(date,1,7) = ?
    """, (uid, month_str)).fetchall()

    completions = {}
    for r in rows:
        completions.setdefault(r["date"], []).append(r["habit_id"])

    return jsonify({
        "habits": [dict(h) for h in habits],
        "completions": completions
    })


# ---- STATS & INSIGHTS (AI-style) using snapshot habits
@app.route('/api/stats/<int:year>/<int:month>', methods=['GET'])
def api_stats(year, month):
    if not session.get('user_id'):
        return jsonify({'error': 'unauthenticated'}), 401
    uid = session['user_id']
    db = get_db()

    # ensure snapshot exists
    ensure_snapshot_for_month(uid, year, month)
    mstr = month_str_from_year_month(year, month)

    habits = [dict(r) for r in db.execute('SELECT habit_id as id, name_at_that_time as name FROM habit_snapshots WHERE user_id = ? AND month = ? ORDER BY habit_id', (uid, mstr)).fetchall()]
    dates = get_month_dates(year, month)
    rows = db.execute('SELECT habit_id, date FROM completions WHERE user_id = ? AND date BETWEEN ? AND ?', (uid, dates[0], dates[-1])).fetchall()
    comp_map = {}
    for r in rows:
        comp_map.setdefault(r['date'], set()).add(r['habit_id'])
    s = stats.compute_stats(habits, comp_map, dates)

    # generate rule notifications and persist (avoid duplicates)
    notes = rules.generate_notifications(db, uid, habits, comp_map)
    for n in notes:
        exists = db.execute('SELECT 1 FROM notifications WHERE user_id = ? AND message = ?', (uid, n['message'])).fetchone()
        if not exists:
            db.execute('INSERT INTO notifications (user_id, message, created_at) VALUES (?,?,?)', (uid, n['message'], datetime.utcnow().isoformat()))
    db.commit()

    return jsonify({'overall_percent': s['overall_percent'], 'habit_counts': s['habit_counts'], 'daily_totals': s['daily_totals'], 'weekly': s['weekly'], 'habits': habits})


# ---- Notifications endpoints ----
@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    if not session.get('user_id'):
        return jsonify({'error': 'unauthenticated'}), 401
    uid = session['user_id']
    db = get_db()
    rows = db.execute('SELECT id, message, created_at, read FROM notifications WHERE user_id = ? ORDER BY id DESC', (uid,)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/notifications/<int:nid>/read', methods=['POST'])
def api_mark_read(nid):
    if not session.get('user_id'):
        return jsonify({'error': 'unauthenticated'}), 401
    db = get_db()
    uid = session['user_id']
    db.execute('UPDATE notifications SET read = 1 WHERE id = ? AND user_id = ?', (nid, uid))
    db.commit()
    return jsonify({'read': nid})


# ---- ML predict per-habit for "tomorrow"
@app.route('/api/predict/nextday', methods=['GET'])
def api_predict_nextday():
    if not session.get('user_id'):
        return jsonify({'error':'unauthenticated'}), 401
    uid = session['user_id']
    db = get_db()

    # Use the CURRENT MONTH snapshot habits (only habits added for this month)
    today = date.today()
    month_str = today.strftime('%Y-%m')
    habits = [dict(r) for r in db.execute(
        'SELECT habit_id as id, name_at_that_time as name FROM habit_snapshots WHERE user_id = ? AND month = ? ORDER BY habit_id',
        (uid, month_str)).fetchall()]

    # Optional fallback: if there are no snapshot habits for this month, you may
    # want to predict on the global habit list. Uncomment below if desired.
    # if not habits:
    #     habits = [dict(r) for r in db.execute('SELECT id,name FROM habits WHERE user_id = ? ORDER BY id', (uid,)).fetchall()]

    # Build recent stats from last 30 days
    end = date.today()
    start = end - timedelta(days=30)
    rows = db.execute('SELECT habit_id, date FROM completions WHERE user_id = ? AND date BETWEEN ? AND ?', (uid, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))).fetchall()
    comp_map = {}
    for r in rows:
        comp_map.setdefault(r['date'], set()).add(r['habit_id'])

    # Build features and call ml_model (same as before)
    feats = []
    for h in habits:
        hid = h['id']
        # recent7
        recent7 = 0
        for i in range(1,8):
            d = (end - timedelta(days=i-1)).strftime('%Y-%m-%d')
            if hid in comp_map.get(d, set()):
                recent7 += 1
        recent7 = recent7 / 7.0
        # dow tomorrow
        dow = (end + timedelta(days=1)).weekday()
        # streak length
        streak = 0
        k = 0
        while True:
            d = (end - timedelta(days=k)).strftime('%Y-%m-%d')
            if hid in comp_map.get(d, set()):
                streak += 1
                k += 1
            else:
                break
        feats.append({'habit_id': hid, 'recent7': recent7, 'dow': dow, 'streak': streak})

    import pandas as pd
    df = pd.DataFrame(feats)
    df = pd.get_dummies(df, columns=['dow'], prefix='dow')
    for i in range(7):
        col = f'dow_{i}'
        if col not in df.columns:
            df[col] = 0
    cols = ['recent7','streak'] + [f'dow_{i}' for i in range(7)]
    if df.shape[0] == 0:
        # No habits to predict for this month — return empty list
        return jsonify([])

    X = df[cols]
    probs = ml_model.predict_for_user(uid, X)  # your existing model API
    out = []
    for i,h in enumerate(habits):
        p = float(probs[i]) if (probs is not None and i < len(probs)) else None
        out.append({'habit_id': h['id'], 'name': h['name'], 'probability_next_day': p})
    return jsonify(out)

if __name__ == '__main__':
    # if DB missing, create via migrations (get_db will call migration routine)
    if not os.path.exists('habit_tracker.db'):
        with app.app_context():
            get_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

# ---------------------------
# Development admin endpoints
# ---------------------------
import shutil
from flask import send_file

# WARNING: These endpoints are for DEV use only. Remove or protect before deploying.

@app.route('/admin/reset-db', methods=['POST'])
def admin_reset_db():
    """Reset DB: backup existing db then re-run schema to create a fresh DB."""
    # optional protect: require a secret token in POST for minimal safety
    token = request.headers.get('X-ADMIN-TOKEN')
    # set a short token value while developing (or remove check if local dev)
    if token != os.environ.get('HABIT_ADMIN_TOKEN', 'dev-token'):
        return jsonify({'error':'unauthorized'}), 403

    # backup current DB and recreate
    project = os.path.dirname(__file__)
    db_path = os.path.join(project, 'habit_tracker.db')
    backups_dir = os.path.join(project, 'backups')
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)

    if os.path.exists(db_path):
        ts = int(os.path.getmtime(db_path))
        dst = os.path.join(backups_dir, f"habit_tracker.db.bak.{ts}")
        shutil.copy2(db_path, dst)

    # run init_db logic by importing or reading schema
    from init_db import create_db_from_schema
    create_db_from_schema()
    return jsonify({'reset': True})

@app.route('/admin/download-db', methods=['GET'])
def admin_download_db():
    """Download current DB file for local backup."""
    token = request.args.get('token')
    if token != os.environ.get('HABIT_ADMIN_TOKEN', 'dev-token'):
        return jsonify({'error':'unauthorized'}), 403
    project = os.path.dirname(__file__)
    db_path = os.path.join(project, 'habit_tracker.db')
    if not os.path.exists(db_path):
        return jsonify({'error':'db_missing'}), 404
    return send_file(db_path, as_attachment=True, download_name='habit_tracker.db')
