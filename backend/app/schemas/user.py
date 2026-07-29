"""
FinPilot AI – User Pydantic Schemas
Defines request/response contracts for user-related API operations.
"""

import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Shared Base ───────────────────────────────────────────────────────────────

class _APIResponse(BaseModel):
    """Common envelope used across all response schemas."""
    success: bool
    message: str


# ── Request Schemas ───────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Payload for POST /api/v1/auth/register"""

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full display name",
        examples=["Aryan Sharma"],
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address (becomes the login identifier)",
        examples=["aryan@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Minimum 8 chars — must contain uppercase, digit, special char",
        examples=["SecurePass@123"],
    )
    confirm_password: str = Field(
        ...,
        description="Must exactly match the password field",
        examples=["SecurePass@123"],
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match.")
        return v


class UserLogin(BaseModel):
    """Payload for POST /api/v1/auth/login"""

    email: EmailStr = Field(..., examples=["aryan@example.com"])
    password: str = Field(..., examples=["SecurePass@123"])


class TokenRefreshRequest(BaseModel):
    """Payload for POST /api/v1/auth/refresh"""

    refresh_token: str = Field(..., description="A valid, unexpired refresh token")


class LogoutRequest(BaseModel):
    """Payload for POST /api/v1/auth/logout"""

    refresh_token: str = Field(..., description="Refresh token to revoke")


# ── Response Schemas ──────────────────────────────────────────────────────────

class UserPublic(BaseModel):
    """Serialized user data safe to return in API responses (no password hash)."""

    model_config = {"from_attributes": True}

    id: str
    full_name: str
    email: EmailStr
    risk_profile: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class TokenData(BaseModel):
    """Token payload returned on login / token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds until access token expires


class RegisterResponse(_APIResponse):
    """Response for POST /api/v1/auth/register"""

    data: dict


class LoginResponse(_APIResponse):
    """Response for POST /api/v1/auth/login"""

    data: dict


class TokenRefreshResponse(_APIResponse):
    """Response for POST /api/v1/auth/refresh"""

    data: dict


class MeResponse(_APIResponse):
    """Response for GET /api/v1/auth/me"""

    data: dict


class LogoutResponse(_APIResponse):
    """Response for POST /api/v1/auth/logout"""

    data: None = None
