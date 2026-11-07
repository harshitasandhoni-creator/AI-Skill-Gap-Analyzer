from passlib.context import CryptContext

# Configure password hashing
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


# Hash a password before storing it
def hash_password(password: str) -> str:

    return pwd_context.hash(password)


# Verify a password during login
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )