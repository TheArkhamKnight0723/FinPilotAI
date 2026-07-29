"""
FinPilot AI – Authentication Dependencies
FastAPI dependency functions for protecting routes with JWT verification.
Inject `CurrentUser` into any route handler to require authentication.
"""

import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import get_db
from app.exceptions.exceptions import UnauthorizedException
from app.models.user import User

logger = logging.getLogger(__name__)

# ── HTTP Bearer Extractor ─────────────────────────────────────────────────────
# auto_error=False lets us return a clean 401 instead of FastAPI's 403 default.
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts and validates the Bearer JWT from the Authorization header.
    Returns the authenticated User ORM instance.

    Raises:
        UnauthorizedException: If the token is missing, malformed, expired,
                               or the user no longer exists / is inactive.

    Usage::

        @router.get("/protected")
        async def protected(user: User = Depends(get_current_user)):
            return {"hello": user.email}
    """
    if credentials is None:
        raise UnauthorizedException(
            "Authentication required. Provide a Bearer token."
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise UnauthorizedException(f"Invalid or expired token: {exc}")

    user_id: str = payload.get("sub", "")
    if not user_id:
        raise UnauthorizedException("Token payload is missing subject claim.")

    user = await db.get(User, user_id)
    if not user:
        raise UnauthorizedException("User associated with this token no longer exists.")
    if not user.is_active:
        raise UnauthorizedException("This account has been deactivated.")

    return user


# ── Type alias for cleaner route signatures ───────────────────────────────────
CurrentUser = Depends(get_current_user)
