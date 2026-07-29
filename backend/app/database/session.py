"""
FinPilot AI – Async Database Session Management
Configures the SQLAlchemy async engine and session factory.
Provides a FastAPI dependency for injecting database sessions.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Engine ─────────────────────────────────────────────────────────────────────

def _build_engine() -> AsyncEngine:
    """Creates the SQLAlchemy async engine from the DATABASE_URL setting."""
    kwargs: dict = {
        "echo": settings.DEBUG,          # Log SQL statements in dev mode
        "future": True,                  # SQLAlchemy 2.x style
    }

    # SQLite requires check_same_thread=False
    if settings.is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}

    return create_async_engine(settings.DATABASE_URL, **kwargs)


engine: AsyncEngine = _build_engine()

# ── Session Factory ────────────────────────────────────────────────────────────

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy-load errors after commit
    autocommit=False,
    autoflush=False,
)


# ── FastAPI Dependency ────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session per request.
    The session is automatically committed on success and rolled back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
