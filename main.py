import logging
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import models
import schemas
from config import settings
from dashboard import DASHBOARD_HTML
from database import Base, engine, get_db
from email_service import send_daily_report
from sheets import sync_order_to_sheet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 訂單狀態白名單（POS 系統可能用不同詞）
VALID_STATUSES = {"completed", "paid", "confirmed", "success", "done"}

scheduler = AsyncIOScheduler(timezone="Asia/Taipei")


def run_daily_email():
    """每天 09:00 發送昨日新單 Email"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        yesterday = date.today() - timedelta(days=1)
        start = datetime.combine(yesterday, datetime.min.time())
        end = datetime.combine(date.today(), datetime.min.time())

        new_orders = (
            db.query(models.Order)
            .filter(models.Order.received_at >= start)
            .filter(models.Order.received_at < end)
            .filter(models.Order.emailed == False)
            .all()
        )

        # 優先讀 DB 設定的收件人，fallback 到環境變數
        recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
        if recipients_row and recipients_row.value:
            settings.EMAIL_RECIPIENTS = recipients_row.value

        fields_row = db.query(models.Setting).filter(models.Setting.key == "email_fields").first()
        fields = fields_row.value.split(",") if fields_row and fields_row.value else None

        recip = settings.get_recipients()
        send_daily_report(new_orders, yesterday, fields)

        for o in new_orders:
            o.emailed = True
        db.add(models.EmailLog(
            trigger="schedule",
            date_range=str(yesterday),
            order_count=len(new_orders),
            recipients=",".join(recip),
            status="ok",
        ))
        db.commit()
        logger.info(f"Daily email done: {len(new_orders)} orders")
    except Exception as e:
        logger.error(f"Daily email job failed: {e}")
        try:
            db.add(models.EmailLog(trigger="schedule", date_range=str(date.today() - timedelta(days=1)),
                                   order_count=0, recipients="", status="error", error=str(e)))
            db.commit()
        except Exception:
            pass
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 建立資料表
    Base.metadata.create_all(bind=engine)

    # 啟動排程：每天 09:00 台北時間（僅在 Email 設定完成時啟用）
    if settings.email_enabled:
        scheduler.add_job(run_daily_email, "cron", hour=9, minute=0, id="daily_email")
        scheduler.start()
        logger.info("Scheduler started — daily email at 09:00 Taipei time")
    else:
        logger.info("Email not configured — scheduler skipped")

    yield

    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="BOS-ETMALL 訂單管理系統",
    description="""
## 系統說明

BOS-ETMALL 後端 API，負責接收 POS 訂單、同步 Google Sheets，並每日自動發送 Email 報表。

### 主要功能
- **Webhook 接收**：POS 系統下單後即時推送，自動寫入資料庫
- **Google Sheets 同步**：每筆訂單即時寫入試算表
- **每日 Email 報表**：每天 09:00（台北時間）自動發送前一日名單，含 CSV 附件
- **後台管理**：可視化儀表板，支援收件人、報表欄位設定，及手動發送

### 訂單篩選條件
- 訂單狀態：`completed` / `paid` / `confirmed` / `success` / `done`
- 消費金額：≥ NT$1,000

