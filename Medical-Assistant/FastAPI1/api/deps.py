"""
FastAPI 依赖注入
提供认证、权限等通用功能
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    验证访问 Token
    
    Args:
        credentials: HTTP Bearer 凭证
        
    Returns:
        用户 ID 或 Token
        
    Raises:
        HTTPException: 认证失败
    """
    if credentials is None:
        # 开发环境允许无 Token 访问
        logger.warning("⚠️ 未提供认证 Token（开发模式）")
        return "anonymous"
    
    token = credentials.credentials
    
    # TODO: 实现真实的 Token 验证逻辑
    # 这里可以对接 JWT、OAuth2 等认证系统
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )
    
    logger.debug(f"✅ Token 验证通过")
    return token


async def get_current_user(token: str = Depends(verify_token)) -> dict:
    """
    获取当前用户信息
    
    Args:
        token: 访问 Token
        
    Returns:
        用户信息字典
    """
    # TODO: 从数据库或缓存获取用户信息
    # 这里返回示例数据
    return {
        "user_id": "user_123",
        "username": "test_user",
        "token": token
    }


def check_bucket_exists(bucket_name: str) -> str:
    """
    检查 MinIO 存储桶是否存在
    
    Args:
        bucket_name: 存储桶名称
        
    Returns:
        存储桶名称
        
    Raises:
        HTTPException: 存储桶不存在
    """
    # TODO: 实现存储桶检查逻辑
    # 目前直接返回，假设存储桶已存在
    return bucket_name
