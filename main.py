import discord
from discord.ext import commands
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
import os
from config import *

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

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    await bot.load_extension('cogs.line_bridge')

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
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        discord.utils.get_running_loop().create_task(
            channel.send(f"Line - {event.source.user_id}: {event.message.text}")
        )

# 啟動 Discord 機��人
import threading
def run_discord_bot():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_discord_bot, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 