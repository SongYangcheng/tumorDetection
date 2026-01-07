# 部署指南

## 概述

本指南介绍如何将tumorDetection应用部署到生产环境。

## 部署架构

### 单机部署

```
┌─────────────────┐
│   Nginx/Apache   │
│     (端口80)     │
└─────────────────┘
         │
    ┌────┴────┐
    │  Flask  │
    │ (端口5000)│
└─────────────────┘
```

### 分布式部署

```
┌─────────────────┐
│   Load Balancer  │
│     (Nginx)      │
└─────────────────┘
         │
    ┌────┼────┐
    │         │
┌──────┐ ┌──────┐
│Flask │ │Flask │
│App 1 │ │App 2 │
└──────┘ └──────┘
```

## 环境准备

### 服务器要求

- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 7+
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: 50GB以上
- **网络**: 稳定的互联网连接

### 软件依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python
sudo apt install python3 python3-pip python3-venv -y

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装Nginx
sudo apt install nginx -y

# 安装Git
sudo apt install git -y
```

## 部署步骤

### 1. 代码部署

```bash
# 创建应用目录
sudo mkdir -p /var/www/tumorDetection
cd /var/www/tumorDetection

# 克隆代码
git clone <repository-url> .
```

### 2. 后端部署

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 创建启动脚本
cat > start.sh << EOF
#!/bin/bash
source /var/www/tumorDetection/venv/bin/activate
cd /var/www/tumorDetection
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
EOF

chmod +x start.sh
```

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 复制构建文件到Nginx目录
sudo cp -r dist/* /var/www/html/
```

### 4. Nginx配置

```bash
# 创建Nginx配置文件
sudo cat > /etc/nginx/sites-available/tumorDetection << EOF
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/tumorDetection /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 5. Systemd服务配置

```bash
# 创建systemd服务文件
sudo cat > /etc/systemd/system/tumorDetection.service << EOF
[Unit]
Description=Tumor Detection Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tumorDetection
Environment="PATH=/var/www/tumorDetection/venv/bin"
ExecStart=/var/www/tumorDetection/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl enable tumorDetection
sudo systemctl start tumorDetection
```

## Docker部署

### Dockerfile (后端)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
```

### Dockerfile (前端)

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend/models:/app/models
    environment:
      - FLASK_ENV=production

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

## SSL证书配置

### 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 监控和日志

### 应用日志

```bash
# 查看应用日志
sudo journalctl -u tumorDetection -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 健康检查

```bash
# 添加健康检查端点
curl http://localhost/api/health
```

### 监控工具

- **Prometheus**: 指标收集
- **Grafana**: 可视化仪表板
- **ELK Stack**: 日志聚合

## 备份策略

### 数据库备份 (如果使用)

```bash
# 每日备份
0 2 * * * pg_dump -U username -h localhost dbname > /backup/db_$(date +\%Y\%m\%d).sql
```

### 文件备份

```bash
# 备份模型文件和配置
0 3 * * * tar -czf /backup/models_$(date +\%Y\%m\%d).tar.gz /var/www/tumorDetection/models/
```

## 性能优化

### Nginx优化

```nginx
# 在nginx.conf中添加
worker_processes auto;
worker_connections 1024;

# 启用gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### Flask优化

```python
# 使用Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent main:app
```

### 缓存配置

- 使用Redis缓存API响应
- 配置浏览器缓存静态资源
- 实现CDN加速

## 安全加固

### 防火墙配置

```bash
# UFW配置
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 定期更新

```bash
# 自动更新
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### 入侵检测

- 安装fail2ban
- 配置SSH密钥认证
- 禁用root远程登录

## 故障排除

### 常见问题

**问题**: 502 Bad Gateway
**解决**: 检查Flask应用是否运行，检查Nginx配置

**问题**: 内存不足
**解决**: 增加服务器内存或优化应用

**问题**: 模型加载失败
**解决**: 检查模型文件权限和路径

### 调试命令

```bash
# 检查端口占用
sudo netstat -tlnp | grep :5000

# 检查服务状态
sudo systemctl status tumorDetection

# 检查磁盘使用
df -h
```

## 扩展部署

### 负载均衡

使用Nginx或HAProxy进行负载均衡。

### 容器化

使用Kubernetes进行容器编排。

### 云部署

- AWS EC2/EB
- Google Cloud Run
- Azure App Service

## 维护计划

- 每日备份检查
- 每周安全更新
- 每月性能监控
- 每季度依赖更新