
import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "skill_gap.db"
SQL_PATH = BASE_DIR / "resource_progress_setup.sql"

# Check whether SQL file exists
if not SQL_PATH.exists():
    raise FileNotFoundError("resource_progress_setup.sql file not found!")

# Connect to the existing database
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

try:
    # Read and execute SQL setup file
    with open(SQL_PATH, "r", encoding="utf-8") as file:
        sql_script = file.read()

    conn.executescript(sql_script)
    conn.commit()

    print("Progress tracking tables created successfully!")

except Exception as error:
    conn.rollback()
    print("Error creating progress tables:", error)

finally:
    conn.close()
