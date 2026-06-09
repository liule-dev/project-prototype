FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# 设置环境变量以避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 安装 Python 和系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建符号链接
RUN ln -s /usr/bin/python3.10 /usr/bin/python

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（使用 GPU 版本的 PyTorch）
# 注意：需要在 pip install 时指定 --extra-index-url 来下载 CUDA 版本的 PyTorch
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建缓存目录并设置权限
RUN mkdir -p /app/cache && chmod 755 /app/cache

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令（将在 docker-compose 中覆盖）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
