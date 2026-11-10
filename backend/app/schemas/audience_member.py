from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class AudienceMemberBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["John Smith"])
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    preferred_language: str = Field("en", max_length=10, examples=["en"])
    consent_status: bool = False


class AudienceMemberCreate(AudienceMemberBase):
    pass


class AudienceMemberRead(AudienceMemberBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
