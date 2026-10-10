from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=150, description="Email address or 10-digit mobile number")
    password: str = Field(..., min_length=4, max_length=128, description="Account password")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        s = v.strip() if isinstance(v, str) else ""
        if len(s) < 3:
            raise ValueError("Username/mobile number must be at least 3 characters long")
        return s

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("Password cannot be empty")
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters long")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    name: str
    email: Optional[EmailStr] = None
    role: str
