# 云主机反向代理配置

## 架构说明

- **云主机公网 IP**：`113.46.196.84`
- **本地主机 IP**：`100.93.80.112`
- **本地服务端口范围**：`5000-6000`
- **目标**：通过云主机反向代理，将公网请求转发到本地主机的 5000-6000 端口服务

本项目后端默认端口为 `5001`，在 5000-6000 范围内，可被代理访问。

---

## 一、云主机安装 Nginx

```bash
# 1. 更新包管理器
sudo apt update

# 2. 安装 nginx
sudo apt install -y nginx

# 3. 启动并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx

# 4. 验证安装
nginx -v
```

**原因**：Nginx 是高性能反向代理服务器，负责将公网请求转发到内网服务。

---

## 二、配置反向代理

### 2.1 创建站点配置文件

```bash
sudo nano /etc/nginx/sites-available/portal-website
```

写入以下内容：

```nginx
server {
    listen 80;
    server_name 113.46.196.84;

    # 代理本地主机 5000-6000 端口的所有服务
    # 方式一：按路径前缀转发到不同端口（推荐）
    # 例如 /app5001/ 转发到 100.93.80.112:5001
    location ~ ^/app(\d+)/(.*)$ {
        proxy_pass http://100.93.80.112:$1/$2$is_args$args;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 方式二：默认转发到 5001 端口（本项目后端）
    location / {
        proxy_pass http://100.93.80.112:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2.2 启用站点

```bash
# 创建软链接启用站点
sudo ln -s /etc/nginx/sites-available/portal-website /etc/nginx/sites-enabled/

# 删除默认站点（可选）
sudo rm -f /etc/nginx/sites-enabled/default
```

**原因**：sites-available 存储配置，sites-enabled 通过软链接启用，便于管理多个站点。

### 2.3 测试并重载 Nginx

```bash
# 测试配置语法
sudo nginx -t

# 重载配置（不中断服务）
sudo systemctl reload nginx
```

**原因**：`nginx -t` 检查配置正确性，避免重载导致服务中断。

---

## 三、配置防火墙（如启用）

```bash
# 允许 HTTP 流量
sudo ufw allow 80/tcp

# 允许 HTTPS 流量（如需）
sudo ufw allow 443/tcp

# 查看防火墙状态
sudo ufw status
```

**原因**：确保公网能访问云主机的 80/443 端口。

---

## 四、云主机安全组配置

在云服务商控制台的安全组中，放行以下端口：
- TCP 80（HTTP）
- TCP 443（HTTPS，如需）

---

## 五、验证代理

```bash
# 在云主机上测试能否访问本地服务
curl http://100.93.80.112:5001/api/health

# 从公网测试代理
curl http://113.46.196.84/api/health
```

**预期结果**：返回 `{"code":0,"message":"ok","data":{"status":"running"}}`

---

## 六、（可选）配置 HTTPS

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书并自动配置 Nginx
sudo certbot --nginx -d 113.46.196.84

# 自动续期
sudo certbot renew --dry-run
```

**原因**：HTTPS 保障数据传输安全，生产环境建议启用。
