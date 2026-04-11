from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, func
from database import Base


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
