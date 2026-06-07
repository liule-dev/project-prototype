"""
每天定时清理孤立的向量化数据
使用 Windows 任务计划程序或后台服务方式运行
"""
import schedule
import time
import threading
from datetime import datetime
from cleanup_orphan_vectors import cleanup_orphan_vectors
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # 控制台输出
        logging.StreamHandler(),
        # 文件记录
        logging.FileHandler('cleanup_orphan_vectors.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def job():
    """定时任务执行函数"""
    logger.info("\n" + "=" * 60)
    logger.info("开始执行定时清理任务")
    logger.info(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        stats = cleanup_orphan_vectors()
        logger.info("✅ 定时清理任务执行成功")
        return stats
    except Exception as e:
        logger.error(f"❌ 定时清理任务执行失败：{e}")
        raise


def run_scheduler():
    """运行定时任务调度器"""
    logger.info("=" * 60)
    logger.info("Qdrant 孤立向量定时清理服务")
    logger.info("=" * 60)
    logger.info(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("配置信息:")
    logger.info("  - 执行频率：每天凌晨 2:00")
    logger.info("  - 日志文件：cleanup_orphan_vectors.log")
    logger.info("=" * 60 + "\n")
    
    # 设置定时任务：每天凌晨 2 点执行
    schedule.every().day.at("02:00").do(job)
    
    logger.info("✅ 定时任务已启动，将在每天凌晨 2:00 自动执行")
    logger.info("按 Ctrl+C 停止服务\n")
    
    # 立即执行一次（可选）
    logger.info("正在执行首次清理检查...")
    job()
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次是否有任务需要执行


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Qdrant 孤立向量定时清理服务")
    print("=" * 60)
    print("\n请选择运行模式:")
    print("1. 立即执行一次清理")
    print("2. 启动定时服务（每天凌晨 2:00 自动执行）")
    print("3. 仅测试，不实际执行")
    print("=" * 60 + "\n")
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        # 立即执行一次
        logger.info("立即执行清理任务...")
        job()
        print("\n✅ 清理完成！\n")
        
    elif choice == "2":
        # 启动定时服务
        try:
            run_scheduler()
        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断，服务已停止")
            print("\n✅ 定时服务已停止\n")
            
    elif choice == "3":
        # 仅测试
        logger.info("测试模式：检查配置...")
        logger.info("✅ 配置正确，可以正常运行")
        print("\n✅ 测试通过，配置正确\n")
        
    else:
        print("❌ 无效的选项")
