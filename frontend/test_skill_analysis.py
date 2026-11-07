import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from skill_analysis_math import analyze_skill_gap

required_skills = [
    "Python",
    "SQL",
    "Excel",
    "Power BI",
    "Statistics",
    "Data Cleaning"
]

student_skills = [
    "python",
    "SQL",
    "Excel",
    "Data Cleaning"
]

result = analyze_skill_gap(
    required_skills,
    student_skills
)

print(result)