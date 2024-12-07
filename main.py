import discord
from discord.ext import commands
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    JoinEvent, LeaveEvent
)
import os
from config import *

# 新增這個字典
line_groups = {}

# 設定 Discord 機器人
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 設定 Line 機器人
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 設定 Flask
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return 'Bot is running!'

# Discord -> Line
@bot.event
async def on_message(message):
    # 避免機器人回應自己的訊息
    if message.author == bot.user:
        return
    
    # 確認是否來自指定頻道
    if message.channel.id == int(DISCORD_CHANNEL_ID):
        try:
            # 改用 broadcast 直接發送給所有訂閱者
            line_bot_api.broadcast(
                TextSendMessage(text=f"Discord - {message.author.name}: {message.content}")
            )
        except Exception as e:
            print(f"Error sending to Line groups: {e}")

# Line -> Discord
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
    if channel:
        if event.source.type == 'group':
            group_id = event.source.group_id
            try:
                # 取得群組資訊
                group_summary = line_bot_api.get_group_summary(group_id)
                group_name = group_summary.group_name
                # 發送到 Discord
                discord.utils.get_running_loop().create_task(
                    channel.send(f"Line群組「{group_name}」: {event.message.text}")
                )
            except Exception as e:
                print(f"Error sending to Discord: {e}")
        elif event.source.type == 'user':
            try:
                # 取得用戶資料
                profile = line_bot_api.get_profile(event.source.user_id)
                user_name = profile.display_name
                discord.utils.get_running_loop().create_task(
                    channel.send(f"Line - {user_name}: {event.message.text}")
                )
            except Exception as e:
                print(f"Error sending to Discord: {e}")

# 啟動 Discord 機器人
import threading
def run_discord_bot():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_discord_bot, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 