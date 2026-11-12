
"""
Resume and Manual Input Integration
-----------------------------------

Connects resume parsing and manual skill input
to the existing ML recommendation pipeline.
"""

from ml.recommendation_pipeline import RecommendationPipeline
from resume_parsing.resume_info import parse_resume

class ResumeRecommendationSystem:

    def __init__(self, pipeline=None):
        self.pipeline = pipeline if pipeline is not None else RecommendationPipeline()

    # --------------------------------------------
    # 1. Common recommendation function
    # --------------------------------------------

    def _generate_recommendations(
        self,
        student_skills,
        candidate_name=None,
        top_n=5,
        include_resources=True
    ):

        if not isinstance(student_skills, (list, tuple, set)):
            raise TypeError("Skills must be provided as a list.")

        student_skills = [
            skill.strip()
            for skill in student_skills
            if isinstance(skill, str) and skill.strip()
        ]

        if not student_skills:
            return {
                "error": "No valid skills were provided.",
                "candidate_name": candidate_name,
                "extracted_skills": []
            }

        # Run the existing ML recommendation pipeline
        result = self.pipeline.run(
            student_skills=student_skills,
            top_n=top_n,
            include_resources=include_resources
        )

        return {
            "candidate_name": candidate_name,
            "input_source": None,
            "extracted_skills": student_skills,
            "total_extracted_skills": len(student_skills),
            "recommendations": result
        }

    # --------------------------------------------
    # 2. Resume PDF input
    # --------------------------------------------

    def recommend_from_resume(
        self,
        pdf_path,
        top_n=5,
        include_resources=True
    ):

        # Parse the resume
        resume_data = parse_resume(pdf_path)

        if "error" in resume_data:
            return resume_data

        student_skills = resume_data.get("skills", [])
        candidate_name = resume_data.get("candidate_name")

        if not student_skills:
            return {
                "error": "No skills were extracted from the resume.",
                "candidate_name": candidate_name,
                "extracted_skills": [],
                "total_extracted_skills": 0
            }

        result = self._generate_recommendations(
            student_skills=student_skills,
            candidate_name=candidate_name,
            top_n=top_n,
            include_resources=include_resources
        )

        result["input_source"] = "resume"

        return result

    # --------------------------------------------
    # 3. Manual skill input
    # --------------------------------------------

    def recommend_from_manual_skills(
        self,
        student_skills,
        top_n=5,
        include_resources=True,
        candidate_name=None
    ):

        if isinstance(student_skills, str):
            student_skills = student_skills.split(",")

        result = self._generate_recommendations(
            student_skills=student_skills,
            candidate_name=candidate_name,
            top_n=top_n,
            include_resources=include_resources
        )

        result["input_source"] = "manual"

        return result

    # --------------------------------------------
    # 4. Display final result
    # --------------------------------------------

    def display_report(self, result):

        if "error" in result:
            print("Error:", result["error"])
            return

        print("\n" + "=" * 70)
        print("          AI SKILL GAP RECOMMENDATION REPORT")
        print("=" * 70)

        print("\nCandidate:", result.get("candidate_name") or "Not provided")
        print("Input source:", result.get("input_source"))

        print("\nSkills provided:")

        for skill in result["extracted_skills"]:
            print("-", skill)

        print(
            "\nTotal extracted skills:",
            result["total_extracted_skills"]
        )

        print("\n" + "=" * 70)
        print("             ML RECOMMENDATION RESULTS")
        print("=" * 70)

        self.pipeline.display_report(
            result["recommendations"]
        )


# --------------------------------------------
# 5. Example execution
# --------------------------------------------

if __name__ == "__main__":

    system = ResumeRecommendationSystem()

    print("Choose your input method:")
    print("1. Upload resume PDF")
    print("2. Enter skills manually")

    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":

        pdf_path = input("Enter resume PDF path: ").strip()

        result = system.recommend_from_resume(
            pdf_path=pdf_path,
            top_n=5,
            include_resources=True
        )

    elif choice == "2":

        skills = input(
            "Enter your skills separated by commas: "
        )

        result = system.recommend_from_manual_skills(
            student_skills=skills,
            top_n=5,
            include_resources=True
        )

    else:
        print("Invalid choice.")
        raise SystemExit(1)

    system.display_report(result)
