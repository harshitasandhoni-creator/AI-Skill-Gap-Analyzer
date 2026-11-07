import sqlite3
from pathlib import Path

DB_PATH = Path("database/skill_gap.db")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

conn.execute("PRAGMA foreign_keys = ON")

# Student profiles table
conn.execute("""
CREATE TABLE IF NOT EXISTS students (

    student_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

)
""")

# Student skill progress table
conn.execute("""
CREATE TABLE IF NOT EXISTS student_skill_progress (

    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER NOT NULL,

    role_id INTEGER NOT NULL,

    skill_name TEXT NOT NULL,

    progress_percentage REAL NOT NULL DEFAULT 0
        CHECK (
            progress_percentage >= 0
            AND progress_percentage <= 100
        ),

    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id),

    UNIQUE (student_id, role_id, skill_name)

)
""")

conn.commit()

print("Progress tracking tables created successfully!")

conn.close()