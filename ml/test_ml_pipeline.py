
"""
Integration tests for the Recommendation Pipeline.

Tests:
1. Skill preprocessing and normalization.
2. Duplicate skill removal.
3. Invalid input handling.
4. Role ranking integration.
5. Skill-gap analysis integration.
6. Resource recommendation integration.
7. Pipeline execution without resources.
8. Complete output structure.
"""

import unittest
from unittest.mock import Mock

from ml.recommendation_pipeline import RecommendationPipeline


# --------------------------------------------------
# Mock components
# --------------------------------------------------

class MockRoleMatcher:

    def rank_roles(self, student_skills, top_n=None):

        return [
            {
                "role_id": 1,
                "job_role": "Data Scientist",
                "sector": "Technology",
                "experience_requirement": "Entry Level",
                "education_background": "B.Tech",
                "required_coverage": 0.75,
                "math_coverage": 0.50,
                "overall_score": 0.70,
                "required_result": {
                    "requirement_details": [
                        {
                            "required_skill": "Python",
                            "matched_student_skill": "python",
                            "match_type": "exact",
                            "similarity": 1.0,
                            "credit": 1.0
                        }
                    ]
                },
                "math_result": {
                    "requirement_details": [
                        {
                            "required_skill": "Statistics",
                            "matched_student_skill": None,
                            "match_type": "missing",
                            "similarity": 0.0,
                            "credit": 0.0
                        }
                    ]
                }
            }
        ][:top_n]


class MockGapAnalyzer:

    def __init__(self):
        self.called = False

    def analyze(self, ranked_roles, include_resources=True):

        self.called = True

        return {
            "total_roles_analyzed": len(ranked_roles),

            "required_skill_gaps": [
                {
                    "skill": "Machine Learning",
                    "status": "missing",
                    "priority_score": 6.5,
                    "relevant_roles": ["Data Scientist"]
                }
            ],

            "math_skill_gaps": [
                {
                    "skill": "Statistics",
                    "status": "missing",
                    "priority_score": 4.5,
                    "relevant_roles": ["Data Scientist"]
                }
            ],

            "priority_learning_path": [],

            "summary": {
                "missing_skills": 2,
                "partial_skills": 0,
                "skills_needing_review": 0
            }
        }


class MockResourceRecommender:

    def __init__(self):
        self.called = False

    def recommend(self, skill_gap_report):

        self.called = True

        return {
            "required_recommendations": [],
            "math_recommendations": [],
            "learning_sequence": [],
            "all_resources": [],

            "summary": {
                "total_skills": 2,
                "skills_with_resources": 2,
                "skills_without_resources": 0,
                "total_resources_fetched": 2,
                "total_unique_resources": 2,
                "duplicate_resources_removed": 0,
                "per_skill_duplicates_removed": {},
                "required_skills": 1,
                "math_skills": 1
            }
        }


# --------------------------------------------------
# Test Recommendation Pipeline
# --------------------------------------------------

