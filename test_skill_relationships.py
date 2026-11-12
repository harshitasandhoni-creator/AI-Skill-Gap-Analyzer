
from ml.skill_relationships import SkillRelationships


def run_tests():

    matcher = SkillRelationships()

    test_cases = [

        # ----------------------------------------------
        # EXACT MATCHES
        # ----------------------------------------------

        (
            "Python",
            "Python",
            "exact",
        ),

        (
            "Machine Learning",
            "machine learning",
            "exact",
        ),

        # ----------------------------------------------
        # EQUIVALENT MATCHES
        # ----------------------------------------------

        (
            "Python Programming",
            "Python",
            "equivalent",
        ),

        (
            "Scikit-learn",
            "sklearn",
            "equivalent",
        ),

        (
            "C++",
            "cpp",
            "equivalent",
        ),

        (
            "PostgreSQL",
            "postgres",
            "equivalent",
        ),

        (
            "Microsoft Excel",
            "Excel",
            "equivalent",
        ),

        # ----------------------------------------------
        # STATISTICS AND PROBABILITY
        # ----------------------------------------------

        (
            "Statistics",
            "Probability",
            "related",
        ),

        (
            "Statistics",
            "Hypothesis Testing",
            "related",
        ),

        (
            "Statistics",
            "Descriptive Statistics",
            "related",
        ),

        (
            "Statistics",
            "Probability and inferential statistics",
            "related",
        ),

        # ----------------------------------------------
        # REGRESSION
        # ----------------------------------------------

        (
            "Regression",
            "Linear Regression",
            "related",
        ),

        (
            "Regression",
            "Forecasting",
            "related",
        ),

        (
            "Statistics",
            "Regression",
            "unrelated",
        ),

        # ----------------------------------------------
        # MACHINE LEARNING
        # ----------------------------------------------

        (
            "Machine Learning",
            "Supervised Learning",
            "related",
        ),

        (
            "Machine Learning",
            "Clustering",
            "related",
        ),

        (
            "Deep Learning",
            "Neural Networks",
            "related",
        ),

        # ----------------------------------------------
        # FEATURE ENGINEERING
        # ----------------------------------------------

        (
            "Feature Engineering",
            "Feature Selection",
            "related",
        ),

        (
            "Feature Engineering",
            "Feature Extraction",
            "related",
        ),

        # ----------------------------------------------
        # MODEL EVALUATION
        # ----------------------------------------------

        (
            "Model Evaluation",
            "Cross Validation",
            "related",
        ),

        (
            "Model Evaluation",
            "Error Analysis",
            "related",
        ),

        # ----------------------------------------------
        # DATA ANALYSIS
        # ----------------------------------------------

        (
            "Data Analysis",
            "Exploratory Data Analysis",
            "related",
        ),

        (
            "Data Cleaning",
            "Data Validation",
            "related",
        ),

        (
            "Data Visualization",
            "Data Storytelling",
            "related",
        ),

        (
            "Data Visualization",
            "Data Cleaning",
            "unrelated",
        ),

        # ----------------------------------------------
        # MATHEMATICS
        # ----------------------------------------------

        (
            "Linear Algebra",
            "Matrices",
            "related",
        ),

        (
            "Calculus",
            "Derivatives",
            "related",
        ),

        (
            "Optimization",
            "Gradient Descent",
            "related",
        ),

        # ----------------------------------------------
        # UNRELATED SKILLS
        # ----------------------------------------------

        (
            "Python",
            "HTML",
            "unrelated",
        ),

        (
            "Statistics",
            "Web Development",
            "unrelated",
        ),

        (
            "Calculus",
            "SQL",
            "unrelated",
        ),

        # ----------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------

        (
            "",
            "Python",
            "unrelated",
        ),

        (
            None,
            "Statistics",
            "unrelated",
        ),
    ]

    passed = 0
    failed = 0

    print("\n")
    print("=" * 70)
    print("       SKILL RELATIONSHIP TESTING")
    print("=" * 70)

    for skill_a, skill_b, expected in test_cases:

        actual = matcher.classify_relationship(
            skill_a,
            skill_b
        )

        if actual == expected:

            passed += 1

            print(
                f"[PASS] {str(skill_a):35} "
                f"<-> {str(skill_b):30} "
                f"| {actual}"
            )

        else:

            failed += 1

            print(
                f"[FAIL] {str(skill_a):35} "
                f"<-> {str(skill_b):30} "
                f"| Expected: {expected}, Got: {actual}"
            )

    print("\n" + "=" * 70)
    print(f"Total tests : {len(test_cases)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print("=" * 70)

    if failed == 0:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Review the results above.")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()

    if not success:
        raise SystemExit(1)
