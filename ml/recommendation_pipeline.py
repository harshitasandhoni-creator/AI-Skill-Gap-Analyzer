
"""
Recommendation Pipeline
-----------------------

Integrates the complete ML recommendation workflow:

1. Preprocess student skills.
2. Normalize and remove duplicate skills.
3. Match student skills against available job roles.
4. Rank the most suitable roles.
5. Analyze missing required and mathematical skills.
6. Recommend learning resources.
7. Generate a consolidated recommendation report.
"""

from ml.text_preprocessor import TextPreprocessor
from ml.skill_normalizer import SkillNormalizer
from ml.role_matcher import RoleMatcher
from ml.skill_gap_analyzer import SkillGapAnalyzer
from ml.resource_recommender import ResourceRecommender

from ml.config import TOP_N_ROLES


class RecommendationPipeline:

    def __init__(
        self,
        role_matcher=None,
        gap_analyzer=None,
        resource_recommender=None
    ):
        """
        Initialize all pipeline components.

        Optional dependency injection makes the pipeline
        easier to test independently.
        """

        self.preprocessor = TextPreprocessor()
        self.normalizer = SkillNormalizer()

        self.role_matcher = role_matcher or RoleMatcher()

        self.gap_analyzer = (
            gap_analyzer or SkillGapAnalyzer()
        )

        self.resource_recommender = (
            resource_recommender or ResourceRecommender()
        )

    # --------------------------------------------------
    # 1. Prepare student skills
    # --------------------------------------------------

    def prepare_skills(self, student_skills):
        """
        Preprocess, normalize and deduplicate student skills.

        Args:
            student_skills: List, tuple or set of skills.

        Returns:
            list: Cleaned and normalized skills.
        """

        if not isinstance(student_skills, (list, tuple, set)):
            raise TypeError(
                "student_skills must be a list, tuple, or set."
            )

        prepared_skills = []
        seen_skills = set()

        for skill in student_skills:

            if not isinstance(skill, str):
                continue

            cleaned = self.preprocessor.preprocess(skill)

            if not cleaned:
                continue

            normalized = self.normalizer.normalize_skill(cleaned)

            if not normalized:
                continue

            key = normalized.strip().lower()

            if key not in seen_skills:
                prepared_skills.append(normalized)
                seen_skills.add(key)

        if not prepared_skills:
            raise ValueError(
                "No valid skills found after preprocessing."
            )

        return prepared_skills

    # --------------------------------------------------
    # 2. Generate empty resource report
    # --------------------------------------------------

    @staticmethod
    def _empty_resource_report():
        """
        Return a consistent empty resource report
        when resource recommendations are disabled.
        """

        return {
            "required_recommendations": [],
            "math_recommendations": [],
            "learning_sequence": [],
            "all_resources": [],
            "summary": {
                "total_skills": 0,
                "skills_with_resources": 0,
                "skills_without_resources": 0,
                "total_resources_fetched": 0,
                "total_unique_resources": 0,
                "duplicate_resources_removed": 0,
                "per_skill_duplicates_removed": {},
                "required_skills": 0,
                "math_skills": 0
            }
        }

    # --------------------------------------------------
    # 3. Execute complete recommendation pipeline
    # --------------------------------------------------

    def run(
        self,
        student_skills,
        top_n=None,
        include_resources=True
    ):
        """
        Execute the complete recommendation workflow.

        Args:
            student_skills: Student's extracted skills.
            top_n: Number of job roles to recommend.
            include_resources: Whether to fetch learning resources.

        Returns:
            dict: Consolidated recommendation report.
        """

        # Step 1: Preprocess and normalize skills
        prepared_skills = self.prepare_skills(student_skills)

        print("\n" + "=" * 65)
        print("STUDENT SKILL PREPARATION")
        print("=" * 65)

        print(f"Input skills: {len(student_skills)}")
        print(f"Valid unique skills: {len(prepared_skills)}")

        for skill in prepared_skills:
            print(f"  - {skill}")

        # Step 2: Match and rank job roles
        print("\nMatching student skills with job roles...")

        ranked_roles = self.role_matcher.rank_roles(
            student_skills=prepared_skills,
            top_n=top_n if top_n is not None else TOP_N_ROLES
        )

        if not ranked_roles:
            raise RuntimeError(
                "No job-role recommendations were generated."
            )

        # Step 3: Analyze skill gaps
        print("Analyzing required and mathematical skill gaps...")

        skill_gap_report = self.gap_analyzer.analyze(
            ranked_roles,
            include_resources=False
        )

        # Step 4: Recommend learning resources
        if include_resources:

            print("Fetching learning resources...")

            resource_report = self.resource_recommender.recommend(
                skill_gap_report
            )

        else:
            resource_report = self._empty_resource_report()

        # Step 5: Generate consolidated summary
        summary = {
            "total_input_skills": len(student_skills),
            "total_valid_skills": len(prepared_skills),
            "total_roles_recommended": len(ranked_roles),
            "total_required_skill_gaps": len(
                skill_gap_report.get("required_skill_gaps", [])
            ),
            "total_math_skill_gaps": len(
                skill_gap_report.get("math_skill_gaps", [])
            ),
            "total_learning_resources": resource_report.get(
                "summary", {}
            ).get("total_unique_resources", 0)
        }

        # Step 6: Return complete result
        result = {
            "input_skills": prepared_skills,
            "total_input_skills": len(prepared_skills),
            "ranked_roles": ranked_roles,
            "total_roles_recommended": len(ranked_roles),
            "skill_gap_report": skill_gap_report,
            "resource_report": resource_report,
            "summary": summary
        }

        return result

    # --------------------------------------------------
    # 4. Display consolidated report
    # --------------------------------------------------

    def display_report(self, result):
        """
        Display role recommendations, skill gaps
        and learning resources.
        """

        if not isinstance(result, dict):
            raise TypeError("result must be a dictionary.")

        print("\n")
        print("#" * 70)
        print("             COMPLETE AI SKILL GAP REPORT")
        print("#" * 70)

        # Student skills
        print("\nSTUDENT SKILLS")
        print("-" * 70)

        for skill in result.get("input_skills", []):
            print(f"  - {skill}")

        # Ranked roles
        print("\nRECOMMENDED JOB ROLES")
        print("-" * 70)

        self.role_matcher.display_ranked_roles(
            result.get("ranked_roles", [])
        )

        # Skill gaps
        print("\nSKILL GAP ANALYSIS")
        print("-" * 70)

        self.gap_analyzer.display_report(
            result.get("skill_gap_report", {})
        )

        # Learning resources
        print("\nLEARNING RESOURCE RECOMMENDATIONS")
        print("-" * 70)

        self.resource_recommender.display_report(
            result.get("resource_report", {})
        )

        # Final summary
        print("\nPIPELINE SUMMARY")
        print("-" * 70)

        for key, value in result.get("summary", {}).items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        print("\n" + "#" * 70)
        print("             END OF RECOMMENDATION REPORT")
        print("#" * 70)


# ------------------------------------------------------
# 5. Standalone execution
# ------------------------------------------------------

if __name__ == "__main__":

    # Sample student skills
    sample_student_skills = [
        "Python",
        "C++",
        "SQL",
        "Machine Learning",
        "Scikit-Learn",
        "Pandas",
        "NumPy",
        "Statistics",
        "Probability",
        "Linear Algebra",
        "Data Visualization",
        "Git",
        "HTML",
        "CSS"
    ]

    # Initialize pipeline
    pipeline = RecommendationPipeline()

    # Execute pipeline
    result = pipeline.run(
        student_skills=sample_student_skills,
        top_n=5,
        include_resources=True
    )

    # Display complete report
    pipeline.display_report(result)
