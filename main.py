import logging
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
import schemas
from config import settings
from dashboard import DASHBOARD_HTML
from database import Base, engine, get_db
from email_service import dedupe_same_day_store_phone, send_daily_report
from sheets import mark_order_deleted_in_sheet, restore_order_in_sheet, sync_order_to_sheet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 訂單狀態白名單（POS 系統可能用不同詞）
VALID_STATUSES = {"completed", "paid", "confirmed", "success", "done"}

TAIPEI_TZ = ZoneInfo("Asia/Taipei")

scheduler = AsyncIOScheduler(timezone="Asia/Taipei")


def _dedupe_enabled(db: Session) -> bool:
    """讀取 settings.email_dedupe_same_day_phone，預設為 True。"""
    row = db.query(models.Setting).filter(models.Setting.key == "email_dedupe_same_day_phone").first()
    if not row or row.value is None:
        return True
    return str(row.value).strip().lower() != "false"


def taipei_day_to_utc_range(d: date) -> tuple:
    """將台北時區的某天轉成 naive UTC 的 (start, end) datetime，用於查 DB。"""
    start_tp = datetime(d.year, d.month, d.day, tzinfo=TAIPEI_TZ)
    end_tp = start_tp + timedelta(days=1)
    return (
        start_tp.astimezone(timezone.utc).replace(tzinfo=None),
        end_tp.astimezone(timezone.utc).replace(tzinfo=None),
    )


def run_daily_email():
    """每天 09:00 發送昨日新單 Email"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        now_taipei = datetime.now(TAIPEI_TZ)
        yesterday = (now_taipei - timedelta(days=1)).date()
        start, end = taipei_day_to_utc_range(yesterday)

        new_orders = (
            db.query(models.Order)
            .filter(models.Order.received_at >= start)
            .filter(models.Order.received_at < end)
            .filter(models.Order.emailed == False)
            .filter(models.Order.deleted_at.is_(None))
            .order_by(models.Order.received_at.desc())
            .all()
        )

        # 優先讀 DB 設定的收件人，fallback 到環境變數
        recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
        if recipients_row and recipients_row.value:
            settings.EMAIL_RECIPIENTS = recipients_row.value

        fields_row = db.query(models.Setting).filter(models.Setting.key == "email_fields").first()
        fields = fields_row.value.split(",") if fields_row and fields_row.value else None

        report_orders = dedupe_same_day_store_phone(new_orders) if _dedupe_enabled(db) else new_orders

        recip = settings.get_recipients()
        send_daily_report(report_orders, yesterday, fields)

        # 已被決策（不論寄出或被去重排除）一律標記為 emailed，避免明天再被撈到
        for o in new_orders:
            o.emailed = True
        db.add(models.EmailLog(
            trigger="schedule",
            date_range=str(yesterday),
            order_count=len(report_orders),
            recipients=",".join(recip),
            status="ok",
        ))
        db.commit()
        logger.info(
            f"Daily email done: {len(report_orders)}/{len(new_orders)} orders "
            f"(dedupe excluded {len(new_orders) - len(report_orders)})"
        )
    except Exception as e:
        logger.error(f"Daily email job failed: {e}")
        try:
            db.add(models.EmailLog(trigger="schedule", date_range=str(yesterday),
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

    # Migration：為既有 orders 表補上 deleted_at 欄位（PostgreSQL 9.6+）
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE orders ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_orders_deleted_at ON orders (deleted_at)"
            ))
        logger.info("Migration ok: orders.deleted_at ensured")
    except Exception as e:
        logger.warning(f"Migration skipped or failed: {e}")

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


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    data = (STATIC_DIR / "favicon.ico").read_bytes()
    return Response(content=data, media_type="image/x-icon",
                    headers={"Cache-Control": "public, max-age=86400"})


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


@app.get("/manifest.json", include_in_schema=False)
def pwa_manifest():
    return JSONResponse({
        "name": "BOS-ETMALL 訂單後台",
        "short_name": "BOS-ETMALL",
        "description": "名留集團 ML Group 訂單管理後台",
        "start_url": "/dashboard",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#ffffff",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    })


@app.get("/icon-192.png", include_in_schema=False)
def icon_192():
    data = (STATIC_DIR / "icon-192.png").read_bytes()
    return Response(content=data, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})


@app.get("/icon-512.png", include_in_schema=False)
def icon_512():
    data = (STATIC_DIR / "icon-512.png").read_bytes()
    return Response(content=data, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    sw_code = """
