import base64
import csv
import io
import requests
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from config import settings
import logging

MIN_DT = datetime.min.replace(tzinfo=timezone.utc)

logger = logging.getLogger(__name__)

TAIPEI_TZ = ZoneInfo("Asia/Taipei")

FIELD_LABELS = {
    "order_id":       "訂單編號",
    "store_name":     "店家名稱",
    "store_id":       "店家編號",
    "consumer_name":  "消費者姓名",
    "consumer_phone": "消費者手機",
    "amount":         "消費金額",
    "order_status":   "訂單狀態",
    "order_time":     "訂單時間",
    "received_at":    "接收時間",
}

DEFAULT_FIELDS = ["store_name", "consumer_phone", "received_at"]


def _to_taipei(dt):
    """將資料庫中 naive UTC datetime 轉為台北時區。"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TAIPEI_TZ)


def _mask_phone(phone: str) -> str:
    """0912345678 → 0912***678"""
    if not phone or len(phone) < 7:
        return phone or ""
    return phone[:4] + "***" + phone[-3:]


def get_field_value(order, field: str, mask: bool = True) -> str:
    if field == "amount":
        return f"NT$ {order.amount:,.0f}"
    if field == "order_time" and order.order_time:
        return _to_taipei(order.order_time).strftime("%Y-%m-%d %H:%M")
    if field == "received_at" and order.received_at:
        return _to_taipei(order.received_at).strftime("%Y-%m-%d %H:%M")
    if field == "store_name":
        return order.store_name or order.store_id or ""
    if field == "consumer_phone" and mask:
        return _mask_phone(order.consumer_phone)
    return str(getattr(order, field, "") or "")


def dedupe_same_day_store_phone(orders: list) -> list:
    """同台北日、同 store_id、同 consumer_phone 的訂單只保留最早一筆。

    沒有 consumer_phone 的訂單一律保留（不視為重複）。回傳結果維持原本傳入的排序。
    """
    by_asc = sorted(orders, key=lambda o: _to_taipei(o.received_at) or MIN_DT)
    seen = set()
    keep_ids = set()
    for o in by_asc:
        phone = (o.consumer_phone or "").strip()
        if not phone:
            keep_ids.add(id(o))
            continue
        ref_dt = _to_taipei(o.received_at)
        day = ref_dt.date() if ref_dt else None
        key = (day, o.store_id or "", phone)
        if key in seen:
            continue
        seen.add(key)
        keep_ids.add(id(o))
    return [o for o in orders if id(o) in keep_ids]


def build_email_html(orders: list, report_date: date, fields: list = None) -> str:
    return f"""
    <html><body style="font-family:'Helvetica Neue',Arial,'PingFang TC','Microsoft JhengHei',sans-serif;color:#1a1a1a;line-height:1.8;font-size:14px;max-width:640px;margin:0 auto;padding:24px;">
      <p>敬啟者 您好，</p>
      <p>茲附上 <strong>{report_date.strftime('%Y/%m/%d')}</strong> 點數儲值名單，共計 <strong>{len(orders)}</strong> 筆，
      詳細內容請參照附件檔案，惠請查收。</p>
      <p>如有任何疑問，敬請隨時來信聯繫，謝謝您的協助。</p>
      <p>順頌 商祺</p>
      <br>
      <p style="color:#273951;margin:0;">名留集團 ML Group</p>
      <hr style="border:none;border-top:1px solid #e5edf5;margin:20px 0 12px;">
      <p style="color:#94a3b8;font-size:12px;margin:0;">此郵件由 BOS-ETMALL 系統自動發送，請勿直接回覆本信件。</p>
    </body></html>
    """


def build_csv_base64(orders: list, fields: list) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([FIELD_LABELS.get(f, f) for f in fields])
    for o in orders:
        writer.writerow([get_field_value(o, f, mask=False) for f in fields])
    # utf-8-sig adds BOM automatically for Excel compatibility
    content = buf.getvalue().encode("utf-8-sig")
    return base64.b64encode(content).decode("ascii")


def send_daily_report(orders: list, report_date: date, fields: list = None):
    recipients = settings.get_recipients()
    if not recipients:
        logger.warning("No email recipients configured")
        return

    if not orders:
        logger.info(f"No new orders for {report_date}, skipping email")
        return

    html_content = build_email_html(orders, report_date, fields)
    subject = f"{report_date.strftime('%Y/%m/%d')}，每日點數儲值名單 — 共 {len(orders)} 筆"

    csv_b64 = build_csv_base64(orders, fields or DEFAULT_FIELDS)
    filename = f"名留集團 ML Group_點數儲值名單_{report_date.strftime('%Y%m%d')}.csv"

    try:
        resp = requests.post(
            "https://api.zeabur.com/api/v1/zsend/emails",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.ZEABUR_EMAIL_API_KEY}",
            },
            json={
                "from": f"名留集團 ML Group <{settings.EMAIL_FROM}>",
                "to": recipients,
                "subject": subject,
                "html": html_content,
                "attachments": [
                    {
                        "filename": filename,
                        "content": csv_b64,
                        "content_type": "text/csv",
                    }
                ],
            },
            timeout=15,
        )
        resp.raise_for_status()
        logger.info(f"Daily report sent via Zeabur Email to {recipients} — {len(orders)} orders")
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        raise
