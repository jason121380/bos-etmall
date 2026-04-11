# BOS-ETMALL Webhook 串接文件

**版本：** v1.0  
**更新日期：** 2026-04-11  
**Webhook 端點：** `https://bos-etmall.zeabur.app`

---

## 串接說明

當訂單成立時，POS 系統需主動 POST 訂單資料至本系統 Webhook。  
本系統收到後將自動記錄並同步至後台報表。

---

## API 端點

### 訂單通知

```
POST https://bos-etmall.zeabur.app/webhook/order
```

### Request Headers

| Header | 值 | 說明 |
|--------|-----|------|
| `Content-Type` | `application/json` | 必填 |

### Request Body（JSON）

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `order_id` | string | ✅ | 訂單唯一編號（不可重複） |
| `store_id` | string | ✅ | 店家編號 |
| `store_name` | string | ❌ | 店家名稱 |
| `consumer_phone` | string | ✅ | 消費者手機號碼 |
| `consumer_name` | string | ❌ | 消費者姓名 |
| `amount` | number | ✅ | 消費金額（元） |
| `order_status` | string | ✅ | 訂單狀態（見下表） |
| `order_time` | string | ✅ | 訂單時間（ISO 8601 格式） |

### 訂單狀態 `order_status` 可接受值

| 值 | 說明 |
|----|------|
| `completed` | 訂單完成 |
| `paid` | 已付款 |
| `confirmed` | 已確認 |
| `success` | 成功 |
| `done` | 完成 |

---

## 範例

### Request

```bash
curl -X POST https://bos-etmall.zeabur.app/webhook/order \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "POS-20260411-00123",
    "store_id": "STORE-001",
    "store_name": "信義旗艦店",
    "consumer_phone": "0912345678",
    "consumer_name": "王小明",
    "amount": 1500,
    "order_status": "completed",
    "order_time": "2026-04-11T10:30:00+08:00"
  }'
```

### Response（成功接收）

```json
{
  "status": "accepted",
  "message": "Order received and stored",
  "order_id": "POS-20260411-00123"
}
```

### Response（重複訂單）

```json
{
  "status": "duplicate",
  "message": "Order already exists",
  "order_id": "POS-20260411-00123"
}
```

---

## 健康檢查

```
GET https://bos-etmall.zeabur.app/health
```

Response：
```json
{
  "status": "ok",
  "time": "2026-04-11T10:00:00.000000"
}
```

---

## 注意事項

1. `order_id` 為唯一識別碼，重複傳送同一訂單不會重複寫入
2. `order_time` 請使用 ISO 8601 格式，例如 `2026-04-11T10:30:00+08:00`
3. 請在訂單成立後 **即時** 發送 Webhook，避免資料遺漏
4. 如 Webhook 發送失敗（網路問題），建議實作 retry 機制（最多 3 次，間隔 5 秒）

---

## 聯絡窗口

如有串接問題，請聯繫：jason121380@gmail.com
