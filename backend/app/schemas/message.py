from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    bounced = "bounced"


class MessageBase(BaseModel):
    campaign_id: int
    audience_member_id: int
    template_id: Optional[int] = None
    channel: str = Field(..., max_length=20, examples=["email"])
    status: MessageStatus = MessageStatus.pending


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
