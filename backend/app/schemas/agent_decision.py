"""Agent decision schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AgentDecisionBase(BaseModel):
    ticker: str
    action: str  # Buy, Hold, Sell
    reasoning: Optional[str] = None
    signals: Optional[str] = None


class AgentDecisionCreate(AgentDecisionBase):
    pass


class AgentDecisionRead(AgentDecisionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
