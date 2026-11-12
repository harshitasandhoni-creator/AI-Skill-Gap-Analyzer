
import re


class SkillRelationships:
    """
    Identifies equivalent and conceptually related skills.

    Equivalent:
        Two names represent substantially the same skill.

    Related:
        Two skills have a meaningful conceptual relationship,
        but are not interchangeable.

    Unrelated:
        No curated relationship is defined.

    Important:
        Related does not mean the student has mastered the
        required skill. It only supports partial matching.
    """

    def __init__(self):

        # --------------------------------------------------
        # EQUIVALENT SKILL GROUPS
        # --------------------------------------------------

        self.equivalent_groups = [

            {
                "python",
                "python programming",
            },

            {
                "javascript",
                "js",
            },

            {
                "c++",
                "cpp",
                "c plus plus",
            },

            {
                "c#",
                "c sharp",
            },

            {
                "scikit learn",
                "sklearn",
                "scikit learn library",
            },

            {
                "pytorch",
                "torch",
            },

            {
                "tensorflow",
                "tf",
            },

            {
                "postgresql",
                "postgres",
            },

            {
                "node js",
                "nodejs",
            },

            {
                "power bi",
                "microsoft power bi",
            },

            {
                "tableau",
                "tableau desktop",
            },

            {
                "excel",
                "microsoft excel",
                "ms excel",
            },

            {
                "aws",
                "amazon web services",
            },

            {
                "google cloud",
                "google cloud platform",
                "gcp",
            },
        ]

        # --------------------------------------------------
        # RELATED SKILL GROUPS
        #
        # Skills inside one group have a curated conceptual
        # relationship. They are NOT equivalent.
        # --------------------------------------------------

        self.related_groups = [

            # Statistics and probability
            {
                "statistics",
                "statistical analysis",
                "descriptive statistics",
                "inferential statistics",
                "statistical inference",
                "probability",
                "probability theory",
                "probability distributions",
                "probability distribution",
                "conditional probability",
                "probability and statistics",
                "statistics and probability",
                "probability and inferential statistics",
                "statistical estimation",
                "hypothesis testing",
                "statistical hypothesis testing",
            },

            # Regression and predictive modelling
            {
                "regression",
                "regression analysis",
                "linear regression",
                "multiple linear regression",
                "logistic regression",
                "regression modelling",
                "predictive modelling",
                "predictive modeling",
                "forecasting",
                "time series forecasting",
                "time series analysis",
            },

            # Machine learning
            {
                "machine learning",
                "supervised learning",
                "unsupervised learning",
                "classification",
                "clustering",
                "predictive analytics",
                "predictive modelling",
                "predictive modeling",
            },

            # Deep learning and neural networks
            {
                "deep learning",
                "neural networks",
                "artificial neural networks",
                "convolutional neural networks",
                "recurrent neural networks",
                "transformers",
            },

            # Feature preparation
            {
                "feature engineering",
                "feature selection",
                "feature extraction",
                "feature transformation",
            },

            # Model evaluation
            {
                "model evaluation",
                "model validation",
                "cross validation",
                "cross validation techniques",
                "evaluation metrics",
                "performance metrics",
                "error analysis",
            },

            # Data analysis and exploration
            {
                "data analysis",
                "exploratory data analysis",
                "eda",
                "data exploration",
                "data profiling",
            },

            # Data cleaning and quality
            {
                "data cleaning",
                "data preprocessing",
                "data quality",
                "data validation",
                "data quality checks",
                "data wrangling",
            },

            # Data visualization and communication
            {
                "data visualization",
                "data visualisation",
                "data storytelling",
                "data presentation",
                "data reporting",
                "communicating insights",
            },

            # Linear algebra
            {
                "linear algebra",
                "vectors",
                "vector operations",
                "matrices",
                "matrix operations",
                "eigenvalues",
                "eigenvectors",
            },

            # Calculus
            {
                "calculus",
                "differential calculus",
                "derivatives",
                "partial derivatives",
                "integration",
                "integrals",
                "gradients",
            },

            # Optimization
            {
                "optimization",
                "optimization basics",
                "mathematical optimization",
                "gradient descent",
                "optimization algorithms",
                "optimization and gradients",
            },

            # Databases
            {
                "sql",
                "mysql",
                "postgresql",
                "sqlite",
                "database management",
                "database management systems",
                "relational databases",
            },

            # Cloud computing
            {
                "cloud computing",
                "cloud infrastructure",
                "cloud storage",
                "cloud platforms",
                "cloud deployment",
            },

            # Software development workflow
            {
                "software development",
                "version control",
                "git",
                "github",
                "code collaboration",
                "collaboration in code review",
            },

            # Web development
            {
                "web development",
                "frontend development",
                "backend development",
                "full stack development",
            },

            # Mathematics foundations
            {
                "discrete mathematics",
                "boolean logic",
                "sets",
                "relations",
                "functions",
                "mathematical logic",
            },

            # Quantitative reasoning
            {
                "basic numeracy",
                "percentages",
                "ratios",
                "averages",
                "quantitative reasoning",
                "numerical reasoning",
            },
        ]

    # --------------------------------------------------
    # NORMALIZE SKILL TEXT
    # --------------------------------------------------

    @staticmethod
    def clean(skill):
        """
        Normalize text for relationship comparison.

        Preserves meaningful technical characters by replacing
        punctuation with spaces where appropriate.
        """

        if skill is None:
            return ""

        text = str(skill).strip().casefold()

        # Standardize common technical expressions.
        text = text.replace("c plus plus", "c++")
        text = text.replace("c sharp", "c#")
        text = text.replace("node.js", "node js")
        text = text.replace("scikit-learn", "scikit learn")
        text = text.replace("cross-validation", "cross validation")
        text = text.replace("time-series", "time series")

        # Remove punctuation while retaining letters and digits.
        text = re.sub(r"[^\w+#]+", " ", text)

        # Collapse repeated whitespace.
        text = re.sub(r"\s+", " ", text).strip()

        return text

    # --------------------------------------------------
    # EQUIVALENT MATCH
    # --------------------------------------------------

    def are_equivalent(self, skill_a, skill_b):
        """
        Return True when two skills are known equivalents.
        """

        a = self.clean(skill_a)
        b = self.clean(skill_b)

        if not a or not b:
            return False

        if a == b:
            return True

        for group in self.equivalent_groups:

            normalized_group = {
                self.clean(skill)
                for skill in group
            }

            if a in normalized_group and b in normalized_group:
                return True

        return False

    # --------------------------------------------------
    # RELATED MATCH
    # --------------------------------------------------

    def are_related(self, skill_a, skill_b):
        """
        Return True when two skills belong to a curated
        conceptual relationship group.

        Equivalent skills are not classified as related.
        """

        a = self.clean(skill_a)
        b = self.clean(skill_b)

        if not a or not b:
            return False

        if a == b:
            return False

        if self.are_equivalent(a, b):
            return False

        for group in self.related_groups:

            normalized_group = {
                self.clean(skill)
                for skill in group
            }

            if a in normalized_group and b in normalized_group:
                return True

        return False

    # --------------------------------------------------
    # CLASSIFY RELATIONSHIP
    # --------------------------------------------------

    def classify_relationship(self, skill_a, skill_b):
        """
        Return one of:
            exact
            equivalent
            related
            unrelated
        """

        a = self.clean(skill_a)
        b = self.clean(skill_b)

        if not a or not b:
            return "unrelated"

        if a == b:
            return "exact"

        if self.are_equivalent(a, b):
            return "equivalent"

        if self.are_related(a, b):
            return "related"

        return "unrelated"
