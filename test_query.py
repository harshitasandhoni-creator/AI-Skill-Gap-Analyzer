
import sqlite3

conn = sqlite3.connect("database/skill_gap.db")

role_name = input("Enter a job role: ").strip()

query = """
SELECT skill_name
FROM role_skills
JOIN roles USING (role_id)
WHERE LOWER(TRIM(job_role)) = LOWER(?)
AND skill_type = 'required';
"""

results = conn.execute(query, (role_name,)).fetchall()

if results:
    print(f"\nRequired skills for {role_name}:\n")

    for row in results:
        print("-", row[0])
else:
    print("Role not found. Please check the role name.")

conn.close()

