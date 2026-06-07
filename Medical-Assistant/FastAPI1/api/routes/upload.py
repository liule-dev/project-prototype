"""
文件上传接口
支持医疗文档、影像图片、视频上传
"""
import os

# 设置 HuggingFace 国内镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = './cache'

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from core import settings
from services.minio_service import minio_service
from services.vector_service import vector_service
from agents.clip_extractor import clip_feature_extractor
from sentence_transformers import SentenceTransformer
import asyncio
import tempfile
import os
import logging
from PIL import Image
import io
import numpy as np
from docx import Document
import PyPDF2
from services.bm25_service import bm25_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["文件上传"])

# 初始化 Embedding 模型（使用本地缓存）
embed_model = SentenceTransformer(
    settings.EMBEDDING_MODEL_NAME,
    cache_folder=settings.EMBEDDING_CACHE_FOLDER,
    local_files_only=True  # 强制使用本地缓存的模型
)


@router.post("/medical-docs/")
async def upload_medical_docs(file: UploadFile = File(...)):
    """
    上传医疗文档（PDF/Word）
    
    Args:
        file: 文档文件
        
    Returns:
        上传结果
    """
    try:
        logger.info(f"📄 开始上传文档：{file.filename}")
        
        # 验证文件类型
        if file.content_type not in settings.ALLOWED_FILE_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型：{file.content_type}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)
        
        # 生成文件名
        import time
        file_name = f"doc_{time.time()}_{file.filename}"
        
        # 上传到 MinIO
        await file.seek(0)
        minio_service.upload_file_data(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_name,
            file_data=file_content,
            content_type=file.content_type
        )
        
        # 文本提取和向量化
        try:
            # 读取文件内容
            await file.seek(0)
            file_content = await file.read()
            
            # 提取文本
            full_text = ""
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext == '.docx':
                doc = Document(io.BytesIO(file_content))
                full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif file_ext == '.pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                full_text = ""
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        full_text += text + "\n"
            else:
                full_text = file_content.decode('utf-8')
            
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
            
            chunked_docs = split_text_into_chunks(
                full_text,
                chunk_size=settings.TEXT_CHUNK_SIZE,
                chunk_overlap=settings.TEXT_CHUNK_OVERLAP
            )
            
            # 向量化并存储
            added_count = 0
            
            # 根据文件名自动识别科室分类
            domain_map = {
                '呼吸道': '内科',
                '心血管': '内科',
                '消化': '内科',
                '神经': '内科',
                '内分泌': '内科',
                '呼吸': '内科',
                '循环': '内科',
                '外科': '外科',
                '骨科': '外科',
                '泌尿': '外科',
                '妇产': '妇产科',
                '儿科': '儿科',
                '肿瘤': '肿瘤科',
                '皮肤': '皮肤科',
                '眼科': '眼科',
                '口腔': '口腔科'
            }
            
            # 默认 domain
            detected_domain = '医疗'
            file_name_lower = file.filename.lower()
            for keyword, domain in domain_map.items():
                if keyword.lower() in file_name_lower:
                    detected_domain = domain
                    logger.info(f"📋 检测到科室分类：{detected_domain} (基于关键词：{keyword})")
                    break

            for i, chunk in enumerate(chunked_docs):
                try:
                    # 生成文本向量
                    text_vector = embed_model.encode(chunk, convert_to_numpy=True)
                    text_vector = np.array(text_vector, dtype=np.float32)

                    # 验证向量维度
                    if text_vector.ndim == 1 and len(text_vector) == 512:
                        # 生成唯一的 doc_id
                        doc_id = f"{file_name}_chunk_{i}"
                        metadata = {
                            "type": "medical_document",
                            "content": chunk[:2000],
                            "minio_path": f"{settings.MINIO_BUCKET_NAME}/{file_name}",
                            "original_file_name": file.filename,
                            "domain": detected_domain,
                            "file_type": file_ext,
                            "chunk_index": i,
                            "upload_time": str(asyncio.get_event_loop().time()),
                            "file_size": file_size
                        }

                        # 生成稀疏向量 (BM25)
                        sparse_vector = bm25_service.encode_sparse_vector(chunk)

                        vector_service.add_document_vector(text_vector, metadata, sparse_vector=sparse_vector)

                        added_count += 1
                    else:
                        logger.error(f"文档向量维度错误：{text_vector.shape}")
                except Exception as chunk_err:
                    logger.error(f"处理文档分块失败：{str(chunk_err)}")
                    continue

            logger.info(f"文档向量化及稀疏向量存储完成：{file.filename}")

            logger.info(f"文档向量化完成：{file.filename}, 成功{added_count}/{len(chunked_docs)}个分块")
            
        except Exception as e:
            logger.warning(f"文档向量化失败：{e}")
        
        return JSONResponse(content={
            "code": 200,
            "msg": "文档上传成功",
            "data": {
                "file_name": file_name,
                "bucket": settings.MINIO_BUCKET_NAME,
                "file_size": f"{file_size / 1024 / 1024:.2f}MB"
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传失败：{e}")
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")


@router.post("/medical-images/")
async def upload_medical_images(files: list[UploadFile] = File(...)):
    """
    上传医疗影像图片（批量）
    
    Args:
        files: 图片文件列表
        
    Returns:
        批量上传结果
    """
    upload_result = []
    
    for file in files:
        try:
            logger.info(f"🖼️ 开始上传图片：{file.filename}")
            
            # 验证文件类型
            if file.content_type not in ["image/jpeg", "image/png", "image/tiff", "image/webp"]:
                upload_result.append({
                    "file_name": file.filename,
                    "status": "失败",
                    "reason": f"不支持的影像类型：{file.content_type}"
                })
                continue
            
            # 读取文件内容
            file_content = await file.read()
            file_size = len(file_content)
            
            # 处理图片
            img = Image.open(io.BytesIO(file_content)).convert('RGB')
            
            # 生成文件名
            import time
            file_name = f"img_{time.time()}_{file.filename}"
            
            # 上传到 MinIO
            await file.seek(0)
            minio_service.upload_file_data(
                bucket_name=settings.MINIO_BUCKET_NAME1,
                object_name=file_name,
                file_data=file_content,
                content_type=file.content_type
            )
            
            # 提取 CLIP 特征
            feature_vector = clip_feature_extractor.extract_image_features(img)
            
            # 添加到向量库
            metadata = {
                "bucket_name": settings.MINIO_BUCKET_NAME1,
                "filename": file.filename,
                "minio_object_name": file_name,
                "minio_bucket": settings.MINIO_BUCKET_NAME1,
                "upload_time": str(asyncio.get_event_loop().time())
            }
            
            vector_service.add_image_vector(feature_vector, metadata)
            
            upload_result.append({
                "file_name": file.filename,
                "storage_name": file_name,
                "status": "成功",
                "file_size": f"{file_size / 1024 / 1024:.2f}MB"
            })
            
            logger.info(f"✅ 图片上传并向量化完成：{file.filename}")
            
        except Exception as e:
            logger.error(f"图片上传失败：{e}")
            upload_result.append({
                "file_name": file.filename,
                "status": "失败",
                "reason": str(e)
            })
    
    return {
        "code": 200,
        "msg": "批量影像上传完成",
        "data": upload_result
    }


@router.post("/medical-videos/")
async def upload_medical_videos(files: list[UploadFile] = File(...)):
    """
    上传医疗视频（仅存储，不向量化）
    
    Args:
        files: 视频文件列表
        
    Returns:
        批量上传结果
    """
    upload_result = []
    
    for file in files:
        try:
            logger.info(f"🎥 开始上传视频：{file.filename}")
            
            if file.content_type not in settings.ALLOWED_FILE_CONTENT_TYPES:
                upload_result.append({
                    "file_name": file.filename,
                    "status": "失败",
                    "reason": f"不支持的视频类型：{file.content_type}"
                })
                continue
            
            file_content = await file.read()
            file_size = len(file_content)
            
            import time
            file_name = f"video_{time.time()}_{file.filename}"
            
            await file.seek(0)
            minio_service.upload_file_data(
                bucket_name=settings.MINIO_BUCKET_NAME2,
                object_name=file_name,
                file_data=file_content,
                content_type=file.content_type
            )
            
            upload_result.append({
                "file_name": file.filename,
                "storage_name": file_name,
                "status": "成功",
                "file_size": f"{file_size / 1024 / 1024:.2f}MB"
            })
            
            logger.info(f"✅ 视频上传成功：{file.filename}")
            
        except Exception as e:
            logger.error(f"视频上传失败：{e}")
            upload_result.append({
                "file_name": file.filename,
                "status": "失败",
                "reason": str(e)
            })
    
    return {
        "code": 200,
        "msg": "批量视频上传完成",
        "data": upload_result
    }
