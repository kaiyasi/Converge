import os
import json
import time
import asyncio
import threading
import tempfile
import aiohttp
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    PushMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.exceptions import InvalidSignatureError
import discord
from discord.ext import commands
from openai import OpenAI

# Flask 應用
app = Flask(__name__)

# Discord 設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# LINE Bot 設定
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
line_bot_api = MessagingApi(ApiClient(configuration))

# OpenAI 設定
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 全域變數
line_groups = {
    'default': os.getenv('LINE_GROUP_ID'),
    'active_groups': {}
}

# 聊天狀態管理
class ChatState:
    def __init__(self):
        self.histories = {}
        self.last_interaction = {}
    
    def get_history(self, user_id):
        current_time = time.time()
        if user_id in self.last_interaction:
            if current_time - self.last_interaction[user_id] > 1800:
                self.histories[user_id] = []
        
        if user_id not in self.histories:
            self.histories[user_id] = []
        
        self.last_interaction[user_id] = current_time
        return self.histories[user_id]
    
    def add_message(self, user_id, role, content):
        history = self.get_history(user_id)
        history.append({"role": role, "content": content})
        if len(history) > 10:
            history = history[-10:]
        self.histories[user_id] = history

chat_state = ChatState()

# AI 回應功能
async def get_ai_response(user_id, message):
    try:
        chat_state.add_message(user_id, "user", message)
        
        messages = [
            {"role": "system", "content": "你是一個友善的AI助手。請用繁體中文回答，並保持回答簡潔。"}
        ] + chat_state.get_history(user_id)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        chat_state.add_message(user_id, "assistant", ai_response)
        
        return ai_response
        
    except Exception as e:
        app.logger.error(f"AI 回應錯誤：{str(e)}")
        return "抱歉，我現在無法回應。請稍後再試。"

# Discord 事件處理
@bot.event
async def on_ready():
    print(f'Discord 機器人已登入為 {bot.user}')
    try:
        channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
        if channel:
            await channel.send("🤖 機器人已上線！")
            
            if line_groups['default']:
                try:
                    group_summary = line_bot_api.get_group_summary(
                        group_id=line_groups['default']
                    )
                    line_groups['active_groups'][line_groups['default']] = {
                        'id': line_groups['default'],
                        'name': group_summary.group_name
                    }
                    await channel.send(
                        "```\n"
                        "📱 LINE 群組設定\n"
                        f"✅ 已連接到預設群組：{group_summary.group_name}\n"
                        "```"
                    )
                    app.logger.info(f"已設定預設群組：{group_summary.group_name}")
                except Exception as e:
                    await channel.send(
                        "```\n"
                        "❌ LINE 群組設定失敗\n"
                        f"錯誤：{str(e)}\n"
                        "```"
                    )
                    app.logger.error(f"設定預設群組時發生錯誤：{str(e)}")
    except Exception as e:
        app.logger.error(f"機器人初始化時發生錯誤：{str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.id == int(os.getenv('DISCORD_CHANNEL_ID')):
        try:
            if line_groups['active_groups']:
                for group in line_groups['active_groups'].values():
                    if group and 'id' in group:
                        messages = []
                        
                        if message.content:
                            formatted_text = (
                                "💬 Discord\n"
                                f"👤 {message.author.name}\n"
                                f"📝 {message.content}"
                            )
                            messages.append(TextMessage(type='text', text=formatted_text))
                        
                        for attachment in message.attachments:
                            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(attachment.url) as resp:
                                            if resp.status == 200:
                                                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                                                    temp_file.write(await resp.read())
                                                    temp_file_path = temp_file.name
                                                
                                                with open(temp_file_path, 'rb') as f:
                                                    response = line_bot_api.upload_rich_menu_image(
                                                        f.read(),
                                                        'image/jpeg'
                                                    )
                                                    image_url = response.get('url')
                                                    
                                                    messages.append(ImageMessage(
                                                        type='image',
                                                        originalContentUrl=image_url,
                                                        previewImageUrl=image_url
                                                    ))
                                                
                                                os.unlink(temp_file_path)
                                                
                                except Exception as e:
                                    app.logger.error(f"處理圖片時發生錯誤：{str(e)}")
                        
                        if messages:
                            request = PushMessageRequest(
                                to=group['id'],
                                messages=messages
                            )
                            response = line_bot_api.push_message(request)
                            app.logger.info("訊息發送成功")
                            
        except Exception as e:
            app.logger.error(f"發送到 Line 時發生錯誤：{str(e)}")

# LINE Webhook 處理
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    app.logger.info(f"收到 webhook 請求")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error(f"簽名驗證失敗")
        app.logger.error(f"收到的簽名: {signature}")
        abort(400)
    except Exception as e:
        app.logger.error(f"處理 webhook 時發生錯誤：{str(e)}")
        return str(e), 500
    
    return 'OK', 200

@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        try:
            if event.source.type == 'user':
                user_id = event.source.user_id
                app.logger.info(f"收到私人訊息：{event.message.text}")
                
                profile = line_bot_api.get_profile(user_id)
                user_name = profile.display_name
                
                response = asyncio.run(get_ai_response(user_id, event.message.text))
                
                request = PushMessageRequest(
                    to=user_id,
                    messages=[
                        TextMessage(
                            type='text',
                            text=(
                                "🤖 AI 助手\n"
                                f"👋 Hi, {user_name}!\n"
                                f"📝 {response}"
                            )
                        )
                    ]
                )
                line_bot_api.push_message(request)
                app.logger.info(f"已發送 AI 回應給用戶：{user_id}")
                
            elif event.source.type == 'group':
                handle_group_message(event)
                
        except Exception as e:
            app.logger.error(f"處理訊息時發生錯誤：{str(e)}")

def handle_group_message(event):
    try:
        group_id = event.source.group_id
        profile = line_bot_api.get_group_member_profile(
            group_id=group_id,
            user_id=event.source.user_id
        )
        user_name = profile.display_name
        
        channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
        if channel:
            message_text = (
                "```\n"
                "📱 LINE\n"
                f"👤 {user_name}\n"
                f"📝 {event.message.text}\n"
                "```"
            )
            
            future = asyncio.run_coroutine_threadsafe(
                channel.send(message_text),
                bot.loop
            )
            future.result()
            
    except Exception as e:
        app.logger.error(f"處理群組訊息時發生錯誤：{str(e)}")

# 主程式
if __name__ == "__main__":
    discord_thread = threading.Thread(target=lambda: bot.run(os.getenv('DISCORD_TOKEN')), daemon=True)
    discord_thread.start()
    
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
