"""
FinPilot AI – Portfolio Service
All business logic for portfolio and holding CRUD operations.
Routers stay thin; all computation lives here.
"""

import logging
import uuid
from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.portfolio import Holding, Portfolio
from app.schemas.portfolio import HoldingCreate, PortfolioCreate, PortfolioUpdate

logger = logging.getLogger(__name__)


def _portfolio_to_dict(p: Portfolio) -> dict:
    """Serializes a Portfolio ORM object to a response-ready dict."""
    holdings_out = [_holding_to_dict(h) for h in p.holdings]
    total_invested = sum(h["total_invested"] for h in holdings_out)
    total_value = sum(h["current_value"] for h in holdings_out)
    gain_loss = round(total_value - total_invested, 2)
    gain_loss_pct = round((gain_loss / total_invested) * 100, 2) if total_invested else 0.0

    return {
        "id": p.id,
        "user_id": p.user_id,
        "name": p.name,
        "description": p.description,
        "currency": p.currency,
        "holdings": holdings_out,
        "holdings_count": len(holdings_out),
        "total_invested": total_invested,
        "total_value": total_value,
        "total_gain_loss": gain_loss,
        "total_gain_loss_pct": gain_loss_pct,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


def _holding_to_dict(h: Holding) -> dict:
    """Serializes a Holding ORM object to a response-ready dict."""
    return {
        "id": h.id,
        "symbol": h.symbol,
        "exchange": h.exchange,
        "company_name": h.company_name,
        "asset_type": h.asset_type,
        "quantity": h.quantity,
        "average_buy_price": h.average_buy_price,
        "current_price": h.current_price,
        "current_value": h.current_value,
        "total_invested": h.total_invested,
        "gain_loss": h.gain_loss,
        "gain_loss_pct": h.gain_loss_pct,
        "added_at": h.added_at.isoformat(),
        "updated_at": h.updated_at.isoformat(),
    }


class PortfolioService:
    """Encapsulates all portfolio business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _get_portfolio(self, portfolio_id: str, user_id: str) -> Portfolio:
        """Fetch portfolio by ID, raise 404/403 as appropriate."""
        portfolio = await self.db.get(Portfolio, portfolio_id)
        if not portfolio:
            raise NotFoundException("Portfolio not found.")
        if portfolio.user_id != user_id:
            raise ForbiddenException("You do not have access to this portfolio.")
        return portfolio

    # ── Create Portfolio ──────────────────────────────────────────────────────

    async def create_portfolio(self, user_id: str, payload: PortfolioCreate) -> dict:
        """
        Creates a new portfolio for the user.

        Raises:
            BadRequestException: If user already has a portfolio with this name.
        """
        portfolio = Portfolio(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=payload.name.strip(),
            description=payload.description,
            currency=payload.currency.upper(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        try:
            self.db.add(portfolio)
            await self.db.flush()
        except IntegrityError:
            raise BadRequestException(
                f"You already have a portfolio named '{payload.name}'."
            )

        logger.info("Portfolio created: %s for user %s", portfolio.id, user_id)
        return {
            "portfolio": {
                "id": portfolio.id,
                "user_id": portfolio.user_id,
                "name": portfolio.name,
                "description": portfolio.description,
                "currency": portfolio.currency,
                "total_value": 0.0,
                "holdings_count": 0,
                "created_at": portfolio.created_at.isoformat(),
            }
        }

    # ── Get Portfolio ─────────────────────────────────────────────────────────

    async def get_portfolio(self, portfolio_id: str, user_id: str) -> dict:
        """Returns a portfolio with all its holdings and computed financials."""
        portfolio = await self._get_portfolio(portfolio_id, user_id)
        return {"portfolio": _portfolio_to_dict(portfolio)}

    # ── List Portfolios ───────────────────────────────────────────────────────

    async def list_portfolios(self, user_id: str) -> dict:
        """Returns all portfolios for the authenticated user."""
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.user_id == user_id)
        )
        portfolios = result.scalars().all()
        return {
            "portfolios": [_portfolio_to_dict(p) for p in portfolios],
            "total": len(portfolios),
        }

    # ── Update Portfolio (metadata + add holdings) ────────────────────────────

    async def update_portfolio(
        self, portfolio_id: str, user_id: str, payload: PortfolioUpdate
    ) -> dict:
        """
        Updates portfolio metadata and/or upserts holdings.
        Existing holdings with the same symbol+exchange are updated;
        new ones are inserted.
        """
        portfolio = await self._get_portfolio(portfolio_id, user_id)

        if payload.name is not None:
            portfolio.name = payload.name.strip()
        if payload.description is not None:
            portfolio.description = payload.description
        portfolio.updated_at = datetime.now(UTC)

        if payload.holdings:
            await self._upsert_holdings(portfolio, payload.holdings)

        await self.db.flush()
        data = _portfolio_to_dict(portfolio)
        logger.info("Portfolio updated: %s", portfolio_id)
        return {
            "portfolio": {
                "id": data["id"],
                "name": data["name"],
                "holdings_count": data["holdings_count"],
                "total_value": data["total_value"],
                "updated_at": data["updated_at"],
            }
        }

    async def _upsert_holdings(
        self, portfolio: Portfolio, new_holdings: list[HoldingCreate]
    ) -> None:
        """Upsert a list of holdings into the portfolio."""
        # Build a lookup: (symbol.upper, exchange.upper) -> existing Holding
        existing: dict[tuple[str, str], Holding] = {
            (h.symbol.upper(), h.exchange.upper()): h for h in portfolio.holdings
        }

        for h_data in new_holdings:
            key = (h_data.symbol.upper(), h_data.exchange.upper())
            if key in existing:
                holding = existing[key]
                holding.quantity = h_data.quantity
                holding.average_buy_price = h_data.average_buy_price
                holding.asset_type = h_data.asset_type
                holding.company_name = h_data.company_name
                holding.updated_at = datetime.now(UTC)
            else:
                holding = Holding(
                    id=str(uuid.uuid4()),
                    portfolio_id=portfolio.id,
                    symbol=h_data.symbol.upper(),
                    exchange=h_data.exchange.upper(),
                    company_name=h_data.company_name,
                    quantity=h_data.quantity,
                    average_buy_price=h_data.average_buy_price,
                    asset_type=h_data.asset_type,
                    current_price=h_data.average_buy_price,  # seed with buy price
                    added_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                self.db.add(holding)
                portfolio.holdings.append(holding)

    # ── Delete Holding ────────────────────────────────────────────────────────

    async def delete_holding(
        self, portfolio_id: str, holding_id: str, user_id: str
    ) -> dict:
        """
        Removes a single holding from a portfolio.

        Raises:
            NotFoundException: If portfolio or holding is not found.
            ForbiddenException: If the portfolio belongs to another user.
        """
        portfolio = await self._get_portfolio(portfolio_id, user_id)

        holding = next((h for h in portfolio.holdings if h.id == holding_id), None)
        if not holding:
            raise NotFoundException("Holding not found in this portfolio.")

        await self.db.delete(holding)
        await self.db.flush()

        # Re-compute remaining value
        remaining = [h for h in portfolio.holdings if h.id != holding_id]
        updated_value = sum(h.current_value for h in remaining)

        logger.info("Holding %s deleted from portfolio %s", holding_id, portfolio_id)
        return {
            "deleted_holding_id": holding_id,
            "portfolio_id": portfolio_id,
            "remaining_holdings": len(remaining),
            "updated_total_value": round(updated_value, 2),
        }

    # ── Portfolio Summary ─────────────────────────────────────────────────────

    async def get_summary(
        self, portfolio_id: str, user_id: str, period: str
    ) -> dict:
        """
        Computes a high-level analytical summary of the portfolio.
        Covers asset allocation, top/bottom performers, and basic risk indicators.
        """
        valid_periods = {"1W", "1M", "3M", "6M", "1Y", "ALL"}
        if period not in valid_periods:
            raise BadRequestException(
                f"Invalid period '{period}'. Choose from: {', '.join(sorted(valid_periods))}"
            )

        portfolio = await self._get_portfolio(portfolio_id, user_id)
        holdings = portfolio.holdings

        total_invested = sum(h.total_invested for h in holdings)
        total_value = sum(h.current_value for h in holdings)
        gain_loss = round(total_value - total_invested, 2)
        gain_loss_pct = round((gain_loss / total_invested) * 100, 2) if total_invested else 0.0

        # Asset allocation by type (% of total_value)
        allocation: dict[str, float] = defaultdict(float)
        for h in holdings:
            allocation[h.asset_type] += h.current_value
        asset_allocation = {
            k: round((v / total_value) * 100, 2) if total_value else 0.0
            for k, v in allocation.items()
        }

        # Sort performers
        sorted_holdings = sorted(holdings, key=lambda h: h.gain_loss_pct, reverse=True)
        top_performers = [
            {"symbol": h.symbol, "gain_pct": h.gain_loss_pct}
            for h in sorted_holdings[:3]
            if h.gain_loss_pct > 0
        ]
        bottom_performers = [
            {"symbol": h.symbol, "gain_pct": h.gain_loss_pct}
            for h in reversed(sorted_holdings)
            if h.gain_loss_pct < 0
        ][:3]

        # Simple risk score (0–10) based on # of unique symbols and asset types
        num_holdings = len(holdings)
        unique_types = len({h.asset_type for h in holdings})
        diversification_score = min(10.0, round((num_holdings / 10) * 10, 1))
        risk_score = round(10 - diversification_score + (1 if unique_types == 1 else 0), 1)

        return {
            "summary": {
                "portfolio_id": portfolio_id,
                "total_value": round(total_value, 2),
                "total_invested": round(total_invested, 2),
                "total_gain_loss": gain_loss,
                "total_gain_loss_pct": gain_loss_pct,
                "period_return_pct": gain_loss_pct,  # simplified; real impl needs price history
                "asset_allocation": asset_allocation,
                "top_performers": top_performers,
                "bottom_performers": bottom_performers,
                "risk_score": risk_score,
                "diversification_score": diversification_score,
                "period": period,
            }
        }
