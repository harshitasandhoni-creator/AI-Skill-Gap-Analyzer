
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus

# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

DB_PATH = (
    Path(__file__).resolve().parent
    / "database"
    / "skill_gap.db"
)

ALLOWED_RESOURCE_TYPES = {"Video", "Playlist", "Course"}


def youtube_search(topic, playlist=False):
    """Create a YouTube search URL for a learning topic."""
    if playlist:
        query = f"{topic} complete tutorial playlist"
    else:
        query = f"{topic} tutorial for beginners"

    return (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )


# --------------------------------------------------
# LEARNING RESOURCES
#
# Format:
# skill_name, platform, title, URL, resource_type
# --------------------------------------------------

RESOURCES = [
    # 1. PYTHON
    (
        "Python", "Python.org",
        "Official Python Tutorial",
        "https://docs.python.org/3/tutorial/",
        "Course"
    ),
    (
        "Python", "YouTube",
        "Python Beginner Tutorial - Video Search",
        youtube_search("Python programming beginner"),
        "Video"
    ),
    (
        "Python", "YouTube",
        "Python Complete Learning Playlists",
        youtube_search("Python programming", playlist=True),
        "Playlist"
    ),

    # 2. SQL
    (
        "SQL", "SQLBolt",
        "Interactive SQL Lessons",
        "https://sqlbolt.com/",
        "Course"
    ),
    (
        "SQL", "YouTube",
        "SQL Tutorial for Beginners - Video Search",
        youtube_search("SQL tutorial beginner"),
        "Video"
    ),
    (
        "SQL", "YouTube",
        "Complete SQL Learning Playlists",
        youtube_search("SQL full course", playlist=True),
        "Playlist"
    ),

    # 3. GIT
    (
        "Git", "GitHub Skills",
        "Introduction to GitHub",
        "https://skills.github.com/",
        "Course"
    ),
    (
        "Git", "YouTube",
        "Git and GitHub Beginner Tutorials",
        youtube_search("Git and GitHub beginner"),
        "Video"
    ),
    (
        "Git", "YouTube",
        "Git Complete Learning Playlists",
        youtube_search("Git and GitHub", playlist=True),
        "Playlist"
    ),

    # 4. DESCRIPTIVE STATISTICS
    (
        "Descriptive statistics", "Khan Academy",
        "Statistics and Probability",
        "https://www.khanacademy.org/math/statistics-probability",
        "Course"
    ),
    (
        "Descriptive statistics", "YouTube",
        "Descriptive Statistics Tutorials",
        youtube_search("descriptive statistics mean median mode variance"),
        "Video"
    ),
    (
        "Descriptive statistics", "YouTube",
        "Descriptive Statistics Playlists",
        youtube_search("descriptive statistics", playlist=True),
        "Playlist"
    ),

    # 5. PROBABILITY
    (
        "Probability", "Khan Academy",
        "Probability Lessons",
        "https://www.khanacademy.org/math/statistics-probability/probability-library",
        "Course"
    ),
    (
        "Probability", "YouTube",
        "Probability for Beginners",
        youtube_search("probability mathematics beginner"),
        "Video"
    ),

    # 6. STATISTICS AND PROBABILITY
    (
        "Statistics and probability", "Khan Academy",
        "Statistics and Probability Course",
        "https://www.khanacademy.org/math/statistics-probability",
        "Course"
    ),
    (
        "Statistics and probability", "YouTube",
        "Statistics and Probability Tutorials",
        youtube_search("statistics and probability beginner"),
        "Playlist"
    ),

    # 7. BASIC REGRESSION
    (
        "Basic regression for trend analysis", "Google",
        "Machine Learning Crash Course",
        "https://developers.google.com/machine-learning/crash-course",
        "Course"
    ),
    (
        "Basic regression for trend analysis", "YouTube",
        "Linear Regression Tutorials",
        youtube_search("linear regression trend analysis"),
        "Video"
    ),

    # 8. MACHINE LEARNING
    (
        "Machine Learning", "Google",
        "Google Machine Learning Crash Course",
        "https://developers.google.com/machine-learning/crash-course",
        "Course"
    ),
    (
        "Machine Learning", "YouTube",
        "Machine Learning Beginner Tutorials",
        youtube_search("machine learning beginner"),
        "Video"
    ),
    (
        "Machine Learning", "YouTube",
        "Machine Learning Complete Playlists",
        youtube_search("machine learning full course", playlist=True),
        "Playlist"
    ),

    # 9. EXCEL
    (
        "Excel", "Microsoft Learn",
        "Excel Help and Learning",
        "https://support.microsoft.com/en-us/excel",
        "Course"
    ),
    (
        "Excel", "YouTube",
        "Excel for Data Analysis Tutorials",
        youtube_search("Excel for data analysis beginner"),
        "Video"
    ),
    (
        "Excel", "YouTube",
        "Excel Complete Learning Playlists",
        youtube_search("Excel full course", playlist=True),
        "Playlist"
    ),

    # 10. POWER BI
    (
        "Power BI", "Microsoft Learn",
        "Get Started with Power BI",
        "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
        "Course"
    ),
    (
        "Power BI", "YouTube",
        "Power BI Beginner Tutorials",
        youtube_search("Power BI beginner tutorial"),
        "Video"
    ),
    (
        "Power BI", "YouTube",
        "Power BI Complete Learning Playlists",
        youtube_search("Power BI full course", playlist=True),
        "Playlist"
    ),

    # 11. DEBUGGING
    (
        "debugging", "Python.org",
        "Python Debugger Documentation",
        "https://docs.python.org/3/library/pdb.html",
        "Course"
    ),
    (
        "debugging", "YouTube",
        "Python Debugging Tutorials",
        youtube_search("Python debugging VS Code"),
        "Video"
    ),

    # 12. DOCUMENTATION
    (
        "documentation", "Google",
        "Technical Writing Courses",
        "https://developers.google.com/tech-writing",
        "Course"
    ),
    (
        "documentation", "YouTube",
        "Technical Documentation Tutorials",
        youtube_search("technical documentation for developers"),
        "Video"
    ),

    # 13. BASIC ALGEBRA
    (
        "Basic algebra", "Khan Academy",
        "Algebra Basics",
        "https://www.khanacademy.org/math/algebra-basics",
        "Course"
    ),
    (
        "Basic algebra", "YouTube",
        "Basic Algebra Tutorials",
        youtube_search("basic algebra beginner"),
        "Video"
    ),

    # 14. BOOLEAN LOGIC AND DISCRETE MATHEMATICS
    (
        "Boolean logic and discrete mathematics", "YouTube",
        "Boolean Logic and Discrete Mathematics Tutorials",
        youtube_search("Boolean logic discrete mathematics"),
        "Video"
    ),
    (
        "Boolean logic and discrete mathematics", "YouTube",
        "Discrete Mathematics Learning Playlists",
        youtube_search("discrete mathematics", playlist=True),
        "Playlist"
    ),

    # 15. COMPLEXITY ANALYSIS
    (
        "Complexity analysis (Big-O)", "YouTube",
        "Big-O Notation Explained",
        youtube_search("Big O notation algorithms"),
        "Video"
    ),
    (
        "Complexity analysis (Big-O)", "YouTube",
        "Data Structures and Algorithms Playlists",
        youtube_search("data structures algorithms Big O", playlist=True),
        "Playlist"
    ),
]


