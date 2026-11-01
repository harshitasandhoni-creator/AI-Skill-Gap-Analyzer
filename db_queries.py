
import sqlite3
from pathlib import Path


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "skill_gap.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    """Create and return a connection to the database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at: {DB_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==========================================
# 1. GET ALL JOB ROLES
# ==========================================

def get_all_roles():
    """Return all available job roles."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT role_id, sector, job_role
            FROM roles
            ORDER BY sector, job_role
        """)
        return [dict(row) for row in cursor.fetchall()]


# ==========================================
# 2. SEARCH FOR A JOB ROLE
# ==========================================

def search_roles(keyword):
    """Search job roles by name or sector."""
    if not keyword or not keyword.strip():
        return []

    keyword = keyword.strip()

    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT role_id, sector, job_role
            FROM roles
            WHERE job_role LIKE ? COLLATE NOCASE
               OR sector LIKE ? COLLATE NOCASE
            ORDER BY job_role
        """, (f"%{keyword}%", f"%{keyword}%"))

        return [dict(row) for row in cursor.fetchall()]


# ==========================================
# 3. GET REQUIRED SKILLS FOR A JOB ROLE
# ==========================================

def get_required_skills(role_id):
    """Return all skills associated with a role ID."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT skill_name, skill_type
            FROM role_skills
            WHERE role_id = ?
            ORDER BY skill_type, skill_name
        """, (role_id,))

        return [dict(row) for row in cursor.fetchall()]


# ==========================================
# 4. GET ALL LEARNING RESOURCES FOR A SKILL
# ==========================================

def get_learning_resources(skill_name):
    """Return all resources matching a skill name."""
    if not skill_name or not skill_name.strip():
        return []

    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT
                resource_id,
                skill_name,
                platform,
                resource_title,
                resource_url,
                resource_type
            FROM learning_resources
            WHERE LOWER(TRIM(skill_name)) = LOWER(TRIM(?))
            ORDER BY
                CASE resource_type
                    WHEN 'Video' THEN 1
                    WHEN 'Playlist' THEN 2
                    WHEN 'Course' THEN 3
                    ELSE 4
                END,
                platform,
                resource_title
        """, (skill_name.strip(),))

        return [dict(row) for row in cursor.fetchall()]


# ==========================================
# 5. GET ROLE DETAILS WITH ITS SKILLS
# ==========================================

def get_role_details(role_id):
    """Return role information and associated skills."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT role_id, sector, job_role
            FROM roles
            WHERE role_id = ?
        """, (role_id,))

        role = cursor.fetchone()

        if role is None:
            return None

        role_details = dict(role)
        role_details["skills"] = get_required_skills(role_id)

        return role_details


# ==========================================
# 6. GET RESOURCES FOR EVERY SKILL IN A ROLE
# ==========================================

def get_resources_for_role(role_id):
    """
    Return all required skills and their exact-name resources.
    Skills without resources are included with an empty list.
    """
    role = get_role_details(role_id)

    if role is None:
        return None

    results = []

    for skill in role["skills"]:
        resources = get_learning_resources(skill["skill_name"])

        results.append({
            "skill_name": skill["skill_name"],
            "skill_type": skill["skill_type"],
            "resources": resources
        })

    return {
        "role_id": role["role_id"],
        "job_role": role["job_role"],
        "sector": role["sector"],
        "skills": results
    }


# ==========================================
# 7. GET NUMBER OF ROLES PER SECTOR
# ==========================================

def get_sector_summary():
    """Return the number of job roles in each sector."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT sector, COUNT(*) AS total_roles
            FROM roles
            GROUP BY sector
            ORDER BY total_roles DESC
        """)

        return [dict(row) for row in cursor.fetchall()]


# ==========================================
# 8. GET DATABASE STATISTICS
# ==========================================

def get_database_stats():
    """Return total records in the main tables."""
    with get_connection() as conn:
        tables = {
            "roles": "roles",
            "role_skills": "role_skills",
            "learning_resources": "learning_resources"
        }

        stats = {}

        for label, table in tables.items():
            stats[label] = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

        return stats


# ==========================================
# 9. TEST DATABASE FUNCTIONS
# ==========================================

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("DATABASE FUNCTIONS TEST")
        print("=" * 50)

        # Test 1: Database statistics
        print("\n1. DATABASE STATISTICS")
        print(get_database_stats())

        # Test 2: Search for a job role
        print("\n2. SEARCH RESULTS")
        roles = search_roles("AI / Machine Learning Engineer")

        for role in roles:
            print(role)

        # Test 3: Display role details and required skills
        if roles:
            role_id = roles[0]["role_id"]
            details = get_role_details(role_id)

            print("\n3. REQUIRED SKILLS")
            print("Job Role:", details["job_role"])
            print("Sector:", details["sector"])

            for skill in details["skills"]:
                print(
                    f"- {skill['skill_name']} "
                    f"({skill['skill_type']})"
                )

            # Test 4: Resources for the selected role
            print("\n4. RESOURCES FOR SELECTED ROLE")
            role_resources = get_resources_for_role(role_id)

            for skill in role_resources["skills"]:
                print(f"\nSkill: {skill['skill_name']}")

                if skill["resources"]:
                    for resource in skill["resources"]:
                        print(
                            f"  - {resource['resource_title']} "
                            f"| {resource['platform']} "
                            f"| {resource['resource_type']} "
                            f"| {resource['resource_url']}"
                        )
                else:
                    print("  No exact-name resource match found.")

        # Test 5: All Python resources
        print("\n5. PYTHON LEARNING RESOURCES")
        resources = get_learning_resources("Python")

        for resource in resources:
            print(
                f"- {resource['resource_title']} "
                f"| {resource['platform']} "
                f"| {resource['resource_type']} "
                f"| {resource['resource_url']}"
            )

        print(f"Total Python resources: {len(resources)}")

        # Test 6: Sector summary
        print("\n6. SECTOR SUMMARY")

        for sector in get_sector_summary():
            print(sector)

        print("\nDATABASE FUNCTIONS TEST COMPLETED!")

    except (sqlite3.Error, FileNotFoundError) as error:
        print("Database error:", error)
