"""
文档检索工具
用于检索医疗文档知识库
"""
import os

# 设置 HuggingFace 国内镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = './cache'

from langchain_core.tools import tool
from services.cache_service import cache_service
from services.vector_service import vector_service
from services.bm25_service import bm25_service
from sentence_transformers import SentenceTransformer
from core import settings
import numpy as np
import logging
from FlagEmbedding import FlagReranker


logger = logging.getLogger(__name__)

# 初始化 Embedding 模型（优先使用本地缓存）
embed_model = SentenceTransformer(
    settings.EMBEDDING_MODEL_NAME,
    cache_folder=settings.EMBEDDING_CACHE_FOLDER,
    local_files_only=False  # 优先尝试下载，失败则使用缓存
)

# 重排序模型延迟加载（避免启动时内存不足）
_reranker_instance = None

def get_reranker():
    """
    获取重排序模型实例（单例模式，延迟加载）
    只在第一次调用时才初始化模型，避免 Celery Worker 启动时内存溢出
    """
    global _reranker_instance
    if _reranker_instance is None:
        logger.info("🔄 正在初始化重排序模型 BAAI/bge-reranker-v2-m3...")
        try:
            _reranker_instance = FlagReranker(
                'BAAI/bge-reranker-v2-m3',
                use_fp16=False,  # Windows 下禁用 FP16 避免内存问题
                device='cpu'     # 强制使用 CPU
            )
            logger.info("✅ 重排序模型初始化完成")
        except Exception as e:
            logger.error(f"❌ 重排序模型初始化失败：{e}")
            raise
    return _reranker_instance


@tool
def document_search_tool(query: str, top_k: int = 5, domain: str = None,
                         search_mode: str = "hybrid") -> dict:
    """
    检索医疗文档知识库（含重排序优化）

    参数:
        query: 用户查询文本
        top_k: 返回文档数量，默认 3 篇
        domain: 领域过滤（如"内科"、"外科"、"心血管"）
        search_mode: 搜索模式 ("vector" | "bm25" | "hybrid")，默认混合搜索

    返回:
        包含检索结果的字典
    """
    try:
        logger.info(f"开始文档检索：{query[:50]}, 模式：{search_mode}")

        # 1. 生成查询向量
        query_vector = embed_model.encode(query, convert_to_numpy=True)
        query_vector = np.array(query_vector, dtype=np.float32)

        # 2. 构建过滤条件
        filter_dict = {"type": "medical_document"}
        if domain:
            filter_dict["domain"] = domain

        # 【关键修改】：先检索出更多的候选项（例如 10 个），用于重排序
        candidate_k = max(top_k * 3, 10) 

        # 3. 根据搜索模式执行检索
        results = []
        if search_mode == "vector":
            results = vector_service.search_documents(
                query_vector=query_vector,
                filter_dict=filter_dict,
                top_k=candidate_k
            )
        elif search_mode == "bm25":
            bm25_results = bm25_service.search(query=query, top_k=candidate_k)
            for item in bm25_results:
                results.append({
                    "id": item["doc_id"],
                    "similarity": item["score"],
                    "metadata": {"content": item["content"]}
                })
        else:
            # 混合检索
            results = vector_service.hybrid_search_documents(
                query_text=query,
                query_vector=query_vector,
                filter_dict=filter_dict,
                top_k=candidate_k
            )

        # 4. 【新增】重排序（Rerank）逻辑：对候选文档进行精细化相关性打分
        import time
        rerank_start = time.time()
        if len(results) > 1:
            logger.info(f"🔄 开始重排序，候选文档数：{len(results)}")
            pairs = []
            # 构建查询与文档内容的配对列表，用于重排序模型输入
            for res in results:
                content = res.get("metadata", {}).get("content", "")
                if content:
                    pairs.append([query, content])
            
            if pairs:
                # 获取重排序模型实例（延迟加载）
                reranker = get_reranker()
                # 使用 Reranker 计算每对查询-文档的相关性得分，并归一化
                scores = reranker.compute_score(pairs, normalize=True)
                
                # 将计算得到的重排序得分赋值回对应的结果对象中
                for i, res in enumerate(results):
                    if i < len(scores):
                        res['rerank_score'] = scores[i]
                
                # 根据重排序得分从高到低对结果列表进行重新排序
                results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
                logger.info(f"✅ 重排序完成，耗时：{time.time() - rerank_start:.2f}秒")
            else:
                logger.warning("⚠️ 没有有效的文档内容用于重排序")
        else:
            logger.info("⏭️ 跳过重排序（候选文档不足）")

        # 5. 截取最终需要的 top_k 个最相关文档
        final_results = results[:top_k]

        # 6. 格式化返回结果
        documents = []
        for result in final_results:
            metadata = result.get("metadata", {})
            documents.append({
                "file_name": metadata.get("original_file_name", "未知文档"),
                "content_snippet": metadata.get("content", "")[:512],
                "similarity": result.get("rerank_score", result.get("similarity", 0)),
                "chunk_index": metadata.get("chunk_index", 0),
                "upload_time": metadata.get("upload_time", ""),
                "user_id": metadata.get("user_id", "")
            })

        logger.info(f"文档检索完成，返回 {len(documents)} 篇文档")

        return {
            "documents": documents,
            "total_count": len(documents),
            "query": query,
            "search_mode": search_mode
        }

    except Exception as e:
        logger.error(f"文档检索失败：{e}", exc_info=True)
        return {
            "documents": [],
            "total_count": 0,
            "query": query,
            "error": str(e)
        }
