# database.py
import sqlite3, os
from flask import g
DB_PATH = 'habit_tracker.db'
SCHEMA = os.path.join('migrations', 'schema.sql')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        should_init = not os.path.exists(DB_PATH)
        db = g._database = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
        if should_init:
            with open(SCHEMA, 'r') as f:
                db.executescript(f.read())
            db.commit()
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def ensure_snapshot_for_month(user_id, year, month):
    db = get_db()
    month_str = f"{year}-{month:02d}"

    # Check if snapshot exists
    existing = db.execute("""
        SELECT COUNT(*) AS c
        FROM habit_snapshots
        WHERE user_id = ? AND month = ?
    """, (user_id, month_str)).fetchone()["c"]

    if existing > 0:
        return  # snapshot already exists

    # Create EMPTY snapshot → DO NOT COPY ANY HABITS
    # No insert happens here, empty month by default
    return
