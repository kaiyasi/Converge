# API 文檔

本文檔詳細說明 Converge 提供的所有 REST API 端點。

## 📚 目錄

- [基礎資訊](#基礎資訊)
- [健康檢查 API](#健康檢查-api)
- [統計資訊 API](#統計資訊-api)
- [使用者管理 API](#使用者管理-api)
- [訊息管理 API](#訊息管理-api)
- [系統資訊 API](#系統資訊-api)
- [Webhook API](#webhook-api)

---

## 基礎資訊

### Base URL

```
http://localhost:8080/api
```

### 認證

目前版本不需要認證。未來版本將加入 API Token 認證機制。

### 響應格式

所有 API 均返回 JSON 格式數據。

---

## 健康檢查 API

### 健康狀態

檢查系統各組件的健康狀態。

**端點:** `GET /api/health`

**響應:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T18:30:00.123456",
  "checks": {
    "database": "ok",
    "discord_bot": "ok",
    "ai_engine": "ok"
  }
}
```

**狀態碼:**
- `200` - 系統健康
- `503` - 系統異常

### Prometheus 指標

導出 Prometheus 格式的監控指標。

**端點:** `GET /api/metrics`

**響應:** (text/plain)
```
# HELP system_cpu_percent CPU 使用率
# TYPE system_cpu_percent gauge
system_cpu_percent 15.2

# HELP total_users 總使用者數
# TYPE total_users gauge
total_users 42
...
```

---

## 統計資訊 API

### 獲取統計資訊

**端點:** `GET /api/stats`

**響應:**
```json
{
  "database": {
    "total_users": 42,
    "total_messages": 1234,
    "total_chat_history": 567,
    "active_group_mappings": 2,
    "db_size_bytes": 1048576,
    "db_size_mb": 1.0
  },
  "platforms": {
    "line": {
      "users": 25,
      "messages": 800
    },
    "discord": {
      "users": 17,
      "messages": 434
    }
  },
  "today": {
    "messages": 89
  },
  "quotas": [
    {
      "quota_type": "line_monthly",
      "usage_count": 350,
      "limit_count": 500,
      "reset_period": "monthly"
    }
  ],
  "timestamp": "2025-10-19T18:30:00"
}
```

### 獲取圖表數據

**端點:** `GET /api/stats/chart`

**參數:**
- `days` (int, 可選): 統計天數，預設 7

**範例:** `GET /api/stats/chart?days=7`

**響應:**
```json
{
  "daily_messages": [
    {"date": "2025-10-13", "count": 45},
    {"date": "2025-10-14", "count": 62},
    ...
  ],
  "platform_distribution": [
    {"platform": "line", "count": 800},
    {"platform": "discord", "count": 434}
  ],
  "hourly_messages": [
    {"hour": "08", "count": 12},
    {"hour": "09", "count": 25},
    ...
  ]
}
```

---

## 使用者管理 API

### 獲取使用者列表

**端點:** `GET /api/users`

**參數:**
- `platform` (str, 可選): 篩選平台 (line/discord)
- `limit` (int, 可選): 限制數量，預設 50
- `offset` (int, 可選): 偏移量，預設 0

**範例:** `GET /api/users?platform=line&limit=20&offset=0`

**響應:**
```json
{
  "users": [
    {
      "user_id": "U1234567890abcdef",
      "platform": "line",
      "display_name": "張三",
      "created_at": "2025-10-01T10:00:00",
      "updated_at": "2025-10-19T18:00:00",
      "is_active": true,
      "metadata": {}
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### 獲取使用者詳情

**端點:** `GET /api/users/<user_id>`

**參數:**
- `platform` (str, 可選): 平台名稱，預設 line

**範例:** `GET /api/users/U1234567890abcdef?platform=line`

**響應:**
```json
{
  "user": {
    "user_id": "U1234567890abcdef",
    "platform": "line",
    "display_name": "張三",
    "created_at": "2025-10-01T10:00:00",
    "is_active": true
  },
  "message_count": 125,
  "quotas": [
    {
      "quota_type": "ai_daily",
      "usage_count": 5,
      "limit_count": 20,
      "remaining": 15,
      "usage_percentage": 25.0
    }
  ]
}
```

---

## 訊息管理 API

### 獲取訊息列表

**端點:** `GET /api/messages`

**參數:**
- `limit` (int, 可選): 限制數量，預設 50
- `keyword` (str, 可選): 搜尋關鍵字
- `platform` (str, 可選): 篩選平台

**範例:**
- `GET /api/messages?limit=100`
- `GET /api/messages?keyword=測試&platform=line`

**響應:**
```json
{
  "messages": [
    {
      "id": 1,
      "message_id": "M123456",
      "user_id": "U1234567890abcdef",
      "platform": "line",
      "content": "測試訊息",
      "message_type": "text",
      "group_id": "C123abc",
      "created_at": "2025-10-19T18:30:00",
      "metadata": {}
    }
  ],
  "count": 1
}
```

---

## 系統資訊 API

### 獲取系統資訊

**端點:** `GET /api/system`

**響應:**
```json
{
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "memory_available_mb": 2048.5,
    "disk_percent": 60.2,
    "disk_free_gb": 25.3
  },
  "discord": {
    "ready": true,
    "latency": 125.5,
    "user": "Converge#1234"
  },
  "process": {
    "pid": 12345,
    "cpu_percent": 2.5,
    "memory_mb": 150.2,
    "threads": 8,
    "uptime_seconds": 86400
  },
  "timestamp": "2025-10-19T18:30:00"
}
```

---

## Webhook API

### Line Webhook

接收 Line 平台的事件通知。

**端點:** `POST /callback`

**Headers:**
- `X-Line-Signature`: Line Webhook 簽名

**請求 Body:** Line Webhook 事件 JSON

**響應:**
- `200 OK` - 處理成功
- `400 Bad Request` - 簽名驗證失敗
- `500 Internal Server Error` - 處理錯誤

### GitHub Webhook

接收 GitHub 事件並轉發到 Discord。

**端點:** `POST /github`

**Headers:**
- `X-GitHub-Event`: 事件類型 (push, pull_request, issues)

**請求 Body:** GitHub Webhook Payload JSON

**支援的事件:**
- `push` - 代碼推送
- `pull_request` - Pull Request
- `issues` - Issue 事件

**響應:**
```json
{
  "status": "success"
}
```

### 自訂 Webhook

通用的 Webhook 端點，可發送訊息到 Discord 或 Line。

**端點:** `POST /custom`

**Headers:**
- `Authorization`: Bearer Token (可選，未來實作)

**請求 Body:**
```json
{
  "platform": "discord",
  "target": "123456789",
  "message": "Hello from webhook!"
}
```

**參數說明:**
- `platform` (str, 必填): 目標平台 (discord/line)
- `target` (str, 可選): 目標 ID (channel_id 或 user_id)
- `message` (str, 必填): 訊息內容

**響應:**
```json
{
  "status": "success"
}
```

**狀態碼:**
- `200` - 發送成功
- `400` - 參數錯誤
- `503` - 服務不可用

---

## 錯誤處理

### 錯誤響應格式

```json
{
  "error": "錯誤訊息"
}
```

### 常見狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 成功 |
| 400 | 請求參數錯誤 |
| 404 | 資源不存在 |
| 500 | 伺服器內部錯誤 |
| 503 | 服務不可用 |

---

## 使用範例

### Python

```python
import requests

# 獲取統計資訊
response = requests.get('http://localhost:8080/api/stats')
data = response.json()
print(f"總使用者數: {data['database']['total_users']}")

# 搜尋訊息
response = requests.get(
    'http://localhost:8080/api/messages',
    params={'keyword': '測試', 'platform': 'line'}
)
messages = response.json()['messages']

# 自訂 Webhook
response = requests.post(
    'http://localhost:8080/custom',
    json={
        'platform': 'discord',
        'message': 'Hello from Python!'
    }
)
```

### cURL

```bash
# 健康檢查
curl http://localhost:8080/api/health

# 獲取統計
curl http://localhost:8080/api/stats

# 搜尋訊息
curl "http://localhost:8080/api/messages?keyword=測試"

# 發送 Webhook
curl -X POST http://localhost:8080/custom \
  -H "Content-Type: application/json" \
  -d '{"platform":"discord","message":"Hello!"}'
```

---

## 速率限制

目前版本沒有速率限制。未來版本將加入以下限制：

- API 請求: 100 次/分鐘
- Webhook: 30 次/分鐘

---

## 變更日誌

### v2.0.0 (2025-10-19)
- ✨ 新增完整的 REST API
- ✨ 新增 Prometheus 指標導出
- ✨ 新增 Webhook 系統
- 📝 完整的 API 文檔

---

**[⬆ 回到頂部](#api-文檔)**
