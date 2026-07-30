"""
FinPilot AI – Market Provider Abstract Base
Defines the interface every market data provider must implement.
Swap the concrete provider in settings without touching the router or service.
"""

from abc import ABC, abstractmethod


class BaseMarketProvider(ABC):
    """
    Abstract market data provider.

    Concrete implementations (Yahoo Finance, Alpha Vantage, NSE API, etc.)
    must subclass this and implement every method.
    The MarketService depends only on this interface.
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        exchange: str | None,
        asset_type: str | None,
        limit: int,
    ) -> dict:
        """Search stocks/ETFs/MFs by symbol or company name."""

    @abstractmethod
    async def get_stock_details(
        self,
        symbol: str,
        exchange: str | None,
        period: str,
    ) -> dict:
        """Return comprehensive stock details including price and fundamentals."""

    @abstractmethod
    async def get_market_overview(self, exchanges: list[str]) -> dict:
        """Return indices snapshot, top gainers/losers, and market breadth."""

    @abstractmethod
    async def get_trending(
        self,
        exchange: str,
        category: str,
        limit: int,
    ) -> dict:
        """Return trending stocks for a given exchange and category."""
