"""
清理 Redis 缓存数据
支持按类型清理或清空所有缓存
"""
import sys
import os

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.redis import redis_client
from core import REDIS_KEY_PREFIX, CACHE_TTL
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_redis_stats():
    """获取 Redis 统计信息"""
    try:
        # 使用底层的 redis 客户端
        info = redis_client.client.info()
        db_size = redis_client.client.dbsize()

        stats = {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_human': info.get('used_memory_human', 'N/A'),
            'total_keys': db_size,
            'uptime_days': info.get('uptime_in_days', 0)
        }

        return stats
    except Exception as e:
        logger.error(f"获取 Redis 统计失败：{e}")
        return None


def count_keys_by_pattern(pattern: str) -> int:
    """统计匹配某模式的 key 数量（使用 SCAN 避免阻塞）"""
    try:
        count = 0
        cursor = 0
        while True:
            cursor, keys = redis_client.client.scan(cursor=cursor, match=pattern, count=100)
            count += len(keys)
            if cursor == 0:
                break
        return count
    except Exception as e:
        logger.error(f"统计 key 数量失败：{e}")
        return 0


def parse_memory_to_bytes(memory_str: str) -> int:
    """
    将内存字符串转换为字节数

    Args:
        memory_str: 内存字符串 (如 "834.15K", "1.2M", "500B")

    Returns:
        字节数 (int)
    """
    try:
        memory_str = memory_str.strip().upper()

        if memory_str.endswith('KB') or memory_str.endswith('K'):
            value = float(memory_str.replace('KB', '').replace('K', ''))
            return int(value * 1024)
        elif memory_str.endswith('MB') or memory_str.endswith('M'):
            value = float(memory_str.replace('MB', '').replace('M', ''))
            return int(value * 1024 * 1024)
        elif memory_str.endswith('GB') or memory_str.endswith('G'):
            value = float(memory_str.replace('GB', '').replace('G', ''))
            return int(value * 1024 * 1024 * 1024)
        elif memory_str.endswith('B'):
            return int(float(memory_str.replace('B', '')))
        else:
            # 假设是字节
            return int(float(memory_str))
    except Exception:
        return 0


def delete_keys_by_pattern(pattern: str, dry_run: bool = True) -> int:
    """
    删除匹配某模式的 key（使用 SCAN 迭代删除）

    Args:
        pattern: Redis key 模式（支持通配符）
        dry_run: True=仅模拟，不实际删除；False=实际删除

    Returns:
        删除的 key 数量
    """
    try:
        deleted_count = 0
        cursor = 0
        found_keys = []

        # 第一次扫描用于统计和 dry_run 显示
        while True:
            cursor, keys = redis_client.client.scan(cursor=cursor, match=pattern, count=100)
            found_keys.extend(keys)
            if cursor == 0:
                break

        count = len(found_keys)

        if count == 0:
            logger.debug(f"ℹ️  未找到匹配的 key: {pattern}")
            return 0

        if dry_run:
            logger.info(f"📊 拟删除 {count} 个 key (模式：{pattern})")
            # 显示前 5 个示例
            for key in found_keys[:5]:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                logger.debug(f"  - {key_str}")
            if count > 5:
                logger.debug(f"  ... 还有 {count - 5} 个")
        else:
            # 实际删除
            for key in found_keys:
                # 使用封装的 delete 方法，保持一致性
                redis_client.delete(key)
                deleted_count += 1
            logger.info(f"✅ 已删除 {deleted_count} 个 key (模式：{pattern})")

        return count

    except Exception as e:
        logger.error(f"删除 key 失败：{e}")
        return 0


def clear_clip_vectors(dry_run: bool = True):
    """清理 CLIP 向量缓存"""
    pattern = f"{REDIS_KEY_PREFIX['CLIP_TEXT']}:*"
    return delete_keys_by_pattern(pattern, dry_run)


def clear_minio_urls(dry_run: bool = True):
    """清理 MinIO 临时链接缓存"""
    pattern = f"{REDIS_KEY_PREFIX['MINIO_URL']}:*"
    return delete_keys_by_pattern(pattern, dry_run)


def clear_llm_answers(dry_run: bool = True):
    """清理 LLM 回答缓存"""
    pattern = f"{REDIS_KEY_PREFIX['LLM_ANSWER']}:*"
    return delete_keys_by_pattern(pattern, dry_run)


def clear_session_history(dry_run: bool = True):
    """清理会话历史缓存"""
    pattern = f"{REDIS_KEY_PREFIX['HISTORY']}:*"
    return delete_keys_by_pattern(pattern, dry_run)


