"""
Web Dashboard 路由
提供視覺化的管理介面
"""
from flask import Blueprint, render_template, jsonify
from models.database import Database
from core.discord_bot import DiscordBotManager
from core.ai_engine import AIEngine
from utils.logger import get_logger

logger = get_logger(__name__)


def create_dashboard_blueprint(
    db: Database,
    discord_manager: DiscordBotManager,
    ai_engine: AIEngine
) -> Blueprint:
    """
    建立 Dashboard Blueprint

    Args:
        db: 資料庫實例
        discord_manager: Discord 管理器
        ai_engine: AI 引擎

    Returns:
        Flask Blueprint
    """
    dashboard = Blueprint('dashboard', __name__)

    @dashboard.route('/')
    def index():
        """主頁 - 儀表板"""
        return render_template('dashboard.html')

    @dashboard.route('/users')
    def users_page():
        """使用者管理頁面"""
        return render_template('users.html')

    @dashboard.route('/messages')
    def messages_page():
        """訊息記錄頁面"""
        return render_template('messages.html')

    @dashboard.route('/settings')
    def settings_page():
        """系統設定頁面"""
        return render_template('settings.html')

    return dashboard
