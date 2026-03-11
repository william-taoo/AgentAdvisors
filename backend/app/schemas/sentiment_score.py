"""Sentiment score schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SentimentScoreBase(BaseModel):
    ticker: str
    score: float  # -1.0 to 1.0
    source: Optional[str] = None
    summary: Optional[str] = None


class SentimentScoreCreate(SentimentScoreBase):
    pass


class SentimentScoreRead(SentimentScoreBase):
    id: int
    computed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
