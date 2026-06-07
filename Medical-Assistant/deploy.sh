#!/bin/bash

# 医疗助手一键部署脚本 (Linux)
# 使用前请确保已安装 Docker 和 NVIDIA Container Toolkit

set -e

echo "========================================="
echo "  医疗助手 Docker 一键部署脚本"
echo "========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose v2+"
    exit 1
fi

# 检查 NVIDIA Container Toolkit
if ! docker info | grep -i "nvidia" &> /dev/null; then
    echo "⚠️  警告: 未检测到 NVIDIA Container Toolkit"
    echo "   如果需要 GPU 加速，请安装 NVIDIA Container Toolkit"
    echo "   参考: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在"
    echo "   请复制 .env.example 并修改配置"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p FastAPI1/cache
mkdir -p MedicalAssistant_vue/dist

# 构建前端（如果尚未构建）
if [ ! -d "MedicalAssistant_vue/dist" ] || [ -z "$(ls -A MedicalAssistant_vue/dist)" ]; then
    echo "🔨 构建前端应用..."
    cd MedicalAssistant_vue
    if command -v npm &> /dev/null; then
        npm install
        npm run build
    else
        echo "⚠️  Node.js/npm 未安装，使用 Docker 构建前端"
        cd ..
        docker build -t medical-frontend ./MedicalAssistant_vue
        # 从容器复制构建产物
        docker run --rm -v $(pwd)/MedicalAssistant_vue/dist:/output medical-frontend cp -r /usr/share/nginx/html/. /output/
    fi
    cd ..
fi

echo ""
echo "🚀 启动 Docker 服务..."
echo ""

# 停止并删除旧容器
docker compose down

# 构建并启动所有服务
docker compose up -d --build

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 服务状态："
docker compose ps

echo ""
echo "========================================="
echo "  访问地址："
echo "========================================="
echo "  🌐 前端应用: http://localhost"
echo "  📚 API 文档: http://localhost/docs"
echo "  💚 健康检查: http://localhost/health"
echo "  🌸 Flower 监控: http://localhost:5555 (admin/admin123)"
echo "  📦 MinIO 控制台: http://localhost:9001"
echo ""
echo "========================================="
echo "  常用命令："
echo "========================================="
echo "  查看日志: docker compose logs -f"
echo "  重启服务: docker compose restart"
echo "  停止服务: docker compose down"
echo "  更新部署: git pull && docker compose up -d --build"
echo ""
echo "💡 提示: 首次启动可能需要较长时间下载模型和初始化数据库"
echo ""
