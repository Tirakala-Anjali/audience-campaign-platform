from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DeliveryLogBase(BaseModel):
    message_id: int
    delivery_status: str = Field(..., max_length=20, examples=["delivered"])
    error_details: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class DeliveryLogCreate(DeliveryLogBase):
    pass


class DeliveryLogRead(DeliveryLogBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
