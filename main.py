import logging
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, Header
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

        send_daily_report(new_orders, yesterday, fields)

        for o in new_orders:
            o.emailed = True
        db.commit()
        logger.info(f"Daily email done: {len(new_orders)} orders")
    except Exception as e:
        logger.error(f"Daily email job failed: {e}")
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

    scheduler.shutdown()


app = FastAPI(
    title="POS Webhook Backend",
    description="接收 POS 訂單、篩選符合條件名單、同步 Google Sheet + 每日 Email",
    version="1.0.0",
    lifespan=lifespan,
)


def verify_secret(x_webhook_secret: str = Header(default="")):
    """可選：驗證 POS 傳來的 Secret Header"""
    if settings.WEBHOOK_SECRET and x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


@app.get("/dashboard", response_class=HTMLResponse)
def monitoring_dashboard():
    return DASHBOARD_HTML


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.post("/webhook/order", response_model=schemas.WebhookResponse)
def receive_order(
    payload: schemas.OrderWebhook,
    db: Session = Depends(get_db),
    _: None = Depends(verify_secret),
):
    """
    POS 系統在訂單成立後 POST 到此端點。
    系統會篩選：訂單狀態已成立 + 消費金額 ≥ 1000。
    """
    # 防重複：訂單編號已存在則跳過
    existing = db.query(models.Order).filter(models.Order.order_id == payload.order_id).first()
    if existing:
        return schemas.WebhookResponse(
            status="duplicate",
            message="Order already exists",
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


@app.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    store_id: str = None,
    db: Session = Depends(get_db),
):
    """查詢已儲存的符合條件訂單"""
    query = db.query(models.Order)
    if store_id:
        query = query.filter(models.Order.store_id == store_id)
    return query.order_by(models.Order.received_at.desc()).offset(skip).limit(limit).all()


@app.get("/admin/settings")
def get_settings(db: Session = Depends(get_db)):
    """取得後台設定"""
    rows = db.query(models.Setting).all()
    return {r.key: r.value for r in rows}


@app.post("/admin/settings")
def update_settings(data: dict, db: Session = Depends(get_db)):
    """更新後台設定"""
    for key, value in data.items():
        row = db.query(models.Setting).filter(models.Setting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(models.Setting(key=key, value=value))
    db.commit()
    return {"status": "ok"}


@app.post("/admin/send-report-now")
def trigger_report_now(db: Session = Depends(get_db)):
    """手動觸發昨日 Email 報表"""
    run_daily_email()
    return {"status": "ok", "message": "Report triggered"}


@app.post("/admin/send-today-report")
def send_today_report(db: Session = Depends(get_db)):
    """立即發送今日正式報表"""
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

    send_daily_report(orders, today, fields)
    return {"status": "ok", "message": f"Today report sent: {len(orders)} orders"}


@app.post("/admin/test-email")
def test_email(db: Session = Depends(get_db)):
    """發送測試信（使用今日所有訂單）"""
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
        json={"from": settings.EMAIL_FROM, "to": recipients, "subject": "BOS-ETMALL 測試信", "html": html},
        timeout=15,
    )
    return {"status": "ok", "zeabur_response": resp.json(), "recipients": recipients}