### 相關連結
- [後台儀表板](/dashboard)
- [GitHub](https://github.com/jason121380/bos-etmall)
""",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_tags=[
        {"name": "Webhook", "description": "POS 訂單推送接口"},
        {"name": "訂單查詢", "description": "查詢已儲存的訂單資料"},
        {"name": "後台管理", "description": "Email、報表、設定管理"},
        {"name": "系統", "description": "健康檢查、儀表板"},
    ],
)


def verify_secret(x_webhook_secret: str = Header(default="")):
    """可選：驗證 POS 傳來的 Secret Header"""
    if settings.WEBHOOK_SECRET and x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


NOTION_DOCS_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
  body { font-family: 'Inter', -apple-system, sans-serif !important; background: #ffffff !important; }
  .swagger-ui { font-family: 'Inter', -apple-system, sans-serif !important; }
  .swagger-ui .topbar { background: #ffffff !important; border-bottom: 1px solid #e9e9e7 !important; padding: 12px 24px !important; }
  .swagger-ui .topbar .download-url-wrapper { display: none !important; }
  .swagger-ui .topbar-wrapper { display: flex; align-items: center; gap: 12px; }
  .swagger-ui .topbar-wrapper .link { display: flex; align-items: center; gap: 10px; text-decoration: none; }
  .swagger-ui .topbar-wrapper .link img { display: none; }
  .swagger-ui .topbar-wrapper .link::before {
    content: 'BOS-ETMALL'; font-size: 15px; font-weight: 600; color: #1a1a1a; letter-spacing: -0.3px;
  }
  .swagger-ui .info { margin: 32px 0 24px !important; padding: 0 !important; }
  .swagger-ui .info .title { font-size: 24px !important; font-weight: 700 !important; color: #1a1a1a !important; letter-spacing: -0.5px !important; }
  .swagger-ui .info .description { color: #6b6b6b !important; font-size: 14px !important; line-height: 1.7 !important; }
  .swagger-ui .info .description h2 { font-size: 16px !important; font-weight: 600 !important; color: #1a1a1a !important; margin: 16px 0 8px !important; }
  .swagger-ui .info .description ul { padding-left: 20px !important; }
  .swagger-ui .info .description code { background: #f7f6f3 !important; padding: 1px 6px !important; border-radius: 4px !important; font-size: 12px !important; color: #eb5757 !important; }
  .swagger-ui .info .description a { color: #2383e2 !important; }
  .swagger-ui .scheme-container { background: #ffffff !important; border: none !important; padding: 0 !important; box-shadow: none !important; }
  .swagger-ui .opblock-tag { font-size: 14px !important; font-weight: 600 !important; color: #1a1a1a !important; border-bottom: 1px solid #e9e9e7 !important; padding: 12px 0 !important; }
  .swagger-ui .opblock-tag:hover { background: #f7f6f3 !important; }
  .swagger-ui .opblock { border: 1px solid #e9e9e7 !important; border-radius: 6px !important; margin: 6px 0 !important; box-shadow: none !important; }
  .swagger-ui .opblock.opblock-post { border-color: #e9e9e7 !important; background: #ffffff !important; }
  .swagger-ui .opblock.opblock-get { border-color: #e9e9e7 !important; background: #ffffff !important; }
  .swagger-ui .opblock .opblock-summary { padding: 10px 14px !important; }
  .swagger-ui .opblock .opblock-summary-method { border-radius: 4px !important; font-size: 11px !important; font-weight: 600 !important; min-width: 60px !important; padding: 4px 8px !important; }
  .swagger-ui .opblock.opblock-post .opblock-summary-method { background: #0f7b0f !important; }
  .swagger-ui .opblock.opblock-get .opblock-summary-method { background: #2383e2 !important; }
  .swagger-ui .opblock .opblock-summary-path { font-size: 13px !important; font-weight: 500 !important; color: #1a1a1a !important; font-family: 'SF Mono', 'Fira Code', monospace !important; }
  .swagger-ui .opblock .opblock-summary-description { color: #6b6b6b !important; font-size: 13px !important; }
  .swagger-ui .opblock-body { border-top: 1px solid #e9e9e7 !important; }
  .swagger-ui .opblock-description-wrapper p, .swagger-ui .opblock-description-wrapper li { color: #4a4a4a !important; font-size: 13px !important; line-height: 1.6 !important; }
  .swagger-ui .opblock-description-wrapper code { background: #f7f6f3 !important; padding: 1px 5px !important; border-radius: 3px !important; font-size: 12px !important; color: #eb5757 !important; }
  .swagger-ui .btn { border-radius: 5px !important; font-size: 13px !important; font-weight: 500 !important; }
  .swagger-ui .btn.execute { background: #1a1a1a !important; border-color: #1a1a1a !important; }
  .swagger-ui .btn.execute:hover { background: #333 !important; }
  .swagger-ui table thead tr th { font-size: 12px !important; font-weight: 600 !important; color: #6b6b6b !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
  .swagger-ui .response-col_status { font-weight: 600 !important; }
  .swagger-ui .model-box { background: #f7f6f3 !important; border-radius: 6px !important; }
  .swagger-ui section.models { border: 1px solid #e9e9e7 !important; border-radius: 6px !important; }
  .swagger-ui section.models h4 { font-size: 14px !important; color: #1a1a1a !important; }
  #swagger-ui { max-width: 1100px !important; margin: 0 auto !important; padding: 0 24px 48px !important; }
</style>
"""


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    base = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="BOS-ETMALL API 文件",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1, "docExpansion": "list"},
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_favicon_url="",
    )
    html = base.body.decode("utf-8").replace("</head>", NOTION_DOCS_CSS + "</head>")
    return HTMLResponse(html)


