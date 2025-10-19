# Line Bot 設置教學

本教學將引導您完成 Line Messaging API 的設置流程。

## 📋 目錄

1. [建立 Line 開發者帳號](#1-建立-line-開發者帳號)
2. [建立 Provider](#2-建立-provider)
3. [建立 Messaging API Channel](#3-建立-messaging-api-channel)
4. [取得 Channel Secret 和 Access Token](#4-取得-channel-secret-和-access-token)
5. [設定 Webhook URL](#5-設定-webhook-url)
6. [取得群組 ID](#6-取得群組-id)
7. [測試 Bot](#7-測試-bot)

---

## 1. 建立 Line 開發者帳號

### 步驟 1.1: 註冊開發者帳號

1. 前往 [Line Developers Console](https://developers.line.biz/console/)
2. 使用您的 Line 帳號登入
3. 如果是首次使用，請填寫開發者資訊:
   - 姓名
   - Email
   - 同意服務條款

### 步驟 1.2: 驗證 Email

1. 檢查您的信箱
2. 點擊驗證連結
3. 完成驗證

---

## 2. 建立 Provider

### 步驟 2.1: 建立新 Provider

1. 登入 [Line Developers Console](https://developers.line.biz/console/)
2. 點擊 **「Create a new provider」**
3. 輸入 Provider 名稱，例如: `Converge Provider`
4. 點擊 **「Create」**

![建立 Provider](../images/line-create-provider.png)

⚠️ **注意:** Provider 是管理多個 Channel 的容器，建議使用有意義的名稱。

---

## 3. 建立 Messaging API Channel

### 步驟 3.1: 建立 Channel

1. 在 Provider 頁面，點擊 **「Create a Messaging API channel」**
2. 填寫 Channel 資訊:
   - **Channel type**: Messaging API
   - **Provider**: (自動選擇)
   - **Company or owner's name**: 您的名稱或公司名稱
   - **Channel name**: `Converge`
   - **Channel description**: 機器人功能描述
   - **Category**: 選擇適合的類別
   - **Subcategory**: 選擇子類別

### 步驟 3.2: 填寫詳細資訊

3. 繼續填寫:
   - **Email address**: 您的 Email
   - **Privacy policy URL**: (可選)
   - **Terms of use URL**: (可選)

4. 上傳 Channel Icon (可選)

5. 閱讀並同意:
   - ✅ Line Official Account Terms of Use
   - ✅ Line Official Account API Terms of Use

6. 點擊 **「Create」**

---

## 4. 取得 Channel Secret 和 Access Token

### 步驟 4.1: 取得 Channel Secret

1. 進入您剛建立的 Channel
2. 選擇 **「Basic settings」** 標籤
3. 向下滾動到 **「Channel secret」** 區塊
4. 點擊 **「Show」** 查看，然後複製

```env
# 貼到 .env 檔案中
LINE_CHANNEL_SECRET=你複製的Channel_Secret
```

### 步驟 4.2: 發行 Channel Access Token

1. 選擇 **「Messaging API」** 標籤
2. 向下滾動到 **「Channel access token」** 區塊
3. 點擊 **「Issue」** 按鈕
4. 複製生成的 Token

```env
# 貼到 .env 檔案中
LINE_CHANNEL_ACCESS_TOKEN=你複製的Access_Token
```

⚠️ **安全提醒:**
- **絕對不要** 將 Token 分享給他人
- **絕對不要** 將 Token 提交到 Git
- **絕對不要** 在公開場合展示 Token
- Token 一旦洩漏，立即重新發行

### 步驟 4.3: 啟用必要設定

在 **「Messaging API」** 標籤中:

1. **Use webhooks**: 開啟 ✅
2. **Auto-reply messages**: 關閉 ❌ (避免與 Bot 衝突)
3. **Greeting messages**: 關閉 ❌ (可選)

---

## 5. 設定 Webhook URL

### 步驟 5.1: 準備 HTTPS URL

Line Webhook **必須使用 HTTPS**。本地開發可使用 ngrok:

```bash
# 安裝 ngrok
# macOS
brew install ngrok

# 或從官網下載: https://ngrok.com/

# 啟動 ngrok
ngrok http 8080
```

ngrok 會提供一個 HTTPS URL，例如: `https://abc123.ngrok.io`

### 步驟 5.2: 設定 Webhook URL

1. 在 **「Messaging API」** 標籤
2. 找到 **「Webhook URL」** 區塊
3. 點擊 **「Edit」**
4. 輸入您的 Webhook URL:
   ```
   https://your-domain.com/callback
   ```
   或使用 ngrok:
   ```
   https://abc123.ngrok.io/callback
   ```
5. 點擊 **「Update」**

### 步驟 5.3: 驗證 Webhook

1. 確保您的 Bot 已啟動
2. 點擊 **「Verify」** 按鈕
3. 如果設定正確，會顯示 **「Success」**

**常見錯誤:**
- ❌ `Connection failed` - 檢查 URL 是否正確，Bot 是否運行
- ❌ `Invalid signature` - 檢查 Channel Secret 是否正確
- ❌ `404 Not Found` - 檢查路由是否正確設定

---

## 6. 取得群組 ID

如果您想將 Bot 加入群組並取得群組 ID:

### 步驟 6.1: 加入 Bot 為好友

1. 在 **「Messaging API」** 標籤
2. 找到 **「Bot basic ID」** 或掃描 QR Code
3. 在 Line 中加入 Bot 為好友

### 步驟 6.2: 建立群組

1. 在 Line 中建立新群組
2. 將 Bot 邀請到群組中

### 步驟 6.3: 取得群組 ID

有兩種方式取得群組 ID:

**方式 1: 透過 Bot 日誌**

1. 在群組中發送任意訊息
2. 查看 Bot 的日誌檔案 `logs/bot.log`
3. 找到類似 `group_id: C1234567890abcdef` 的記錄

**方式 2: 透過 Line API**

使用 Line API 查詢:

```python
from linebot import LineBotApi

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')

# 發送測試訊息到群組
# Bot 會在日誌中記錄 group_id
```

```env
# 貼到 .env 檔案中
LINE_GROUP_ID=你的群組ID
```

---

## 7. 測試 Bot

### 步驟 7.1: 確認環境變數

確保 `.env` 檔案包含:

```env
LINE_CHANNEL_SECRET=你的Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的Access_Token
LINE_GROUP_ID=你的群組ID
```

### 步驟 7.2: 啟動 Bot

```bash
python main_new.py
```

### 步驟 7.3: 驗證連線

成功啟動後，您應該會在終端機看到:

```
✅ Line Bot 已初始化
✅ Webhook URL: https://your-domain.com/callback
🌐 啟動 Flask 伺服器 (Host: 0.0.0.0, Port: 8080)
```

### 步驟 7.4: 測試私訊

私訊 Line Bot:

```
你: 你好
Bot: 🤖 你好！有什麼我可以幫助你的嗎？
```

### 步驟 7.5: 測試群組訊息

在群組中輸入:

```
#status
```

Bot 應該回覆系統狀態。

---

## 🎯 完整設定檢查清單

- [ ] Line 開發者帳號已建立
- [ ] Provider 已建立
- [ ] Messaging API Channel 已建立
- [ ] Channel Secret 已取得
- [ ] Channel Access Token 已發行
- [ ] Webhook URL 已設定並驗證成功
- [ ] 自動回覆已關閉
- [ ] Bot 已加為好友
- [ ] 群組 ID 已取得 (如需群組功能)
- [ ] .env 檔案已正確設定
- [ ] Bot 成功收發訊息

---

## 🐛 故障排除

### Webhook 驗證失敗

**可能原因:**
1. URL 不是 HTTPS
2. Bot 未啟動
3. Channel Secret 錯誤
4. 防火牆阻擋

**解決方案:**
1. 確保使用 HTTPS (ngrok 或正式域名)
2. 確認 Bot 正在運行
3. 重新檢查 .env 中的 Channel Secret
4. 檢查伺服器防火牆設定

### Bot 收不到訊息

**可能原因:**
1. Webhook URL 未設定
2. 自動回覆未關閉
3. Bot 被封鎖

**解決方案:**
1. 確認 Webhook URL 已設定且驗證成功
2. 關閉自動回覆和歡迎訊息
3. 檢查 Bot 是否被封鎖，重新加為好友

### Bot 無法發送訊息

**可能原因:**
1. Access Token 錯誤或過期
2. 使用者 ID 或群組 ID 錯誤
3. API 配額超限

**解決方案:**
1. 重新發行 Access Token
2. 確認 ID 正確
3. 檢查配額使用狀況

### Error: Invalid signature

**原因:** Channel Secret 不正確

**解決方案:**
1. 重新複製 Channel Secret
2. 確認 .env 檔案中沒有多餘空格
3. 重新啟動 Bot

---

## 📊 配額限制

Line Messaging API 有以下限制:

| 方案 | 每月免費訊息數 | 超額費用 |
|------|---------------|----------|
| Free | 500 則 | 無法發送 |
| Basic | 1,000 則 | 超額後付費 |
| Pro | 依方案 | 依方案計費 |

⚠️ **重要:**
- 系統已內建配額管理，會在接近限制時發出警告
- 可使用 `!quota` 指令查看當前配額使用狀況
- 建議監控 Dashboard 的配額統計圖表

---

## 📚 延伸閱讀

- [Line Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [Line Bot SDK for Python](https://github.com/line/line-bot-sdk-python)
- [Converge 使用手冊](../USAGE.md)

---

## 💡 最佳實踐

1. **定期檢查配額**: 避免超限無法發送訊息
2. **使用群組 ID**: 集中管理群組訊息
3. **關閉自動回覆**: 避免與 Bot 邏輯衝突
4. **備份 Token**: 記錄所有 Token 和 ID (加密保存)
5. **監控 Webhook**: 定期檢查 Webhook 狀態
6. **測試環境分離**: 開發和生產使用不同的 Channel

---

## 🔐 安全建議

1. **Token 管理**:
   - 使用環境變數，不要硬編碼
   - 定期輪換 Access Token
   - 洩漏時立即重新發行

2. **Webhook 安全**:
   - 始終驗證 X-Line-Signature
   - 使用 HTTPS
   - 實作請求限流

3. **權限控制**:
   - 限制 Bot 權限為必要範圍
   - 記錄所有 API 呼叫
   - 監控異常活動

---

**設定完成！** 🎉

下一步: [設置 Gemini AI](./GEMINI.md)

**[⬆ 回到文檔中心](../README.md)**
