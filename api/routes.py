"""
REST API 路由
提供系統資訊、統計、管理功能的 API 端點
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import psutil
import os
from models.database import Database
from models.user import User
from models.message import Message
from models.quota import Quota, SystemQuota
from core.discord_bot import DiscordBotManager
from core.ai_engine import AIEngine
from utils.logger import get_logger

logger = get_logger(__name__)


def create_api_blueprint(db: Database, discord_manager: DiscordBotManager, ai_engine: AIEngine) -> Blueprint:
    """
    建立 API Blueprint

    Args:
        db: 資料庫實例
        discord_manager: Discord 管理器
        ai_engine: AI 引擎

    Returns:
        Flask Blueprint
    """
    api = Blueprint('api', __name__)

    # ==================== 健康檢查 ====================

    @api.route('/health', methods=['GET'])
    def health_check():
        """健康檢查端點"""
        try:
            # 檢查資料庫
            db_healthy = False
            try:
                with db.get_cursor() as cursor:
                    cursor.execute("SELECT 1")
                    db_healthy = True
            except Exception as e:
                logger.error(f"資料庫健康檢查失敗: {e}")

            # 檢查 Discord Bot
            discord_healthy = discord_manager.is_ready

            # 整體健康狀態
            healthy = db_healthy and discord_healthy

            return jsonify({
                'status': 'healthy' if healthy else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'checks': {
                    'database': 'ok' if db_healthy else 'error',
                    'discord_bot': 'ok' if discord_healthy else 'error',
                    'ai_engine': 'ok'
                }
            }), 200 if healthy else 503

        except Exception as e:
            logger.exception("健康檢查時發生錯誤")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    @api.route('/metrics', methods=['GET'])
    def metrics():
        """Prometheus 格式的指標端點"""
        try:
            # 系統指標
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # 資料庫統計
            stats = db.get_stats()

            # 配額資訊
            quota_info = SystemQuota.get_all()

            # 生成 Prometheus 格式
            metrics_output = []

            # 系統指標
            metrics_output.append(f"# HELP system_cpu_percent CPU 使用率")
            metrics_output.append(f"# TYPE system_cpu_percent gauge")
            metrics_output.append(f"system_cpu_percent {cpu_percent}")

            metrics_output.append(f"# HELP system_memory_percent 記憶體使用率")
            metrics_output.append(f"# TYPE system_memory_percent gauge")
            metrics_output.append(f"system_memory_percent {memory.percent}")

            metrics_output.append(f"# HELP system_disk_percent 磁碟使用率")
            metrics_output.append(f"# TYPE system_disk_percent gauge")
            metrics_output.append(f"system_disk_percent {disk.percent}")

            # 業務指標
            metrics_output.append(f"# HELP total_users 總使用者數")
            metrics_output.append(f"# TYPE total_users gauge")
            metrics_output.append(f"total_users {stats['total_users']}")

            metrics_output.append(f"# HELP total_messages 總訊息數")
            metrics_output.append(f"# TYPE total_messages counter")
            metrics_output.append(f"total_messages {stats['total_messages']}")

            # 配額指標
            for quota in quota_info:
                quota_type = quota['quota_type']
                metrics_output.append(f"# HELP quota_{quota_type}_usage {quota_type} 使用量")
                metrics_output.append(f"# TYPE quota_{quota_type}_usage gauge")
                metrics_output.append(f"quota_{quota_type}_usage {quota['usage_count']}")

                metrics_output.append(f"# HELP quota_{quota_type}_limit {quota_type} 限制")
                metrics_output.append(f"# TYPE quota_{quota_type}_limit gauge")
                metrics_output.append(f"quota_{quota_type}_limit {quota['limit_count']}")

            return '\n'.join(metrics_output), 200, {'Content-Type': 'text/plain; charset=utf-8'}

        except Exception as e:
            logger.exception("獲取指標時發生錯誤")
            return str(e), 500

    # ==================== 統計資訊 ====================

    @api.route('/stats', methods=['GET'])
    def get_stats():
        """獲取統計資訊"""
        try:
            stats = db.get_stats()

            # 平台統計
            line_users = User.count(platform='line')
            discord_users = User.count(platform='discord')
            line_messages = Message.count_by_platform('line')
            discord_messages = Message.count_by_platform('discord')

            # 今日統計
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE date(created_at) = date('now')
                """)
                today_messages = cursor.fetchone()[0]

            # 配額資訊
            quotas = SystemQuota.get_all()

            return jsonify({
                'database': stats,
                'platforms': {
                    'line': {
                        'users': line_users,
                        'messages': line_messages
                    },
                    'discord': {
                        'users': discord_users,
                        'messages': discord_messages
                    }
                },
                'today': {
                    'messages': today_messages
                },
                'quotas': quotas,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.exception("獲取統計資訊時發生錯誤")
            return jsonify({'error': str(e)}), 500

    @api.route('/stats/chart', methods=['GET'])
    def get_chart_data():
        """獲取圖表數據"""
        try:
            days = int(request.args.get('days', 7))

            with db.get_cursor() as cursor:
                # 每日訊息統計
                cursor.execute("""
                    SELECT date(created_at) as date, COUNT(*) as count
                    FROM messages
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY date(created_at)
                    ORDER BY date
                """, (days,))
                daily_messages = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

                # 平台分布
                cursor.execute("""
                    SELECT platform, COUNT(*) as count
                    FROM messages
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY platform
                """, (days,))
                platform_distribution = [{'platform': row[0], 'count': row[1]} for row in cursor.fetchall()]

                # 每小時訊息統計 (最近24小時)
                cursor.execute("""
                    SELECT strftime('%H', created_at) as hour, COUNT(*) as count
                    FROM messages
                    WHERE created_at >= datetime('now', '-1 day')
                    GROUP BY hour
                    ORDER BY hour
                """)
                hourly_messages = [{'hour': row[0], 'count': row[1]} for row in cursor.fetchall()]

            return jsonify({
                'daily_messages': daily_messages,
                'platform_distribution': platform_distribution,
                'hourly_messages': hourly_messages
            })

        except Exception as e:
            logger.exception("獲取圖表數據時發生錯誤")
            return jsonify({'error': str(e)}), 500

    # ==================== 使用者管理 ====================

    @api.route('/users', methods=['GET'])
    def get_users():
        """獲取使用者列表"""
        try:
            platform = request.args.get('platform')
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))

            if platform:
                users = User.get_all(platform=platform)
            else:
                users = User.get_all()

            # 分頁
            paginated_users = users[offset:offset + limit]

            return jsonify({
                'users': [user.to_dict() for user in paginated_users],
                'total': len(users),
                'limit': limit,
                'offset': offset
            })

        except Exception as e:
            logger.exception("獲取使用者列表時發生錯誤")
            return jsonify({'error': str(e)}), 500

    @api.route('/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        """獲取特定使用者資訊"""
        try:
            platform = request.args.get('platform', 'line')
            user = User.get_by_id(user_id, platform)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # 獲取使用者的訊息統計
            message_count = Message.count_by_user(user_id)

            # 獲取使用者的配額資訊
            quotas = Quota.get_user_quotas(user_id)

            return jsonify({
                'user': user.to_dict(),
                'message_count': message_count,
                'quotas': [q.to_dict() for q in quotas]
            })

        except Exception as e:
            logger.exception("獲取使用者資訊時發生錯誤")
            return jsonify({'error': str(e)}), 500

    # ==================== 訊息管理 ====================

    @api.route('/messages', methods=['GET'])
    def get_messages():
        """獲取訊息列表"""
        try:
            limit = int(request.args.get('limit', 50))
            keyword = request.args.get('keyword')
            platform = request.args.get('platform')

            if keyword:
                messages = Message.search(keyword, platform, limit)
            else:
                messages = Message.get_recent_messages(limit)

            return jsonify({
                'messages': [msg.to_dict() for msg in messages],
                'count': len(messages)
            })

        except Exception as e:
            logger.exception("獲取訊息列表時發生錯誤")
            return jsonify({'error': str(e)}), 500

    # ==================== 系統資訊 ====================

    @api.route('/system', methods=['GET'])
    def get_system_info():
        """獲取系統資訊"""
        try:
            # 系統資源
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Discord Bot 資訊
            discord_info = {
                'ready': discord_manager.is_ready,
                'latency': discord_manager.latency if discord_manager.is_ready else None,
                'user': str(discord_manager.user) if discord_manager.user else None
            }

            # 進程資訊
            process = psutil.Process()
            process_info = {
                'pid': process.pid,
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'threads': process.num_threads(),
                'uptime_seconds': int((datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds())
            }

            return jsonify({
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / 1024 / 1024,
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / 1024 / 1024 / 1024
                },
                'discord': discord_info,
                'process': process_info,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.exception("獲取系統資訊時發生錯誤")
            return jsonify({'error': str(e)}), 500

    return api
