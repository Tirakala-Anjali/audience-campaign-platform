from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class CampaignStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"


class CampaignBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Summer Newsletter"])
    description: Optional[str] = None
    status: CampaignStatus = CampaignStatus.draft
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignRead(CampaignBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
