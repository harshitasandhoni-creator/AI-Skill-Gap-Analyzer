
import unittest

from ml.skill_gap_analyzer import SkillGapAnalyzer


class TestSkillGapAnalyzer(unittest.TestCase):

    def setUp(self):

        self.analyzer = SkillGapAnalyzer(
            resource_loader=lambda skill: []
        )

    def create_role(
        self,
        role_name,
        required_details,
        math_details=None
    ):

        return {
            "job_role": role_name,
            "overall_score": 30.0,
            "required_result": {
                "requirement_details": required_details
            },
            "math_result": {
                "requirement_details": math_details or []
            },
        }

    def create_detail(self, skill, match_type):

        return {
            "required_skill": skill,
            "match_type": match_type,
            "matched_student_skill": None,
            "similarity": 0.0,
            "credit": 0.0,
        }

    def test_missing_skill_is_identified(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [self.create_detail("Python", "missing")]
            )
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        gaps = report["required_skill_gaps"]

        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["skill"], "Python")
        self.assertEqual(gaps[0]["status"], "missing")

    def test_related_skill_is_partial(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [self.create_detail("Probability", "related")]
            )
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        gap = report["required_skill_gaps"][0]

        self.assertEqual(gap["status"], "partial")
        self.assertIn(
            "Data Scientist",
            gap["partial_in_roles"]
        )

    def test_semantic_suggestion_needs_review(self):

        roles = [
            self.create_role(
                "ML Engineer",
                [
                    self.create_detail(
                        "Deep Learning",
                        "semantic_suggestion"
                    )
                ]
            )
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        gap = report["required_skill_gaps"][0]

        self.assertEqual(gap["status"], "needs_review")

    def test_exact_match_is_not_a_gap(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [
                    self.create_detail("Python", "exact"),
                    self.create_detail("SQL", "equivalent"),
                ]
            )
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        self.assertEqual(report["required_skill_gaps"], [])

    def test_same_skill_across_multiple_roles_is_grouped(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [self.create_detail("Python", "missing")]
            ),
            self.create_role(
                "ML Engineer",
                [self.create_detail("Python", "missing")]
            ),
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        gaps = report["required_skill_gaps"]

        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["role_count"], 2)
        self.assertEqual(
            len(gaps[0]["required_by_roles"]),
            2
        )

    def test_math_and_required_skills_are_separate(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [
                    self.create_detail("Python", "missing")
                ],
                [
                    self.create_detail("Calculus", "missing")
                ]
            )
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        self.assertEqual(
            len(report["required_skill_gaps"]),
            1
        )

        self.assertEqual(
            len(report["math_skill_gaps"]),
            1
        )

        self.assertEqual(
            report["math_skill_gaps"][0]["skill"],
            "Calculus"
        )

    def test_missing_has_priority_over_partial(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [
                    self.create_detail("Python", "related")
                ]
            ),
            self.create_role(
                "ML Engineer",
                [
                    self.create_detail("Python", "missing")
                ]
            ),
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        gap = report["required_skill_gaps"][0]

        self.assertEqual(gap["status"], "missing")
        self.assertEqual(len(gap["missing_in_roles"]), 1)
        self.assertEqual(len(gap["partial_in_roles"]), 1)

    def test_empty_role_list(self):

        report = self.analyzer.analyze([])

        self.assertEqual(report["total_roles_analyzed"], 0)
        self.assertEqual(report["required_skill_gaps"], [])
        self.assertEqual(report["math_skill_gaps"], [])

    def test_priority_learning_path_is_sorted(self):

        roles = [
            self.create_role(
                "Data Scientist",
                [
                    self.create_detail("Python", "related"),
                    self.create_detail("SQL", "missing"),
                    self.create_detail("Git", "missing"),
                ]
            )
        ]

        report = self.analyzer.analyze(
            roles,
            include_resources=False
        )

        priorities = [
            item["priority_score"]
            for item in report["priority_learning_path"]
        ]

        self.assertEqual(
            priorities,
            sorted(priorities, reverse=True)
        )

    def test_resource_loader_is_called(self):

        calls = []

        def fake_loader(skill):
            calls.append(skill)
            return ["Resource A", "Resource B"]

        analyzer = SkillGapAnalyzer(
            resource_loader=fake_loader
        )

        roles = [
            self.create_role(
                "Data Scientist",
                [self.create_detail("Python", "missing")]
            )
        ]

        report = analyzer.analyze(
            roles,
            include_resources=True
        )

        self.assertEqual(calls, ["Python"])

        self.assertEqual(
            report["required_skill_gaps"][0]["resources"],
            ["Resource A", "Resource B"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)