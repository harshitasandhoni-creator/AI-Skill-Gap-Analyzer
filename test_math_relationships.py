
from ml.skill_relationships import SkillRelationships

relationships = SkillRelationships()

tests = [

    ("Python", "Python Programming"),

    ("Statistics", "Probability"),

    ("Statistics", "Hypothesis Testing"),

    ("Statistics", "Regression"),

    ("Statistics", "Linear Algebra"),

    ("Machine Learning", "Deep Learning"),

    ("NumPy", "Linear Algebra"),

    ("Data Visualization", "Data Cleaning"),

    ("Data Visualization", "Data Storytelling"),

    ("Scikit-learn", "sklearn"),

    ("Calculus", "Derivatives"),

    ("Optimization", "Gradient Descent"),

    ("Model Evaluation", "Error Analysis")

]

for skill1, skill2 in tests:

    result = relationships.classify_relationship(
        skill1,
        skill2
    )

    print(
        f"{skill1} <-> {skill2}: {result}"
    )
