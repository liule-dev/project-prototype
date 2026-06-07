"""  
医疗 AI 助手 - 企业级架构
主入口文件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from core import settings, redis_client, qdrant_client, init_db, engine
from api.routes import upload_router, auth_router
from api.routes import query_async
from api.routes import websocket_async
import logging
import uvicorn
import subprocess
import platform
import time
import socket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def check_port(host: str, port: int) -> bool:
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_service_windows(service_name: str, command: str, port: int) -> bool:
    """Windows 下启动服务"""
    if platform.system() != 'Windows':
        return False
    
    try:
        logger.info(f"🚀 正在启动 {service_name}...")
        subprocess.Popen(
            command,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        # 等待服务启动
        for i in range(10):
            if check_port('localhost', port):
                logger.info(f"✅ {service_name} 启动成功")
                return True
            time.sleep(1)
        logger.warning(f"⚠️ {service_name} 启动超时，请手动检查")
        return False
    except Exception as e:
        logger.error(f"❌ 启动 {service_name} 失败：{e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ========== 启动时执行 ==========
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} 启动中...")
    logger.info("=" * 60)
    
    # 检查并启动 Redis
    if not check_port(settings.REDIS_HOST, settings.REDIS_PORT):
        logger.warning("⚠️ Redis 未运行")
        if platform.system() == 'Windows':
            start_service_windows(
                "Redis",
                "redis-server",
                settings.REDIS_PORT
            )
    
    # 测试 Redis 连接
    try:
        if redis_client.ping():
            logger.info("✅ Redis 连接成功")
        else:
            logger.warning("⚠️ Redis 连接失败，部分缓存功能不可用")
    except Exception as e:
        logger.error(f"❌ Redis 连接失败：{e}")
        logger.warning("请手动启动 Redis: redis-server")
    
    # 检查并启动 Qdrant
    if not check_port(settings.QDRANT_HOST, settings.QDRANT_PORT):
        logger.warning("⚠️ Qdrant 未运行")
        if platform.system() == 'Windows':
            start_service_windows(
                "Qdrant",
                "qdrant",
                settings.QDRANT_PORT
            )
    
    # 连接 Qdrant (带重试机制)
    try:
        qdrant_client.connect()
        logger.info("✅ Qdrant 连接成功")
    except Exception as e:
        logger.error(f"❌ Qdrant 连接失败：{e}")
        logger.warning("请手动启动 Qdrant: qdrant")
    
    # 初始化 MySQL 数据库
    try:
        init_db()
        logger.info("✅ MySQL 数据库连接成功并初始化完成")
    except Exception as e:
        logger.error(f"❌ MySQL 数据库初始化失败：{e}")
        logger.warning("请检查数据库配置及连接状态")
    
    # 检查 Celery Workers
    logger.info("=" * 60)
    logger.info("📋 Celery Workers 状态检查：")
    logger.info("   请确保以下 Celery Workers 已启动：")
    logger.info("   1. AI Queue Worker: celery -A celery_worker:celery_app worker --queues=ai_queue")
    logger.info("   2. File Queue Worker: celery -A celery_worker:celery_app worker --queues=file_queue")
    logger.info("   3. Data Queue Worker: celery -A celery_worker:celery_app worker --queues=data_queue")
    logger.info("   或使用脚本: start_celery_workers.bat")
    
    logger.info("=" * 60)
    logger.info(f"📍 服务地址：http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"📚 API 文档：http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info(f"💐 Flower 监控：http://localhost:5555 (如果已启动)")
    logger.info("=" * 60)
    
    yield
    
    # ========== 关闭时执行 ==========
    logger.info("正在关闭服务...")
    
    # 关闭 MySQL 连接
    engine.dispose()
    logger.info("✅ MySQL 连接池已释放")
    
    # 关闭 Redis 连接
    redis_client.close()
    logger.info("✅ Redis 连接已关闭")
    
    # 关闭 Qdrant 连接
    qdrant_client.close()
    logger.info("✅ Qdrant 连接已关闭")
    
    logger.info("✅ 服务已安全关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="医疗 AI 助手 - 企业级架构",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
)

# 注册路由
app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(query_async.router)  # 注册异步问答路由
app.include_router(websocket_async.router)  # 注册异步 WebSocket 路由


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    redis_status = "connected" if redis_client.ping() else "disconnected"
    
    # 检查 MySQL 连接
    mysql_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        mysql_status = "disconnected"
    
    return {
        "status": "healthy",
        "services": {
            "mysql": mysql_status,
            "redis": redis_status,
            "qdrant": "connected"
        }
    }


if __name__ == "__main__":
    # 开发环境运行
    uvicorn.run(
        app="main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
