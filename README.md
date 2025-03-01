# SecureFileGuard

# 1. 开发环境

| 环境 | 版本 | 备注 |
| --- | --- | --- |
| Windows | 11 | x64 |
| Python | 3.12.9 | x64 |
| PySide6 | 6.8.2.1 | 基于QT6, 包含addon和essential |
| PyYaml | 6.0.2 | 用于配置解析 |
| SQLite |  | 轻量级数据库 |
| cryptography |  | 加密模块 支持AES,DES/3DES |
| pysm4 |  | 加密模块 支持SM4 |
| 支持加密算法 |  | AES, DES/3DES, SM4 |
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
- [ ]  用户注销
- [ ]  修改密码
- [ ]  修改个人信息
- [ ]  管理员删除用户

# 3. 界面模块

- [x]  欢迎页面
- [x]  登陆页面
- [x]  注册窗口
- [ ]  主页面(文件列表)
- [ ]  文件上传页
- [ ]  文件下载页
- [ ]  管理员文件列表页面
- [ ]  管理员用户管理页面

# 4. 文件模块

- [ ]  文件上传
- [ ]  文件AES加密
- [ ]  文件CHACHA加密
- [ ]  文件SM4加密
- [ ]  文件列表
- [ ]  文件重命名
- [ ]  文件描述更新
- [ ]  生成随机强密码
- [ ]  复制密码到剪贴板
- [ ]  文件AES解密
- [ ]  文件CHACHA解密
- [ ]  文件SM4解密
- [ ]  文件下载
- [ ]  文件删除
- [ ]  文件名查找
- [ ]  文件用户过滤
- [ ]  文件加密算法过滤
- [ ]  文件更新日期排序

### 属性:

- id主键
- 保存路径
- 创建时间
- 修改时间
- 原始文件名
- 文件描述
- 加密算法
- 上传用户ID
- 上传用户昵称
- salt(盐)
- 密码(加密后的密码字符串)

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
