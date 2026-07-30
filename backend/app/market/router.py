"""
FinPilot AI – Market Router
Endpoints under /api/v1/market (all JWT-protected):

  GET  /search               Search stocks by symbol / name
  GET  /stocks/{symbol}      Full stock details + price history
  GET  /overview             Index snapshot, gainers, losers
  GET  /trending             Trending stocks by exchange & category
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.market.providers.mock_provider import MockMarketProvider
from app.market.service import MarketService
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["Market"])


def _meta() -> dict:
    return {"timestamp": datetime.now(UTC).isoformat()}


def _get_market_service() -> MarketService:
    """
    FastAPI dependency that builds the MarketService with the configured provider.
    To swap providers, change MockMarketProvider -> YahooFinanceProvider here.
    Provider selection can also be driven by settings.MARKET_PROVIDER in future.
    """
    return MarketService(provider=MockMarketProvider())


# ── GET /search ───────────────────────────────────────────────────────────────

@router.get("/search", status_code=status.HTTP_200_OK, summary="Search stocks")
async def search_stocks(
    q: str = Query(..., min_length=2, description="Symbol or company name"),
    exchange: str | None = Query(None, description="NSE | BSE | NASDAQ | NYSE"),
    type: str | None = Query(None, description="equity | etf | mutual_fund | crypto"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    service: MarketService = Depends(_get_market_service),
) -> JSONResponse:
    """Searches stocks, ETFs, and mutual funds by symbol or company name."""
    data = await service.search(q, exchange, type, limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Search results retrieved.", "data": data, "meta": _meta()},
    )


# ── GET /stocks/{symbol} ──────────────────────────────────────────────────────

@router.get("/stocks/{symbol}", status_code=status.HTTP_200_OK, summary="Get stock details")
async def get_stock_details(
    symbol: str,
    exchange: str | None = Query(None),
    period: str = Query("1D", description="1D | 1W | 1M | 3M | 6M | 1Y | 5Y"),
    current_user: User = Depends(get_current_user),
    service: MarketService = Depends(_get_market_service),
) -> JSONResponse:
    """Returns comprehensive stock details including price, fundamentals, and history."""
    data = await service.get_stock_details(symbol, exchange, period)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Stock details retrieved.", "data": {"stock": data}, "meta": _meta()},
    )


# ── GET /overview ─────────────────────────────────────────────────────────────

@router.get("/overview", status_code=status.HTTP_200_OK, summary="Market overview")
async def get_market_overview(
    exchanges: str = Query("NSE,BSE", description="Comma-separated exchange list"),
    current_user: User = Depends(get_current_user),
    service: MarketService = Depends(_get_market_service),
) -> JSONResponse:
    """Returns index snapshot, top movers, and market breadth indicators."""
    data = await service.get_market_overview(exchanges)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Market overview retrieved.", "data": {"overview": data}, "meta": _meta()},
    )


# ── GET /trending ─────────────────────────────────────────────────────────────

@router.get("/trending", status_code=status.HTTP_200_OK, summary="Trending stocks")
async def get_trending_stocks(
    exchange: str = Query("NSE"),
    category: str = Query("all", description="all | gainers | losers | volume | 52w_high | 52w_low"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    service: MarketService = Depends(_get_market_service),
) -> JSONResponse:
    """Returns curated trending stocks by exchange and category."""
    data = await service.get_trending(exchange, category, limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Trending stocks retrieved.", "data": data, "meta": _meta()},
    )
