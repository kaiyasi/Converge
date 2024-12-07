import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

class LineBridge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        self.handler = WebhookHandler(LINE_CHANNEL_SECRET)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        # 忽略機器人自己的訊息
        if message.author.bot:
            return
            
        # 只處理指定頻道的訊息
        if message.channel.id == DISCORD_CHANNEL_ID:
            # 將 Discord 訊息轉發到 Line
            try:
                self.line_bot_api.broadcast(
                    TextSendMessage(text=f"Discord - {message.author.name}: {message.content}")
                )
            except Exception as e:
                print(f"Error sending to LINE: {e}")

async def setup(bot):
    await bot.add_cog(LineBridge(bot)) 