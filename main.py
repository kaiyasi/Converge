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
import google.generativeai as genai

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
        self.daily_usage = {}
        self.cooldowns = {}  # 新增冷卻時間追蹤
    
    def is_in_cooldown(self, user_id):
        # 檢查是否在冷卻時間內（30秒）
        if user_id in self.cooldowns:
            elapsed = time.time() - self.cooldowns[user_id]
            return elapsed < 30
        return False
    
    def set_cooldown(self, user_id):
        # 設定冷卻時間
        self.cooldowns[user_id] = time.time()
    
    def get_remaining_cooldown(self, user_id):
        # 取得剩餘冷卻時間
        if user_id in self.cooldowns:
            elapsed = time.time() - self.cooldowns[user_id]
            remaining = max(0, 30 - elapsed)
            return int(remaining)
        return 0
    
    def can_use_ai(self, user_id):
        # 檢查是否超過每日限制
        today = time.strftime('%Y-%m-%d')
        if today not in self.daily_usage:
            self.daily_usage = {today: {}}
        
        if user_id not in self.daily_usage[today]:
            self.daily_usage[today][user_id] = 0
            
        # 設定每人每日限制次數（例如：20次）
        return self.daily_usage[today][user_id] < 20
    
    def increment_usage(self, user_id):
        today = time.strftime('%Y-%m-%d')
        self.daily_usage[today][user_id] += 1
    
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

# 初始化 Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# AI 回應功能
async def get_ai_response(user_id, message):
    try:
        # 檢查冷卻時間
        if chat_state.is_in_cooldown(user_id):
            remaining = chat_state.get_remaining_cooldown(user_id)
            return f"請稍等 {remaining} 秒後再發送新的問題。"
        
        # 檢查使用限制
        if not chat_state.can_use_ai(user_id):
            return (
                "抱歉，您今日的 AI 對話次數已達上限。\n"
                "配額將於明日重置。\n"
                "感謝您的理解！"
            )
        
        # 生成回應
        response = model.generate_content(
            f"請用繁體中文回答以下問題，並保持回答簡潔：\n{message}"
        )
        
        # 設定冷卻時間
        chat_state.set_cooldown(user_id)
        
        # 增加使用次數
        chat_state.increment_usage(user_id)
        
        return response.text
        
    except Exception as e:
        app.logger.error(f"AI 回應錯誤：{str(e)}")
        return "抱歉，AI 助手暫時無法回應。請稍後再試。"

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
                            formatted_text = f"(Discord) - {message.author.name} - {message.content}"
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
            message_text = f"(LINE) - {user_name} - {event.message.text}"
            
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
