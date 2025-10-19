# 配置說明

本文檔詳細說明 Converge 的所有配置選項。

## 📋 目錄

- [環境變數](#環境變數)
- [Discord 設定](#discord-設定)
- [Line 設定](#line-設定)
- [AI 設定](#ai-設定)
- [伺服器設定](#伺服器設定)
- [資料庫設定](#資料庫設定)
- [配額設定](#配額設定)
- [日誌設定](#日誌設定)
- [進階設定](#進階設定)

---

## 環境變數

### .env 檔案結構

```env
# ====================================
# Discord Bot 設定
# ====================================
DISCORD_TOKEN=你的_Discord_Bot_Token
DISCORD_CHANNEL_ID=你的_Discord_頻道_ID

# ====================================
# Line Bot 設定
# ====================================
LINE_CHANNEL_SECRET=你的_Line_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的_Line_Access_Token
LINE_GROUP_ID=你的_Line_群組_ID

# ====================================
# Google Gemini AI 設定
# ====================================
GOOGLE_API_KEY=你的_Gemini_API_Key

# ====================================
# 伺服器設定
# ====================================
HOST=0.0.0.0
PORT=8080
DEBUG=False

# ====================================
# AI 功能設定
# ====================================
AI_DAILY_LIMIT_PER_USER=20
AI_MODEL_NAME=gemini-pro
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000

# ====================================
# Line API 配額設定
# ====================================
LINE_MONTHLY_LIMIT=500

# ====================================
# 資料庫設定
# ====================================
DATABASE_PATH=data/bot.db
DB_BACKUP_ENABLED=True
DB_BACKUP_INTERVAL=24

# ====================================
# 日誌設定
# ====================================
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
LOG_ENABLE_JSON=False

# ====================================
# 安全設定
# ====================================
WEBHOOK_VERIFY_SIGNATURE=True
MAX_MESSAGE_LENGTH=2000
RATE_LIMIT_ENABLED=True
```

---

## Discord 設定

### 必要設定

#### DISCORD_TOKEN

Discord Bot 的認證 Token。

- **類型:** `str`
- **必填:** ✅ 是
- **取得方式:** [Discord 設置教學](./setup/DISCORD.md)
- **範例:** `MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.ABCDEF.aBcDeFgHiJkLmNoPqRsTuVwXyZ`

```env
DISCORD_TOKEN=你的_Discord_Bot_Token
```

⚠️ **安全提醒:** 絕對不要將 Token 公開或提交到 Git。

#### DISCORD_CHANNEL_ID

預設的 Discord 頻道 ID (用於轉發訊息)。

- **類型:** `int`
- **必填:** ✅ 是
- **取得方式:** 啟用開發者模式 → 右鍵頻道 → 複製 ID
- **範例:** `1234567890123456789`

```env
DISCORD_CHANNEL_ID=1234567890123456789
```

### 可選設定

#### DISCORD_COMMAND_PREFIX

Discord 指令前綴。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `!`
- **範例:** `!`, `$`, `/`

```env
DISCORD_COMMAND_PREFIX=!
```

#### DISCORD_STATUS_MESSAGE

Bot 的自訂狀態訊息。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `!help 查看指令`

```env
DISCORD_STATUS_MESSAGE=🤖 Converge | !help
```

---

## Line 設定

### 必要設定

#### LINE_CHANNEL_SECRET

Line Channel 的 Secret，用於驗證 Webhook 簽名。

- **類型:** `str`
- **必填:** ✅ 是
- **取得方式:** [Line 設置教學](./setup/LINE.md)
- **範例:** `abc123def456ghi789jkl012mno345pq`

```env
LINE_CHANNEL_SECRET=你的_Channel_Secret
```

#### LINE_CHANNEL_ACCESS_TOKEN

Line Bot 的 Access Token，用於發送訊息。

- **類型:** `str`
- **必填:** ✅ 是
- **取得方式:** [Line 設置教學](./setup/LINE.md)
- **範例:** `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890==`

```env
LINE_CHANNEL_ACCESS_TOKEN=你的_Access_Token
```

#### LINE_GROUP_ID

預設的 Line 群組 ID (用於轉發訊息)。

- **類型:** `str`
- **必填:** ⚠️ 使用群組功能時必填
- **取得方式:** 查看 Bot 日誌或使用 Line API
- **範例:** `C1234567890abcdef1234567890abcdef`

```env
LINE_GROUP_ID=你的_群組_ID
```

### 可選設定

#### LINE_COMMAND_PREFIX

Line 群組指令前綴。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `#`

```env
LINE_COMMAND_PREFIX=#
```

---

## AI 設定

### 必要設定

#### GOOGLE_API_KEY

Google Gemini API 金鑰。

- **類型:** `str`
- **必填:** ✅ 是
- **取得方式:** [Gemini 設置教學](./setup/GEMINI.md)
- **範例:** `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

```env
GOOGLE_API_KEY=你的_API_Key
```

### AI 行為設定

#### AI_MODEL_NAME

使用的 Gemini 模型名稱。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `gemini-pro`
- **可選值:**
  - `gemini-pro` - 一般對話
  - `gemini-pro-vision` - 圖片理解
  - `gemini-ultra` - 最強性能 (需申請)

```env
AI_MODEL_NAME=gemini-pro
```

#### AI_TEMPERATURE

AI 回應的創造性參數。

- **類型:** `float`
- **必填:** ❌ 否
- **預設值:** `0.7`
- **範圍:** `0.0` - `1.0`
- **說明:**
  - `0.0` - 最保守、確定的回應
  - `0.5` - 平衡創造性與一致性
  - `1.0` - 最大創造性、較隨機

```env
AI_TEMPERATURE=0.7
```

#### AI_MAX_TOKENS

AI 回應的最大長度 (tokens)。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `1000`
- **範圍:** `1` - `32768`
- **建議:** `1000` - `2000`

```env
AI_MAX_TOKENS=1000
```

#### AI_DAILY_LIMIT_PER_USER

每位使用者每日可使用 AI 的次數。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `20`
- **建議:** `10` - `50`

```env
AI_DAILY_LIMIT_PER_USER=20
```

---

## 伺服器設定

### HOST

Flask 伺服器監聽的 IP 位址。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `0.0.0.0`
- **常用值:**
  - `0.0.0.0` - 允許外部連線
  - `127.0.0.1` - 僅本機存取

```env
HOST=0.0.0.0
```

### PORT

Flask 伺服器監聽的埠號。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `8080`
- **範圍:** `1024` - `65535`

```env
PORT=8080
```

### DEBUG

是否啟用 Debug 模式。

- **類型:** `bool`
- **必填:** ❌ 否
- **預設值:** `False`
- **說明:**
  - `True` - 開發模式，詳細日誌、自動重載
  - `False` - 生產模式，精簡日誌

```env
DEBUG=False
```

⚠️ **警告:** 生產環境請務必設為 `False`。

---

## 資料庫設定

### DATABASE_PATH

SQLite 資料庫檔案路徑。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `data/bot.db`

```env
DATABASE_PATH=data/bot.db
```

### DB_BACKUP_ENABLED

是否啟用自動備份。

- **類型:** `bool`
- **必填:** ❌ 否
- **預設值:** `True`

```env
DB_BACKUP_ENABLED=True
```

### DB_BACKUP_INTERVAL

備份間隔 (小時)。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `24`

```env
DB_BACKUP_INTERVAL=24
```

### DB_BACKUP_PATH

備份檔案存放目錄。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `data/backups`

```env
DB_BACKUP_PATH=data/backups
```

---

## 配額設定

### LINE_MONTHLY_LIMIT

Line API 每月訊息配額。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `500`
- **說明:** Line 免費方案每月 500 則訊息

```env
LINE_MONTHLY_LIMIT=500
```

### QUOTA_WARNING_THRESHOLD

配額警告閾值 (百分比)。

- **類型:** `float`
- **必填:** ❌ 否
- **預設值:** `0.8` (80%)

```env
QUOTA_WARNING_THRESHOLD=0.8
```

---

## 日誌設定

### LOG_LEVEL

日誌記錄級別。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `INFO`
- **可選值:**
  - `DEBUG` - 最詳細
  - `INFO` - 一般資訊
  - `WARNING` - 警告訊息
  - `ERROR` - 錯誤訊息
  - `CRITICAL` - 嚴重錯誤

```env
LOG_LEVEL=INFO
```

### LOG_DIR

日誌檔案存放目錄。

- **類型:** `str`
- **必填:** ❌ 否
- **預設值:** `logs`

```env
LOG_DIR=logs
```

### LOG_MAX_BYTES

單個日誌檔案最大大小 (bytes)。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `10485760` (10 MB)

```env
LOG_MAX_BYTES=10485760
```

### LOG_BACKUP_COUNT

保留的日誌備份數量。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `5`

```env
LOG_BACKUP_COUNT=5
```

### LOG_ENABLE_JSON

是否啟用 JSON 格式日誌。

- **類型:** `bool`
- **必填:** ❌ 否
- **預設值:** `False`

```env
LOG_ENABLE_JSON=False
```

---

## 進階設定

### WEBHOOK_VERIFY_SIGNATURE

是否驗證 Webhook 簽名。

- **類型:** `bool`
- **必填:** ❌ 否
- **預設值:** `True`
- **說明:** 生產環境強烈建議啟用

```env
WEBHOOK_VERIFY_SIGNATURE=True
```

### MAX_MESSAGE_LENGTH

最大訊息長度。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `2000`

```env
MAX_MESSAGE_LENGTH=2000
```

### RATE_LIMIT_ENABLED

是否啟用請求限流。

- **類型:** `bool`
- **必填:** ❌ 否
- **預設值:** `True`

```env
RATE_LIMIT_ENABLED=True
```

### MAX_REQUESTS_PER_MINUTE

每分鐘最大請求數。

- **類型:** `int`
- **必填:** ❌ 否
- **預設值:** `60`

```env
MAX_REQUESTS_PER_MINUTE=60
```

---

## 配置範例

### 開發環境

```env
# 開發環境配置
DEBUG=True
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8080

# 寬鬆的配額限制
AI_DAILY_LIMIT_PER_USER=100
LINE_MONTHLY_LIMIT=1000

# 停用安全檢查 (僅開發)
WEBHOOK_VERIFY_SIGNATURE=False
RATE_LIMIT_ENABLED=False
```

### 生產環境

```env
# 生產環境配置
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8080

# 嚴格的配額限制
AI_DAILY_LIMIT_PER_USER=20
LINE_MONTHLY_LIMIT=500

# 啟用所有安全檢查
WEBHOOK_VERIFY_SIGNATURE=True
RATE_LIMIT_ENABLED=True

# 啟用備份
DB_BACKUP_ENABLED=True
DB_BACKUP_INTERVAL=12
```

### 測試環境

```env
# 測試環境配置
DEBUG=False
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8080

# 極低配額 (快速測試配額機制)
AI_DAILY_LIMIT_PER_USER=5
LINE_MONTHLY_LIMIT=100

# 使用測試資料庫
DATABASE_PATH=data/test_bot.db
```

---

## 配置驗證

### 使用內建驗證工具

```bash
python -c "from config import BotConfig; config = BotConfig(); print('✅ 配置驗證通過')"
```

### 檢查必要設定

```python
# check_config.py
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'DISCORD_TOKEN',
    'DISCORD_CHANNEL_ID',
    'LINE_CHANNEL_SECRET',
    'LINE_CHANNEL_ACCESS_TOKEN',
    'GOOGLE_API_KEY'
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print(f"❌ 缺少必要環境變數: {', '.join(missing)}")
else:
    print("✅ 所有必要環境變數已設定")
```

---

## 常見問題

### Q: 如何重置配額？

**A:** 配額會自動重置:
- AI 每日配額: 每天 00:00 重置
- Line 每月配額: 每月 1 日重置

手動重置:
```bash
python -c "from models.quota import Quota; Quota.reset_all()"
```

### Q: 如何更改配置後生效？

**A:** 需要重新啟動 Bot:
```bash
# 停止 Bot (Ctrl+C)
# 修改 .env
# 重新啟動
python main_new.py
```

### Q: 如何備份配置？

**A:**
```bash
# 備份 .env
cp .env .env.backup

# 備份資料庫
cp data/bot.db data/bot.db.backup
```

---

## 最佳實踐

1. **環境分離**
   - 開發、測試、生產使用不同的 `.env` 檔案
   - 使用 `.env.development`、`.env.production` 等

2. **安全管理**
   - 絕對不要提交 `.env` 到 Git
   - 使用 `.env.example` 作為範本
   - 定期輪換 Token 和 API Key

3. **配額監控**
   - 定期檢查 Dashboard
   - 設定合理的警告閾值
   - 備用方案 (配額用完時)

4. **日誌管理**
   - 生產環境使用 INFO 級別
   - 定期清理舊日誌
   - 考慮使用外部日誌服務

5. **備份策略**
   - 啟用自動備份
   - 定期手動備份
   - 測試恢復流程

---

**[⬆ 回到文檔中心](./README.md)**
