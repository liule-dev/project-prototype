"""
AI 推理相关异步任务
包括 LLM 对话、向量检索、图片特征提取等
"""
from core.celery_config import celery_app
from agents.medical_agent import get_medical_agent
from services.vector_service import vector_service
from agents.clip_extractor import clip_feature_extractor
from sentence_transformers import SentenceTransformer
from core import settings
import numpy as np
import logging
import json

logger = logging.getLogger(__name__)

# 初始化 Embedding 模型（全局单例）
embed_model = SentenceTransformer(
    settings.EMBEDDING_MODEL_NAME,
    cache_folder=settings.EMBEDDING_CACHE_FOLDER,
    local_files_only=True
)


@celery_app.task(name='ai_tasks.generate_llm_response', bind=True, max_retries=3)
def generate_llm_response(self, question: str, context_messages: list = None) -> dict:
    """
    异步生成 LLM 回答
    
    Args:
        question: 用户问题
        context_messages: 历史对话上下文
        
    Returns:
        {
            "answer": str,
            "images": list,
            "confidence": float,
            "specialty": str
        }
    """
    try:
        logger.info(f"🤖 [Task] 开始生成 LLM 回答：{question[:50]}")
        
        # 获取智能体
        agent = get_medical_agent()
        
        # 调用智能体工作流
        result = agent.query_with_context(
            question=question,
            context_messages=context_messages or []
        )
        
        logger.info(f"✅ [Task] LLM 回答生成完成，置信度：{result.get('confidence', 0):.2f}")
        
        return {
            "answer": result.get("answer", ""),
            "images": result.get("images", []),
            "confidence": result.get("confidence", 0.0),
            "specialty": result.get("specialty", "unknown"),
            "retry_count": result.get("retry_count", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] LLM 回答生成失败：{e}")
        
        # 重试逻辑
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
        return {
            "answer": f"抱歉，处理您的问题时出现错误：{str(e)}",
            "images": [],
            "confidence": 0.0,
            "specialty": "error",
            "retry_count": 0,
            "error": str(e)
        }


@celery_app.task(name='ai_tasks.extract_image_features', bind=True)
def extract_image_features(self, image_bytes: bytes) -> dict:
    """
    异步提取图片 CLIP 特征
    
    Args:
        image_bytes: 图片二进制数据
        
    Returns:
        {
            "feature_vector": list,
            "dimension": int
        }
    """
    try:
        from PIL import Image
        import io
        
        logger.info(f"🖼️ [Task] 开始提取图片特征")
        
        # 加载图片
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # 提取特征
        feature_vector = clip_feature_extractor.extract_image_features(img)
        
        logger.info(f"✅ [Task] 图片特征提取完成，维度：{len(feature_vector)}")
        
        return {
            "feature_vector": feature_vector.tolist(),
            "dimension": len(feature_vector)
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 图片特征提取失败：{e}")
        raise


@celery_app.task(name='ai_tasks.vector_search_images', bind=True)
def vector_search_images(self, query_vector: list, top_k: int = 5, filter_dict: dict = None) -> list:
    """
    异步向量检索图片
    
    Args:
        query_vector: 查询向量
        top_k: 返回数量
        filter_dict: 过滤条件
        
    Returns:
        相似图片结果列表
    """
    try:
        logger.info(f"🔍 [Task] 开始向量检索图片")
        
        # 转换为 numpy 数组
        query_vec = np.array(query_vector, dtype=np.float32)
        
        # 执行检索
        results = vector_service.search_images(
            query_vector=query_vec,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        logger.info(f"✅ [Task] 图片检索完成，找到 {len(results)} 个结果")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ [Task] 图片检索失败：{e}")
        raise


@celery_app.task(name='ai_tasks.vector_search_documents', bind=True)
def vector_search_documents(self, query_text: str, query_vector: list, 
                           filter_dict: dict = None, top_k: int = 3) -> list:
    """
    异步混合检索文档（向量 + BM25）
    
    Args:
        query_text: 查询文本（用于 BM25）
        query_vector: 查询向量（用于向量检索）
        filter_dict: 过滤条件
        top_k: 返回数量
        
    Returns:
        混合检索结果列表
    """
    try:
        logger.info(f"🔍 [Task] 开始混合检索文档")
        
        # 转换为 numpy 数组
        query_vec = np.array(query_vector, dtype=np.float32)
        
        # 执行混合检索
        results = vector_service.hybrid_search_documents(
            query_text=query_text,
            query_vector=query_vec,
            filter_dict=filter_dict,
            top_k=top_k
        )
        
        logger.info(f"✅ [Task] 文档检索完成，找到 {len(results)} 个结果")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ [Task] 文档检索失败：{e}")
        raise


@celery_app.task(name='ai_tasks.generate_text_embedding', bind=True)
def generate_text_embedding(self, text: str) -> dict:
    """
    异步生成文本 Embedding
    
    Args:
        text: 输入文本
        
    Returns:
        {
            "embedding": list,
            "dimension": int
        }
    """
    try:
        logger.info(f"📝 [Task] 开始生成文本 Embedding")
        
        # 生成 Embedding
        embedding = embed_model.encode(text, convert_to_numpy=True)
        embedding = np.array(embedding, dtype=np.float32)
        
        logger.info(f"✅ [Task] 文本 Embedding 生成完成，维度：{len(embedding)}")
        
        return {
            "embedding": embedding.tolist(),
            "dimension": len(embedding)
        }
        
    except Exception as e:
        logger.error(f"❌ [Task] 文本 Embedding 生成失败：{e}")
        raise
