# 金融证书AI智能模考平台 - Docker 部署指南

## 📋 目录结构

```
scoring/
├── Dockerfile              # 多阶段构建文件（后端 + 前端）
├── docker-compose.yml      # Docker Compose 编排配置
├── nginx.conf              # Nginx 反向代理配置
├── .env.example            # 环境变量示例文件
├── .dockerignore           # Docker 忽略文件
├── requirements.txt        # Python 依赖
├── manage.py               # Django 管理脚本
├── scoring/                # Django 项目配置
├── management/             # 核心业务模块
├── notebook/               # 错题本模块
├── exam/                   # 考试模块
├── common_ai/              # 统一 AI 服务模块
└── ScoringMangement/       # Vue3 前端项目
```

---

## 🚀 快速开始

### 1️⃣ 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0
- Git（可选，用于克隆代码）

### 2️⃣ 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填写真实配置
vim .env
```

**必须修改的配置**：
```bash
# Django 密钥（生成随机字符串）
DJANGO_SECRET_KEY=your-random-secret-key-here

# 数据库密码
DB_PASSWORD=your-strong-password

# 通义千问 API Key
QWEN_API_KEY=sk-your-real-api-key
```

### 3️⃣ 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4️⃣ 访问应用

- **前端页面**: http://localhost
- **后端 API**: http://localhost:8000/api/
- **Django Admin**: http://localhost/admin/
- **MySQL**: localhost:3310
- **Redis**: localhost:6379

---

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f backend

# 进入容器内部
docker-compose exec backend bash
docker-compose exec mysql mysql -u root -p
```

### 数据库操作

```bash
# 执行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser

# 备份数据库
docker-compose exec mysql mysqldump -u root -p questiondatabase > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p questiondatabase < backup.sql
```

### 构建与更新

```bash
# 重新构建镜像
docker-compose build --no-cache

# 更新代码后重启
docker-compose up -d --build

# 清理未使用的镜像和卷
docker system prune -a
docker volume prune
```

---

## 📊 架构说明

### 服务组成

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| mysql | mysql:8.0 | 3310 | MySQL 数据库 |
| redis | redis:7-alpine | 6379 | Redis 缓存 |
| backend | 自定义（Python 3.11） | 8000 | Django 后端 |
| frontend | 自定义（Nginx） | 80 | Vue3 前端 |

### 网络拓扑

```
客户端 (浏览器)
    ↓
  Nginx (frontend:80)
    ├─→ 静态文件 (/)
    └─→ 反向代理 (/api/ → backend:8000)
              ↓
         Django Backend
              ├─→ MySQL (mysql:3306)
              └─→ Redis (redis:6379)
```

### 数据持久化

使用 Docker Volume 持久化以下数据：
- `mysql_data`: MySQL 数据库文件
- `redis_data`: Redis 持久化数据
- `static_volume`: Django 静态文件
- `media_volume`: 用户上传的媒体文件

---

## ⚙️ 配置说明

### Django 配置适配

在 `scoring/settings.py` 中添加环境变量支持：

```python
import os

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'questiondatabase'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Redis 配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/1",
    }
}

# 通义千问 API
TONGYI_API_KEY = os.environ.get('QWEN_API_KEY', '')
```

### Nginx 配置

已配置：
- ✅ 前端静态文件服务
- ✅ 后端 API 反向代理
- ✅ WebSocket 支持
- ✅ Gzip 压缩
- ✅ 静态资源缓存

---

## 🔐 安全建议

### 生产环境必做

1. **修改默认密码**
   ```bash
   # .env 文件中设置强密码
   DB_PASSWORD=YourStrongPassword123!
   DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
   ```

2. **限制允许的主机**
   ```bash
   DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

3. **启用 HTTPS**
   - 使用 Let's Encrypt 免费证书
   - 配置 Nginx SSL

4. **关闭 DEBUG 模式**
   ```bash
   DJANGO_DEBUG=False
   ```

5. **定期备份数据库**
   ```bash
   # 添加到 crontab
   0 2 * * * docker-compose exec -T mysql mysqldump -u root -p$DB_PASSWORD questiondatabase > /backup/db_$(date +\%Y\%m\%d).sql
   ```

---

## 🐛 故障排查

### 1. 容器启动失败

```bash
# 查看详细日志
docker-compose logs backend

# 检查配置文件
docker-compose config

# 重新构建
docker-compose build --no-cache
```

### 2. 数据库连接失败

```bash
# 检查 MySQL 是否就绪
docker-compose exec mysql mysqladmin ping -h localhost

# 查看 MySQL 日志
docker-compose logs mysql
```

### 3. 前端无法访问后端

```bash
# 检查 Nginx 配置
docker-compose exec frontend nginx -t

# 测试后端连通性
docker-compose exec frontend curl http://backend:8000/api/
```

### 4. 静态文件 404

```bash
# 重新收集静态文件
docker-compose exec backend python manage.py collectstatic --noinput

# 检查权限
docker-compose exec backend ls -la /app/staticfiles/
```

---

## 📈 性能优化

### 1. Gunicorn 调优

```yaml
# docker-compose.yml
command: >
  gunicorn scoring.wsgi:application 
  --bind 0.0.0.0:8000 
  --workers 4 
  --threads 2 
  --timeout 120 
  --keep-alive 5
```

### 2. MySQL 优化

```ini
# my.cnf
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 1G
query_cache_size = 64M
```

### 3. Redis 优化

```bash
# 启用持久化
appendonly yes
save 900 1
save 300 10
save 60 10000
```

---

## 🔄 CI/CD 集成

### GitHub Actions 示例

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and Deploy
        run: |
          docker-compose build
          docker-compose up -d
          docker-compose exec backend python manage.py migrate
          docker-compose restart
```

---

## 📞 技术支持

- **项目文档**: 查看项目根目录 README.md
- **问题反馈**: 提交 Issue
- **API 文档**: http://localhost:8000/api/docs/

---

## 📝 更新日志

### v1.0.0 (2024-01-01)
- ✅ 初始 Docker 支持
- ✅ 多阶段构建优化镜像大小
- ✅ 完整的 docker-compose 编排
- ✅ Nginx 反向代理配置
- ✅ 环境变量管理
