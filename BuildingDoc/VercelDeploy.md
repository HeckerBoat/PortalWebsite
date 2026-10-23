# Vercel 部署步骤

> 注意：本项目后端为 Flask（Python），Vercel 对 Python 支持有限。
> 推荐方案：前端部署到 Vercel，后端部署到云主机（见 CloudDeploy.md）。
> 以下为前端单独部署到 Vercel 的步骤。

---

## 一、准备工作

### 1. 注册 Vercel 账号
访问 https://vercel.com 注册账号（支持 GitHub 登录）。

### 2. 安装 Vercel CLI

```bash
npm install -g vercel
```

### 3. 修改前端 API 地址

由于前端部署到 Vercel，后端在云主机，需要修改前端请求地址。

编辑 `Frontend/src/api/request.ts`，将 baseURL 改为后端地址：

```typescript
const request = axios.create({
  baseURL: 'http://113.46.196.84',  // 云主机后端地址
  timeout: 15000,
})
```

或使用环境变量：
```typescript
baseURL: import.meta.env.VITE_API_BASE_URL || '/'
```

在 `Frontend/.env.production` 中配置：
```env
VITE_API_BASE_URL=http://113.46.196.84
```

---

## 二、配置 Vercel

### 方式一：通过 Vercel 网页部署

1. 登录 Vercel，点击 "Add New Project"
2. 导入 GitHub 仓库
3. 配置构建设置：
   - **Framework Preset**: Vite
   - **Root Directory**: `Frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. 添加环境变量：
   - `VITE_API_BASE_URL` = `http://113.46.196.84`
5. 点击 "Deploy"

### 方式二：通过 CLI 部署

```bash
cd Frontend

# 登录
vercel login

# 部署（开发预览）
vercel

# 部署到生产环境
vercel --prod
```

---

## 三、配置重写规则（可选）

如果后端 API 需要通过 Vercel 代理，创建 `Frontend/vercel.json`：

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "http://113.46.196.84/api/:path*" },
    { "source": "/static/html/:path*", "destination": "http://113.46.196.84/static/html/:path*" }
  ]
}
```

**原因**：通过 Vercel 代理后端请求，避免跨域问题。

---

## 四、后端 CORS 配置

确保后端允许 Vercel 域名跨域访问。

编辑 `app.py`：

```python
CORS(app, supports_credentials=True, resources={
    r"/api/*": {"origins": ["https://your-project.vercel.app"]}
})
```

---

## 五、验证部署

部署完成后，Vercel 会提供一个域名，如 `https://portal-website.vercel.app`。

访问该域名，测试：
1. 登录功能（admin / 1q2w3e4r）
2. HTML 文件列表加载
3. 扫描同步功能
4. URL 复制功能

---

## 六、注意事项

1. **后端必须独立部署**：Vercel Serverless Functions 不适合 Flask 长驻服务，后端需部署到云主机
2. **CORS 配置**：确保后端允许 Vercel 域名
3. **环境变量**：敏感信息使用 Vercel 环境变量管理，不要硬编码
4. **自定义域名**：可在 Vercel 项目设置中绑定自定义域名
