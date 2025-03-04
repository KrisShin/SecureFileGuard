import os
import random
import string
from pathlib import Path

from passlib.context import CryptContext
from PySide6.QtWidgets import QApplication, QWidget

from interface.custom_widget import MyQLabelTip
from setting.global_variant import PWD_CHARACTORS

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False


def generate_strong_password():
    """生成符合安全规范的强密码"""

    # 生成8位密码
    length = 8

    # 确保包含至少一个特殊字符和数字
    while True:
        password = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*"),
        ] + [random.choice(PWD_CHARACTORS) for _ in range(length - 4)]

        random.shuffle(password)
        password = ''.join(password)

        # 验证密码强度, 大小写数字加特殊符号
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            break
    return password


def create_dir_if_not_exists(file_path: Path):
    """创建文件夹路径"""
    if isinstance(file_path, str):
        file_path = Path(file_path)  # 字符串对象转换为Path对象
    if not os.path.exists(file_path.parent):
        os.makedirs(file_path.parent)  # 创建多层文件夹


def handle_set_strong_password(container: QWidget, password_line: QWidget):
    """生成强密码并复制到剪贴板"""
    password = generate_strong_password()
    password_line.setText(password)
    clipboard = QApplication.clipboard()
    clipboard.setText(password)
    MyQLabelTip("密码已生成并复制到剪贴板", container)
