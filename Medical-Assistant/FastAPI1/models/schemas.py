"""
数据模型定义
包含医疗助手系统所需的数据库表结构
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 关系
    sessions = relationship("ChatSession", back_populates="user")


class ChatSession(Base):
    """会话表"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, comment="会话ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    session_id = Column(String(100), unique=True, nullable=False, index=True, comment="会话标识")
    title = Column(String(200), nullable=True, comment="会话标题")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, comment="消息ID")
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色：user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    confidence = Column(Float, nullable=True, comment="置信度")
    specialty = Column(String(50), nullable=True, comment="专科分类")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    session = relationship("ChatSession", back_populates="messages")


class Document(Base):
    """文档表"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    filename = Column(String(200), nullable=False, comment="文件名")
    file_type = Column(String(20), nullable=False, comment="文件类型：pdf/doc/docx")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    domain = Column(String(50), nullable=True, comment="科室分类")
    upload_time = Column(DateTime, default=datetime.now, comment="上传时间")
    status = Column(String(20), default="uploaded", comment="状态：uploaded/processed/error")
    text_length = Column(Integer, nullable=True, comment="文本长度")

    __table_args__ = {
        'comment': '医疗文档信息表'
    }
