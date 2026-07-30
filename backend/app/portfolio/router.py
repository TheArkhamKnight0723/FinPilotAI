"""
FinPilot AI – Portfolio Router
Endpoints under /api/v1/portfolios (all JWT-protected):

  POST   /                           Create a portfolio
  GET    /                           List all user portfolios
  GET    /{portfolio_id}             Get a portfolio with holdings
  PATCH  /{portfolio_id}             Update portfolio / add holdings
  DELETE /{portfolio_id}/holdings/{holding_id}   Remove a holding
  GET    /{portfolio_id}/summary     Analytical summary
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.portfolio.service import PortfolioService
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolios", tags=["Portfolio"])


def _meta() -> dict:
    return {"timestamp": datetime.now(UTC).isoformat()}


# ── POST / ────────────────────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a portfolio")
async def create_portfolio(
    payload: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Creates a new named portfolio for the authenticated user."""
    service = PortfolioService(db)
    data = await service.create_portfolio(current_user.id, payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"success": True, "message": "Portfolio created successfully.", "data": data, "meta": _meta()},
    )


# ── GET / ─────────────────────────────────────────────────────────────────────

@router.get("/", status_code=status.HTTP_200_OK, summary="List all portfolios")
async def list_portfolios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Returns all portfolios belonging to the authenticated user."""
    service = PortfolioService(db)
    data = await service.list_portfolios(current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Portfolios retrieved.", "data": data, "meta": _meta()},
    )


# ── GET /{portfolio_id} ───────────────────────────────────────────────────────

@router.get("/{portfolio_id}", status_code=status.HTTP_200_OK, summary="Get a portfolio")
async def get_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Returns the portfolio and all its holdings with computed P&L."""
    service = PortfolioService(db)
    data = await service.get_portfolio(portfolio_id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Portfolio retrieved.", "data": data, "meta": _meta()},
    )


# ── PATCH /{portfolio_id} ─────────────────────────────────────────────────────

@router.patch("/{portfolio_id}", status_code=status.HTTP_200_OK, summary="Update portfolio")
async def update_portfolio(
    portfolio_id: str,
    payload: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Updates portfolio metadata and/or upserts holdings."""
    service = PortfolioService(db)
    data = await service.update_portfolio(portfolio_id, current_user.id, payload)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Portfolio updated successfully.", "data": data, "meta": _meta()},
    )


# ── DELETE /{portfolio_id}/holdings/{holding_id} ─────────────────────────────

@router.delete(
    "/{portfolio_id}/holdings/{holding_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a holding",
)
async def delete_holding(
    portfolio_id: str,
    holding_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Removes a specific holding from a portfolio."""
    service = PortfolioService(db)
    data = await service.delete_holding(portfolio_id, holding_id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Holding removed from portfolio.", "data": data, "meta": _meta()},
    )


# ── GET /{portfolio_id}/summary ───────────────────────────────────────────────

@router.get(
    "/{portfolio_id}/summary",
    status_code=status.HTTP_200_OK,
    summary="Get portfolio summary",
)
async def get_summary(
    portfolio_id: str,
    period: str = Query(default="1M", description="Period: 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Returns analytical summary including P&L, allocation, and performer rankings."""
    service = PortfolioService(db)
    data = await service.get_summary(portfolio_id, current_user.id, period)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Portfolio summary retrieved.", "data": data, "meta": _meta()},
    )
