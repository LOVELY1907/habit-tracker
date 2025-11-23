🧠 Smart Habit Tracker
Modern, AI-powered habit tracking with monthly snapshots, insights & predictions

A clean, fast, intelligent habit tracking web app built using Python (Flask), SQLite, and Vanilla JS, featuring:

✔ Month-isolated habit tracking
✔ Smart AI predictions
✔ Notifications for missed habits
✔ Auto-generated insights
✔ Clean Notion-style UI
✔ Secure user accounts
✔ Full habit history stored forever
✔ Mobile-friendly UI
✔ Works offline once loaded (PWA-ready)

🌟 Features
🔐 User Accounts

Users can register/login via email + password. Passwords are hashed using PBKDF2-SHA256.

📅 Monthly Snapshot Habit Tracking

Every month starts fresh.

Habits added in November stay in November; December is empty until the user adds new habits.

Monthly history is preserved permanently through the habit_snapshots system.

Allows accurate month-to-month comparison.

🗓 Interactive Calendar

Clickable calendar like Notion.

Check off habits for each day.

Real-time updates.

Smooth navigation between months.

📊 Statistics & Graphs

Three interactive charts:

Habit-wise Progress (frequency per habit)

Monthly Trend (daily completion)

Weekly Consistency (weekly totals)

All charts are powered by Chart.js.

🤖 AI-Powered Insights

The system analyzes your performance and gives:

Top habit of the month

Weakest habit

Overall monthly percentage

Customized recommendations

Missed habit alerts

“Needs attention” notifications

🔮 AI Predictions (Next-day Probability)

Using a lightweight ML model trained per user:

Predicts the probability that you will complete each habit tomorrow

Builds features like recent streak, weekday behavior, last 30-day pattern

Works per-user and auto-re-trains every ~20 completions

🔔 Notifications

The system generates notifications when:

A habit is neglected for several days

Consistency is low

Performance drops

AI flags something important

Users can mark notifications as read.

🧱 Tech Stack
Layer	Technology
Backend	Python, Flask
Frontend	HTML, CSS, JavaScript
Database	SQLite
Auth	PBKDF2-SHA256
ML	scikit-learn (Logistic Regression), pandas, numpy
Charts	Chart.js
UI	Tailwind-style custom CSS
Deployment-ready	Gunicorn / Render
🗂 Project Structure
habit-tracker/
│
├── app.py                # Main Flask app
├── database.py           # DB connection helpers
├── habit_tracker.db      # SQLite database (auto-created)
│
├── migrations/
│   └── schema.sql        # Tables: users, habits, snapshots, notifications, completions
│
├── ai_engine/
│   ├── rules.py          # Smart insights & recommendations
│   ├── stats.py          # Monthly stats generation
│   ├── ml_model.py       # Prediction model loader & inference
│   └── trainer.py        # Trains user-specific ML models
│
├── static/
│   ├── dashboard.js      # Calendar, charts, predictions, UI logic
│   └── styles.css        # Clean UI styling
│
├── templates/
│   ├── layout.html       # Master layout
│   ├── dashboard.html    # Calendar + charts + AI insights  
│   ├── login.html
│   └── register.html
│
├── init_db.py            # (Optional) Script to reset/initialize DB
└── README.md             # This file

🚀 Getting Started
1️⃣ Clone the repository
git clone https://github.com/<your-username>/smart-habit-tracker.git
cd smart-habit-tracker

2️⃣ Create a virtual environment
python -m venv venv


Activate:

Windows:

venv\Scripts\Activate.ps1


Mac/Linux:

source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Initialize the database
python init_db.py


This creates habit_tracker.db from migrations/schema.sql.

5️⃣ Run the app
python app.py


Open:
👉 http://127.0.0.1:5000/

🔧 Development Tools
Reset Database (dev only)
Invoke-RestMethod -Uri http://127.0.0.1:5000/admin/reset-db -Method POST -Headers @{ "X-ADMIN-TOKEN" = "dev-token" }

Download a DB backup
http://127.0.0.1:5000/admin/download-db?token=dev-token


(Remove before deploying.)

🧪 ML Model Details

Logistic Regression classifier

Features per habit:

Last 7-day consistency

Day-of-week one-hot encoded

Streak length

Model retrains after every 20 completions

Each user has an isolated model in ml_models/

🛡 Security

Password hashing using PBKDF2-SHA256

Session-based authentication

No habit data leaked between users

Snapshots ensure history cannot mutate

Database file excluded from Git (add habit_tracker.db to .gitignore)

📸 Screenshots (Add your images here)
[ Add screenshots of dashboard, calendar, charts, AI insights, login page ]

🌍 Future Enhancements

Dark mode

PWA mobile app version

AI-based habit suggestions

Weekly/monthly PDF reports

Social accountability groups

Google login

📝 License

This project is licensed under the MIT License.

💛 Author

Lovely Pavithra G
💌 lovely.g1907@gmail.com

🧠 Cybersecurity + AI/ML + Web Developer

If you like this project, ⭐ star the repository!
