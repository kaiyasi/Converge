"""
待處理訊息佇列模型
"""
from datetime import datetime
from typing import List, Dict, Any
from .database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)


class QueuedMessage:
    """待處理訊息類"""

    def __init__(
        self,
        source_platform: str,
        source_user_name: str,
        content: str,
        created_at: datetime = None,
        status: str = 'queued',
        id: int = None
    ):
        self.id = id
        self.source_platform = source_platform
        self.source_user_name = source_user_name
        self.content = content
        self.created_at = created_at or datetime.now()
        self.status = status

    def save(self):
        """儲存到資料庫"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO queued_messages
                (source_platform, source_user_name, content, created_at, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.source_platform,
                self.source_user_name,
                self.content,
                self.created_at.isoformat(),
                self.status
            ))
            self.id = cursor.lastrowid
            logger.info(f"新增待處理訊息到佇列: {self.id}")

    @classmethod
    def get_queued_messages(cls, limit: int = 10) -> List['QueuedMessage']:
        """獲取佇列中待處理的訊息"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM queued_messages
                WHERE status = 'queued'
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [cls._from_row(row) for row in rows]

    @classmethod
    def mark_as_sent(cls, ids: List[int]):
        """將訊息標記為已發送"""
        if not ids:
            return

        db = get_db()
        with db.get_cursor() as cursor:
            placeholders = ', '.join('?' for _ in ids)
            cursor.execute(f"""
                UPDATE queued_messages
                SET status = 'sent'
                WHERE id IN ({placeholders})
            """, ids)
            logger.info(f"標記 {len(ids)} 則訊息為已發送")

    @classmethod
    def _from_row(cls, row: Dict[str, Any]) -> 'QueuedMessage':
        """從資料庫行建立物件"""
        return cls(
            id=row['id'],
            source_platform=row['source_platform'],
            source_user_name=row['source_user_name'],
            content=row['content'],
            created_at=datetime.fromisoformat(row['created_at']),
            status=row['status']
        )
