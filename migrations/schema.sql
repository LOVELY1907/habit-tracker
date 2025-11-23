PRAGMA foreign_keys = ON;

-------------------------------------------------------------------
-- USERS TABLE
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
);

-------------------------------------------------------------------
-- HABITS TABLE
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS habits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-------------------------------------------------------------------
-- COMPLETIONS TABLE (Stores daily checkbox marks)
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  habit_id INTEGER NOT NULL,
  date TEXT NOT NULL,  -- YYYY-MM-DD
  UNIQUE(user_id, habit_id, date),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
);

-------------------------------------------------------------------
-- NOTIFICATIONS TABLE
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL,
  read INTEGER DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-------------------------------------------------------------------
-- ML MODELS TABLE (stores model path per user)
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ml_models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  model_path TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-------------------------------------------------------------------
-- HABIT SNAPSHOTS TABLE (KEY FOR MONTH-SPECIFIC HABITS)
-- This preserves habit names & habit list per month.
-- IMPORTANT: We DO NOT add a foreign key constraint to habit_id here,
-- so snapshots remain even if the habit is later deleted.
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS habit_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    habit_id INTEGER NOT NULL,
    name_at_that_time TEXT NOT NULL,
    month TEXT NOT NULL,   -- format "YYYY-MM"

    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    -- note: habit_id intentionally has no FOREIGN KEY so snapshots persist
);

-------------------------------------------------------------------
-- RECOMMENDED INDEXES (FASTER LOADING)
-------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_completions_user_date
ON completions(user_id, date);

CREATE INDEX IF NOT EXISTS idx_snapshots_user_month
ON habit_snapshots(user_id, month);

CREATE INDEX IF NOT EXISTS idx_snapshots_habit
ON habit_snapshots(habit_id);
