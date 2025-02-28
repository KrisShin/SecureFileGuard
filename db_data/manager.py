# db/db_manager.py
from sqlite3 import connect, Row
from contextlib import contextmanager
from typing import List, Dict
from setting.config_loader import config
from module.user_apis import get_password_hash


class DBManager(object):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()

    @contextmanager
    def _get_connection(self):
        conn = connect(self.db_path)
        conn.row_factory = Row  # 支持字典式访问
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        with self._get_connection() as conn:
            # 执行所有建表SQL
            conn.executescript(SQL_CREATE_TABLES)

    def init_amdin_user(self) -> dict:
        """初始化管理员用户"""
        admin_obj = self.get_user('admin')
        if not admin_obj:
            password = get_password_hash(config.other.default_admin_password)
            with self._get_connection() as conn:
                conn.execute('''INSERT INTO sfg_user (username, password, role) VALUES (?, ?, ?)''', ('admin', password, 'admin'))
                conn.commit()

    def get_user(self, username) -> dict:
        """根据用户名查询用户信息"""
        with self._get_connection() as conn:
            cursor = conn.execute('''SELECT * FROM sfg_user WHERE username=? ''', (username,))
            user_obj = cursor.fetchone()
            return dict(user_obj)

    def get_user_list(self, params: dict) -> List[dict]:
        """根据用户名查询用户信息"""
        with self._get_connection() as conn:
            sql_str = """SELECT * FROM sfg_user"""
            sql_params = None
            if params:
                sql_params = []
                [sql_params.extend([k, v]) for k, v in params.items()]
                sql_str += 'WHERE' + ' '.join(['?=?' for _ in range(len(sql_params))])
            cursor = conn.execute(sql_str, sql_params)

            user_obj = cursor.fetchone()
            return dict(user_obj)

    # 用户操作示例
    def create_user(self, user_data: Dict) -> bool:
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
            except sqlite3.IntegrityError:
                return False

    # 文件查询（带分页）
    def get_user_files(self, username: str, page: int = 1, per_page: int = 20) -> List[Dict]:
        offset = (page - 1) * per_page
        with self._get_connection() as conn:
            cursor = conn.execute(
                '''
                SELECT * FROM encrypted_file
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''',
                (username, per_page, offset),
            )
            return [dict(row) for row in cursor]

    # 安全审计日志
    def log_operation(self, log_data: Dict):
        with self._get_connection() as conn:
            conn.execute(
                '''
                INSERT INTO audit_log 
                (user_id, action_type, ip_address, ...)
                VALUES (?, ?, ?, ...)
            ''',
                (log_data['user_id'], ...),
            )
            conn.commit()


# 建表语句示例
SQL_CREATE_TABLES = '''
CREATE TABLE IF NOT EXISTS sfg_user (
    username VARCHAR(50) PRIMARY KEY,          -- 账号（主键）
    password CHAR(256) NOT NULL,               -- 加密后的密码
    role TEXT CHECK(role IN ('user', 'admin')) DEFAULT 'user',  -- 用户角色
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,                       -- 最后登录时间
    phone VARCHAR(20) UNIQUE,                  -- 唯一手机号
    email VARCHAR(100) UNIQUE,                 -- 唯一邮箱
    is_locked BOOLEAN DEFAULT FALSE            -- 删除末尾的逗号
);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_user_role ON sfg_user(role);
CREATE INDEX IF NOT EXISTS idx_user_lock ON sfg_user(is_locked);

CREATE TABLE IF NOT EXISTS sfg_encrypted_file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_path TEXT NOT NULL,               -- 加密后存储路径
    original_name VARCHAR(255) NOT NULL,      -- 原始文件名
    file_size BIGINT,                         -- 文件大小（字节）
    description TEXT,                         -- 文件描述
    algorithm VARCHAR(50) NOT NULL,           -- 加密算法（AES-256等）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_at DATETIME,                     -- 最后修改时间
    user_name VARCHAR(50) NOT NULL,           -- 上传用户ID（外键）
    salt CHAR(32) NOT NULL,                   -- 加密盐值
    encrypted_password TEXT NOT NULL,         -- 加密后的密码
    is_public BOOLEAN DEFAULT FALSE,          -- 是否公开
    FOREIGN KEY (user_name) REFERENCES user(username)
);
-- 文件表索引
CREATE INDEX IF NOT EXISTS idx_file_algorithm ON sfg_encrypted_file(algorithm);
CREATE INDEX IF NOT EXISTS idx_file_user ON sfg_encrypted_file(user_name);
CREATE INDEX IF NOT EXISTS idx_file_public ON sfg_encrypted_file(is_public);

CREATE TABLE IF NOT EXISTS sfg_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(50) NOT NULL,           -- 操作用户
    action_type VARCHAR(50) NOT NULL,         -- 操作类型：login/upload/delete
    action_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_id INTEGER NOT NULL,                 -- 文件id
    result TEXT CHECK(result IN('success','failed')) NOT NULL, -- 操作结果
    details TEXT,                             -- 详细日志
    FOREIGN KEY (user_name) REFERENCES user(username)
    FOREIGN KEY (file_id) REFERENCES encrypted_file(id)
);
-- 日志表索引
CREATE INDEX IF NOT EXISTS idx_log_action ON sfg_audit_log(action_type);
CREATE INDEX IF NOT EXISTS idx_log_user ON sfg_audit_log(user_name);
'''

db = DBManager(config.path.db_file)