class TestRecommendationPipeline(unittest.TestCase):

    def setUp(self):

        self.role_matcher = MockRoleMatcher()
        self.gap_analyzer = MockGapAnalyzer()
        self.resource_recommender = MockResourceRecommender()

        self.pipeline = RecommendationPipeline(
            role_matcher=self.role_matcher,
            gap_analyzer=self.gap_analyzer,
            resource_recommender=self.resource_recommender
        )

    # --------------------------------------------------
    # 1. Skill preparation tests
    # --------------------------------------------------

    def test_prepare_valid_skills(self):

        skills = [
            "Python",
            "SQL",
            "Machine Learning"
        ]

        result = self.pipeline.prepare_skills(skills)

        self.assertEqual(len(result), 3)
        self.assertIn("python", [s.lower() for s in result])

    def test_remove_duplicate_skills(self):

        skills = [
            "Python",
            "python",
            "PYTHON",
            "SQL"
        ]

        result = self.pipeline.prepare_skills(skills)

        self.assertEqual(len(result), 2)

    def test_ignore_invalid_skill_entries(self):

        skills = [
            "Python",
            "",
            None,
            123,
            "SQL"
        ]

        result = self.pipeline.prepare_skills(skills)

        self.assertEqual(len(result), 2)

    def test_empty_skill_list_raises_error(self):

        with self.assertRaises(ValueError):
            self.pipeline.prepare_skills([])

    def test_invalid_skill_input_type_raises_error(self):

        with self.assertRaises(TypeError):
            self.pipeline.prepare_skills("Python")

    # --------------------------------------------------
    # 2. Role ranking tests
    # --------------------------------------------------

    def test_role_ranking_integration(self):

        result = self.pipeline.run(
            student_skills=["Python", "SQL"],
            top_n=5,
            include_resources=False
        )

        self.assertEqual(len(result["ranked_roles"]), 1)

        self.assertEqual(
            result["ranked_roles"][0]["job_role"],
            "Data Scientist"
        )

    def test_top_n_is_passed_to_role_matcher(self):

        mock_role_matcher = Mock()

        mock_role_matcher.rank_roles.return_value = [
            {
                "job_role": "Data Scientist",
                "overall_score": 0.75,
                "required_result": {"requirement_details": []},
                "math_result": {"requirement_details": []}
            }
        ]

        pipeline = RecommendationPipeline(
            role_matcher=mock_role_matcher,
            gap_analyzer=self.gap_analyzer,
            resource_recommender=self.resource_recommender
        )

        pipeline.run(
            student_skills=["Python"],
            top_n=3,
            include_resources=False
        )

        mock_role_matcher.rank_roles.assert_called_once_with(
            student_skills=["python"],
            top_n=3
        )

    # --------------------------------------------------
    # 3. Skill-gap analysis tests
    # --------------------------------------------------

    def test_skill_gap_analysis_integration(self):

        result = self.pipeline.run(
            student_skills=["Python", "SQL"],
            include_resources=False
        )

        self.assertTrue(self.gap_analyzer.called)

        self.assertIn(
            "skill_gap_report",
            result
        )

        self.assertEqual(
            len(result["skill_gap_report"]["required_skill_gaps"]),
            1
        )

        self.assertEqual(
            len(result["skill_gap_report"]["math_skill_gaps"]),
            1
        )

    # --------------------------------------------------
    # 4. Resource recommendation tests
    # --------------------------------------------------

    def test_resource_recommendations_enabled(self):

        result = self.pipeline.run(
            student_skills=["Python"],
            include_resources=True
        )

        self.assertTrue(self.resource_recommender.called)

        self.assertEqual(
            result["resource_report"]["summary"]["total_unique_resources"],
            2
        )

    def test_resource_recommendations_disabled(self):

        result = self.pipeline.run(
            student_skills=["Python"],
            include_resources=False
        )

        self.assertFalse(self.resource_recommender.called)

        self.assertEqual(
            result["resource_report"]["summary"]["total_unique_resources"],
            0
        )

    # --------------------------------------------------
    # 5. Complete pipeline output tests
    # --------------------------------------------------

    def test_complete_pipeline_output_structure(self):

        result = self.pipeline.run(
            student_skills=[
                "Python",
                "SQL",
                "Machine Learning"
            ]
        )

        expected_keys = [
            "input_skills",
            "total_input_skills",
            "ranked_roles",
            "total_roles_recommended",
            "skill_gap_report",
            "resource_report",
            "summary"
        ]

        for key in expected_keys:
            self.assertIn(key, result)

    def test_pipeline_summary_values(self):

        result = self.pipeline.run(
            student_skills=["Python", "SQL"]
        )

        summary = result["summary"]

        self.assertEqual(summary["total_input_skills"], 2)
        self.assertEqual(summary["total_valid_skills"], 2)
        self.assertEqual(summary["total_roles_recommended"], 1)
        self.assertEqual(summary["total_required_skill_gaps"], 1)
        self.assertEqual(summary["total_math_skill_gaps"], 1)
        self.assertEqual(summary["total_learning_resources"], 2)

    def test_no_role_recommendations_raises_error(self):

        mock_role_matcher = MockRoleMatcher()
        mock_role_matcher.rank_roles = Mock(return_value=[])

        pipeline = RecommendationPipeline(
            role_matcher=mock_role_matcher,
            gap_analyzer=self.gap_analyzer,
            resource_recommender=self.resource_recommender
        )

        with self.assertRaises(RuntimeError):

            pipeline.run(
                student_skills=["Python"]
            )

    # --------------------------------------------------
    # 6. Report display test
    # --------------------------------------------------

    def test_display_report(self):

        result = self.pipeline.run(
            student_skills=["Python"],
            include_resources=False
        )

        # Ensure displaying the report does not raise an error.
        with unittest.mock.patch("builtins.print"):

            with unittest.mock.patch.object(
                self.role_matcher,
                "display_ranked_roles",
                create=True
            ):

                with unittest.mock.patch.object(
                    self.gap_analyzer,
                    "display_report",
                    create=True
                ):

                    with unittest.mock.patch.object(
                        self.resource_recommender,
                        "display_report",
                        create=True
                    ):

                        self.pipeline.display_report(result)


# --------------------------------------------------
# Run tests
# --------------------------------------------------

if __name__ == "__main__":

    unittest.main(verbosity=2)
