"""Price snapshot schemas."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class PriceSnapshotBase(BaseModel):
    ticker: str
    date: date
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    volume: Optional[int] = None


class PriceSnapshotCreate(PriceSnapshotBase):
    pass


class PriceSnapshotRead(PriceSnapshotBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
