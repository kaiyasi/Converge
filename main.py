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
from config import config

# Flask 應用
app = Flask(__name__)

# Discord 設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# LINE Bot 設定
configuration = Configuration(access_token=config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
line_bot_api = MessagingApi(ApiClient(configuration))


# 全域變數
line_groups = {
    'default': config.LINE_GROUP_ID,
    'active_groups': {}
}

# 聊天狀態管理
class ChatState:
    def __init__(self):
        self.histories = {}
        self.last_interaction = {}
        self.daily_usage = {}
        self.processing = set()
        self.last_message = {}
        self.line_quota_exceeded = False
        self.monthly_message_count = 0  # 追蹤每月訊息數
        self.monthly_reset_date = None  # 月重置日期
        # 修復: 添加缺少的屬性初始化
        self.request_count = 0
        self.last_request_time = time.time()
        self.quota_notice_sent = False
    
    def check_monthly_reset(self):
        # 檢查是否需要重置月計數
        current_date = time.strftime('%Y-%m')
        if self.monthly_reset_date != current_date:
            self.monthly_reset_date = current_date
            self.monthly_message_count = 0
            self.line_quota_exceeded = False
            self.quota_notice_sent = False
    
    def increment_message_count(self):
        self.check_monthly_reset()
        self.monthly_message_count += 1
        # 接近限制時提前警告
        warning_threshold = int(config.LINE_MONTHLY_LIMIT * config.LINE_WARNING_THRESHOLD)
        if self.monthly_message_count >= warning_threshold:
            app.logger.warning(f"接近月訊息限制：{self.monthly_message_count}/{config.LINE_MONTHLY_LIMIT}")
        return self.monthly_message_count < config.LINE_MONTHLY_LIMIT

    def get_remaining_quota(self):
        return max(0, config.LINE_MONTHLY_LIMIT - self.monthly_message_count)
    
    def can_make_request(self):
        # 重置計數器（每分鐘）
        current_time = time.time()
        if current_time - self.last_request_time >= 60:
            self.request_count = 0
            self.last_request_time = current_time

        # 檢查請求限制
        return self.request_count < config.AI_REQUEST_PER_MINUTE
    
    def increment_request(self):
        self.request_count += 1
        
    def is_similar_message(self, user_id, message):
        # 檢查訊息相似度（避免輕微變化的重複訊息）
        if user_id in self.last_message:
            last_msg = self.last_message[user_id]
            # 如果兩條訊息長度相差不大且有高度重疊
            if abs(len(message) - len(last_msg)) <= config.MESSAGE_LENGTH_DIFF:
                common_chars = sum(1 for a, b in zip(message, last_msg) if a == b)
                similarity = common_chars / max(len(message), len(last_msg))
                return similarity > config.MESSAGE_SIMILARITY_THRESHOLD
        return False
    
    def is_processing(self, user_id):
        return user_id in self.processing
    
    def start_processing(self, user_id):
        self.processing.add(user_id)
    
    def end_processing(self, user_id):
        self.processing.discard(user_id)
    
    def is_duplicate_message(self, user_id, message):
        return (user_id in self.last_message and 
                self.last_message[user_id] == message)
    
    def update_last_message(self, user_id, message):
        self.last_message[user_id] = message
    
    def can_use_ai(self, user_id):
        # 檢查是否超過每日限制
        today = time.strftime('%Y-%m-%d')
        if today not in self.daily_usage:
            self.daily_usage = {today: {}}

        if user_id not in self.daily_usage[today]:
            self.daily_usage[today][user_id] = 0

        # 設定每人每日限制次數
        return self.daily_usage[today][user_id] < config.AI_DAILY_LIMIT_PER_USER
    
    def increment_usage(self, user_id):
        today = time.strftime('%Y-%m-%d')
        self.daily_usage[today][user_id] += 1
    
    def get_history(self, user_id):
        current_time = time.time()
        if user_id in self.last_interaction:
            if current_time - self.last_interaction[user_id] > config.CONVERSATION_TIMEOUT:
                self.histories[user_id] = []

        if user_id not in self.histories:
            self.histories[user_id] = []

        self.last_interaction[user_id] = current_time
        return self.histories[user_id]

    def add_message(self, user_id, role, content):
        history = self.get_history(user_id)
        history.append({"role": role, "content": content})
        if len(history) > config.MAX_HISTORY_LENGTH:
            history = history[-config.MAX_HISTORY_LENGTH:]
        self.histories[user_id] = history

chat_state = ChatState()

# 初始化 Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# AI 回應功能
async def get_ai_response(user_id, message):
    try:
        # 檢查請求限制
        if not chat_state.can_make_request():
            return "系統正忙，請稍後再試。"
        
        # 檢查訊息相似度
        if chat_state.is_similar_message(user_id, message):
            return None
        
        # 更新最後訊息
        chat_state.update_last_message(user_id, message)
        
        # 檢查使用限制
        if not chat_state.can_use_ai(user_id):
            return "今日 AI 對話次數已達上限，明日重置。"
        
        # 增加請求計數
        chat_state.increment_request()
        
        # 生成回應
        response = model.generate_content(
            f"請用繁體中文回答以下問題，保持簡潔：\n{message}",
            generation_config={
                "temperature": config.AI_TEMPERATURE,
                "top_p": config.AI_TOP_P,
                "top_k": config.AI_TOP_K,
                "max_output_tokens": config.AI_MAX_TOKENS,
            }
        )
        
        # 增加使用次數
        chat_state.increment_usage(user_id)
        
        return response.text
        
    except Exception as e:
        app.logger.error(f"AI 回應錯誤：{str(e)}")
        return "AI 助手暫時無法回應，請稍後再試。"

# Discord 事件處理
@bot.event
async def on_ready():
    print(f'Discord 機器人已登入為 {bot.user}')
    try:
        channel = bot.get_channel(int(config.DISCORD_CHANNEL_ID))
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
    
    if message.channel.id == int(config.DISCORD_CHANNEL_ID):
        try:
            if line_groups['active_groups']:
                for group in line_groups['active_groups'].values():
                    if group and 'id' in group:
                        messages = []
                        
                        if message.content:
                            formatted_text = f"Discord - {message.author.name} - {message.content}"
                            messages.append(TextMessage(type='text', text=formatted_text))
                        
                        for attachment in message.attachments:
                            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                                try:
                                    # 修復: 直接使用 Discord 的圖片 URL
                                    # Discord CDN URL 是公開可訪問的,不需要重新上傳
                                    image_url = attachment.url

                                    messages.append(ImageMessage(
                                        type='image',
                                        originalContentUrl=image_url,
                                        previewImageUrl=image_url
                                    ))
                                    app.logger.info(f"已添加圖片訊息: {attachment.filename}")

                                except Exception as e:
                                    app.logger.error(f"處理圖片時發生錯誤：{str(e)}")
                                    # 如果圖片處理失敗,至少發送通知
                                    messages.append(TextMessage(
                                        type='text',
                                        text=f"Discord - {message.author.name} 發送了圖片: {attachment.filename}"
                                    ))
                        
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
                # 檢查配額
                if not chat_state.increment_message_count():
                    chat_state.line_quota_exceeded = True
                    remaining = chat_state.get_remaining_quota()
                    app.logger.warning(f"本月剩餘配額：{remaining}")
                    # ... 其他處理邏輯 ...
                
                if chat_state.is_processing(event.source.user_id):
                    return
                
                chat_state.start_processing(event.source.user_id)
                
                try:
                    message = event.message.text.strip()
                    if not message:  # 忽略空白訊息
                        return
                        
                    app.logger.info(f"處理用戶訊息：{event.source.user_id}")
                    
                    response = asyncio.run(get_ai_response(event.source.user_id, message))
                    
                    if response:
                        try:
                            request = PushMessageRequest(
                                to=event.source.user_id,
                                messages=[
                                    TextMessage(
                                        type='text',
                                        text=f"🤖 {response}"
                                    )
                                ]
                            )
                            line_bot_api.push_message(request)
                            
                        except Exception as e:
                            if "429" in str(e) or "monthly limit" in str(e).lower():
                                chat_state.line_quota_exceeded = True
                            raise e
                
                finally:
                    chat_state.end_processing(event.source.user_id)
                    
            elif event.source.type == 'group':
                handle_group_message(event)
                
        except Exception as e:
            app.logger.error(f"訊息處理錯誤：{str(e)}")
            if event.source.type == 'user':
                chat_state.end_processing(event.source.user_id)

def handle_group_message(event):
    try:
        group_id = event.source.group_id
        profile = line_bot_api.get_group_member_profile(
            group_id=group_id,
            user_id=event.source.user_id
        )
        user_name = profile.display_name
        
        channel = bot.get_channel(int(config.DISCORD_CHANNEL_ID))
        if channel:
            message_text = f"LINE - {user_name} - {event.message.text}"
            
            future = asyncio.run_coroutine_threadsafe(
                channel.send(message_text),
                bot.loop
            )
            future.result()
            
    except Exception as e:
        app.logger.error(f"處理群組訊息時發生錯誤：{str(e)}")

# 主程式
if __name__ == "__main__":
    # 驗證配置
    try:
        config.validate()
        print("✅ 配置驗證通過")
    except ValueError as e:
        print(f"❌ 配置錯誤: {e}")
        exit(1)

    # 啟動 Discord 機器人
    discord_thread = threading.Thread(target=lambda: bot.run(config.DISCORD_TOKEN), daemon=True)
    discord_thread.start()

    # 啟動 Flask 伺服器
    print(f"🚀 啟動 Flask 伺服器 (Host: {config.HOST}, Port: {config.PORT})")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
