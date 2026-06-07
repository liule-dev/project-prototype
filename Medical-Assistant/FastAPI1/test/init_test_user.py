"""
初始化测试用户脚本
用于创建默认的测试用户账号
"""
from sqlalchemy.orm import Session
from core import SessionLocal, init_db
from models.schemas import User
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_user():
    """创建测试用户"""
    db = SessionLocal()
    
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == "admin").first()
        
        if existing_user:
            logger.info("✅ 测试用户已存在，跳过创建")
            return
        
        # 创建新用户
        hashed_password = pwd_context.hash("admin123")
        new_user = User(
            username="admin",
            email="admin@medical.com",
            password_hash=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info("✅ 测试用户创建成功！")
        logger.info(f"用户名: admin")
        logger.info(f"密码: admin123")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 创建测试用户失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 创建测试用户
    create_test_user()
    
    logger.info("🎉 初始化完成！")
