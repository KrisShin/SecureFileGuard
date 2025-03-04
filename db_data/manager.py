# db/db_manager.py
from contextlib import contextmanager
from sqlite3 import IntegrityError, Row, connect
from typing import Dict, List

from module.common import get_password_hash
from setting.config_loader import config


class DBManager(object):
    """数据库管理类"""

    def __init__(self, db_path: str):
        self.db_path = db_path  # 读取数据库文件路径
        self._init_tables()

    @contextmanager
    def _get_connection(self):
        """连接数据库"""
        conn = connect(self.db_path)
        conn.row_factory = Row  # 支持字典式访问
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        """初始化表格"""
        with self._get_connection() as conn:
            # 执行初始化表格sql语句L
            conn.executescript(SQL_CREATE_TABLES)

    def init_amdin_user(self) -> dict:
        """初始化管理员用户, 查找是否有admin用户, 没有则新建admin用户"""
        admin_obj = self.get_user('admin')
        if not admin_obj:
            password = get_password_hash(config.other.default_admin_password)
            with self._get_connection() as conn:
                conn.execute('''INSERT INTO sfg_user (username, password, role) VALUES (?, ?, ?)''', ('admin', password, 'admin'))
                conn.commit()  # 提交sql命令
        # 增加一些测试用户
        # self._add_test_user()

    def get_user(self, username) -> dict:
        """根据用户名查询用户信息"""
        with self._get_connection() as conn:
            cursor = conn.execute('''SELECT * FROM sfg_user WHERE username=? ''', (username,))
            user_obj = cursor.fetchone()
            return user_obj and dict(user_obj)

    def get_user_list(self, params: dict, query: str = '') -> List[dict]:
        """查询用户信息列表"""
        with self._get_connection() as conn:
            """拼接sql语句适配各种参数"""
            sql_str = """SELECT * FROM sfg_user """
            sql_values = []
            if params:
                sql_keys = []
                for key, value in params.items():
                    sql_keys.append(f'"{key}"=?')
                    sql_values.append(value)
                sql_str += 'WHERE ' + ' and '.join(sql_keys)
            if query:
                if params:
                    sql_str += f" AND "
                else:
                    sql_str += f" WHERE "
                sql_str += f"(username LIKE ? OR phone LIKE ? OR email LIKE ?)"
                sql_values.extend([f'%{query}%'] * 3)
            sql_str += ' ORDER BY username'  # 根据用户名排序
            cursor = conn.execute(sql_str, sql_values)
            rows = cursor.fetchall()
            return rows and [dict(user_obj) for user_obj in rows]

    # 用户操作示例
    def create_user(self, user_data: Dict) -> bool:
        """创建用户"""
        password = get_password_hash(user_data['password'])
        with self._get_connection() as conn:
            try:
                conn.execute(
                    '''INSERT INTO sfg_user (username, password, phone, email) VALUES (?, ?, ?, ?)''',
                    (user_data['username'], password, user_data.get('phone'), user_data.get('email')),
                )
                conn.commit()
                print(f"用户{user_data['username']} 注册成功")
                return True
            except IntegrityError:
                return False

    def update_user_info(self, username: str, params: dict) -> Dict:
        """更新用户数据"""
        sql_str = """update sfg_user set """
        if not params:
            return
        sql_keys = []
        sql_values = []
        for key, value in params.items():
            sql_keys.append(f'"{key}"=?')
            sql_values.append(value)
        sql_str += ' , '.join(sql_keys)
        sql_values.append(username)
        with self._get_connection() as conn:
            try:
                conn.execute(f'''{sql_str} WHERE username = ?''', sql_values)
                conn.commit()
                print(f"用户{username} 更新成功")
                return True
            except IntegrityError:
                return False

    def update_user_last_login(self, username: str):
        """更新用户上次登录时间"""
        with self._get_connection() as conn:
            try:
                conn.execute('''UPDATE sfg_user SET last_login = CURRENT_TIMESTAMP WHERE username=? ''', (username,))
                conn.commit()
                print(f"用户{username} 登录成功")
                return True
            except IntegrityError:
                return False

    def delete_user(self, username: str):
        """删除用户"""
        with self._get_connection() as conn:
            try:
                conn.execute('''DELETE FROM sfg_user WHERE username=? ''', (username,))
                conn.commit()
                print(f"用户{username} 删除成功")
                return True
            except IntegrityError:
                return False

    def _add_test_user(self):
        """添加测试用户"""
        import datetime
        import random
        import string

        password = get_password_hash(config.other.default_admin_password)
        with self._get_connection() as conn:
            for index in range(100):
                username = f'{index}__' + ''.join(random.choices(string.ascii_letters, k=random.randint(3, 20)))
                phone = '1' + ''.join(random.choices(string.digits, k=10))
                email = (
                    ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
                    + '@'
                    + ''.join(random.choices(string.ascii_letters, k=random.randint(2, 8)))
                    + '.'
                    + ''.join(random.choices(string.ascii_letters, k=random.randint(2, 5)))
                )
                last_login = datetime.datetime(
                    day=random.randint(1, 28), month=random.randint(1, 12), year=2025, hour=random.randint(0, 23), minute=random.randint(0, 59)
                )
                conn.execute(
                    '''INSERT INTO sfg_user (username, password, role, phone, email, last_login) VALUES (?, ?, ?, ?, ?, ?)''',
                    (username, password, 'user', phone, email, last_login),
                )
            conn.commit()

    # 上传文件
    def upload_file(self, password, password_hash, iv, username, file_path, algorithm, file_size, file_name) -> bool:
        """上传用户"""
        with self._get_connection() as conn:
            try:
                conn.execute(
                    '''INSERT INTO sfg_encrypted_file (password, password_hash, iv, user_name, file_path, algorithm, file_size, file_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (password, password_hash, iv, username, file_path, algorithm, file_size, file_name),
                )
                conn.commit()
                print(f"用户{username} 上传文件 {file_name} 成功")
                return True
            except IntegrityError:
                return False

    def edit_file(self, file_id, password, password_hash, iv, algorithm, file_name) -> bool:
        # 编辑用户信息
        with self._get_connection() as conn:
            try:
                conn.execute(
                    f'''update sfg_encrypted_file set  password=?, password_hash=?, iv=?, algorithm=?, file_name=?, modified_at=CURRENT_TIMESTAMP where id=?''',
                    (password, password_hash, iv, algorithm, file_name, file_id),
                )
                conn.commit()
                print(f"更新文件 {file_name} 成功")
                return True
            except IntegrityError:
                return False

    # 查找单个文件
    def get_file_by_id(self, file_id: int) -> dict | None:
        with self._get_connection() as conn:
            try:
                cursor = conn.execute('''SELECT * FROM sfg_encrypted_file WHERE id=?''', (file_id,))
                file_obj = cursor.fetchone()
                return file_obj and dict(file_obj)
            except IntegrityError:
                return False

    # 文件查询
    def get_file_list(self, params: dict = {}, query: str = '') -> List[Dict]:
        with self._get_connection() as conn:
            sql_str = """SELECT * FROM sfg_encrypted_file """
            sql_values = []
            if params:
                sql_keys = []
                for key, value in params.items():
                    sql_keys.append(f'"{key}"=?')
                    sql_values.append(value)
                sql_str += 'WHERE ' + ' and '.join(sql_keys)
            if query:
                if params:
                    sql_str += f" AND "
                else:
                    sql_str += f" WHERE "
                sql_str += f"(file_name LIKE ? OR user_name LIKE ? OR algorithm LIKE ?)"
                sql_values.extend([f'%{query}%'] * 3)
            sql_str += ' ORDER BY file_name, algorithm '
            cursor = conn.execute(sql_str, sql_values)
            rows = cursor.fetchall()
            return rows and [dict(file_obj) for file_obj in rows]

    def delete_file(self, file_id: int):
        """删除文件"""
        with self._get_connection() as conn:
            try:
                conn.execute('''DELETE FROM sfg_encrypted_file WHERE id=? ''', (file_id,))
                conn.commit()
                print(f"文件删除成功")
                return True
            except IntegrityError:
                return False


# 建表语句示例
SQL_CREATE_TABLES = '''
CREATE TABLE IF NOT EXISTS sfg_user (
    username VARCHAR(50) PRIMARY KEY,          -- 账号（主键）
    password CHAR(256) NOT NULL,               -- 加密后的密码
    role TEXT CHECK(role IN ('user', 'admin')) DEFAULT 'user',  -- 用户角色
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,                       -- 最后登录时间
    phone VARCHAR(20) UNIQUE COLLATE NOCASE,   -- 唯一手机号(忽略大小写)
    email VARCHAR(100) UNIQUE COLLATE NOCASE,  -- 唯一邮箱(忽略大小写)
    is_locked BOOLEAN DEFAULT FALSE            -- 是否锁定(禁止登录)
);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_user_role ON sfg_user(role);
CREATE INDEX IF NOT EXISTS idx_user_lock ON sfg_user(is_locked);

CREATE TABLE IF NOT EXISTS sfg_encrypted_file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,                  -- 加密后存储路径
    file_name VARCHAR(255) NOT NULL,          -- 原始文件名
    file_size BIGINT,                         -- 文件大小（字节）
    description TEXT,                         -- 文件描述
    algorithm VARCHAR(50) NOT NULL,           -- 加密算法（AES-256等）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_at DATETIME,                     -- 最后修改时间
    user_name VARCHAR(50) NOT NULL,           -- 上传用户ID（外键）
    password CHAR(32) NOT NULL,               -- 密码(用于查询找回密码)
    password_hash CHAR(32) NOT NULL,          -- 加密密码
    iv CHAR(32) NULL,                         -- 加密向量
    is_public BOOLEAN DEFAULT FALSE,          -- 是否公开
    FOREIGN KEY (user_name) REFERENCES user(username)
);
-- 文件表索引
CREATE INDEX IF NOT EXISTS idx_file_algorithm ON sfg_encrypted_file(algorithm);
CREATE INDEX IF NOT EXISTS idx_file_user ON sfg_encrypted_file(user_name);
CREATE INDEX IF NOT EXISTS idx_file_public ON sfg_encrypted_file(is_public);
'''

db = DBManager(config.path.db_file)
