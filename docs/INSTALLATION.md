# 安裝指南

本指南將協助您完成 Converge 的安裝和初始設置。

## 📋 系統需求

### 最低要求

- **作業系統**: Linux / macOS / Windows 10+
- **Python**: 3.8 或更高版本
- **記憶體**: 512 MB RAM
- **磁碟空間**: 200 MB

### 推薦配置

- **作業系統**: Ubuntu 20.04+ / macOS 12+ / Windows 11
- **Python**: 3.10+
- **記憶體**: 1 GB RAM
- **磁碟空間**: 1 GB

### 必要的服務

- **Discord Bot Token** ([取得方式](./setup/DISCORD.md))
- **Line Messaging API** ([取得方式](./setup/LINE.md))
- **Google Gemini API Key** ([取得方式](./setup/GEMINI.md))
- **HTTPS 服務器** (用於 Line Webhook，可使用 ngrok)

---

## 🚀 安裝步驟

### 1. 安裝 Python

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

#### macOS

```bash
# 使用 Homebrew
brew install python@3.10
```

#### Windows

從 [Python 官網](https://www.python.org/downloads/) 下載安裝程式。

**驗證安裝:**

```bash
python --version
# 應該顯示: Python 3.10.x 或更高
```

### 2. 克隆專案

```bash
git clone https://github.com/kaiyasi/Converge.git
cd Converge
```

### 3. 建立虛擬環境

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

**成功啟動後**，命令提示字元會顯示 `(venv)`。

### 4. 安裝依賴套件

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**等待安裝完成**，約需 1-2 分鐘。

### 5. 配置環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案
nano .env  # 或使用您喜歡的編輯器
```

**填入以下資訊:**

```env
# Discord 設定
DISCORD_TOKEN=你的_Discord_Bot_Token
DISCORD_CHANNEL_ID=你的_頻道_ID

# Line 設定
LINE_CHANNEL_SECRET=你的_Line_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的_Line_Access_Token
LINE_GROUP_ID=你的_Line_群組_ID

# Google Gemini AI
GOOGLE_API_KEY=你的_Gemini_API_Key

# 伺服器設定
HOST=0.0.0.0
PORT=8080
DEBUG=False
```

詳細設置請參考:
- [Discord 設置教學](./setup/DISCORD.md)
- [Line 設置教學](./setup/LINE.md)
- [Gemini 設置教學](./setup/GEMINI.md)

### 6. 初始化資料庫

```bash
python -c "from models.database import get_db; get_db()"
```

**成功後會顯示:**
```
✅ 資料庫已初始化
```

### 7. 啟動應用

```bash
python main_new.py
```

**成功啟動後會看到:**

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

---

## ✅ 驗證安裝

### 1. 檢查 Web Dashboard

在瀏覽器開啟: `http://localhost:8080/`

應該能看到儀表板介面。

### 2. 檢查 API

```bash
curl http://localhost:8080/api/health
```

應該返回:
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

### 3. 測試 Discord Bot

在 Discord 頻道輸入: `!ping`

Bot 應該回覆延遲資訊。

### 4. 測試 Line Bot

私訊 Line Bot: `你好`

Bot 應該用 AI 回覆。

---

## 🔧 進階安裝

### 使用 Docker

```bash
# 建立 Docker 映像
docker build -t converge .

# 執行容器
docker run -d \
  --name converge \
  --env-file .env \
  -p 8080:8080 \
  converge
```

### 使用 Docker Compose

```bash
docker-compose up -d
```

### 生產環境部署

使用 Gunicorn:

```bash
gunicorn main_new:app \
  -w 4 \
  -b 0.0.0.0:8080 \
  --worker-class gevent
```

詳細部署指南請參考 [部署文檔](./DEPLOYMENT.md)。

---

## 🐛 常見問題

### 問題: ModuleNotFoundError

**解決方案:**
```bash
# 確認虛擬環境已啟動
source venv/bin/activate  # Linux/macOS

# 重新安裝依賴
pip install -r requirements.txt
```

### 問題: Discord Bot 無法啟動

**檢查事項:**
1. Token 是否正確
2. 是否啟用了 Message Content Intent
3. Bot 是否已加入伺服器

詳細解決方案: [故障排除](./TROUBLESHOOTING.md)

### 問題: Line Webhook 驗證失敗

**解決方案:**
1. 確認使用 HTTPS
2. 檢查 Channel Secret 是否正確
3. 使用 ngrok 建立臨時 HTTPS

```bash
# 安裝 ngrok
brew install ngrok  # macOS
# 或從官網下載: https://ngrok.com/

# 啟動 ngrok
ngrok http 8080

# 將 ngrok 提供的 HTTPS URL 設置到 Line Webhook
```

---

## 📝 下一步

安裝完成後，您可以:

1. 📖 閱讀 [使用手冊](./USAGE.md)
2. 🎨 探索 [Web Dashboard](./DASHBOARD.md)
3. 🤖 了解 [指令系統](./COMMANDS.md)
4. 🔧 查看 [配置選項](./CONFIGURATION.md)

---

## 💡 提示

- 🔒 不要將 `.env` 檔案提交到 Git
- 📝 定期備份資料庫檔案
- 🔄 定期更新依賴套件
- 📊 監控系統資源使用

---

**需要幫助？** 查看 [FAQ](./FAQ.md) 或 [提出問題](https://github.com/kaiyasi/Converge/issues)

**[⬆ 回到文檔中心](./README.md)**
