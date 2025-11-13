"""
数据库管理器 - 负责数据库连接和会话管理
"""
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from src.models.db_models import Base
from src.utils.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_url: str, pool_size: int = 10, max_overflow: int = 20):
        """
        初始化数据库管理器
        
        Args:
            db_url: 数据库连接URL
            pool_size: 连接池大小
            max_overflow: 最大溢出连接数
        """
        setting = get_settings()
        self.db_url = db_url
        self.engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # 连接前检查
            echo=setting.log_sql  # 不打印SQL语句（生产环境）
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"数据库连接已建立: {db_url}")
    
    def create_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def drop_tables(self):
        """删除所有表（谨慎使用）"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("数据库表已删除")
        except Exception as e:
            logger.error(f"删除数据库表失败: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        获取数据库会话（上下文管理器）
        
        Yields:
            Session: 数据库会话对象
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def get_new_session(self) -> Session:
        """
        获取新的数据库会话（需手动管理）
        
        Returns:
            Session: 数据库会话对象
        """
        return self.SessionLocal()
    
    def close(self):
        """关闭数据库引擎"""
        self.engine.dispose()
        logger.info("数据库连接已关闭")


# 全局数据库管理器实例（单例模式）
_db_manager: DatabaseManager = None


def init_db_manager(db_url: str, pool_size: int = 10, max_overflow: int = 20) -> DatabaseManager:
    """
    初始化全局数据库管理器
    
    Args:
        db_url: 数据库连接URL
        pool_size: 连接池大小
        max_overflow: 最大溢出连接数
        
    Returns:
        DatabaseManager: 数据库管理器实例
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_url, pool_size, max_overflow)
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """
    获取全局数据库管理器实例
    
    Returns:
        DatabaseManager: 数据库管理器实例
        
    Raises:
        RuntimeError: 如果数据库管理器未初始化
    """
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("数据库管理器未初始化，请先调用 init_db_manager()")
    return _db_manager
