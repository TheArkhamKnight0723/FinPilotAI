"""
FinPilot AI – SQLAlchemy Declarative Base
All ORM models must inherit from this Base so Alembic can
discover them for migration generation.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Root declarative base for all SQLAlchemy models."""
    pass
