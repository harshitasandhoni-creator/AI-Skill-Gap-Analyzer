
from db_queries import get_all_roles, get_required_skills

from ml.semantic_matcher import SemanticMatcher

from ml.config import (
    REQUIRED_SKILL_WEIGHT,
    MATH_SKILL_WEIGHT,
    TOP_N_ROLES,
)


class RoleMatcher:

    def __init__(self):
        self.semantic_matcher = SemanticMatcher()

    # --------------------------------------------------
    # SEPARATE REQUIRED AND MATHEMATICAL SKILLS
    # --------------------------------------------------

    def separate_skills(self, skill_records):
        """
        Separate database skill records into required skills
        and mathematical skills.
        """

        required_skills = []
        math_skills = []

        for record in skill_records:

            skill_name = record["skill_name"]
            skill_type = record["skill_type"]

            if skill_type == "required":
                required_skills.append(skill_name)

            elif skill_type == "math":
                math_skills.append(skill_name)

        return required_skills, math_skills

    # --------------------------------------------------
    # MATCH ONE ROLE
    # --------------------------------------------------

    def match_role(self, student_skills, role):
        """
        Compare student skills with one job role.
        """

        role_id = role["role_id"]

        skill_records = get_required_skills(role_id)

        required_skills, math_skills = self.separate_skills(
            skill_records
        )

        required_result = self.semantic_matcher.match_skills(
            student_skills,
            required_skills
        )

        math_result = self.semantic_matcher.match_skills(
            student_skills,
            math_skills
        )

        required_coverage = required_result["coverage_score"]
        math_coverage = math_result["coverage_score"]

        overall_score = (
            required_coverage * REQUIRED_SKILL_WEIGHT
            + math_coverage * MATH_SKILL_WEIGHT
        )

        return {
            "role_id": role_id,
            "job_role": role["job_role"],
            "sector": role["sector"],
            "experience_requirement": role.get(
                "experience_requirement"
            ),
            "education_background": role.get(
                "education_background"
            ),
            "required_result": required_result,
            "math_result": math_result,
            "required_coverage": required_coverage,
            "math_coverage": math_coverage,
            "overall_score": overall_score,
        }

    # --------------------------------------------------
    # RANK ALL ROLES
    # --------------------------------------------------

    def rank_roles(self, student_skills, top_n=None):
        """
        Rank job roles based on student skill coverage.
        """

        if not student_skills:
            raise ValueError(
                "Please provide at least one student skill."
            )

        roles = get_all_roles()

        if not roles:
            raise ValueError(
                "No job roles found in the database."
            )

        ranked_roles = []

        for role in roles:

            result = self.match_role(
                student_skills,
                role
            )

            ranked_roles.append(result)

        ranked_roles.sort(
            key=lambda item: item["overall_score"],
            reverse=True
        )

        if top_n is None:
            top_n = TOP_N_ROLES

        return ranked_roles[:top_n]

    # --------------------------------------------------
    # DISPLAY SKILL MATCHING RESULTS
    # --------------------------------------------------

    def display_skill_result(self, title, result):

        print(f"\n{title}")
        print("-" * 65)

        # EXACT MATCHES
        print("\nVERIFIED EXACT MATCHES")

        if result["matched_skills"]:

            for item in result["matched_skills"]:
                print(
                    f"  {item['required_skill']} "
                    f"<-> {item['student_skill']}"
                )

        else:
            print("  None")

        # EQUIVALENT MATCHES
        print("\nVERIFIED EQUIVALENT MATCHES")

        if result["equivalent_matches"]:

            for item in result["equivalent_matches"]:
                print(
                    f"  {item['required_skill']} "
                    f"<-> {item['student_skill']}"
                )

        else:
            print("  None")

        # RELATED MATCHES
        print("\nPARTIAL RELATED MATCHES")

        if result["related_matches"]:

            for item in result["related_matches"]:
                print(
                    f"  {item['required_skill']} "
                    f"<-> {item['student_skill']} "
                    f"(Credit: {item['credit']})"
                )

        else:
            print("  None")

        # SEMANTIC SUGGESTIONS
        print("\nSEMANTIC SUGGESTIONS - NEEDS REVIEW")

        if result["semantic_suggestions"]:

            for item in result["semantic_suggestions"]:
                print(
                    f"  {item['required_skill']} "
                    f"<-> {item['student_skill']} "
                    f"(Similarity: {item['similarity']:.2f})"
                )

        else:
            print("  None")

        # MISSING SKILLS
        print("\nMISSING SKILLS")

        if result["missing_skills"]:

            for skill in result["missing_skills"]:
                print(f"  - {skill}")

        else:
            print("  None")

        # UNMATCHED STUDENT SKILLS
        print("\nOTHER STUDENT SKILLS")

        if result["unmatched_student_skills"]:

            for skill in result["unmatched_student_skills"]:
                print(f"  - {skill}")

        else:
            print("  None")

        # COVERAGE
        print("\nCOVERAGE SUMMARY")

        print(
            f"  Overall Coverage: "
            f"{result['coverage_score']:.2f}%"
        )

        print(
            f"  Strict Coverage: "
            f"{result['strict_coverage_score']:.2f}%"
        )

        print(
            f"  Average Verified Match Similarity: "
            f"{result['average_matched_similarity']:.2f}"
        )

    # --------------------------------------------------
    # DISPLAY ONE ROLE
    # --------------------------------------------------

    def display_role(self, result, rank):

        print("\n" + "#" * 70)

        print(
            f"RANK {rank}: {result['job_role']}"
        )

        print(
            f"Sector: {result['sector']}"
        )

        print("-" * 70)

        print(
            f"Overall Match: "
            f"{result['overall_score']:.2f}%"
        )

        print(
            f"Required Skill Coverage: "
            f"{result['required_coverage']:.2f}%"
        )

        print(
            f"Mathematics Skill Coverage: "
            f"{result['math_coverage']:.2f}%"
        )

        if result["experience_requirement"]:
            print(
                f"Experience Requirement: "
                f"{result['experience_requirement']}"
            )

        if result["education_background"]:
            print(
                f"Education Background: "
                f"{result['education_background']}"
            )

        self.display_skill_result(
            "REQUIRED SKILLS ANALYSIS",
            result["required_result"]
        )

        self.display_skill_result(
            "MATHEMATICAL SKILLS ANALYSIS",
            result["math_result"]
        )

    # --------------------------------------------------
    # DISPLAY ALL RANKED ROLES
    # --------------------------------------------------

    def display_ranked_roles(self, ranked_roles):

        print("\n")
        print("=" * 70)

        print(
            "       AI SKILL-GAP ANALYZER - ROLE RECOMMENDATIONS"
        )

        print("=" * 70)

        if not ranked_roles:
            print("No role recommendations available.")
            return

        for rank, result in enumerate(
            ranked_roles,
            start=1
        ):

            self.display_role(
                result,
                rank
            )

        print("\n" + "=" * 70)
        print("ROLE RANKING SUMMARY")
        print("=" * 70)

        for rank, result in enumerate(
            ranked_roles,
            start=1
        ):

            print(
                f"{rank}. {result['job_role']} "
                f"({result['overall_score']:.2f}%) "
                f"- {result['sector']}"
            )

        print("=" * 70)

    # --------------------------------------------------
    # MAIN RECOMMENDATION FUNCTION
    # --------------------------------------------------

    def recommend_roles(self, student_skills, top_n=None):

        ranked_roles = self.rank_roles(
            student_skills,
            top_n
        )

        self.display_ranked_roles(ranked_roles)

        return ranked_roles


# --------------------------------------------------
# RUN MODULE DIRECTLY
# --------------------------------------------------

if __name__ == "__main__":

    matcher = RoleMatcher()

    # Sample student profile.
    # Replace these with skills extracted from a resume later.

    student_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "Pandas",
        "NumPy",
        "Data Visualization",
        "Statistics",
        "Scikit-learn",
    ]

    recommendations = matcher.recommend_roles(
        student_skills,
        top_n=TOP_N_ROLES
    )
