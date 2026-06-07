"""
MinIO 对象存储服务层
提供文件上传、下载、临时链接生成等接口
"""
from minio import Minio
from core import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class MinIOService:
    """MinIO 对象存储服务"""
    
    def __init__(self):
        """初始化 MinIO 客户端"""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._init_buckets()
    
    def _init_buckets(self):
        """初始化存储桶"""
        buckets = [
            settings.MINIO_BUCKET_NAME,   # 文档
            settings.MINIO_BUCKET_NAME1,  # 图片
            settings.MINIO_BUCKET_NAME2   # 视频
        ]
        
        for bucket_name in buckets:
            if not self.client.bucket_exists(bucket_name):
                try:
                    self.client.make_bucket(bucket_name)
                    logger.info(f"✅ 创建 MinIO 存储桶：{bucket_name}")
                except Exception as e:
                    logger.error(f"创建存储桶 {bucket_name} 失败：{e}")
    
    # ========== 文件上传 ==========
    
    def upload_file(self, bucket_name: str, object_name: str, file_path: str, content_type: str = None):
        """
        上传文件到 MinIO
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（文件路径）
            file_path: 本地文件路径
            content_type: 文件类型
        """
        try:
            self.client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )
            logger.info(f"✅ 文件上传成功：{object_name}")
            return True
        except Exception as e:
            logger.error(f"上传文件失败：{e}")
            raise
    
    def upload_file_data(self, bucket_name: str, object_name: str, file_data: bytes, content_type: str = None):
        """
        上传文件数据到 MinIO（从内存）
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
            file_data: 文件数据（bytes）
            content_type: 文件类型
        """
        try:
            from io import BytesIO
            
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            logger.info(f"✅ 文件数据上传成功：{object_name}")
            return True
        except Exception as e:
            logger.error(f"上传文件数据失败：{e}")
            raise
    
    # ========== 文件下载 ==========
    
    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        从 MinIO 下载文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
            file_path: 本地保存路径
        """
        try:
            self.client.fget_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path
            )
            logger.info(f"✅ 文件下载成功：{object_name}")
        except Exception as e:
            logger.error(f"下载文件失败：{e}")
            raise
    
    def get_file_data(self, bucket_name: str, object_name: str) -> bytes:
        """
        获取文件数据（从内存）
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
            
        Returns:
            文件数据（bytes）
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            file_data = response.read()
            response.close()
            response.release_conn()
            logger.debug(f"✅ 获取文件数据成功：{object_name}")
            return file_data
        except Exception as e:
            logger.error(f"获取文件数据失败：{e}")
            raise
    
    # ========== 临时链接 ==========
    
    def generate_presigned_url(self, object_name: str, bucket_name: str = None, expires: timedelta = timedelta(hours=1)) -> str:
        """
        生成临时访问链接
        
        Args:
            object_name: 对象名称
            bucket_name: 存储桶名称（可选，默认使用图片存储桶）
            expires: 过期时间
            
        Returns:
            临时访问链接
        """
        try:
            if bucket_name is None:
                bucket_name = settings.MINIO_BUCKET_NAME1
            
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )
            logger.debug(f"✅ 生成临时链接：{object_name}")
            return url
        except Exception as e:
            logger.error(f"生成临时链接失败：{e}")
            raise
    
    # ========== 文件删除 ==========
    
    def delete_file(self, bucket_name: str, object_name: str):
        """删除文件"""
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"✅ 文件已删除：{object_name}")
        except Exception as e:
            logger.error(f"删除文件失败：{e}")
            raise
    
    def delete_files(self, bucket_name: str, object_names: list):
        """批量删除文件"""
        try:
            errors = self.client.remove_objects(bucket_name, object_names)
            for error in errors:
                logger.error(f"删除文件失败：{error}")
            logger.info(f"✅ 批量删除 {len(object_names)} 个文件成功")
        except Exception as e:
            logger.error(f"批量删除文件失败：{e}")
            raise
    
    # ========== 存储桶管理 ==========
    
    def list_buckets(self) -> list:
        """列出所有存储桶"""
        try:
            buckets = self.client.list_buckets()
            return [bucket.name for bucket in buckets]
        except Exception as e:
            logger.error(f"列出存储桶失败：{e}")
            return []
    
    def list_objects(self, bucket_name: str, prefix: str = "") -> list:
        """列出存储桶中的对象"""
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except Exception as e:
            logger.error(f"列出对象失败：{e}")
            return []


# 全局 MinIO 服务实例
minio_service = MinIOService()
