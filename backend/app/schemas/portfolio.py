"""
FinPilot AI – Portfolio Pydantic Schemas
Request/response contracts for all portfolio-related API operations.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Asset Types ───────────────────────────────────────────────────────────────

VALID_ASSET_TYPES = Literal["equity", "mutual_fund", "etf", "crypto", "bond"]
VALID_PERIODS = Literal["1W", "1M", "3M", "6M", "1Y", "ALL"]


# ── Request Schemas ───────────────────────────────────────────────────────────

class PortfolioCreate(BaseModel):
    """Payload for POST /api/v1/portfolios"""
    name: str = Field(..., min_length=2, max_length=100, examples=["My Growth Portfolio"])
    description: str | None = Field(None, max_length=500)
    currency: str = Field("INR", max_length=10, examples=["INR"])


class HoldingCreate(BaseModel):
    """Schema for a single holding entry (used inside PortfolioUpdate)."""
    symbol: str = Field(..., min_length=1, max_length=20, examples=["TCS"])
    exchange: str = Field("NSE", max_length=20, examples=["NSE"])
    company_name: str = Field("", max_length=200)
    quantity: float = Field(..., gt=0, description="Number of units held")
    average_buy_price: float = Field(..., gt=0, description="Cost basis per unit")
    asset_type: VALID_ASSET_TYPES = Field("equity")  # type: ignore[assignment]


class PortfolioUpdate(BaseModel):
    """Payload for PATCH /api/v1/portfolios/{id} — all fields optional."""
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)
    holdings: list[HoldingCreate] | None = None


# ── Response Schemas ──────────────────────────────────────────────────────────

class HoldingOut(BaseModel):
    """Serialized holding returned in API responses."""
    model_config = {"from_attributes": True}

    id: str
    symbol: str
    exchange: str
    company_name: str
    asset_type: str
    quantity: float
    average_buy_price: float
    current_price: float
    current_value: float
    total_invested: float
    gain_loss: float
    gain_loss_pct: float
    added_at: datetime
    updated_at: datetime


class PortfolioOut(BaseModel):
    """Serialized portfolio returned in API responses."""
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    name: str
    description: str | None
    currency: str
    holdings: list[HoldingOut]
    holdings_count: int
    total_invested: float
    total_value: float
    total_gain_loss: float
    total_gain_loss_pct: float
    created_at: datetime
    updated_at: datetime
