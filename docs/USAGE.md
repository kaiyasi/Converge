# 使用手冊

本手冊詳細說明 Converge 的所有功能和使用方法。

## 📋 目錄

- [快速開始](#快速開始)
- [Discord 功能](#discord-功能)
- [Line 功能](#line-功能)
- [AI 對話](#ai-對話)
- [訊息轉發](#訊息轉發)
- [Web Dashboard](#web-dashboard)
- [Webhook 整合](#webhook-整合)
- [配額管理](#配額管理)

---

## 快速開始

### 啟動 Bot

```bash
# 啟動虛擬環境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 啟動 Bot
python main_new.py
```

### 驗證運行狀態

成功啟動後，您會看到:

```
✅ 配置驗證通過
✅ 資料庫已初始化
✅ Line Bot 已初始化
✅ Discord Bot 已初始化
✅ AI 引擎已初始化
✅ 指令處理器已初始化
✅ Flask 路由已註冊
🤖 啟動 Discord Bot...
Discord 機器人已登入為 Converge#1234
✅ Discord Bot 已就緒
🌐 啟動 Flask 伺服器 (Host: 0.0.0.0, Port: 8080)
✨ Converge 已完全啟動
```

### 基本測試

**測試 Discord Bot:**
```
!ping
```

**測試 Line Bot:**
```
你好
```

**測試 Web Dashboard:**
```
http://localhost:8080/
```

---

## Discord 功能

### 指令列表

Converge 提供豐富的 Discord 指令。

#### !status - 系統狀態

查看 Bot 的運行狀態。

**語法:**
```
!status
```

**範例回應:**
```
🤖 系統狀態報告

✅ Discord Bot: 在線
   延遲: 125.5 ms
   登入為: Converge#1234

✅ AI 引擎: 正常
   模型: gemini-pro

✅ 資料庫: 正常
   使用者: 42 位
   訊息: 1,234 則

⏰ 運行時間: 1 天 5 小時 30 分鐘
```

#### !quota - 配額查詢

查看 API 配額使用狀況。

**語法:**
```
!quota [使用者ID]
```

**範例:**
```
!quota
!quota U1234567890abcdef
```

**回應:**
```
📊 API 配額狀態

✅ AI 對話 (每日/每人)
   使用: 5 / 20 (25.0%)
   剩餘: 15 次
   重置: 5 小時後

✅ Line API (每月)
   使用: 250 / 500 (50.0%)
   剩餘: 250 則
   重置: 12 天後
```

#### !stats - 統計資訊

查看系統統計資訊。

**語法:**
```
!stats
```

**回應:**
```
📊 系統統計

👥 使用者統計
   總數: 42 位
   Line: 25 位
   Discord: 17 位

💬 訊息統計
   總數: 1,234 則
   今日: 89 則
   Line: 800 則
   Discord: 434 則

🗄️ 資料庫
   大小: 1.5 MB
   對話記錄: 567 則
```

#### !users - 使用者列表

查看使用者列表。

**語法:**
```
!users [平台] [數量]
```

**參數:**
- `平台` (可選): `line` 或 `discord`
- `數量` (可選): 顯示數量，預設 10

**範例:**
```
!users
!users line
!users discord 20
```

**回應:**
```
👥 使用者列表 (Line)

1. 張三 (U123456)
   訊息: 125 則
   加入: 2025-10-01

2. 李四 (U789012)
   訊息: 89 則
   加入: 2025-10-05

...

總計: 25 位使用者
```

#### !dbstats - 資料庫統計

查看資料庫詳細統計。

**語法:**
```
!dbstats
```

**回應:**
```
🗄️ 資料庫統計

📊 資料表統計
   users: 42 筆
   messages: 1,234 筆
   chat_history: 567 筆
   quotas: 84 筆
   group_mappings: 2 筆

💾 儲存空間
   資料庫大小: 1.5 MB
   備份數量: 5 個
   最後備份: 2 小時前
```

#### !ping - 延遲測試

測試 Bot 的回應延遲。

**語法:**
```
!ping
```

**回應:**
```
🏓 Pong!
延遲: 125.5 ms
```

#### !help - 幫助訊息

顯示指令幫助。

**語法:**
```
!help [指令名稱]
```

**範例:**
```
!help
!help status
```

**回應:**
```
🤖 Converge 指令列表

📊 資訊查詢
   !status  - 查看系統狀態
   !quota   - 查看 API 配額
   !stats   - 查看統計資訊
   !users   - 查看使用者列表
   !dbstats - 查看資料庫統計

🔧 工具
   !ping    - 測試延遲

❓ 幫助
   !help    - 顯示此訊息

💡 提示: 私訊 Line Bot 即可開始 AI 對話
```

---

## Line 功能

### 私訊功能

#### AI 對話

直接私訊 Line Bot 即可開始對話:

```
你: 你好
Bot: 🤖 你好！有什麼我可以幫助你的嗎？

你: 請問今天天氣如何？
Bot: 🤖 抱歉，我目前無法查詢即時天氣資訊...
```

**特色:**
- ✅ 支援上下文對話 (記憶前 10 輪對話)
- ✅ 自動配額管理
- ✅ 回應超時保護
- ✅ 錯誤處理與降級

#### 圖片訊息

發送圖片給 Bot:

```
[發送圖片]
Bot: 🖼️ 已收到圖片，正在轉發到 Discord...
```

**支援格式:**
- JPG/JPEG
- PNG
- GIF
- WebP

**限制:**
- 最大檔案大小: 10 MB

#### 檔案訊息

發送檔案給 Bot:

```
[發送 PDF 檔案]
Bot: 📄 已收到檔案: report.pdf (1.2 MB)
     正在轉發到 Discord...
```

**支援類型:**
- 文件: PDF, DOC, DOCX, TXT
- 壓縮檔: ZIP, RAR
- 影片: MP4, MOV, AVI
- 音訊: MP3, M4A, WAV

### 群組功能

#### 群組指令

在 Line 群組中使用 `#` 開頭的指令:

##### #status - 系統狀態

```
#status
```

Bot 會回覆系統狀態資訊。

##### #help - 幫助訊息

```
#help
```

顯示可用的群組指令。

#### 群組訊息轉發

群組中的訊息會自動轉發到 Discord (如果啟用):

```
Line 群組:
張三: 大家好！

Discord 頻道:
[Line] 張三: 大家好！
```

---

## AI 對話

### 基本對話

**開始對話:**
```
你: 你好，請介紹一下自己
Bot: 🤖 你好！我是 Converge，一個整合了 Google Gemini AI 的智能助手。我可以回答問題、提供建議，並協助處理各種對話需求。有什麼我可以幫助你的嗎？
```

### 多輪對話

Bot 會記住前 10 輪對話:

```
你: 我想學 Python
Bot: 🤖 太好了！Python 是很適合初學者的程式語言...

你: 有推薦的學習資源嗎？
Bot: 🤖 基於您想學 Python，我推薦以下資源...
      [Bot 記得之前的對話內容]
```

### 對話限制

- **每日配額:** 預設每位使用者每日 20 次
- **訊息長度:** 最長 2000 字元
- **回應時間:** 約 1-3 秒

### 配額用完時

```
你: 你好
Bot: ⚠️ 您今日的 AI 對話配額已用完 (20/20)
     明日 00:00 將自動重置

     💡 提示: 使用 !quota 指令查看詳細配額
```

### 錯誤處理

如果 AI 無法回應:

```
你: [複雜問題]
Bot: ❌ AI 服務暫時不可用，請稍後再試。

可能原因:
- API 配額超限
- 網路連線問題
- 內容被安全過濾
```

---

## 訊息轉發

### Line → Discord

Line 的訊息會自動轉發到 Discord:

**文字訊息:**
```
Line 私訊:
張三: 測試訊息

Discord 頻道:
[Line] 張三: 測試訊息
```

**圖片訊息:**
```
Line: [發送圖片]

Discord:
[Line] 張三 發送了圖片
[顯示圖片]
```

### Discord → Line

Discord 的訊息也可以轉發到 Line (需配置):

```
Discord 頻道:
李四: 大家好

Line 群組:
[Discord] 李四: 大家好
```

### 訊息格式轉換

系統會自動處理不同平台的訊息格式:

| Line | Discord |
|------|---------|
| 圖片 | Embed + 圖片 URL |
| 貼圖 | 🎨 [貼圖: 名稱] |
| 位置 | 📍 [位置: 地址] |
| 檔案 | 📎 檔案連結 |

---

## Web Dashboard

### 存取 Dashboard

```
http://localhost:8080/
```

如果部署到伺服器:
```
https://your-domain.com/
```

### Dashboard 功能

#### 首頁 - 即時統計

- 📊 即時數據
  - 總使用者數
  - 今日訊息數
  - 平台分布
  - 系統資源 (CPU, Memory, Disk)

- 📈 圖表
  - 每日訊息趨勢 (7 天)
  - 平台分布圓餅圖
  - 小時訊息分布

- ⚡ 快速操作
  - 重新整理資料
  - 查看詳細統計
  - 系統健康檢查

#### 使用者管理 (/users)

**功能:**
- 查看所有使用者
- 平台篩選 (Line/Discord)
- 搜尋使用者
- 查看使用者詳情
  - 訊息數量
  - 配額使用
  - 加入時間

**操作:**
1. 選擇平台或查看全部
2. 使用搜尋框查找特定使用者
3. 點擊使用者查看詳情

#### 訊息記錄 (/messages)

**功能:**
- 查看所有訊息
- 關鍵字搜尋
- 平台篩選
- 訊息類型篩選

**操作:**
1. 輸入關鍵字搜尋
2. 選擇平台篩選
3. 查看訊息詳情

#### 系統設定 (/settings)

**功能:**
- 系統資訊
  - Python 版本
  - 運行時間
  - 資料庫資訊
- 資料庫管理
  - 備份資料庫
  - 查看備份列表
  - 資料庫優化
- 配置檢視

---

## Webhook 整合

### Line Webhook

Line 平台會自動呼叫此 Webhook。

**端點:**
```
POST https://your-domain.com/callback
```

**設定:**
在 Line Developers Console 設定 Webhook URL。

### GitHub Webhook

接收 GitHub 事件並轉發到 Discord。

**端點:**
```
POST https://your-domain.com/github
```

**支援事件:**
- `push` - 代碼推送
- `pull_request` - Pull Request
- `issues` - Issue 事件

**設定步驟:**

1. 前往 GitHub Repository → Settings → Webhooks
2. 點擊 "Add webhook"
3. 填入:
   - Payload URL: `https://your-domain.com/github`
   - Content type: `application/json`
   - Events: 選擇需要的事件
4. 點擊 "Add webhook"

**Discord 通知範例:**

```
🔔 GitHub 通知

📦 Repository: kaiyasi/Converge
🌿 Branch: main
👤 Author: kaiyasi

📝 Commit Message:
   feat: 新增 Webhook 系統

🔗 查看變更: https://github.com/...
```

### 自訂 Webhook

發送自訂訊息到 Discord 或 Line。

**端點:**
```
POST https://your-domain.com/custom
```

**請求 Body:**
```json
{
  "platform": "discord",
  "target": "123456789",
  "message": "測試訊息"
}
```

**參數:**
- `platform` (str, 必填): `discord` 或 `line`
- `target` (str, 可選): 目標 ID (channel_id 或 user_id)
- `message` (str, 必填): 訊息內容

**Python 範例:**
```python
import requests

response = requests.post(
    'http://localhost:8080/custom',
    json={
        'platform': 'discord',
        'message': '自動化通知: 任務完成'
    }
)

if response.status_code == 200:
    print('訊息發送成功')
```

**cURL 範例:**
```bash
curl -X POST http://localhost:8080/custom \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "discord",
    "message": "測試訊息"
  }'
```

---

## 配額管理

### 查看配額

**Discord 指令:**
```
!quota
```

**Web Dashboard:**
```
http://localhost:8080/
```
查看首頁的配額統計。

### 配額類型

#### AI 每日配額

- **預設限制:** 20 次/天/人
- **重置時間:** 每日 00:00
- **用途:** AI 對話功能

#### Line 每月配額

- **預設限制:** 500 則/月
- **重置時間:** 每月 1 日
- **用途:** Line 訊息發送

### 配額警告

當配額使用達到 80% 時:

```
⚠️ 配額警告

AI 對話配額已使用 80% (16/20)
剩餘 4 次請求

💡 建議:
- 明智使用剩餘配額
- 查看 Dashboard 監控使用量
- 明日將自動重置
```

### 配額用盡

```
❌ 配額已用完

您今日的 AI 對話配額已用完 (20/20)

⏰ 重置時間: 明日 00:00
📊 查看詳情: !quota
```

### 調整配額

編輯 `.env`:
```env
# 增加每日 AI 配額
AI_DAILY_LIMIT_PER_USER=50

# 增加 Line 每月配額
LINE_MONTHLY_LIMIT=1000
```

重新啟動 Bot 以套用。

---

## 常見使用情境

### 情境 1: 團隊協作

**設置:**
1. 建立 Discord 頻道: `#line-sync`
2. 建立 Line 群組並邀請 Bot
3. 配置 `LINE_GROUP_ID` 和 `DISCORD_CHANNEL_ID`

**使用:**
- Line 群組討論自動同步到 Discord
- Discord 訊息回傳到 Line
- 跨平台無縫協作

### 情境 2: AI 客服

**設置:**
1. 加 Line Bot 為好友
2. 自訂 AI 提示詞 (optional)

**使用:**
- 使用者私訊 Line Bot
- AI 自動回覆常見問題
- 配額控制避免濫用

### 情境 3: 自動化通知

**設置:**
1. 設定 GitHub Webhook
2. 或使用自訂 Webhook API

**使用:**
- GitHub 有新 commit → Discord 通知
- CI/CD 完成 → Line 通知
- 監控警報 → 雙平台通知

---

## 最佳實踐

1. **配額管理**
   - 定期查看 Dashboard
   - 監控配額使用趨勢
   - 提前調整限制

2. **訊息管理**
   - 使用搜尋功能查找歷史訊息
   - 定期備份重要對話
   - 清理測試訊息

3. **安全性**
   - 不要在對話中分享敏感資訊
   - 定期查看使用者列表
   - 監控異常活動

4. **效能優化**
   - 避免發送過大檔案
   - 控制訊息頻率
   - 定期清理資料庫

---

## 故障排除

### Bot 沒有回應

**檢查:**
1. Bot 是否正在運行
2. 網路連線是否正常
3. 查看日誌檔案: `logs/bot.log`

### AI 無法回應

**可能原因:**
- 配額已用完
- API Key 無效
- 網路問題

**解決方案:**
1. 使用 `!quota` 檢查配額
2. 檢查 `.env` 中的 `GOOGLE_API_KEY`
3. 查看錯誤日誌

### 訊息未轉發

**檢查:**
1. 群組 ID 是否正確
2. Bot 是否在群組中
3. Webhook 是否設定正確

---

**需要更多幫助?** 查看 [FAQ](./FAQ.md) 或 [提出問題](https://github.com/kaiyasi/Converge/issues)

**[⬆ 回到文檔中心](./README.md)**
