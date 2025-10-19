# 指令參考

完整的 Converge 指令列表和詳細說明。

## 📋 目錄

- [Discord 指令](#discord-指令)
- [Line 指令](#line-指令)
- [API 指令](#api-指令)
- [指令權限](#指令權限)
- [自訂指令](#自訂指令)

---

## Discord 指令

所有 Discord 指令使用 `!` 前綴 (可自訂)。

### 系統資訊

#### !status

查看 Bot 的完整運行狀態。

**語法:**
```
!status
```

**權限:** 所有人

**回應範例:**
```
🤖 系統狀態報告

✅ Discord Bot: 在線
   延遲: 125.5 ms
   登入為: Converge#1234
   伺服器: 3 個
   頻道: 15 個

✅ AI 引擎: 正常
   模型: gemini-pro
   回應時間: 1.2s

✅ 資料庫: 正常
   使用者: 42 位
   訊息: 1,234 則
   配額記錄: 84 筆

💾 系統資源
   CPU: 15.2%
   記憶體: 256.5 MB / 1024 MB (25.0%)
   磁碟: 60.2% 使用

⏰ 運行時間: 1 天 5 小時 30 分鐘
📅 啟動時間: 2025-10-18 13:00:00
```

**用途:**
- 檢查 Bot 是否正常運行
- 查看延遲和效能
- 監控系統資源

---

#### !ping

測試 Bot 的回應延遲。

**語法:**
```
!ping
```

**權限:** 所有人

**回應範例:**
```
🏓 Pong!
延遲: 125.5 ms
WebSocket: 123.2 ms
```

**用途:**
- 快速測試連線
- 檢查延遲

---

### 配額管理

#### !quota

查看 API 配額使用狀況。

**語法:**
```
!quota [使用者ID] [平台]
```

**參數:**
- `使用者ID` (可選): 查詢特定使用者
- `平台` (可選): `line` 或 `discord`

**範例:**
```
!quota
!quota U1234567890abcdef line
!quota @user
```

**權限:**
- 無參數: 所有人 (查詢自己)
- 帶參數: 管理員

**回應範例:**

**情況 1: 正常使用**
```
📊 API 配額狀態
使用者: 張三 (U123456)

✅ AI 對話 (每日/每人)
   使用: 5 / 20 (25.0%)
   剩餘: 15 次
   重置: 5 小時 30 分鐘後
   進度: ▰▰▰▰▱▱▱▱▱▱

✅ Line API (每月)
   使用: 250 / 500 (50.0%)
   剩餘: 250 則
   重置: 12 天後
   進度: ▰▰▰▰▰▱▱▱▱▱
```

**情況 2: 配額警告 (>80%)**
```
⚠️ AI 對話配額警告
   使用: 17 / 20 (85.0%)
   剩餘: 3 次
   進度: ▰▰▰▰▰▰▰▰▰▱

💡 建議:
- 明智使用剩餘配額
- 配額將在明日 00:00 重置
```

**情況 3: 配額用盡**
```
❌ AI 對話配額已用完
   使用: 20 / 20 (100.0%)
   剩餘: 0 次
   進度: ▰▰▰▰▰▰▰▰▰▰

⏰ 重置時間: 明日 00:00 (5 小時 30 分後)
```

**用途:**
- 查看配額使用狀況
- 監控 API 用量
- 管理員查詢使用者配額

---

### 統計資訊

#### !stats

查看系統統計資訊。

**語法:**
```
!stats [類型] [時間範圍]
```

**參數:**
- `類型` (可選): `users`, `messages`, `platform`, `all`
- `時間範圍` (可選): `today`, `week`, `month`, `all`

**範例:**
```
!stats
!stats users
!stats messages today
!stats platform week
```

**權限:** 所有人

**回應範例:**

**基本統計 (!stats)**
```
📊 系統統計

👥 使用者統計
   總數: 42 位
   Line: 25 位 (59.5%)
   Discord: 17 位 (40.5%)
   今日新增: 3 位

💬 訊息統計
   總數: 1,234 則
   今日: 89 則
   本週: 456 則
   Line: 800 則 (64.8%)
   Discord: 434 則 (35.2%)

🤖 AI 對話
   總請求: 678 次
   今日: 45 次
   成功率: 98.5%

🗄️ 資料庫
   大小: 1.5 MB
   對話記錄: 567 則
   配額記錄: 84 筆
```

**使用者統計 (!stats users)**
```
👥 使用者統計報告

📈 總覽
   總使用者: 42 位
   活躍使用者: 28 位 (66.7%)
   本週新增: 5 位

📊 平台分布
   Line: 25 位 (59.5%)
   Discord: 17 位 (40.5%)

🏆 Top 5 活躍使用者
   1. 張三 - 125 則訊息
   2. 李四 - 89 則訊息
   3. 王五 - 67 則訊息
   4. 趙六 - 45 則訊息
   5. 錢七 - 34 則訊息
```

**訊息統計 (!stats messages today)**
```
💬 訊息統計 - 今日

📊 總覽
   總訊息數: 89 則
   Line: 56 則 (62.9%)
   Discord: 33 則 (37.1%)

📈 小時分布
   高峰時段: 14:00 - 15:00 (12 則)
   低峰時段: 03:00 - 04:00 (0 則)

📝 訊息類型
   文字: 75 則 (84.3%)
   圖片: 8 則 (9.0%)
   檔案: 4 則 (4.5%)
   其他: 2 則 (2.2%)
```

**用途:**
- 了解系統使用狀況
- 分析使用者活躍度
- 監控訊息趨勢

---

#### !users

查看使用者列表。

**語法:**
```
!users [平台] [數量] [排序]
```

**參數:**
- `平台` (可選): `line`, `discord`, `all`
- `數量` (可選): 顯示數量 (1-50)，預設 10
- `排序` (可選): `messages`, `date`, `name`

**範例:**
```
!users
!users line
!users discord 20
!users all 10 messages
```

**權限:** 管理員

**回應範例:**
```
👥 使用者列表 (Line) - 依訊息數排序
顯示: 10 / 25 位

1. 張三 (U123456)
   📊 訊息: 125 則
   🤖 AI 使用: 15/20
   📅 加入: 2025-10-01
   ✅ 狀態: 活躍

2. 李四 (U789012)
   📊 訊息: 89 則
   🤖 AI 使用: 8/20
   📅 加入: 2025-10-05
   ✅ 狀態: 活躍

...

10. 錢十 (U345678)
    📊 訊息: 12 則
    🤖 AI 使用: 2/20
    📅 加入: 2025-10-15
    ⚠️ 狀態: 不活躍

---
總計: 25 位使用者 | 使用 !users all 50 查看全部
```

**用途:**
- 管理使用者
- 查看活躍度
- 識別異常帳號

---

#### !dbstats

查看資料庫詳細統計。

**語法:**
```
!dbstats [詳細程度]
```

**參數:**
- `詳細程度` (可選): `simple`, `detailed`

**範例:**
```
!dbstats
!dbstats detailed
```

**權限:** 管理員

**回應範例:**

**簡單模式 (!dbstats)**
```
🗄️ 資料庫統計

📊 資料表統計
   users: 42 筆
   messages: 1,234 筆
   chat_history: 567 筆
   quotas: 84 筆
   system_quotas: 2 筆
   group_mappings: 2 筆

💾 儲存空間
   資料庫大小: 1.5 MB
   索引大小: 0.3 MB
   總計: 1.8 MB

🔄 備份資訊
   最後備份: 2 小時前
   備份數量: 5 個
   備份總大小: 7.5 MB
```

**詳細模式 (!dbstats detailed)**
```
🗄️ 資料庫詳細統計

📊 資料表統計
┌──────────────────┬────────┬─────────┐
│ 資料表           │ 筆數   │ 大小    │
├──────────────────┼────────┼─────────┤
│ users            │ 42     │ 0.5 MB  │
│ messages         │ 1,234  │ 0.8 MB  │
│ chat_history     │ 567    │ 0.1 MB  │
│ quotas           │ 84     │ 0.05 MB │
│ system_quotas    │ 2      │ 0.01 MB │
│ group_mappings   │ 2      │ 0.01 MB │
└──────────────────┴────────┴─────────┘

📈 成長趨勢 (本週)
   新增使用者: +5
   新增訊息: +456
   新增對話: +123

🔍 資料完整性
   ✅ 無孤立記錄
   ✅ 索引完整
   ✅ 無損壞資料

💡 最後優化: 1 天前
```

**用途:**
- 監控資料庫狀態
- 評估儲存空間
- 規劃備份策略

---

### 幫助指令

#### !help

顯示指令幫助訊息。

**語法:**
```
!help [指令名稱]
```

**範例:**
```
!help
!help status
!help quota
```

**權限:** 所有人

**回應範例:**

**總覽 (!help)**
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
   !help [指令] - 顯示指令詳細說明

💡 提示:
- 私訊 Line Bot 即可開始 AI 對話
- 使用 !help <指令> 查看詳細說明
- 管理員指令需要特定權限

📚 完整文檔: https://github.com/kaiyasi/Converge
```

**詳細說明 (!help status)**
```
📖 指令詳細說明: !status

📝 描述:
   查看 Bot 的完整運行狀態，包括:
   - Discord Bot 狀態
   - AI 引擎狀態
   - 資料庫狀態
   - 系統資源使用
   - 運行時間

🔧 語法:
   !status

👥 權限: 所有人

💡 範例:
   !status

🔗 相關指令:
   !ping - 測試延遲
   !stats - 查看統計
```

---

## Line 指令

Line 群組指令使用 `#` 前綴。

### #status

查看系統狀態 (簡化版)。

**語法:**
```
#status
```

**權限:** 所有人

**回應範例:**
```
🤖 系統狀態

✅ Bot: 在線
⏰ 運行: 1天5小時

今日訊息: 89 則
使用者: 42 位

💡 私訊我開始 AI 對話
```

---

### #help

顯示 Line 群組可用指令。

**語法:**
```
#help
```

**權限:** 所有人

**回應範例:**
```
🤖 Line 群組指令

📊 資訊
   #status - 系統狀態
   #help - 顯示此訊息

💬 AI 對話
   私訊 Bot 即可開始對話

💡 更多功能請前往:
   http://localhost:8080/
```

---

### 私訊 AI 對話

直接私訊 Line Bot 任何文字即可開始 AI 對話。

**範例:**
```
你: 你好
Bot: 🤖 你好！有什麼我可以幫助你的嗎？

你: 請介紹一下自己
Bot: 🤖 我是 Converge，整合了 Google Gemini AI...
```

**限制:**
- 每日 20 次 (可調整)
- 最長 2000 字元
- 支援多輪對話 (記憶 10 輪)

---

## API 指令

通過 REST API 執行指令。

### 健康檢查

```http
GET /api/health
```

**回應:**
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "discord_bot": "ok",
    "ai_engine": "ok"
  }
}
```

---

### 獲取統計

```http
GET /api/stats
```

**回應:**
```json
{
  "database": {
    "total_users": 42,
    "total_messages": 1234
  },
  "platforms": {
    "line": {"users": 25, "messages": 800},
    "discord": {"users": 17, "messages": 434}
  }
}
```

---

### 查詢配額

```http
GET /api/users/<user_id>?platform=line
```

**回應:**
```json
{
  "user": {
    "user_id": "U123456",
    "platform": "line"
  },
  "quotas": [
    {
      "quota_type": "ai_daily",
      "usage_count": 5,
      "limit_count": 20,
      "remaining": 15
    }
  ]
}
```

完整 API 文檔: [API.md](./API.md)

---

## 指令權限

### 權限等級

| 等級 | 說明 | 可用指令 |
|------|------|----------|
| **所有人** | 任何使用者 | !status, !ping, !help, !quota (自己), !stats |
| **管理員** | Discord 管理員權限 | !users, !dbstats, !quota (全部) |
| **擁有者** | Bot 擁有者 | 所有指令 + 維護功能 |

### 檢查權限

```python
# 在 Discord 中
@bot.command()
@commands.has_permissions(administrator=True)
async def admin_command(ctx):
    # 僅管理員可用
    pass
```

---

## 自訂指令

### 新增 Discord 指令

編輯 `handlers/commands.py`:

```python
@self.discord_bot.bot.command(name='mycommand')
async def my_command(ctx, arg1: str = None):
    """
    自訂指令說明
    """
    await ctx.send(f"執行自訂指令: {arg1}")
```

### 新增 Line 群組指令

編輯訊息處理邏輯:

```python
if message_text.startswith('#mycommand'):
    response = "執行自訂 Line 指令"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )
```

### 最佳實踐

1. **指令命名**
   - 使用小寫
   - 簡短明瞭
   - 避免特殊字元

2. **參數設計**
   - 提供預設值
   - 驗證輸入
   - 清楚的錯誤訊息

3. **權限控制**
   - 敏感操作需要權限檢查
   - 記錄管理員操作
   - 防止濫用

4. **回應格式**
   - 使用 Emoji 提升可讀性
   - 結構化輸出
   - 適當的錯誤處理

---

## 指令別名

某些指令支援別名:

| 指令 | 別名 |
|------|------|
| !status | !st, !info |
| !quota | !q, !limit |
| !stats | !statistics |
| !users | !userlist, !ul |
| !help | !h, !? |

設定別名:

```python
@bot.command(name='status', aliases=['st', 'info'])
async def status(ctx):
    # 指令邏輯
    pass
```

---

## 指令使用提示

### 快速參考

```
# 查看狀態
!status

# 檢查配額
!quota

# 查看統計
!stats

# 測試延遲
!ping

# 查看幫助
!help
```

### 常見組合

```
# 完整系統檢查
!status
!quota
!stats
!dbstats

# 使用者管理
!users line 20
!quota U123456

# AI 對話 (Line 私訊)
你好
請介紹一下自己
```

---

## 故障排除

### 指令無回應

**可能原因:**
- Bot 未啟動
- 權限不足
- 指令拼寫錯誤

**解決方案:**
1. 確認 Bot 在線: !ping
2. 檢查權限
3. 使用 !help 查看正確語法

### 權限錯誤

```
❌ 權限不足
此指令需要管理員權限
```

**解決方案:**
- 確認您有 Discord 管理員權限
- 聯繫伺服器管理員

### 參數錯誤

```
❌ 參數錯誤
正確語法: !quota [使用者ID] [平台]
範例: !quota U123456 line
```

**解決方案:**
- 使用 !help <指令> 查看詳細說明
- 檢查參數格式

---

**[⬆ 回到文檔中心](./README.md)**
