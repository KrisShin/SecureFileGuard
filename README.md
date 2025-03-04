# SecureFileGuard

# 1. 开发环境

| 环境 | 版本 | 备注 |
| --- | --- | --- |
| Windows | 11 | x64 |
| Python | 3.12.9 | x64 |
| PySide6 | 6.8.2.1 | 基于QT6, 包含addon和essential |
| PyYaml | 6.0.2 | 用于配置解析 |
| SQLite |  | 轻量级数据库 |
| cryptography | 44.0.2 | 加密模块 支持AES,3DES, SM4 |
| pycryptodome | 3.21.0 | 加密模块 支持DES |
| 支持加密算法 |  | AES, DES, 3DES, SM4 |
| nuitka | 2.* | 用于编译打包 |
| .net_x64 |  | win系统组件库 |

# 2. 用户模块

- [x]  用户注册
    - 账号(主键)
    - 密码
    - 角色(用户/管理员)
    - 创建时间
    - 上次登录时间
    - 电话
    - 邮箱
- [x]  用户登录
- [x]  用户注销
- [x]  修改密码
- [x]  修改个人信息
- [x]  管理员删除用户
- [x]  用户查找
- [x]  用户列表
- [x]  支持密码切换明文/密文显示

# 3. 界面模块

- [x]  欢迎页面

![image.png](attachment:ba391deb-65cd-43de-894d-bc0abbaf9e03:image.png)

- [x]  登陆页面

![image.png](attachment:58a35f5e-74c4-4ab5-ab4a-dc3d55dc8bb6:image.png)

- [x]  注册页面

![image.png](attachment:fbdb8bb5-ac59-4931-b5f3-74b84d01c748:image.png)

- [x]  主页面(文件列表)

![image.png](attachment:c0726a9f-2500-460a-a4bb-03b97e7be517:image.png)

- [x]  文件上传页

![image.png](attachment:9aabb6d4-0f9c-4716-81ba-e2e6290a8324:image.png)

- [x]  文件编辑页

![image.png](attachment:32de596c-3fca-45ef-bcf5-39219f7f410b:image.png)

- [x]  用户密码修改

![image.png](attachment:d466eb0e-d53e-4242-81ee-d8341d0d8b48:image.png)

- [x]  用户信息编辑

![image.png](attachment:cf61f875-8788-41d4-b465-2bc8bc2eb9c1:image.png)

- [x]  管理员用户管理页面

![image.png](attachment:70d78f6a-3f9d-4daa-b0f1-ccbf47acbab6:image.png)

# 4. 文件模块

- [x]  文件上传
- [x]  文件AES加密
- [x]  文件DES加密
- [x]  文件3DES加密
- [x]  文件SM4加密
- [x]  文件列表
- [x]  文件信息编辑(文件名, 加密算法, 改密码)
- [x]  生成随机强密码
- [x]  复制密码到剪贴板
- [x]  文件AES解密
- [x]  文件DES解密
- [x]  文件3DES解密
- [x]  文件SM4解密
- [x]  文件下载
- [x]  文件删除
- [x]  文件名查找
- [x]  文件查找
- [x]  文件用户过滤
- [x]  文件加密算法过滤

### 属性:

```sql
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
```

# 5. 配置文件

```yaml
app:
  name: "文件加密工具"          # 项目名称
  version: "0.1.0"             # 版本号
  author: "Kris"               # 作者
  release_date: "2025-02-28"   # 发布日期

path:
  static: "assets"             # 静态文件路径
  db_file: "db_data/data.db"    # 数据库文件路径
  upload: "upload"              # 文件上传路径
  download: "download"          # 文件下载路径

security:
  default_algorithm: "AES"      # 默认使用加密算法
  algorithms:                   # 支持算法
    - "AES"
    - "DES/3DES"
    - "SM4"

other:
  width: 900                    # 窗口宽度
  height: 600                   # 窗口高度
  splash_timeout: 1000           # 欢迎屏幕持续时间
  default_admin_password: '123qwe' # 默认管理员密码
```