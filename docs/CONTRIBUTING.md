# 貢獻指南

感謝您對 Converge 專案的關注與支持!為確保所有貢獻能順利整合並維持高品質,我們制定以下貢獻流程與準則。

## 🤝 參與方式

您可以透過以下方式貢獻本專案:
- 🔧 提交程式碼改進(新增功能、修正錯誤、效能優化等)
- 📚 改善文件內容(README、教學文件、註解等)
- 🐛 回報問題與提出改進建議
- 🧪 協助測試、驗證或翻譯

在提交前,請先閱讀本文件與專案的 [行為準則](CODE_OF_CONDUCT.md)。

## 🐛 回報問題(Issues)

若發現錯誤、漏洞或使用疑慮,請先確認以下事項:

1. ✅ 已搜尋過現有討論,確定問題尚未被提出
2. 📝 提供明確的重現步驟、環境資訊與錯誤訊息
3. 🔒 若為安全性問題,**請勿公開發佈**,改以電子郵件方式通報

### 問題回報範本

```markdown
### 問題描述
(清楚描述遇到的問題)

### 重現步驟
1. …
2. …
3. …

### 預期結果
(說明您認為應該出現的正確行為)

### 實際結果
(附上錯誤訊息或截圖)

### 環境資訊
- 作業系統:
- Python 版本:
- Discord.py 版本:
- Line SDK 版本:
```

## 🔄 提交變更(Pull Requests)

### 1. Fork 與分支

- 請先 Fork 本專案至您的帳號
- 建立新分支進行開發:`feature/<描述>` 或 `fix/<描述>`
  - 例:`feature/image-support` 或 `fix/webhook-signature-bug`

### 2. Commit 規範

每次提交訊息應簡潔且具描述性,建議格式如下:

```bash
feat: 新增圖片轉發功能
fix: 修正 Webhook 簽名驗證錯誤
docs: 更新部署說明文件
refactor: 重構訊息處理模組
style: 調整程式碼格式
test: 新增單元測試
chore: 更新依賴套件
```

請避免使用「update」「change」等無意義訊息。

### 3. Pull Request 說明

開啟 PR 時,請於描述中包含:
- 🎯 變更目的與背景
- 📋 主要修改項目
- ✅ 驗證方式或測試結果
- 🔍 影響範圍(是否改動核心功能)
- 🔗 相關 Issue 編號(如適用)

## 📝 程式風格

為保持一致性,請遵循以下格式規範:

| 語言 | 標準 | 工具 |
|------|------|------|
| Python | PEP8 | Black, flake8, isort |
| Markdown / 文件 | UTF-8, 每行 ≤ 100 字元 | markdownlint |

### 程式碼品質檢查

```bash
# Python 格式化
black .

# Python 程式碼檢查
flake8 .

# Python import 排序
isort .
```

## 🧪 測試與驗證

- 若您的變更涉及邏輯或功能修改,請確保功能正常運作
- 測試 Discord 與 Line 之間的訊息轉發是否正常
- 測試 AI 回應功能是否運作正常
- 確認不會破壞現有功能

### 測試建議

```bash
# 1. 啟動機器人
python main.py

# 2. 測試以下功能:
# - Discord 發送訊息到 Line 群組
# - Line 群組訊息轉發到 Discord
# - Line 私訊 AI 對話功能
# - 圖片轉發功能(如適用)
```

## 🛠️ 開發環境設定

### 快速開始

```bash
# 1. Fork 並複製專案
git clone https://github.com/你的帳號/Converge.git
cd Converge

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env
# 編輯 .env 並填入必要的配置

# 5. 啟動機器人
python main.py
```

## 📖 文檔撰寫

### 文檔規範

- 使用繁體中文撰寫,專業術語可保留英文
- 提供程式碼範例和截圖
- 保持文檔與程式碼同步更新
- 使用 Markdown 格式,遵循 CommonMark 標準

## 📄 授權與貢獻歸屬

所有貢獻皆將遵循專案主要授權條款(見 [LICENSE](../LICENSE))。
提交 Pull Request 即代表您同意授予專案維護者使用與再發佈該內容的權利。
我們會在貢獻記錄與發布說明中感謝所有貢獻者。

### 貢獻者協議

- ✅ 您確認擁有所提交程式碼的著作權
- ✅ 您同意將貢獻內容以 MIT 授權釋出
- ✅ 您理解貢獻可能被修改或重新整合

## 📞 聯繫與支援

若您有任何疑問、建議或需要私下通報問題,請聯繫:

- 👨‍💻 **專案維護者**: [@kaiyasi](https://github.com/kaiyasi)
- 🐛 **問題回報**: [GitHub Issues](https://github.com/kaiyasi/Converge/issues)

### 回應時間

- **一般問題**: 48-72 小時內回覆
- **安全性問題**: 24 小時內回覆
- **Pull Request 審查**: 72 小時內初步回覆

## 🙏 感謝您的貢獻

每一位貢獻者都是專案成長的一部分。
感謝您願意投入時間與心力,讓這個專案更好。

### 貢獻者名單

我們會在以下地方感謝所有貢獻者:
- 專案 README.md
- GitHub Contributors 頁面
- 發布說明

---

**準備好開始貢獻了嗎?** 查看我們的 [開放 Issues](https://github.com/kaiyasi/Converge/issues) 找找有興趣的任務!
