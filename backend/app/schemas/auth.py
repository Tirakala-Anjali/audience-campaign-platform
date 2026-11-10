"""
Pydantic schemas for authentication endpoints.
"""
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# ── Validators ────────────────────────────────────────────────────────────────

PASSWORD_RE = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
)
PHONE_RE = re.compile(r'^\+?[0-9\s\-().]{7,20}$')


def _validate_password_strength(value: str) -> str:
    if not PASSWORD_RE.match(value):
        raise ValueError(
            "Password must contain at least 8 characters, one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )
    return value


# ── Register ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    phone: str = Field(..., min_length=7, max_length=20, examples=["9876543210"])
    organization_name: str = Field(..., min_length=2, max_length=150,
                                   examples=["Example Organisation"])
    password: str = Field(..., min_length=8, examples=["StrongPass@1"])
    role: str = Field(..., min_length=1, max_length=50, examples=["Campaign Manager"])

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Full name is required.")
        return v

    @field_validator("organization_name")
    @classmethod
    def org_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Organisation name is required.")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        v = v.strip()
        if not PHONE_RE.match(v):
            raise ValueError(
                "Phone number must be 7-20 digits and may include +, spaces, "
                "dashes, dots, or parentheses."
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)

    @field_validator("role")
    @classmethod
    def role_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Please select a role.")
        return v


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., min_length=1, examples=["StrongPass@1"])

    @field_validator("password")
    @classmethod
    def password_not_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("Password is required.")
        return v


class LoginResponse(BaseModel):
    message: str
    user: "UserResponse"
    access_token: str = ""
    token_type: str = "bearer"


# ── Shared response shapes ────────────────────────────────────────────────────

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    organization_name: Optional[str] = None
    role: Optional[str] = None          # role name — never the password hash

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


# Resolve forward ref
LoginResponse.model_rebuild()
