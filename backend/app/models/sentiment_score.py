"""Sentiment score model — NewsAgent output and stored sentiment per ticker."""
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    score = Column(Float, nullable=False)  # -1.0 to 1.0
    source = Column(String(50), nullable=True)  # e.g. "news", "analyst"
    summary = Column(String(2000), nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
