"""Price snapshot model — OHLCV market data from ingestion."""
from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
