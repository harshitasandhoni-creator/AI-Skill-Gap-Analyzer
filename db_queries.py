
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
# 9. REGISTER A STUDENT
# ==========================================

def register_student(name, email):
    """Register a student or return the existing student ID."""

    if not name or not name.strip():
        raise ValueError("Student name cannot be empty.")

    if not email or not email.strip():
        raise ValueError("Email cannot be empty.")

    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO students (name, email)
            VALUES (?, ?)
        """, (name.strip(), email.strip().lower()))

        student = conn.execute("""
            SELECT student_id
            FROM students
            WHERE email = ?
        """, (email.strip().lower(),)).fetchone()

        return student["student_id"]


# ==========================================
# 10. ASSIGN ROLE RESOURCES TO A STUDENT
# ==========================================

def assign_resources_to_student(student_id, role_id):
    """Assign all learning resources of a role to a student."""

    role_resources = get_resources_for_role(role_id)

    if role_resources is None:
        raise ValueError("Invalid role ID.")

    assigned_count = 0

    with get_connection() as conn:
        for skill in role_resources["skills"]:

            for resource in skill["resources"]:

                cursor = conn.execute("""
                    INSERT OR IGNORE INTO student_resource_progress
                    (student_id, role_id, resource_id)
                    VALUES (?, ?, ?)
                """, (
                    student_id,
                    role_id,
                    resource["resource_id"]
                ))

                assigned_count += cursor.rowcount

    return assigned_count


# ==========================================
# 11. UPDATE RESOURCE PROGRESS
# ==========================================

def update_resource_progress(
    student_id,
    role_id,
    resource_id,
    status
):
    """Update the completion status of a learning resource."""

    valid_statuses = [
        "Not Started",
        "In Progress",
        "Completed"
    ]

    if status not in valid_statuses:
        raise ValueError("Invalid progress status.")

    with get_connection() as conn:

        cursor = conn.execute("""
            UPDATE student_resource_progress

            SET
                status = ?,

                started_at = CASE
                    WHEN ? = 'Not Started' THEN NULL
                    ELSE COALESCE(started_at, CURRENT_TIMESTAMP)
                END,

                completed_at = CASE
                    WHEN ? = 'Completed' THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END,

                updated_at = CURRENT_TIMESTAMP

            WHERE student_id = ?
              AND role_id = ?
              AND resource_id = ?

        """, (
            status,
            status,
            status,
            student_id,
            role_id,
            resource_id
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                "Resource progress record not found. "
                "Assign resources first."
            )

        return True


# ==========================================
# 12. GET STUDENT OVERALL PROGRESS
# ==========================================

def get_student_overall_progress(student_id, role_id):
    """Calculate overall learning resource completion."""

    with get_connection() as conn:
        result = conn.execute("""
            SELECT
                COUNT(*) AS total_resources,

                SUM(
                    CASE WHEN status = 'Completed'
                    THEN 1 ELSE 0 END
                ) AS completed_resources,

                SUM(
                    CASE WHEN status = 'In Progress'
                    THEN 1 ELSE 0 END
                ) AS in_progress_resources

            FROM student_resource_progress
            WHERE student_id = ?
              AND role_id = ?
        """, (student_id, role_id)).fetchone()

        total = result["total_resources"]
        completed = result["completed_resources"] or 0
        in_progress = result["in_progress_resources"] or 0

        percentage = (
            (completed / total) * 100
            if total > 0 else 0
        )

        return {
            "total_resources": total,
            "completed_resources": completed,
            "in_progress_resources": in_progress,
            "not_started_resources": total - completed - in_progress,
            "progress_percentage": round(percentage, 2)
        }

# ==========================================
# 13. GET STUDENT RESOURCES WITH PROGRESS
# ==========================================

def get_student_resources_with_progress(student_id, role_id):
    """Return assigned resources with their progress status."""

    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT
                srp.resource_id,
                lr.skill_name,
                lr.platform,
                lr.resource_title,
                lr.resource_url,
                lr.resource_type,
                srp.status,
                srp.started_at,
                srp.completed_at,
                srp.updated_at

            FROM student_resource_progress AS srp

            JOIN learning_resources AS lr
                ON srp.resource_id = lr.resource_id

            WHERE srp.student_id = ?
              AND srp.role_id = ?

            ORDER BY lr.skill_name, lr.resource_title
        """, (student_id, role_id))

        return [dict(row) for row in cursor.fetchall()]

# ==========================================
# 12. TEST DATABASE FUNCTIONS
# ==========================================

if __name__ == "__main__":
    try:
         # Test 7: Student Registration
        print("\n7. STUDENT REGISTRATION")

        student_id = register_student(
            "Test Student",
            "teststudent@example.com"
        )

        print("Student ID:", student_id)
        # Test 8: Assign Resources
        print("\n8. ASSIGN RESOURCES TO STUDENT")

        assigned_count = assign_resources_to_student(
            student_id,
            1
        )

        print("New resources assigned:", assigned_count)
         # Test 9: Update Resource Progress
        print("\n9. UPDATE RESOURCE PROGRESS")

        role_resources = get_resources_for_role(1)

        test_resource_id = role_resources["skills"][0]["resources"][0]["resource_id"]

        update_resource_progress(
            student_id,
            1,
            test_resource_id,
            "In Progress"
        )

        print("Resource ID:", test_resource_id)
        print("Status updated to: In Progress")
          # Test 11: Mark Resource as Completed
        print("\n11. MARK RESOURCE AS COMPLETED")

        update_resource_progress(
            student_id,
            1,
            test_resource_id,
            "Completed"
        )

        print("Resource status updated to: Completed")
        # Test 10: Overall Student Progress
        print("\n10. STUDENT OVERALL PROGRESS")

        progress = get_student_overall_progress(student_id, 1)

        print(progress)
                # Test 12: Student Resources with Progress
        print("\n12. STUDENT RESOURCES WITH PROGRESS")

        student_resources = get_student_resources_with_progress(
            student_id, 1
        )

        for resource in student_resources:
            print(resource)
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
