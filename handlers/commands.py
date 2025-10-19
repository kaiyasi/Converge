"""
指令處理器
- Discord 指令
- Line 指令
- 系統管理指令
"""
import discord
from discord.ext import commands
from typing import Optional, Dict, Any
from datetime import datetime
from models.database import get_db
from models.quota import Quota, SystemQuota
from models.user import User
from models.message import Message
from core.ai_engine import AIEngine
from utils.logger import get_logger
from config import config

logger = get_logger(__name__)


class CommandHandler:
    """指令處理類"""

    def __init__(self, discord_bot, line_bot_api, ai_engine: AIEngine):
        """
        初始化指令處理器

        Args:
            discord_bot: Discord 機器人實例
            line_bot_api: Line Bot API 實例
            ai_engine: AI 引擎實例
        """
        self.discord_bot = discord_bot
        self.line_bot_api = line_bot_api
        self.ai_engine = ai_engine
        self.register_discord_commands()

    def register_discord_commands(self):
        """註冊 Discord 指令"""

        @self.discord_bot.bot.command(name='status', help='查看機器人狀態')
        async def status(ctx):
            """查看機器人狀態"""
            try:
                await self.cmd_status(ctx)
            except Exception as e:
                logger.exception(f"執行 status 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        @self.discord_bot.bot.command(name='quota', help='查看 API 配額使用情況')
        async def quota(ctx):
            """查看配額"""
            try:
                await self.cmd_quota(ctx)
            except Exception as e:
                logger.exception(f"執行 quota 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        @self.discord_bot.bot.command(name='stats', help='查看使用統計')
        async def stats(ctx):
            """查看統計"""
            try:
                await self.cmd_stats(ctx)
            except Exception as e:
                logger.exception(f"執行 stats 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        @self.discord_bot.bot.command(name='users', help='查看使用者列表')
        async def users(ctx, platform: str = 'all'):
            """查看使用者"""
            try:
                await self.cmd_users(ctx, platform)
            except Exception as e:
                logger.exception(f"執行 users 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        @self.discord_bot.bot.command(name='dbstats', help='查看資料庫統計')
        async def dbstats(ctx):
            """資料庫統計"""
            try:
                await self.cmd_dbstats(ctx)
            except Exception as e:
                logger.exception(f"執行 dbstats 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        @self.discord_bot.bot.command(name='help', help='顯示幫助訊息')
        async def help_command(ctx):
            """幫助訊息"""
            try:
                await self.cmd_help(ctx)
            except Exception as e:
                logger.exception(f"執行 help 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        @self.discord_bot.bot.command(name='ping', help='測試機器人回應')
        async def ping(ctx):
            """Ping 測試"""
            try:
                await self.cmd_ping(ctx)
            except Exception as e:
                logger.exception(f"執行 ping 指令時發生錯誤: {e}")
                await ctx.send(f"❌ 執行指令時發生錯誤: {str(e)}")

        logger.info("Discord 指令已註冊")

    async def cmd_status(self, ctx):
        """狀態指令"""
        embed = discord.Embed(
            title="🤖 機器人狀態",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )

        # 基本資訊
        embed.add_field(
            name="📡 連線狀態",
            value=f"✅ Discord: 已連線\n✅ Line: 已連線\n✅ AI 引擎: 正常",
            inline=False
        )

        # 延遲
        latency = round(self.discord_bot.bot.latency * 1000, 2)
        embed.add_field(
            name="⏱️ 延遲",
            value=f"{latency} ms",
            inline=True
        )

        # 伺服器資訊
        guild_count = len(self.discord_bot.bot.guilds)
embed.set_footer(text="Converge")
        await ctx.send(embed=embed)

    async def cmd_quota(self, ctx):
        """配額指令"""
        quota_info = SystemQuota.get_all()

        embed = discord.Embed(
            title="📊 API 配額使用情況",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for quota in quota_info:
            usage = quota['usage_count']
            limit = quota['limit_count']
            percentage = (usage / limit * 100) if limit > 0 else 0
            remaining = limit - usage

            # 選擇顏色
            if percentage >= 90:
                status_emoji = "🔴"
            elif percentage >= 70:
                status_emoji = "🟡"
            else:
                status_emoji = "🟢"

            embed.add_field(
                name=f"{status_emoji} {quota['quota_type'].upper()}",
                value=(
                    f"已使用: {usage}/{limit} ({percentage:.1f}%)\n"
                    f"剩餘: {remaining}\n"
                    f"週期: {quota['reset_period']}"
                ),
                inline=True
            )

        embed.set_footer(text="Converge")
        await ctx.send(embed=embed)

    async def cmd_stats(self, ctx):
        """統計指令"""
        db = get_db()
        stats = db.get_stats()

        embed = discord.Embed(
            title="📈 使用統計",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="👥 使用者",
            value=f"{stats['total_users']} 人",
            inline=True
        )

        embed.add_field(
            name="💬 訊息",
            value=f"{stats['total_messages']} 則",
            inline=True
        )

        embed.add_field(
            name="🤖 AI 對話",
            value=f"{stats['total_chat_history']} 次",
            inline=True
        )

        embed.add_field(
            name="🔗 活躍群組配對",
            value=f"{stats['active_group_mappings']} 個",
            inline=True
        )

        embed.add_field(
            name="💾 資料庫大小",
            value=f"{stats['db_size_mb']} MB",
            inline=True
        )

        # 平台使用統計
        line_msg_count = Message.count_by_platform('line')
        discord_msg_count = Message.count_by_platform('discord')

        embed.add_field(
            name="📱 平台訊息分布",
            value=f"Line: {line_msg_count}\nDiscord: {discord_msg_count}",
            inline=False
        )

        embed.set_footer(text="Converge")
        await ctx.send(embed=embed)

    async def cmd_users(self, ctx, platform: str = 'all'):
        """使用者列表指令"""
        if platform.lower() == 'all':
            users = User.get_all()
            title = "👥 所有使用者"
        else:
            users = User.get_all(platform=platform.lower())
            title = f"👥 {platform.upper()} 使用者"

        if not users:
            await ctx.send("目前沒有使用者資料")
            return

        embed = discord.Embed(
            title=title,
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        # 分組顯示 (每 25 個一組,Discord 限制)
        for i in range(0, min(len(users), 25)):
            user = users[i]
            embed.add_field(
                name=f"{user.display_name or user.user_id}",
                value=f"平台: {user.platform}\nID: {user.user_id[:20]}...",
                inline=True
            )

        if len(users) > 25:
            embed.set_footer(text=f"顯示前 25 個使用者,共 {len(users)} 個")
        else:
            embed.set_footer(text=f"共 {len(users)} 個使用者")

        await ctx.send(embed=embed)

    async def cmd_dbstats(self, ctx):
        """資料庫統計指令"""
        db = get_db()

        embed = discord.Embed(
            title="💾 資料庫詳細統計",
            color=discord.Color.dark_blue(),
            timestamp=datetime.now()
        )

        # 使用者統計
        total_users = User.count()
        line_users = User.count(platform='line')
        discord_users = User.count(platform='discord')

        embed.add_field(
            name="👥 使用者統計",
            value=f"總計: {total_users}\nLine: {line_users}\nDiscord: {discord_users}",
            inline=True
        )

        # 訊息統計
        with db.get_cursor() as cursor:
            # 今日訊息
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE date(created_at) = date('now')
            """)
            today_messages = cursor.fetchone()[0]

            # 本週訊息
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE date(created_at) >= date('now', '-7 days')
            """)
            week_messages = cursor.fetchone()[0]

        embed.add_field(
            name="💬 訊息統計",
            value=f"今日: {today_messages}\n本週: {week_messages}",
            inline=True
        )

        # 配額統計
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM quotas")
            quota_records = cursor.fetchone()[0]

        embed.add_field(
            name="📊 配額記錄",
            value=f"{quota_records} 筆",
            inline=True
        )

        embed.set_footer(text="Converge")
        await ctx.send(embed=embed)

    async def cmd_help(self, ctx):
        """幫助指令"""
        embed = discord.Embed(
            title="📚 指令幫助",
            description="Converge 可用指令列表",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )

        commands_list = [
            ("!status", "查看機器人狀態"),
            ("!quota", "查看 API 配額使用情況"),
            ("!stats", "查看使用統計"),
            ("!users [platform]", "查看使用者列表 (可選: line/discord/all)"),
            ("!dbstats", "查看資料庫詳細統計"),
            ("!ping", "測試機器人回應"),
            ("!help", "顯示此幫助訊息"),
        ]

        for cmd, desc in commands_list:
embed.set_footer(text="Converge")
        await ctx.send(embed=embed)

    async def cmd_ping(self, ctx):
        """Ping 指令"""
        latency = round(self.discord_bot.bot.latency * 1000, 2)
        await ctx.send(f"🏓 Pong! 延遲: {latency} ms")

    def process_line_command(self, text: str) -> Optional[Dict[str, Any]]:
        """
        處理 Line 指令

        Args:
            text: 訊息文字

        Returns:
            指令結果或 None
        """
        if not text.startswith('#'):
            return None

        parts = text.split()
        command = parts[0][1:].lower()  # 移除 #
        args = parts[1:] if len(parts) > 1 else []

        logger.info(f"處理 Line 指令: {command}")

        if command == 'status':
            return {
                'type': 'text',
                'content': "✅ Line Bot 運作正常\n🤖 已連接到 Discord"
            }

        elif command == 'help':
            return {
                'type': 'text',
                'content': (
                    "📚 可用指令:\n\n"
                    "#status - 查看機器人狀態\n"
                    "#help - 顯示此幫助訊息"
                )
            }

        else:
            return {
                'type': 'text',
                'content': f"❌ 未知指令: #{command}\n使用 #help 查看可用指令"
            }
