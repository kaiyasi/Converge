# Converge 優化與新功能規劃

## 📋 目錄

- [當前問題分析](#-當前問題分析)
- [優化方案](#-優化方案)
- [新功能規劃](#-新功能規劃)
- [實施優先級](#-實施優先級)
- [技術棧升級](#-技術棧升級)

---

## 🔍 當前問題分析

### ❌ 架構問題

#### 1. **缺少錯誤恢復機制**
```python
# 問題: main.py:77 - ChatState 類別缺少初始化
def can_make_request(self):
    current_time = time.time()
    if current_time - self.last_request_time >= 60:  # AttributeError 風險
```
**影響**: 首次調用會崩潰,因為 `last_request_time` 未初始化

#### 2. **硬編碼的配置值**
```python
# 問題: 分散在程式碼中的魔術數字
return self.daily_usage[today][user_id] < 20  # 硬編碼
self.monthly_message_count >= 450  # 硬編碼
```
**影響**: 難以調整和維護

#### 3. **圖片轉發功能錯誤**
```python
# 問題: main.py:259 - 使用錯誤的 API
response = line_bot_api.upload_rich_menu_image(...)  # 這是用於 Rich Menu 的 API
```
**影響**: 圖片轉發功能無法正常運作

#### 4. **缺少資料持久化**
- 所有狀態都在記憶體中
- 重啟後所有配額、歷史記錄遺失
- 無法進行統計分析

#### 5. **單執行緒 Flask 效能瓶頸**
```python
app.run(host='0.0.0.0', port=port)  # 開發伺服器,不適合生產環境
```

#### 6. **缺少日誌系統**
- 使用 `print()` 和簡單的 `app.logger`
- 沒有日誌輪替
- 無法追蹤歷史錯誤

#### 7. **缺少監控和健康檢查**
- 無法知道機器人是否正常運作
- 沒有性能指標收集

---

## 🔧 優化方案

### 1️⃣ **修復核心錯誤**

#### 修復 ChatState 初始化
```python
class ChatState:
    def __init__(self):
        self.histories = {}
        self.last_interaction = {}
        self.daily_usage = {}
        self.processing = set()
        self.last_message = {}
        self.line_quota_exceeded = False
        self.monthly_message_count = 0
        self.monthly_reset_date = None
        # 新增: 修復缺少的屬性
        self.request_count = 0
        self.last_request_time = time.time()
```

#### 修復圖片轉發功能
```python
# 使用正確的 API
from linebot.v3.messaging import ImageSendMessage

# Discord → Line 圖片轉發
messages.append(ImageSendMessage(
    originalContentUrl=image_url,
    previewImageUrl=image_url
))
```

### 2️⃣ **配置管理優化**

#### 創建配置類
```python
# config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    """機器人配置"""

    # Discord
    DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN')
    DISCORD_CHANNEL_ID: str = os.getenv('DISCORD_CHANNEL_ID')

    # Line
    LINE_CHANNEL_SECRET: str = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_GROUP_ID: str = os.getenv('LINE_GROUP_ID')

    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY')

    # 伺服器
    PORT: int = int(os.getenv('PORT', 8080))
    HOST: str = os.getenv('HOST', '0.0.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    # 配額限制
    AI_DAILY_LIMIT_PER_USER: int = int(os.getenv('AI_DAILY_LIMIT', 20))
    AI_REQUEST_PER_MINUTE: int = int(os.getenv('AI_RPM', 30))
    LINE_MONTHLY_LIMIT: int = int(os.getenv('LINE_MONTHLY_LIMIT', 500))
    LINE_WARNING_THRESHOLD: float = float(os.getenv('LINE_WARNING_THRESHOLD', 0.9))

    # AI 參數
    AI_TEMPERATURE: float = float(os.getenv('AI_TEMPERATURE', 0.7))
    AI_TOP_P: float = float(os.getenv('AI_TOP_P', 0.8))
    AI_TOP_K: int = int(os.getenv('AI_TOP_K', 40))
    AI_MAX_TOKENS: int = int(os.getenv('AI_MAX_TOKENS', 200))

    # 對話設定
    CONVERSATION_TIMEOUT: int = int(os.getenv('CONVERSATION_TIMEOUT', 1800))
    MAX_HISTORY_LENGTH: int = int(os.getenv('MAX_HISTORY', 10))

    # 相似度檢測
    MESSAGE_SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', 0.8))
    MESSAGE_LENGTH_DIFF: int = int(os.getenv('LENGTH_DIFF', 5))

config = BotConfig()
```

### 3️⃣ **資料持久化 - SQLite 整合**

#### 資料庫架構
```python
# database.py
import sqlite3
from datetime import datetime
from contextlib import contextmanager

class Database:
    def __init__(self, db_path='bot_data.db'):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """初始化資料庫表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 使用者表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    display_name TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # AI 使用記錄
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    count INTEGER DEFAULT 1,
                    UNIQUE(user_id, date)
                )
            ''')

            # 訊息記錄
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT,
                    user_id TEXT,
                    platform TEXT,
                    content TEXT,
                    message_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    forwarded BOOLEAN DEFAULT 0
                )
            ''')

            # Line API 配額追蹤
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS line_quota (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year_month TEXT UNIQUE,
                    message_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 統計資料
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    metric_value TEXT,
                    date DATE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
```

### 4️⃣ **日誌系統優化**

```python
# logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name='converge', log_dir='logs'):
    """設置完整的日誌系統"""

    # 創建日誌目錄
    os.makedirs(log_dir, exist_ok=True)

    # 創建 logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 格式化
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 檔案處理器 - 一般日誌
    file_handler = RotatingFileHandler(
        f'{log_dir}/bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 檔案處理器 - 錯誤日誌
    error_handler = RotatingFileHandler(
        f'{log_dir}/error.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 添加處理器
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger
```

### 5️⃣ **模組化重構**

#### 建議的專案結構
```
Converge/
├── main.py                 # 主程式入口(簡化)
├── config.py              # 配置管理
├── requirements.txt
├── .env.example
├── README.md
├── bot/                   # 機器人核心模組
│   ├── __init__.py
│   ├── discord_bot.py    # Discord 機器人邏輯
│   ├── line_bot.py       # Line 機器人邏輯
│   ├── bridge.py         # 橋接邏輯
│   └── ai_handler.py     # AI 處理邏輯
├── services/              # 服務層
│   ├── __init__.py
│   ├── database.py       # 資料庫服務
│   ├── cache.py          # 快取服務(Redis 可選)
│   ├── message_queue.py  # 訊息佇列
│   └── quota_manager.py  # 配額管理
├── models/                # 資料模型
│   ├── __init__.py
│   ├── user.py
│   ├── message.py
│   └── chat_state.py
├── utils/                 # 工具函數
│   ├── __init__.py
│   ├── logger.py         # 日誌工具
│   ├── validators.py     # 驗證工具
│   └── formatters.py     # 格式化工具
├── api/                   # Web API
│   ├── __init__.py
│   ├── webhook.py        # Line Webhook
│   ├── health.py         # 健康檢查
│   └── stats.py          # 統計 API
├── docs/                  # 文檔
│   ├── CONTRIBUTING.md
│   ├── CODE_OF_CONDUCT.md
│   ├── SECURITY.md
│   └── OPTIMIZATION_PLAN.md
└── tests/                 # 測試
    ├── __init__.py
    ├── test_discord_bot.py
    ├── test_line_bot.py
    └── test_ai_handler.py
```

---

## 🚀 新功能規劃

### 功能分類

#### 🎯 **核心功能增強**

##### 1. **多群組支援**
- 支援同時橋接多個 Discord 頻道和 Line 群組
- 靈活的路由規則配置
- 群組別名和標籤系統

```python
# 配置範例
BRIDGE_MAPPINGS = [
    {
        'name': 'Tech Team',
        'discord_channel': '123456789',
        'line_group': 'C1234567890abcdef',
        'bidirectional': True,
        'filters': ['tech', 'development']
    },
    {
        'name': 'Announcements',
        'discord_channel': '987654321',
        'line_group': 'C0987654321fedcba',
        'bidirectional': False,  # 單向: Discord → Line
        'filters': []
    }
]
```

##### 2. **訊息過濾與規則引擎**
- 關鍵字過濾(黑名單/白名單)
- 正則表達式匹配
- 使用者權限控制
- 訊息長度限制
- 敏感詞過濾

```python
# filters.py
class MessageFilter:
    def __init__(self):
        self.blacklist = set()  # 黑名單關鍵字
        self.whitelist = set()  # 白名單使用者
        self.regex_patterns = []  # 正則表達式

    def should_forward(self, message, user_id):
        """判斷訊息是否應該轉發"""
        # 檢查白名單
        if self.whitelist and user_id not in self.whitelist:
            return False

        # 檢查黑名單關鍵字
        if any(word in message.lower() for word in self.blacklist):
            return False

        # 檢查正則表達式
        if any(pattern.match(message) for pattern in self.regex_patterns):
            return False

        return True
```

##### 3. **媒體檔案支援增強**
- ✅ 圖片(PNG, JPG, GIF)
- 🆕 影片檔案
- 🆕 音訊檔案
- 🆕 文件檔案(PDF, DOCX 等)
- 🆕 貼圖轉發(Line 貼圖 → Discord Emoji)

##### 4. **訊息編輯與刪除同步**
- Discord 訊息編輯 → Line 更新通知
- Discord 訊息刪除 → Line 刪除通知
- 訊息撤回同步

#### 🤖 **AI 功能增強**

##### 5. **多模型支援**
```python
# ai_models.py
from enum import Enum

class AIModel(Enum):
    GEMINI_PRO = 'gemini-pro'
    GEMINI_PRO_VISION = 'gemini-pro-vision'
    GPT_4 = 'gpt-4'  # 可選
    CLAUDE = 'claude-3'  # 可選

class AIHandler:
    def __init__(self, default_model=AIModel.GEMINI_PRO):
        self.models = {
            AIModel.GEMINI_PRO: GeminiHandler(),
            AIModel.GEMINI_PRO_VISION: GeminiVisionHandler(),
        }
        self.default_model = default_model

    async def get_response(self, message, user_id, model=None):
        """根據指定模型生成回應"""
        model = model or self.default_model
        return await self.models[model].generate(message, user_id)
```

##### 6. **圖片分析功能**
- 使用 Gemini Pro Vision 分析 Line 傳來的圖片
- 自動圖片描述
- OCR 文字辨識

##### 7. **對話上下文增強**
- 更長的對話記憶(使用向量資料庫)
- 跨平台對話追蹤
- 對話摘要功能

##### 8. **自訂 AI 人格**
```python
# 系統提示詞配置
AI_PERSONALITIES = {
    'default': '你是一個友善的助手',
    'technical': '你是一個專業的技術專家',
    'casual': '你是一個輕鬆幽默的朋友',
}
```

#### 📊 **管理與監控功能**

##### 9. **Web 管理介面**
- 即時訊息監控
- 配額使用情況儀表板
- 使用者管理
- 群組設定管理
- 日誌查看

技術棧:
- 後端: FastAPI
- 前端: Vue.js 3 + Tailwind CSS
- 即時更新: WebSocket

##### 10. **統計與分析**
```python
# 統計指標
- 每日/每週/每月訊息量
- 活躍使用者數
- AI 使用率
- 平台分佈
- 高峰時段分析
- 回應時間統計
```

##### 11. **健康檢查端點**
```python
# api/health.py
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'discord': check_discord_connection(),
        'line': check_line_connection(),
        'database': check_database(),
        'uptime': get_uptime(),
        'version': '2.0.0'
    }

@app.route('/metrics')
def metrics():
    """Prometheus 格式的指標"""
    return generate_prometheus_metrics()
```

##### 12. **管理指令系統**
Discord 指令:
```python
# 管理員專用指令
!bridge status          # 顯示橋接狀態
!bridge list            # 列出所有橋接
!bridge add <discord> <line>  # 新增橋接
!bridge remove <id>     # 移除橋接
!stats                  # 顯示統計資訊
!quota                  # 顯示配額使用
!ai config <param>      # 設定 AI 參數
!filter add <keyword>   # 新增過濾關鍵字
```

#### 🔔 **通知與提醒**

##### 13. **關鍵字通知**
- 訂閱特定關鍵字
- 提及時發送通知
- 支援正則表達式

##### 14. **定時訊息**
- 定時發送訊息到指定群組
- 支援 Cron 格式
- 提醒功能

##### 15. **配額警告通知**
- Line API 配額接近上限時通知管理員
- AI 使用量統計報告
- 異常活動警報

#### 🔒 **安全性增強**

##### 16. **權限管理系統**
```python
# permissions.py
class Permission(Enum):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    BANNED = 'banned'

class PermissionManager:
    def __init__(self, db):
        self.db = db

    def check_permission(self, user_id, required_permission):
        """檢查使用者權限"""
        user_permission = self.get_user_permission(user_id)
        return user_permission.value >= required_permission.value

    def set_user_permission(self, user_id, permission):
        """設定使用者權限"""
        # 儲存到資料庫
        pass
```

##### 17. **速率限制增強**
```python
# rate_limiter.py
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)
        self.limits = {
            'messages_per_minute': 10,
            'messages_per_hour': 100,
            'ai_requests_per_day': 20
        }

    def check_rate_limit(self, user_id, limit_type):
        """檢查速率限制"""
        # 實作滑動視窗演算法
        pass
```

##### 18. **內容審核**
- AI 驅動的不當內容偵測
- 垃圾訊息過濾
- 惡意連結檢測

#### 🌐 **整合與擴充**

##### 19. **Webhook 整合**
- 接收外部服務的 Webhook
- 發送通知到 Discord/Line
- 支援 GitHub, GitLab, Jenkins 等

##### 20. **插件系統**
```python
# plugins/base.py
class Plugin:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        """訊息處理鉤子"""
        pass

    async def on_command(self, command, args):
        """指令處理鉤子"""
        pass

# 載入插件
plugin_manager = PluginManager()
plugin_manager.load_plugin('weather')
plugin_manager.load_plugin('translator')
```

##### 21. **翻譯功能**
- 自動偵測語言
- 即時翻譯
- 支援多語言

##### 22. **備份與還原**
- 自動資料庫備份
- 配置備份
- 一鍵還原功能

---

## 📅 實施優先級

### 🔴 **P0 - 緊急修復(立即實施)**
1. ✅ 修復 ChatState 初始化錯誤
2. ✅ 修復圖片轉發 API 錯誤
3. ✅ 添加基礎錯誤處理
4. ✅ 實施配置管理

**預估時間**: 1-2 天

### 🟠 **P1 - 重要優化(1-2 週內)**
5. ✅ 實施資料持久化(SQLite)
6. ✅ 完整的日誌系統
7. ✅ 模組化重構
8. ✅ 健康檢查端點
9. ✅ 多群組支援

**預估時間**: 1-2 週

### 🟡 **P2 - 功能增強(1 個月內)**
10. ✅ 訊息過濾系統
11. ✅ 管理指令系統
12. ✅ 統計與分析
13. ✅ 權限管理
14. ✅ 媒體檔案增強
15. ✅ AI 功能增強

**預估時間**: 2-4 週

### 🟢 **P3 - 進階功能(2-3 個月)**
16. ✅ Web 管理介面
17. ✅ 插件系統
18. ✅ 多 AI 模型支援
19. ✅ Webhook 整合
20. ✅ 翻譯功能

**預估時間**: 1-3 個月

---

## 🛠️ 技術棧升級建議

### 當前技術棧
```
Backend:
- Python 3.8+
- Flask (開發伺服器)
- Discord.py 2.3+
- Line Bot SDK 3.5+
- Google Generative AI

Storage:
- 無(僅記憶體)
```

### 建議升級方案

#### 選項 A: 輕量級升級(推薦快速實施)
```
Backend:
- Python 3.11+ (效能提升)
- Flask + Gunicorn (生產就緒)
- Discord.py 2.3+
- Line Bot SDK 3.5+
- Google Generative AI
- APScheduler (定時任務)

Storage:
- SQLite (內建,無需額外設定)
- JSON 檔案備份

Monitoring:
- Python logging
- 基礎健康檢查

Deployment:
- Docker (可選)
- Systemd service
```

#### 選項 B: 完整升級(推薦長期發展)
```
Backend:
- Python 3.11+
- FastAPI (取代 Flask,更快更現代)
- Discord.py 2.3+
- Line Bot SDK 3.5+
- Google Generative AI
- APScheduler
- Celery (背景任務)

Storage:
- PostgreSQL (主資料庫)
- Redis (快取 + 訊息佇列)
- MinIO / S3 (媒體檔案儲存)

Frontend (Web 管理介面):
- Vue.js 3
- Tailwind CSS
- Chart.js / ECharts

Monitoring:
- Prometheus (指標收集)
- Grafana (視覺化)
- Sentry (錯誤追蹤)

Deployment:
- Docker + Docker Compose
- Kubernetes (可選,大規模)
- CI/CD (GitHub Actions)
```

---

## 📈 效能優化建議

### 1. **非同步優化**
```python
# 使用 asyncio 完全非同步化
import asyncio
import aiohttp

# 批次處理訊息
async def batch_send_messages(messages):
    tasks = [send_message(msg) for msg in messages]
    await asyncio.gather(*tasks)
```

### 2. **快取策略**
```python
# 使用 Redis 或記憶體快取
from functools import lru_cache
import redis

# 快取使用者資訊
@lru_cache(maxsize=1000)
def get_user_info(user_id):
    # ...
    pass

# 快取 AI 回應(相同問題)
redis_client = redis.Redis()
def get_cached_ai_response(message_hash):
    return redis_client.get(f'ai_response:{message_hash}')
```

### 3. **連接池**
```python
# 資料庫連接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://...',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0
)
```

### 4. **訊息佇列**
```python
# 使用 Celery 處理背景任務
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def process_ai_request(user_id, message):
    # 非同步處理 AI 請求
    pass
```

---

## 🧪 測試策略

### 單元測試
```python
# tests/test_message_filter.py
import pytest
from bot.filters import MessageFilter

def test_blacklist_filter():
    filter = MessageFilter()
    filter.add_blacklist('spam')
    assert not filter.should_forward('This is spam', 'user123')
    assert filter.should_forward('This is ok', 'user123')
```

### 整合測試
```python
# tests/test_bridge.py
import pytest
from bot.bridge import MessageBridge

@pytest.mark.asyncio
async def test_discord_to_line():
    bridge = MessageBridge()
    result = await bridge.forward_message(
        source='discord',
        destination='line',
        message='Test message'
    )
    assert result.success
```

### 端到端測試
```bash
# 使用 pytest 和 mock
pytest tests/ --cov=bot --cov-report=html
```

---

## 📚 文檔更新需求

1. ✅ API 文檔(使用 Swagger/OpenAPI)
2. ✅ 架構設計文檔
3. ✅ 部署指南(Docker, Kubernetes)
4. ✅ 管理員手冊
5. ✅ 插件開發指南
6. ✅ 故障排除指南
7. ✅ 效能調優指南

---

## 🎯 成功指標

### 效能指標
- 訊息轉發延遲 < 1 秒
- API 回應時間 < 200ms
- 系統正常運行時間 > 99.9%
- 記憶體使用 < 500MB

### 可靠性指標
- 錯誤率 < 0.1%
- 資料遺失率 = 0%
- 自動恢復成功率 > 95%

### 使用者體驗指標
- AI 回應準確率 > 90%
- 使用者滿意度 > 4.5/5
- 功能使用率 > 70%

---

## 🚀 開始實施

### 第一階段:緊急修復(本週)
```bash
# 1. 創建新分支
git checkout -b feature/critical-fixes

# 2. 修復核心錯誤
# 3. 添加基礎測試
# 4. 更新文檔

# 5. 提交 PR
git add .
git commit -m "fix: critical bug fixes and config management"
git push origin feature/critical-fixes
```

### 第二階段:重構與優化(下週開始)
- 資料持久化實施
- 模組化重構
- 日誌系統完善

### 第三階段:新功能開發(第三週開始)
- 多群組支援
- 管理指令
- 統計分析

---

**準備好開始優化了嗎?** 讓我知道你想先從哪個部分開始! 🎉
