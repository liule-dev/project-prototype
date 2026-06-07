"""
会话服务层：封装数据库会话操作
提供会话历史的持久化存储和查询
"""
from sqlalchemy.orm import Session
from models.schemas import ChatSession, ChatMessage
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """会话数据库服务"""
    
    @staticmethod
    def get_or_create_session(db: Session, user_id: int, session_id: str) -> ChatSession:
        """
        获取或创建会话
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            session_id: 会话标识
            
        Returns:
            ChatSession 对象
        """
        try:
            # 查询是否存在该会话
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                # 创建新会话
                session = ChatSession(
                    user_id=user_id,
                    session_id=session_id,
                    title=f"会话_{datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(session)
                db.commit()
                db.refresh(session)
                logger.info(f"✅ 创建新会话：{session_id}")
            else:
                # 更新会话时间
                session.updated_at = datetime.now()
                db.commit()
                
            return session
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建/获取会话失败：{e}")
            raise
    
    @staticmethod
    def save_message(db: Session, session_id: int, role: str, content: str, 
                    confidence: float = None, specialty: str = None) -> ChatMessage:
        """
        保存聊天消息
        
        Args:
            db: 数据库会话
            session_id: 会话ID（数据库主键）
            role: 角色（user/assistant/system）
            content: 消息内容
            confidence: 置信度
            specialty: 专科分类
            
        Returns:
            ChatMessage 对象
        """
        try:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                confidence=confidence,
                specialty=specialty,
                created_at=datetime.now()
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            logger.debug(f"✅ 保存消息：{role} - {content[:50]}...")
            return message
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存消息失败：{e}")
            raise
    
    @staticmethod
    def get_session_messages(db: Session, session_id: str, limit: int = 40) -> list:
        """
        获取会话的历史消息
        
        Args:
            db: 数据库会话
            session_id: 会话标识
            limit: 返回消息数量限制
            
        Returns:
            消息列表，格式：[{"role": "user", "content": "..."}, ...]
        """
        try:
            # 先查找会话
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                logger.debug(f"⚠️ 会话不存在：{session_id}")
                return None
            
            # 查询消息（按时间排序，取最近 limit 条）
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
            
            # 反转顺序（从旧到新）
            messages.reverse()
            
            # 转换为前端需要的格式（content 统一为纯字符串，防止后续 LLM/压缩工具报错）
            history = []
            for msg in messages:
                history.append({
                    "role": msg.role,
                    "content": msg.content  # 直接使用字符串格式
                })
            
            logger.info(f"✅ 从数据库加载 {len(history)} 条历史消息：{session_id}")
            return history
            
        except Exception as e:
            logger.error(f"获取会话消息失败：{e}")
            return None
    
    @staticmethod
    def update_session_title(db: Session, session_id: int, title: str):
        """更新会话标题"""
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                session.title = title
                session.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"更新会话标题失败：{e}")


# 全局会话服务实例
session_service = SessionService()
