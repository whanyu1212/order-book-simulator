from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()


class DBTraderAccount(Base):
    __tablename__ = "trader_accounts"

    trader_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    balance = Column(Numeric(precision=20, scale=8), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trades = relationship("DBTrade", back_populates="trader")
    orders = relationship("DBOrder", back_populates="trader")


class DBTrade(Base):
    __tablename__ = "trades"

    trade_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trader_id = Column(String, ForeignKey("trader_accounts.trader_id"))
    order_id = Column(String, nullable=False)
    side = Column(String, nullable=False)  # 'BUY' or 'SELL'
    price = Column(Numeric(precision=20, scale=8), nullable=False)
    quantity = Column(Numeric(precision=20, scale=8), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="EXECUTED")  # EXECUTED, CANCELLED, FAILED
    fee = Column(Numeric(precision=20, scale=8), default=0)
    counter_party_id = Column(String, nullable=True)  # ID of the other trader

    # Relationships
    trader = relationship("DBTraderAccount", back_populates="trades")


class DBOrder(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True)
    trader_id = Column(String, ForeignKey("trader_accounts.trader_id"))
    side = Column(String, nullable=False)  # 'BUY' or 'SELL'
    price = Column(Numeric(precision=20, scale=8), nullable=False)
    quantity = Column(Numeric(precision=20, scale=8), nullable=False)
    remaining_quantity = Column(
        Numeric(precision=20, scale=8), nullable=False
    )  # For partial fills
    priority = Column(Numeric, nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE, FILLED, CANCELLED, REJECTED
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trader = relationship("DBTraderAccount", back_populates="orders")
