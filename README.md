# BOS-ETMALL 後端系統

POS 訂單接收 → PostgreSQL + Google Sheets 同步 → 每日 Email 報表

**Live URL：** https://bos-etmall.zeabur.app  
**部署平台：** Zeabur  
**GitHub：** https://github.com/jason121380/bos-etmall

---

## 系統架構

```
POS 系統
  │
  │ POST /webhook/order
  ▼
FastAPI 後端 (Zeabur)
  │
  ├── PostgreSQL 資料庫（寫入訂單）
  ├── Google Sheets（即時同步）
  └── Zeabur Email（每天 09:00 寄報表）
```

---

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/webhook/order` | 接收 POS 訂單（主要接口） |
| `GET` | `/orders` | 查詢所有訂單 |
| `GET` | `/health` | 健康檢查 |
| `GET` | `/dashboard` | 監控儀表板（含設定頁） |
| `GET` | `/admin/settings` | 取得後台設定 |
| `POST` | `/admin/settings` | 更新後台設定 |
| `GET` | `/admin/email-logs` | 查詢 Email 發送紀錄 |
| `POST` | `/admin/send-report-now` | 手動觸發昨日 Email 報表 |
| `POST` | `/admin/send-today-report` | 立即發送今日報表 |
| `POST` | `/admin/send-date-report` | 發送指定日期區間報表 |
| `POST` | `/admin/test-email` | 發送測試信 |
| `GET` | `/docs` | API 互動文件（Notion 風格） |

---

## 監控儀表板

https://bos-etmall.zeabur.app/dashboard

左側選單功能：
- **監控儀表板**：今日/本月/累計訂單統計、最新訂單表格、店家分布
- **健康檢查**：API 連線狀態
- **設定**：
  - Email 欄位多選（9 個欄位可自由勾選）
  - 收件人管理（UI 直接設定，不需改環境變數）
  - 手動發送報表（今日、指定日期/區間）
  - **Email 發送紀錄**（顯示最近 20 筆，含時間/類型/筆數/狀態）
- **API 文件**：Swagger UI（Notion 風格 + 繁中說明）

---

## Webhook Payload 格式

```json
POST https://bos-etmall.zeabur.app/webhook/order
Content-Type: application/json

{
  "order_id": "POS-20260411-00123",
  "store_id": "STORE-001",
  "store_name": "信義旗艦店",
  "consumer_phone": "0912345678",
  "consumer_name": "王小明",
  "amount": 1500,
  "order_status": "completed",
  "order_time": "2026-04-11T10:30:00+08:00"
}
```

**order_status 可接受值：** `completed` / `paid` / `confirmed` / `success` / `done`

**自動篩選條件：**
- 訂單狀態需在白名單內
- 消費金額 ≥ NT$1,000（`MIN_ORDER_AMOUNT`）

---

## 資料庫欄位

### orders 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | int | 自動遞增 |
| order_id | string | POS 訂單編號（唯一） |
| store_id | string | 店家編號 |
| store_name | string | 店家名稱 |
| consumer_phone | string | 消費者手機 |
| consumer_name | string | 消費者姓名 |
| amount | float | 消費金額 |
| order_status | string | 訂單狀態 |
| order_time | datetime | POS 訂單時間 |
| received_at | datetime | 系統接收時間 |
| emailed | bool | 是否已寄入 Email 報表 |
| synced_to_sheet | bool | 是否已同步 Google Sheet |

### email_logs 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | int | 自動遞增 |
| sent_at | datetime | 發送時間 |
| trigger | string | `schedule` / `manual_today` / `manual_date` / `test` |
| date_range | string | 報表涵蓋日期區間 |
| order_count | int | 發送筆數 |
| recipients | string | 收件人（逗號分隔） |
| status | string | `ok` / `error` |
| error | string | 錯誤訊息（失敗時） |

### settings 表

| key | 說明 |
|-----|------|
| `email_recipients` | 收件人清單（逗號分隔） |
| `email_fields` | 報表欄位（逗號分隔） |

---

## 每日 Email 報表

- **時間：** 每天早上 09:00（台北時間）
- **寄件人：** 名留集團 ML Group `<report@mlgroup.vip>`
- **內容：** 前一天新收到的訂單名單（HTML 表格 + CSV 附件）
- **收件人：** 從後台儀表板「設定」頁面管理
- **發送服務：** Zeabur Email API
- **CSV 檔名：** `名留集團 ML Group_點數儲值名單_YYYYMMDD.csv`

---

## 環境變數

| 變數 | 必填 | 說明 |
|------|------|------|
| `DATABASE_URL` | ✅ | PostgreSQL 連線字串 |
| `GOOGLE_SHEET_ID` | ✅ | Google Sheet ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ✅ | Service Account 憑證（JSON 字串） |
| `ZEABUR_EMAIL_API_KEY` | ❌ | Zeabur Email API Key |
| `EMAIL_FROM` | ❌ | 發件人（需為已驗證網域，例如 report@mlgroup.vip） |
| `EMAIL_RECIPIENTS` | ❌ | 預設收件人（可從後台 UI 覆蓋，建議用後台設定） |
| `WEBHOOK_SECRET` | ❌ | Webhook 安全驗證（可選） |
| `MIN_ORDER_AMOUNT` | ❌ | 最低訂單金額篩選（預設 1000） |

---

## 部署資訊

### Zeabur 服務

| 服務 | 說明 |
|------|------|
| bos-etmall 後端 | Python FastAPI |
| bos-etmall 資料庫 | PostgreSQL |

### Google Cloud

- **Project：** gen-lang-client-0895534454
- **Service Account：** pos-backend-sheets@gen-lang-client-0895534454.iam.gserviceaccount.com
- **啟用 API：** Google Sheets API

### Zeabur Email

- **網域：** mlgroup.vip（已驗證）
- **發件人：** report@mlgroup.vip

---

## 本機開發

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
open http://localhost:8000/dashboard
```

---

## 檔案結構

```
pos-backend/
├── main.py          # FastAPI 主程式（路由、排程）
├── models.py        # 資料表定義（Order、Setting、EmailLog）
├── schemas.py       # API 資料格式
├── database.py      # DB 連線
├── sheets.py        # Google Sheets 整合
├── email_service.py # Zeabur Email 報表
├── dashboard.py     # 監控儀表板 HTML
├── config.py        # 環境變數
├── Dockerfile       # 容器化
├── zbpack.json      # Zeabur 設定
└── .env.example     # 環境變數範本
```
