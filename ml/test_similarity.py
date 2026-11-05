
from ml.semantic_matcher import SemanticMatcher

matcher = SemanticMatcher()

student_skills = [
    "Statistics",
    "Python",
    "SQL",
    "Machine Learning",
    "Pandas",
    "NumPy",
    "Scikit-learn"
]

role_skills = [
    "Probability and inferential statistics",
    "Statistical estimation and hypothesis testing",
    "Linear Algebra",
    "Regression",
    "Evaluation metrics and error analysis",
    "Exploratory data analysis",
    "Feature engineering"
]

similarity_matrix = matcher.calculate_similarity_matrix(
    student_skills,
    role_skills
)

print("\n========== SIMILARITY DIAGNOSTICS ==========\n")

for j, role_skill in enumerate(role_skills):

    print(f"\nRole requirement: {role_skill}")

    scores = []

    for i, student_skill in enumerate(student_skills):

        score = float(similarity_matrix[i, j])

        scores.append((student_skill, score))

    scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    for skill, score in scores:
        print(f"  {skill:<22} {score:.4f}")

print("\n============================================")
