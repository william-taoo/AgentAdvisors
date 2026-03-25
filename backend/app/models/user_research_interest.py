"""User-scoped research targets used to drive ingestion relevance."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class UserResearchInterest(Base):
    __tablename__ = "user_research_interests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    ticker = Column(String(20), nullable=True, index=True)
    industry = Column(String(120), nullable=True, index=True)
    sector = Column(String(120), nullable=True, index=True)
    keyword = Column(String(255), nullable=True)
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
