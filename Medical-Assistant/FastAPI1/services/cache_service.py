"""
缓存服务层：封装 Redis 操作 + 内存缓存
提供业务级的三级缓存接口（L1内存 + L2 Redis + L3 MySQL）
支持缓存击穿/雪崩防护
"""
import json
import hashlib
import time
import random
import asyncio
import threading
import numpy as np
from typing import Optional, Callable, Any
from core import redis_client, CACHE_TTL, REDIS_KEY_PREFIX
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """业务缓存服务（三级缓存架构）"""
    
    def __init__(self):
        # ========== L1: 内存缓存 ==========
        self._memory_cache = {}  # 内存缓存字典
        self._memory_ttl = {}    # 内存缓存 TTL 管理
        self._cache_lock = threading.Lock()  # 内存缓存锁
        self._max_memory_cache = 1000  # 最大缓存条目数
        
        # 缓存击穿防护：互斥锁字典
        self._locks: dict = {}
        self._locks_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            "l1_hits": 0,        # L1 内存缓存命中
            "l2_hits": 0,        # L2 Redis 缓存命中
            "cache_misses": 0,
            "lock_waits": 0
        }
    
    @staticmethod
    def calculate_md5(text: str) -> str:
        """计算 MD5 哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _cleanup_memory_cache(self):
        """清理过期的内存缓存（保留最近 1000 条）"""
        if len(self._memory_cache) > self._max_memory_cache:
            # 删除最旧的 100 条
            keys_to_remove = list(self._memory_cache.keys())[:100]
            for key in keys_to_remove:
                del self._memory_cache[key]
                self._memory_ttl.pop(key, None)
    
    def _get_from_memory_cache(self, key: str) -> Any:
        """从 L1 内存缓存获取数据"""
        with self._cache_lock:
            if key in self._memory_cache:
                # 检查 TTL
                if time.time() < self._memory_ttl.get(key, 0):
                    self.stats["l1_hits"] += 1
                    return self._memory_cache[key]
                else:
                    # 过期，删除
                    del self._memory_cache[key]
                    self._memory_ttl.pop(key, None)
        return None
    
    def _save_to_memory_cache(self, key: str, value: Any, ttl: int):
        """保存到 L1 内存缓存"""
        with self._cache_lock:
            self._memory_cache[key] = value
            self._memory_ttl[key] = time.time() + ttl
            self._cleanup_memory_cache()
    
    @staticmethod
    def calculate_md5(text: str) -> str:
        """计算 MD5 哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_lock(self, key: str) -> threading.Lock:
        """获取或创建互斥锁（防止缓存击穿）"""
        with self._locks_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            # 清理过多的锁（保留最近 1000 个）
            if len(self._locks) > 1000:
                keys_to_remove = list(self._locks.keys())[:100]
                for k in keys_to_remove:
                    del self._locks[k]
            return self._locks[key]
    
    def _add_jitter(self, ttl: int, jitter_percent: float = 0.2) -> int:
        """
        添加随机抖动，防止缓存雪崩
        Args:
            ttl: 基础 TTL
            jitter_percent: 抖动百分比（默认 20%）
        Returns:
            添加抖动后的 TTL
        """
        jitter = int(ttl * jitter_percent * random.random())
        return ttl + jitter
    
    # ========== CLIP 向量缓存（三级缓存）==========
    
    def get_clip_vector(self, query_text: str) -> np.ndarray | None:
        """获取 CLIP 文本向量缓存（L1 → L2）"""
        cache_key = f"{REDIS_KEY_PREFIX['CLIP_TEXT']}:{self.calculate_md5(query_text)}"
        
        # L1: 内存缓存
        cached = self._get_from_memory_cache(cache_key)
        if cached is not None:
            logger.debug(f"✅ CLIP 向量内存缓存命中：{query_text[:50]}")
            return cached
        
        # L2: Redis 缓存
        try:
            cached = redis_client.get(cache_key)
            if cached:
                vector = np.frombuffer(cached, dtype=np.float32)
                # 回填 L1
                self._save_to_memory_cache(cache_key, vector, CACHE_TTL['CLIP_VECTOR'])
                self.stats["l2_hits"] += 1
                logger.debug(f"✅ CLIP 向量 Redis 缓存命中：{query_text[:50]}")
                return vector
        except Exception as e:
            logger.error(f"获取 CLIP 向量缓存失败：{e}")
        
        self.stats["cache_misses"] += 1
        return None
    
    def save_clip_vector(self, query_text: str, vector: np.ndarray):
        """保存 CLIP 向量到缓存（L1 + L2）"""
        cache_key = f"{REDIS_KEY_PREFIX['CLIP_TEXT']}:{self.calculate_md5(query_text)}"
        
        # L1: 内存缓存
        self._save_to_memory_cache(cache_key, vector, CACHE_TTL['CLIP_VECTOR'])
        
        # L2: Redis 缓存
        try:
            ttl_with_jitter = self._add_jitter(CACHE_TTL['CLIP_VECTOR'])
            redis_client.setex(
                cache_key,
                ttl_with_jitter,
                vector.astype(np.float32).tobytes()
            )
            logger.debug(f"✅ CLIP 向量已缓存（L1+L2）：{query_text[:50]}")
        except Exception as e:
            logger.error(f"保存 CLIP 向量缓存失败：{e}")
    
    # ========== MinIO 临时链接缓存（三级缓存）==========
    
    def get_minio_url(self, object_name: str) -> str | None:
        """获取 MinIO 临时链接缓存（L1 → L2）"""
        cache_key = f"{REDIS_KEY_PREFIX['MINIO_URL']}:{object_name}"
        
        # L1: 内存缓存
        cached = self._get_from_memory_cache(cache_key)
        if cached is not None:
            logger.debug(f"✅ MinIO 链接内存缓存命中：{object_name}")
            return cached
        
        # L2: Redis 缓存
        try:
            cached = redis_client.get(cache_key)
            if cached:
                url = cached.decode('utf-8') if isinstance(cached, bytes) else cached
                # 回填 L1
                self._save_to_memory_cache(cache_key, url, CACHE_TTL['MINIO_URL'])
                self.stats["l2_hits"] += 1
                return url
        except Exception as e:
            logger.error(f"获取 MinIO 链接缓存失败：{e}")
        
        return None
    
    def save_minio_url(self, object_name: str, url: str):
        """保存 MinIO 临时链接（L1 + L2）"""
        cache_key = f"{REDIS_KEY_PREFIX['MINIO_URL']}:{object_name}"
        
        # L1: 内存缓存
        self._save_to_memory_cache(cache_key, url, CACHE_TTL['MINIO_URL'])
        
        # L2: Redis 缓存
        try:
            ttl_with_jitter = self._add_jitter(CACHE_TTL['MINIO_URL'])
            redis_client.setex(cache_key, ttl_with_jitter, url)
            logger.debug(f"✅ MinIO 链接已缓存（L1+L2）：{object_name}")
        except Exception as e:
            logger.error(f"保存 MinIO 链接缓存失败：{e}")
    
    # ========== LLM 回答缓存（三级缓存）==========
    
    def get_llm_answer(self, question: str) -> str | None:
        """
        获取 LLM 回答缓存（L1 → L2，带击穿防护）
        """
        cache_key = f"{REDIS_KEY_PREFIX['LLM_ANSWER']}:{self.calculate_md5(question)}"
        
        # L1: 内存缓存⭐ 关键优化
        cached = self._get_from_memory_cache(cache_key)
        if cached is not None:
            logger.info(f"✅ LLM 回答内存缓存命中")
            self.stats["l1_hits"] += 1
            return cached
        
        # L2: Redis 缓存
        try:
            cached = redis_client.get(cache_key)
            if cached:
                answer = cached.decode('utf-8') if isinstance(cached, bytes) else cached
                # 回填 L1
                self._save_to_memory_cache(cache_key, answer, CACHE_TTL['LLM_ANSWER'])
                self.stats["l2_hits"] += 1
                logger.info(f"✅ LLM 回答 Redis 缓存命中")
                return answer
        except Exception as e:
            logger.error(f"获取 LLM 回答缓存失败：{e}")
        
        self.stats["cache_misses"] += 1
        return None
    
    def get_llm_answer_with_protection(self, question: str, fetch_func: Callable) -> str:
        """
        带击穿防护的 LLM 回答获取（三级缓存）
        
        Args:
            question: 用户问题
            fetch_func: 缓存未命中时的数据获取函数（同步）
            
        Returns:
            LLM 回答
            
        使用互斥锁确保同一问题只有一个请求执行 fetch_func
        """
        cache_key = f"{REDIS_KEY_PREFIX['LLM_ANSWER']}:{self.calculate_md5(question)}"
        
        # L1: 内存缓存
        cached = self._get_from_memory_cache(cache_key)
        if cached is not None:
            self.stats["l1_hits"] += 1
            return cached
        
        # L2: Redis 缓存（无锁，快速路径）
        try:
            cached = redis_client.get(cache_key)
            if cached:
                answer = cached.decode('utf-8') if isinstance(cached, bytes) else cached
                # 回填 L1
                self._save_to_memory_cache(cache_key, answer, CACHE_TTL['LLM_ANSWER'])
                self.stats["l2_hits"] += 1
                return answer
        except Exception as e:
            logger.error(f"获取 LLM 回答缓存失败：{e}")
        
        # 缓存未命中，使用互斥锁
        lock = self._get_lock(cache_key)
        
        with lock:
            # 双重检查：获取锁后再次检查缓存
            cached = self._get_from_memory_cache(cache_key)
            if cached is not None:
                return cached
            
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    answer = cached.decode('utf-8') if isinstance(cached, bytes) else cached
                    self._save_to_memory_cache(cache_key, answer, CACHE_TTL['LLM_ANSWER'])
                    return answer
            except Exception as e:
                logger.error(f"双重检查缓存失败：{e}")
            
            # 真正执行数据获取
            self.stats["lock_waits"] += 1
            logger.info(f"🔒 缓存未命中，执行 LLM 查询（互斥锁保护）：{question[:50]}")
            
            try:
                answer = fetch_func()
                
                if answer:
                    # 同时保存到 L1 和 L2
                    ttl_with_jitter = self._add_jitter(CACHE_TTL['LLM_ANSWER'])
                    self._save_to_memory_cache(cache_key, answer, ttl_with_jitter)
                    redis_client.setex(cache_key, ttl_with_jitter, answer)
                    logger.info(f"✅ LLM 回答已缓存（L1+L2），TTL={ttl_with_jitter}s")
                
                return answer
                
            except Exception as e:
                logger.error(f"❌ LLM 查询失败：{e}")
                raise
            finally:
                # 清理锁（避免内存泄漏）
                with self._locks_lock:
                    if cache_key in self._locks:
                        del self._locks[cache_key]
    
    def save_llm_answer(self, question: str, answer: str):
        """
        保存 LLM 回答（L1 + L2，同一问题出现 3 次才持久化，带随机抖动防雪崩）
        
        Args:
            question: 用户问题
            answer: LLM 回答
        """
        try:
            cache_key = f"{REDIS_KEY_PREFIX['LLM_ANSWER']}:{self.calculate_md5(question)}"
            count_key = f"{cache_key}:count"  # 计数器 key
            
            # L1: 立即写入内存缓存（无需等待 3 次）
            self._save_to_memory_cache(cache_key, answer, CACHE_TTL['LLM_ANSWER'])
            
            # L2: Redis 计数逻辑（保持原有策略）
            current_count = redis_client.get(count_key)
            count = int(current_count) if current_count else 0
            
            # 计数 +1
            new_count = count + 1
            
            if new_count >= 3:
                # 达到 3 次，缓存答案并删除计数器
                ttl_with_jitter = self._add_jitter(CACHE_TTL['LLM_ANSWER'])
                redis_client.setex(cache_key, ttl_with_jitter, answer)
                redis_client.delete(count_key)
                logger.info(f"✅ LLM 回答已缓存（L1+L2，问题出现 {new_count} 次），TTL={ttl_with_jitter}s")
            else:
                # 未达到 3 次，只更新计数器（设置过期时间避免永久累积）
                redis_client.setex(count_key, 3600 * 24, str(new_count))
                logger.info(f"⏳ 问题出现第 {new_count} 次，L1已缓存，L2待达到3次")
        except Exception as e:
            logger.error(f"保存 LLM 回答缓存失败：{e}")
    
    # ========== 会话历史缓存（三级缓存）==========
    
    def get_session_history(self, session_id: str) -> list | None:
        """获取会话历史（L1 → L2）"""
        cache_key = f"{REDIS_KEY_PREFIX['HISTORY']}:{session_id}"
        
        # L1: 内存缓存
        cached = self._get_from_memory_cache(cache_key)
        if cached is not None:
            logger.debug(f"✅ 会话历史内存缓存命中：{session_id}")
            return cached
        
        # L2: Redis 缓存
        try:
            cached = redis_client.get(cache_key)
            if cached:
                if isinstance(cached, bytes):
                    cached = cached.decode('utf-8')
                history = json.loads(cached)
                # 回填 L1
                self._save_to_memory_cache(cache_key, history, CACHE_TTL['SESSION_HISTORY'])
                self.stats["l2_hits"] += 1
                logger.debug(f"✅ 会话历史 Redis 缓存命中：{session_id}")
                return history
        except Exception as e:
            logger.error(f"获取会话历史失败：{e}")
        
        return None
    
    def save_session_history(self, session_id: str, history: list):
        """保存会话历史（L1 + L2，带随机抖动防雪崩）"""
        cache_key = f"{REDIS_KEY_PREFIX['HISTORY']}:{session_id}"
        
        # 只保留最近 40 条对话
        recent_history = history[-40:]
        
        # L1: 内存缓存
        self._save_to_memory_cache(cache_key, recent_history, CACHE_TTL['SESSION_HISTORY'])
        
        # L2: Redis 缓存
        try:
            ttl_with_jitter = self._add_jitter(CACHE_TTL['SESSION_HISTORY'])
            redis_client.setex(
                cache_key,
                ttl_with_jitter,
                json.dumps(recent_history, ensure_ascii=False)
            )
            logger.debug(f"✅ 会话历史已保存（L1+L2）：{session_id}, TTL={ttl_with_jitter}s")
        except Exception as e:
            logger.error(f"保存会话历史失败：{e}")
    
    # ========== 通用缓存方法 ==========
    
    @staticmethod
    def delete_cache(prefix: str, key: str):
        """删除指定缓存"""
        try:
            cache_key = f"{prefix}:{key}"
            redis_client.delete(cache_key)
            logger.debug(f"✅ 缓存已删除：{cache_key}")
        except Exception as e:
            logger.error(f"删除缓存失败：{e}")
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        total_requests = self.stats["l1_hits"] + self.stats["l2_hits"] + self.stats["cache_misses"]
        l1_hit_rate = (self.stats["l1_hits"] / total_requests * 100) if total_requests > 0 else 0
        l2_hit_rate = (self.stats["l2_hits"] / total_requests * 100) if total_requests > 0 else 0
        total_hit_rate = ((self.stats["l1_hits"] + self.stats["l2_hits"]) / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "l1_hits": self.stats["l1_hits"],
            "l2_hits": self.stats["l2_hits"],
            "misses": self.stats["cache_misses"],
            "lock_waits": self.stats["lock_waits"],
            "l1_hit_rate": f"{l1_hit_rate:.2f}%",
            "l2_hit_rate": f"{l2_hit_rate:.2f}%",
            "total_hit_rate": f"{total_hit_rate:.2f}%",
            "total_requests": total_requests,
            "memory_cache_size": len(self._memory_cache)
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "cache_misses": 0,
            "lock_waits": 0
        }
        logger.info("📊 缓存统计已重置")


# 全局缓存服务实例
cache_service = CacheService()
