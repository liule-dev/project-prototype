"""
核心模块导出
统一管理配置、数据库连接及外部服务客户端
"""

# 1. 环境变量与配置
from core.config import settings, Settings

# 2. MySQL 数据库引擎与会话
from core.database import engine, SessionLocal, Base, init_db, get_db

# 3. Redis 客户端
from core.redis import redis_client, RedisClient

# 4. Qdrant 向量数据库客户端
from core.qdrant import qdrant_client, QdrantDatabaseClient

# 5. 缓存相关常量
CACHE_TTL = {
    'CLIP_VECTOR': 86400,      # 24 小时 - CLIP 文本/图片向量
    'MINIO_URL': 300,          # 5 分钟 - MinIO 临时访问链接
    'LLM_ANSWER': 86400,        # 1 小时 - 大模型回答（节省成本）
    'SESSION_HISTORY': 7200,   # 2 小时 - 会话历史
    'DOCUMENT_TEXT': 86400,    # 24 小时 - 文档文本内容
}

REDIS_KEY_PREFIX = {
    'CLIP_TEXT': 'clip:text',
    'CLIP_IMAGE': 'clip:image',
    'MINIO_URL': 'minio:url',
    'LLM_ANSWER': 'llm:answer',
    'SESSION': 'session',
    'HISTORY': 'history'
}
