from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SegmentBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["English Speakers"])
    description: Optional[str] = Field(None, max_length=500)
    filter_criteria: Optional[Dict[str, Any]] = Field(
        None, examples=[{"language": "en", "consent_status": True}]
    )


class SegmentCreate(SegmentBase):
    pass


class SegmentRead(SegmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
