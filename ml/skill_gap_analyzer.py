
from collections import defaultdict

from db_queries import get_learning_resources
from ml.skill_normalizer import SkillNormalizer
from ml.config import MAX_RESOURCES_PER_SKILL


class SkillGapAnalyzer:
    """
    Converts ranked role-matching results into a prioritized
    skill-gap report.

    Missing skills receive the highest priority.
    Related matches receive partial-improvement priority.
    Semantic suggestions are flagged for manual review.
    """

    def __init__(self, resource_loader=None):

        self.normalizer = SkillNormalizer()

        # Allows tests to supply a mock resource loader.
        self.resource_loader = (
            resource_loader
            if resource_loader is not None
            else get_learning_resources
        )

    def normalize_key(self, skill):
        """Create a consistent key for grouping skill names."""

        normalized = self.normalizer.normalize_skill(skill)

        if not normalized:
            return ""

        return normalized.strip().lower()

    def _get_priority_points(self, skill_type, match_type):
        """
        Higher points mean greater learning priority.

        Required skills generally receive more weight than
        mathematical skills.
        """

        if skill_type == "required":

            if match_type == "missing":
                return 3.0

            if match_type == "related":
                return 2.0

            if match_type == "semantic_suggestion":
                return 1.0

        elif skill_type == "math":

            if match_type == "missing":
                return 2.0

            if match_type == "related":
                return 1.5

            if match_type == "semantic_suggestion":
                return 0.75

        return 0.0

    def _collect_skill_gaps(self, ranked_roles):
        """
        Read requirement_details from every ranked role
        and collect missing, partial, and unverified skills.
        """

        collected = {}

        for rank, role_result in enumerate(ranked_roles, start=1):

            role_name = role_result.get(
                "job_role",
                "Unknown role"
            )

            role_score = role_result.get(
                "overall_score",
                0.0
            )

            result_sections = [
                ("required", role_result.get("required_result", {})),
                ("math", role_result.get("math_result", {})),
            ]

            for skill_type, section in result_sections:

                details = section.get("requirement_details", [])

                for detail in details:

                    match_type = detail.get("match_type")

                    # Exact and equivalent matches are already satisfied.
                    if match_type not in (
                        "missing",
                        "related",
                        "semantic_suggestion"
                    ):
                        continue

                    skill_name = detail.get("required_skill")

                    if not skill_name:
                        continue

                    key = self.normalize_key(skill_name)

                    if not key:
                        continue

                    if key not in collected:

                        collected[key] = {
                            "skill": skill_name,
                            "skill_type": skill_type,
                            "missing_roles": [],
                            "partial_roles": [],
                            "review_roles": [],
                            "priority_points": 0.0,
                            "role_count": 0,
                            "role_names": [],
                            "match_types": set(),
                        }

                    item = collected[key]

                    # Keep the first readable name encountered.
                    if role_name not in item["role_names"]:
                        item["role_names"].append(role_name)
                        item["role_count"] += 1

                    item["match_types"].add(match_type)

                    if match_type == "missing":
                        target = "missing_roles"

                    elif match_type == "related":
                        target = "partial_roles"

                    else:
                        target = "review_roles"

                    if role_name not in item[target]:
                        item[target].append(role_name)

                    item["priority_points"] += self._get_priority_points(
                        skill_type,
                        match_type
                    )

        return collected

    def _determine_status(self, item):
        """Choose the most important gap status."""

        if item["missing_roles"]:
            return "missing"

        if item["partial_roles"]:
            return "partial"

        return "needs_review"

    def _calculate_priority(self, item):
        """
        Combine importance and role frequency.

        The frequency bonus rewards skills that are relevant
        across several recommended roles.
        """

        frequency_bonus = max(0, item["role_count"] - 1) * 0.5

        return round(
            item["priority_points"] + frequency_bonus,
            2
        )

    def _get_resources(self, skill_name):
        """Retrieve available learning resources for a skill."""

        try:
            resources = self.resource_loader(skill_name)

            if not resources:
                return []

            return resources[:MAX_RESOURCES_PER_SKILL]

        except Exception as error:
            print(
                f"Could not retrieve resources for "
                f"{skill_name}: {error}"
            )
            return []

    def analyze(self, ranked_roles, include_resources=True):
        """
        Generate a consolidated skill-gap report.

        Parameters
        ----------
        ranked_roles : list
            Output from RoleMatcher.rank_roles().

        include_resources : bool
            Whether to retrieve learning resources.

        Returns
        -------
        dict
            Consolidated skill-gap report.
        """

        if not ranked_roles:
            return {
                "total_roles_analyzed": 0,
                "required_skill_gaps": [],
                "math_skill_gaps": [],
                "priority_learning_path": [],
                "summary": {
                    "missing_skills": 0,
                    "partial_skills": 0,
                    "skills_needing_review": 0,
                },
            }

        collected = self._collect_skill_gaps(ranked_roles)

        required_gaps = []
        math_gaps = []

        for item in collected.values():

            status = self._determine_status(item)

            priority = self._calculate_priority(item)

            gap = {
                "skill": item["skill"],
                "skill_type": item["skill_type"],
                "status": status,
                "priority_score": priority,
                "required_by_roles": item["role_names"],
                "missing_in_roles": item["missing_roles"],
                "partial_in_roles": item["partial_roles"],
                "needs_review_in_roles": item["review_roles"],
                "role_count": item["role_count"],
                "resources": [],
            }

            if include_resources:
                gap["resources"] = self._get_resources(
                    item["skill"]
                )

            if item["skill_type"] == "required":
                required_gaps.append(gap)
            else:
                math_gaps.append(gap)

        # Highest-priority skills appear first.
        required_gaps.sort(
            key=lambda item: (
                item["priority_score"],
                item["role_count"],
                item["skill"]
            ),
            reverse=True
        )

        math_gaps.sort(
            key=lambda item: (
                item["priority_score"],
                item["role_count"],
                item["skill"]
            ),
            reverse=True
        )

        # Combined learning path, with required skills first
        # when two skills have the same priority.
        priority_learning_path = sorted(
            required_gaps + math_gaps,
            key=lambda item: (
                item["priority_score"],
                item["skill_type"] == "required",
                item["role_count"]
            ),
            reverse=True
        )

        all_gaps = required_gaps + math_gaps

        summary = {
            "missing_skills": sum(
                1 for item in all_gaps
                if item["status"] == "missing"
            ),
            "partial_skills": sum(
                1 for item in all_gaps
                if item["status"] == "partial"
            ),
            "skills_needing_review": sum(
                1 for item in all_gaps
                if item["status"] == "needs_review"
            ),
        }

        return {
            "total_roles_analyzed": len(ranked_roles),
            "required_skill_gaps": required_gaps,
            "math_skill_gaps": math_gaps,
            "priority_learning_path": priority_learning_path,
            "summary": summary,
        }

    def display_report(self, report):

        print("\n" + "=" * 70)
        print("             PERSONALIZED SKILL GAP REPORT")
        print("=" * 70)

        print(
            f"\nRoles analyzed: "
            f"{report['total_roles_analyzed']}"
        )

        summary = report["summary"]

        print("\nGAP SUMMARY")
        print("-" * 70)
        print(f"Missing skills: {summary['missing_skills']}")
        print(f"Partial skills: {summary['partial_skills']}")
        print(
            "Skills needing review: "
            f"{summary['skills_needing_review']}"
        )

        sections = [
            (
                "REQUIRED / TECHNICAL SKILL GAPS",
                report["required_skill_gaps"]
            ),
            (
                "MATHEMATICAL SKILL GAPS",
                report["math_skill_gaps"]
            ),
        ]

        for heading, gaps in sections:

            print(f"\n{heading}")
            print("-" * 70)

            if not gaps:
                print("No gaps found.")
                continue

            for index, item in enumerate(gaps, start=1):

                print(f"\n{index}. {item['skill']}")
                print(f"   Status: {item['status']}")
                print(
                    f"   Priority score: "
                    f"{item['priority_score']}"
                )
                print(
                    f"   Relevant roles: "
                    f"{', '.join(item['required_by_roles'])}"
                )

                if item["missing_in_roles"]:
                    print(
                        "   Missing in: "
                        + ", ".join(item["missing_in_roles"])
                    )

                if item["partial_in_roles"]:
                    print(
                        "   Partial in: "
                        + ", ".join(item["partial_in_roles"])
                    )

                if item["needs_review_in_roles"]:
                    print(
                        "   Needs review in: "
                        + ", ".join(item["needs_review_in_roles"])
                    )

                if item["resources"]:
                    print("   Learning resources:")

                    for resource in item["resources"]:
                        print(f"      - {resource}")

        print("\n" + "=" * 70)
        print("PRIORITIZED LEARNING PATH")
        print("=" * 70)

        for index, item in enumerate(
            report["priority_learning_path"],
            start=1
        ):

            print(
                f"{index}. {item['skill']} "
                f"({item['skill_type']}) "
                f"- {item['status']} "
                f"- Priority: {item['priority_score']}"
            )

        print("\n" + "=" * 70)


if __name__ == "__main__":

    from ml.role_matcher import RoleMatcher

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

    role_matcher = RoleMatcher()

    ranked_roles = role_matcher.rank_roles(
        student_skills,
        top_n=5
    )

    analyzer = SkillGapAnalyzer()

    report = analyzer.analyze(
        ranked_roles,
        include_resources=True
    )

    analyzer.display_report(report)
