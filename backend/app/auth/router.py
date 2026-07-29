"""
FinPilot AI – Authentication Router
Exposes the following endpoints under /api/v1/auth:

  POST   /register       Create a new account
  POST   /login          Authenticate and receive JWT tokens
  POST   /logout         Revoke current session (stateless / blacklist-ready)
  POST   /refresh        Exchange refresh token for a new access token
  GET    /me             Return the currently authenticated user
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.service import AuthService
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    LogoutRequest,
    TokenRefreshRequest,
    UserCreate,
    UserLogin,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _meta() -> dict:
    return {"timestamp": datetime.now(UTC).isoformat()}


# ── POST /register ────────────────────────────────────────────────────────────

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Creates a new user account.

    - Validates email uniqueness
    - Hashes password with bcrypt
    - Returns the created user (no password hash exposed)
    """
    service = AuthService(db)
    data = await service.register(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Account created successfully. Please verify your email.",
            "data": data,
            "meta": _meta(),
        },
    )


# ── POST /login ───────────────────────────────────────────────────────────────

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT tokens",
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Authenticates a user with email/password.
    Returns a JWT access token and refresh token on success.
    """
    service = AuthService(db)
    data = await service.login(payload)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Login successful.",
            "data": data,
            "meta": _meta(),
        },
    )


# ── POST /logout ──────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout and revoke current session",
)
async def logout(
    payload: LogoutRequest,
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """
    Stateless logout endpoint.

    The client MUST delete both tokens from storage.

    Production note: To prevent refresh token reuse after logout,
    store the token's `jti` claim in a Redis blacklist and check
    it in `decode_refresh_token()`. This endpoint is designed to
    be extended with that pattern without breaking the contract.
    """
    logger.info("User logged out: %s", current_user.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Logged out successfully. Please delete your tokens.",
            "data": None,
            "meta": _meta(),
        },
    )


# ── POST /refresh ─────────────────────────────────────────────────────────────

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Exchange refresh token for a new access token",
)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Validates the provided refresh token and issues a fresh access token.
    Does NOT require an Authorization header — uses the refresh token itself.
    """
    service = AuthService(db)
    data = await service.refresh_token(payload.refresh_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Token refreshed successfully.",
            "data": data,
            "meta": _meta(),
        },
    )


# ── GET /me ───────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get the currently authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """
    Returns the profile of the currently authenticated user.
    Requires a valid Bearer access token in the Authorization header.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Current user retrieved.",
            "data": {
                "user": {
                    "id": current_user.id,
                    "full_name": current_user.full_name,
                    "email": current_user.email,
                    "risk_profile": current_user.risk_profile,
                    "is_active": current_user.is_active,
                    "is_verified": current_user.is_verified,
                    "created_at": current_user.created_at.isoformat(),
                    "updated_at": current_user.updated_at.isoformat(),
                }
            },
            "meta": _meta(),
        },
    )
