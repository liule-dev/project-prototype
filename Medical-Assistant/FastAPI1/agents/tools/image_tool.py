"""
图片检索工具
根据文本描述检索相似的医疗影像图片
"""
from langchain_core.tools import tool
from services.cache_service import cache_service
from services.vector_service import vector_service
from services.minio_service import minio_service
from agents.clip_extractor import clip_feature_extractor
import numpy as np
import logging

logger = logging.getLogger(__name__)


@tool
def image_search_tool(query_text: str, top_k: int = 3) -> dict:
    """
    根据文本描述检索医疗影像图片
    
    参数:
        query_text: 用户的症状描述或图片特征文本（如"肺部 CT 有阴影"）
        top_k: 返回最相似的图片数量，默认 3 张
    
    返回:
        包含图片元数据和 MinIO 临时访问链接的字典
    """
    try:
        logger.info(f"🖼️ 开始图片检索：{query_text[:50]}")
        
        # 1. 从缓存获取 CLIP 向量
        text_vec = cache_service.get_clip_vector(query_text)
        
        if text_vec is None:
            # 未命中缓存，调用 CLIP 模型计算
            logger.debug("⚠️ CLIP 向量缓存未命中，正在计算...")
            text_vec = clip_feature_extractor.encode_text(query_text)
            
            # 保存到缓存
            cache_service.save_clip_vector(query_text, text_vec)
            logger.debug("✅ CLIP 向量已缓存")
        
        # 2. 检索相似图片
        similar_results = vector_service.search_images(
            query_vector=text_vec,
            top_k=top_k
        )
        
        if not similar_results:
            logger.info(f"ℹ️ 未检索到相关图片：{query_text}")
            return {
                "images": [],
                "message": "未找到相关图片",
                "total_count": 0
            }
        
        # 3. 生成 MinIO 临时链接
        result_list = []
        for item in similar_results:
            img_metadata = item.get("metadata", {})
            object_name = img_metadata.get("minio_object_name")
            
            if not object_name:
                logger.warning(f"⚠️ 图片元数据缺少文件路径信息")
                continue
            
            # 从缓存获取 MinIO 链接
            minio_url = cache_service.get_minio_url(object_name)
            
            if not minio_url:
                # 生成新的临时链接
                minio_url = minio_service.generate_presigned_url(object_name)
                
                # 保存到缓存
                cache_service.save_minio_url(object_name, minio_url)
            
            result_list.append({
                "similarity": round(float(item.get("similarity", 0)), 4),
                "url": minio_url,
                "bucket_name": img_metadata.get("minio_bucket", ""),
                "object_name": object_name,
                "filename": img_metadata.get("filename", "unknown"),
                "upload_time": img_metadata.get("upload_time", "")
            })
        
        logger.info(f"✅ 图片检索完成，找到 {len(result_list)} 张图片")
        
        return {
            "images": result_list,
            "message": f"找到{len(result_list)}张相关图片",
            "total_count": len(result_list)
        }
        
    except Exception as e:
        logger.error(f"图片检索失败：{e}")
        return {
            "images": [],
            "message": f"检索失败：{str(e)}",
            "total_count": 0,
            "error": str(e)
        }
