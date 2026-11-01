
import sqlite3
from pathlib import Path

# Connect to the existing database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "skill_gap.db"

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def show_section(title):
    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)


try:
    # 1. Database overview
    show_section("1. DATABASE OVERVIEW")

    for table in ["roles", "role_skills", "learning_resources"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"Total rows in {table}: {cursor.fetchone()[0]}")

    # 2. Number of job roles in each sector
    show_section("2. JOB ROLES BY SECTOR")

    cursor.execute("""
        SELECT sector, COUNT(*) AS total_roles
        FROM roles
        GROUP BY sector
        ORDER BY total_roles DESC, sector;
    """)

    for sector, count in cursor.fetchall():
        print(f"{sector}: {count} roles")

    # 3. Roles with the highest number of required skills
    show_section("3. TOP 10 ROLES BY REQUIRED SKILLS")

    cursor.execute("""
        SELECT
            r.job_role,
            r.sector,
            COUNT(DISTINCT rs.skill_name) AS total_skills
        FROM roles r
        LEFT JOIN role_skills rs
            ON r.role_id = rs.role_id
        GROUP BY r.role_id, r.job_role, r.sector
        ORDER BY total_skills DESC, r.job_role
        LIMIT 10;
    """)

    for job_role, sector, count in cursor.fetchall():
        print(f"{job_role} ({sector}): {count} skills")

    # 4. Most frequently required skills across job roles
    show_section("4. TOP 15 MOST COMMON SKILLS")

    cursor.execute("""
        SELECT
            LOWER(TRIM(skill_name)) AS skill,
            COUNT(DISTINCT role_id) AS roles_requiring_skill
        FROM role_skills
        WHERE TRIM(skill_name) != ''
        GROUP BY LOWER(TRIM(skill_name))
        ORDER BY roles_requiring_skill DESC, skill
        LIMIT 15;
    """)

    for skill, count in cursor.fetchall():
        print(f"{skill}: required by {count} roles")

    # 5. Skill categories
    show_section("5. SKILL TYPE DISTRIBUTION")

    cursor.execute("""
        SELECT
            COALESCE(NULLIF(TRIM(skill_type), ''), 'Unspecified'),
            COUNT(*)
        FROM role_skills
        GROUP BY COALESCE(NULLIF(TRIM(skill_type), ''), 'Unspecified')
        ORDER BY COUNT(*) DESC;
    """)

    for skill_type, count in cursor.fetchall():
        print(f"{skill_type}: {count} entries")

    # 6. Inspect the required skills for one job role
    show_section("6. REQUIRED SKILLS FOR A SAMPLE JOB ROLE")

    cursor.execute("""
        SELECT role_id, job_role, sector
        FROM roles
        WHERE LOWER(job_role) =
              LOWER('AI / Machine Learning Engineer')
        LIMIT 1;
    """)

    role = cursor.fetchone()

    if role:
        role_id, job_role, sector = role
        print(f"Role: {job_role}")
        print(f"Sector: {sector}")
        print("Required skills:")

        cursor.execute("""
            SELECT DISTINCT skill_name, skill_type
            FROM role_skills
            WHERE role_id = ?
            ORDER BY skill_name;
        """, (role_id,))

        skills = cursor.fetchall()

        if skills:
            for skill_name, skill_type in skills:
                print(f"- {skill_name} ({skill_type or 'Unspecified'})")
        else:
            print("No skills found for this role.")
    else:
        print("Sample role not found. Check the exact job role name.")

    # 7. Match required skills with available learning resources
    show_section("7. LEARNING RESOURCE COVERAGE")

    cursor.execute("""
        SELECT COUNT(DISTINCT LOWER(TRIM(rs.skill_name)))
        FROM role_skills rs
        WHERE EXISTS (
            SELECT 1
            FROM learning_resources lr
            WHERE LOWER(TRIM(lr.skill_name)) =
                  LOWER(TRIM(rs.skill_name))
        );
    """)

    covered = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT LOWER(TRIM(skill_name)))
        FROM role_skills
        WHERE TRIM(skill_name) != '';
    """)

    total_skills = cursor.fetchone()[0]

    print(f"Distinct required skills: {total_skills}")
    print(f"Skills with matching resources: {covered}")
    print(f"Skills without exact resource-name matches: "
          f"{total_skills - covered}")

    print("\nNote: Resource matching is case-insensitive, "
          "but skill names must otherwise match.")

    print("\n" + "=" * 55)
    print("SQL ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 55)

finally:
    conn.close()
