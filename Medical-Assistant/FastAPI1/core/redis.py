"""
Redis 客户端封装（单例模式）
提供统一的 Redis 连接管理
"""
import redis
from redis.connection import ConnectionPool
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 客户端单例"""
    
    _instance = None
    _pool = None
    _connected = None  # 连接状态标记
    
    def __new__(cls):
        if cls._instance is None:
            config = {
                'host': settings.REDIS_HOST,
                'port': settings.REDIS_PORT,
                'password': settings.REDIS_PASSWORD or "",
                'db': settings.REDIS_DB,
                'decode_responses': False,
                'socket_connect_timeout': 5,
                'socket_keepalive': True,
                'retry_on_timeout': True,
                'max_connections': 200,
                'health_check_interval': 30,
                'socket_timeout': 5
            }
            cls._pool = ConnectionPool(**config)
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(connection_pool=cls._pool)
            cls._connected = None
                
        return cls._instance
    
    def ping(self) -> bool:
        """测试连接是否可用（延迟连接）"""
        if self._connected is not None:
            return self._connected
        
        try:
            if self.client.ping():
                logger.info("✅ Redis 连接成功")
                self._connected = True
                return True
        except Exception as e:
            logger.warning(f"⚠️ Redis 连接失败：{e}")
            self._connected = False
            return False
        return False
    
    def get(self, key: str):
        """获取缓存值"""
        if not self.ping():
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET 失败 {key}: {e}")
            return None
    
    def setex(self, key: str, ttl: int, value):
        """设置带过期时间的缓存"""
        if not self.ping():
            return
        try:
            self.client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis SETEX 失败 {key}: {e}")
    
    def delete(self, key: str):
        """删除缓存"""
        if not self.ping():
            return
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE 失败 {key}: {e}")
    
    def exists(self, key: str) -> bool:
        """检查 key 是否存在"""
        if not self.ping():
            return False
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 失败 {key}: {e}")
            return False
    
    def close(self):
        """关闭连接池"""
        if self._pool:
            self._pool.disconnect()
            logger.info("✅ Redis 连接池已关闭")

# 全局 Redis 客户端实例
redis_client = RedisClient()
