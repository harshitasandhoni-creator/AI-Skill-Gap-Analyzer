from db_queries import (
    get_all_roles,
    get_role_details,
    get_learning_resources
)

from skill_analysis_math import analyze_skill_gap
import re

def normalize_skill(skill):
    """Normalize skill names for better matching."""

    skill = skill.strip().lower()

    aliases = {
        "python programming": "python",
        "python language": "python",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "structured query language": "sql",
        "mysql": "sql",
        "statistical analysis": "statistics",
        "power bi": "power bi",
        "ml": "machine learning",
        "ai": "artificial intelligence",
    }

    skill = re.sub(r"\s+", " ", skill)

    return aliases.get(skill, skill)

def analyze_skill_gap(required_skills, student_skills):

    # Normalize student skills
    student = {
        normalize_skill(skill)
        for skill in student_skills
        if skill.strip()
    }

    matched = []
    missing = []

    # Check every required skill
    for requirement in required_skills:

        requirement = requirement.strip().lower()

        # Handle alternatives such as Power BI or Tableau
        alternatives = re.split(r"\s+or\s+", requirement)

        is_matched = False

        for alternative in alternatives:

            normalized = normalize_skill(alternative)

            if normalized and normalized in student:
                is_matched = True
                break

        # Store the result
        if is_matched:
            matched.append(requirement)
        else:
            missing.append(requirement)

    # Calculate percentage
    total = len(matched) + len(missing)

    percentage = (
        (len(matched) / total) * 100
        if total > 0 else 0
    )

    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "match_percentage": round(percentage, 2)
    }

# Test the function
def analyze_role_gap(role_id, student_skills):

    # Get job role details from the database
    role = get_role_details(role_id)

    if role is None:
        return None

    # Extract required skills from database
    required_skills = [
        skill["skill_name"]
        for skill in role["skills"]
    ]
       
    # Compare student skills with job skills
    result = analyze_skill_gap(
        required_skills,
        student_skills
    )
    # Get learning resources for missing skills
    learning_plan = {}

    for skill in result["missing_skills"]:

        resources = get_learning_resources(skill)

        learning_plan[skill] = resources

        print(skill, ":", len(resources), "resources found")

    result["learning_plan"] = learning_plan

    # Add job role information
    result["job_role"] = role["job_role"]
    result["sector"] = role["sector"]

    return result

if __name__ == "__main__":

    print("\n===== AI SKILL GAP ANALYZER =====")

    # Get all job roles from database
    roles = get_all_roles()

    print("\n" + "=" * 60)
    print("          AVAILABLE JOB ROLES")
    print("=" * 60)

    for index, role in enumerate(roles[:20], start=1):
        print(
            f"{index:2}. {role['job_role']:<40} "
            f"ID: {role['role_id']}"
        )
    print("=" * 60)
    
    # Ask user to select a role
    role_id = int(input("\nEnter the Role ID: "))

    # Ask student to enter their skills
    skills_input = input(
        "\nEnter your skills separated by commas: "
    )

    student_skills = [
        skill.strip()
        for skill in skills_input.split(",")
        if skill.strip()
    ]

    # Perform skill gap analysis
    result = analyze_role_gap(
        role_id,
        student_skills
    )

    # Display results
    if result is None:
        print("\nInvalid Role ID!")

    else:
        print("\n===== SKILL GAP REPORT =====")

        print("Job Role:", result["job_role"])
        print("Sector:", result["sector"])

        print(
            "Matched Skills:",
            result["matched_skills"]
        )

        print(
            "Missing Skills:",
            result["missing_skills"]
        )

        print(
            "Match Percentage:",
            result["match_percentage"],
            "%"
        )
        # Display learning resources
        print("\n===== RECOMMENDED LEARNING RESOURCES =====")

        for skill, resources in result["learning_plan"].items():

            print(f"\nSkill to Learn: {skill}")

            if resources:

                for resource in resources:
                    print("Platform:", resource["platform"])
                    print("Course:", resource["resource_title"])
                    print("Type:", resource["resource_type"])
                    print("Link:", resource["resource_url"])
                    print("-" * 50)

            else:
                print("No learning resources found for this skill.")
   