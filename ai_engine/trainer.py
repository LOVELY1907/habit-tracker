# ai_engine/trainer.py
"""
Trainer utility to build features from completions for a user and train logistic regression
Features (example):
- day_of_week (0-6)
- recent_7day_completion_rate
- habit_weekly_avg
- streak_length
Target:
- whether the habit was completed the NEXT DAY (binary)
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from ai_engine.ml_model import train_model_for_user, model_path_for
import os

DB = 'habit_tracker.db'

def build_user_dataset(user_id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # load habits
    cur.execute('SELECT id FROM habits WHERE user_id = ?', (user_id,))
    habits = [r['id'] for r in cur.fetchall()]
    # load completions (date strings)
    cur.execute('SELECT habit_id, date FROM completions WHERE user_id = ?', (user_id,))
    rows = cur.fetchall()
    comp = {}
    for r in rows:
        comp.setdefault(r['date'], set()).add(r['habit_id'])
    # flatten into rows per habit-date
    all_dates = sorted(comp.keys())
    rows_out = []
    for i, d in enumerate(all_dates):
        for hid in habits:
            done = 1 if hid in comp.get(d, set()) else 0
            # compute recent 7-day completion rate for this habit (including this day)
            prev7 = []
            for j in range(7):
                idx = i - j
                if idx < 0: break
                dt = all_dates[idx]
                prev7.append(1 if hid in comp.get(dt, set()) else 0)
            recent7 = sum(prev7)/len(prev7) if prev7 else 0
            # day of week
            dow = datetime.strptime(d, '%Y-%m-%d').weekday()
            # streak (consecutive days up to this day)
            streak = 0
            k = i
            while k >= 0 and hid in comp.get(all_dates[k], set()):
                streak += 1
                k -= 1
            rows_out.append({'date': d, 'habit_id': hid, 'done': done, 'recent7': recent7, 'dow': dow, 'streak': streak})
    df = pd.DataFrame(rows_out)
    conn.close()
    return df

def prepare_features_and_target(df):
    # target is next-day completion for same habit
    df = df.sort_values(['habit_id','date'])
    df['next_done'] = df.groupby('habit_id')['done'].shift(-1)
    df = df.dropna(subset=['next_done'])
    X = df[['recent7','dow','streak']].copy()
    # one-hot encode dow
    X = pd.get_dummies(X, columns=['dow'], prefix='dow')
    y = df['next_done'].astype(int)
    return X, y

def train_for_user(user_id):
    df = build_user_dataset(user_id)
    if df.empty:
        return None
    X, y = prepare_features_and_target(df)
    path = train_model_for_user(user_id, X, y)
    return path

if __name__ == '__main__':
    # quick CLI
    import sys
    if len(sys.argv) < 2:
        print("Usage: python trainer.py <user_id>")
        sys.exit(1)
    uid = int(sys.argv[1])
    p = train_for_user(uid)
    if p:
        print("Trained model:", p)
    else:
        print("Not enough data to train")
