"""
文件处理相关异步任务
包括文档解析、图片处理、MinIO 上传等
"""
from core.celery_config import celery_app
from services.minio_service import minio_service
from core import settings
import logging
import io
import time

logger = logging.getLogger(__name__)


@celery_app.task(name='file_tasks.process_document', bind=True, max_retries=2)
def process_document(self, file_data: bytes, filename: str, file_type: str) -> dict:
    """
    异步处理文档（提取文本、分块）
    
    Args:
        file_data: 文件二进制数据
        filename: 文件名
        file_type: 文件类型 (pdf/docx/txt)
        
    Returns:
        {
            "chunks": list,
            "full_text": str,
            "chunk_count": int
        }
    """
    try:
        logger.info(f"📄 [Task] 开始处理文档：{filename}")
        
        full_text = ""
        
        # 根据文件类型提取文本
        if file_type == 'pdf':
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    full_text += text + "\n"
                    
        elif file_type == 'docx':
            from docx import Document
            doc = Document(io.BytesIO(file_data))
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            
        else:  # txt
            full_text = file_data.decode('utf-8')
        
        # 文本分块
        def split_text_into_chunks(text: str, chunk_size: int = 512, chunk_overlap: int = 50):
            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                if chunk.strip():
                    chunks.append(chunk)
                start += chunk_size - chunk_overlap
            return chunks
        
        chunks = split_text_into_chunks(
            full_text,
            chunk_size=settings.TEXT_CHUNK_SIZE,
            chunk_overlap=settings.TEXT_CHUNK_OVERLAP
        )
        
        logger.info(f"✅ [Task] 文档处理完成：{filename}, 分块数：{len(chunks)}")
        
        return {
            "chunks": chunks,
            "full_text": full_text[:10000],  # 限制长度
            "chunk_count": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 文档处理失败：{e}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=5)
        
        raise


@celery_app.task(name='file_tasks.upload_to_minio', bind=True, max_retries=3)
def upload_to_minio(self, file_data: bytes, bucket_name: str, object_name: str, 
                   content_type: str = None) -> dict:
    """
    异步上传文件到 MinIO
    
    Args:
        file_data: 文件二进制数据
        bucket_name: 存储桶名称
        object_name: 对象名称
        content_type: 内容类型
        
    Returns:
        {
            "bucket": str,
            "object_name": str,
            "url": str
        }
    """
    try:
        logger.info(f"☁️ [Task] 开始上传文件到 MinIO：{object_name}")
        
        # 上传到 MinIO
        minio_service.upload_file_data(
            bucket_name=bucket_name,
            object_name=object_name,
            file_data=file_data,
            content_type=content_type
        )
        
        # 生成访问 URL
        url = f"http://{settings.MINIO_ENDPOINT}/{bucket_name}/{object_name}"
        
        logger.info(f"✅ [Task] 文件上传成功：{object_name}")
        
        return {
            "bucket": bucket_name,
            "object_name": object_name,
            "url": url
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 文件上传失败：{e}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
        raise


@celery_app.task(name='file_tasks.process_image', bind=True)
def process_image(self, image_data: bytes, filename: str) -> dict:
    """
    异步处理图片（格式转换、压缩）
    
    Args:
        image_data: 图片二进制数据
        filename: 文件名
        
    Returns:
        {
            "processed_data": bytes,
            "format": str,
            "size": int
        }
    """
    try:
        from PIL import Image
        
        logger.info(f"🖼️ [Task] 开始处理图片：{filename}")
        
        # 打开图片
        img = Image.open(io.BytesIO(image_data))
        
        # 转换为 RGB（如果需要）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 压缩图片（保持质量 85%）
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG', quality=85, optimize=True)
        processed_data = output_buffer.getvalue()
        
        logger.info(f"✅ [Task] 图片处理完成：{filename}, 大小：{len(processed_data)} bytes")
        
        return {
            "processed_data": processed_data.hex(),  # 转为 hex 字符串以便序列化
            "format": "JPEG",
            "size": len(processed_data),
            "original_size": len(image_data)
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 图片处理失败：{e}")
        raise


@celery_app.task(name='file_tasks.batch_upload_images', bind=True)
def batch_upload_images(self, images: list) -> list:
    """
    批量上传图片到 MinIO
    
    Args:
        images: 图片列表，每个元素为 {
            "data": bytes (hex),
            "filename": str,
            "content_type": str
        }
        
    Returns:
        上传结果列表
    """
    try:
        logger.info(f"📸 [Task] 开始批量上传图片，数量：{len(images)}")
        
        results = []
        
        for img_info in images:
            try:
                # 解码 hex 数据
                image_data = bytes.fromhex(img_info["data"])
                filename = img_info["filename"]
                content_type = img_info.get("content_type", "image/jpeg")
                
                # 生成对象名
                object_name = f"img_{time.time()}_{filename}"
                
                # 上传
                result = upload_to_minio(
                    file_data=image_data,
                    bucket_name=settings.MINIO_BUCKET_NAME1,
                    object_name=object_name,
                    content_type=content_type
                )
                
                results.append({
                    "filename": filename,
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"❌ [Task] 单张图片上传失败：{filename}, 错误：{e}")
                results.append({
                    "filename": filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(f"✅ [Task] 批量上传完成，成功：{sum(1 for r in results if r['status'] == 'success')}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ [Task] 批量上传失败：{e}")
        raise
