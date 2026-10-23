# HTML 自动管理网站

自动扫描 Frontend 目录下的 HTML 文件，为每个文件生成访问 URL，支持 URL 的增删改查与一键复制。

## 技术栈

- **后端**：Python Flask + SQLModel + SQLite
- **前端**：Vue3 + Vite + TypeScript + Element Plus
- **认证**：JWT + 密码二次哈希

## 功能特性

- 自动扫描 `Frontend` 目录下所有 HTML 文件并生成 URL
- 扫描时自动提取页面标题、文件大小、修改时间
- URL 列表管理：搜索、编辑、删除、预览
- 一键复制完整 URL 到剪贴板
- 用户注册/登录（邮箱或手机号），密码二次哈希加密
- 管理员可对任意用户信息进行任意修改
- 系统配置持久化到 SQLite，前端参数修改后自动保存

## 快速开始

### 1. 环境要求

- Python 3.12
- Node.js 18+
- uv（Python 包管理器）

### 2. 安装依赖

```bash
# 创建 Python 虚拟环境
uv venv .venv --python 3.12
uv pip install -r requirements.txt

# 安装前端依赖并构建
cd Frontend
npm install
npm run build
cd ..
```

### 3. 启动项目

**Windows（推荐）**：
```bash
run_app.bat
```

**手动启动**：
```bash
# 激活虚拟环境
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Linux/Mac

# 启动
python app.py
```

### 4. 访问

- 前端页面：http://127.0.0.1:5001
- 默认管理员：`admin` / `1q2w3e4r`

## 目录结构

```
PortalWebsite/
├── app.py              # 后端启动入口
├── run_app.bat         # 启动脚本
├── requirements.txt    # Python 依赖
├── .env                # 环境变量
├── backend/            # 后端代码
│   ├── models/         # 数据模型
│   ├── routes/         # API 路由
│   ├── services/       # 业务服务
│   └── utils/          # 工具函数
├── Frontend/           # 前端代码
│   ├── src/
│   │   ├── views/      # 页面
│   │   ├── api/        # API 请求
│   │   └── stores/     # 状态管理
│   └── dist/           # 构建产物
├── db/                 # SQLite 数据库
└── BuildingDoc/        # 项目文档
```

## 配置说明

编辑 `.env` 文件修改配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_HOST | 服务监听地址 | 0.0.0.0 |
| FLASK_PORT | 服务端口 | 5001 |
| HTML_SCAN_DIR | HTML 扫描目录 | Frontend |
| ADMIN_USERNAME | 管理员用户名 | admin |
| ADMIN_PASSWORD | 管理员密码 | 1q2w3e4r |

## 文档

- [数据库设计](./BuildingDoc/SQLTable.md)
- [架构说明](./BuildingDoc/architecture.md)
- [已完成需求](./BuildingDoc/finish_req.md)
- [云主机配置](./BuildingDoc/CloudConfig.md)
- [云主机部署](./BuildingDoc/CloudDeploy.md)
- [Vercel 部署](./BuildingDoc/VercelDeploy.md)
