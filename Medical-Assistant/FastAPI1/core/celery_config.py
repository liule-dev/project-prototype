"""
Celery 配置和初始化
"""
import sys
import os
# 确保项目根目录在 Python 路径中，以便 Celery 能找到 tasks 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⚠️ 在导入 settings 之前先设置 Hugging Face 环境变量
from core import settings

# ⚠️ 为 Celery Worker 强制设置 Hugging Face 离线模式环境变量
cache_dir = os.path.abspath(settings.TRANSFORMERS_CACHE)
os.environ['HF_HOME'] = cache_dir
os.environ['HUGGINGFACE_HUB_CACHE'] = cache_dir
os.environ['HF_ENDPOINT'] = settings.HF_ENDPOINT
os.environ['HF_HUB_OFFLINE'] = '1'  # ✅ 关键：启用离线模式
os.environ['TRANSFORMERS_OFFLINE'] = '1'

print(f"🔧 [Celery] HF_HOME: {os.environ.get('HF_HOME')}")
print(f"🔧 [Celery] HF_HUB_OFFLINE: {os.environ.get('HF_HUB_OFFLINE')}")

from celery import Celery
import logging

logger = logging.getLogger(__name__)
# 创建 Celery 应用实例，指定应用名称为 'medical_assistant'
celery_app = Celery(
    'medical_assistant',
    # 设置消息代理（Broker）地址，使用 Redis 数据库 1
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1',
    # 设置结果后端（Backend）地址，使用 Redis 数据库 2
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/2',
)

# 更新 Celery 应用的配置参数
celery_app.conf.update(
    # --- 任务序列化配置 ---
    # 指定任务序列化为 JSON 格式
    task_serializer='json',
    # 允许接收的内容类型为 JSON
    accept_content=['json'],
    # 指定结果序列化为 JSON 格式
    result_serializer='json',
    
    # --- 时区设置 ---
    # 设置时区为上海时间
    timezone='Asia/Shanghai',
    # 启用 UTC 时间支持
    enable_utc=True,
    
    # --- 任务路由配置 ---
    # 将不同模块的任务分配到不同的队列，实现任务隔离
    task_routes={
        # AI 相关任务分配到 'ai_queue' 队列
        'tasks.ai_tasks.*': {'queue': 'ai_queue'},
        # AI 具体任务显式路由
        'ai_tasks.generate_llm_response': {'queue': 'ai_queue'},
        'ai_tasks.extract_image_features': {'queue': 'ai_queue'},
        'ai_tasks.generate_text_embedding': {'queue': 'ai_queue'},
        'ai_tasks.vector_search_documents': {'queue': 'ai_queue'},
        'ai_tasks.vector_search_images': {'queue': 'ai_queue'},
        # 文件处理任务分配到 'file_queue' 队列
        'tasks.file_tasks.*': {'queue': 'file_queue'},
        # 文件具体任务显式路由
        'file_tasks.process_document': {'queue': 'file_queue'},
        'file_tasks.process_image': {'queue': 'file_queue'},
        'file_tasks.upload_to_minio': {'queue': 'file_queue'},
        'file_tasks.batch_upload_images': {'queue': 'file_queue'},
        # 数据处理任务分配到 'data_queue' 队列
        'tasks.data_tasks.*': {'queue': 'data_queue'},
        # 数据具体任务显式路由
        'data_tasks.save_session_message': {'queue': 'data_queue'},
        'data_tasks.update_session_cache': {'queue': 'data_queue'},
        'data_tasks.sync_session_to_db': {'queue': 'data_queue'},
        'data_tasks.log_operation': {'queue': 'data_queue'},
        'data_tasks.cleanup_expired_sessions': {'queue': 'data_queue'},
    },
    
    # --- 并发配置 ---
    # 设置每个 Worker 进程的并发数为 8（提升吞吐量）
    worker_concurrency=8,
    # 设置预取倍数为 2，平衡任务调度效率和公平性
    worker_prefetch_multiplier=2,
    
    # --- 任务超时配置 ---
    # 设置软超时时间为 300 秒（5 分钟），超过此时间会抛出 SoftTimeLimitExceeded 异常
    task_soft_time_limit=300,
    # 设置硬超时时间为 600 秒（10 分钟），超过此时间任务会被强制终止
    task_time_limit=600,
    
    # --- 任务确认与重试配置 ---
    # 启用延迟确认，任务执行完成后才向 Broker 发送确认信号，防止任务丢失
    task_acks_late=True,
    # 当 Worker 丢失时拒绝任务，使任务重新入队以便其他 Worker 执行
    task_reject_on_worker_lost=True,
    
    # --- 结果过期配置 ---
    # 设置任务结果在 backend 中的保留时间为 3600 秒（1 小时）
    result_expires=3600,
    
    # --- 速率限制配置 ---
    # 对特定任务设置执行频率限制，防止系统过载
    task_annotations={
        # 限制 LLM 响应生成任务每分钟最多执行 30 次（提升 3 倍）
        'tasks.ai_tasks.generate_llm_response': {'rate_limit': '30/m'},
        # 限制图像特征提取任务每分钟最多执行 50 次（提升 2.5 倍）
        'tasks.ai_tasks.extract_image_features': {'rate_limit': '50/m'},
    }
)

# 自动发现并注册 'tasks' 包下的所有任务
# 显式指定包名，确保 Celery 能正确找到 tasks 模块
celery_app.autodiscover_tasks(['tasks'], related_name=None)

# 记录 Celery 配置完成的日志信息
logger.info("✅ Celery 配置完成")
