"""
訊息處理服務
- 訊息轉換
- 訊息格式化
- 平台適配
"""
from typing import List, Dict, Any, Optional
import discord
from linebot.v3.messaging import TextMessage, ImageMessage, VideoMessage, AudioMessage
from services.media_handler import MediaHandler
from models.message import Message
from models.user import User
from utils.logger import get_logger

logger = get_logger(__name__)


class MessageProcessor:
    """訊息處理器"""

    @staticmethod
    async def process_discord_message(
        message: discord.Message
    ) -> List[Dict[str, Any]]:
        """
        處理 Discord 訊息,轉換為統一格式

        Args:
            message: Discord 訊息物件

        Returns:
            訊息列表 (可能包含多個部分)
        """
        messages = []

        # 處理文字內容
        if message.content:
            messages.append({
                'type': 'text',
                'content': message.content,
                'author': message.author.name,
                'author_id': str(message.author.id)
            })

        # 處理附件
        for attachment in message.attachments:
            attachment_info = await MediaHandler.process_discord_attachment(attachment)

            if not attachment_info['supported']:
                logger.warning(f"不支援的檔案類型: {attachment.filename}")
                messages.append({
                    'type': 'text',
                    'content': f"[不支援的檔案: {attachment.filename}]",
                    'author': message.author.name,
                    'author_id': str(message.author.id)
                })
                continue

            if not attachment_info['size_ok']:
                logger.warning(f"檔案過大: {attachment.filename}")
                messages.append({
                    'type': 'text',
                    'content': f"[檔案過大: {attachment.filename} ({attachment_info['size_formatted']})]",
                    'author': message.author.name,
                    'author_id': str(message.author.id)
                })
                continue

            messages.append({
                'type': attachment_info['media_type'],
                'url': attachment.url,
                'filename': attachment.filename,
                'size': attachment.size,
                'author': message.author.name,
                'author_id': str(message.author.id)
            })

        # 處理嵌入 (Embeds)
        for embed in message.embeds:
            if embed.description:
                messages.append({
                    'type': 'text',
                    'content': f"[嵌入訊息] {embed.title or ''}: {embed.description}",
                    'author': message.author.name,
                    'author_id': str(message.author.id)
                })

        return messages

    @staticmethod
    async def convert_to_line_messages(
        processed_messages: List[Dict[str, Any]]
    ) -> List:
        """
        將處理後的訊息轉換為 Line 訊息格式

        Args:
            processed_messages: 處理後的訊息列表

        Returns:
            Line 訊息物件列表
        """
        line_messages = []

        for msg in processed_messages:
            msg_type = msg['type']
            author = msg.get('author', '未知')

            if msg_type == 'text':
                # 文字訊息
                content = msg['content']
                text = f"Discord - {author} - {content}"
                line_messages.append(TextMessage(type='text', text=text))

            elif msg_type == 'image':
                # 圖片訊息
                url = msg['url']
                line_messages.append(ImageMessage(
                    type='image',
                    originalContentUrl=url,
                    previewImageUrl=url
                ))
                # 添加說明文字
                line_messages.append(TextMessage(
                    type='text',
                    text=f"Discord - {author} 發送了圖片: {msg['filename']}"
                ))

            elif msg_type == 'video':
                # 影片訊息 - Line 需要預覽圖
                # 暫時使用文字通知
                line_messages.append(TextMessage(
                    type='text',
                    text=f"Discord - {author} 發送了影片: {msg['filename']}\n{msg['url']}"
                ))

            elif msg_type == 'audio':
                # 音訊訊息
                line_messages.append(TextMessage(
                    type='text',
                    text=f"Discord - {author} 發送了音訊: {msg['filename']}\n{msg['url']}"
                ))

            elif msg_type == 'file':
                # 一般檔案
                line_messages.append(TextMessage(
                    type='text',
                    text=f"Discord - {author} 發送了檔案: {msg['filename']}\n{msg['url']}"
                ))

        return line_messages

    @staticmethod
    async def save_message_to_db(
        message_id: str,
        user_id: str,
        platform: str,
        content: str,
        message_type: str = 'text',
        group_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        儲存訊息到資料庫

        Args:
            message_id: 訊息 ID
            user_id: 使用者 ID
            platform: 平台
            content: 內容
            message_type: 訊息類型
            group_id: 群組 ID
            metadata: 元數據
        """
        try:
            # 確保使用者存在
            User.get_or_create(user_id=user_id, platform=platform)

            # 儲存訊息
            Message(
                message_id=message_id,
                user_id=user_id,
                platform=platform,
                content=content,
                message_type=message_type,
                group_id=group_id,
                metadata=metadata
            ).save()

            logger.debug(f"儲存訊息到資料庫: {message_id}")

        except Exception as e:
            logger.exception(f"儲存訊息到資料庫失敗: {e}")

    @staticmethod
    def format_discord_message(
        author_name: str,
        content: str,
        message_type: str = 'text'
    ) -> str:
        """
        格式化 Discord 訊息

        Args:
            author_name: 作者名稱
            content: 內容
            message_type: 訊息類型

        Returns:
            格式化後的訊息
        """
        type_emoji = {
            'text': '💬',
            'image': '🖼️',
            'video': '🎬',
            'audio': '🎵',
            'file': '📎'
        }

        emoji = type_emoji.get(message_type, '📝')
        return f"{emoji} LINE - {author_name} - {content}"

    @staticmethod
    async def process_line_message(
        event,
        line_bot_api
    ) -> Optional[Dict[str, Any]]:
        """
        處理 Line 訊息

        Args:
            event: Line 事件物件
            line_bot_api: Line Bot API

        Returns:
            處理後的訊息字典
        """
        try:
            message_type = event.message.type
            user_id = event.source.user_id
            group_id = getattr(event.source, 'group_id', None)

            # 獲取使用者資訊
            if group_id:
                profile = line_bot_api.get_group_member_profile(
                    group_id=group_id,
                    user_id=user_id
                )
            else:
                profile = line_bot_api.get_profile(user_id)

            user_name = profile.display_name

            result = {
                'user_id': user_id,
                'user_name': user_name,
                'group_id': group_id,
                'message_type': message_type,
                'timestamp': event.timestamp
            }

            # 根據訊息類型處理
            if message_type == 'text':
                result['content'] = event.message.text

            elif message_type == 'image':
                result['message_id'] = event.message.id
                result['content'] = '[圖片]'

            elif message_type == 'video':
                result['message_id'] = event.message.id
                result['content'] = '[影片]'
                result['duration'] = getattr(event.message, 'duration', None)

            elif message_type == 'audio':
                result['message_id'] = event.message.id
                result['content'] = '[語音訊息]'
                result['duration'] = getattr(event.message, 'duration', None)

            elif message_type == 'file':
                result['message_id'] = event.message.id
                result['file_name'] = event.message.fileName
                result['file_size'] = event.message.fileSize
                result['content'] = f"[檔案: {event.message.fileName}]"

            elif message_type == 'location':
                result['title'] = event.message.title
                result['address'] = event.message.address
                result['latitude'] = event.message.latitude
                result['longitude'] = event.message.longitude
                result['content'] = f"[位置: {event.message.title or event.message.address}]"

            elif message_type == 'sticker':
                result['package_id'] = event.message.packageId
                result['sticker_id'] = event.message.stickerId
                result['content'] = f"[貼圖]"

            else:
                result['content'] = f"[不支援的訊息類型: {message_type}]"

            logger.info(f"處理 Line 訊息: {message_type} from {user_name}")
            return result

        except Exception as e:
            logger.exception(f"處理 Line 訊息時發生錯誤: {e}")
            return None
