"""
FinPilot AI – Authentication Service
Contains all business logic for user registration, login,
and token management. Routes delegate here; services call the DB.
"""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.exceptions.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """
    Encapsulates all authentication operations.
    Each method maps directly to one API endpoint.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Register ──────────────────────────────────────────────────────────────

    async def register(self, payload: UserCreate) -> dict:
        """
        Creates a new user account.

        Raises:
            BadRequestException: If the email is already registered.
        """
        # Check for existing email
        existing = await self.db.scalar(
            select(User).where(User.email == payload.email.lower())
        )
        if existing:
            raise BadRequestException(
                "An account with this email already exists."
            )

        user = User(
            id=str(uuid.uuid4()),
            full_name=payload.full_name.strip(),
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            is_active=True,
            is_verified=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        try:
            self.db.add(user)
            await self.db.flush()          # Get DB-generated defaults if any
        except IntegrityError:
            raise BadRequestException(
                "An account with this email already exists."
            )

        logger.info("New user registered: %s", user.email)
        return {
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
            }
        }

    # ── Login ─────────────────────────────────────────────────────────────────

    async def login(self, payload: UserLogin) -> dict:
        """
        Authenticates a user and issues JWT access + refresh tokens.

        Raises:
            UnauthorizedException: If credentials are invalid or account is inactive.
        """
        user = await self.db.scalar(
            select(User).where(User.email == payload.email.lower())
        )

        if not user or not verify_password(payload.password, user.password_hash):
            # Deliberately vague error to prevent email enumeration
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("This account has been deactivated.")

        access_token = create_access_token(user_id=user.id)
        refresh_token = create_refresh_token(user_id=user.id)

        logger.info("User logged in: %s", user.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "is_verified": user.is_verified,
            },
        }

    # ── Refresh Token ─────────────────────────────────────────────────────────

    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Validates a refresh token and issues a new access token.

        Raises:
            UnauthorizedException: If token is invalid, expired, or user not found.

        Note:
            In production, implement a token blacklist (e.g. Redis) to prevent
            refresh token reuse after logout.
        """
        from jwt.exceptions import InvalidTokenError

        try:
            payload = decode_refresh_token(refresh_token)
        except InvalidTokenError as exc:
            raise UnauthorizedException(f"Invalid or expired refresh token: {exc}")

        user_id: str = payload.get("sub", "")
        user = await self.db.get(User, user_id)

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or account is inactive.")

        new_access_token = create_access_token(user_id=user.id)
        logger.info("Access token refreshed for user: %s", user.email)

        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    # ── Get User by ID ────────────────────────────────────────────────────────

    async def get_user_by_id(self, user_id: str) -> User:
        """
        Fetches a user by primary key.

        Raises:
            NotFoundException: If the user does not exist.
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundException("User not found.")
        return user
