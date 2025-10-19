"""
資料庫管理模組
- SQLite 連接管理
- 資料庫初始化
- 遷移管理
"""
import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
from utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """資料庫管理類"""

    def __init__(self, db_path: str = 'data/bot.db'):
        """
        初始化資料庫

        Args:
            db_path: 資料庫檔案路徑
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._connection: Optional[sqlite3.Connection] = None
        self.init_database()

    def _ensure_db_directory(self):
        """確保資料庫目錄存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"建立資料庫目錄: {db_dir}")

    def get_connection(self) -> sqlite3.Connection:
        """
        獲取資料庫連接

        Returns:
            SQLite 連接物件
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0
            )
            self._connection.row_factory = sqlite3.Row
            # 啟用外鍵約束
            self._connection.execute("PRAGMA foreign_keys = ON")
            logger.debug(f"建立資料庫連接: {self.db_path}")
        return self._connection

    @contextmanager
    def get_cursor(self):
        """
        獲取資料庫游標 (上下文管理器)

        Yields:
            SQLite 游標
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"資料庫操作失敗: {e}")
            raise
        finally:
            cursor.close()

    def init_database(self):
        """初始化資料庫表結構"""
        logger.info("初始化資料庫表結構")

        with self.get_cursor() as cursor:
            # 使用者表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    display_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT
                )
            """)

            # 訊息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    user_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    group_id TEXT,
                    content TEXT,
                    message_type TEXT DEFAULT 'text',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # 建立訊息索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_user_id
                ON messages (user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_created_at
                ON messages (created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_group_id
                ON messages (group_id)
            """)

            # 對話歷史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # 建立對話歷史索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_history_user_id
                ON chat_history (user_id, created_at DESC)
            """)

            # 配額表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    quota_type TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    limit_count INTEGER NOT NULL,
                    reset_period TEXT NOT NULL,
                    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE (user_id, quota_type, reset_period)
                )
            """)

            # 建立配額索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_quotas_user_type
                ON quotas (user_id, quota_type)
            """)

            # 系統配額表 (全域配額)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_quotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quota_type TEXT UNIQUE NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    limit_count INTEGER NOT NULL,
                    reset_period TEXT NOT NULL,
                    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 初始化系統配額
            cursor.execute("""
                INSERT OR IGNORE INTO system_quotas
                (quota_type, usage_count, limit_count, reset_period)
                VALUES
                ('line_monthly', 0, 500, 'monthly'),
                ('gemini_rpm', 0, 30, 'minute')
            """)

            # 群組配對表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_channel_id TEXT NOT NULL,
                    line_group_id TEXT NOT NULL,
                    name TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (discord_channel_id, line_group_id)
                )
            """)

            # 待處理訊息佇列
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS queued_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_platform TEXT NOT NULL,
                    source_user_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'queued'
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_queued_messages_status
                ON queued_messages (status, created_at)
            """)

            # 版本表 (用於資料庫遷移)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)

            # 記錄當前版本
            cursor.execute("""
                INSERT OR IGNORE INTO schema_version (version, description)
                VALUES (1, 'Initial schema')
            """)

        logger.info("資料庫初始化完成")

    def close(self):
        """關閉資料庫連接"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("資料庫連接已關閉")

    def vacuum(self):
        """優化資料庫"""
        logger.info("開始優化資料庫")
        with self.get_cursor() as cursor:
            cursor.execute("VACUUM")
        logger.info("資料庫優化完成")

    def backup(self, backup_path: str):
        """
        備份資料庫

        Args:
            backup_path: 備份檔案路徑
        """
        logger.info(f"備份資料庫到: {backup_path}")
        import shutil

        # 確保備份目錄存在
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        shutil.copy2(self.db_path, backup_path)
        logger.info("資料庫備份完成")

    def get_stats(self) -> dict:
        """
        獲取資料庫統計資訊

        Returns:
            統計資訊字典
        """
        with self.get_cursor() as cursor:
            stats = {}

            # 使用者數量
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]

            # 訊息數量
            cursor.execute("SELECT COUNT(*) FROM messages")
            stats['total_messages'] = cursor.fetchone()[0]

            # 對話歷史數量
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            stats['total_chat_history'] = cursor.fetchone()[0]

            # 群組配對數量
            cursor.execute("SELECT COUNT(*) FROM group_mappings WHERE is_active = 1")
            stats['active_group_mappings'] = cursor.fetchone()[0]

            # 資料庫大小
            stats['db_size_bytes'] = os.path.getsize(self.db_path)
            stats['db_size_mb'] = round(stats['db_size_bytes'] / 1024 / 1024, 2)

        return stats


# 全域資料庫實例
_db_instance: Optional[Database] = None


def get_db(db_path: str = 'data/bot.db') -> Database:
    """
    獲取全域資料庫實例

    Args:
        db_path: 資料庫路徑

    Returns:
        Database 實例
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


def close_db():
    """關閉全域資料庫連接"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
