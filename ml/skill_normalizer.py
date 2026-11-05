
"""
Skill normalization module.

Converts different names and abbreviations of skills
into consistent standard skill names.
"""


class SkillNormalizer:

    def __init__(self):

        # Common skill aliases mapped to standard names
        self.skill_aliases = {

            # Programming languages
            "py": "Python",
            "cpp": "C++",
            "c plus plus": "C++",
            "c sharp": "C#",
            "js": "JavaScript",

            # Machine learning and AI
            "ml": "Machine Learning",
            "ai": "Artificial Intelligence",
            "dl": "Deep Learning",
            "nlp": "Natural Language Processing",
            "sklearn": "scikit-learn",
            "scikit learn": "scikit-learn",

            # Data science
            "ds": "Data Science",
            "eda": "Exploratory Data Analysis",
            "ms excel": "Excel",
            "excel spreadsheet": "Excel",

            # Databases
            "mysql db": "MySQL",
            "postgres": "PostgreSQL",
            "postgres db": "PostgreSQL",

            # Web development
            "html5": "HTML",
            "css3": "CSS",
            "node js": "Node.js",
            "react js": "React",

            # Cloud and DevOps
            "amazon web services": "AWS",
            "google cloud platform": "Google Cloud",
            "continuous integration and continuous deployment": "CI/CD",

            # Mathematics and statistics
            "stats": "Statistics",
            "prob": "Probability",
            "linear algebra": "Linear Algebra",
        }

    # -----------------------------------------------
    # 1. Basic text normalization
    # -----------------------------------------------

    def clean_skill_name(self, skill):

        """
        Standardize capitalization and whitespace.
        """

        if not isinstance(skill, str):
            return ""

        skill = skill.strip().lower()

        skill = " ".join(skill.split())

        return skill

    # -----------------------------------------------
    # 2. Normalize a single skill
    # -----------------------------------------------

    def normalize_skill(self, skill):

        """
        Convert a skill or alias into its standard name.
        """

        cleaned_skill = self.clean_skill_name(skill)

        if not cleaned_skill:
            return ""

        # Return standard name if alias exists
        if cleaned_skill in self.skill_aliases:

            return self.skill_aliases[cleaned_skill]

        # Preserve unknown skills
        # Capitalization is standardized without
        # assuming that every skill is an abbreviation.
        return skill.strip()

    # -----------------------------------------------
    # 3. Normalize multiple skills
    # -----------------------------------------------

    def normalize_skills(self, skills):

        """
        Normalize a list of skills and remove duplicates.
        """

        if not isinstance(skills, (list, tuple, set)):
            return []

        normalized_skills = []

        seen_skills = set()

        for skill in skills:

            normalized = self.normalize_skill(skill)

            if not normalized:
                continue

            comparison_name = normalized.casefold()

            if comparison_name not in seen_skills:

                normalized_skills.append(normalized)

                seen_skills.add(comparison_name)

        return normalized_skills

    # -----------------------------------------------
    # 4. Normalize database and resume skills
    # -----------------------------------------------

    def normalize_skill_pair(self, resume_skill, database_skill):

        """
        Normalize two skills before comparison.
        """

        normalized_resume_skill = self.normalize_skill(
            resume_skill
        )

        normalized_database_skill = self.normalize_skill(
            database_skill
        )

        return (
            normalized_resume_skill,
            normalized_database_skill
        )


# -----------------------------------------------
# 5. Standalone testing
# -----------------------------------------------

if __name__ == "__main__":

    normalizer = SkillNormalizer()

    sample_skills = [
        "PY",
        "Python",
        "ML",
        "Machine Learning",
        "NLP",
        "Natural Language Processing",
        "SKLearn",
        "JavaScript",
        "JS",
        "Excel",
        "MS Excel",
        "Node JS",
        "Postgres",
        "Statistics",
        "Communication Skills"
    ]

    print("ORIGINAL SKILLS:")

    print(sample_skills)

    normalized_skills = normalizer.normalize_skills(
        sample_skills
    )

    print("\nNORMALIZED SKILLS:")

    print(normalized_skills)

    print("\nINDIVIDUAL SKILL TESTS:")

    print("ML:", normalizer.normalize_skill("ML"))

    print("NLP:", normalizer.normalize_skill("NLP"))

    print(
        "SKLearn:",
        normalizer.normalize_skill("SKLearn")
    )

    print(
        "Unknown skill:",
        normalizer.normalize_skill("Communication Skills")
    )
