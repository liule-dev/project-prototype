# Linux 一键部署指南

## 🚀 快速开始

### 1. 前置要求

确保你的 Linux 服务器已安装：

- **Docker** 20.10+
- **Docker Compose** v2.0+
- **NVIDIA Container Toolkit**（如果需要 GPU 加速）

### 2. 安装 NVIDIA Container Toolkit（GPU 加速必需）

```bash
# 添加 NVIDIA 包仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装 NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker 使用 NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 验证安装
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 3. 一键部署

```bash
# 克隆项目（如果还没有）
git clone <your-repo-url>
cd Medical-Assistant

# 给脚本执行权限
chmod +x deploy.sh

# 修改 .env 配置文件
cp .env.example .env
vim .env  # 修改必要的配置，特别是 LLM_API_KEY

# 运行一键部署脚本
./deploy.sh
```

## 📋 手动部署步骤

如果不想使用一键脚本，可以手动执行：

### 1. 配置环境变量

```bash
cp .env.example .env
vim .env
```

必须修改的配置：
```bash
LLM_API_KEY=your-api-key-here
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=your-strong-password
DB_PASSWORD=your-strong-password
```

### 2. 构建前端

```bash
cd MedicalAssistant_vue
npm install
npm run build
cd ..
```

### 3. 启动服务

```bash
docker compose up -d --build
```

### 4. 查看日志

```bash
docker compose logs -f
```

## 🔧 常见问题

### Q1: 提示 "permission denied"

```bash
# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### Q2: GPU 不可用

```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# 重启 Docker
sudo systemctl restart docker
```

### Q3: 端口被占用

修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8080:80"  # 将 80 改为 8080
```

### Q4: 内存不足

编辑 `docker-compose.yml`，限制容器内存：
```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

### Q5: 模型下载慢

在 `FastAPI1/Dockerfile` 中已配置清华镜像源，如果仍然慢，可以：

```bash
# 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com
```

或在 `.env` 中添加：
```bash
HF_ENDPOINT=https://hf-mirror.com
```

## 📊 监控和维护

### 查看服务状态

```bash
docker compose ps
```

### 查看资源使用

```bash
docker stats
```

### 查看日志

```bash
# 所有服务
docker compose logs -f

# 特定服务
docker compose logs -f fastapi
docker compose logs -f nginx
```

### 重启服务

```bash
docker compose restart
```

### 更新部署

```bash
git pull
docker compose up -d --build
```

### 清理无用资源

```bash
# 清理停止的容器
docker compose down

# 清理未使用的镜像
docker image prune -a

# 清理卷（⚠️ 会删除所有数据）
docker compose down -v
```

## 🔐 安全建议

1. **修改默认密码**：务必修改 `.env` 中的所有默认密码
2. **配置防火墙**：
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
3. **配置 HTTPS**：使用 Let's Encrypt 免费证书
4. **定期备份**：
   ```bash
   # 备份 MySQL
   docker exec mysql-medical mysqldump -u root -p123456 medical_assistant > backup.sql
   
   # 备份 MinIO 数据
   docker cp minio-medical:/data ./minio-backup
   ```

## 📝 服务架构

```
┌─────────────┐
│   Nginx     │ :80 (前端 + API 代理)
└──────┬──────┘
       │
       ├─→ FastAPI (:8000) ─→ Redis, MySQL, MinIO, Qdrant
       │                      ─→ Celery Workers (GPU)
       │
       └─→ Static Files (Vue dist)
```

## 💡 性能优化

### 1. 调整 Worker 数量

编辑 `docker-compose.yml`：
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8
```

### 2. 增加 Celery 并发

```yaml
command: celery -A celery_worker:celery_app worker --concurrency=4
```

### 3. 配置 Nginx 缓存

已在 `nginx.conf` 中配置静态资源缓存。

## 🆘 获取帮助

查看详细文档：[README_Docker.md](README_Docker.md)

查看实时日志：
```bash
docker compose logs -f --tail=100
```
