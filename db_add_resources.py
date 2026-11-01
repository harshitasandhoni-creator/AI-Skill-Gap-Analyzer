
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "skill_gap.db"


# Official learning resources for commonly used skills.
# Other skills will get topic-specific YouTube search links.
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


def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Check that database/skill_gap.db exists."
        )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


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


def get_existing_resource_count(connection):
    return connection.execute(
        "SELECT COUNT(*) FROM learning_resources"
    ).fetchone()[0]


def add_resource(
    connection, skill_name, platform, title, url, resource_type
):
    query = """
        SELECT resource_id
        FROM learning_resources
        WHERE LOWER(TRIM(skill_name)) = LOWER(TRIM(?))
          AND LOWER(TRIM(platform)) = LOWER(TRIM(?))
          AND LOWER(TRIM(resource_title)) = LOWER(TRIM(?))
          AND TRIM(resource_url) = TRIM(?)
        LIMIT 1
    """

    existing = connection.execute(
        query, (skill_name, platform, title, url)
    ).fetchone()

    if existing:
        return False

    connection.execute(
        """
        INSERT INTO learning_resources
            (skill_name, platform, resource_title,
             resource_url, resource_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (skill_name, platform, title, url, resource_type),
    )

    return True


def resources_for_skill(skill_name):
    normalized = skill_name.strip().casefold()

    if normalized in CURATED_RESOURCES:
        return CURATED_RESOURCES[normalized]

    search_url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(skill_name + " tutorial for beginners")
    )

    return [
        (
            "YouTube Search",
            f"Learn {skill_name} - Tutorial Search",
            search_url,
            "Video",
        )
    ]


def main():
    connection = get_connection()

    try:
        skills = get_all_skills(connection)
        before_count = get_existing_resource_count(connection)

        added = 0
        skipped = 0

        connection.execute("BEGIN")

        for skill_name in skills:
            resources = resources_for_skill(skill_name)

            for platform, title, url, resource_type in resources:
                if add_resource(
                    connection,
                    skill_name,
                    platform,
                    title,
                    url,
                    resource_type,
                ):
                    added += 1
                else:
                    skipped += 1

        connection.commit()

        after_count = get_existing_resource_count(connection)

        skills_with_resources = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT TRIM(skill_name) AS skill_name
                FROM role_skills
                WHERE skill_name IS NOT NULL
                  AND TRIM(skill_name) <> ''
            ) AS skills
            WHERE EXISTS (
                SELECT 1
                FROM learning_resources AS lr
                WHERE LOWER(TRIM(lr.skill_name))
                    = LOWER(TRIM(skills.skill_name))
            )
            """
        ).fetchone()[0]

        total_skills = len(skills)

        print("\n" + "=" * 55)
        print("LEARNING RESOURCE UPDATE REPORT")
        print("=" * 55)
        print(f"Distinct skills: {total_skills}")
        print(f"Resources before update: {before_count}")
        print(f"New resources added: {added}")
        print(f"Duplicate resources skipped: {skipped}")
        print(f"Resources after update: {after_count}")
        print(
            f"Skills with resources: "
            f"{skills_with_resources}/{total_skills}"
        )

        if total_skills:
            coverage = skills_with_resources / total_skills * 100
            print(f"Exact-name resource coverage: {coverage:.2f}%")

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
            print(f"- {row['resource_type']}: {row['total']}")

        print("\nUpdate completed successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
