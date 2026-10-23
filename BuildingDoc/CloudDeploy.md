# 云主机部署步骤

## 前提条件
- 云主机已配置反向代理（见 [CloudConfig.md](./CloudConfig.md)）
- 本地主机（100.93.80.112）可被云主机访问
- 项目代码已上传到本地主机

---

## 一、本地主机环境准备

### 1. 安装 Python 3.12 和 uv

```bash
# 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 固定 Python 版本
uv python pin 3.12
```

### 2. 安装 Node.js（用于构建前端）

```bash
# 使用 nvm 安装 Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

### 3. 克隆/上传项目

```bash
cd /opt
git clone <项目仓库地址> PortalWebsite
cd PortalWebsite
```

---

## 二、配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

重点修改：
```env
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
SECRET_KEY=<随机密钥>
JWT_SECRET=<随机密钥>
ADMIN_PASSWORD=<管理员密码>
```

---

## 三、安装依赖

### 1. Python 依赖

```bash
# 创建虚拟环境
uv venv .venv --python 3.12

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

### 2. 前端依赖与构建

```bash
cd Frontend
npm install
npm run build
cd ..
```

---

## 四、启动服务

### 方式一：直接启动（开发/测试）

```bash
# Windows
run_app.bat

# Linux
source .venv/bin/activate
python app.py
```

### 方式二：使用 systemd 后台运行（生产推荐）

创建服务文件：

```bash
sudo nano /etc/systemd/system/portal-website.service
```

写入：

```ini
[Unit]
Description=HTML Portal Website
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/PortalWebsite
ExecStart=/opt/PortalWebsite/.venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：

```bash
sudo systemctl daemon-reload
sudo systemctl start portal-website
sudo systemctl enable portal-website

# 查看状态
sudo systemctl status portal-website

# 查看日志
sudo journalctl -u portal-website -f
```

---

## 五、验证部署

```bash
# 本地测试
curl http://127.0.0.1:5001/api/health

# 公网测试（通过云主机代理）
curl http://113.46.196.84/api/health

# 浏览器访问
# http://113.46.196.84
```

---

## 六、更新部署

```bash
cd /opt/PortalWebsite
git pull

# 如有新依赖
uv pip install -r requirements.txt

# 重新构建前端
cd Frontend && npm install && npm run build && cd ..

# 重启服务
sudo systemctl restart portal-website
```
