
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "skill_gap.db"


# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384


# --------------------------------------------------
# MATCHING THRESHOLDS
# --------------------------------------------------

# Minimum similarity for a semantic suggestion.
# This does NOT establish that a student knows the skill.
SEMANTIC_SUGGESTION_THRESHOLD = 0.70

# Strong similarity: useful for prioritizing manual review.
STRONG_MATCH_THRESHOLD = 0.80


# --------------------------------------------------
# MATCHING SCORES
# --------------------------------------------------

EXACT_MATCH_CREDIT = 1.0

EQUIVALENT_MATCH_CREDIT = 1.0

RELATED_MATCH_CREDIT = 0.25

MISSING_MATCH_CREDIT = 0.0


# --------------------------------------------------
# ROLE MATCHING WEIGHTS
# --------------------------------------------------

REQUIRED_SKILL_WEIGHT = 0.80

MATH_SKILL_WEIGHT = 0.20

TOP_N_ROLES = 5


# --------------------------------------------------
# SKILL COVERAGE
# --------------------------------------------------

SKILL_COVERAGE_THRESHOLD = 0.65


# --------------------------------------------------
# TEXT PREPROCESSING
# --------------------------------------------------

LOWERCASE_TEXT = True

REMOVE_EXTRA_WHITESPACE = True


# --------------------------------------------------
# LEARNING RESOURCES
# --------------------------------------------------

MAX_RESOURCES_PER_SKILL = 3
