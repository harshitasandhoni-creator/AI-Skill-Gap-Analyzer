
import numpy as np

from ml.skill_normalizer import SkillNormalizer
from ml.skill_relationships import SkillRelationships
from ml.embedding_model import EmbeddingModel

from ml.config import (
    EXACT_MATCH_CREDIT,
    EQUIVALENT_MATCH_CREDIT,
    RELATED_MATCH_CREDIT,
    MISSING_MATCH_CREDIT,
    SEMANTIC_SUGGESTION_THRESHOLD,
)


# One student skill can provide partial support to at most this many
# related requirements. This prevents unlimited score inflation.
MAX_RELATED_USES_PER_STUDENT_SKILL = 3


class SemanticMatcher:

    def __init__(self):
        self.normalizer = SkillNormalizer()
        self.relationships = SkillRelationships()
        self.embedding_model = EmbeddingModel()

    def prepare_skills(self, skills):
        """Normalize skills and remove duplicates while preserving order."""
        prepared = []
        seen = set()

        for skill in skills:
            normalized = self.normalizer.normalize_skill(skill)

            if not normalized:
                continue

            key = normalized.lower()

            if key not in seen:
                prepared.append(normalized)
                seen.add(key)

        return prepared

    def calculate_similarity_matrix(self, student_skills, required_skills):
        """
        Return a matrix with shape:
        (number of student skills, number of required skills).
        """
        if not student_skills or not required_skills:
            return np.zeros((len(student_skills), len(required_skills)))

        student_embeddings = self.embedding_model.generate_embeddings(
            student_skills
        )

        required_embeddings = self.embedding_model.generate_embeddings(
            required_skills
        )

        return np.dot(student_embeddings, required_embeddings.T)

    def _create_match(self, required_skill, student_skill, similarity, credit):
        return {
            "required_skill": required_skill,
            "student_skill": student_skill,
            "similarity": round(float(similarity), 4),
            "credit": float(credit),
        }

    def match_skills(self, student_skills, required_skills):

        student_skills = self.prepare_skills(student_skills)
        required_skills = self.prepare_skills(required_skills)

        similarity_matrix = self.calculate_similarity_matrix(
            student_skills,
            required_skills
        )

        result = {
            "matched_skills": [],
            "equivalent_matches": [],
            "related_matches": [],
            "semantic_suggestions": [],
            "missing_skills": [],
            "unverified_skills": [],
            "requirement_details": [],
            "unmatched_student_skills": [],
            "coverage_score": 0.0,
            "strict_coverage_score": 0.0,
            "average_matched_similarity": 0.0,
        }

        if not required_skills:
            result["unmatched_student_skills"] = student_skills.copy()
            return result

        # Tracks student skills already used for exact/equivalent matches.
        reserved_student_indices = set()

        # Tracks requirements that have already received a match.
        matched_requirement_indices = set()

        # Tracks how often each student skill is used for related matches.
        related_use_count = {}

        total_credit = 0.0
        strict_credit = 0.0
        strict_similarities = []

        # ---------------------------------------------------------
        # PASS 1: EXACT MATCHES
        # Exact matches always receive priority.
        # ---------------------------------------------------------
        for req_index, required_skill in enumerate(required_skills):

            required_clean = self.relationships.clean(required_skill)

            for student_index, student_skill in enumerate(student_skills):

                if student_index in reserved_student_indices:
                    continue

                student_clean = self.relationships.clean(student_skill)

                if required_clean == student_clean:

                    similarity = similarity_matrix[
                        student_index, req_index
                    ]

                    match = self._create_match(
                        required_skill,
                        student_skill,
                        similarity,
                        EXACT_MATCH_CREDIT
                    )

                    result["matched_skills"].append(match)
                    result["requirement_details"].append({
                        "required_skill": required_skill,
                        "matched_student_skill": student_skill,
                        "match_type": "exact",
                        "similarity": round(float(similarity), 4),
                        "credit": float(EXACT_MATCH_CREDIT),
                    })

                    reserved_student_indices.add(student_index)
                    matched_requirement_indices.add(req_index)

                    total_credit += EXACT_MATCH_CREDIT
                    strict_credit += EXACT_MATCH_CREDIT
                    strict_similarities.append(float(similarity))

                    break

        # ---------------------------------------------------------
        # PASS 2: EQUIVALENT MATCHES
        # These also receive full credit.
        # ---------------------------------------------------------
        for req_index, required_skill in enumerate(required_skills):

            if req_index in matched_requirement_indices:
                continue

            for student_index, student_skill in enumerate(student_skills):

                if student_index in reserved_student_indices:
                    continue

                if self.relationships.are_equivalent(
                    required_skill,
                    student_skill
                ):

                    similarity = similarity_matrix[
                        student_index, req_index
                    ]

                    match = self._create_match(
                        required_skill,
                        student_skill,
                        similarity,
                        EQUIVALENT_MATCH_CREDIT
                    )

                    result["equivalent_matches"].append(match)
                    result["requirement_details"].append({
                        "required_skill": required_skill,
                        "matched_student_skill": student_skill,
                        "match_type": "equivalent",
                        "similarity": round(float(similarity), 4),
                        "credit": float(EQUIVALENT_MATCH_CREDIT),
                    })

                    reserved_student_indices.add(student_index)
                    matched_requirement_indices.add(req_index)

                    total_credit += EQUIVALENT_MATCH_CREDIT
                    strict_credit += EQUIVALENT_MATCH_CREDIT
                    strict_similarities.append(float(similarity))

                    break

        # ---------------------------------------------------------
        # PASS 3: RELATED MATCHES
        # Partial credit. A student skill can support up to three
        # related requirements, but cannot be reused if reserved
        # by an exact/equivalent match.
        # ---------------------------------------------------------
        for req_index, required_skill in enumerate(required_skills):

            if req_index in matched_requirement_indices:
                continue

            best_student_index = None
            best_similarity = -1.0

            for student_index, student_skill in enumerate(student_skills):

                if student_index in reserved_student_indices:
                    continue

                if related_use_count.get(student_index, 0) >= (
                    MAX_RELATED_USES_PER_STUDENT_SKILL
                ):
                    continue

                if self.relationships.are_related(
                    required_skill,
                    student_skill
                ):
                    similarity = float(
                        similarity_matrix[student_index, req_index]
                    )

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_student_index = student_index

            if best_student_index is not None:

                student_skill = student_skills[best_student_index]

                match = self._create_match(
                    required_skill,
                    student_skill,
                    best_similarity,
                    RELATED_MATCH_CREDIT
                )

                result["related_matches"].append(match)
                result["requirement_details"].append({
                    "required_skill": required_skill,
                    "matched_student_skill": student_skill,
                    "match_type": "related",
                    "similarity": round(best_similarity, 4),
                    "credit": float(RELATED_MATCH_CREDIT),
                })

                related_use_count[best_student_index] = (
                    related_use_count.get(best_student_index, 0) + 1
                )

                matched_requirement_indices.add(req_index)
                total_credit += RELATED_MATCH_CREDIT

        # ---------------------------------------------------------
        # PASS 4: SEMANTIC SUGGESTIONS
        # Similarity alone does not prove a skill is equivalent.
        # Suggestions receive zero credit.
        # ---------------------------------------------------------
        suggested_student_indices = set()

        for req_index, required_skill in enumerate(required_skills):

            if req_index in matched_requirement_indices:
                continue

            best_student_index = None
            best_similarity = -1.0

            for student_index, student_skill in enumerate(student_skills):

                if student_index in reserved_student_indices:
                    continue

                if related_use_count.get(student_index, 0) > 0:
                    continue

                if student_index in suggested_student_indices:
                    continue

                similarity = float(
                    similarity_matrix[student_index, req_index]
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_student_index = student_index

            if (
                best_student_index is not None
                and best_similarity >= SEMANTIC_SUGGESTION_THRESHOLD
            ):

                student_skill = student_skills[best_student_index]

                suggestion = self._create_match(
                    required_skill,
                    student_skill,
                    best_similarity,
                    MISSING_MATCH_CREDIT
                )

                result["semantic_suggestions"].append(suggestion)
                result["unverified_skills"].append(suggestion)

                result["requirement_details"].append({
                    "required_skill": required_skill,
                    "matched_student_skill": student_skill,
                    "match_type": "semantic_suggestion",
                    "similarity": round(best_similarity, 4),
                    "credit": float(MISSING_MATCH_CREDIT),
                })

                suggested_student_indices.add(best_student_index)
                matched_requirement_indices.add(req_index)

        # ---------------------------------------------------------
        # PASS 5: MISSING REQUIREMENTS
        # ---------------------------------------------------------
        for req_index, required_skill in enumerate(required_skills):

            if req_index not in matched_requirement_indices:

                result["missing_skills"].append(required_skill)

                result["requirement_details"].append({
                    "required_skill": required_skill,
                    "matched_student_skill": None,
                    "match_type": "missing",
                    "similarity": 0.0,
                    "credit": float(MISSING_MATCH_CREDIT),
                })

        # ---------------------------------------------------------
        # FINAL SCORES
        # ---------------------------------------------------------
        requirement_count = len(required_skills)

        result["coverage_score"] = round(
            (total_credit / requirement_count) * 100,
            2
        )

        result["strict_coverage_score"] = round(
            (strict_credit / requirement_count) * 100,
            2
        )

        if strict_similarities:
            result["average_matched_similarity"] = round(
                sum(strict_similarities) / len(strict_similarities),
                4
            )

        used_student_indices = (
            reserved_student_indices
            | set(related_use_count.keys())
            | suggested_student_indices
        )

        result["unmatched_student_skills"] = [
            skill
            for index, skill in enumerate(student_skills)
            if index not in used_student_indices
        ]

        return result

    def display_results(self, result):

        print("\n" + "=" * 60)
        print("SEMANTIC SKILL MATCHING RESULTS")
        print("=" * 60)

        sections = [
            ("EXACT MATCHES", "matched_skills"),
            ("EQUIVALENT MATCHES", "equivalent_matches"),
            ("RELATED MATCHES (PARTIAL CREDIT)", "related_matches"),
            ("SEMANTIC SUGGESTIONS (UNVERIFIED)", "semantic_suggestions"),
        ]

        for heading, key in sections:

            print(f"\n{heading}:")

            if not result[key]:
                print("  None")
                continue

            for item in result[key]:
                print(
                    f"  Required: {item['required_skill']} | "
                    f"Student: {item['student_skill']} | "
                    f"Similarity: {item['similarity']} | "
                    f"Credit: {item['credit']}"
                )

        print("\nMISSING SKILLS:")

        if result["missing_skills"]:
            for skill in result["missing_skills"]:
                print(f"  - {skill}")
        else:
            print("  None")

        print("\nOTHER STUDENT SKILLS:")

        if result["unmatched_student_skills"]:
            for skill in result["unmatched_student_skills"]:
                print(f"  - {skill}")
        else:
            print("  None")

        print("\nSCORES:")
        print(f"  Overall coverage: {result['coverage_score']}%")
        print(f"  Strict coverage: {result['strict_coverage_score']}%")
        print(
            "  Average exact/equivalent similarity: "
            f"{result['average_matched_similarity']}"
        )

        print("=" * 60)


if __name__ == "__main__":

    matcher = SemanticMatcher()

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

    required_skills = [
        "Python Programming",
        "SQL",
        "Hypothesis Testing",
        "Regression",
        "Data Analysis",
        "HTML",
    ]

    result = matcher.match_skills(student_skills, required_skills)
    matcher.display_results(result)
