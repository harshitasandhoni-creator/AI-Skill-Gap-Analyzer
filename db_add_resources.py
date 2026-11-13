
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "skill_gap.db"


# --------------------------------------------------
# CURATED LEARNING RESOURCES
# Official resources for commonly used skills
# --------------------------------------------------

CURATED_RESOURCES = {
    "python": [
        (
            "Python.org",
            "Official Python Tutorial",
            "https://docs.python.org/3/tutorial/",
            "Course",
        )
    ],

    "sql": [
        (
            "SQLBolt",
            "Interactive SQL Lessons",
            "https://sqlbolt.com/",
            "Course",
        )
    ],

    "statistics": [
        (
            "Khan Academy",
            "Statistics and Probability",
            "https://www.khanacademy.org/math/statistics-probability",
            "Course",
        )
    ],

    "statistics and probability": [
        (
            "Khan Academy",
            "Statistics and Probability",
            "https://www.khanacademy.org/math/statistics-probability",
            "Course",
        )
    ],

    "git": [
        (
            "GitHub Skills",
            "Introduction to GitHub",
            "https://skills.github.com/",
            "Course",
        )
    ],

    "excel": [
        (
            "Microsoft Support",
            "Excel Help and Learning",
            "https://support.microsoft.com/excel",
            "Course",
        )
    ],

    "power bi": [
        (
            "Microsoft Learn",
            "Get Started with Power BI",
            "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
            "Course",
        )
    ],

    "machine learning": [
        (
            "Google for Developers",
            "Machine Learning Crash Course",
            "https://developers.google.com/machine-learning/crash-course",
            "Course",
        )
    ],

    "scikit-learn": [
        (
            "scikit-learn",
            "Official User Guide",
            "https://scikit-learn.org/stable/user_guide.html",
            "Course",
        )
    ],

    "pytorch": [
        (
            "PyTorch",
            "Official Tutorials",
            "https://pytorch.org/tutorials/",
            "Course",
        )
    ],

    "tensorflow": [
        (
            "TensorFlow",
            "Official Tutorials",
            "https://www.tensorflow.org/tutorials",
            "Course",
        )
    ],

    "pandas": [
        (
            "pandas",
            "Official Getting Started Tutorials",
            "https://pandas.pydata.org/docs/getting_started/intro_tutorials/",
            "Course",
        )
    ],

    "numpy": [
        (
            "NumPy",
            "Official Quickstart Tutorial",
            "https://numpy.org/doc/stable/user/quickstart.html",
            "Course",
        )
    ],
}


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# --------------------------------------------------
# GET ALL DISTINCT SKILLS
# --------------------------------------------------

def get_all_skills(connection):

    query = """
        SELECT DISTINCT TRIM(skill_name) AS skill_name
        FROM role_skills
        WHERE skill_name IS NOT NULL
          AND TRIM(skill_name) <> ''
        ORDER BY skill_name COLLATE NOCASE
    """

    rows = connection.execute(query).fetchall()

    return [row["skill_name"] for row in rows]


# --------------------------------------------------
# RESOURCE COUNT
# --------------------------------------------------

def get_existing_resource_count(connection):

    return connection.execute(
        "SELECT COUNT(*) FROM learning_resources"
    ).fetchone()[0]


# --------------------------------------------------
# CHECK WHETHER A SKILL ALREADY HAS A RESOURCE
# --------------------------------------------------

def skill_has_resource(connection, skill_name):

    query = """
        SELECT 1
        FROM learning_resources
        WHERE LOWER(TRIM(skill_name))
              = LOWER(TRIM(?))
        LIMIT 1
    """

    return connection.execute(
        query, (skill_name,)
    ).fetchone() is not None


# --------------------------------------------------
# INSERT RESOURCE WITHOUT DUPLICATES
# --------------------------------------------------

