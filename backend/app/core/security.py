"""
FinPilot AI – Security Utilities
Handles password hashing (bcrypt direct) and JWT token
creation / verification (PyJWT).
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Returns a bcrypt hash of the plain-text password.
    Uses bcrypt directly (compatible with bcrypt>=4.0).
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ── JWT Token Helpers ─────────────────────────────────────────────────────────

def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Internal helper that builds and signs a JWT.

    Args:
        subject:       The JWT 'sub' claim — typically the user ID.
        token_type:    Either "access" or "refresh".
        expires_delta: How long until the token expires.
        extra_claims:  Any additional claims to embed.

    Returns:
        A signed JWT string.
    """
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    """Creates a short-lived JWT access token."""
    return _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    """Creates a long-lived JWT refresh token."""
    return _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodes and validates a JWT token.

    Raises:
        ExpiredSignatureError: Token has expired.
        DecodeError:           Token is malformed.
        InvalidTokenError:     Any other JWT validation failure.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodes a token and asserts it is of type 'access'.

    Raises:
        InvalidTokenError: If the token is not an access token.
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise InvalidTokenError("Token is not an access token.")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """
    Decodes a token and asserts it is of type 'refresh'.

    Raises:
        InvalidTokenError: If the token is not a refresh token.
    """
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Token is not a refresh token.")
    return payload
