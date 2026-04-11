import requests
from datetime import date
from config import settings
import logging

logger = logging.getLogger(__name__)

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

DEFAULT_FIELDS = ["order_id", "store_name", "consumer_name", "consumer_phone", "amount", "order_status", "order_time"]


def get_field_value(order, field: str) -> str:
    if field == "amount":
        return f"NT$ {order.amount:,.0f}"
    if field == "order_time" and order.order_time:
        return order.order_time.strftime("%Y-%m-%d %H:%M")
    if field == "received_at" and order.received_at:
        return order.received_at.strftime("%Y-%m-%d %H:%M")
    if field == "store_name":
        return order.store_name or order.store_id or ""
    return str(getattr(order, field, "") or "")


def build_email_html(orders: list, report_date: date, fields: list = None) -> str:
    if not fields:
        fields = DEFAULT_FIELDS

    headers = "".join(f"<th>{FIELD_LABELS.get(f, f)}</th>" for f in fields)
    rows = ""
    for o in orders:
        cells = "".join(f"<td>{get_field_value(o, f)}</td>" for f in fields)
        rows += f"<tr>{cells}</tr>"

    return f"""
    <html><body style="font-family:sans-serif;">
    <h2 style="color:#061b31;">每日消費名單報表 — {report_date.strftime('%Y/%m/%d')}</h2>
    <p style="color:#64748d;">共 <strong>{len(orders)}</strong> 筆訂單</p>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;margin-top:12px;">
        <thead style="background:#533afd;color:white;">
            <tr>{headers}</tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <br><p style="color:#94a3b8;font-size:12px;">此郵件由 BOS-ETMALL 系統自動發送</p>
    </body></html>
    """


def send_daily_report(orders: list, report_date: date, fields: list = None):
    recipients = settings.get_recipients()
    if not recipients:
        logger.warning("No email recipients configured")
        return

    if not orders:
        logger.info(f"No new orders for {report_date}, skipping email")
        return

    html_content = build_email_html(orders, report_date, fields)
    subject = f"每日消費名單 {report_date.strftime('%Y/%m/%d')} — 共 {len(orders)} 筆"

    try:
        resp = requests.post(
            "https://api.zeabur.com/api/v1/zsend/emails",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.ZEABUR_EMAIL_API_KEY}",
            },
            json={
                "from": settings.EMAIL_FROM,
                "to": recipients,
                "subject": subject,
                "html": html_content,
            },
            timeout=15,
        )
        resp.raise_for_status()
        logger.info(f"Daily report sent via Zeabur Email to {recipients} — {len(orders)} orders")
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        raise
