# Habitory — Smart Habit Tracker (Flask + SQLite + ML)

Notion-like, user-friendly habit tracker with:
- Email & password auth
- Per-user persistent history (like GitHub contributions)
- Monthly calendar (click to mark completions)
- Charts: habit-wise, monthly, weekly
- Rule-based AI insights & notifications
- Statistical metrics (moving averages, consistency)
- Per-user ML model (logistic regression) predicting next-day completion
- Auto-retraining heuristic (every 20 completions)

## Quick start (VS Code)
1. Clone this folder.
2. Create venv:
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
3. Install:
pip install -r requirements.txt

4. Initialize DB (first run of app will create DB automatically using migrations/schema.sql). Or run:


sqlite3 habit_tracker.db < migrations/schema.sql

5. Run:


python app.py

6. Open http://127.0.0.1:5000 — register and use the app.

## Notes
- Models are stored in `models/` as `user_{id}_model.pkl`.
- Trainer CLI: `python -m ai_engine.trainer <user_id>` to force training.
- To deploy: replace SQLite with PostgreSQL (change `database.py`), set secret key, and use a production WSGI server.

## What I delivered
- Full-stack app with multi-user functionality
- UI (Notion-like style) and charts
- AI engine: rule-based + statistical + ML predictive
- Everything ready to push to GitHub

