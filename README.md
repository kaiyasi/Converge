# Line-Discord 訊息橋接機器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-blue.svg?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Line SDK](https://img.shields.io/badge/Line_SDK-2.0+-green.svg?logo=line&logoColor=white)](https://developers.line.biz/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<div align="center">
  <img src="https://i.imgur.com/YourImage.png" alt="Bot Logo" width="200">
  
  🤖 一個連接 Line 和 Discord 群組的橋接機器人，實現跨平台即時通訊功能。
</div>

## 📚 簡介
這個機器人能夠：
- 🔄 自動同步 Line 和 Discord 的訊息
- 🛡️ 安全地處理跨平台通訊
- ⚡ 即時轉發所有對話內容

## ✨ 功能特色
| 功能 | 說明 |
|------|------|
| 🔄 即時同步 | Line 和 Discord 群組之間的即時訊息同步 |
| 🧩 模組化設計 | 使用 Discord.py Cog 系統的模組化設計 |
| 🔒 安全驗證 | 支援 Line Webhook 的安全驗證機制 |
| 🚀 簡易部署 | 支援 Render 雲端平台的快速部署流程 |

## 🔧 系統需求
| 需求 | 版本/說明 |
|------|-----------|
| Python | 3.8 或更新版本 |
| Discord Bot | 需要 Bot Token |
| Line Bot | 需要 Messaging API 帳號 |
| 伺服器 | 支援 HTTPS |

## 🚀 開始使用

<details>
<summary>📥 安裝步驟</summary>

```bash
git clone https://github.com/yourusername/line-discord-bridge.git
cd line-discord-bridge
```
2. 安裝相依套件
```bash
pip install -r requirements.txt
```
3. 設定環境變數

```bash
DISCORD_TOKEN=你的Discord機器人Token
DISCORD_CHANNEL_ID=你的Discord頻道ID
LINE_CHANNEL_SECRET=你的Line頻道密鑰
LINE_CHANNEL_ACCESS_TOKEN=你的Line存取權杖
```

### 啟動機器人

```bash
python main.py
```

## ⚙️ 詳細設定指南

### 🤖 Discord 機器人設定
<details>
<summary>點擊展開 Discord 設定步驟</summary>

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 點擊「New Application」建立新應用程式
3. 進入「Bot」分頁建立機器人
4. 複製機器人的 Token
5. 在「Bot」分頁中開啟必要的 Intents 權限：
   - ✅ MESSAGE CONTENT INTENT
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
</details>

### 📱 Line 機器人設定
<details>
<summary>點擊展開 Line 設定步驟</summary>

1. 前往 [Line Developers Console](https://developers.line.biz/console/)
2. 建立新的 Provider（若尚未建立）
3. 建立新的 Channel（Messaging API）
4. 在 Basic Settings 中取得 Channel Secret
5. 在 Messaging API 分頁中：
   - ✅ 生成 Channel Access Token
   - ✅ 開啟 Use webhook
   - ✅ 設定 Webhook URL
   - ✅ 關閉自動回覆訊息功能
</details>

## 🔧 故障排除

<details>
<summary>常見問題解答</summary>

### 連線問題
- ✅ 檢查網路連線
- ✅ 確認 Token 正確性
- ✅ 驗證權限設定

### 訊息同步問題
- ✅ 確認頻道 ID
- ✅ 檢查 Webhook 設定
- ✅ 查看錯誤日誌
</details>

## 🤝 參與貢獻

我們歡迎所有形式的貢獻：
- 🐛 回報 Bug
- 💡 提供新想法
- 📝 改善文檔
- 🔧 提交程式碼

## 📜 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

---

<div align="center">

### 🌟 支持本專案

如果這個專案對你有幫助，請給我們一個 Star ⭐️

**Made with ❤️ by [Zeng_Eric]**  
**Co-created with 🤖 [Claude](https://claude.ai) - Anthropic's AI Assistant**

[![Anthropic](https://img.shields.io/badge/Powered_by-Claude_AI-7C4DFF?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai)

</div>

