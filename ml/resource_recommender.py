
from collections.abc import Mapping
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

from db_queries import get_learning_resources
from ml.config import MAX_RESOURCES_PER_SKILL


class ResourceRecommender:
    """
    Recommends learning resources for identified skill gaps.

    Improvements:
    1. Deduplicates resources using normalized URLs, IDs, and fallback details.
    2. Keeps a resource attached to every skill it can help with.
    3. Builds a separate global catalogue of unique resources.
    4. Displays resource details in a readable format.
    5. Handles missing resources and database lookup errors safely.
    """

    STATUS_PRIORITY = {
        "missing": 3,
        "partial": 2,
        "needs_review": 1,
    }

    TRACKING_PARAMETERS = {
        "gclid",
        "fbclid",
        "dclid",
        "mc_cid",
        "mc_eid",
    }

    def __init__(self, resource_loader=None):
        self.resource_loader = (
            resource_loader
            if resource_loader is not None
            else get_learning_resources
        )

    # ---------------------------------------------------------
    # RESOURCE CONVERSION
    # ---------------------------------------------------------

    def _resource_to_dict(self, resource):
        """Convert database rows or mappings into dictionaries."""

        if isinstance(resource, Mapping):
            return dict(resource)

        if hasattr(resource, "keys"):
            try:
                return {
                    key: resource[key]
                    for key in resource.keys()
                }
            except (KeyError, TypeError, IndexError):
                pass

        if hasattr(resource, "__dict__"):
            return dict(resource.__dict__)

        return {"value": str(resource)}

    # ---------------------------------------------------------
    # URL NORMALIZATION AND DUPLICATE DETECTION
    # ---------------------------------------------------------

    def _normalize_url(self, url):
        """
        Normalize URLs so that superficial differences do not
        cause duplicate resources.

        Examples:
        - Hostname capitalization is ignored.
        - URL fragments are removed.
        - Trailing slashes are normalized.
        - Common tracking parameters are removed.
        - Remaining query parameters are sorted.
        """

        if not url:
            return None

        url = str(url).strip()

        if not url:
            return None

        try:
            parsed = urlsplit(url)

            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            path = parsed.path.rstrip("/")

            query_items = parse_qsl(
                parsed.query,
                keep_blank_values=True
            )

            filtered_query = []

            for key, value in query_items:
                key_lower = key.lower()

                if key_lower.startswith("utm_"):
                    continue

                if key_lower in self.TRACKING_PARAMETERS:
                    continue

                filtered_query.append((key, value))

            filtered_query.sort()

            normalized_query = urlencode(filtered_query)

            return urlunsplit((
                scheme,
                netloc,
                path,
                normalized_query,
                ""
            )).lower()

        except (TypeError, ValueError):
            return url.lower()

    def _resource_identity(self, resource):
        """
        Return a stable identity for duplicate detection.

        URL is checked first because two database records may
        have different IDs but point to the same resource.
        """

        data = self._resource_to_dict(resource)

        url = (
            data.get("resource_url")
            or data.get("url")
            or data.get("link")
        )

        normalized_url = self._normalize_url(url)

        if normalized_url:
            return ("url", normalized_url)

        for key in ("resource_id", "id"):
            value = data.get(key)

            if value is not None and str(value).strip():
                return (key, str(value).strip().lower())

        # Fallback when neither URL nor ID is available.
        normalized_items = []

        for key, value in data.items():
            normalized_key = str(key).strip().lower()
            normalized_value = " ".join(
                str(value).strip().lower().split()
            )

            normalized_items.append(
                (normalized_key, normalized_value)
            )

        return tuple(sorted(normalized_items))

    # ---------------------------------------------------------
    # RESOURCE RETRIEVAL
    # ---------------------------------------------------------

    def _fetch_resources(self, skill_name):
        """Retrieve resources for one skill safely."""

        try:
            resources = self.resource_loader(skill_name)

            if not resources:
                return []

            return list(resources)[:MAX_RESOURCES_PER_SKILL]

        except Exception as error:
            print(
                f"Resource lookup failed for "
                f"'{skill_name}': {error}"
            )
            return []

    # ---------------------------------------------------------
    # PRIORITY AND SKILL PREPARATION
    # ---------------------------------------------------------

    def _get_status_priority(self, status):
        return self.STATUS_PRIORITY.get(status, 0)

    def _prepare_skill_entries(self, skill_gap_report):
        """Combine required and mathematical skill gaps."""

        entries = []

        sections = [
            (
                "required",
                skill_gap_report.get("required_skill_gaps", [])
            ),
            (
                "math",
                skill_gap_report.get("math_skill_gaps", [])
            ),
        ]

        for skill_type, gaps in sections:
            for gap in gaps:
                try:
                    priority_score = float(
                        gap.get("priority_score", 0.0)
                    )
                except (TypeError, ValueError):
                    priority_score = 0.0

                entries.append({
                    "skill": gap.get("skill", "Unknown skill"),
                    "skill_type": skill_type,
                    "status": gap.get("status", "missing"),
                    "priority_score": priority_score,
                    "required_by_roles": gap.get(
                        "required_by_roles", []
                    ),
                    "missing_in_roles": gap.get(
                        "missing_in_roles", []
                    ),
                    "partial_in_roles": gap.get(
                        "partial_in_roles", []
                    ),
                    "needs_review_in_roles": gap.get(
                        "needs_review_in_roles", []
                    ),
                })

        # Missing skills first, then partial, then review.
        # Within each status, higher priority comes first.
        entries.sort(
            key=lambda item: (
                self._get_status_priority(item["status"]),
                item["priority_score"],
                item["skill_type"] == "required",
            ),
            reverse=True,
        )

        return entries

    # ---------------------------------------------------------
    # RESOURCE FORMATTING
    # ---------------------------------------------------------

    def _get_resource_field(self, resource, *field_names):
        """Return the first available non-empty resource field."""

        for field in field_names:
            value = resource.get(field)

            if value is not None and str(value).strip():
                return str(value).strip()

        return "Not specified"

    def _display_resource(self, resource, number):
        """Print one resource in a readable format."""

        title = self._get_resource_field(
            resource,
            "resource_title",
            "title",
            "name",
        )

        platform = self._get_resource_field(
            resource,
            "platform",
            "provider",
            "source",
        )

        resource_type = self._get_resource_field(
            resource,
            "resource_type",
            "type",
        )

        url = self._get_resource_field(
            resource,
            "resource_url",
            "url",
            "link",
        )

        print(f"  {number}. {title}")
        print(f"     Platform: {platform}")
        print(f"     Type: {resource_type}")
        print(f"     URL: {url}")

    # ---------------------------------------------------------
    # MAIN RECOMMENDATION LOGIC
    # ---------------------------------------------------------

    def recommend(self, skill_gap_report):
        """
        Generate recommendations for every skill gap.

        Each skill retains its own resource list, even if a
        resource is also recommended for another skill.

        The all_resources section contains unique resources
        with a list of the skills associated with each one.
        """

        if not isinstance(skill_gap_report, Mapping):
            skill_gap_report = {}

        entries = self._prepare_skill_entries(skill_gap_report)

        recommendations = []

        # Global catalogue of unique resources.
        unique_resource_catalogue = {}

        total_resources_fetched = 0
        per_skill_duplicates_removed = 0

        for entry in entries:
            skill_name = entry["skill"]

            fetched_resources = self._fetch_resources(skill_name)

            total_resources_fetched += len(fetched_resources)

            skill_resources = []
            seen_for_this_skill = set()

            for resource in fetched_resources:
                resource_data = self._resource_to_dict(resource)
                identity = self._resource_identity(resource_data)

                # Remove duplicates within this skill.
                if identity in seen_for_this_skill:
                    per_skill_duplicates_removed += 1
                    continue

                seen_for_this_skill.add(identity)
                skill_resources.append(resource_data)

                # Add to global catalogue or associate with
                # another skill if it already exists.
                if identity not in unique_resource_catalogue:
                    unique_resource_catalogue[identity] = {
                        "resource": resource_data,
                        "skills": [],
                    }

                associated_skills = (
                    unique_resource_catalogue[identity]["skills"]
                )

                skill_association = {
                    "skill": skill_name,
                    "skill_type": entry["skill_type"],
                    "status": entry["status"],
                }

                if skill_association not in associated_skills:
                    associated_skills.append(skill_association)

            recommendations.append({
                **entry,
                "resources": skill_resources,
                "resource_count": len(skill_resources),
                "resource_available": bool(skill_resources),
            })

        # Convert the global catalogue into a list.
        all_resources = []

        for catalogue_item in unique_resource_catalogue.values():
            all_resources.append({
                "resource": catalogue_item["resource"],
                "skills": catalogue_item["skills"],
            })

        required_recommendations = [
            item
            for item in recommendations
            if item["skill_type"] == "required"
        ]

        math_recommendations = [
            item
            for item in recommendations
            if item["skill_type"] == "math"
        ]

        skills_with_resources = sum(
            1
            for item in recommendations
            if item["resource_available"]
        )

        skills_without_resources = (
            len(recommendations) - skills_with_resources
        )

        summary = {
            "total_skills": len(recommendations),
            "skills_with_resources": skills_with_resources,
            "skills_without_resources": skills_without_resources,
            "total_resources_fetched": total_resources_fetched,
            "total_unique_resources": len(all_resources),
            "duplicate_resources_removed": (
                total_resources_fetched - len(all_resources)
            ),
            "per_skill_duplicates_removed": (
                per_skill_duplicates_removed
            ),
            "required_skills": len(required_recommendations),
            "math_skills": len(math_recommendations),
        }

        return {
            "required_recommendations": required_recommendations,
            "math_recommendations": math_recommendations,
            "learning_sequence": recommendations,
            "all_resources": all_resources,
            "summary": summary,
        }

    # ---------------------------------------------------------
    # REPORT DISPLAY
    # ---------------------------------------------------------

    def _display_skill_section(self, title, recommendations):
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)

        if not recommendations:
            print("No skills in this section.")
            return

        for item in recommendations:
            print(f"\nSkill: {item['skill']}")
            print(f"Status: {item['status']}")
            print(f"Priority: {item['priority_score']:.2f}")

            if item["required_by_roles"]:
                print(
                    "Required by roles: "
                    + ", ".join(map(str, item["required_by_roles"]))
                )

            if not item["resource_available"]:
                print("Resources: No resources found.")
                continue

            print(f"Resources ({item['resource_count']}):")

            for number, resource in enumerate(
                item["resources"],
                start=1
            ):
                self._display_resource(resource, number)

    def display_report(self, report):
        """Display the recommendation report."""

        if not isinstance(report, Mapping):
            print("No valid recommendation report supplied.")
            return

        summary = report.get("summary", {})

        print("\n" + "=" * 70)
        print("             LEARNING RESOURCE RECOMMENDATIONS")
        print("=" * 70)

        print("\nRESOURCE SUMMARY")
        print("-" * 70)

        print(
            f"Skills analyzed: "
            f"{summary.get('total_skills', 0)}"
        )

        print(
            f"Skills with resources: "
            f"{summary.get('skills_with_resources', 0)}"
        )

        print(
            f"Skills without resources: "
            f"{summary.get('skills_without_resources', 0)}"
        )

        print(
            f"Resources fetched: "
            f"{summary.get('total_resources_fetched', 0)}"
        )

        print(
            f"Unique resources: "
            f"{summary.get('total_unique_resources', 0)}"
        )

        print(
            f"Duplicate resources removed: "
            f"{summary.get('duplicate_resources_removed', 0)}"
        )

        print(
            f"Required skills: "
            f"{summary.get('required_skills', 0)}"
        )

        print(
            f"Mathematical skills: "
            f"{summary.get('math_skills', 0)}"
        )

        self._display_skill_section(
            "TECHNICAL / REQUIRED SKILLS",
            report.get("required_recommendations", [])
        )

        self._display_skill_section(
            "MATHEMATICAL SKILLS",
            report.get("math_recommendations", [])
        )

        print("\n" + "=" * 70)
        print("PRIORITIZED LEARNING SEQUENCE")
        print("=" * 70)

        for number, item in enumerate(
            report.get("learning_sequence", []),
            start=1
        ):
            resource_status = (
                "Resources available"
                if item["resource_available"]
                else "No resources available"
            )

            print(
                f"{number}. {item['skill']} "
                f"({item['skill_type']}) | "
                f"{item['status']} | "
                f"Priority: {item['priority_score']:.2f} | "
                f"{resource_status}"
            )

        print("\n" + "=" * 70)
        print("END OF REPORT")
        print("=" * 70)


# -------------------------------------------------------------
# INTEGRATION TEST / MODULE EXECUTION
# -------------------------------------------------------------

if __name__ == "__main__":

    from ml.role_matcher import RoleMatcher
    from ml.skill_gap_analyzer import SkillGapAnalyzer

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

    print("Running role matching...")

    role_matcher = RoleMatcher()

    ranked_roles = role_matcher.rank_roles(
        student_skills,
        top_n=5
    )

    print("Analyzing skill gaps...")

    gap_analyzer = SkillGapAnalyzer()

    gap_report = gap_analyzer.analyze(
        ranked_roles,
        include_resources=False
    )

    print("Generating resource recommendations...")

    resource_recommender = ResourceRecommender()

    resource_report = resource_recommender.recommend(
        gap_report
    )

    resource_recommender.display_report(
        resource_report
    )
