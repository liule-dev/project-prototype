"""
向量服务层：封装 Qdrant 操作
提供业务级的向量存储和检索接口
"""


import numpy as np
from core import qdrant_client, settings
from services.bm25_service import bm25_service
import logging

logger = logging.getLogger(__name__)

# 确保 Qdrant 客户端已连接
if not qdrant_client._initialized:
    try:
        qdrant_client.connect()
    except Exception as e:
        logger.warning(f"Qdrant 连接失败：{e}")


class VectorService:
    """业务向量服务"""
    
    # ========== 图片向量服务 ==========
    
    @staticmethod
    def add_image_vector(feature_vector: np.ndarray, metadata: dict):
        """
        添加图片向量到向量库
        
        Args:
            feature_vector: 图片特征向量（512 维）
            metadata: 图片元数据（文件名、路径、上传时间等）
        """
        try:
            # 验证向量维度
            if feature_vector.ndim != 1 or len(feature_vector) != 512:
                logger.error(f"图片向量维度错误：{feature_vector.shape}, 期望：(512,)")
                raise ValueError(f"特征向量维度不正确，期望 512 维")
            
            # 添加到 Qdrant
            qdrant_client.add_vector(
                collection=settings.QDRANT_COLLECTION_NAME,
                vector=feature_vector.astype(np.float32).tolist(),
                metadata=metadata
            )
            logger.info(f"✅ 图片向量已添加：{metadata.get('filename', 'unknown')}")
        except Exception as e:
            logger.error(f"添加图片向量失败：{e}")
            raise
    
    @staticmethod
    def search_images(query_vector: np.ndarray, top_k: int = 5, filter_dict: dict = None):
        """
        检索相似图片
        
        Args:
            query_vector: 查询向量（文本或图片的特征向量）
            top_k: 返回数量
            filter_dict: 过滤条件（可选）
            
        Returns:
            相似图片结果列表
        """
        try:
            results = qdrant_client.search_similar(
                collection=settings.QDRANT_COLLECTION_NAME,
                query_vector=query_vector.astype(np.float32).tolist(),
                top_k=top_k,
                filter_dict=filter_dict
            )
            logger.info(f"✅ 图片检索完成，找到 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"图片检索失败：{e}")
            return []
    
    # ========== 文档向量服务 ==========
    
    @staticmethod
    def add_document_vector(chunk_vector: np.ndarray, metadata: dict, sparse_vector: dict = None):
        """
        添加文档向量到向量库（支持混合存储）
        
        Args:
            chunk_vector: 文档分块稠密向量（512 维）
            metadata: 文档元数据
            sparse_vector: 可选的稀疏向量（用于 BM25）
        """
        try:
            # 验证向量维度
            if chunk_vector.ndim != 1 or len(chunk_vector) != 512:
                logger.error(f"文档向量维度错误：{chunk_vector.shape}, 期望：(512,)")
                raise ValueError(f"特征向量维度不正确，期望 512 维")
            
            # 添加到 Qdrant
            qdrant_client.add_vector(
                collection=settings.QDRANT_DOC_COLLECTION_NAME,
                vector=chunk_vector.astype(np.float32).tolist(),
                metadata=metadata,
                sparse_vector=sparse_vector
            )
            logger.debug(f"✅ 文档向量已添加：{metadata.get('original_file_name', 'unknown')}")
        except Exception as e:
            logger.error(f"添加文档向量失败：{e}")
            raise
    
    @staticmethod
    def search_documents(query_vector: np.ndarray, filter_dict: dict = None, top_k: int = 3):
        """
        检索相似文档
        
        Args:
            query_vector: 查询向量
            filter_dict: 过滤条件（如 domain: "内科"）
            top_k: 返回数量
            
        Returns:
            相似文档结果列表
        """
        try:
            results = qdrant_client.search_similar(
                collection=settings.QDRANT_DOC_COLLECTION_NAME,
                query_vector=query_vector.astype(np.float32).tolist(),
                top_k=top_k,
                filter_dict=filter_dict
            )
            logger.info(f"文档检索完成，找到 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"文档检索失败：{e}")
            return []
    
    # ========== 向量库管理 ==========
    
    @staticmethod
    def get_collection_stats(collection_name: str) -> dict:
        """获取向量集合统计信息"""
        try:
            stats = qdrant_client.collection_stats(collection_name)
            return {
                "points_count": stats.points_count if hasattr(stats, 'points_count') else 0,
                "vectors_count": stats.vectors_count if hasattr(stats, 'vectors_count') else 0
            }
        except Exception as e:
            logger.error(f"获取集合统计失败：{e}")
            return {}

    @staticmethod
    def hybrid_search_documents(query_text: str, query_vector: np.ndarray,
                                filter_dict: dict = None, top_k: int = 3) -> list:
        """
        基于 Qdrant 原生的混合检索（稠密向量 + 稀疏向量 BM25）

        Args:
            query_text: 查询文本（用于生成稀疏向量）
            query_vector: 查询稠密向量
            filter_dict: 过滤条件
            top_k: 返回数量

        Returns:
            混合排序后的文档结果列表
        """
        try:
            logger.info(f"🔍 开始 Qdrant 原生混合检索：{query_text[:50]}")

            # 1. 生成稀疏向量 (BM25)
            # 注意：这里需要一个简单的分词器将文本转为 {indices: [], values: []} 格式
            sparse_vector = bm25_service.encode_sparse_vector(query_text)

            # 2. 执行 Qdrant 混合查询
            results = qdrant_client.hybrid_search(
                collection=settings.QDRANT_DOC_COLLECTION_NAME,
                dense_vector=query_vector.astype(np.float32).tolist(),
                sparse_vector=sparse_vector,
                filter_dict=filter_dict,
                limit=top_k
            )

            logger.info(f"✅ 混合检索完成，返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"混合检索失败：{e}")
            return []

    @staticmethod
    def _reciprocal_rank_fusion(vector_results: list, bm25_results: list,
                                top_k: int = 3, alpha: float = 0.7) -> list:
        """
        使用倒数排名融合（RRF）合并两种检索结果

        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            top_k: 最终返回数量
            alpha: 向量检索权重

        Returns:
            融合后的结果列表
        """
        try:
            # 构建文档ID到结果的映射
            doc_scores = {}

            # 处理向量检索结果
            for rank, result in enumerate(vector_results, 1):
                doc_id = result.get("id") or result.get("metadata", {}).get("doc_id")
                if doc_id:
                    # RRF 分数：1 / (k + rank)，k 通常取 60
                    rrf_score = 1.0 / (60 + rank)
                    vector_score = result.get("similarity", 0)

                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = {
                            "doc_id": doc_id,
                            "vector_score": vector_score,
                            "bm25_score": 0,
                            "rrf_vector": rrf_score,
                            "rrf_bm25": 0,
                            "metadata": result.get("metadata", {})
                        }
                    else:
                        doc_scores[doc_id]["rrf_vector"] = max(doc_scores[doc_id]["rrf_vector"], rrf_score)
                        doc_scores[doc_id]["vector_score"] = max(doc_scores[doc_id]["vector_score"], vector_score)

            # 处理 BM25 检索结果
            for rank, result in enumerate(bm25_results, 1):
                doc_id = result.get("doc_id")
                if doc_id:
                    rrf_score = 1.0 / (60 + rank)
                    bm25_score = result.get("score", 0)

                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = {
                            "doc_id": doc_id,
                            "vector_score": 0,
                            "bm25_score": bm25_score,
                            "rrf_vector": 0,
                            "rrf_bm25": rrf_score,
                            "metadata": {"content": result.get("content", "")}
                        }
                    else:
                        doc_scores[doc_id]["rrf_bm25"] = max(doc_scores[doc_id]["rrf_bm25"], rrf_score)
                        doc_scores[doc_id]["bm25_score"] = max(doc_scores[doc_id]["bm25_score"], bm25_score)

            # 计算最终分数：alpha * vector_rrf + (1-alpha) * bm25_rrf
            for doc_id, scores in doc_scores.items():
                final_score = alpha * scores["rrf_vector"] + (1 - alpha) * scores["rrf_bm25"]
                scores["final_score"] = final_score

            # 按最终分数排序
            sorted_results = sorted(
                doc_scores.values(),
                key=lambda x: x["final_score"],
                reverse=True
            )[:top_k]

            # 格式化输出
            formatted_results = []
            for item in sorted_results:
                formatted_results.append({
                    "id": item["doc_id"],
                    "similarity": item["final_score"],
                    "vector_score": item["vector_score"],
                    "bm25_score": item["bm25_score"],
                    "metadata": item["metadata"]
                })

            return formatted_results

        except Exception as e:
            logger.error(f"RRF 融合失败：{e}")
            return []



# 全局向量服务实例
vector_service = VectorService()