const CACHE = 'bos-etmall-v1';
const PRECACHE = ['/dashboard', '/manifest.json', '/icon-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // API calls: network first
  if (url.pathname.startsWith('/admin') || url.pathname.startsWith('/orders') || url.pathname === '/health') {
    e.respondWith(fetch(e.request).catch(() => new Response('{}', {headers:{'Content-Type':'application/json'}})));
    return;
  }
  // Static: stale-while-revalidate
  e.respondWith(
    caches.match(e.request).then(cached => {
      const fresh = fetch(e.request).then(r => {
        caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        return r;
      });
      return cached || fresh;
    })
  );
});
"""
    return Response(content=sw_code, media_type="application/javascript",
                    headers={"Service-Worker-Allowed": "/"})


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


@app.delete("/admin/orders/{order_id}", tags=["後台管理"], summary="刪除單筆訂單（軟刪除）")
def delete_order(order_id: str, db: Session = Depends(get_db)):
    """
    將指定訂單移到垃圾桶（軟刪除）。資料會保留在資料庫中但不會出現在
    `/orders`、Email 報表等一般查詢；可透過 `/admin/trash/{order_id}/restore` 復原。

    若該訂單已同步 Google Sheet，Sheet 上對應列不會被刪除，
    而是將「訂單狀態」欄標記為「已刪除」。
    """
    row = (
        db.query(models.Order)
        .filter(models.Order.order_id == order_id, models.Order.deleted_at.is_(None))
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Order not found: {order_id}")

    sheet_marked = False
    if settings.sheets_enabled and row.synced_to_sheet:
        sheet_marked = mark_order_deleted_in_sheet(order_id)

    row.deleted_at = datetime.utcnow()
    db.commit()
    logger.info(f"Order soft-deleted: {order_id} (sheet_marked={sheet_marked})")
    return {"status": "ok", "order_id": order_id, "sheet_marked": sheet_marked}


@app.post("/admin/orders/bulk-delete", tags=["後台管理"], summary="批次刪除訂單（軟刪除）")
def bulk_delete_orders(data: dict, db: Session = Depends(get_db)):
    """
    批次將訂單移到垃圾桶（軟刪除）。

    **Request Body：**
    ```json
    { "order_ids": ["POS-001", "POS-002"] }
    ```

    已同步 Google Sheet 的訂單，Sheet 上對應列會被標記為「已刪除」而非移除。
    """
    ids = data.get("order_ids") or []
    if not isinstance(ids, list) or not ids:
        raise HTTPException(status_code=400, detail="order_ids 必須為非空陣列")

    rows = (
        db.query(models.Order)
        .filter(models.Order.order_id.in_(ids), models.Order.deleted_at.is_(None))
        .all()
    )

    sheet_marked = 0
    now = datetime.utcnow()
    for r in rows:
        if settings.sheets_enabled and r.synced_to_sheet:
            if mark_order_deleted_in_sheet(r.order_id):
                sheet_marked += 1
        r.deleted_at = now

    db.commit()
    logger.info(f"Bulk soft-deleted {len(rows)} orders (sheet_marked={sheet_marked})")
    return {"status": "ok", "deleted": len(rows), "sheet_marked": sheet_marked}


@app.get("/admin/trash", response_model=list[schemas.OrderOut], tags=["後台管理"], summary="查詢垃圾桶")
def get_trash(limit: int = 200, db: Session = Depends(get_db)):
    """回傳所有已軟刪除的訂單，依 `deleted_at` 由新到舊排序。"""
    return (
        db.query(models.Order)
        .filter(models.Order.deleted_at.isnot(None))
        .order_by(models.Order.deleted_at.desc())
        .limit(limit)
        .all()
    )


@app.post("/admin/trash/{order_id}/restore", tags=["後台管理"], summary="從垃圾桶復原訂單")
def restore_order(order_id: str, db: Session = Depends(get_db)):
    """
    將已軟刪除的訂單還原（`deleted_at` 設為 NULL）。
    若該訂單原本有同步 Google Sheet，Sheet 上的狀態欄也會從「已刪除」還原為原本的訂單狀態。
    """
    row = (
        db.query(models.Order)
        .filter(models.Order.order_id == order_id, models.Order.deleted_at.isnot(None))
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Deleted order not found: {order_id}")

    row.deleted_at = None
    db.commit()

    sheet_restored = False
    if settings.sheets_enabled and row.synced_to_sheet:
        sheet_restored = restore_order_in_sheet(order_id, row.order_status)

    logger.info(f"Order restored: {order_id} (sheet_restored={sheet_restored})")
    return {"status": "ok", "order_id": order_id, "sheet_restored": sheet_restored}


@app.delete("/admin/trash/{order_id}", tags=["後台管理"], summary="永久刪除訂單")
def permanent_delete_order(order_id: str, db: Session = Depends(get_db)):
    """
    永久從資料庫刪除已在垃圾桶中的訂單，**此動作無法復原**。
    Google Sheet 上的「已刪除」標記不會變動。
    """
    row = (
        db.query(models.Order)
        .filter(models.Order.order_id == order_id, models.Order.deleted_at.isnot(None))
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Deleted order not found: {order_id}")

    db.delete(row)
    db.commit()
    logger.info(f"Order permanently deleted: {order_id}")
    return {"status": "ok", "order_id": order_id}


@app.get("/orders", tags=["訂單查詢"], summary="查詢訂單列表")
def list_orders(
    skip: int = 0,
    limit: int = 50,
    store_id: str = None,
    date: str = None,
    db: Session = Depends(get_db),
):
    """
    查詢已儲存的訂單，支援分頁、店家篩選、日期篩選。

    **參數說明：**
    - `skip`：跳過前幾筆（預設 0）
    - `limit`：最多回傳幾筆（預設 50）
    - `store_id`：依店家編號篩選（選填）
    - `date`：依日期篩選（台北時區 `YYYY-MM-DD`，選填）

    **回傳：** `{ "orders": [...], "total": N }`
    """
    query = db.query(models.Order).filter(models.Order.deleted_at.is_(None))
    if store_id:
        query = query.filter(models.Order.store_id == store_id)
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式錯誤，請使用 YYYY-MM-DD")
        start, end = taipei_day_to_utc_range(d)
        query = query.filter(models.Order.received_at >= start, models.Order.received_at < end)

    total = query.count()
    orders = query.order_by(models.Order.received_at.desc()).offset(skip).limit(limit).all()

    return {
        "orders": [schemas.OrderOut.model_validate(o).model_dump() for o in orders],
        "total": total,
    }


@app.get("/admin/stats", tags=["後台管理"], summary="儀表板統計資料")
def get_stats(db: Session = Depends(get_db)):
    """回傳今日/本月/累計訂單統計、已同步筆數、店家分布（全部由伺服器端以台北時區計算）。"""
    from sqlalchemy import func as F

    base = db.query(models.Order).filter(models.Order.deleted_at.is_(None))

    now_taipei = datetime.now(TAIPEI_TZ)
    today = now_taipei.date()
    month_start = today.replace(day=1)

    today_start, today_end = taipei_day_to_utc_range(today)
    month_start_utc, _ = taipei_day_to_utc_range(month_start)

    today_q = base.filter(models.Order.received_at >= today_start, models.Order.received_at < today_end)
    month_q = base.filter(models.Order.received_at >= month_start_utc, models.Order.received_at < today_end)

    total_count = base.count()
    total_amount = base.with_entities(F.coalesce(F.sum(models.Order.amount), 0)).scalar()
    synced_count = base.filter(models.Order.synced_to_sheet == True).count()

    store_label = F.coalesce(models.Order.store_name, models.Order.store_id)
    stores = (
        base.with_entities(
            store_label.label("name"),
            F.count().label("count"),
            F.sum(models.Order.amount).label("amount"),
        )
        .group_by(store_label)
        .order_by(F.count().desc())
        .all()
    )

    return {
        "today": {
            "count": today_q.count(),
            "amount": today_q.with_entities(F.coalesce(F.sum(models.Order.amount), 0)).scalar(),
        },
        "month": {
            "count": month_q.count(),
            "amount": month_q.with_entities(F.coalesce(F.sum(models.Order.amount), 0)).scalar(),
        },
        "total": {"count": total_count, "amount": total_amount},
        "synced": synced_count,
        "stores": [{"name": s.name or "—", "count": s.count, "amount": float(s.amount or 0)} for s in stores],
    }


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
    """立即發送今日（當天，台北時間）所有訂單的正式報表，含 CSV 附件。"""
    today = datetime.now(TAIPEI_TZ).date()
    start, end = taipei_day_to_utc_range(today)

    orders = (
        db.query(models.Order)
        .filter(models.Order.received_at >= start)
        .filter(models.Order.received_at < end)
        .filter(models.Order.deleted_at.is_(None))
        .order_by(models.Order.received_at.desc())
        .all()
    )

    # 優先讀 DB 設定的收件人
    recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
    if recipients_row and recipients_row.value:
        settings.EMAIL_RECIPIENTS = recipients_row.value

    fields_row = db.query(models.Setting).filter(models.Setting.key == "email_fields").first()
    fields = fields_row.value.split(",") if fields_row and fields_row.value else None

    if _dedupe_enabled(db):
        orders = dedupe_same_day_store_phone(orders)

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

    start_dt, _ = taipei_day_to_utc_range(start)
    _, end_dt = taipei_day_to_utc_range(end)

    orders = (
        db.query(models.Order)
        .filter(models.Order.received_at >= start_dt)
        .filter(models.Order.received_at < end_dt)
        .filter(models.Order.deleted_at.is_(None))
        .order_by(models.Order.received_at.desc())
        .all()
    )

    recipients_row = db.query(models.Setting).filter(models.Setting.key == "email_recipients").first()
    if recipients_row and recipients_row.value:
        settings.EMAIL_RECIPIENTS = recipients_row.value

    fields_row = db.query(models.Setting).filter(models.Setting.key == "email_fields").first()
    fields = fields_row.value.split(",") if fields_row and fields_row.value else None

    if _dedupe_enabled(db):
        orders = dedupe_same_day_store_phone(orders)

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
            "sent_at": r.sent_at.isoformat() + "Z" if r.sent_at else None,
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

    orders = (
        db.query(models.Order)
        .filter(models.Order.deleted_at.is_(None))
        .order_by(models.Order.received_at.desc())
        .limit(5)
        .all()
    )
    html = f"""
    <html><body style="font-family:'Helvetica Neue',Arial,'PingFang TC','Microsoft JhengHei',sans-serif;color:#1a1a1a;line-height:1.8;font-size:14px;max-width:640px;margin:0 auto;padding:24px;">
      <p>敬啟者 您好，</p>
      <p>此為 BOS-ETMALL 系統發送之測試信，用於確認郵件通道運作正常，
      目前系統最新訂單筆數為 <strong>{len(orders)}</strong> 筆。</p>
      <p>若您順利收到本封信件，代表 Email 設定已完成，毋需進行其他操作。</p>
      <p>順頌 商祺</p>
      <br>
      <p style="color:#273951;margin:0;">名留集團 ML Group</p>
      <hr style="border:none;border-top:1px solid #e5edf5;margin:20px 0 12px;">
      <p style="color:#94a3b8;font-size:12px;margin:0;">此郵件由 BOS-ETMALL 系統自動發送，請勿直接回覆本信件。</p>
    </body></html>
    """

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
