"""
定时清理 Qdrant 向量化数据
每天检查 MinIO 中的文档，如果文档不存在就清除对应的向量化数据
"""
from core.qdrant_client import qdrant_client
from services.minio_service import minio_service
from config.settings import settings
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_document_exists(minio_path: str) -> bool:
    """
    检查文档是否在 MinIO 中存在
    
    Args:
        minio_path: MinIO 中的路径（格式：bucket_name/object_name）
        
    Returns:
        True 如果文档存在，否则 False
    """
    try:
        # 解析路径
        if '/' in minio_path:
            parts = minio_path.split('/', 1)
            bucket_name = parts[0]
            object_name = parts[1]
            
            # 检查对象是否存在
            objects = minio_service.list_objects(bucket_name, prefix=object_name)
            exists = object_name in objects
            
            if exists:
                logger.debug(f"✅ 文档存在：{minio_path}")
            else:
                logger.warning(f"⚠️  文档不存在：{minio_path}")
            
            return exists
        else:
            logger.error(f"无效的 MinIO 路径格式：{minio_path}")
            return False
    
    except Exception as e:
        logger.error(f"检查文档失败：{e}")
        return False


def delete_vectors_by_filename(collection_name: str, filename: str):
    """
    根据文件名删除向量
    
    Args:
        collection_name: 集合名称
        filename: 原始文件名
    """
    try:
        # 确保已连接
        if not qdrant_client._initialized:
            logger.info("正在连接 Qdrant...")
            qdrant_client.connect()
        
        # 检查集合是否存在
        if not qdrant_client.client.collection_exists(collection_name):
            logger.warning(f"集合 {collection_name} 不存在，跳过")
            return 0
        
        # 查找所有匹配的点
        points_to_delete = []
        offset = None
        
        while True:
            response = qdrant_client.client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset
            )
            
            points, next_offset = response
            
            if not points:
                break
            
            # 筛选出匹配文件名的点
            for point in points:
                payload = point.payload or {}
                original_filename = payload.get('original_file_name', '')
                
                if original_filename == filename:
                    points_to_delete.append(point.id)
            
            offset = next_offset
            if next_offset is None:
                break
        
        # 批量删除
        if points_to_delete:
            from qdrant_client.http.models import PointIdsList
            
            qdrant_client.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=points_to_delete)
            )
            
            logger.info(f"✅ 已删除集合 {collection_name} 中文件 {filename} 的 {len(points_to_delete)} 条向量")
            return len(points_to_delete)
        else:
            logger.debug(f"ℹ️  集合 {collection_name} 中未找到文件 {filename} 的向量")
            return 0
    
    except Exception as e:
        logger.error(f"删除向量失败：{e}")
        return 0


def cleanup_orphan_vectors():
    """
    清理孤立的向量化数据（MinIO 中不存在的文档对应的向量）
    
    Returns:
        清理统计信息
    """
    logger.info("=" * 60)
    logger.info("开始清理孤立的向量化数据")
    logger.info(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    stats = {
        'total_checked': 0,
        'total_deleted': 0,
        'collections_processed': []
    }
    
    # 确保已连接
    if not qdrant_client._initialized:
        logger.info("正在连接 Qdrant...")
        qdrant_client.connect()
        logger.info("✅ Qdrant 连接成功")
    
    # 处理文档集合
    collections_to_check = ['medical_documents']
    
    for collection_name in collections_to_check:
        try:
            # 检查集合是否存在
            if not qdrant_client.client.collection_exists(collection_name):
                logger.warning(f"⚠️  集合 {collection_name} 不存在，跳过")
                continue
            
            logger.info(f"\n📊 处理集合：{collection_name}")
            stats['collections_processed'].append(collection_name)
            
            # 获取集合中的所有唯一文件名
            unique_filenames = set()
            offset = None
            
            while True:
                response = qdrant_client.client.scroll(
                    collection_name=collection_name,
                    limit=100,
                    offset=offset
                )
                
                points, next_offset = response
                
                if not points:
                    break
                
                for point in points:
                    payload = point.payload or {}
                    original_filename = payload.get('original_file_name', '')
                    minio_path = payload.get('minio_path', '')
                    
                    if original_filename and minio_path:
                        unique_filenames.add((original_filename, minio_path))
                
                offset = next_offset
                if next_offset is None:
                    break
            
            logger.info(f"📋 集合中共有 {len(unique_filenames)} 个唯一文件")
            stats['total_checked'] += len(unique_filenames)
            
            # 检查每个文件并删除孤立的向量
            deleted_count = 0
            for filename, minio_path in unique_filenames:
                # 检查 MinIO 中是否存在
                exists = check_document_exists(minio_path)
                
                if not exists:
                    # 文档不存在，删除对应的向量
                    count = delete_vectors_by_filename(collection_name, filename)
                    deleted_count += count
                    logger.info(f"🗑️  已清理孤立文件 {filename} 的 {count} 条向量")
                else:
                    logger.debug(f"✅ 文件 {filename} 存在，保留向量")
            
            logger.info(f"✅ 集合 {collection_name} 清理完成，共删除 {deleted_count} 条向量")
            stats['total_deleted'] += deleted_count
        
        except Exception as e:
            logger.error(f"❌ 处理集合 {collection_name} 失败：{e}")
            continue
    
    logger.info("\n" + "=" * 60)
    logger.info("清理完成！")
    logger.info(f"检查文件数：{stats['total_checked']}")
    logger.info(f"删除向量数：{stats['total_deleted']}")
    logger.info(f"处理集合：{', '.join(stats['collections_processed'])}")
    logger.info("=" * 60)
    
    return stats


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Qdrant 孤立向量清理工具")
    print("=" * 60)
    print(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # 执行清理
    stats = cleanup_orphan_vectors()
    
    print(f"\n✅ 清理完成！")
    print(f"   检查文件数：{stats['total_checked']}")
    print(f"   删除向量数：{stats['total_deleted']}")
    print(f"   处理集合：{', '.join(stats['collections_processed'])}\n")
