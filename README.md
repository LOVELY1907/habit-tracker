# 🧠 Smart Habit Tracker
### Modern, AI-powered habit tracking with monthly snapshots, insights & predictions

A clean, fast, intelligent habit tracking web app built using **Python (Flask)**, **SQLite**, and **Vanilla JS**, featuring:

✔ Month-isolated habit tracking  
✔ Smart AI predictions  
✔ Notifications for missed habits  
✔ Auto-generated insights  
✔ Clean Notion-style UI  
✔ Secure user accounts  
✔ Full habit history stored forever  
✔ Mobile-friendly UI  
✔ Works offline once loaded (PWA-ready)

---

## 🌟 Features

### 🔐 User Accounts  
Users can register/login via email + password. Passwords are hashed using **PBKDF2-SHA256**.

---

### 📅 Monthly Snapshot Habit Tracking  
- Every month starts **fresh**  
- Habits added in November stay in **November**  
- December starts **empty** until you add new habits  
- Your history is preserved forever using the `habit_snapshots` system  
- Enables proper month-to-month comparison  

---

### 🗓 Interactive Calendar  
- Clickable calendar like Notion  
- Mark habits daily  
- Real-time updates  
- Smooth navigation between months  

---

### 📊 Statistics & Graphs  
Three interactive charts:

- **Habit-wise Progress** (frequency per habit)  
- **Monthly Trend** (daily completion)  
- **Weekly Consistency** (weekly totals)  

Powered by **Chart.js**.

---

### 🤖 AI-Powered Insights  
The system analyzes your performance and gives:

- Top habit of the month  
- Weakest habit  
- Overall monthly percentage  
- Customized recommendations  
- Missed habit alerts  
- “Needs attention” warnings  

---

### 🔮 AI Predictions (Next-day Probability)

Uses a lightweight ML model trained per user:

- Predicts the probability that you will complete each habit tomorrow  
- Features include recent streak, weekday patterns, last 30-day behavior  
- Retrains automatically every ~20 completions  
- Each user has an isolated model  

---

### 🔔 Notifications  
Generated when:

- Habits are neglected  
- Consistency drops  
- Performance declines  
- AI flags unusual activity  

Notifications can be marked as read.

---

## 🧱 Tech Stack<br>
<br>
| Layer | Technology |<br>
|------|------------|<br>
| Backend | Python, Flask |<br>
| Frontend | HTML, CSS, JavaScript |<br>
| Database | SQLite |<br>
| Auth | PBKDF2-SHA256 |<br>
| ML | scikit-learn (Logistic Regression), pandas, numpy |<br>
| Charts | Chart.js |<br>
| UI | Tailwind-style custom CSS |<br>
| Deployment-ready | Gunicorn / Render |<br>

---

## 🗂 Project Structure

habit-tracker/<br>
│<br>
├── app.py # Main Flask app<br>
├── database.py # DB connection helpers<br>
├── habit_tracker.db # SQLite database (auto-created)<br>
│<br>
├── migrations/<br>
│ └── schema.sql # Tables: users, habits, snapshots, notifications, completions<br>
│<br>
├── ai_engine/<br>
│ ├── rules.py # Smart insights & recommendations<br>
│ ├── stats.py # Monthly stats generation<br>
│ ├── ml_model.py # Prediction model loader & inference<br>
│ └── trainer.py # Trains user-specific ML models<br>
│<br>
├── static/<br>
│ ├── dashboard.js # Calendar, charts, predictions, UI logic<br>
│ └── styles.css # Clean UI styling<br>
│<br>
├── templates/<br>
│ ├── layout.html # Master layout<br>
│ ├── dashboard.html # Calendar + charts + AI insights<br>
│ ├── login.html<br>
│ └── register.html<br>
│<br>
├── init_db.py # (Optional) Script to reset/initialize DB<br>
└── README.md # This file<br>


---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
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


This creates habit_tracker.db using migrations/schema.sql.

5️⃣ Run the app
python app.py


Open:
👉 http://127.0.0.1:5000/

🔧 Development Tools
Reset Database (dev only)
Invoke-RestMethod -Uri http://127.0.0.1:5000/admin/reset-db -Method POST -Headers @{ "X-ADMIN-TOKEN" = "dev-token" }

Download a DB backup
http://127.0.0.1:5000/admin/download-db?token=dev-token


⚠ Remove admin endpoints before deploying publicly.

🧪 ML Model Details

Algorithm: Logistic Regression

Features:

Last 7-day consistency

Day-of-week (one-hot encoded)

Current streak length

Retrains every 20 completions

Each user has an isolated model in ml_models/

🛡 Security

Passwords hashed using PBKDF2-SHA256

Session-based authentication

No data leaked across users

Monthly snapshots ensure history is immutable

Add habit_tracker.db to .gitignore (do not push to GitHub)

📸 Screenshots (Add images here)
[ Add screenshots of dashboard, calendar, charts, AI insights, login page ]

🌍 Future Enhancements

Dark mode

PWA (installable mobile/desktop app)

AI-based habit suggestions

Weekly/monthly PDF reports

Social accountability groups

Google login

📝 License

This project is licensed under the MIT License.

💛 Author

Lovely Pavithra G
💌 lovely.g1907@gmail.com

🧠 Cybersecurity • AI/ML • Web Developer

If you like this project, ⭐ star the repository!

