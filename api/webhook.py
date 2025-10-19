"""
Webhook 路由處理
處理 Line Webhook 和其他外部 Webhook 事件
"""
from flask import Blueprint, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent, VideoMessageContent, AudioMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import PushMessageRequest, TextMessage
import asyncio
from datetime import datetime

from core.discord_bot import DiscordBotManager
from core.ai_engine import AIEngine
from services.message_processor import MessageProcessor
from models.message import Message
from models.user import User
from utils.logger import get_logger

logger = get_logger(__name__)


def create_webhook_blueprint(
    line_handler: WebhookHandler,
    line_bot_api: MessagingApi,
    discord_manager: DiscordBotManager,
    ai_engine: AIEngine
) -> Blueprint:
    """
    建立 Webhook Blueprint

    Args:
        line_handler: Line Webhook Handler
        line_bot_api: Line Bot API
        discord_manager: Discord 管理器
        ai_engine: AI 引擎

    Returns:
        Flask Blueprint
    """
    webhook = Blueprint('webhook', __name__)

    # ==================== Line Webhook ====================

    @webhook.route('/callback', methods=['POST'])
    def line_callback():
        """Line Webhook 回調端點"""
        signature = request.headers.get('X-Line-Signature', '')
        body = request.get_data(as_text=True)

        logger.info("收到 Line Webhook 請求")

        try:
            line_handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("Line Webhook 簽名驗證失敗")
            abort(400)
        except Exception as e:
            logger.exception(f"處理 Line Webhook 時發生錯誤: {e}")
            return str(e), 500

        return 'OK', 200

    # ==================== Line 事件處理器 ====================

    @line_handler.add(MessageEvent, message=TextMessageContent)
    def handle_text_message(event):
        """處理文字訊息"""
        try:
            user_id = event.source.user_id
            group_id = getattr(event.source, 'group_id', None)
            message_text = event.message.text

            logger.info(f"收到 Line 文字訊息: {message_text[:50]}...")

            # 檢查是否為指令
            if message_text.startswith('#'):
                if message_text == '#訊息更新':
                    from models.queued_message import QueuedMessage
                    queued_messages = QueuedMessage.get_queued_messages(limit=10)
                    if not queued_messages:
                        response_text = "目前沒有待處理的訊息。"
                    else:
                        response_text = "待處理的訊息：\n\n"
                        for msg in queued_messages:
                            response_text += f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.source_user_name}: {msg.content}\n"
                        
                        ids_to_mark_sent = [msg.id for msg in queued_messages]
                        QueuedMessage.mark_as_sent(ids_to_mark_sent)

                    request_obj = PushMessageRequest(
                        to=group_id or user_id,
                        messages=[TextMessage(type='text', text=response_text)]
                    )
                    line_bot_api.push_message(request_obj)
                    return
                else:
                    from handlers.commands import CommandHandler
                    cmd_handler = CommandHandler(discord_manager, line_bot_api, ai_engine)
                    result = cmd_handler.process_line_command(message_text)

                    if result:
                        request_obj = PushMessageRequest(
                            to=user_id,
                            messages=[TextMessage(type='text', text=result['content'])]
                        )
                        line_bot_api.push_message(request_obj)
                    return

            # 私訊 - AI 對話
            if event.source.type == 'user':
                logger.info(f"處理 AI 對話: {user_id}")
                response = asyncio.run(ai_engine.generate_response(
                    user_id=user_id,
                    message=message_text,
                    platform='line'
                ))

                if response:
                    from models.quota import SystemQuota
                    from models.queued_message import QueuedMessage

                    if SystemQuota.can_use('line_monthly'):
                        request_obj = PushMessageRequest(
                            to=user_id,
                            messages=[TextMessage(type='text', text=f"🤖 {response}")]
                        )
                        line_bot_api.push_message(request_obj)
                        SystemQuota.increment_usage('line_monthly')
                    else:
                        # 配額不足，將訊息存入佇列
                        print("Line quota exceeded. Queuing AI response.")
                        queued_msg = QueuedMessage(
                            source_platform='ai',
                            source_user_name='Converge AI',
                            content=response
                        )
                        queued_msg.save()

            # 群組訊息 - 轉發到 Discord
            elif event.source.type == 'group':
                processed = asyncio.run(MessageProcessor.process_line_message(event, line_bot_api))

                if processed and discord_manager.is_ready:
                    from config import config
                    channel = discord_manager.get_channel(int(config.DISCORD_CHANNEL_ID))

                    if channel:
                        message_content = MessageProcessor.format_discord_message(
                            author_name=processed['user_name'],
                            content=processed['content'],
                            message_type=processed['message_type']
                        )

                        asyncio.run_coroutine_threadsafe(
                            channel.send(message_content),
                            discord_manager.bot.loop
                        )

                        # 儲存到資料庫
                        asyncio.run(MessageProcessor.save_message_to_db(
                            message_id=event.message.id,
                            user_id=user_id,
                            platform='line',
                            content=message_text,
                            message_type='text',
                            group_id=group_id
                        ))

        except Exception as e:
            logger.exception(f"處理 Line 文字訊息時發生錯誤: {e}")

    @line_handler.add(MessageEvent, message=ImageMessageContent)
    def handle_image_message(event):
        """處理圖片訊息"""
        try:
            user_id = event.source.user_id
            group_id = getattr(event.source, 'group_id', None)

            logger.info(f"收到 Line 圖片訊息: {event.message.id}")

            # 只處理群組訊息
            if event.source.type == 'group':
                processed = asyncio.run(MessageProcessor.process_line_message(event, line_bot_api))

                if processed and discord_manager.is_ready:
                    from config import config
                    channel = discord_manager.get_channel(int(config.DISCORD_CHANNEL_ID))

                    if channel:
                        message_content = f"📷 LINE - {processed['user_name']} 發送了圖片"

                        asyncio.run_coroutine_threadsafe(
                            channel.send(message_content),
                            discord_manager.bot.loop
                        )

                        # 儲存到資料庫
                        asyncio.run(MessageProcessor.save_message_to_db(
                            message_id=event.message.id,
                            user_id=user_id,
                            platform='line',
                            content='[圖片]',
                            message_type='image',
                            group_id=group_id
                        ))

        except Exception as e:
            logger.exception(f"處理 Line 圖片訊息時發生錯誤: {e}")

    # ==================== GitHub Webhook ====================

    @webhook.route('/github', methods=['POST'])
    def github_webhook():
        """GitHub Webhook 端點"""
        try:
            event_type = request.headers.get('X-GitHub-Event')
            payload = request.json

            logger.info(f"收到 GitHub Webhook: {event_type}")

            if not discord_manager.is_ready:
                return jsonify({'status': 'Discord bot not ready'}), 503

            from config import config
            channel = discord_manager.get_channel(int(config.DISCORD_CHANNEL_ID))

            if not channel:
                return jsonify({'status': 'Channel not found'}), 404

            # 處理不同的事件類型
            message = None

            if event_type == 'push':
                repo = payload.get('repository', {}).get('full_name', 'Unknown')
                pusher = payload.get('pusher', {}).get('name', 'Unknown')
                commits = payload.get('commits', [])
                branch = payload.get('ref', '').split('/')[-1]

                message = (
                    f"🔔 **GitHub Push 通知**\n"
                    f"📦 倉庫: `{repo}`\n"
                    f"🌿 分支: `{branch}`\n"
                    f"👤 推送者: {pusher}\n"
                    f"📝 提交數量: {len(commits)}"
                )

            elif event_type == 'pull_request':
                action = payload.get('action')
                pr = payload.get('pull_request', {})
                title = pr.get('title', 'Unknown')
                user = pr.get('user', {}).get('login', 'Unknown')
                number = pr.get('number', 0)

                message = (
                    f"🔔 **GitHub PR 通知**\n"
                    f"📋 動作: {action}\n"
                    f"#️⃣ PR #{number}: {title}\n"
                    f"👤 作者: {user}"
                )

            elif event_type == 'issues':
                action = payload.get('action')
                issue = payload.get('issue', {})
                title = issue.get('title', 'Unknown')
                user = issue.get('user', {}).get('login', 'Unknown')
                number = issue.get('number', 0)

                message = (
                    f"🔔 **GitHub Issue 通知**\n"
                    f"📋 動作: {action}\n"
                    f"#️⃣ Issue #{number}: {title}\n"
                    f"👤 作者: {user}"
                )

            if message:
                asyncio.run_coroutine_threadsafe(
                    channel.send(message),
                    discord_manager.bot.loop
                )

            return jsonify({'status': 'success'}), 200

        except Exception as e:
            logger.exception(f"處理 GitHub Webhook 時發生錯誤: {e}")
            return jsonify({'error': str(e)}), 500

    # ==================== 自訂 Webhook ====================

    @webhook.route('/custom', methods=['POST'])
    def custom_webhook():
        """自訂 Webhook 端點 - 接收外部事件並轉發"""
        try:
            data = request.json
            auth_token = request.headers.get('Authorization')

            # TODO: 驗證 token

            message = data.get('message')
            platform = data.get('platform', 'discord')  # discord 或 line
            target = data.get('target')  # channel_id 或 user_id

            if not message:
                return jsonify({'error': 'Missing message'}), 400

            if platform == 'discord':
                if not discord_manager.is_ready:
                    return jsonify({'error': 'Discord bot not ready'}), 503

                channel_id = target or int(config.DISCORD_CHANNEL_ID)
                channel = discord_manager.get_channel(channel_id)

                if not channel:
                    return jsonify({'error': 'Channel not found'}), 404

                asyncio.run_coroutine_threadsafe(
                    channel.send(f"📨 {message}"),
                    discord_manager.bot.loop
                )

            elif platform == 'line':
                if not target:
                    return jsonify({'error': 'Missing target user_id'}), 400

                request_obj = PushMessageRequest(
                    to=target,
                    messages=[TextMessage(type='text', text=f"📨 {message}")]
                )
                line_bot_api.push_message(request_obj)

            else:
                return jsonify({'error': 'Invalid platform'}), 400

            return jsonify({'status': 'success'}), 200

        except Exception as e:
            logger.exception(f"處理自訂 Webhook 時發生錯誤: {e}")
            return jsonify({'error': str(e)}), 500

    return webhook
