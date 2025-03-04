import os
import time
from pathlib import Path

from Crypto.Cipher import DES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from db_data.manager import db
from module.common import create_dir_if_not_exists
from setting.config_loader import config
from setting.global_variant import DELIMITER


def encrypt_file_AES(input_file: str, username: str, filename: str, key: bytes, plaintext: str = '', file_path: Path = ''):
    """使用 AES 加密文件"""
    iv = os.urandom(16)  # 生成 16 字节的随机 IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    if not plaintext:
        with open(input_file, 'rb') as f:
            plaintext = f.read()

    # PKCS7 填充
    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    file_path = file_path or Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    return iv, file_path


def decrypt_file_AES(file_id: int, key: bytes):
    """使用 AES 解密文件"""
    file_dict = db.get_file_by_id(file_id)
    with open(file_dict['file_path'], 'rb') as f:
        data = f.read()

    iv = file_dict['iv']  # 读取 IV
    ciphertext = data

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # 去除 PKCS7 填充
    pad_len = plaintext[-1]
    plaintext = plaintext[:-pad_len]

    return plaintext


def encrypt_file_SM4(input_file: str, username: str, filename: str, key: bytes, plaintext: str = '', file_path: Path = ''):
    """使用 SM4 加密文件"""
    iv = os.urandom(16)  # 生成 16 字节的随机 IV
    cipher = Cipher(algorithms.SM4(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    if not plaintext:
        with open(input_file, 'rb') as f:
            plaintext = f.read()

    # PKCS7 填充
    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    file_path = file_path or Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    return iv, file_path


def decrypt_file_SM4(file_id: int, key: bytes):
    """使用 SM4 解密文件"""
    file_dict = db.get_file_by_id(file_id)
    with open(file_dict['file_path'], 'rb') as f:
        data = f.read()

    iv = file_dict['iv']  # 读取 IV
    ciphertext = data

    cipher = Cipher(algorithms.SM4(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # 去除 PKCS7 填充
    pad_len = plaintext[-1]
    plaintext = plaintext[:-pad_len]

    return plaintext


def encrypt_file_3DES(input_file: str, username: str, filename: str, key: bytes, plaintext: str = '', file_path: Path = ''):
    """使用 3DES 加密文件"""
    iv = os.urandom(8)  # 3DES IV 长度为 8 字节
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    if not plaintext:
        with open(input_file, 'rb') as f:
            plaintext = f.read()

    # PKCS7 填充
    pad_len = 8 - (len(plaintext) % 8)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    file_path = file_path or Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    return iv, file_path


def decrypt_file_3DES(file_id: int, key: bytes):
    """使用 3DES 解密文件"""
    file_dict = db.get_file_by_id(file_id)
    with open(file_dict['file_path'], 'rb') as f:
        data = f.read()

    iv = file_dict['iv']  # 读取 IV
    ciphertext = data

    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # 去除 PKCS7 填充
    pad_len = plaintext[-1]
    plaintext = plaintext[:-pad_len]

    return plaintext


def encrypt_file_DES(input_file: str, username: str, filename: str, key: bytes, plaintext: str = '', file_path: Path = ''):
    """使用 DES 加密文件"""
    iv = os.urandom(8)  # DES IV 长度为 8 字节
    cipher = DES.new(key, DES.MODE_CBC, iv)

    if not plaintext:
        with open(input_file, 'rb') as f:
            plaintext = f.read()

    # PKCS7 填充
    pad_len = 8 - (len(plaintext) % 8)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = cipher.encrypt(plaintext)

    file_path = file_path or Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    return iv, file_path


def decrypt_file_DES(file_id: int, key: bytes):
    """使用 DES 解密文件"""
    file_dict = db.get_file_by_id(file_id)
    with open(file_dict['file_path'], 'rb') as f:
        data = f.read()

    iv = file_dict['iv']  # 读取 IV
    ciphertext = data

    cipher = DES.new(key, DES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    # 去除 PKCS7 填充
    pad_len = plaintext[-1]
    plaintext = plaintext[:-pad_len]

    return plaintext


def encrypt_file(algorithm: str, input_file, username, file_name, password, plaintext: str = '', file_path: str = ''):
    match algorithm:
        case 'AES':
            if len(password) > 32:
                return False, "错误", "AES加密, 密码不能超过32位"
            filled_password = password.rjust(32, DELIMITER)
            iv, fpath = encrypt_file_AES(input_file, username, file_name, filled_password.encode('utf-8'), plaintext=plaintext, file_path=file_path)
        case 'DES':
            if len(password) > 8:
                return False, "错误", "DES加密, 密码不能超过8位"
            filled_password = password.rjust(8, DELIMITER)
            iv, fpath = encrypt_file_DES(input_file, username, file_name, filled_password.encode('utf-8'), plaintext=plaintext, file_path=file_path)
        case '3DES':
            if len(password) > 8:
                return False, "错误", "3DES加密, 密码不能超过8位"
            filled_password = password.rjust(8, DELIMITER)
            iv, fpath = encrypt_file_3DES(input_file, username, file_name, filled_password.encode('utf-8'), plaintext=plaintext, file_path=file_path)
        case 'SM4':
            if len(password) > 16:
                return False, "错误", "SM4加密, 密码不能超过16位"
            filled_password = password.rjust(16, DELIMITER)
            iv, fpath = encrypt_file_SM4(input_file, username, file_name, filled_password.encode('utf-8'), plaintext=plaintext, file_path=file_path)
    return True, iv, fpath, filled_password


def decrypt_file(algorithm: str, password: str, file_id: int):
    match algorithm:
        case 'AES':
            filled_password = password.rjust(32, DELIMITER)
            decrypt_text = decrypt_file_AES(file_id, filled_password.encode('utf-8'))
        case 'DES':
            filled_password = password.rjust(8, DELIMITER)
            decrypt_text = decrypt_file_DES(file_id, filled_password.encode('utf-8'))
        case '3DES':
            filled_password = password.rjust(8, DELIMITER)
            decrypt_text = decrypt_file_3DES(file_id, filled_password.encode('utf-8'))
        case 'SM4':
            filled_password = password.rjust(16, DELIMITER)
            decrypt_text = decrypt_file_SM4(file_id, filled_password.encode('utf-8'))
    return decrypt_text, filled_password


# 示例使用
if __name__ == "__main__":
    decrypt_file_AES(1, '123123'.rjust(32, '_').encode('utf-8'))
