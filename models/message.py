"""訊息資料模型"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)


class Message:
    """訊息類"""

    def __init__(
        self,
        message_id: str,
        user_id: str,
        platform: str,
        content: Optional[str] = None,
        message_type: str = 'text',
        group_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.message_id = message_id
        self.user_id = user_id
        self.platform = platform
        self.content = content
        self.message_type = message_type
        self.group_id = group_id
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}

    @classmethod
    def from_db_row(cls, row) -> 'Message':
        """從資料庫行建立訊息物件"""
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        return cls(
            id=row['id'],
            message_id=row['message_id'],
            user_id=row['user_id'],
            platform=row['platform'],
            content=row['content'],
            message_type=row['message_type'],
            group_id=row['group_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            metadata=metadata
        )

    def save(self):
        """儲存訊息到資料庫"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR IGNORE INTO messages
                (message_id, user_id, platform, content, message_type, group_id, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.message_id,
                self.user_id,
                self.platform,
                self.content,
                self.message_type,
                self.group_id,
                self.created_at.isoformat(),
                json.dumps(self.metadata, ensure_ascii=False)
            ))
        logger.debug(f"儲存訊息: {self.message_id} ({self.platform})")

    @classmethod
    def get_by_id(cls, message_id: str) -> Optional['Message']:
        """
        根據 ID 獲取訊息

        Args:
            message_id: 訊息 ID

        Returns:
            Message 物件或 None
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM messages
                WHERE message_id = ?
            """, (message_id,))
            row = cursor.fetchone()
            return cls.from_db_row(row) if row else None

    @classmethod
    def get_user_messages(
        cls,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List['Message']:
        """
        獲取使用者的訊息

        Args:
            user_id: 使用者 ID
            limit: 限制數量
            offset: 偏移量

        Returns:
            訊息列表
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM messages
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [cls.from_db_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_group_messages(
        cls,
        group_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List['Message']:
        """
        獲取群組的訊息

        Args:
            group_id: 群組 ID
            limit: 限制數量
            offset: 偏移量

        Returns:
            訊息列表
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM messages
                WHERE group_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (group_id, limit, offset))
            return [cls.from_db_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_recent_messages(cls, limit: int = 100) -> List['Message']:
        """
        獲取最近的訊息

        Args:
            limit: 限制數量

        Returns:
            訊息列表
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM messages
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return [cls.from_db_row(row) for row in cursor.fetchall()]

    @classmethod
    def search(
        cls,
        keyword: str,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> List['Message']:
        """
        搜尋訊息

        Args:
            keyword: 關鍵字
            platform: 篩選平台
            limit: 限制數量

        Returns:
            訊息列表
        """
        db = get_db()
        with db.get_cursor() as cursor:
            if platform:
                cursor.execute("""
                    SELECT * FROM messages
                    WHERE content LIKE ? AND platform = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f'%{keyword}%', platform, limit))
            else:
                cursor.execute("""
                    SELECT * FROM messages
                    WHERE content LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f'%{keyword}%', limit))

            return [cls.from_db_row(row) for row in cursor.fetchall()]

    @classmethod
    def count_by_user(cls, user_id: str) -> int:
        """統計使用者訊息數量"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()[0]

    @classmethod
    def count_by_platform(cls, platform: str) -> int:
        """統計平台訊息數量"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE platform = ?
            """, (platform,))
            return cursor.fetchone()[0]

    @classmethod
    def delete_old_messages(cls, days: int = 30) -> int:
        """
        刪除舊訊息

        Args:
            days: 保留天數

        Returns:
            刪除的訊息數量
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM messages
                WHERE created_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            deleted_count = cursor.rowcount
        logger.info(f"刪除 {deleted_count} 條超過 {days} 天的訊息")
        return deleted_count

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'platform': self.platform,
            'content': self.content,
            'message_type': self.message_type,
            'group_id': self.group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata
        }

    def __repr__(self):
        return f"<Message {self.message_id} from {self.user_id}@{self.platform}>"
