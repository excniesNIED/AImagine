# AI Gallery 部署指南

本文档详细说明了如何在生产服务器上部署 AI Gallery 应用。

## 系统要求

- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB RAM
- 至少 10GB 存储空间

## 部署步骤

### 1. 克隆代码

```bash
git clone https://github.com/yourusername/openai-gallery.git
cd openai-gallery
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件，配置以下关键参数：

```env
# 修改为强密码
SECRET_KEY=your-very-strong-secret-key-here

# 配置 Alist
ALIST_URL=https://your-domain.com/alist
ALIST_USERNAME=admin
ALIST_PASSWORD=your-strong-password
ALIST_UPLOAD_PATH=/gallery
```

### 3. 生成 SSL 证书

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt update
sudo apt install certbot

# 生成证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### 4. 创建数据目录

```bash
mkdir -p data/{alist,uploads}
sudo chown -R 1000:1000 data
```

### 5. 启动服务

```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 6. 初始化数据库

```bash
# 进入后端容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 运行数据库迁移
alembic upgrade head

# 初始化管理员账号
python -m app.utils.init_db
```

### 7. 配置 Alist

1. 访问 `https://your-domain.com/alist`
2. 使用配置的账号密码登录
3. 在存储设置中配置你的云存储（如阿里云OSS、腾讯云COS等）
4. 创建 `/gallery` 目录用于存储图片

## 服务管理

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker-compose -f docker-compose.prod.yml up -d --build
```

### 备份数据

```bash
# 备份数据库
sudo cp data/gallery.db data/gallery.db.backup.$(date +%Y%m%d)

# 备份 Alist 数据
sudo tar -czf alist-data-backup.tar.gz data/alist/
```

### 查看日志

```bash
# 所有服务日志
docker-compose -f docker-compose.prod.yml logs

# 特定服务日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs alist
```

## 性能优化

### 1. 配置 Nginx

编辑 `nginx.conf` 优化性能：

```nginx
# 启用 gzip 压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript image/svg+xml;

# 缓存静态文件
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. 优化数据库

```sql
-- 创建索引
CREATE INDEX idx_images_owner_created ON images(owner_id, created_at);
CREATE INDEX idx_images_category ON images(category_id);
CREATE INDEX idx_images_model ON images(model_id);
```

### 3. 配置 CDN

可以将 Nginx 配置为使用 CDN 加速静态资源：

```nginx
location /d/ {
    proxy_pass https://your-cdn-domain.com;
    proxy_set_header Host $host;
}
```

## 故障排除

### 问题 1：无法访问 Alist

检查 Alist 容器状态：

```bash
docker logs aigallery-alist-prod
```

确保 Alist URL 配置正确。

### 问题 2：上传图片失败

1. 检查 Alist 存储配置
2. 确认上传路径存在且有写权限
3. 查看后端日志获取详细错误信息

### 问题 3：内存不足

增加 swap 空间：

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 问题 4：证书过期

续期证书：

```bash
sudo certbot renew
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
docker-compose -f docker-compose.prod.yml restart nginx
```

## 安全建议

1. 定期更新系统和 Docker 镜像
2. 使用强密码
3. 启用防火墙，只开放必要端口
4. 定期备份数据
5. 监控系统资源使用情况

## 监控配置

可以使用以下工具监控服务状态：

```bash
# 安装监控工具
docker run -d \
  --name=cadvisor \
  -p 8080:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:ro \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  gcr.io/cadvisor/cadvisor
```

访问 `http://your-server:8080` 查看容器监控信息。