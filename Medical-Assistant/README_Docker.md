# 医疗助手 Docker 部署说明

## 📋 目录结构

```
Medical-Assistant/
├── docker-compose.yml          # Docker Compose 配置文件
├── nginx.conf                  # Nginx 配置文件
├── .env                        # 环境变量配置
├── FastAPI1/                   # 后端服务
│   ├── Dockerfile              # 后端 Docker 镜像构建文件
│   └── ...
└── MedicalAssistant_vue/       # 前端服务
    ├── Dockerfile              # 前端 Docker 镜像构建文件
    └── ...
```

## 🚀 快速开始

### 1. 前置要求

- Docker Engine 20.10+
- Docker Compose v2.0+

### 2. 配置环境变量

编辑根目录下的 `.env` 文件，修改以下配置：

```bash
# LLM API 密钥（必须）
LLM_API_KEY=your-api-key

# MinIO 访问密钥（建议修改）
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin123456

# MySQL 密码（建议修改）
DB_PASSWORD=123456
```

### 3. 构建并启动服务

```bash
# 在项目根目录执行
docker-compose up -d --build
```

### 4. 访问服务

- **前端应用**: http://localhost
- **API 文档**: http://localhost/docs
- **健康检查**: http://localhost/health
- **Flower 监控**: http://localhost:5555 (用户名: admin, 密码: admin123)
- **MinIO 控制台**: http://localhost:9001 (用户名/密码见 .env 配置)

## 🔧 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi
docker-compose logs -f nginx
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart fastapi
```

### 停止服务
```bash
docker-compose down
```

### 停止并删除数据卷（⚠️ 会清除所有数据）
```bash
docker-compose down -v
```

### 重新构建并启动
```bash
docker-compose up -d --build
```

## 📦 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| nginx | 80, 443 | 反向代理和静态文件服务 |
| fastapi | 8000 | FastAPI 后端服务 |
| redis | 6379 | Redis 缓存和消息队列 |
| mysql | 3310 | MySQL 数据库 |
| minio | 9000, 9001 | MinIO 对象存储及控制台 |
| qdrant | 6333, 6334 | Qdrant 向量数据库 |
| celery-ai | - | AI 任务 Celery Worker |
| celery-file | - | 文件处理 Celery Worker |
| celery-data | - | 数据处理 Celery Worker |
| flower | 5555 | Celery 任务监控面板 |

## 🔐 安全建议

1. **修改默认密码**：务必修改 `.env` 中的默认密码
2. **HTTPS 配置**：生产环境请配置 SSL 证书
3. **防火墙设置**：仅开放必要端口（80, 443）
4. **定期备份**：定期备份 MySQL 和 MinIO 数据

## 🛠️ 故障排查

### 前端无法访问后端 API

检查 Nginx 配置和日志：
```bash
docker-compose logs nginx
```

### 后端服务启动失败

检查后端日志：
```bash
docker-compose logs fastapi
```

### 数据库连接失败

确保 MySQL 服务正常运行：
```bash
docker-compose logs mysql
```

### 查看容器状态
```bash
docker-compose ps
```

## 📝 注意事项

1. **首次启动**可能需要较长时间下载依赖和初始化数据库
2. **模型缓存**：AI 模型会下载到 `FastAPI1/cache` 目录，占用较大空间
3. **数据持久化**：所有数据存储在 Docker volumes 中，不会因容器删除而丢失
4. **资源需求**：建议至少 4GB RAM 和 10GB 磁盘空间

## 🔄 更新部署

```bash
# 拉取最新代码后
git pull
docker-compose up -d --build
```

## 📞 技术支持

如有问题，请查看各服务的日志文件或联系技术支持。
