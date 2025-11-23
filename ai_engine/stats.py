# ai_engine/stats.py
import numpy as np
from datetime import date, timedelta

def compute_stats(habits, completions_map, view_dates):
    """
    habits: list of dicts {id,name}
    completions_map: dict date->set(habit_id)
    view_dates: list of date strings (YYYY-MM-DD) for the desired period (month)
    returns habit_counts, daily_totals, overall_percent, weekly_scores
    """
    habit_counts = [{ 'id': h['id'], 'name': h['name'], 'count': 0 } for h in habits]
    id_to_idx = { h['id']: i for i,h in enumerate(habits) }
    daily_totals = []
    for d in view_dates:
        s = completions_map.get(d, set())
        daily_totals.append(len(s))
        for hid in s:
            idx = id_to_idx.get(hid)
            if idx is not None:
                habit_counts[idx]['count'] += 1
    total_possible = len(view_dates) * max(1, len(habits))
    total_done = sum(h['count'] for h in habit_counts)
    overall = int((total_done/total_possible)*100) if total_possible else 0
    # weekly: group into chunks of 7
    weekly = []
    for i in range(0, len(daily_totals), 7):
        chunk = daily_totals[i:i+7]
        weekly.append(int((sum(chunk) / (len(chunk) * max(1,len(habits))))*100) if chunk else 0)
    return {'habit_counts': habit_counts, 'daily_totals': daily_totals, 'overall_percent': overall, 'weekly': weekly}