def add_resource(
    connection,
    skill_name,
    platform,
    title,
    url,
    resource_type
):

    query = """
        SELECT resource_id
        FROM learning_resources
        WHERE LOWER(TRIM(skill_name))
              = LOWER(TRIM(?))
          AND LOWER(TRIM(platform))
              = LOWER(TRIM(?))
          AND LOWER(TRIM(resource_title))
              = LOWER(TRIM(?))
          AND TRIM(resource_url) = TRIM(?)
        LIMIT 1
    """

    existing = connection.execute(
        query,
        (skill_name, platform, title, url)
    ).fetchone()

    if existing:
        return False

    connection.execute(
        """
        INSERT INTO learning_resources
        (
            skill_name,
            platform,
            resource_title,
            resource_url,
            resource_type
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            skill_name,
            platform,
            title,
            url,
            resource_type
        )
    )

    return True


# --------------------------------------------------
# GENERATE RESOURCE FOR EACH SKILL
# --------------------------------------------------

def resources_for_skill(skill_name):

    normalized = skill_name.strip().casefold()

    # Use curated official resources wherever available
    if normalized in CURATED_RESOURCES:

        return CURATED_RESOURCES[normalized]

    # Generate topic-specific YouTube search link
    search_query = skill_name + " tutorial for beginners"

    search_url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(search_query)
    )

    return [
        (
            "YouTube Search",
            f"Learn {skill_name} - Tutorial Search",
            search_url,
            "Video",
        )
    ]


# --------------------------------------------------
# VERIFY DATABASE COVERAGE
# --------------------------------------------------

def get_skills_without_resources(connection):

    query = """
        SELECT DISTINCT TRIM(rs.skill_name) AS skill_name
        FROM role_skills AS rs
        WHERE rs.skill_name IS NOT NULL
          AND TRIM(rs.skill_name) <> ''
          AND NOT EXISTS (
              SELECT 1
              FROM learning_resources AS lr
              WHERE LOWER(TRIM(lr.skill_name))
                    = LOWER(TRIM(rs.skill_name))
          )
        ORDER BY skill_name COLLATE NOCASE
    """

    return connection.execute(query).fetchall()


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def main():

    connection = get_connection()

    try:

        # Check required tables and columns
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        if not {"roles", "role_skills", "learning_resources"}.issubset(tables):
            raise RuntimeError(
                "Required database tables are missing."
            )

        required_columns = {
            "skill_name",
            "platform",
            "resource_title",
            "resource_url",
            "resource_type",
        }

        actual_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(learning_resources)"
            ).fetchall()
        }

        if not required_columns.issubset(actual_columns):
            raise RuntimeError(
                "learning_resources table has an unexpected schema."
            )

        # Initial statistics
        skills = get_all_skills(connection)

        before_count = get_existing_resource_count(connection)

        added = 0
        skipped = 0

        # Start transaction
        connection.execute("BEGIN")

        for skill_name in skills:

            # Preserve all existing resources.
            # Add a resource only if this skill has none.
            if skill_has_resource(connection, skill_name):
                skipped += 1
                continue

            resources = resources_for_skill(skill_name)

            for platform, title, url, resource_type in resources:

                if add_resource(
                    connection,
                    skill_name,
                    platform,
                    title,
                    url,
                    resource_type
                ):
                    added += 1
                else:
                    skipped += 1

        # Save changes
        connection.commit()

        # Final statistics
        after_count = get_existing_resource_count(connection)

        skills_without_resources = get_skills_without_resources(
            connection
        )

        total_skills = len(skills)

        skills_with_resources = (
            total_skills - len(skills_without_resources)
        )

        # --------------------------------------------------
        # FINAL REPORT
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("       LEARNING RESOURCE UPDATE REPORT")
        print("=" * 60)

        print(f"Database: {DB_PATH.name}")

        print(f"\nDistinct skills: {total_skills}")

        print(f"Resources before update: {before_count}")

        print(f"New resources added: {added}")

        print(f"Existing skills skipped: {skipped}")

        print(f"Resources after update: {after_count}")

        print(
            f"\nSkills with resources: "
            f"{skills_with_resources}/{total_skills}"
        )

        if total_skills:

            coverage = (
                skills_with_resources / total_skills
            ) * 100

            print(f"Resource coverage: {coverage:.2f}%")

        print("\nResources by type:")

        rows = connection.execute(
            """
            SELECT resource_type, COUNT(*) AS total
            FROM learning_resources
            GROUP BY resource_type
            ORDER BY total DESC
            """
        ).fetchall()

        for row in rows:

            print(
                f"- {row['resource_type']}: {row['total']}"
            )

        if skills_without_resources:

            print("\nSkills still missing resources:")

            for row in skills_without_resources:
                print("-", row["skill_name"])

        else:

            print("\nAll skills have at least one resource!")

        # Database integrity check
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        print("\nDATABASE INTEGRITY:", integrity)

        print("\nUpdate completed successfully!")

        print("=" * 60)

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# --------------------------------------------------
# SCRIPT ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
