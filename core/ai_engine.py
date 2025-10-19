"""
AI 引擎模組
- Gemini AI 整合
- 對話管理
- 配額控制
"""
import google.generativeai as genai
from typing import Optional, List, Dict
from models.quota import Quota, SystemQuota
from models.user import User
from utils.logger import get_logger
from utils.retry import retry_with_backoff
from config import config

logger = get_logger(__name__)


class AIEngine:
    """AI 引擎類"""

    def __init__(self):
        """初始化 AI 引擎"""
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("AI 引擎已初始化")

    @retry_with_backoff(
        max_retries=3,
        base_delay=2.0,
        exceptions=(Exception,)
    )
    async def generate_response(
        self,
        user_id: str,
        message: str,
        platform: str = 'line'
    ) -> Optional[str]:
        """
        生成 AI 回應

        Args:
            user_id: 使用者 ID
            message: 訊息內容
            platform: 平台名稱

        Returns:
            AI 回應或 None
        """
        try:
            # 檢查系統配額
            if not SystemQuota.can_use('gemini_rpm'):
                logger.warning("Gemini API 配額已達上限")
                return "系統繁忙,請稍後再試。"

            # 檢查使用者配額
            quota = Quota.get_or_create(
                user_id=user_id,
                quota_type='ai_daily',
                limit_count=config.AI_DAILY_LIMIT_PER_USER,
                reset_period='daily'
            )

            if not quota.can_use():
                logger.info(f"使用者 {user_id} AI 配額已用盡")
                return f"今日 AI 對話次數已達上限 ({quota.limit_count} 次),明日重置。"

            # 確保使用者存在
            user = User.get_or_create(user_id=user_id, platform=platform)

            # 生成回應
            logger.info(f"生成 AI 回應: {user_id}")

            response = self.model.generate_content(
                f"請用繁體中文回答以下問題,保持簡潔:\n{message}",
                generation_config={
                    "temperature": config.AI_TEMPERATURE,
                    "top_p": config.AI_TOP_P,
                    "top_k": config.AI_TOP_K,
                    "max_output_tokens": config.AI_MAX_TOKENS,
                }
            )

            # 增加配額使用
            quota.increment()
            SystemQuota.increment_usage('gemini_rpm')

            # 記錄到資料庫
            from models.message import Message
            Message(
                message_id=f"ai_req_{user_id}_{int(__import__('time').time())}",
                user_id=user_id,
                platform=platform,
                content=message,
                message_type='ai_request'
            ).save()

            Message(
                message_id=f"ai_resp_{user_id}_{int(__import__('time').time())}",
                user_id=user_id,
                platform='ai',
                content=response.text,
                message_type='ai_response'
            ).save()

            logger.info(f"AI 回應成功: {user_id}")
            return response.text

        except Exception as e:
            logger.exception(f"生成 AI 回應時發生錯誤: {e}")
            return "AI 助手暫時無法回應,請稍後再試。"

    def get_user_quota_info(self, user_id: str) -> Dict:
        """
        獲取使用者配額資訊

        Args:
            user_id: 使用者 ID

        Returns:
            配額資訊字典
        """
        quota = Quota.get_or_create(
            user_id=user_id,
            quota_type='ai_daily',
            limit_count=config.AI_DAILY_LIMIT_PER_USER,
            reset_period='daily'
        )

        return {
            'used': quota.usage_count,
            'limit': quota.limit_count,
            'remaining': quota.get_remaining(),
            'percentage': quota.get_usage_percentage()
        }

    @staticmethod
    def get_system_quota_info() -> Dict:
        """
        獲取系統配額資訊

        Returns:
            系統配額資訊
        """
        line_quota = SystemQuota.get_quota('line_monthly')
        gemini_quota = SystemQuota.get_quota('gemini_rpm')

        return {
            'line': line_quota,
            'gemini': gemini_quota
        }
