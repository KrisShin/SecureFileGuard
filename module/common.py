from passlib.context import CryptContext
import random
import string


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


def generate_strong_password():
    """生成符合安全规范的强密码"""

    # 定义字符集
    characters = string.ascii_letters + string.digits + "!@#$%^&*"

    # 生成12-16位密码
    length = random.randint(12, 16)

    # 确保包含至少一个特殊字符和数字
    while True:
        password = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*"),
        ] + [random.choice(characters) for _ in range(length - 4)]

        random.shuffle(password)
        password = ''.join(password)

        # 验证密码强度
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            break
    return password
