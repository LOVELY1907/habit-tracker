# init_db.py
import os
import shutil
import sqlite3

PROJECT_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(PROJECT_DIR, "habit_tracker.db")
SCHEMA_PATH = os.path.join(PROJECT_DIR, "migrations", "schema.sql")
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")

def backup_db():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if os.path.exists(DB_PATH):
        name = f"habit_tracker.db.backup.{int(os.path.getmtime(DB_PATH))}"
        dst = os.path.join(BACKUP_DIR, name)
        print(f"Backing up existing DB to: {dst}")
        shutil.copy2(DB_PATH, dst)

def create_db_from_schema():
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    # remove old DB (we backed it up above)
    if os.path.exists(DB_PATH):
        print("Removing existing DB file (fresh create).")
        os.remove(DB_PATH)

    # create a fresh DB and run schema SQL
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("Database created from schema at:", DB_PATH)

def main(backup_existing=True):
    if backup_existing:
        backup_db()
    create_db_from_schema()
    print("Done.")

if __name__ == "__main__":
    main(backup_existing=True)
