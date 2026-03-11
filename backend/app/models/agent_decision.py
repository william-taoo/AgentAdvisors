"""Agent decision model — StrategyAgent output: Buy/Hold/Sell + reasoning."""
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # Buy, Hold, Sell
    reasoning = Column(Text, nullable=True)
    signals = Column(Text, nullable=True)  # JSON string of cited signals
    created_at = Column(DateTime(timezone=True), server_default=func.now())
