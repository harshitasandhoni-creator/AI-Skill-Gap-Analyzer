
import re

def normalize_skill(skill):
    """
    Standardize skill names before comparison.
    Example: ' PYTHON ' becomes 'python'.
    """
    skill = skill.strip().lower()
    skill = re.sub(r"[^a-z0-9+#. ]", "", skill)
    skill = re.sub(r"\s+", " ", skill)

    return skill


def analyze_skill_gap(required_skills, student_skills):
    """
    Compare student skills with the skills required
    for a selected job role.
    """

    # Normalize and remove empty values
    required = list(dict.fromkeys(
        normalize_skill(skill)
        for skill in required_skills
        if skill.strip()
    ))

    student = set(
        normalize_skill(skill)
        for skill in student_skills
        if skill.strip()
    )

    # Find matched and missing skills
    matched_skills = [
        skill for skill in required if skill in student
    ]

    missing_skills = [
        skill for skill in required if skill not in student
    ]

    # Calculate percentages
    total_skills = len(required)
    matched_count = len(matched_skills)

    if total_skills == 0:
        match_percentage = 0
    else:
        match_percentage = (
            matched_count / total_skills
        ) * 100

    gap_percentage = 100 - match_percentage

    # Return analysis results
    return {
        "total_required_skills": total_skills,
        "matched_count": matched_count,
        "missing_count": len(missing_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "initial_match_percentage": round(match_percentage, 2),
        "skill_gap_percentage": round(gap_percentage, 2)
    }
