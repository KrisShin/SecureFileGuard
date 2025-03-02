from pathlib import Path
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import DES
import os

from module.common import create_dir_if_not_exists, get_password_hash
from setting.config_loader import config
from db_data.manager import db


def encrypt_file_AES(input_file: str, username: str, filename: str, key: bytes):
    """使用 AES 加密文件"""
    iv = os.urandom(16)  # 生成 16 字节的随机 IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    file_size = Path(input_file).stat().st_size
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    # PKCS7 填充
    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    file_path = Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    db.upload_file(key, get_password_hash(key), iv, username, file_path.as_posix(), 'AES', file_size, filename)


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


def encrypt_file_SM4(input_file: str, username: str, filename: str, key: bytes):
    """使用 SM4 加密文件"""
    iv = os.urandom(16)  # 生成 16 字节的随机 IV
    cipher = Cipher(algorithms.SM4(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    file_size = Path(input_file).stat().st_size
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    # PKCS7 填充
    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    file_path = Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    db.upload_file(key, get_password_hash(key), iv, username, file_path.as_posix(), 'SM4', file_size, filename)


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


def encrypt_file_3DES(input_file: str, username: str, filename: str, key: bytes):
    """使用 3DES 加密文件"""
    iv = os.urandom(8)  # 3DES IV 长度为 8 字节
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    file_size = Path(input_file).stat().st_size
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    # PKCS7 填充
    pad_len = 8 - (len(plaintext) % 8)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    file_path = Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    db.upload_file(key, get_password_hash(key), iv, username, file_path.as_posix(), '3DES', file_size, filename)


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


def encrypt_file_DES(input_file: str, username: str, filename: str, key: bytes):
    """使用 DES 加密文件"""
    iv = os.urandom(8)  # DES IV 长度为 8 字节
    cipher = DES.new(key, DES.MODE_CBC, iv)

    file_size = Path(input_file).stat().st_size
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    # PKCS7 填充
    pad_len = 8 - (len(plaintext) % 8)
    plaintext += bytes([pad_len] * pad_len)

    ciphertext = cipher.encrypt(plaintext)

    file_path = Path(config.path.upload) / username / (filename + str(time.time()))
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(ciphertext)  # 存储密文
    db.upload_file(key, get_password_hash(key), iv, username, file_path.as_posix(), 'DES', file_size, filename)


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


# 示例使用
if __name__ == "__main__":
    decrypt_file_AES(1, '123123'.rjust(32, '$').encode('utf-8'))
