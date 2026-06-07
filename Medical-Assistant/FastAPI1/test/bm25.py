"""
初始化 BM25 索引脚本
从 Qdrant 中读取所有文档，构建 BM25 索引
"""
import sys

sys.path.insert(0, '.')

from core.qdrant import qdrant_client
from core.config import settings
from services.bm25_service import bm25_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_bm25_index():
    """从 Qdrant 读取文档并初始化 BM25 索引"""
    try:
        logger.info("🔄 开始初始化 BM25 索引...")

        # 连接 Qdrant
        if not qdrant_client._initialized:
            qdrant_client.connect()

        # 获取集合信息
        collection_name = settings.QDRANT_DOC_COLLECTION_NAME
        logger.info(f"📖 从集合 {collection_name} 读取文档...")

        # 注意：这里需要根据实际的 Qdrant API 来获取所有文档
        # 由于 Qdrant 的 scroll API 可以分页获取所有点
        all_points = []
        offset = None

        while True:
            records, next_offset = qdrant_client.client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            all_points.extend(records)

            if next_offset is None:
                break
            offset = next_offset

        logger.info(f"✅ 读取到 {len(all_points)} 个文档")

        # 准备文档数据
        documents = []
        for point in all_points:
            doc_id = str(point.id)
            content = point.payload.get("content", "")
            if content:
                documents.append({
                    "id": doc_id,
                    "content": content
                })

        # 批量添加到 BM25 索引
        if documents:
            bm25_service.add_documents_batch(documents)
            logger.info(f"✅ BM25 索引初始化完成，共 {len(documents)} 个文档")
        else:
            logger.warning("⚠️ 没有找到可索引的文档")

        # 打印统计信息
        stats = bm25_service.get_stats()
        logger.info(f"📊 BM25 索引统计：{stats}")

    except Exception as e:
        logger.error(f"❌ 初始化 BM25 索引失败：{e}", exc_info=True)
        raise


if __name__ == "__main__":
    initialize_bm25_index()
