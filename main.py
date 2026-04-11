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

        send_daily_report(new_orders, yesterday)

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


@app.post("/admin/send-report-now")
def trigger_report_now():
    """手動觸發今日 Email 報表（測試用）"""
    run_daily_email()
    return {"status": "ok", "message": "Report triggered"}
