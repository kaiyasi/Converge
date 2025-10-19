"""使用者資料模型"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)


class User:
    """使用者類"""

    def __init__(
        self,
        user_id: str,
        platform: str,
        display_name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.platform = platform
        self.display_name = display_name
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_active = is_active
        self.metadata = metadata or {}

    @classmethod
    def from_db_row(cls, row) -> 'User':
        """從資料庫行建立使用者物件"""
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        return cls(
            user_id=row['user_id'],
            platform=row['platform'],
            display_name=row['display_name'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            is_active=bool(row['is_active']),
            metadata=metadata
        )

    def save(self):
        """儲存使用者到資料庫"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO users
                (user_id, platform, display_name, created_at, updated_at, is_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id,
                self.platform,
                self.display_name,
                self.created_at.isoformat(),
                datetime.now().isoformat(),
                self.is_active,
                json.dumps(self.metadata, ensure_ascii=False)
            ))
        logger.debug(f"儲存使用者: {self.user_id} ({self.platform})")

    def update(self, **kwargs):
        """更新使用者資料"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.save()

    def delete(self):
        """刪除使用者 (軟刪除)"""
        self.is_active = False
        self.save()
        logger.info(f"停用使用者: {self.user_id}")

    @classmethod
    def get_by_id(cls, user_id: str, platform: str) -> Optional['User']:
        """
        根據 ID 和平台獲取使用者

        Args:
            user_id: 使用者 ID
            platform: 平台名稱

        Returns:
            User 物件或 None
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                WHERE user_id = ? AND platform = ?
            """, (user_id, platform))
            row = cursor.fetchone()
            return cls.from_db_row(row) if row else None

    @classmethod
    def get_or_create(cls, user_id: str, platform: str, **kwargs) -> 'User':
        """
        獲取或建立使用者

        Args:
            user_id: 使用者 ID
            platform: 平台名稱
            **kwargs: 其他使用者屬性

        Returns:
            User 物件
        """
        user = cls.get_by_id(user_id, platform)
        if user is None:
            user = cls(user_id=user_id, platform=platform, **kwargs)
            user.save()
            logger.info(f"建立新使用者: {user_id} ({platform})")
        return user

    @classmethod
    def get_all(cls, platform: Optional[str] = None, is_active: bool = True) -> List['User']:
        """
        獲取所有使用者

        Args:
            platform: 篩選平台 (None 表示所有平台)
            is_active: 只獲取活躍使用者

        Returns:
            使用者列表
        """
        db = get_db()
        with db.get_cursor() as cursor:
            if platform:
                cursor.execute("""
                    SELECT * FROM users
                    WHERE platform = ? AND is_active = ?
                    ORDER BY created_at DESC
                """, (platform, is_active))
            else:
                cursor.execute("""
                    SELECT * FROM users
                    WHERE is_active = ?
                    ORDER BY created_at DESC
                """, (is_active,))

            return [cls.from_db_row(row) for row in cursor.fetchall()]

    @classmethod
    def count(cls, platform: Optional[str] = None, is_active: bool = True) -> int:
        """
        統計使用者數量

        Args:
            platform: 篩選平台
            is_active: 只統計活躍使用者

        Returns:
            使用者數量
        """
        db = get_db()
        with db.get_cursor() as cursor:
            if platform:
                cursor.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE platform = ? AND is_active = ?
                """, (platform, is_active))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE is_active = ?
                """, (is_active,))

            return cursor.fetchone()[0]

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'user_id': self.user_id,
            'platform': self.platform,
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'metadata': self.metadata
        }

    def __repr__(self):
        return f"<User {self.user_id}@{self.platform}>"
