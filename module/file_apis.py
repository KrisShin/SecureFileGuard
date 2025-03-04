from pathlib import Path
from db_data.manager import db
from module.common import get_password_hash
from module.encrypt_apis import decrypt_file, encrypt_file


def file_upload(selected_algorithm: str, filename: str, password: str, selected_file: str, username: str):
    """文件上传"""

    if not selected_file:
        return False, "错误", "请先选择文件！"
    if not password:
        return False, "错误", "请输入加密密码！"

    file_size = Path(selected_file).stat().st_size

    is_success, iv_or_title, file_path_or_message, filled_password = encrypt_file(selected_algorithm, selected_file, username, filename, password)
    if is_success:
        db.upload_file(
            filled_password,
            get_password_hash(filled_password),
            iv_or_title,
            username,
            file_path_or_message.as_posix(),
            selected_algorithm,
            file_size,
            filename,
        )
        return True, "成功", f"上传文件{filename}, {selected_algorithm}加密成功"
    else:
        return False, "成功", iv_or_title, file_path_or_message


def file_edit(password: str, file_id: int, selected_algorithm: str, username: str, filename: str):
    """文件编辑"""
    if not password:
        return False, "错误", "请输入加密密码！"

    org_file = db.get_file_by_id(file_id)
    decrypt_text, _ = decrypt_file(org_file['algorithm'], password, file_id)

    is_success, iv_or_title, file_path_or_message, filled_password = encrypt_file(
        selected_algorithm,
        None,
        username,
        filename,
        password,
        plaintext=decrypt_text,
        file_path=org_file['file_path'],
    )
    if is_success:
        db.edit_file(file_id, filled_password, get_password_hash(filled_password), iv_or_title, selected_algorithm, filename)
        return True, "成功", f"更新文件{filename}-{selected_algorithm}加密成功"
    else:
        return False, iv_or_title, file_path_or_message


def get_files_by_user():
    """查找用户文件"""
