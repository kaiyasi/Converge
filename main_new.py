"""
Converge 主程式 (重構版)
整合所有新模組,提供統一的入口點
"""
import asyncio
import signal
import sys
from flask import Flask
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration

from config import config
from utils.logger import setup_logging, get_logger
from models.database import get_db, close_db
from core.discord_bot import DiscordBotManager
from core.ai_engine import AIEngine
from handlers.commands import CommandHandler
from api.routes import create_api_blueprint
from api.webhook import create_webhook_blueprint
from api.dashboard import create_dashboard_blueprint

# 設定日誌
setup_logging(
    log_dir='logs',
    log_level=config.DEBUG and 'DEBUG' or 'INFO',
    enable_console=True,
    enable_file=True,
    enable_json=True
)

logger = get_logger(__name__)


class ConvergeApp:
    """Converge 應用程式主類"""

    def __init__(self):
        """初始化應用程式"""
        logger.info("=" * 60)
        logger.info("🚀 初始化 Converge")
        logger.info("=" * 60)

        # 驗證配置
        try:
            config.validate()
            logger.info("✅ 配置驗證通過")
        except ValueError as e:
            logger.error(f"❌ 配置錯誤: {e}")
            sys.exit(1)

        # 初始化 Flask
        self.flask_app = Flask(__name__)
        self.flask_app.config['SECRET_KEY'] = 'your-secret-key-here'  # TODO: 從環境變數讀取

        # 初始化資料庫
        self.db = get_db()
        logger.info("✅ 資料庫已初始化")

        # 初始化 Line Bot
        self.line_configuration = Configuration(
            access_token=config.LINE_CHANNEL_ACCESS_TOKEN
        )
        self.line_bot_api = MessagingApi(ApiClient(self.line_configuration))
        self.line_handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
        logger.info("✅ Line Bot 已初始化")

        # 初始化 Discord Bot
        self.discord_manager = DiscordBotManager()
        logger.info("✅ Discord Bot 已初始化")

        # 初始化 AI 引擎
        self.ai_engine = AIEngine()
        logger.info("✅ AI 引擎已初始化")

        # 初始化指令處理器
        self.command_handler = CommandHandler(
            discord_bot=self.discord_manager,
            line_bot_api=self.line_bot_api,
            ai_engine=self.ai_engine
        )
        logger.info("✅ 指令處理器已初始化")

        # 註冊 Flask 路由
        self._register_routes()
        logger.info("✅ Flask 路由已註冊")

        # 設定信號處理
        self._setup_signal_handlers()

    def _register_routes(self):
        """註冊 Flask 路由"""
        # Webhook 路由
        webhook_bp = create_webhook_blueprint(
            line_handler=self.line_handler,
            line_bot_api=self.line_bot_api,
            discord_manager=self.discord_manager,
            ai_engine=self.ai_engine
        )
        self.flask_app.register_blueprint(webhook_bp)

        # API 路由
        api_bp = create_api_blueprint(
            db=self.db,
            discord_manager=self.discord_manager,
            ai_engine=self.ai_engine
        )
        self.flask_app.register_blueprint(api_bp, url_prefix='/api')

        # Dashboard 路由
        dashboard_bp = create_dashboard_blueprint(
            db=self.db,
            discord_manager=self.discord_manager,
            ai_engine=self.ai_engine
        )
        self.flask_app.register_blueprint(dashboard_bp)

    def _setup_signal_handlers(self):
        """設定信號處理器 (優雅關閉)"""
        def signal_handler(sig, frame):
            logger.info(f"收到信號 {sig},開始優雅關閉...")
            self.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def run(self):
        """啟動應用程式"""
        logger.info("=" * 60)
        logger.info("🎯 啟動 Converge")
        logger.info("=" * 60)

        # 啟動 Discord Bot (在獨立線程中)
        logger.info("🤖 啟動 Discord Bot...")
        self.discord_manager.run_in_thread()

        # 等待 Discord Bot 就緒
        try:
            asyncio.run(self.discord_manager.wait_until_ready(timeout=30.0))
            logger.info("✅ Discord Bot 已就緒")
        except asyncio.TimeoutError:
            logger.error("❌ Discord Bot 啟動超時")

        # 啟動 Flask 伺服器
        logger.info(f"🌐 啟動 Flask 伺服器 (Host: {config.HOST}, Port: {config.PORT})")
        logger.info("=" * 60)
        logger.info("✨ Converge 已完全啟動")
        logger.info("=" * 60)

        self.flask_app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )

    def shutdown(self):
        """關閉應用程式"""
        logger.info("🛑 正在關閉 Converge...")

        # 關閉 Discord Bot
        try:
            asyncio.run(self.discord_manager.stop())
            logger.info("✅ Discord Bot 已停止")
        except Exception as e:
            logger.error(f"❌ 停止 Discord Bot 時發生錯誤: {e}")

        # 關閉資料庫
        try:
            close_db()
            logger.info("✅ 資料庫連接已關閉")
        except Exception as e:
            logger.error(f"❌ 關閉資料庫時發生錯誤: {e}")

        logger.info("👋 Converge 已完全關閉")


def main():
    """主函數"""
    app = ConvergeApp()
    app.run()


if __name__ == "__main__":
    main()
