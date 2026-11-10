"""Pydantic schemas for Campaign endpoints — full spec fields."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CampaignStatus(str, Enum):
    draft     = "draft"
    active    = "active"
    paused    = "paused"
    completed = "completed"
    cancelled = "cancelled"


class CampaignPriority(str, Enum):
    low       = "low"
    medium    = "medium"
    high      = "high"
    emergency = "emergency"


class CampaignCreate(BaseModel):
    name:          str                        = Field(..., min_length=2, max_length=100)
    description:   Optional[str]             = Field(None, max_length=1000)
    campaign_type: Optional[str]             = Field(None, max_length=50)
    objective:     Optional[str]             = Field(None, max_length=255)
    channels:      Optional[List[str]]       = None   # ["email","sms","whatsapp","push"]
    status:        CampaignStatus            = CampaignStatus.draft
    priority:      CampaignPriority          = CampaignPriority.medium
    start_at:      Optional[datetime]        = None
    end_at:        Optional[datetime]        = None


class CampaignUpdate(BaseModel):
    name:          Optional[str]             = Field(None, min_length=2, max_length=100)
    description:   Optional[str]            = Field(None, max_length=1000)
    campaign_type: Optional[str]            = Field(None, max_length=50)
    objective:     Optional[str]            = Field(None, max_length=255)
    channels:      Optional[List[str]]      = None
    status:        Optional[CampaignStatus] = None
    priority:      Optional[CampaignPriority] = None
    start_at:      Optional[datetime]       = None
    end_at:        Optional[datetime]       = None


class CampaignRead(BaseModel):
    id:            int
    name:          str
    description:   Optional[str]
    campaign_type: Optional[str]
    objective:     Optional[str]
    channels:      Optional[List[str]]
    status:        str
    priority:      str
    start_at:      Optional[datetime]
    end_at:        Optional[datetime]
    creator_id:    Optional[int]
    created_at:    datetime
    updated_at:    Optional[datetime]

    model_config = {"from_attributes": True}