# --------------------------------------------------
# INSERT RESOURCES AND PREVENT DUPLICATES
# --------------------------------------------------

def add_resources():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Check that this file is in your project root."
        )

    added = 0
    skipped = 0

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # Verify that the expected table and columns exist.
        table_info = conn.execute(
            "PRAGMA table_info(learning_resources)"
        ).fetchall()

        existing_columns = {row[1] for row in table_info}

        required_columns = {
            "resource_id",
            "skill_name",
            "platform",
            "resource_title",
            "resource_url",
            "resource_type",
        }

        if not required_columns.issubset(existing_columns):
            missing = required_columns - existing_columns
            raise RuntimeError(
                "learning_resources table is missing columns: "
                + ", ".join(sorted(missing))
            )

        # One logical resource cannot be duplicated just because
        # its skill name, platform or title uses different casing
        # or extra surrounding spaces.
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_learning_resources_unique
            ON learning_resources (
                LOWER(TRIM(skill_name)),
                LOWER(TRIM(platform)),
                LOWER(TRIM(resource_title)),
                TRIM(resource_url)
            )
        """)

        insert_query = """
            INSERT OR IGNORE INTO learning_resources (
                skill_name,
                platform,
                resource_title,
                resource_url,
                resource_type
            )
            VALUES (?, ?, ?, ?, ?)
        """

        for resource in RESOURCES:
            skill, platform, title, url, resource_type = resource

            if resource_type not in ALLOWED_RESOURCE_TYPES:
                raise ValueError(
                    f"Invalid resource type: {resource_type}"
                )

            if not all(
                isinstance(value, str) and value.strip()
                for value in resource
            ):
                raise ValueError(
                    f"Resource contains an empty field: {resource}"
                )

            cursor = conn.execute(
                insert_query,
                (
                    skill.strip(),
                    platform.strip(),
                    title.strip(),
                    url.strip(),
                    resource_type,
                ),
            )

            if cursor.rowcount == 1:
                added += 1
            else:
                skipped += 1

        total = conn.execute(
            "SELECT COUNT(*) FROM learning_resources"
        ).fetchone()[0]

        print("\nResource insertion completed.")
        print(f"New resources added: {added}")
        print(f"Duplicate resources skipped: {skipped}")
        print(f"Total resources in database: {total}")

        print("\nResources per skill:")

        rows = conn.execute("""
            SELECT
                skill_name,
                COUNT(*) AS resource_count
            FROM learning_resources
            GROUP BY LOWER(TRIM(skill_name))
            ORDER BY skill_name
        """).fetchall()

        for skill, count in rows:
            print(f"{skill}: {count}")


if __name__ == "__main__":
    try:
        add_resources()
    except (sqlite3.Error, OSError, RuntimeError, ValueError) as error:
        print(f"\nError: {error}")
