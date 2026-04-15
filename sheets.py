import json
import gspread
from google.oauth2.service_account import Credentials
from config import settings
import logging

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_HEADERS = [
    "訂單編號", "店家ID", "店家名稱", "消費者手機", "消費者姓名",
    "消費金額", "訂單狀態", "訂單時間", "接收時間"
]


def get_sheet():
    creds_dict = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1
    return sheet


def ensure_headers(sheet):
    first_row = sheet.row_values(1)
    if first_row != SHEET_HEADERS:
        sheet.insert_row(SHEET_HEADERS, index=1)


def sync_order_to_sheet(order) -> bool:
    try:
        sheet = get_sheet()
        ensure_headers(sheet)
        row = [
            order.order_id,
            order.store_id,
            order.store_name or "",
            order.consumer_phone,
            order.consumer_name or "",
            order.amount,
            order.order_status,
            order.order_time.strftime("%Y-%m-%d %H:%M:%S"),
            order.received_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        logger.error(f"Google Sheets sync failed: {e}")
        return False


def mark_order_deleted_in_sheet(order_id: str) -> bool:
    """
    將 Google Sheet 中對應 order_id 的列「訂單狀態」欄位標記為「已刪除」，
    不會真的刪除列。若找不到訂單編號則回傳 False。
    """
    try:
        sheet = get_sheet()
        # 訂單編號在第 1 欄
        cell = sheet.find(order_id, in_column=1)
        if not cell:
            logger.warning(f"Order {order_id} not found in sheet")
            return False
        # 訂單狀態在第 7 欄（見 SHEET_HEADERS）
        sheet.update_cell(cell.row, 7, "已刪除")
        return True
    except Exception as e:
        logger.error(f"Google Sheets mark deleted failed for {order_id}: {e}")
        return False