@app.get("/dashboard", response_class=HTMLResponse, tags=["系統"], summary="後台管理儀表板")
def monitoring_dashboard():
    """開啟視覺化後台，可查看訂單統計、設定 Email 收件人與報表欄位、手動發送報表。"""
    return DASHBOARD_HTML


@app.get("/health", tags=["系統"], summary="健康檢查")
def health():
    """回傳 API 服務狀態與伺服器時間，用於確認服務是否正常運作。"""
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.post(
    "/webhook/order",
    response_model=schemas.WebhookResponse,
    tags=["Webhook"],
    summary="接收 POS 訂單",
)
def receive_order(
    payload: schemas.OrderWebhook,
    db: Session = Depends(get_db),
    _: None = Depends(verify_secret),
):
    """
    POS 系統下單後呼叫此端點，將訂單寫入資料庫並同步 Google Sheets。

    **自動篩選條件：**
    - 訂單狀態：`completed` / `paid` / `confirmed` / `success` / `done`
    - 消費金額：≥ NT$1,000

    **防重複機制：** 相同 `order_id` 只會寫入一次。

    **Header（可選）：**
    - `x-webhook-secret`：若後台有設定 `WEBHOOK_SECRET`，需帶入此 Header 驗證
    """
    # 防重複：訂單編號已存在則跳過
    existing = db.query(models.Order).filter(models.Order.order_id == payload.order_id).first()
    if existing:
        return schemas.WebhookResponse(
            status="duplicate",
            message="Order already exists",
            order_id=payload.order_id,
        )

    # 篩選：訂單狀態 + 消費金額
    if payload.order_status.lower() not in VALID_STATUSES:
        return schemas.WebhookResponse(
            status="ignored",
            message=f"Order status '{payload.order_status}' not in valid list",
            order_id=payload.order_id,
        )
    if payload.amount < settings.MIN_ORDER_AMOUNT:
        return schemas.WebhookResponse(
            status="ignored",
            message=f"Amount {payload.amount} below minimum {settings.MIN_ORDER_AMOUNT}",
            order_id=payload.order_id,
        )

    # 寫入資料庫
    order = models.Order(
        order_id=payload.order_id,
        store_id=payload.store_id,
        store_name=payload.store_name,
        consumer_phone=payload.consumer_phone,
        consumer_name=payload.consumer_name,
        amount=payload.amount,
        order_status=payload.order_status,
        order_time=payload.order_time,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # 同步 Google Sheets（可選，未設定時跳過）
    if settings.sheets_enabled:
        synced = sync_order_to_sheet(order)
        if synced:
            order.synced_to_sheet = True
            db.commit()

    logger.info(f"New order accepted: {order.order_id} | {order.consumer_phone} | NT${order.amount}")

    return schemas.WebhookResponse(
        status="accepted",
        message="Order received and stored",
        order_id=order.order_id,
    )


@app.get("/orders", response_model=list[schemas.OrderOut], tags=["訂單查詢"], summary="查詢訂單列表")
def list_orders(
    skip: int = 0,
    limit: int = 100,
    store_id: str = None,
    db: Session = Depends(get_db),
):
    """
    查詢已儲存的訂單，支援分頁與店家篩選。

    **參數說明：**
    - `skip`：跳過前幾筆（預設 0）
    - `limit`：最多回傳幾筆（預設 100）
    - `store_id`：依店家編號篩選（選填）
    """
    query = db.query(models.Order)
    if store_id:
        query = query.filter(models.Order.store_id == store_id)
    return query.order_by(models.Order.received_at.desc()).offset(skip).limit(limit).all()


@app.get("/admin/settings", tags=["後台管理"], summary="取得後台設定")
def get_settings(db: Session = Depends(get_db)):
    """
    取得所有後台設定，以 key-value 格式回傳。

    **常用 key：**
    - `email_recipients`：收件人清單（逗號分隔）
    - `email_fields`：報表欄位（逗號分隔）
    """
    rows = db.query(models.Setting).all()
    return {r.key: r.value for r in rows}


@app.post("/admin/settings", tags=["後台管理"], summary="更新後台設定")
def update_settings(data: dict, db: Session = Depends(get_db)):
    """
    更新後台設定，傳入 JSON 物件，key 為設定名稱，value 為設定值。

    **範例：**
    ```json
    {
      "email_recipients": "a@example.com,b@example.com",
      "email_fields": "store_name,consumer_phone,order_time"
    }
    ```
    """
    for key, value in data.items():
        row = db.query(models.Setting).filter(models.Setting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(models.Setting(key=key, value=value))
    db.commit()
    return {"status": "ok"}


@app.post("/admin/send-report-now", tags=["後台管理"], summary="手動發送昨日報表")
def trigger_report_now(db: Session = Depends(get_db)):
    """
    手動觸發昨日 Email 報表（與排程邏輯相同）。

    只會發送「昨日」尚未標記 `emailed=True` 的訂單，發送後會更新 `emailed` 旗標。
    """
    run_daily_email()
    return {"status": "ok", "message": "Report triggered"}


@app.post("/admin/send-today-report", tags=["後台管理"], summary="立即發送今日報表")
def send_today_report(db: Session = Depends(get_db)):
    """立即發送今日（當天）所有訂單的正式報表，含 CSV 附件。"""
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today + timedelta(days=1), datetime.min.time())

    orders = (
        db.query(models.Order)
        .filter(models.Order.received_at >= start)
        .filter(models.Order.received_at < end)
        .all()
    )

    # 優先讀 DB 設定的收件人
    recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
    if recipients_row and recipients_row.value:
        settings.EMAIL_RECIPIENTS = recipients_row.value

    fields_row = db.query(models.Setting).filter(models.Setting.key == "email_fields").first()
    fields = fields_row.value.split(",") if fields_row and fields_row.value else None

    recipients = settings.get_recipients()
    send_daily_report(orders, today, fields)
    db.add(models.EmailLog(
        trigger="manual_today",
        date_range=str(today),
        order_count=len(orders),
        recipients=",".join(recipients),
        status="ok",
    ))
    db.commit()
    return {"status": "ok", "message": f"Today report sent: {len(orders)} orders"}


@app.post("/admin/send-date-report", tags=["後台管理"], summary="發送指定日期區間報表")
def send_date_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """
    發送指定日期區間的訂單報表。

    **參數（Query String）：**
    - `start_date`：開始日期，格式 `YYYY-MM-DD`
    - `end_date`：結束日期，格式 `YYYY-MM-DD`（可與 start_date 相同，表示單日）

    **範例：**
    - 單日：`/admin/send-date-report?start_date=2026-04-10&end_date=2026-04-10`
    - 區間：`/admin/send-date-report?start_date=2026-04-01&end_date=2026-04-10`
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式錯誤，請使用 YYYY-MM-DD")

    if end < start:
        raise HTTPException(status_code=400, detail="結束日期不能早於開始日期")

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end + timedelta(days=1), datetime.min.time())

    orders = (
        db.query(models.Order)
        .filter(models.Order.received_at >= start_dt)
        .filter(models.Order.received_at < end_dt)
        .all()
    )

    recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
    if recipients_row and recipients_row.value:
        settings.EMAIL_RECIPIENTS = recipients_row.value

    fields_row = db.query(models.Setting).filter(models.Setting.key == "email_fields").first()
    fields = fields_row.value.split(",") if fields_row and fields_row.value else None

    label = start_date if start_date == end_date else f"{start_date} ~ {end_date}"
    from email_service import build_email_html, build_csv_base64
    import requests as req
    from config import settings as cfg

    recipients = cfg.get_recipients()
    if not recipients:
        raise HTTPException(status_code=400, detail="未設定收件人")

    report_date = start  # use start date as label date
    html_content = build_email_html(orders, report_date, fields)
    subject = f"{label}，點數儲值名單 — 共 {len(orders)} 筆"
    csv_b64 = build_csv_base64(orders, fields or ["store_name", "consumer_phone", "order_time"])
    filename = f"名留集團 ML Group_點數儲值名單_{start_date}_{end_date}.csv"

    resp = req.post(
        "https://api.zeabur.com/api/v1/zsend/emails",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg.ZEABUR_EMAIL_API_KEY}"},
        json={
            "from": f"名留集團 ML Group <{cfg.EMAIL_FROM}>",
            "to": recipients,
            "subject": subject,
            "html": html_content,
            "attachments": [{"filename": filename, "content": csv_b64, "content_type": "text/csv"}],
        },
        timeout=15,
    )
    resp.raise_for_status()
    db.add(models.EmailLog(
        trigger="manual_date",
        date_range=label,
        order_count=len(orders),
        recipients=",".join(recipients),
        status="ok",
    ))
    db.commit()
    return {"status": "ok", "message": f"報表已發送：{label}，共 {len(orders)} 筆"}


@app.get("/admin/email-logs", tags=["後台管理"], summary="查詢 Email 發送紀錄")
def get_email_logs(limit: int = 30, db: Session = Depends(get_db)):
    """回傳最近 N 筆 Email 發送紀錄（預設 30 筆），最新的在最前。"""
    rows = db.query(models.EmailLog).order_by(models.EmailLog.sent_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "sent_at": r.sent_at.isoformat() if r.sent_at else None,
            "trigger": r.trigger,
            "date_range": r.date_range,
            "order_count": r.order_count,
            "recipients": r.recipients,
            "status": r.status,
            "error": r.error,
        }
        for r in rows
    ]


@app.post("/admin/test-email", tags=["後台管理"], summary="發送測試信")
def test_email(db: Session = Depends(get_db)):
    """
    發送測試信，內容為最新 5 筆訂單（不論日期）。

    用於確認 Email 設定正確、收件人能收到信。不會更新 `emailed` 旗標。
    """
    import requests as req
    recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
    recipients_str = (recipients_row.value if recipients_row and recipients_row.value else settings.EMAIL_RECIPIENTS)
    recipients = [e.strip() for e in recipients_str.split(",") if e.strip()]
    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients configured")
    if not settings.ZEABUR_EMAIL_API_KEY:
        raise HTTPException(status_code=400, detail="ZEABUR_EMAIL_API_KEY not set")

    orders = db.query(models.Order).order_by(models.Order.received_at.desc()).limit(5).all()
    rows = "".join(
        f"<tr><td>{o.order_id}</td><td>{o.store_name or o.store_id}</td>"
        f"<td>{o.consumer_phone}</td><td>NT$ {o.amount:,.0f}</td></tr>"
        for o in orders
    )
    html = f"""<h2>BOS-ETMALL Email 測試信</h2>
    <p>這是系統測試信，最新 {len(orders)} 筆訂單：</p>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">
    <tr><th>訂單編號</th><th>店家</th><th>手機</th><th>金額</th></tr>
    {rows}
    </table>"""

    resp = req.post(
        "https://api.zeabur.com/api/v1/zsend/emails",
        headers={"Authorization": f"Bearer {settings.ZEABUR_EMAIL_API_KEY}", "Content-Type": "application/json"},
        json={"from": f"名留集團 ML Group <{settings.EMAIL_FROM}>", "to": recipients, "subject": "名留集團 ML Group — Email 測試信", "html": html},
        timeout=15,
    )
    result = resp.json()
    db.add(models.EmailLog(
        trigger="test",
        date_range="—",
        order_count=len(orders),
        recipients=",".join(recipients),
        status="ok",
    ))
    db.commit()
    return {"status": "ok", "zeabur_response": result, "recipients": recipients}
