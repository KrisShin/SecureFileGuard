from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate password hashed value."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check plain password whether right or not"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False
