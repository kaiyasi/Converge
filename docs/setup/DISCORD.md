# Discord Bot 設置教學

本教學將引導您完成 Discord Bot 的建立和設置流程。

## 📋 目錄

1. [建立 Discord 應用程式](#1-建立-discord-應用程式)
2. [建立 Bot](#2-建立-bot)
3. [設定權限與 Intents](#3-設定權限與-intents)
4. [邀請 Bot 到伺服器](#4-邀請-bot-到伺服器)
5. [取得頻道 ID](#5-取得頻道-id)
6. [測試 Bot](#6-測試-bot)

---

## 1. 建立 Discord 應用程式

### 步驟 1.1: 前往開發者入口

1. 開啟 [Discord Developer Portal](https://discord.com/developers/applications)
2. 使用您的 Discord 帳號登入

### 步驟 1.2: 建立新應用程式

1. 點擊右上角的 **「New Application」** 按鈕
2. 輸入應用程式名稱，例如: `Converge`
3. 閱讀並同意服務條款
4. 點擊 **「Create」**

![建立應用程式](../images/discord-create-app.png)

---

## 2. 建立 Bot

### 步驟 2.1: 進入 Bot 設定頁面

1. 在左側選單選擇 **「Bot」**
2. 點擊 **「Add Bot」** 按鈕
3. 確認建立

### 步驟 2.2: 取得 Bot Token

1. 在 Bot 頁面找到 **「TOKEN」** 區塊
2. 點擊 **「Reset Token」** (首次使用) 或 **「Copy」**
3. **重要**: 將 Token 複製並安全保存

```env
# 貼到 .env 檔案中
DISCORD_TOKEN=你複製的Token
```

⚠️ **安全提醒:**
- **絕對不要** 將 Token 分享給他人
- **絕對不要** 將 Token 提交到 Git
- **絕對不要** 在公開場合展示 Token
- 如果 Token 洩漏，立即重置

### 步驟 2.3: 設定 Bot 屬性

在 Bot 設定頁面:

1. **Public Bot**: 關閉 (除非您想讓他人邀請)
2. **Require OAuth2 Code Grant**: 關閉
3. **Bot Icon**: 上傳 Bot 頭像 (可選)

---

## 3. 設定權限與 Intents

### 步驟 3.1: 啟用 Privileged Gateway Intents

在 Bot 頁面向下滾動到 **「Privileged Gateway Intents」** 區塊:

啟用以下 Intents:

- ✅ **PRESENCE INTENT** (可選)
- ✅ **SERVER MEMBERS INTENT** (可選)
- ✅ **MESSAGE CONTENT INTENT** ⚠️ **必須啟用**

![Intents 設定](../images/discord-intents.png)

⚠️ **重要**: `MESSAGE CONTENT INTENT` 必須啟用，否則 Bot 無法讀取訊息內容。

### 步驟 3.2: 儲存變更

點擊頁面底部的 **「Save Changes」** 按鈕。

---

## 4. 邀請 Bot 到伺服器

### 步驟 4.1: 生成邀請連結

1. 在左側選單選擇 **「OAuth2」** → **「URL Generator」**
2. 在 **「SCOPES」** 區塊勾選:
   - ✅ `bot`
3. 在 **「BOT PERMISSIONS」** 區塊勾選:
   - ✅ `Read Messages/View Channels`
   - ✅ `Send Messages`
   - ✅ `Send Messages in Threads`
   - ✅ `Embed Links`
   - ✅ `Attach Files`
   - ✅ `Read Message History`
   - ✅ `Use External Emojis`
   - ✅ `Add Reactions`

![Bot 權限](../images/discord-permissions.png)

### 步驟 4.2: 使用邀請連結

1. 複製底部生成的 **「GENERATED URL」**
2. 在瀏覽器中開啟該 URL
3. 選擇要加入的伺服器
4. 點擊 **「授權」**
5. 完成人機驗證

---

## 5. 取得頻道 ID

### 步驟 5.1: 啟用開發者模式

1. 開啟 Discord 應用程式
2. 點擊左下角的 **設定** (齒輪圖示)
3. 選擇 **「進階」**
4. 啟用 **「開發者模式」**

![開發者模式](../images/discord-dev-mode.png)

### 步驟 5.2: 複製頻道 ID

1. 在伺服器中找到您要使用的文字頻道
2. 右鍵點擊該頻道
3. 選擇 **「複製 ID」**

```env
# 貼到 .env 檔案中
DISCORD_CHANNEL_ID=你複製的頻道ID
```

---

## 6. 測試 Bot

### 步驟 6.1: 確認環境變數

確保 `.env` 檔案包含:

```env
DISCORD_TOKEN=你的Discord機器人Token
DISCORD_CHANNEL_ID=你的Discord頻道ID
```

### 步驟 6.2: 啟動 Bot

```bash
python main_new.py
```

### 步驟 6.3: 驗證連線

成功啟動後，您應該會在終端機看到:

```
Discord 機器人已登入為 Converge#1234
✅ Discord Bot 已就緒
```

在 Discord 頻道中，Bot 應該會發送上線訊息:
```
🤖 機器人已上線！
```

### 步驟 6.4: 測試指令

在頻道中輸入:
```
!ping
```

Bot 應該回覆:
```
🏓 Pong! 延遲: 125.5 ms
```

---

## 🎯 完整設定檢查清單

- [ ] Discord 應用程式已建立
- [ ] Bot 已建立並取得 Token
- [ ] MESSAGE CONTENT INTENT 已啟用
- [ ] Bot 已邀請到伺服器
- [ ] 頻道 ID 已取得
- [ ] .env 檔案已正確設定
- [ ] Bot 成功上線
- [ ] 測試指令正常運作

---

## 🐛 故障排除

### Bot 無法上線

**可能原因:**
1. Token 錯誤或已過期
2. 網路連線問題
3. Discord API 故障

**解決方案:**
1. 重新生成 Token
2. 檢查網路連線
3. 查看 [Discord Status](https://discordstatus.com/)

### Bot 無法讀取訊息

**原因:** MESSAGE CONTENT INTENT 未啟用

**解決方案:**
1. 回到 Developer Portal
2. 進入 Bot 設定頁面
3. 啟用 MESSAGE CONTENT INTENT
4. 儲存變更
5. 重新啟動 Bot

### Bot 無法發送訊息

**可能原因:**
1. 權限不足
2. 頻道 ID 錯誤

**解決方案:**
1. 檢查 Bot 角色權限
2. 確認頻道 ID 正確
3. 確保 Bot 能看到該頻道

---

## 📚 延伸閱讀

- [Discord Developer Documentation](https://discord.com/developers/docs)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Converge 使用手冊](../USAGE.md)

---

## 💡 最佳實踐

1. **定期更新 Token**: 如有安全疑慮，立即重置
2. **最小權限原則**: 只授予必要的權限
3. **分離環境**: 開發和生產使用不同的 Bot
4. **監控日誌**: 定期檢查 Bot 運作狀態
5. **備份設定**: 記錄所有重要的 ID 和設定

---

**設定完成！** 🎉

下一步: [設置 Line Bot](./LINE.md)

**[⬆ 回到文檔中心](../README.md)**
