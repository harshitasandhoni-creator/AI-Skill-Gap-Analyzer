
import unittest

from ml.resource_recommender import ResourceRecommender


class TestResourceRecommender(unittest.TestCase):

    def setUp(self):

        self.sample_resources = {
            "Python": [
                {
                    "resource_id": 1,
                    "title": "Python Course",
                    "url": "https://example.com/python",
                }
            ],
            "SQL": [
                {
                    "resource_id": 2,
                    "title": "SQL Course",
                    "url": "https://example.com/sql",
                }
            ],
            "Statistics": [
                {
                    "resource_id": 3,
                    "title": "Statistics Course",
                    "url": "https://example.com/statistics",
                }
            ],
            "Machine Learning": [
                {
                    "resource_id": 1,
                    "title": "Python Course",
                    "url": "https://example.com/python",
                }
            ],
        }

        self.calls = []

        def fake_loader(skill):
            self.calls.append(skill)
            return self.sample_resources.get(skill, [])

        self.recommender = ResourceRecommender(
            resource_loader=fake_loader
        )

    def create_gap(self, skill, status, skill_type="required", priority=1):

        return {
            "skill": skill,
            "skill_type": skill_type,
            "status": status,
            "priority_score": priority,
            "required_by_roles": ["Data Scientist"],
            "missing_in_roles": [],
            "partial_in_roles": [],
            "needs_review_in_roles": [],
        }

    def create_report(self, required=None, math=None):

        return {
            "required_skill_gaps": required or [],
            "math_skill_gaps": math or [],
        }

    def test_resources_are_retrieved(self):

        report = self.create_report(
            required=[self.create_gap("Python", "missing")]
        )

        result = self.recommender.recommend(report)

        self.assertEqual(
            result["summary"]["skills_with_resources"],
            1
        )

        self.assertEqual(
            result["required_recommendations"][0]["resource_count"],
            1
        )

    def test_missing_skills_are_prioritized(self):

        report = self.create_report(
            required=[
                self.create_gap("Python", "partial", priority=10),
                self.create_gap("SQL", "missing", priority=1),
            ]
        )

        result = self.recommender.recommend(report)

        self.assertEqual(
            result["learning_sequence"][0]["skill"],
            "SQL"
        )

    def test_partial_skills_follow_missing_skills(self):

        report = self.create_report(
            required=[
                self.create_gap("Python", "partial", priority=10),
                self.create_gap("SQL", "missing", priority=1),
            ]
        )

        result = self.recommender.recommend(report)

        statuses = [
            item["status"]
            for item in result["learning_sequence"]
        ]

        self.assertEqual(statuses, ["missing", "partial"])

    def test_semantic_suggestions_are_included_for_review(self):

        report = self.create_report(
            required=[
                self.create_gap(
                    "Machine Learning",
                    "needs_review"
                )
            ]
        )

        result = self.recommender.recommend(report)

        self.assertEqual(
            result["learning_sequence"][0]["status"],
            "needs_review"
        )

    def test_duplicate_resources_are_removed(self):

        report = self.create_report(
            required=[
                self.create_gap("Python", "missing"),
                self.create_gap("Machine Learning", "missing"),
            ]
        )

        result = self.recommender.recommend(report)

        self.assertEqual(
            result["summary"]["total_unique_resources"],
            1
        )

    def test_math_and_required_resources_are_separate(self):

        report = self.create_report(
            required=[
                self.create_gap("Python", "missing")
            ],
            math=[
                self.create_gap(
                    "Statistics",
                    "missing",
                    skill_type="math"
                )
            ]
        )

        result = self.recommender.recommend(report)

        self.assertEqual(
            len(result["required_recommendations"]),
            1
        )

        self.assertEqual(
            len(result["math_recommendations"]),
            1
        )

    def test_missing_resource_is_handled(self):

        report = self.create_report(
            required=[
                self.create_gap("Unknown Skill", "missing")
            ]
        )

        result = self.recommender.recommend(report)

        self.assertEqual(
            result["summary"]["skills_without_resources"],
            1
        )

        self.assertEqual(
            result["learning_sequence"][0]["resources"],
            []
        )

    def test_resource_loader_error_is_handled(self):

        def failing_loader(skill):
            raise RuntimeError("Database unavailable")

        recommender = ResourceRecommender(
            resource_loader=failing_loader
        )

        report = self.create_report(
            required=[
                self.create_gap("Python", "missing")
            ]
        )

        result = recommender.recommend(report)

        self.assertEqual(
            result["summary"]["skills_without_resources"],
            1
        )

    def test_empty_report(self):

        result = self.recommender.recommend({})

        self.assertEqual(
            result["summary"]["total_skills"],
            0
        )

        self.assertEqual(
            result["all_resources"],
            []
        )

    def test_loader_is_called_for_each_skill(self):

        report = self.create_report(
            required=[
                self.create_gap("Python", "missing"),
                self.create_gap("SQL", "missing"),
            ]
        )

        self.recommender.recommend(report)

        self.assertCountEqual(
            self.calls,
            ["Python", "SQL"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
