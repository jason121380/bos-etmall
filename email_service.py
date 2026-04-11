import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date, timedelta
from typing import List
from config import settings
import logging

logger = logging.getLogger(__name__)


def build_email_html(orders: list, report_date: date) -> str:
    rows = ""
    for o in orders:
        rows += f"""
        <tr>
            <td>{o.order_id}</td>
            <td>{o.store_name or o.store_id}</td>
            <td>{o.consumer_phone}</td>
            <td>{o.consumer_name or '-'}</td>
            <td>NT$ {o.amount:,.0f}</td>
            <td>{o.order_time.strftime('%Y-%m-%d %H:%M')}</td>
        </tr>"""

    return f"""
    <html><body>
    <h2>📊 每日消費名單報表 — {report_date.strftime('%Y/%m/%d')}</h2>
    <p>以下為昨日新增的符合條件名單（消費 ≥ NT$1,000，訂單已成立）：</p>
    <p>共 <strong>{len(orders)}</strong> 筆</p>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
        <thead style="background:#4a90e2;color:white;">
            <tr>
                <th>訂單編號</th><th>店家</th><th>手機</th><th>姓名</th>
                <th>金額</th><th>訂單時間</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <br><p style="color:gray;font-size:12px;">此郵件由系統自動發送</p>
    </body></html>
    """


def send_daily_report(orders: list, report_date: date):
    recipients = settings.get_recipients()
    if not recipients:
        logger.warning("No email recipients configured")
        return

    if not orders:
        logger.info(f"No new orders for {report_date}, skipping email")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 每日消費名單 {report_date.strftime('%Y/%m/%d')} — 共 {len(orders)} 筆"
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(recipients)

    html_content = build_email_html(orders, report_date)
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, recipients, msg.as_string())
        logger.info(f"Daily report sent to {recipients} — {len(orders)} orders")
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        raise
