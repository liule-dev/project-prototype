"""
数据处理相关异步任务
包括会话存储、缓存更新、日志记录等
"""
from core.celery_config import celery_app
from services.session_service import session_service
from services.cache_service import cache_service
from core import SessionLocal
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='data_tasks.save_session_message', bind=True, max_retries=3)
def save_session_message(self, user_id: int, session_id: str, 
                        role: str, content: str,
                        confidence: float = None, specialty: str = None) -> dict:
    """
    异步保存会话消息到数据库
    
    Args:
        user_id: 用户 ID
        session_id: 会话 ID
        role: 角色 (user/assistant)
        content: 消息内容
        confidence: 置信度（仅 assistant）
        specialty: 科室（仅 assistant）
        
    Returns:
        {
            "status": str,
            "message_id": int
        }
    """
    try:
        logger.info(f"💾 [Task] 开始保存会话消息：{session_id}, 角色：{role}")
        
        db = SessionLocal()
        
        try:
            # 获取或创建会话
            db_session = session_service.get_or_create_session(
                db, user_id, session_id
            )
            
            # 保存消息
            message = session_service.save_message(
                db,
                db_session.id,
                role,
                content,
                confidence=confidence,
                specialty=specialty
            )
            
            logger.info(f"✅ [Task] 会话消息保存成功，ID：{message.id}")
            
            return {
                "status": "success",
                "message_id": message.id
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ [Task] 会话消息保存失败：{e}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(name='data_tasks.update_session_cache', bind=True)
def update_session_cache(self, session_id: str, messages: list) -> dict:
    """
    异步更新会话缓存到 Redis
    
    Args:
        session_id: 会话 ID
        messages: 消息历史列表
        
    Returns:
        {
            "status": str,
            "message_count": int
        }
    """
    try:
        logger.info(f"🔄 [Task] 开始更新会话缓存：{session_id}, 消息数：{len(messages)}")
        
        # 保存到 Redis
        cache_service.save_session_history(session_id, messages)
        
        logger.info(f"✅ [Task] 会话缓存更新成功")
        
        return {
            "status": "success",
            "message_count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 会话缓存更新失败：{e}")
        
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(name='data_tasks.sync_session_to_db', bind=True)
def sync_session_to_db(self, session_id: str, messages: list, user_id: int) -> dict:
    """
    异步同步会话历史到数据库（批量保存）
    
    Args:
        session_id: 会话 ID
        messages: 消息历史列表
        user_id: 用户 ID
        
    Returns:
        {
            "status": str,
            "saved_count": int
        }
    """
    try:
        logger.info(f"📦 [Task] 开始批量同步会话到数据库：{session_id}")
        
        db = SessionLocal()
        saved_count = 0
        
        try:
            # 获取或创建会话
            db_session = session_service.get_or_create_session(
                db, user_id, session_id
            )
            
            # 批量保存消息
            for msg in messages:
                try:
                    role = msg.get("role")
                    content = msg.get("content", "")
                    
                    # 处理 content 格式
                    if isinstance(content, list):
                        text_parts = [
                            item.get("text", "") 
                            for item in content 
                            if item.get("type") == "text"
                        ]
                        content = " ".join(text_parts).strip()
                    
                    if role and content:
                        session_service.save_message(
                            db,
                            db_session.id,
                            role,
                            content
                        )
                        saved_count += 1
                        
                except Exception as msg_err:
                    logger.warning(f"⚠️ 单条消息保存失败：{msg_err}")
                    continue
            
            logger.info(f"✅ [Task] 会话批量同步完成，保存 {saved_count} 条消息")
            
            return {
                "status": "success",
                "saved_count": saved_count
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ [Task] 会话批量同步失败：{e}")
        
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(name='data_tasks.cleanup_expired_sessions', bind=True)
def cleanup_expired_sessions(self, days: int = 30) -> dict:
    """
    异步清理过期会话（定时任务）
    
    Args:
        days: 保留天数
        
    Returns:
        {
            "status": str,
            "deleted_count": int
        }
    """
    try:
        logger.info(f"🧹 [Task] 开始清理过期会话，保留 {days} 天")
        
        # TODO: 实现具体的清理逻辑
        # 这里需要根据实际的数据库模型来实现
        
        deleted_count = 0
        
        logger.info(f"✅ [Task] 过期会话清理完成，删除 {deleted_count} 条")
        
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 过期会话清理失败：{e}")
        
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(name='data_tasks.log_operation', bind=True)
def log_operation(self, user_id: int, operation: str, details: dict = None) -> dict:
    """
    异步记录操作日志
    
    Args:
        user_id: 用户 ID
        operation: 操作类型
        details: 详细信息
        
    Returns:
        {
            "status": str
        }
    """
    try:
        logger.info(f"📝 [Task] 记录操作日志：用户 {user_id}, 操作：{operation}")
        
        # TODO: 实现日志记录逻辑
        # 可以写入数据库、文件或外部日志系统
        
        return {
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 操作日志记录失败：{e}")
        
        return {
            "status": "failed",
            "error": str(e)
        }
