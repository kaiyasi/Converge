# Google Gemini AI 設置教學

本教學將引導您完成 Google Gemini API 的設置和配置流程。

## 📋 目錄

1. [關於 Gemini AI](#1-關於-gemini-ai)
2. [建立 Google Cloud 專案](#2-建立-google-cloud-專案)
3. [取得 API Key](#3-取得-api-key)
4. [配置 API Key](#4-配置-api-key)
5. [測試 API](#5-測試-api)
6. [配額管理](#6-配額管理)
7. [進階設定](#7-進階設定)

---

## 1. 關於 Gemini AI

### 什麼是 Gemini？

Google Gemini 是 Google 最新的大型語言模型 (LLM)，提供強大的自然語言理解和生成能力。

### Gemini 版本對比

| 版本 | 特色 | 適用場景 |
|------|------|----------|
| **Gemini Pro** | 平衡性能與成本 | 一般對話、文字生成 |
| **Gemini Pro Vision** | 支援圖片理解 | 圖文混合對話 |
| **Gemini Ultra** | 最強性能 | 複雜推理任務 |

本專案使用 **Gemini Pro**。

### 費用說明

| 計費項目 | 免費額度 | 付費價格 |
|---------|---------|----------|
| 文字輸入 | 每分鐘 60 次請求 | $0.00025 / 1K 字元 |
| 文字輸出 | 每分鐘 60 次請求 | $0.0005 / 1K 字元 |

⚠️ **注意:** 免費額度通常足夠個人和小型專案使用。

---

## 2. 建立 Google Cloud 專案

### 步驟 2.1: 前往 Google AI Studio

1. 開啟 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用您的 Google 帳號登入

> **提示:** 建議使用 Google AI Studio，比 Google Cloud Console 更簡單快速。

### 步驟 2.2: 建立或選擇專案

1. 如果您沒有專案，系統會提示建立新專案
2. 輸入專案名稱，例如: `Converge`
3. 點擊 **「Create」**

---

## 3. 取得 API Key

### 步驟 3.1: 生成 API Key

**方法 1: 使用 Google AI Studio (推薦)**

1. 前往 [API Keys 頁面](https://makersuite.google.com/app/apikey)
2. 點擊 **「Get API key」**
3. 選擇:
   - **Create API key in new project** (建立新專案)
   - 或 **Create API key in existing project** (使用現有專案)
4. 點擊 **「Create API key」**
5. 複製生成的 API Key

![取得 API Key](../images/gemini-api-key.png)

**方法 2: 使用 Google Cloud Console**

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇或建立專案
3. 前往 **「APIs & Services」** > **「Credentials」**
4. 點擊 **「+ CREATE CREDENTIALS」** > **「API key」**
5. 複製生成的 API Key

### 步驟 3.2: 儲存 API Key

```env
# 貼到 .env 檔案中
GOOGLE_API_KEY=你複製的API_Key
```

⚠️ **安全提醒:**
- **絕對不要** 將 API Key 分享給他人
- **絕對不要** 將 API Key 提交到 Git 或公開倉庫
- **絕對不要** 在網頁前端直接使用 API Key
- 如果 Key 洩漏，立即刪除並重新建立

### 步驟 3.3: 限制 API Key (建議)

為了安全，建議限制 API Key 的使用範圍:

1. 在 API Key 頁面點擊您的 Key
2. 點擊 **「Edit API key」**
3. 設定限制:
   - **API restrictions**: 選擇 **「Restrict key」**
     - 勾選 **「Generative Language API」**
   - **Application restrictions**: (可選)
     - **IP addresses**: 限制特定 IP
     - **HTTP referrers**: 限制特定網域

4. 點擊 **「Save」**

---

## 4. 配置 API Key

### 步驟 4.1: 設定環境變數

編輯 `.env` 檔案:

```env
# Google Gemini AI 設定
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# AI 配額限制 (可選)
AI_DAILY_LIMIT_PER_USER=20        # 每位使用者每日 AI 請求限制
AI_MODEL_NAME=gemini-pro          # 使用的模型名稱
AI_TEMPERATURE=0.7                # 創造性參數 (0.0-1.0)
AI_MAX_TOKENS=1000                # 最大輸出長度
```

### 步驟 4.2: 參數說明

| 參數 | 說明 | 建議值 |
|------|------|--------|
| `GOOGLE_API_KEY` | API 金鑰 | (必填) |
| `AI_DAILY_LIMIT_PER_USER` | 每日請求限制 | 20-50 |
| `AI_MODEL_NAME` | 模型名稱 | `gemini-pro` |
| `AI_TEMPERATURE` | 創造性 (0.0-1.0) | 0.7 |
| `AI_MAX_TOKENS` | 最大輸出長度 | 1000-2000 |

**Temperature 參數說明:**
- `0.0` - 更確定、保守的回應
- `0.5` - 平衡創造性與一致性
- `1.0` - 最大創造性，較隨機

---

## 5. 測試 API

### 步驟 5.1: 啟動 Bot

```bash
python main_new.py
```

### 步驟 5.2: 測試 AI 對話

**在 Line 私訊中測試:**

```
你: 你好
Bot: 🤖 你好！有什麼我可以幫助你的嗎？

你: 請問你是誰？
Bot: 🤖 我是 Converge，一個整合了 Google Gemini AI 的智能助手...
```

**在 Discord 中測試:**

```
你: @Converge 你好
Bot: 🤖 你好！我是由 Gemini AI 驅動的機器人。
```

### 步驟 5.3: 檢查日誌

查看 `logs/bot.log` 確認 API 呼叫成功:

```
2025-10-19 18:30:00 [INFO] AI 請求成功 | user_id=U123456 | tokens=150
```

### 步驟 5.4: 使用測試腳本

```python
# test_gemini.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# 配置 API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# 建立模型
model = genai.GenerativeModel('gemini-pro')

# 生成回應
response = model.generate_content('你好，請簡單介紹自己')
print(response.text)
```

執行測試:

```bash
python test_gemini.py
```

---

## 6. 配額管理

### 內建配額系統

Converge 已內建配額管理系統，自動追蹤和限制 API 使用量。

### 查看配額使用狀況

**Discord 指令:**

```
!quota
```

**回應範例:**

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

### Web Dashboard 監控

訪問 `http://localhost:8080/` 查看:

- 即時配額使用圖表
- 每日 AI 請求趨勢
- 配額預警通知

### 配額警告

當配額使用達到 80% 時，系統會自動發出警告:

```
⚠️ 配額警告
AI 對話配額已使用 80% (16/20)
請注意使用量，避免超限。
```

### 修改配額限制

編輯 `.env` 檔案:

```env
# 增加每日限制
AI_DAILY_LIMIT_PER_USER=50

# 增加 Line 每月限制
LINE_MONTHLY_LIMIT=1000
```

重新啟動 Bot 以套用變更。

---

## 7. 進階設定

### 7.1 自訂提示詞 (System Prompt)

編輯 `core/ai_engine.py`:

```python
class AIEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

        # 自訂系統提示詞
        self.system_prompt = """
        你是 Converge，一個友善的 AI 助手。

        特色:
        - 使用繁體中文回應
        - 保持專業但友善的語氣
        - 回應簡潔明瞭
        - 適時使用 emoji

        限制:
        - 不提供醫療建議
        - 不提供法律建議
        - 拒絕不當請求
        """
```

### 7.2 多模型切換

支援根據不同場景使用不同模型:

```python
# config.py
class BotConfig:
    # 一般對話使用 Pro
    AI_MODEL_CHAT = "gemini-pro"

    # 圖片理解使用 Vision
    AI_MODEL_VISION = "gemini-pro-vision"

    # 複雜任務使用 Ultra (需申請)
    AI_MODEL_ULTRA = "gemini-ultra"
```

### 7.3 內容安全設定

調整內容過濾級別:

```python
import google.generativeai as genai

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

model = genai.GenerativeModel(
    'gemini-pro',
    safety_settings=safety_settings
)
```

**閾值選項:**
- `BLOCK_NONE` - 不過濾
- `BLOCK_LOW_AND_ABOVE` - 過濾低風險以上
- `BLOCK_MEDIUM_AND_ABOVE` - 過濾中等風險以上 (推薦)
- `BLOCK_ONLY_HIGH` - 僅過濾高風險

### 7.4 對話歷史管理

啟用多輪對話:

```python
class AIEngine:
    async def generate_response_with_history(
        self,
        user_id: str,
        message: str,
        platform: str = 'line'
    ) -> str:
        # 取得使用者對話歷史
        history = ChatHistory.get_recent(user_id, platform, limit=10)

        # 建立對話
        chat = self.model.start_chat(history=[
            {"role": h.role, "parts": [h.content]}
            for h in history
        ])

        # 生成回應
        response = chat.send_message(message)

        # 儲存歷史
        ChatHistory.add(user_id, platform, "user", message)
        ChatHistory.add(user_id, platform, "model", response.text)

        return response.text
```

### 7.5 錯誤處理

```python
import google.generativeai as genai
from google.api_core import exceptions

try:
    response = model.generate_content(prompt)
except exceptions.ResourceExhausted:
    # 配額耗盡
    return "⚠️ API 配額已用完，請稍後再試。"
except exceptions.InvalidArgument:
    # 參數錯誤
    return "❌ 請求格式錯誤。"
except exceptions.PermissionDenied:
    # 權限不足
    return "❌ API Key 無效或權限不足。"
except Exception as e:
    # 其他錯誤
    logger.error(f"Gemini API 錯誤: {e}")
    return "❌ AI 服務暫時不可用。"
```

---

## 🐛 故障排除

### API Key 無效

**錯誤訊息:**
```
google.api_core.exceptions.PermissionDenied: 403 API key not valid.
```

**解決方案:**
1. 確認 `.env` 中的 API Key 正確
2. 檢查 API Key 是否啟用 Generative Language API
3. 確認沒有多餘空格或換行
4. 嘗試重新生成 API Key

### 配額超限

**錯誤訊息:**
```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded.
```

**解決方案:**
1. 等待配額重置 (每分鐘 60 次請求)
2. 升級到付費方案
3. 優化請求頻率
4. 使用本地配額管理系統

### 回應被過濾

**錯誤訊息:**
```
Response was blocked due to safety filters.
```

**解決方案:**
1. 修改提示詞，避免敏感內容
2. 調整 safety_settings 閾值
3. 檢查使用者輸入內容

### API 回應緩慢

**可能原因:**
- 網路延遲
- 請求內容過長
- API 伺服器負載高

**解決方案:**
1. 設定合理的 timeout
2. 限制輸入長度
3. 使用非同步處理
4. 加入重試機制

---

## 📊 效能優化

### 1. 快取回應

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
```

### 2. 批次處理

```python
# 批次處理多個請求
prompts = ["問題1", "問題2", "問題3"]
responses = model.generate_content(prompts)
```

### 3. 串流回應

```python
# 使用串流接收回應
response = model.generate_content(prompt, stream=True)

for chunk in response:
    print(chunk.text, end='')
```

---

## 📚 延伸閱讀

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Best Practices](https://ai.google.dev/docs/best_practices)

---

## 💡 最佳實踐

1. **API Key 安全**:
   - 使用環境變數
   - 限制 API Key 權限
   - 定期輪換 Key

2. **配額管理**:
   - 實作本地配額限制
   - 監控使用量
   - 設定警告閾值

3. **錯誤處理**:
   - 完整的異常捕獲
   - 友善的錯誤訊息
   - 自動重試機制

4. **效能優化**:
   - 快取常見問題
   - 非同步處理
   - 限制請求頻率

5. **使用者體驗**:
   - 提供載入提示
   - 合理的 timeout
   - 降級方案

---

## ⚠️ 注意事項

1. **隱私保護**:
   - 不要發送敏感個人資料到 API
   - 遵守 GDPR 和隱私法規
   - 告知使用者 AI 使用情況

2. **內容審核**:
   - 過濾不當輸入
   - 審核 AI 輸出
   - 記錄異常對話

3. **成本控制**:
   - 監控 API 費用
   - 設定預算警告
   - 優化請求效率

---

**設定完成！** 🎉

現在您可以開始使用 AI 功能了！

**[⬆ 回到文檔中心](../README.md)**
