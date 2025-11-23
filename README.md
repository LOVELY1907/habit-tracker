🌿 Habitory — Smart Habit Tracker
A Notion-style, AI-powered habit tracking web app (Flask + SQLite + ML)

Habitory is a full-stack, multi-user habit tracking system built with Python, Flask, SQLite, and real AI insights.
Users can create habits, track progress on an interactive GitHub-like calendar, view analytics, and even receive predictive ML suggestions based on their past behavior.

This project demonstrates backend development, frontend development, machine learning, database design, authentication, UX design, and system architecture — making it a strong portfolio addition.

🚀 Features
✅ User Accounts

Register, login, logout (email + password)

Secure password hashing (Werkzeug)

Fully isolated user data

✅ Notion-Style UI

Clean, modern interface built with Tailwind CSS

Soft colors, large spacing, smooth layout

✅ Habit Tracking

Add / rename / delete habits

Track daily completions

GitHub-style contribution calendar

Unlimited history (stored forever)

✅ Analytics & Insights

Habit-wise progress chart

Monthly activity trends

Weekly consistency graph

Overall performance score

AI recommendations

✅ AI Engine (3 levels)
A) Rule-based AI

Missed-habit alerts

Low consistency alerts

Habit suggestions

B) Statistical AI

Weekly averages

Moving completion rate

Custom “habit health score”

C) Machine Learning Predictions

Per-user ML model (Logistic Regression)

Predicts probability of completing each habit tomorrow

Model auto-trains every 20 completions

Stored per-user in /models/user_{id}.pkl

✅ Notifications System

Stored per user

Notion-style reminder cards

Mark-as-read

🏗 Tech Stack
Backend

Python 3

Flask

SQLite

scikit-learn

Pandas

Werkzeug security

Frontend

HTML (Jinja templates)

Tailwind CSS

Vanilla JavaScript

Chart.js

📁 Folder Structure
habit-tracker/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── migrations/
│   └── schema.sql
│
├── ai_engine/
│   ├── rules.py
│   ├── stats.py
│   ├── ml_model.py
│   └── trainer.py
│
├── models/
│   └── (generated ML models)
│
├── static/
│   ├── styles.css
│   └── dashboard.js
│
└── templates/
    ├── layout.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── calendar.html (optional)

⚙️ Setup Instructions
1. Clone the repository
git clone https://github.com/<your-username>/habit-tracker.git
cd habit-tracker

2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # Mac / Linux
# venv\Scripts\activate        # Windows

3. Install dependencies
pip install -r requirements.txt

4. Initialize the database

(First run will auto-create habit_tracker.db, but you can initialize manually too.)

sqlite3 habit_tracker.db < migrations/schema.sql

5. Run the server
python app.py

6. Open in browser
http://127.0.0.1:5000

🔮 Machine Learning Model

Each user gets their own ML model trained on their historical completions.

When does training happen?

Automatically every 20 new habit completions

Can also be manually triggered:

python -m ai_engine.trainer <user_id>

What does the ML model predict?

Probability that a user will complete each habit tomorrow

Used to generate:

“probability_next_day”

Personalized habit suggestions

Predictive analytics

🌟 Why This Project Matters

This is not a todo list or a basic CRUD app.
It's a full production-style system showing:

✔ Authentication
✔ Database design
✔ AI integration
✔ ML model training + prediction
✔ Real user retention logic
✔ A polished Notion-inspired UI
✔ State management with API calls
✔ Chart visualizations
✔ Clean code and folder structure

This is exactly the type of project that impresses:

Recruiters

Professors

Internship panels

Hackathon judges

And it shows you can build complete, AI-driven systems.

🛠 Future Improvements

(You can add these as GitHub “Issues”)

Dark mode

Push notifications

Mobile-first redesign

Streak calendar with color intensity

Habit categories & tags

Google login (OAuth)

PostgreSQL migration for deployment

Docker support

Background ML training scheduler

🤝 Contributing

Pull requests are welcome.
Feel free to open issues for ideas or improvements.

📜 License

MIT License.

🎉 Made with ❤️ using Python & Flask

If you want, I can also generate:

A GitHub banner image

A GIF preview

A feature screenshot pack

A short LinkedIn post description

A professional project summary for your resume
