# 多阶段构建 - 后端 Django
FROM python:3.11-slim AS backend

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=scoring.settings

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput || true

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "scoring.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]


# 多阶段构建 - 前端 Vue3
FROM node:18-alpine AS frontend

# 设置工作目录
WORKDIR /frontend

# 复制 package 文件
COPY ScoringMangement/package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY ScoringMangement/ .

# 构建生产版本
RUN npm run build

# 使用 Nginx 提供前端服务
FROM nginx:alpine

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从前端构建阶段复制静态文件
COPY --from=frontend /frontend/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