def clear_all_cache(dry_run: bool = True):
    """
    清理所有缓存

    Args:
        dry_run: True=仅模拟，不实际删除；False=实际删除
    """
    logger.info("=" * 60)
    logger.info("开始清理 Redis 缓存")
    logger.info(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # 获取清理前统计
    before_stats = get_redis_stats()
    if before_stats:
        logger.info(f"\n📊 清理前统计:")
        logger.info(f"   总 Key 数：{before_stats['total_keys']}")
        logger.info(f"   内存使用：{before_stats['used_memory_human']}")
        logger.info(f"   运行天数：{before_stats['uptime_days']}")

    # 分类清理统计
    stats = {
        'clip_vectors': 0,
        'minio_urls': 0,
        'llm_answers': 0,
        'session_history': 0,
        'total': 0
    }

    logger.info("\n📋 清理详情:")

    # 清理 CLIP 向量
    count = clear_clip_vectors(dry_run)
    stats['clip_vectors'] = count
    stats['total'] += count

    # 清理 MinIO 链接
    count = clear_minio_urls(dry_run)
    stats['minio_urls'] = count
    stats['total'] += count

    # 清理 LLM 回答
    count = clear_llm_answers(dry_run)
    stats['llm_answers'] = count
    stats['total'] += count

    # 清理会话历史
    count = clear_session_history(dry_run)
    stats['session_history'] = count
    stats['total'] += count

    # 获取清理后统计
    after_stats = get_redis_stats()

    logger.info("\n" + "=" * 60)
    if dry_run:
        logger.info("📊 模拟清理完成（未实际删除）")
        logger.info(f"拟删除总数：{stats['total']} 个 key")
    else:
        logger.info("✅ 清理完成！")
        logger.info(f"实际删除：{stats['total']} 个 key")

        if after_stats:
            logger.info(f"\n📊 清理后统计:")
            logger.info(f"   总 Key 数：{after_stats['total_keys']}")
            logger.info(f"   内存使用：{after_stats['used_memory_human']}")

            if before_stats and after_stats:
                before_bytes = parse_memory_to_bytes(before_stats['used_memory_human'])
                after_bytes = parse_memory_to_bytes(after_stats['used_memory_human'])
                freed_bytes = before_bytes - after_bytes

                if freed_bytes >= 1024 * 1024:
                    logger.info(f"   释放内存：约 {freed_bytes / 1024 / 1024:.2f} MB")
                elif freed_bytes >= 1024:
                    logger.info(f"   释放内存：约 {freed_bytes / 1024:.2f} KB")
                else:
                    logger.info(f"   释放内存：约 {freed_bytes} B")

    logger.info("\n📋 分类统计:")
    logger.info(f"   CLIP 向量：{stats['clip_vectors']} 个")
    logger.info(f"   MinIO 链接：{stats['minio_urls']} 个")
    logger.info(f"   LLM 回答：{stats['llm_answers']} 个")
    logger.info(f"   会话历史：{stats['session_history']} 个")
    logger.info("=" * 60)

    return stats


def clear_specific_type(type_name: str, dry_run: bool = True):
    """
    清理指定类型的缓存

    Args:
        type_name: 缓存类型名称
        dry_run: True=仅模拟，不实际删除
    """
    logger.info("=" * 60)
    logger.info(f"开始清理 {type_name} 缓存")
    logger.info("=" * 60)

    clear_functions = {
        'clip': clear_clip_vectors,
        'minio': clear_minio_urls,
        'llm': clear_llm_answers,
        'history': clear_session_history
    }

    if type_name.lower() not in clear_functions:
        logger.error(f"❌ 不支持的缓存类型：{type_name}")
        logger.info("支持的类型：clip, minio, llm, history")
        return 0

    count = clear_functions[type_name.lower()](dry_run)

    logger.info("=" * 60)
    if dry_run:
        logger.info(f"📊 拟删除 {count} 个 {type_name} 缓存")
    else:
        logger.info(f"✅ 已删除 {count} 个 {type_name} 缓存")
    logger.info("=" * 60)

    return count


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Redis 缓存清理工具")
    print("=" * 60)
    print(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # 显示可用缓存类型
    print("可用的缓存类型:")
    print("  1. clip      - CLIP 文本/图片向量缓存")
    print("  2. minio     - MinIO 临时访问链接")
    print("  3. llm       - 大模型回答缓存")
    print("  4. history   - 会话历史记录")
    print("  5. all       - 清空所有缓存")
    print("=" * 60 + "\n")
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        mode = sys.argv[1].lower()
        
        if mode == "all":
            confirm = input("⚠️  确定要清空所有缓存吗？此操作不可恢复！(y/n): ").strip().lower()
            if confirm == 'y':
                clear_all_cache(dry_run=False)
            else:
                print("已取消操作")
                sys.exit(0)
        elif mode in ["clip", "minio", "llm", "history"]:
            confirm = input(f"⚠️  确定要清理 {mode} 缓存吗？(y/n): ").strip().lower()
            if confirm == 'y':
                clear_specific_type(mode, dry_run=False)
            else:
                print("已取消操作")
                sys.exit(0)
        else:
            print(f"❌ 无效的类型：{mode}")
            print("支持的类型：clip, minio, llm, history, all")
            sys.exit(1)
    else:
        # 交互式模式
        print("请选择清理模式:")
        print("1. 测试模式（仅查看，不删除）")
        print("2. 清理指定类型")
        print("3. 清空所有缓存")
        print("=" * 60 + "\n")
        
        choice = input("请输入选项 (1/2/3): ").strip()
        
        if choice == "1":
            # 测试模式
            print("\n正在分析缓存数据...\n")
            clear_all_cache(dry_run=True)
            
        elif choice == "2":
            # 清理指定类型
            type_name = input("\n请输入缓存类型 (clip/minio/llm/history): ").strip().lower()
            if type_name in ["clip", "minio", "llm", "history"]:
                confirm = input(f"\n⚠️  确定要清理 {type_name} 缓存吗？(y/n): ").strip().lower()
                if confirm == 'y':
                    clear_specific_type(type_name, dry_run=False)
                else:
                    print("已取消操作")
                    sys.exit(0)
            else:
                print(f"❌ 无效的类型：{type_name}")
                sys.exit(1)
                
        elif choice == "3":
            # 清空所有
            confirm = input("\n⚠️  确定要清空所有缓存吗？此操作不可恢复！(y/n): ").strip().lower()
            if confirm == 'y':
                clear_all_cache(dry_run=False)
            else:
                print("已取消操作")
                sys.exit(0)
        else:
            print("❌ 无效的选项")
            sys.exit(1)
    
    print("\n✅ 操作完成！\n")
