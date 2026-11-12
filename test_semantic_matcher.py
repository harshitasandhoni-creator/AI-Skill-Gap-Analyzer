
import unittest
import numpy as np

from ml.semantic_matcher import SemanticMatcher
from ml.skill_normalizer import SkillNormalizer
from ml.skill_relationships import SkillRelationships


class TestSemanticMatcher(unittest.TestCase):

    def setUp(self):
        # Avoid downloading/loading the embedding model during unit tests.
        self.matcher = SemanticMatcher.__new__(SemanticMatcher)

        self.matcher.normalizer = SkillNormalizer()
        self.matcher.relationships = SkillRelationships()

        # Default similarity matrix: all similarities are zero.
        self.matcher.calculate_similarity_matrix = (
            lambda students, requirements:
            np.zeros((len(students), len(requirements)))
        )

    def test_exact_match(self):
        result = self.matcher.match_skills(
            ["Python"],
            ["Python"]
        )

        self.assertEqual(len(result["matched_skills"]), 1)
        self.assertEqual(result["coverage_score"], 100.0)
        self.assertEqual(result["strict_coverage_score"], 100.0)

    def test_equivalent_match(self):
        result = self.matcher.match_skills(
            ["Python"],
            ["Python Programming"]
        )

        self.assertEqual(len(result["equivalent_matches"]), 1)
        self.assertEqual(result["coverage_score"], 100.0)
        self.assertEqual(result["strict_coverage_score"], 100.0)

    def test_related_skill_can_support_multiple_requirements(self):
        result = self.matcher.match_skills(
            ["Statistics"],
            [
                "Probability",
                "Hypothesis Testing",
                "Descriptive Statistics",
            ]
        )

        self.assertEqual(len(result["related_matches"]), 3)
        self.assertEqual(result["coverage_score"], 25.0)
        self.assertEqual(result["strict_coverage_score"], 0.0)

    def test_related_skill_use_is_capped_at_three(self):
        result = self.matcher.match_skills(
            ["Statistics"],
            [
                "Probability",
                "Hypothesis Testing",
                "Descriptive Statistics",
                "Inferential Statistics",
            ]
        )

        self.assertEqual(len(result["related_matches"]), 3)
        self.assertEqual(len(result["missing_skills"]), 1)
        self.assertEqual(result["coverage_score"], 18.75)

    def test_unrelated_skill_is_missing(self):
        result = self.matcher.match_skills(
            ["HTML"],
            ["Calculus"]
        )

        self.assertEqual(len(result["related_matches"]), 0)
        self.assertEqual(result["missing_skills"], ["Calculus"])
        self.assertEqual(result["coverage_score"], 0.0)

    def test_exact_match_has_priority_over_related_match(self):
        result = self.matcher.match_skills(
            ["Python"],
            ["Python", "Python Programming"]
        )

        # Python is used for the exact requirement.
        # It must not be reused for the equivalent requirement.
        self.assertEqual(len(result["matched_skills"]), 1)
        self.assertEqual(len(result["equivalent_matches"]), 0)
        self.assertEqual(len(result["missing_skills"]), 1)

    def test_semantic_suggestion_gets_zero_credit(self):
        self.matcher.calculate_similarity_matrix = (
            lambda students, requirements:
            np.array([[0.85]])
        )

        result = self.matcher.match_skills(
            ["Some Related Concept"],
            ["A Different Technical Skill"]
        )

        self.assertEqual(len(result["semantic_suggestions"]), 1)
        self.assertEqual(result["coverage_score"], 0.0)
        self.assertEqual(result["strict_coverage_score"], 0.0)

    def test_duplicate_student_skills_are_removed(self):
        result = self.matcher.match_skills(
            ["Python", "python", "PYTHON"],
            ["Python"]
        )

        self.assertEqual(len(result["matched_skills"]), 1)
        self.assertEqual(result["coverage_score"], 100.0)

    def test_duplicate_requirements_are_removed(self):
        result = self.matcher.match_skills(
            ["Python"],
            ["Python", "python"]
        )

        self.assertEqual(len(result["requirement_details"]), 1)
        self.assertEqual(result["coverage_score"], 100.0)

    def test_empty_requirements(self):
        result = self.matcher.match_skills(
            ["Python", "SQL"],
            []
        )

        self.assertEqual(result["coverage_score"], 0.0)
        self.assertEqual(
            result["unmatched_student_skills"],
            ["Python", "SQL"]
        )

    def test_exact_match_is_not_reused_for_related_requirements(self):
        result = self.matcher.match_skills(
            ["Statistics"],
            ["Statistics", "Probability"]
        )

        self.assertEqual(len(result["matched_skills"]), 1)
        self.assertEqual(len(result["related_matches"]), 0)
        self.assertEqual(result["missing_skills"], ["Probability"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
