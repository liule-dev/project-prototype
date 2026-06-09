"""
应用配置管理
所有环境变量通过此文件统一管理
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置（从环境变量加载）"""
    
    # ========== 应用基础配置 ==========
    APP_NAME: str = "医疗 AI 助手"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # ========== Redis 配置 ==========
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    # ========== Qdrant 向量数据库配置 ==========
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_GRPC_PORT: int = int(os.getenv("QDRANT_GRPC_PORT", 6334))
    QDRANT_COLLECTION_NAME: str = "medical_images"
    QDRANT_DOC_COLLECTION_NAME: str = "medical_documents"
    
    # ========== MinIO 对象存储配置 ==========
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = "medical-docs"
    MINIO_BUCKET_NAME1: str = "medical-images"
    MINIO_BUCKET_NAME2: str = "medical-videos"
    
    # ========== LLM 大模型配置 ==========
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # ========== Embedding 模型配置 ==========
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-zh-v1.5"
    EMBEDDING_CACHE_FOLDER: str = "./cache"
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch16"
    
    # ========== Hugging Face 配置 ==========
    HF_ENDPOINT: str = os.getenv("HF_ENDPOINT", "https://hf-mirror.com")
    TRANSFORMERS_CACHE: str = os.getenv("TRANSFORMERS_CACHE", "./cache")
    
    # ========== CORS 跨域配置 ==========
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # ========== 文件上传配置 ==========
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
    MAX_DOC_TEXT_LENGTH: int = int(os.getenv("MAX_DOC_TEXT_LENGTH", "10000"))  # 10000 字
    TEXT_CHUNK_SIZE: int = int(os.getenv("TEXT_CHUNK_SIZE", "512"))
    TEXT_CHUNK_OVERLAP: int = int(os.getenv("TEXT_CHUNK_OVERLAP", "50"))
    
    # ========== 允许的文件类型 ==========
    ALLOWED_FILE_CONTENT_TYPES: dict = {
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "video/mp4": "mp4",
        "video/x-msvideo": "avi",
        "video/quicktime": "mov",
        "video/webm": "webm"
    }
    
    # ========== MinIO 分片大小（字节） ==========
    MINIO_PART_SIZE: int = int(os.getenv("MINIO_PART_SIZE", "10485760"))  # 10MB
    
    # ========== 数据库配置 (MySQL) ==========
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3310"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "123456")
    DB_NAME: str = os.getenv("DB_NAME", "medical_assistant")

    # BM25 检索配置
    BM25_ENABLED: bool = True
    BM25_K1: float = 1.5  # BM25 参数 k1
    BM25_B: float = 0.75  # BM25 参数 b
    HYBRID_SEARCH_ALPHA: float = 0.7  # 混合检索向量权重

    # GPU 配置
    USE_GPU: bool = os.getenv("USE_GPU", "true").lower() == "true"
    CUDA_DEVICE: str = os.getenv("CUDA_DEVICE", "cuda:0")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def DATABASE_URL(self) -> str:
        """构建 SQLAlchemy 风格的数据库 URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# 全局配置实例
settings = Settings()
