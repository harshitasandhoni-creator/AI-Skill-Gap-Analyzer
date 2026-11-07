
def analyze_skill_gap(required_skills, student_skills):

    # Normalize skills for accurate comparison
    required = {
        skill.strip().lower()
        for skill in required_skills
    }

    student = {
        skill.strip().lower()
        for skill in student_skills
    }

    # Find matching and missing skills
    matched_skills = sorted(required & student)
    missing_skills = sorted(required - student)

    # Calculate match percentage
    total_required = len(required)

    if total_required == 0:
        match_percentage = 0
    else:
        match_percentage = round(
            (len(matched_skills) / total_required) * 100,
            2
        )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage,
        "total_required_skills": total_required
    }
