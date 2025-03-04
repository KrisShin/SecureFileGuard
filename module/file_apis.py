from pathlib import Path

from db_data.manager import db
from module.common import get_password_hash, verify_password
from module.encrypt_apis import decrypt_file, encrypt_file
from setting.global_variant import DELIMITER


def file_upload(selected_algorithm: str, filename: str, password: str, selected_file: str, username: str):
    """文件上传"""

    if not selected_file:
        return False, "请先选择文件！"
    if not password:
        return False, "请输入加密密码！"

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
        return True, f"上传文件{filename}, {selected_algorithm}加密成功"
    else:
        return False, iv_or_title, file_path_or_message


def file_edit(password: str, file_id: int, selected_algorithm: str, username: str, filename: str):
    """文件编辑"""
    if not password:
        return False, "请输入加密密码！"

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
        return True, f"更新文件{filename}-{selected_algorithm}加密成功"
    else:
        return False, file_path_or_message


def varify_file_password(file: str, password: str):
    if not file:
        return False, "请先选择文件！"
    if not password:
        return False, "请输入加密密码！"

    match file['algorithm']:
        case 'AES':
            filled_password = password.rjust(32, DELIMITER)
        case 'DES':
            filled_password = password.rjust(8, DELIMITER)
        case '3DES':
            filled_password = password.rjust(8, DELIMITER)
        case 'SM4':
            filled_password = password.rjust(16, DELIMITER)
    if verify_password(filled_password, file['password_hash']):
        return True, "解密成功"
    else:
        return False, "密码错误"


def get_file_list(current_user: dict, query: str = '') -> list:
    """查找文件列表"""
    params = {}
    if current_user['role'] != 'admin':
        params['user_name'] = current_user['username']
    return db.get_file_list(params, query)


def delete_file(current_user: dict, file: dict) -> bool:
    if current_user['role'] != 'admin':
        if file['user_name'] != current_user['username']:
            return False, "用户只能删除自己上传的文件"
    db.delete_file(file['id'])
    return True, "删除成功"


def download_file(file: dict, password: str, path: Path) -> tuple:
    try:
        decrypt_text, _ = decrypt_file(file['algorithm'], password, file['id'])
        with open(path, 'wb') as f:
            f.write(decrypt_text)
        return True, f'下载成功, 保存位置{path}'
    except:
        from traceback import print_exc

        print_exc()
        return False, '下载失败'
