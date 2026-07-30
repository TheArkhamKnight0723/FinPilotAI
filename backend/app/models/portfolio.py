"""
FinPilot AI – Portfolio & Holding ORM Models
Tables: portfolios, holdings, transactions
"""

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AssetType(str, Enum):
    """Supported asset types for a holding."""
    EQUITY = "equity"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    CRYPTO = "crypto"
    BOND = "bond"


class Portfolio(Base):
    """
    Represents a named investment portfolio owned by a user.

    Columns
    -------
    id          : UUID primary key
    user_id     : FK to users.id (owner)
    name        : Display name (unique per user)
    description : Optional free-text description
    currency    : ISO 4217 currency code (default INR)
    created_at  : UTC creation timestamp
    updated_at  : UTC last-modified timestamp
    """

    __tablename__ = "portfolios"

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_portfolio_user_name"),
        Index("ix_portfolios_user_id", "user_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR", server_default="INR")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    holdings: Mapped[list["Holding"]] = relationship(
        "Holding", back_populates="portfolio", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Portfolio id={self.id!r} name={self.name!r} user={self.user_id!r}>"


class Holding(Base):
    """
    Represents a single stock/asset position within a portfolio.

    Columns
    -------
    id                : UUID primary key
    portfolio_id      : FK to portfolios.id
    symbol            : Ticker symbol (e.g. RELIANCE, TCS)
    exchange          : Exchange name (NSE, BSE, NASDAQ, etc.)
    company_name      : Human-readable company name
    asset_type        : Type of asset (equity, etf, etc.)
    quantity          : Number of units held
    average_buy_price : Cost basis per unit
    current_price     : Latest market price (updated externally)
    added_at          : When the holding was first added
    updated_at        : Last update timestamp
    """

    __tablename__ = "holdings"

    __table_args__ = (
        Index("ix_holdings_portfolio_id", "portfolio_id"),
        Index("ix_holdings_symbol", "symbol"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False, default="NSE", server_default="NSE")
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, default="", server_default="")
    asset_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AssetType.EQUITY.value, server_default=AssetType.EQUITY.value
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    average_buy_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="holdings")

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def total_invested(self) -> float:
        return round(self.quantity * self.average_buy_price, 2)

    @property
    def current_value(self) -> float:
        price = self.current_price if self.current_price > 0 else self.average_buy_price
        return round(self.quantity * price, 2)

    @property
    def gain_loss(self) -> float:
        return round(self.current_value - self.total_invested, 2)

    @property
    def gain_loss_pct(self) -> float:
        if self.total_invested == 0:
            return 0.0
        return round((self.gain_loss / self.total_invested) * 100, 2)

    def __repr__(self) -> str:
        return f"<Holding id={self.id!r} symbol={self.symbol!r} qty={self.quantity}>"
