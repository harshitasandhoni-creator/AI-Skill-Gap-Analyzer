from ml.config import (
    DATABASE_PATH,
    MODEL_NAME,
    EMBEDDING_DIMENSION,
    TOP_N_ROLES
)
print("database path:",DATABASE_PATH)
print("model:",MODEL_NAME)
print("embedding dimensions:",EMBEDDING_DIMENSION)
print("top recommendations:",TOP_N_ROLES)

print("\ndatabase exists:",DATABASE_PATH.exists())