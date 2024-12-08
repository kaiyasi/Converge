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

# 修改全域字典，用來儲存所有 Line 群組資訊
line_groups = {
    'default': os.getenv('LINE_GROUP_ID'),  # 保留預設群組
    'active_groups': {}  # 儲存其他作用中的群組
}

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
            # 送訊息到 Line 群組
            line_bot_api.push_message(
                line_groups['default'],
                TextSendMessage(text=f"Discord - {message.author.name}: {message.content}")
            )
            print(f"已發送到 Line: Discord - {message.author.name}: {message.content}")  # 除錯用
        except Exception as e:
            print(f"Error sending to Line: {e}")  # 錯誤記錄

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
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            if group_id not in line_groups['active_groups']:
                print(f"警告：群組 {group_id} 未註冊為活躍群組")
            else:
                # 取得群組和發送者資訊
                group_summary = line_bot_api.get_group_summary(group_id)
                group_name = group_summary.group_name
                profile = line_bot_api.get_group_member_profile(group_id, event.source.user_id)
                user_name = profile.display_name
                
                # 發送到 Discord，包群組和發送者資訊
                message = f"Line群組「{group_name}」- {user_name}: {event.message.text}"
                channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
                discord.utils.get_running_loop().create_task(channel.send(message))
                print(f"已發送到 Discord: {message}")  # 除錯用
    except Exception as e:
        print(f"Error in handle_message: {e}")  # 錯誤記錄

@handler.add(JoinEvent)
def handle_join(event):
    if event.source.type == 'group':
        group_id = event.source.group_id
        if group_id not in line_groups['active_groups']:
            line_groups['active_groups'][group_id] = {
                'id': group_id,
                'name': line_bot_api.get_group_summary(group_id).group_name
            }
            print(f"已加入新群組：{group_id}")
        else:
            print(f"群組已存在：{group_id}")

@handler.add(LeaveEvent)
def handle_leave(event):
    if event.source.type == 'group':
        group_id = event.source.group_id
        # 離開群組時從清單中移除
        if group_id in line_groups['active_groups']:
            del line_groups['active_groups'][group_id]
            print(f"已離開群組：{group_id}")

@bot.event
async def on_ready():
    print(f'Discord 機器人已登入為 {bot.user}')
    try:
        channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
        if channel:
            await channel.send("機器人已上��！")
            # 如果有預設群組，顯示其資訊
            if line_groups['default']:
                group_summary = line_bot_api.get_group_summary(line_groups['default'])
                await channel.send(f"預設Line群組：{group_summary.group_name}")
    except Exception as e:
        print(f"初始化時發生錯誤：{e}")

# 啟動 Discord 機器人
import threading
def run_discord_bot():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    # 啟動 Discord bot 在背景執行
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    discord_thread.start()
    
    # 修改 Flask 啟動設定
    port = int(os.environ.get('PORT', 5000))  # 改用 5000 端口
    print(f'正在啟動 Flask 伺服器於端口 {port}...')
    app.run(host='0.0.0.0', port=port, debug=False)  # 關閉 debug 模式 