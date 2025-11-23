# ai_engine/rules.py
from datetime import date, timedelta
from collections import defaultdict

def generate_notifications(db, user_id, habits, completions_map):
    """
    Simple rule-based notifications for a user.
    completions_map: dict date->set(habit_id)
    habits: list of dicts {id, name}
    """
    notes = []
    today = date.today()
    # missed habit for last 3 days
    for h in habits:
        hid = h['id']
        missing = 0
        hist_count = 0
        # check last 14 days for history
        for i in range(1, 15):
            d = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            if hid in completions_map.get(d, set()):
                hist_count += 1
        # check recent 3 days
        for i in range(1,4):
            d = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            if hid not in completions_map.get(d, set()):
                missing += 1
        if missing >= 3 and hist_count > 0:
            notes.append({
                'type': 'missed_habit',
                'message': f"You missed '{h['name']}' for {missing} days. Try making it smaller (5 min) or set a reminder."
            })
    # low consistency
    # compute overall percent
    all_dates = sorted(completions_map.keys())
    if all_dates and habits:
        total_possible = len(all_dates) * len(habits)
        total_done = sum(len(completions_map[d]) for d in all_dates)
        overall = int((total_done/total_possible)*100) if total_possible else 0
        if overall < 40:
            notes.append({'type':'low_consistency', 'message': f"Consistency is low this period ({overall}%). Try focusing on 2-3 habits."})
    return notes
