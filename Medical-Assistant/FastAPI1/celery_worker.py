"""
Celery Worker 启动入口
"""
from core.celery_config import celery_app

if __name__ == '__main__':
    # 启动 Celery Worker
    celery_app.start()
