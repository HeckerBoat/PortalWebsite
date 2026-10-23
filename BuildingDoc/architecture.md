# 项目架构说明

本文档记录项目每个文件/目录的作用，方便快速定位功能对应文件。

## 目录结构

```
PortalWebsite/
├── app.py                      # 后端启动入口，注册蓝图、静态服务、前端服务
├── run_app.bat                 # Windows 启动脚本
├── requirements.txt            # Python 依赖
├── .env / .env.example         # 环境变量配置
├── .gitignore
├── README.md / README_zh.md    # 项目说明
│
├── backend/                    # 后端代码（Flask）
│   ├── __init__.py
│   ├── config.py               # 配置加载（从 .env 读取）
│   ├── database.py             # 数据库引擎与会话（SQLModel + SQLite）
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户模型（users 表）
│   │   ├── html_file.py        # HTML 文件模型（html_files 表）
│   │   └── system_config.py    # 系统配置模型（system_configs 表）
│   ├── routes/                 # 路由层（API 接口）
│   │   ├── __init__.py         # 登录/管理员权限装饰器
│   │   ├── auth.py             # 认证接口：注册、登录、当前用户
│   │   ├── html_manager.py     # HTML 管理：扫描、列表、详情、更新、删除
│   │   ├── user_manager.py     # 用户管理：增删改查（仅管理员）
│   │   └── system_config.py    # 系统配置：读写配置项
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── scanner.py          # HTML 文件扫描（遍历目录、提取 title）
│   │   ├── auth_service.py     # 认证服务（注册、登录、JWT、权限校验）
│   │   └── html_service.py     # HTML 管理服务（扫描同步、CRUD）
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── security.py         # 密码二次哈希、JWT 生成/解析
│       └── response.py         # 统一响应封装
│
├── Frontend/                   # 前端代码（Vue3 + Vite + TS + Element Plus）
│   ├── index.html              # Vite 入口 HTML
│   ├── package.json
│   ├── vite.config.ts          # Vite 配置（含 API 代理到 5001）
│   ├── tsconfig.json
│   ├── dist/                   # 构建产物（Flask 直接服务）
│   ├── AI悬浮助手.html         # 被管理的 HTML 示例文件
│   └── src/
│       ├── main.ts             # 应用入口
│       ├── App.vue             # 根组件
│       ├── env.d.ts            # 类型声明
│       ├── router/index.ts     # 路由配置与守卫
│       ├── stores/auth.ts      # Pinia 认证状态
│       ├── api/                # API 请求封装
│       │   ├── request.ts      # axios 实例与拦截器
│       │   ├── auth.ts         # 认证相关 API
│       │   ├── html.ts         # HTML 管理 API
│       │   ├── user.ts         # 用户管理 API
│       │   └── config.ts       # 系统配置 API
│       ├── layouts/
│       │   └── MainLayout.vue  # 主布局（侧边栏+顶栏）
│       └── views/              # 页面
│           ├── Login.vue       # 登录/注册页
│           ├── Dashboard.vue   # HTML 管理（扫描、列表、复制URL、编辑、预览、删除）
│           ├── UserManager.vue # 用户管理（管理员）
│           └── SystemConfig.vue# 系统配置
│
├── db/                         # SQLite 数据库文件目录
│   └── app.db
│
├── tests/                      # 测试脚本
│
└── BuildingDoc/                # 项目文档
    ├── SQLTable.md             # 数据库表设计
    ├── architecture.md         # 本文档
    ├── finish_req.md           # 已完成功能需求
    ├── CloudConfig.md          # 云主机反向代理配置
    ├── CloudDeploy.md          # 云主机部署步骤
    └── VercelDeploy.md         # Vercel 部署步骤
```

## 核心流程

### 1. 启动流程
`app.py` → `init_db()` 建表 → `init_admin()` 创建管理员 → `sync_scan()` 首次扫描 → Flask 服务启动

### 2. HTML 扫描同步流程
`scanner.scan_html_files()` 遍历 Frontend 目录（排除 node_modules/dist/根 index.html） → 提取 `<title>` → `html_service.sync_scan()` 与数据库比对（新增/更新/删除）

### 3. URL 生成与访问
- 生成：`/static/html/{relative_path}`
- 访问：Flask 路由 `/static/html/<path:filename>` 直接服务磁盘文件
- 一键复制：前端拼接 `window.location.origin + url` 复制到剪贴板

### 4. 认证流程
注册 → `hash_password()` 二次哈希 → 存储；登录 → `verify_password()` 校验 → 签发 JWT；请求 → 装饰器校验 token
