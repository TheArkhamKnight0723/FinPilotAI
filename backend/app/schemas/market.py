"""
FinPilot AI – Market Data Pydantic Schemas
Request query parameter contracts for market endpoints.
Responses are dicts constructed by the service and returned as JSONResponse.
"""

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Query parameters for GET /api/v1/market/search"""
    q: str = Field(..., min_length=2, description="Symbol or company name")
    exchange: str | None = Field(None, description="Exchange filter: NSE, BSE, NASDAQ, NYSE")
    type: str | None = Field(None, description="Asset type: equity, etf, mutual_fund, crypto")
    limit: int = Field(10, ge=1, le=50)


class StockDetailQuery(BaseModel):
    """Query parameters for GET /api/v1/market/stocks/{symbol}"""
    exchange: str | None = Field(None)
    period: str = Field("1D", description="Price history window: 1D,1W,1M,3M,6M,1Y,5Y")


class OverviewQuery(BaseModel):
    """Query parameters for GET /api/v1/market/overview"""
    exchanges: str = Field("NSE,BSE", description="Comma-separated exchange list")


class TrendingQuery(BaseModel):
    """Query parameters for GET /api/v1/market/trending"""
    exchange: str = Field("NSE")
    category: str = Field("all", description="all|gainers|losers|volume|52w_high|52w_low")
    limit: int = Field(10, ge=1, le=50)
