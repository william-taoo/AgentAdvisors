"""Article schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    content: Optional[str] = None
    embedding_id: Optional[str] = None
    tickers: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleRead(ArticleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
