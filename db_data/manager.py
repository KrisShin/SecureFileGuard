# db/db_manager.py
import sqlite3
from contextlib import contextmanager
from typing import List, Dict
from setting.config_loader import config
from util.tool import get_password_hash


class DBManager(object):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 支持字典式访问
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        with self._get_connection() as conn:
            # 执行所有建表SQL
            conn.executescript(SQL_CREATE_TABLES)

    def init_amdin_user(self) -> dict:
        with self._get_connection() as conn:
            cursor = conn.execute('''SELECT * FROM sfg_user WHERE username='admin' ''')
            admin_user = cursor.fetchone()
            if not admin_user:
                password = get_password_hash(config.other.default_admin_password)
                conn.execute('''INSERT INTO sfg_user (username, password) VALUES (?, ?)''', ('admin', password))
                conn.commit()

    # 用户操作示例
    def create_user(self, user_data: Dict) -> bool:
        with self._get_connection() as conn:
            try:
                conn.execute(
                    '''
                    INSERT INTO sfg_user (username, password, ...)
                    VALUES (?, ?, ?, ...)
                ''',
                    (user_data['username'], ...),
                )
                conn.commit()
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
