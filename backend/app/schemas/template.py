from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ChannelType(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"
    whatsapp = "whatsapp"


class TemplateBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Welcome Email EN"])
    channel: ChannelType
    language: str = Field("en", max_length=10)
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., examples=["Hello {{name}}, welcome to AudienceFlow!"])


class TemplateCreate(TemplateBase):
    pass


class TemplateRead(TemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
