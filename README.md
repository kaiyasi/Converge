# 🔗 Converge

<div align="center">

**Line 與 Discord 跨平台訊息橋接機器人**

[![License: KYL Open](https://img.shields.io/badge/License-KYL%20Open-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-7289DA.svg)](https://discordpy.readthedocs.io/)
[![Line SDK](https://img.shields.io/badge/Line_SDK-3.0+-00C300.svg)](https://developers.line.biz/)
[![Flask](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[功能特色](#-功能特色) • [快速開始](#-快速開始) • [文檔](#-文檔) • [貢獻](#-貢獻)

</div>

---

## 📖 目錄

- [關於專案](#-關於專案)
- [功能特色](#-功能特色)
- [技術架構](#-技術架構)
- [快速開始](#-快速開始)
- [配置說明](#-配置說明)
- [使用方式](#-使用方式)
- [API 文檔](#-api-文檔)
- [Web Dashboard](#-web-dashboard)
- [開發指南](#-開發指南)
- [FAQ](#-faq)
- [貢獻](#-貢獻)
- [授權](#-授權)

---

## 🌟 關於專案

Converge 是一個功能完整的**跨平台訊息橋接系統**，無縫連接 **Line** 和 **Discord** 兩大通訊平台。除了基本的訊息同步功能，還整合了 **AI 對話**、**Web 管理介面**、**Webhook 系統**等進階功能，適合用於團隊協作、社群整合、自動化通知等多種場景。

### 🎯 使用場景

- 🏢 **團隊協作** - 整合 Line 與 Discord 的團隊溝通
- 🤖 **AI 助手** - 提供智能對話與自動回覆
- 🔔 **自動通知** - GitHub/GitLab 等第三方服務通知
- 📊 **數據監控** - 即時訊息統計與配額管理
- 🌐 **多平台整合** - 統一管理多個通訊平台

---

## ✨ 功能特色

### 核心功能

- 🔄 **雙向訊息同步** - Line ↔ Discord 即時訊息轉發
- 🖼️ **多媒體支援** - 圖片、影片、音訊、檔案自動轉發
- 🤖 **AI 智能對話** - 整合 Google Gemini Pro，支援上下文對話
- 👤 **使用者管理** - 完整的使用者資料與訊息記錄
- 📊 **配額管理** - 智能控制 API 使用量，避免超限

### Web 功能

- 🎨 **管理儀表板** - 視覺化的即時數據與圖表
- 📈 **統計分析** - 使用者活躍度、訊息量趨勢分析
- 🔍 **訊息搜尋** - 強大的關鍵字搜尋與篩選
- ⚙️ **系統監控** - CPU、記憶體、資料庫狀態監控

### 進階功能

- 🔔 **Webhook 系統** - 支援 GitHub、GitLab 等第三方整合
- 🏥 **健康檢查** - Kubernetes/Docker Ready/Liveness 支援
- 📡 **Prometheus 指標** - 標準格式的監控指標導出
- 🛡️ **安全機制** - Webhook 簽名驗證、請求限流
- 🔧 **Discord 指令** - `!status`、`!quota`、`!stats` 等豐富指令
- 📝 **Line 指令** - `#status`、`#help` 群組指令支援

---

## 🏗️ 技術架構

### 核心技術棧

| 類別 | 技術 | 版本 |
|------|------|------|
| 語言 | Python | 3.8+ |
| Bot Framework | Discord.py | 2.0+ |
| Messaging API | Line Bot SDK | 3.0+ |
| AI Engine | Google Gemini | Pro |
| Web Framework | Flask | 3.0 |
| Database | SQLite | 3 |
| Monitoring | Prometheus | - |

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         Converge System                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Discord Bot  │◄──────►│  Flask Web   │◄──────►│   Line Bot   │
│ (Discord.py) │        │  (Webhook)   │        │ (Messaging)  │
└──────────────┘        └──────────────┘        └──────────────┘
        │                        │                        │
        │                        ▼                        │
        │                ┌──────────────┐                │
        │                │  Gemini AI   │                │
        │                │  (対話引擎)   │                │
        │                └──────────────┘                │
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 ▼
                        ┌──────────────┐
                        │   SQLite DB  │
                        │  (數據存儲)   │
                        └──────────────┘
```

### 專案結構

```
Converge/
├── 📂 api/                     # Web API & Dashboard
│   ├── routes.py               # REST API 端點
│   ├── webhook.py              # Webhook 處理
│   └── dashboard.py            # 儀表板路由
├── 📂 core/                    # 核心模組
│   ├── discord_bot.py          # Discord 機器人管理
│   └── ai_engine.py            # AI 引擎
├── 📂 models/                  # 數據模型
│   ├── database.py             # 資料庫管理
│   ├── user.py                 # 使用者模型
│   ├── message.py              # 訊息模型
│   └── quota.py                # 配額模型
├── 📂 services/                # 業務邏輯
│   ├── media_handler.py        # 媒體處理
│   └── message_processor.py   # 訊息處理
├── 📂 handlers/                # 事件處理
│   └── commands.py             # 指令處理
├── 📂 utils/                   # 工具函數
│   ├── logger.py               # 日誌系統
│   └── retry.py                # 重試機制
├── 📂 templates/               # HTML 模板
│   ├── dashboard.html          # 儀表板
│   ├── users.html              # 使用者管理
│   ├── messages.html           # 訊息記錄
│   └── settings.html           # 系統設定
├── 📂 static/                  # 靜態資源
│   ├── css/                    # 樣式表
│   └── js/                     # JavaScript
├── 📂 docs/                    # 文檔
│   ├── API.md                  # API 文檔
│   ├── DEPLOYMENT.md           # 部署指南
│   ├── DEVELOPMENT.md          # 開發指南
│   ├── CONTRIBUTING.md         # 貢獻指南
│   └── SECURITY.md             # 安全政策
├── 📄 main_new.py              # 主程式 (新版)
├── 📄 config.py                # 配置管理
├── 📄 requirements.txt         # Python 依賴
├── 📄 .env.example             # 環境變數範本
└── 📄 README.md                # 本文件
```

---

## 🚀 快速開始

### 系統需求

- Python 3.8 或更高版本
- Discord Bot Token ([取得方式](./docs/SETUP_DISCORD.md))
- Line Messaging API ([取得方式](./docs/SETUP_LINE.md))
- Google Gemini API Key ([取得方式](./docs/SETUP_GEMINI.md))
- HTTPS 服務器 (用於 Line Webhook，可使用 ngrok)

### 安裝步驟

#### 1. 克隆專案

```bash
git clone https://github.com/kaiyasi/Converge.git
cd Converge
```

#### 2. 建立虛擬環境

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

#### 4. 配置環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入您的 API 金鑰
nano .env  # 或使用您喜歡的編輯器
```

#### 5. 啟動應用

```bash
python main_new.py
```

---

## ⚙️ 配置說明

### 環境變數

在 `.env` 檔案中配置以下參數：

```env
# Discord 設定
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_channel_id

# Line 設定
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token
LINE_GROUP_ID=your_line_group_id

# Google Gemini AI
GOOGLE_API_KEY=your_gemini_api_key

# 伺服器設定
HOST=0.0.0.0
PORT=8080
DEBUG=False

# 配額限制
AI_DAILY_LIMIT=20
LINE_MONTHLY_LIMIT=500
```

詳細配置說明請參閱 [配置文檔](./docs/CONFIGURATION.md)。

---

## 📚 使用方式

### Discord 指令

| 指令 | 說明 | 範例 |
|------|------|------|
| `!status` | 查看機器人狀態 | `!status` |
| `!quota` | 查看 API 配額 | `!quota` |
| `!stats` | 查看使用統計 | `!stats` |
| `!users` | 查看使用者列表 | `!users line` |
| `!dbstats` | 查看資料庫統計 | `!dbstats` |
| `!ping` | 測試延遲 | `!ping` |
| `!help` | 顯示幫助 | `!help` |

### Line 指令

| 指令 | 說明 |
|------|------|
| `#status` | 查看機器人狀態 |
| `#help` | 顯示幫助訊息 |

### AI 對話

直接私訊 Line Bot 即可開始 AI 對話：

```
你: 你好
Bot: 🤖 你好！有什麼我可以幫助你的嗎？
```

---

## 🌐 API 文檔

### REST API 端點

#### 健康檢查

```http
GET /api/health
```

**響應範例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T18:30:00",
  "checks": {
    "database": "ok",
    "discord_bot": "ok",
    "ai_engine": "ok"
  }
}
```

#### 統計資訊

```http
GET /api/stats
```

#### Prometheus 指標

```http
GET /api/metrics
```

完整 API 文檔請參閱 [API.md](./docs/API.md)。

---

## 🎨 Web Dashboard

訪問 `http://localhost:8080/` 即可打開 Web 管理介面。

### 功能頁面

| 頁面 | 路徑 | 說明 |
|------|------|------|
| 儀表板 | `/` | 即時統計、圖表、系統監控 |
| 使用者管理 | `/users` | 查看、搜尋、管理使用者 |
| 訊息記錄 | `/messages` | 訊息查詢、搜尋、匯出 |
| 系統設定 | `/settings` | 系統資訊、資料庫管理 |

### 截圖

<details>
<summary>📸 查看截圖</summary>

> 截圖功能開發中...

</details>

---

## 🛠️ 開發指南

### 本地開發

```bash
# 啟用除錯模式
export DEBUG=True
python main_new.py
```

### 執行測試

```bash
# 安裝測試依賴
pip install -r requirements-dev.txt

# 執行測試
pytest tests/

# 檢查程式碼品質
flake8 .
black --check .
```

### 提交代碼

請遵循我們的 [貢獻指南](./docs/CONTRIBUTING.md)。

---

## ❓ FAQ

<details>
<summary><b>Q: 如何獲取 Discord Bot Token？</b></summary>

請參閱 [Discord 設定指南](./docs/SETUP_DISCORD.md)。

</details>

<details>
<summary><b>Q: Line Webhook 驗證失敗怎麼辦？</b></summary>

1. 確認 `.env` 中的 `LINE_CHANNEL_SECRET` 正確
2. 確保使用 HTTPS (本地可用 ngrok)
3. 檢查 Webhook URL 格式: `https://your-domain.com/callback`

</details>

<details>
<summary><b>Q: AI 對話沒有回應？</b></summary>

1. 檢查 `GOOGLE_API_KEY` 是否正確
2. 確認是否超過每日配額 (預設 20 次)
3. 查看日誌檔案 `logs/bot.log` 中的錯誤訊息

</details>

更多問題請查看 [完整 FAQ](./docs/FAQ.md)。

---

## 🤝 貢獻

我們歡迎各種形式的貢獻！

-- 🐛 **回報 Bug**: [開啟 Issue](https://github.com/kaiyasi/Converge/issues)
-- 💡 **提出功能建議**: [開啟 Discussion](https://github.com/kaiyasi/Converge/discussions)
- 📝 **改善文檔**: 提交 Pull Request
- 🔧 **貢獻代碼**: 查看 [CONTRIBUTING.md](./docs/CONTRIBUTING.md)

### 貢獻者

感謝所有為此專案做出貢獻的開發者！

[![Contributors](https://contrib.rocks/image?repo=kaiyasi/Converge)](https://github.com/kaiyasi/Converge/graphs/contributors)

---

## 📄 授權

本專案採用 [KYL Open 授權條款](./LICENSE)。

---

## 🔐 安全性

如果您發現安全漏洞，請**不要公開發布**。請參閱我們的[安全政策](./docs/SECURITY.md)進行私下回報。

---

## :telephone_receiver: 支援與聯繫

### :bug: 問題回報與建議
* **:octocat: GitHub Issues**: [問題回報](https://github.com/kaiyasi/Converge/issues)
* **:speech_balloon: GitHub Discussions**: [功能討論](https://github.com/kaiyasi/Converge/discussions)
* **:shield: 安全問題**: 請參考 [安全政策](docs/SECURITY.md) 私下回報

### :busts_in_silhouette: 社群交流
* **:loudspeaker: 官方 Discord 群組**: [SerelixStudio_Discord](https://discord.gg/eRfGKepusP)
* **:camera_with_flash: 官方 IG**: [SerelixStudio_IG](https://www.instagram.com/serelix_studio?igsh=eGM1anl3em1xaHZ6&utm_source=qr)
* **:e_mail: 官方 Gmail**: [serelixstudio@gmail.com](mailto:serelixstudio@gmail.com)

---

## 🙏 致謝

### 使用的開源專案

- [Discord.py](https://github.com/Rapptz/discord.py) - Discord API 封裝
- [Line Bot SDK](https://github.com/line/line-bot-sdk-python) - Line Messaging API
- [Google Generative AI](https://ai.google.dev/) - Gemini AI
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Bootstrap](https://getbootstrap.com/) - UI 框架
- [Chart.js](https://www.chartjs.org/) - 圖表庫

---

<div align="center">

Converge by kaiyasi - 跨平台訊息橋接機器人 🔗 讓溝通更簡單
如果這個專案對你有幫助，請給我們一個 ⭐️

[⬆ 回到頂部](#-converge)

</div>


See [LICENSING.md](LICENSING.md) for license scope, third-party exceptions, and earlier-version notices.
