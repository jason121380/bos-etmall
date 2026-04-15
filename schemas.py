from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OrderWebhook(BaseModel):
    """POS 系統送過來的 Webhook payload"""
    order_id: str
    store_id: str
    store_name: Optional[str] = None
    consumer_phone: str
    consumer_name: Optional[str] = None
    amount: float
    order_status: str          # "completed" / "paid" / "confirmed" 等
    order_time: datetime


class OrderOut(BaseModel):
    id: int
    order_id: str
    store_id: str
    store_name: Optional[str]
    consumer_phone: str
    consumer_name: Optional[str]
    amount: float
    order_status: str
    order_time: datetime
    received_at: datetime
    emailed: bool
    synced_to_sheet: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebhookResponse(BaseModel):
    status: str
    message: str
    order_id: Optional[str] = None
