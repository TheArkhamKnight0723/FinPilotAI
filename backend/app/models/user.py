"""
FinPilot AI – User ORM Model
Represents the `users` table in the database.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RiskProfile(str, Enum):
    """Investment risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class User(Base):
    """
    Stores registered user accounts.

    Columns
    -------
    id              : UUID primary key (auto-generated)
    full_name       : User's display name
    email           : Unique email address (login identifier)
    password_hash   : bcrypt hash — plain-text password is NEVER stored
    risk_profile    : Investment risk tolerance (conservative/moderate/aggressive)
    is_active       : False = soft-deleted / suspended
    is_verified     : True once the user has verified their email
    created_at      : Row creation timestamp (UTC)
    updated_at      : Last modification timestamp (UTC)
    """

    __tablename__ = "users"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # ── Profile ───────────────────────────────────────────────────────────────
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # ── Preferences ───────────────────────────────────────────────────────────
    risk_profile: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RiskProfile.MODERATE.value,
        server_default=RiskProfile.MODERATE.value,
    )

    # ── Status Flags ─────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("1")
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r} active={self.is_active}>"
