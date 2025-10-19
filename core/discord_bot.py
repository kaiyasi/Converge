"""
Discord 機器人管理模組
- 自動重連
- 錯誤恢復
- 事件處理
"""
import discord
from discord.ext import commands
import asyncio
from typing import Optional, Callable
from utils.logger import get_logger
from utils.retry import ReconnectManager, retry_with_backoff
from config import config

logger = get_logger(__name__)


class DiscordBotManager:
    """Discord 機器人管理器"""

    def __init__(self):
        """初始化 Discord 機器人"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True

        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.reconnect_manager = ReconnectManager(
            max_retries=0,  # 無限重試
            base_delay=5.0,
            max_delay=300.0
        )
        self.is_ready = False
        self._setup_events()

    def _setup_events(self):
        """設定基本事件處理器"""

        @self.bot.event
        async def on_ready():
            """機器人就緒事件"""
            self.is_ready = True
            logger.info(f'Discord 機器人已登入: {self.bot.user.name} (ID: {self.bot.user.id})')

            try:
                channel = self.bot.get_channel(int(config.DISCORD_CHANNEL_ID))
                if channel:
                    await channel.send("🤖 機器人已上線！")
            except Exception as e:
                logger.error(f"發送上線訊息失敗: {e}")

        @self.bot.event
        async def on_disconnect():
            """斷線事件"""
            self.is_ready = False
            logger.warning("Discord 機器人已斷線")

        @self.bot.event
        async def on_resumed():
            """恢復連接事件"""
            self.is_ready = True
            logger.info("Discord 機器人已恢復連接")

        @self.bot.event
        async def on_error(event, *args, **kwargs):
            """錯誤事件"""
            logger.exception(f"Discord 事件錯誤 ({event})")

    def add_event_handler(self, event_name: str, handler: Callable):
        """
        添加事件處理器

        Args:
            event_name: 事件名稱
            handler: 處理函數
        """
        @self.bot.event
        async def event_wrapper(*args, **kwargs):
            try:
                await handler(*args, **kwargs)
            except Exception as e:
                logger.exception(f"處理 {event_name} 事件時發生錯誤: {e}")

        event_wrapper.__name__ = event_name
        setattr(self.bot, event_name, event_wrapper)

    def add_command(self, name: str, handler: Callable, **kwargs):
        """
        添加指令

        Args:
            name: 指令名稱
            handler: 處理函數
            **kwargs: 其他參數
        """
        @self.bot.command(name=name, **kwargs)
        async def command_wrapper(ctx, *args):
            try:
                await handler(ctx, *args)
            except Exception as e:
                logger.exception(f"執行指令 {name} 時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

    @retry_with_backoff(
        max_retries=5,
        base_delay=5.0,
        exceptions=(discord.LoginFailure, discord.ConnectionClosed)
    )
    async def start(self):
        """
        啟動機器人 (帶重試)

        Raises:
            Exception: 啟動失敗時拋出
        """
        logger.info("正在啟動 Discord 機器人...")
        try:
            await self.bot.start(config.DISCORD_TOKEN)
        except discord.LoginFailure as e:
            logger.error(f"Discord Token 無效: {e}")
            raise
        except Exception as e:
            logger.error(f"Discord 機器人啟動失敗: {e}")
            raise

    async def stop(self):
        """停止機器人"""
        logger.info("正在停止 Discord 機器人...")
        await self.bot.close()
        self.is_ready = False

    async def wait_until_ready(self, timeout: float = 60.0):
        """
        等待機器人就緒

        Args:
            timeout: 超時時間 (秒)

        Raises:
            asyncio.TimeoutError: 超時時拋出
        """
        try:
            await asyncio.wait_for(self.bot.wait_until_ready(), timeout=timeout)
            logger.info("Discord 機器人已就緒")
        except asyncio.TimeoutError:
            logger.error("等待 Discord 機器人就緒超時")
            raise

    def get_channel(self, channel_id: int) -> Optional[discord.TextChannel]:
        """
        獲取頻道

        Args:
            channel_id: 頻道 ID

        Returns:
            頻道物件或 None
        """
        return self.bot.get_channel(channel_id)

    async def send_message(
        self,
        channel_id: int,
        content: str = None,
        embed: discord.Embed = None,
        file: discord.File = None
    ) -> Optional[discord.Message]:
        """
        發送訊息 (帶錯誤處理)

        Args:
            channel_id: 頻道 ID
            content: 訊息內容
            embed: 嵌入訊息
            file: 檔案

        Returns:
            發送的訊息或 None
        """
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                logger.error(f"找不到頻道: {channel_id}")
                return None

            message = await channel.send(content=content, embed=embed, file=file)
            logger.debug(f"發送 Discord 訊息成功: {message.id}")
            return message

        except discord.Forbidden as e:
            logger.error(f"沒有權限發送訊息到頻道 {channel_id}: {e}")
        except discord.HTTPException as e:
            logger.error(f"發送訊息失敗 (HTTP錯誤): {e}")
        except Exception as e:
            logger.exception(f"發送訊息時發生未知錯誤: {e}")

        return None

    def run_in_thread(self):
        """在獨立線程中運行機器人"""
        import threading

        def run():
            try:
                asyncio.run(self.start())
            except KeyboardInterrupt:
                logger.info("收到中斷信號,停止 Discord 機器人")
            except Exception as e:
                logger.exception(f"Discord 機器人運行時發生錯誤: {e}")

        thread = threading.Thread(target=run, daemon=True, name="DiscordBot")
        thread.start()
        logger.info("Discord 機器人線程已啟動")
        return thread

    @property
    def user(self) -> Optional[discord.ClientUser]:
        """獲取機器人使用者資訊"""
        return self.bot.user

    @property
    def latency(self) -> float:
        """獲取延遲 (毫秒)"""
        return round(self.bot.latency * 1000, 2)
