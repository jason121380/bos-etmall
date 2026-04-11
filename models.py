from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, func
from database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    sent_at = Column(DateTime, server_default=func.now())
    trigger = Column(String)        # "schedule" / "manual_today" / "manual_date" / "test"
    date_range = Column(String)     # e.g. "2026-04-10" or "2026-04-01 ~ 2026-04-10"
    order_count = Column(Integer)
    recipients = Column(Text)       # comma-separated
    status = Column(String)         # "ok" / "error"
    error = Column(Text, nullable=True)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)   # POS 訂單編號
    store_id = Column(String, index=True)                # 店家編號
    store_name = Column(String, nullable=True)           # 店家名稱
    consumer_phone = Column(String, index=True)          # 消費者手機
    consumer_name = Column(String, nullable=True)        # 消費者姓名
    amount = Column(Float)                               # 消費金額
    order_status = Column(String)                        # 訂單狀態
    order_time = Column(DateTime)                        # 訂單時間
    received_at = Column(DateTime, server_default=func.now())  # 接收時間
    emailed = Column(Boolean, default=False)             # 是否已發過 email
    synced_to_sheet = Column(Boolean, default=False)     # 是否已同步 Google Sheet
