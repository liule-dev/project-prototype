"""
Qdrant 向量数据库客户端封装
提供统一的向量存储和检索接口
"""
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff, WalConfigDiff, PointStruct, SparseVectorParams, SparseIndexType
from core.config import settings
import logging

logger = logging.getLogger(__name__)

QDRANT_CONFIG = {
    'host': settings.QDRANT_HOST,
    'port': settings.QDRANT_PORT,
    'grpc_port': settings.QDRANT_GRPC_PORT
}

QDRANT_COLLECTIONS = {
    settings.QDRANT_COLLECTION_NAME: {'vector_size': 512, 'distance': 'COSINE'},
    settings.QDRANT_DOC_COLLECTION_NAME: {'vector_size': 512, 'distance': 'COSINE'}
}

QDRANT_INDEX_PARAMS = {
    'hnsw_config': {'m': 16, 'ef_construct': 100},
    'wal_config': {'wal_capacity_mb': 32}
}


class QdrantDatabaseClient:
    """Qdrant 数据库客户端"""
    
    def __init__(self, auto_connect=True):
        self.client = None
        self._initialized = False
        if auto_connect:
            self.connect()
    
    def connect(self, max_retries=3, retry_delay=2):
        """连接到 Qdrant 服务"""
        if self._initialized:
            return
        
        import time
        for attempt in range(max_retries):
            try:
                self.client = QdrantClient(
                    host=QDRANT_CONFIG['host'],
                    port=QDRANT_CONFIG['port'],
                    grpc_port=QDRANT_CONFIG['grpc_port'],
                    prefer_grpc=True
                )
                self._init_collections()
                self._initialized = True
                logger.info("✅ Qdrant 连接成功")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Qdrant 连接失败，{retry_delay}秒后重试 ({attempt+1}/{max_retries}): {e}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Qdrant 连接失败，已重试 {max_retries} 次：{e}")
                    raise
    
    def _init_collections(self):
        """初始化向量集合（支持稠密+稀疏向量）"""
        for name, config in QDRANT_COLLECTIONS.items():
            if not self.client.collection_exists(name):
                try:
                    # 定义稠密向量（用于语义检索）
                    vectors_config = VectorParams(
                        size=config['vector_size'],
                        distance=Distance[config['distance']]
                    )
                    
                    # 定义稀疏向量（用于 BM25 关键词检索）
                    # 注意：Qdrant 1.17.1 中 SparseVectorParams 不需要 index 参数
                    sparse_vectors_config = {
                        "sparse-text": SparseVectorParams()
                    }
                    
                    self.client.create_collection(
                        collection_name=name,
                        vectors_config=vectors_config,
                        sparse_vectors_config=sparse_vectors_config,
                        hnsw_config=HnswConfigDiff(**QDRANT_INDEX_PARAMS['hnsw_config']),
                        wal_config=WalConfigDiff(**QDRANT_INDEX_PARAMS['wal_config'])
                    )
                    logger.info(f"✅ 创建 Qdrant 集合（含稀疏向量支持）：{name}")
                except Exception as e:
                    logger.error(f"创建集合 {name} 失败：{e}")
                    # 尝试不带稀疏向量的方式创建（降级方案）
                    try:
                        self.client.create_collection(
                            collection_name=name,
                            vectors_config=VectorParams(
                                size=config['vector_size'],
                                distance=Distance[config['distance']]
                            ),
                            hnsw_config=HnswConfigDiff(**QDRANT_INDEX_PARAMS['hnsw_config']),
                            wal_config=WalConfigDiff(**QDRANT_INDEX_PARAMS['wal_config'])
                        )
                        logger.info(f"⚠️ 创建集合 {name} 成功（仅稠密向量，无稀疏向量支持）")
                    except Exception as e2:
                        logger.error(f"降级方案也失败：{e2}")
    
    def add_vector(self, collection: str, vector: list, metadata: dict, point_id: int = None, sparse_vector: dict = None):
        """
        添加向量到集合（支持稠密+稀疏混合存储）
        
        Args:
            collection: 集合名称
            vector: 稠密向量列表 (512维)
            metadata: 负载数据 (payload)
            point_id: 可选的点ID
            sparse_vector: 可选的稀疏向量字典 {"indices": [...], "values": [...]}
        """
        try:
            import uuid
            if point_id is None:
                point_id = uuid.uuid4().int & (1 << 63) - 1
            
            # 构建向量结构
            # 如果提供了稀疏向量，使用命名字段；否则使用默认向量
            if sparse_vector:
                from qdrant_client.http.models import SparseVector
                vectors = {
                    "": vector,  # 默认稠密向量
                    "sparse-text": SparseVector(
                        indices=sparse_vector['indices'],
                        values=sparse_vector['values']
                    )
                }
            else:
                # 仅稠密向量时，直接传递列表（不使用字典）
                vectors = vector
            
            points = [PointStruct(id=point_id, vector=vectors, payload=metadata)]
            
            self.client.upsert(collection_name=collection, points=points)
            logger.debug(f"✅ 添加向量到 {collection}, ID: {point_id}")
        except Exception as e:
            logger.error(f"添加向量失败 {collection}: {e}")
            raise
    
    def search_similar(self, collection: str, query_vector: list, top_k: int = 5, filter_dict: dict = None):
        """搜索相似向量（稠密）"""
        try:
            search_filter = None
            if filter_dict:
                from qdrant_client.http.models import FieldCondition, MatchValue, Filter
                must_conditions = []
                for key, value in filter_dict.items():
                    must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                search_filter = Filter(must=must_conditions)
            
            results = self.client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=top_k,
                query_filter=search_filter
            )
            
            formatted_results = []
            for result in results.points:
                formatted_results.append({
                    "id": result.id,
                    "similarity": result.score,
                    "metadata": result.payload
                })
            return formatted_results
        except Exception as e:
            logger.error(f"搜索相似向量失败 {collection}: {e}")
            return []

    def hybrid_search(self, collection: str, dense_vector: list, sparse_vector: dict, 
                      filter_dict: dict = None, limit: int = 3):
        """
        执行混合检索（稠密向量 + 稀疏向量）
        
        Args:
            collection: 集合名称
            dense_vector: 稠密向量列表 (BiomedCLIP 等生成)
            sparse_vector: 稀疏向量字典 {"indices": [...], "values": [...]}
            filter_dict: 过滤条件
            limit: 返回数量
        """
        try:
            from qdrant_client.http.models import (
                Prefetch, FusionQuery, SparseVector, FieldCondition, MatchValue, Filter
            )

            # 1. 构建过滤条件
            search_filter = None
            if filter_dict:
                must_conditions = []
                for key, value in filter_dict.items():
                    must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                search_filter = Filter(must=must_conditions)

            # 2. 构建稀疏向量对象
            sparse_obj = SparseVector(
                indices=sparse_vector['indices'],
                values=sparse_vector['values']
            )

            # 3. 执行混合查询 (使用 Fusion 融合)
            # 先分别进行稠密和稀疏检索，然后在 Qdrant 内部融合
            results = self.client.query_points(
                collection_name=collection,
                prefetch=[
                    Prefetch(
                        query=dense_vector,
                        using="",
                        limit=limit * 2
                    ),
                    Prefetch(
                        query=sparse_obj,
                        using="sparse-text",
                        limit=limit * 2
                    )
                ],
                query=FusionQuery(fusion="rrf"),  # 使用 RRF 算法融合
                limit=limit,
                query_filter=search_filter,
                with_payload=True
            )

            formatted_results = []
            for result in results.points:
                formatted_results.append({
                    "id": result.id,
                    "similarity": result.score,
                    "metadata": result.payload
                })
            return formatted_results

        except Exception as e:
            logger.error(f"混合检索失败 {collection}: {e}")
            return []
    
    def delete_vector(self, collection: str, point_ids: list):
        """删除向量"""
        try:
            self.client.delete(collection_name=collection, points_selector={"points": point_ids})
            logger.info(f"✅ 删除 {len(point_ids)} 个向量 from {collection}")
        except Exception as e:
            logger.error(f"删除向量失败 {collection}: {e}")
            raise
    
    def collection_stats(self, collection: str):
        """获取集合统计信息"""
        try:
            return self.client.get_collection(collection)
        except Exception as e:
            logger.error(f"获取集合统计失败 {collection}: {e}")
            return {}
    
    def close(self):
        """关闭连接"""
        self.client.close()
        logger.info("✅ Qdrant 连接已关闭")

# 全局 Qdrant 客户端实例 (延迟初始化)
qdrant_client = QdrantDatabaseClient(auto_connect=False)
