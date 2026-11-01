

import sqlite3
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parent
    / "database"
    / "skill_gap.db"
)


def analyze_skills():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as conn:
        # 1. Database overview
        print("\n" + "=" * 65)
        print("1. DATABASE OVERVIEW")
        print("=" * 65)

        for table in ["roles", "role_skills", "learning_resources"]:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count} records")

        # 2. Most common skills
        print("\n" + "=" * 65)
        print("2. TOP 30 SKILLS BY NUMBER OF JOB ROLES")
        print("=" * 65)

        rows = conn.execute("""
            SELECT
                MIN(TRIM(skill_name)) AS skill_name,
                COUNT(*) AS total_records,
                COUNT(DISTINCT role_id) AS roles_using_skill
            FROM role_skills
            WHERE skill_name IS NOT NULL
              AND TRIM(skill_name) <> ''
            GROUP BY LOWER(TRIM(skill_name))
            ORDER BY roles_using_skill DESC, total_records DESC
            LIMIT 30
        """).fetchall()

        for skill, records, role_count in rows:
            print(
                f"{skill} | Records: {records} "
                f"| Roles: {role_count}"
            )

        # 3. Existing learning resources
        print("\n" + "=" * 65)
        print("3. EXISTING LEARNING RESOURCES")
        print("=" * 65)

        rows = conn.execute("""
            SELECT
                skill_name,
                COUNT(*) AS resource_count
            FROM learning_resources
            GROUP BY LOWER(TRIM(skill_name))
            ORDER BY skill_name
        """).fetchall()

        for skill, count in rows:
            print(f"{skill}: {count} resources")

        # 4. High-priority skills without exact resource matches
        print("\n" + "=" * 65)
        print("4. TOP 30 SKILLS WITHOUT EXACT RESOURCE MATCH")
        print("=" * 65)

        rows = conn.execute("""
            SELECT
                MIN(TRIM(rs.skill_name)) AS skill_name,
                COUNT(DISTINCT rs.role_id) AS roles_using_skill
            FROM role_skills AS rs
            WHERE rs.skill_name IS NOT NULL
              AND TRIM(rs.skill_name) <> ''
              AND NOT EXISTS (
                  SELECT 1
                  FROM learning_resources AS lr
                  WHERE LOWER(TRIM(lr.skill_name))
                        = LOWER(TRIM(rs.skill_name))
              )
            GROUP BY LOWER(TRIM(rs.skill_name))
            ORDER BY roles_using_skill DESC, skill_name
            LIMIT 30
        """).fetchall()

        if rows:
            for skill, role_count in rows:
                print(
                    f"{skill} | Used in {role_count} job roles"
                )
        else:
            print("All skills have exact resource matches.")

        # 5. Resource coverage summary
        print("\n" + "=" * 65)
        print("5. RESOURCE COVERAGE SUMMARY")
        print("=" * 65)

        summary = conn.execute("""
            SELECT
                COUNT(*) AS total_distinct_skills,
                SUM(
                    CASE WHEN EXISTS (
                        SELECT 1
                        FROM learning_resources AS lr
                        WHERE LOWER(TRIM(lr.skill_name))
                              = LOWER(TRIM(rs.skill_name))
                    ) THEN 1 ELSE 0 END
                ) AS matched_skill_names
            FROM (
                SELECT LOWER(TRIM(skill_name)) AS skill_key
                FROM role_skills
                WHERE skill_name IS NOT NULL
                  AND TRIM(skill_name) <> ''
                GROUP BY LOWER(TRIM(skill_name))
            ) AS distinct_skills
            JOIN role_skills AS rs
                ON LOWER(TRIM(rs.skill_name)) =
                   distinct_skills.skill_key
        """).fetchone()

        # Calculate distinct counts directly to avoid counting
        # repeated role-skill records in the summary.
        total_skills = conn.execute("""
            SELECT COUNT(DISTINCT LOWER(TRIM(skill_name)))
            FROM role_skills
            WHERE skill_name IS NOT NULL
              AND TRIM(skill_name) <> ''
        """).fetchone()[0]

        matched_skills = conn.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT LOWER(TRIM(skill_name)) AS skill_key
                FROM role_skills
                WHERE skill_name IS NOT NULL
                  AND TRIM(skill_name) <> ''
                GROUP BY LOWER(TRIM(skill_name))
            ) AS s
            WHERE EXISTS (
                SELECT 1
                FROM learning_resources AS lr
                WHERE LOWER(TRIM(lr.skill_name)) = s.skill_key
            )
        """).fetchone()[0]

        print(f"Distinct skills in role_skills: {total_skills}")
        print(f"Skills with exact resource matches: {matched_skills}")
        print(
            "Skills without exact resource matches: "
            f"{total_skills - matched_skills}"
        )

        print("\nNote:")
        print(
            "No exact match does not necessarily mean "
            "no suitable learning resource exists."
        )
        print(
            "Similar skill names may need manual mapping."
        )

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    analyze_skills()
