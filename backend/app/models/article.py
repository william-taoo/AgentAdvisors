"""Article model — ingested news with Pinecone embedding_id."""
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=True)
    source = Column(String(100), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    content = Column(Text, nullable=True)
    embedding_id = Column(String(100), nullable=True, index=True)  # Pinecone id
    tickers = Column(String(500), nullable=True)  # comma-separated or JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
