from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FeedbackBase(BaseModel):
    audience_member_id: int
    campaign_id: int
    rating: int = Field(..., ge=1, le=5, examples=[4])
    comments: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackRead(FeedbackBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
