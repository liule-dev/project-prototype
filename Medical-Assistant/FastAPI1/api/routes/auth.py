"""
用户认证路由
提供注册、登录功能
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core import get_db
from models.schemas import User
from passlib.context import CryptContext
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    password: str
    email: str = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""
    user_id: int
    username: str
    message: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    Args:
        request: 注册请求
        db: 数据库会话
        
    Returns:
        注册结果
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        if request.email:
            existing_email = db.query(User).filter(User.email == request.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        hashed_password = get_password_hash(request.password)
        new_user = User(
            username=request.username,
            email=request.email,
            password_hash=hashed_password,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ 用户注册成功：{request.username}")
        
        return {
            "user_id": new_user.id,
            "username": new_user.username,
            "message": "注册成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 用户注册失败：{e}")
        raise HTTPException(status_code=500, detail=f"注册失败：{str(e)}")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    Args:
        request: 登录请求
        db: 数据库会话
        
    Returns:
        登录结果
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.username == request.username).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 验证密码
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 检查用户是否激活
        if not user.is_active:
            raise HTTPException(status_code=403, detail="账户已被禁用")
        
        logger.info(f"✅ 用户登录成功：{request.username}")
        
        return LoginResponse(
            user_id=user.id,
            username=user.username,
            message="登录成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户登录失败：{e}")
        raise HTTPException(status_code=500, detail=f"登录失败：{str(e)}")
