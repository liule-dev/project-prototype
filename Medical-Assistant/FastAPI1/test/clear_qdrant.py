"""
清理 Qdrant 数据库中的所有数据
用于重置向量库
"""
from core.qdrant import qdrant_client
from core.qdrant import QDRANT_COLLECTIONS
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_all_collections():
    """清空所有集合中的数据"""
    logger.info("=" * 60)
    logger.info("开始清理 Qdrant 数据库")
    logger.info("=" * 60)
    
    # 确保已连接
    if not qdrant_client._initialized:
        logger.info("正在连接 Qdrant...")
        qdrant_client.connect()
        logger.info("✅ Qdrant 连接成功")
    
    total_deleted = 0
    
    # 遍历所有集合
    for collection_name in QDRANT_COLLECTIONS.keys():
        try:
            # 检查集合是否存在
            if not qdrant_client.client.collection_exists(collection_name):
                logger.warning(f"⚠️  集合 {collection_name} 不存在，跳过")
                continue
            
            # 获取集合信息
            collection_info = qdrant_client.client.get_collection(collection_name)
            points_count = collection_info.points_count
            
            if points_count == 0:
                logger.info(f"ℹ️  集合 {collection_name} 为空，无需清理")
                continue
            
            logger.info(f"📊 集合 {collection_name}: 当前数据量 = {points_count}")
            
            # 删除所有点
            logger.info(f"🗑️  正在删除集合 {collection_name} 中的所有数据...")
            
            # 方法 1: 使用 delete_by_filter 删除所有数据
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue
            
            # 获取所有点的 ID 并删除
            all_points = []
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
                
                all_points.extend([p.id for p in points])
                offset = next_offset
                
                if next_offset is None:
                    break
            
            # 批量删除
            if all_points:
                from qdrant_client.http.models import PointIdsList
                qdrant_client.client.delete(
                    collection_name=collection_name,
                    points_selector=PointIdsList(points=all_points)
                )
                logger.info(f"✅ 已删除集合 {collection_name} 中的 {len(all_points)} 条数据")
                total_deleted += len(all_points)
            else:
                logger.info(f"ℹ️  集合 {collection_name} 中没有数据")
        
        except Exception as e:
            logger.error(f"❌ 清理集合 {collection_name} 失败：{e}")
            continue
    
    logger.info("=" * 60)
    logger.info(f"清理完成！共删除 {total_deleted} 条数据")
    logger.info("=" * 60)
    
    return total_deleted


def clear_collection(collection_name: str):
    """清空指定集合"""
    logger.info("=" * 60)
    logger.info(f"开始清理集合：{collection_name}")
    logger.info("=" * 60)
    
    # 确保已连接
    if not qdrant_client._initialized:
        logger.info("正在连接 Qdrant...")
        qdrant_client.connect()
        logger.info("✅ Qdrant 连接成功")
    
    try:
        # 检查集合是否存在
        if not qdrant_client.client.collection_exists(collection_name):
            logger.error(f"❌ 集合 {collection_name} 不存在")
            return 0
        
        # 获取当前数据量
        collection_info = qdrant_client.client.get_collection(collection_name)
        points_count = collection_info.points_count
        
        if points_count == 0:
            logger.info(f"ℹ️  集合 {collection_name} 为空，无需清理")
            return 0
        
        logger.info(f"📊 集合 {collection_name}: 当前数据量 = {points_count}")
        
        # 获取所有点并删除
        all_points = []
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
            
            all_points.extend([p.id for p in points])
            offset = next_offset
            
            if next_offset is None:
                break
        
        # 批量删除
        if all_points:
            from qdrant_client.http.models import PointIdsList
            qdrant_client.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=all_points)
            )
            logger.info(f"✅ 已删除集合 {collection_name} 中的 {len(all_points)} 条数据")
            return len(all_points)
        else:
            logger.info(f"ℹ️  集合 {collection_name} 中没有数据")
            return 0
    
    except Exception as e:
        logger.error(f"❌ 清理集合 {collection_name} 失败：{e}")
        return 0


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("Qdrant 数据库清理工具")
    print("=" * 60)
    print("\n可用集合:")
    for name in QDRANT_COLLECTIONS.keys():
        print(f"  - {name}")
    print("=" * 60 + "\n")
    
    # 选择清理模式
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target == "all":
            deleted = clear_all_collections()
        elif target in QDRANT_COLLECTIONS:
            deleted = clear_collection(target)
        else:
            print(f"❌ 无效的集合名称：{target}")
            print("使用方法:")
            print("  python clear_qdrant.py all              # 清空所有集合")
            print("  python clear_qdrant.py <集合名称>       # 清空指定集合")
            sys.exit(1)
    else:
        # 交互式选择
        print("请选择清理模式:")
        print("1. 清空所有集合")
        print("2. 清空指定集合")
        choice = input("\n请输入选项 (1/2): ").strip()
        
        if choice == "1":
            confirm = input("\n⚠️  确定要清空所有数据吗？此操作不可恢复！(y/n): ").strip().lower()
            if confirm == 'y':
                deleted = clear_all_collections()
            else:
                print("已取消操作")
                sys.exit(0)
        elif choice == "2":
            collection_name = input("请输入集合名称：").strip()
            if collection_name in QDRANT_COLLECTIONS:
                confirm = input(f"\n⚠️  确定要清空集合 '{collection_name}' 吗？此操作不可恢复！(y/n): ").strip().lower()
                if confirm == 'y':
                    deleted = clear_collection(collection_name)
                else:
                    print("已取消操作")
                    sys.exit(0)
            else:
                print(f"❌ 无效的集合名称：{collection_name}")
                sys.exit(1)
        else:
            print("❌ 无效的选项")
            sys.exit(1)
    
    print(f"\n✅ 清理完成！共删除 {deleted} 条数据\n")
