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
  └── Gmail（每天 09:00 寄報表）
```

---

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/webhook/order` | 接收 POS 訂單（主要接口） |
| `GET` | `/orders` | 查詢所有訂單 |
| `GET` | `/health` | 健康檢查 |
| `POST` | `/admin/send-report-now` | 手動觸發 Email 報表（測試用） |
| `GET` | `/docs` | Swagger 互動文件 |

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

---

## 資料庫欄位（orders 表）

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

---

## Google Sheets

**試算表：** [BOS-ETMALL](https://docs.google.com/spreadsheets/d/1iiP-PyMWOlaqpKP9Q_EzZ8Z2KqNIII1-0Ac4thUY6m4/edit)

每筆符合條件的訂單會即時寫入第一個工作表，欄位順序：

```
訂單編號 | 店家ID | 店家名稱 | 消費者手機 | 消費者姓名 | 消費金額 | 訂單狀態 | 訂單時間 | 接收時間
```

---

## 每日 Email 報表

- **時間：** 每天早上 09:00（台北時間）
- **內容：** 前一天新收到的訂單名單
- **收件人：** 設定於 `EMAIL_RECIPIENTS` 環境變數（逗號分隔多個信箱）

---

## 環境變數

| 變數 | 必填 | 說明 |
|------|------|------|
| `DATABASE_URL` | ✅ | PostgreSQL 連線字串 |
| `GOOGLE_SHEET_ID` | ✅ | Google Sheet ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ✅ | Service Account 憑證（JSON 字串） |
| `SMTP_USER` | ❌ | Gmail 信箱 |
| `SMTP_PASSWORD` | ❌ | Gmail 應用程式密碼 |
| `EMAIL_RECIPIENTS` | ❌ | 收件人（逗號分隔） |
| `MIN_ORDER_AMOUNT` | ❌ | 最低金額篩選（預設 1000，目前已停用） |

---

## 部署資訊

### Zeabur 服務

| 服務 | 說明 |
|------|------|
| bos-etmall 後端 | Python FastAPI |
| bos-etmall 資料庫 | PostgreSQL 18.3 |

### 資料庫連線

```
Host: 54.168.143.169
Port: 31225
Database: zeabur
User: root
```

### Google Cloud

- **Project：** gen-lang-client-0895534454 (AI Image to Video)
- **Service Account：** pos-backend-sheets@gen-lang-client-0895534454.iam.gserviceaccount.com
- **啟用 API：** Google Sheets API

---

## 本機開發

```bash
# 安裝套件
pip install -r requirements.txt

# 建立 .env（參考 .env.example）
cp .env.example .env

# 啟動
uvicorn main:app --reload

# Swagger 文件
open http://localhost:8000/docs
```

---

## 檔案結構

```
pos-backend/
├── main.py          # FastAPI 主程式
├── models.py        # 資料表定義
├── schemas.py       # API 資料格式
├── database.py      # DB 連線
├── sheets.py        # Google Sheets 整合
├── email_service.py # Email 報表
├── config.py        # 環境變數
├── Dockerfile       # 容器化
├── zbpack.json      # Zeabur 設定
└── .env.example     # 環境變數範本
```
