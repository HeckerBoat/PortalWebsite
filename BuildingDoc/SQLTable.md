# 数据库表设计说明

数据库采用 SQLite，使用 SQLModel 思想定义表结构，数据库文件位于 `db/app.db`。

---

## 1. users（用户表）

**作用**：存储系统所有用户账号信息，支持邮箱或手机号注册，密码二次哈希加密存储。

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| id | Integer | 主键ID | 自增主键 |
| username | String(64) | 用户名 | 唯一，登录账号之一 |
| email | String(128) | 邮箱 | 可空，唯一，注册账号之一 |
| phone | String(20) | 手机号 | 可空，唯一，注册账号之一 |
| password_hash | String(512) | 密码密文 | 二次哈希后的密码，格式：`salt$sha256_hash$werkzeug_hash` |
| role | String(20) | 角色 | `admin`（管理员）或 `user`（普通用户），默认 `user` |
| is_active | Boolean | 是否启用 | 默认 True，管理员可禁用用户 |
| created_at | DateTime | 创建时间 | 账号创建时间 |
| updated_at | DateTime | 更新时间 | 信息最后更新时间 |

**设计原因**：
- username/email/phone 均加索引并唯一，支持三种方式登录
- 密码采用二次哈希：先用 werkzeug 的 pbkdf2:sha256 哈希，再叠加随机盐值的 sha256 哈希，双重保障
- role 字段区分管理员与普通用户，管理员可对任意用户信息进行任意修改

---

## 2. html_files（HTML 文件表）

**作用**：存储扫描到的 Frontend 目录下的 HTML 文件信息及生成的访问 URL，支持增删改查。

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| id | Integer | 主键ID | 自增主键 |
| filename | String(255) | 文件名 | 含扩展名，如 `AI悬浮助手.html` |
| relative_path | String(1024) | 相对路径 | 相对于扫描根目录的路径 |
| absolute_path | String(2048) | 绝对路径 | 文件在磁盘上的绝对路径 |
| url | String(2048) | 访问URL | 生成的访问地址，如 `/static/html/AI悬浮助手.html` |
| title | String(255) | 页面标题 | 从 HTML 的 `<title>` 标签提取 |
| description | String(1024) | 备注描述 | 用户可自定义的备注 |
| file_size | Integer | 文件大小 | 单位：字节 |
| last_modified | DateTime | 文件修改时间 | 磁盘文件最后修改时间 |
| created_at | DateTime | 记录创建时间 | 记录入库时间 |
| updated_at | DateTime | 记录更新时间 | 记录最后更新时间 |

**设计原因**：
- relative_path 作为扫描同步的唯一标识，用于判断文件是新增/更新/删除
- url 字段可被用户修改，支持自定义访问地址
- 自动提取 title 方便识别页面内容
- file_size 和 last_modified 用于检测文件变化，触发更新

---

## 3. system_configs（系统配置表）

**作用**：存储前端参数配置，程序启动时读取并同步到前端，参数修改后持久化到数据库。

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| id | Integer | 主键ID | 自增主键 |
| key | String(128) | 配置键 | 唯一，配置项名称 |
| value | String(4096) | 配置值 | 配置项的值，字符串形式 |
| description | String(512) | 配置说明 | 配置项的用途描述 |
| updated_at | DateTime | 更新时间 | 配置最后修改时间 |

**设计原因**：
- key-value 结构灵活，支持任意前端参数存储
- 前端修改参数后调用 API 写入数据库，下次启动自动加载
- 与具体业务解耦，新增配置无需改表结构

---

## 设计总结

1. **三张表职责清晰**：用户、HTML文件、系统配置，覆盖核心业务
2. **密码二次哈希**：满足安全存储要求
3. **扫描同步机制**：通过 relative_path 比对实现自动增删改
4. **配置持久化**：前端参数实时保存到 SQLite，重启不丢失
