"""
媒體處理服務
- 圖片處理
- 影片處理
- 音訊處理
- 檔案處理
"""
import aiohttp
import tempfile
import os
from typing import Optional, Tuple, BinaryIO
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class MediaHandler:
    """媒體處理類"""

    # 支援的媒體類型
    SUPPORTED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    SUPPORTED_VIDEO_TYPES = {'.mp4', '.mov', '.avi', '.mkv'}
    SUPPORTED_AUDIO_TYPES = {'.mp3', '.m4a', '.wav', '.ogg'}
    SUPPORTED_FILE_TYPES = {'.pdf', '.txt', '.doc', '.docx', '.xls', '.xlsx', '.zip'}

    # 檔案大小限制 (bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """獲取檔案副檔名"""
        return Path(filename).suffix.lower()

    @staticmethod
    def is_image(filename: str) -> bool:
        """判斷是否為圖片"""
        return MediaHandler.get_file_extension(filename) in MediaHandler.SUPPORTED_IMAGE_TYPES

    @staticmethod
    def is_video(filename: str) -> bool:
        """判斷是否為影片"""
        return MediaHandler.get_file_extension(filename) in MediaHandler.SUPPORTED_VIDEO_TYPES

    @staticmethod
    def is_audio(filename: str) -> bool:
        """判斷是否為音訊"""
        return MediaHandler.get_file_extension(filename) in MediaHandler.SUPPORTED_AUDIO_TYPES

    @staticmethod
    def is_supported_file(filename: str) -> bool:
        """判斷是否為支援的檔案類型"""
        ext = MediaHandler.get_file_extension(filename)
        return ext in (
            MediaHandler.SUPPORTED_IMAGE_TYPES |
            MediaHandler.SUPPORTED_VIDEO_TYPES |
            MediaHandler.SUPPORTED_AUDIO_TYPES |
            MediaHandler.SUPPORTED_FILE_TYPES
        )

    @staticmethod
    def get_media_type(filename: str) -> str:
        """
        判斷媒體類型

        Returns:
            'image', 'video', 'audio', 'file', 'unknown'
        """
        if MediaHandler.is_image(filename):
            return 'image'
        elif MediaHandler.is_video(filename):
            return 'video'
        elif MediaHandler.is_audio(filename):
            return 'audio'
        elif MediaHandler.get_file_extension(filename) in MediaHandler.SUPPORTED_FILE_TYPES:
            return 'file'
        else:
            return 'unknown'

    @staticmethod
    def check_file_size(size: int, media_type: str) -> bool:
        """
        檢查檔案大小是否符合限制

        Args:
            size: 檔案大小 (bytes)
            media_type: 媒體類型

        Returns:
            是否符合限制
        """
        limits = {
            'image': MediaHandler.MAX_IMAGE_SIZE,
            'video': MediaHandler.MAX_VIDEO_SIZE,
            'audio': MediaHandler.MAX_AUDIO_SIZE,
            'file': MediaHandler.MAX_FILE_SIZE
        }

        max_size = limits.get(media_type, MediaHandler.MAX_FILE_SIZE)
        return size <= max_size

    @staticmethod
    async def download_file(
        url: str,
        max_size: Optional[int] = None
    ) -> Optional[Tuple[bytes, str]]:
        """
        下載檔案

        Args:
            url: 檔案 URL
            max_size: 最大檔案大小限制

        Returns:
            (檔案內容, 檔案名稱) 或 None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"下載檔案失敗 (HTTP {response.status}): {url}")
                        return None

                    # 檢查檔案大小
                    content_length = response.headers.get('Content-Length')
                    if content_length and max_size:
                        if int(content_length) > max_size:
                            logger.warning(f"檔案過大: {content_length} bytes > {max_size} bytes")
                            return None

                    # 下載檔案
                    content = await response.read()

                    # 從 URL 或 Content-Disposition 獲取檔案名稱
                    filename = url.split('/')[-1].split('?')[0]
                    if 'Content-Disposition' in response.headers:
                        disposition = response.headers['Content-Disposition']
                        if 'filename=' in disposition:
                            filename = disposition.split('filename=')[1].strip('"\'')

                    logger.info(f"下載檔案成功: {filename} ({len(content)} bytes)")
                    return content, filename

        except Exception as e:
            logger.exception(f"下載檔案時發生錯誤: {e}")
            return None

    @staticmethod
    async def save_temp_file(
        content: bytes,
        filename: str
    ) -> Optional[str]:
        """
        儲存臨時檔案

        Args:
            content: 檔案內容
            filename: 檔案名稱

        Returns:
            臨時檔案路徑或 None
        """
        try:
            # 建立臨時檔案
            suffix = MediaHandler.get_file_extension(filename)
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                prefix='dilinebot_'
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name

            logger.debug(f"儲存臨時檔案: {temp_path}")
            return temp_path

        except Exception as e:
            logger.exception(f"儲存臨時檔案時發生錯誤: {e}")
            return None

    @staticmethod
    def cleanup_temp_file(file_path: str):
        """
        清理臨時檔案

        Args:
            file_path: 檔案路徑
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"清理臨時檔案: {file_path}")
        except Exception as e:
            logger.warning(f"清理臨時檔案失敗: {e}")

    @staticmethod
    def format_file_size(size: int) -> str:
        """
        格式化檔案大小

        Args:
            size: 檔案大小 (bytes)

        Returns:
            格式化後的字串 (例如: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @staticmethod
    async def process_discord_attachment(attachment) -> dict:
        """
        處理 Discord 附件

        Args:
            attachment: Discord 附件物件

        Returns:
            處理結果字典
        """
        media_type = MediaHandler.get_media_type(attachment.filename)
        file_size = attachment.size

        result = {
            'filename': attachment.filename,
            'url': attachment.url,
            'size': file_size,
            'size_formatted': MediaHandler.format_file_size(file_size),
            'media_type': media_type,
            'supported': MediaHandler.is_supported_file(attachment.filename),
            'size_ok': MediaHandler.check_file_size(file_size, media_type)
        }

        logger.info(f"處理 Discord 附件: {result}")
        return result

    @staticmethod
    async def download_line_content(
        message_id: str,
        line_bot_api
    ) -> Optional[bytes]:
        """
        下載 Line 訊息內容 (圖片/影片/音訊)

        Args:
            message_id: Line 訊息 ID
            line_bot_api: Line Bot API 實例

        Returns:
            檔案內容或 None
        """
        try:
            from linebot.v3.messaging import MessagingApiBlob
            api_client = line_bot_api.api_client

            blob_api = MessagingApiBlob(api_client)
            content = blob_api.get_message_content(message_id)

            logger.info(f"下載 Line 內容成功: {message_id}")
            return content

        except Exception as e:
            logger.exception(f"下載 Line 內容失敗: {e}")
            return None
