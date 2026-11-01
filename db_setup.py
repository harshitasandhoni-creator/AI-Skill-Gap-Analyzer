
import sqlite3
import pandas as pd
from pathlib import Path

# File paths
CSV_PATH = Path("data/role_lookup.csv")
DB_PATH = Path("database/skill_gap.db")

# Create database folder
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Read the existing CSV
df = pd.read_csv(CSV_PATH)

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)

# Preserve all 12 original columns in a raw table
df.to_sql(
    "role_lookup_raw",
    conn,
    if_exists="replace",
    index=False
)

# Create a clean role table
conn.execute("""
CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY,
    sector TEXT,
    job_role TEXT NOT NULL,
    experience_requirement TEXT,
    cgpa_requirement TEXT,
    age_requirement TEXT,
    education_background TEXT,
    observed_employers TEXT,
    underrated_role TEXT,
    market_demand_signal TEXT,
    source_ids TEXT
)
""")

# Create one row per individual skill
conn.execute("""
CREATE TABLE IF NOT EXISTS role_skills (
    role_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    skill_type TEXT NOT NULL
        CHECK (skill_type IN ('required', 'math')),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
)
""")

# Rebuild the derived tables when this script is rerun
conn.execute("DELETE FROM role_skills")
conn.execute("DELETE FROM roles")

for role_id, row in enumerate(
    df.to_dict(orient="records"), start=1
):
    conn.execute("""
        INSERT INTO roles (
            role_id, sector, job_role,
            experience_requirement, cgpa_requirement,
            age_requirement, education_background,
            observed_employers, underrated_role,
            market_demand_signal, source_ids
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        role_id,
        row["Sector"],
        row["Job Role"],
        row["Typical Experience Requirement"],
        row["CGPA Requirement"],
        row["Age Requirement"],
        row["Relevant Education / College Background"],
        row["Observed Employers (not ranked)"],
        row["Underrated / less visible role?"],
        row["Market / demand signal"],
        row["Source IDs"]
    ))

    # Split required skills into individual records
    required = str(
        row["Required Skills (synthetic baseline; verify target posting)"]
    ).split(";")

    for skill in required:
        skill = skill.strip()
        if skill and skill.lower() != "nan":
            conn.execute("""
                INSERT INTO role_skills
                    (role_id, skill_name, skill_type)
                VALUES (?, ?, 'required')
            """, (role_id, skill))

    # Store maths skills separately
    math_skills = str(row["Math Skills Needed"]).split(";")

    for skill in math_skills:
        skill = skill.strip()
        if skill and skill.lower() != "nan":
            conn.execute("""
                INSERT INTO role_skills
                    (role_id, skill_name, skill_type)
                VALUES (?, ?, 'math')
            """, (role_id, skill))

conn.commit()

# Verify the imported records
for table in ["role_lookup_raw", "roles", "role_skills"]:
    count = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]
    print(f"{table}: {count} records")

conn.close()

print("Database created successfully!")
