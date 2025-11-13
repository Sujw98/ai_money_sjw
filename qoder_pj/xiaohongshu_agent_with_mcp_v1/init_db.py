"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_settings
from src.database.db_manager import init_db_manager
from src.utils.logger import setup_logger

logger = setup_logger("db_init", "INFO")


def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 加载配置
        settings = get_settings()
        logger.info(f"数据库地址: {settings.mysql_host}:{settings.mysql_port}")
        logger.info(f"数据库名: {settings.mysql_database}")
        
        # 初始化数据库管理器
        db_manager = init_db_manager(settings.database_url)
        
        # 创建表
        logger.info("创建数据库表...")
        db_manager.create_tables()
        
        logger.info("数据库初始化完成！")
        logger.info("\n表结构说明：")
        logger.info("1. outlines - 大纲表")
        logger.info("2. topics - 主题表")
        logger.info("3. inspirations - 灵感素材表")
        logger.info("4. contents - 内容表")
        logger.info("5. publish_records - 发布记录表")
        
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False


def reset_database():
    """重置数据库（删除所有表并重建）"""
    try:
        logger.warning("警告：即将删除所有数据库表！")
        confirm = input("确定要继续吗？(yes/no): ")
        
        if confirm.lower() != 'yes':
            logger.info("操作已取消")
            return False
        
        # 加载配置
        settings = get_settings()
        
        # 初始化数据库管理器
        db_manager = init_db_manager(settings.database_url)
        
        # 删除所有表
        logger.info("删除所有表...")
        db_manager.drop_tables()
        
        # 重新创建表
        logger.info("重新创建表...")
        db_manager.create_tables()
        
        logger.info("数据库重置完成！")
        return True
        
    except Exception as e:
        logger.error(f"数据库重置失败: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置数据库（删除所有表并重建）"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()
