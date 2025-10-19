import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    """機器人配置類 - 統一管理所有配置"""

    # ============ Discord 設定 ============
    DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN', '')
    DISCORD_CHANNEL_ID: str = os.getenv('DISCORD_CHANNEL_ID', '')

    # ============ Line 設定 ============
    LINE_CHANNEL_SECRET: str = os.getenv('LINE_CHANNEL_SECRET', '')
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
    LINE_GROUP_ID: str = os.getenv('LINE_GROUP_ID', '')

    # ============ Google Gemini AI 設定 ============
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')

    # ============ 伺服器設定 ============
    PORT: int = int(os.getenv('PORT', '8080'))
    HOST: str = os.getenv('HOST', '0.0.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    # ============ 配額限制 ============
    AI_DAILY_LIMIT_PER_USER: int = int(os.getenv('AI_DAILY_LIMIT', '20'))
    AI_REQUEST_PER_MINUTE: int = int(os.getenv('AI_RPM', '30'))
    LINE_MONTHLY_LIMIT: int = int(os.getenv('LINE_MONTHLY_LIMIT', '500'))
    LINE_WARNING_THRESHOLD: float = float(os.getenv('LINE_WARNING_THRESHOLD', '0.9'))

    # ============ AI 參數 ============
    AI_TEMPERATURE: float = float(os.getenv('AI_TEMPERATURE', '0.7'))
    AI_TOP_P: float = float(os.getenv('AI_TOP_P', '0.8'))
    AI_TOP_K: int = int(os.getenv('AI_TOP_K', '40'))
    AI_MAX_TOKENS: int = int(os.getenv('AI_MAX_TOKENS', '200'))

    # ============ 對話設定 ============
    CONVERSATION_TIMEOUT: int = int(os.getenv('CONVERSATION_TIMEOUT', '1800'))  # 30分鐘
    MAX_HISTORY_LENGTH: int = int(os.getenv('MAX_HISTORY', '10'))

    # ============ 相似度檢測 ============
    MESSAGE_SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.8'))
    MESSAGE_LENGTH_DIFF: int = int(os.getenv('LENGTH_DIFF', '5'))

    def validate(self):
        """驗證必要的配置是否已設定"""
        required_fields = [
            ('DISCORD_TOKEN', self.DISCORD_TOKEN),
            ('DISCORD_CHANNEL_ID', self.DISCORD_CHANNEL_ID),
            ('LINE_CHANNEL_SECRET', self.LINE_CHANNEL_SECRET),
            ('LINE_CHANNEL_ACCESS_TOKEN', self.LINE_CHANNEL_ACCESS_TOKEN),
            ('GOOGLE_API_KEY', self.GOOGLE_API_KEY),
        ]

        missing = [name for name, value in required_fields if not value]

        if missing:
            raise ValueError(f"缺少必要的環境變數: {', '.join(missing)}")

        return True

# 創建全域配置實例
config = BotConfig()

# 向後兼容 - 保留舊的變數名稱
DISCORD_TOKEN = config.DISCORD_TOKEN
DISCORD_CHANNEL_ID = config.DISCORD_CHANNEL_ID
LINE_CHANNEL_SECRET = config.LINE_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN = config.LINE_CHANNEL_ACCESS_TOKEN