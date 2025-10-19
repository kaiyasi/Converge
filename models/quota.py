"""配額管理模型"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)


class Quota:
    """配額類"""

    RESET_PERIODS = {
        'minute': timedelta(minutes=1),
        'hourly': timedelta(hours=1),
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30)  # 簡化處理
    }

    def __init__(
        self,
        user_id: str,
        quota_type: str,
        usage_count: int = 0,
        limit_count: int = 0,
        reset_period: str = 'daily',
        last_reset: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.user_id = user_id
        self.quota_type = quota_type
        self.usage_count = usage_count
        self.limit_count = limit_count
        self.reset_period = reset_period
        self.last_reset = last_reset or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_db_row(cls, row) -> 'Quota':
        """從資料庫行建立配額物件"""
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            quota_type=row['quota_type'],
            usage_count=row['usage_count'],
            limit_count=row['limit_count'],
            reset_period=row['reset_period'],
            last_reset=datetime.fromisoformat(row['last_reset']) if row['last_reset'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def save(self):
        """儲存配額到資料庫"""
        db = get_db()
        with db.get_cursor() as cursor:
            if self.id:
                cursor.execute("""
                    UPDATE quotas
                    SET usage_count = ?, limit_count = ?, last_reset = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    self.usage_count,
                    self.limit_count,
                    self.last_reset.isoformat(),
                    datetime.now().isoformat(),
                    self.id
                ))
            else:
                cursor.execute("""
                    INSERT INTO quotas
                    (user_id, quota_type, usage_count, limit_count, reset_period, last_reset, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.user_id,
                    self.quota_type,
                    self.usage_count,
                    self.limit_count,
                    self.reset_period,
                    self.last_reset.isoformat(),
                    self.created_at.isoformat(),
                    datetime.now().isoformat()
                ))
                self.id = cursor.lastrowid

    def check_and_reset(self) -> bool:
        """
        檢查並重置配額

        Returns:
            是否進行了重置
        """
        if self.reset_period not in self.RESET_PERIODS:
            logger.warning(f"未知的重置週期: {self.reset_period}")
            return False

        reset_delta = self.RESET_PERIODS[self.reset_period]
        if datetime.now() - self.last_reset > reset_delta:
            self.usage_count = 0
            self.last_reset = datetime.now()
            self.save()
            logger.info(f"重置配額: {self.user_id} - {self.quota_type}")
            return True
        return False

    def can_use(self) -> bool:
        """
        檢查是否可以使用

        Returns:
            是否還有配額
        """
        self.check_and_reset()
        return self.usage_count < self.limit_count

    def increment(self, amount: int = 1) -> bool:
        """
        增加使用次數

        Args:
            amount: 增加數量

        Returns:
            是否成功 (未超過限制)
        """
        self.check_and_reset()
        if self.usage_count + amount <= self.limit_count:
            self.usage_count += amount
            self.updated_at = datetime.now()
            self.save()
            logger.debug(f"配額使用: {self.user_id} - {self.quota_type}: {self.usage_count}/{self.limit_count}")
            return True
        else:
            logger.warning(f"配額超限: {self.user_id} - {self.quota_type}: {self.usage_count}/{self.limit_count}")
            return False

    def get_remaining(self) -> int:
        """獲取剩餘配額"""
        self.check_and_reset()
        return max(0, self.limit_count - self.usage_count)

    def get_usage_percentage(self) -> float:
        """獲取使用百分比"""
        if self.limit_count == 0:
            return 0.0
        return (self.usage_count / self.limit_count) * 100

    @classmethod
    def get_or_create(
        cls,
        user_id: str,
        quota_type: str,
        limit_count: int,
        reset_period: str = 'daily'
    ) -> 'Quota':
        """
        獲取或建立配額

        Args:
            user_id: 使用者 ID
            quota_type: 配額類型
            limit_count: 限制數量
            reset_period: 重置週期

        Returns:
            Quota 物件
        """
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM quotas
                WHERE user_id = ? AND quota_type = ? AND reset_period = ?
            """, (user_id, quota_type, reset_period))
            row = cursor.fetchone()

            if row:
                quota = cls.from_db_row(row)
                # 檢查並重置
                quota.check_and_reset()
                return quota
            else:
                quota = cls(
                    user_id=user_id,
                    quota_type=quota_type,
                    limit_count=limit_count,
                    reset_period=reset_period
                )
                quota.save()
                logger.info(f"建立新配額: {user_id} - {quota_type}")
                return quota

    @classmethod
    def get_user_quotas(cls, user_id: str) -> List['Quota']:
        """獲取使用者的所有配額"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM quotas
                WHERE user_id = ?
            """, (user_id,))
            return [cls.from_db_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_all_quotas(cls) -> List['Quota']:
        """獲取所有配額"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM quotas ORDER BY updated_at DESC")
            return [cls.from_db_row(row) for row in cursor.fetchall()]

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quota_type': self.quota_type,
            'usage_count': self.usage_count,
            'limit_count': self.limit_count,
            'remaining': self.get_remaining(),
            'usage_percentage': round(self.get_usage_percentage(), 2),
            'reset_period': self.reset_period,
            'last_reset': self.last_reset.isoformat() if self.last_reset else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Quota {self.user_id} - {self.quota_type}: {self.usage_count}/{self.limit_count}>"


class SystemQuota:
    """系統級配額 (全域配額)"""

    @staticmethod
    def get_quota(quota_type: str) -> Optional[Dict[str, Any]]:
        """獲取系統配額"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM system_quotas
                WHERE quota_type = ?
            """, (quota_type,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    def increment_usage(quota_type: str, amount: int = 1) -> bool:
        """增加系統配額使用量"""
        db = get_db()
        quota = SystemQuota.get_quota(quota_type)

        if not quota:
            logger.error(f"未找到系統配額: {quota_type}")
            return False

        # 檢查是否需要重置
        reset_period = quota['reset_period']
        last_reset = datetime.fromisoformat(quota['last_reset'])

        reset_deltas = {
            'minute': timedelta(minutes=1),
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'monthly': timedelta(days=30)
        }

        should_reset = False
        if reset_period in reset_deltas:
            if datetime.now() - last_reset > reset_deltas[reset_period]:
                should_reset = True

        with db.get_cursor() as cursor:
            if should_reset:
                cursor.execute("""
                    UPDATE system_quotas
                    SET usage_count = ?, last_reset = ?, updated_at = ?
                    WHERE quota_type = ?
                """, (amount, datetime.now().isoformat(), datetime.now().isoformat(), quota_type))
                logger.info(f"重置系統配額: {quota_type}")
            else:
                new_usage = quota['usage_count'] + amount
                if new_usage > quota['limit_count']:
                    logger.warning(f"系統配額超限: {quota_type}: {new_usage}/{quota['limit_count']}")
                    return False

                cursor.execute("""
                    UPDATE system_quotas
                    SET usage_count = usage_count + ?, updated_at = ?
                    WHERE quota_type = ?
                """, (amount, datetime.now().isoformat(), quota_type))

        return True

    @staticmethod
    def can_use(quota_type: str) -> bool:
        """檢查系統配額是否可用"""
        quota = SystemQuota.get_quota(quota_type)
        if not quota:
            return False

        # 檢查重置
        reset_period = quota['reset_period']
        last_reset = datetime.fromisoformat(quota['last_reset'])

        reset_deltas = {
            'minute': timedelta(minutes=1),
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'monthly': timedelta(days=30)
        }

        if reset_period in reset_deltas:
            if datetime.now() - last_reset > reset_deltas[reset_period]:
                return True  # 已超過重置時間,可以使用

        return quota['usage_count'] < quota['limit_count']

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """獲取所有系統配額"""
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM system_quotas")
            return [dict(row) for row in cursor.fetchall()]
