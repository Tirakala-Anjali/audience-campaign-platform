from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Jane Doe"])
    email: EmailStr
    role_id: Optional[int] = None


class UserCreate(UserBase):
    # Raw password — hashing happens in the service layer
    password: str = Field(..., min_length=8, examples=["SecurePass123!"])


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
