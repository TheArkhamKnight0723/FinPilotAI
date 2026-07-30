"""
FinPilot AI – Market Service
Orchestrates market data requests through the provider abstraction.
Applies an in-process TTL cache so that repeated calls within the
cache window don't hit the provider (drop-in Redis when ready).
"""

import logging
import time
from typing import Any

from app.exceptions.exceptions import BadRequestException, NotFoundException, ServiceUnavailableException
from app.market.base_provider import BaseMarketProvider

logger = logging.getLogger(__name__)

# ── Valid enumerations ────────────────────────────────────────────────────────
VALID_EXCHANGES = {"NSE", "BSE", "NASDAQ", "NYSE", "ALL"}
VALID_CATEGORIES = {"all", "gainers", "losers", "volume", "52w_high", "52w_low"}
VALID_PERIODS = {"1D", "1W", "1M", "3M", "6M", "1Y", "5Y"}


# ── Simple in-process TTL cache ───────────────────────────────────────────────

class _Cache:
    """
    Thread-safe in-process TTL cache.
    Suitable for single-instance development.
    TODO: Replace with Redis-backed cache for multi-instance production.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (value, time.monotonic() + ttl_seconds)

    def clear(self) -> None:
        self._store.clear()


_cache = _Cache()


class MarketService:
    """
    Facade over the market data provider.
    All validation and caching happens here; routers stay thin.
    """

    def __init__(self, provider: BaseMarketProvider) -> None:
        self._provider = provider

    # ── Search ────────────────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        exchange: str | None = None,
        asset_type: str | None = None,
        limit: int = 10,
    ) -> dict:
        """
        Searches stocks by symbol or name.

        Raises:
            BadRequestException: query < 2 chars or invalid exchange.
        """
        if len(query.strip()) < 2:
            raise BadRequestException("Search query must be at least 2 characters.")
        if exchange and exchange.upper() not in VALID_EXCHANGES:
            raise BadRequestException(
                f"Invalid exchange '{exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}"
            )
        limit = min(max(limit, 1), 50)

        cache_key = f"search:{query}:{exchange}:{asset_type}:{limit}"
        if cached := _cache.get(cache_key):
            return cached

        try:
            data = await self._provider.search(query, exchange, asset_type, limit)
        except Exception as exc:
            logger.error("Market provider search failed: %s", exc)
            raise ServiceUnavailableException("Market data service is temporarily unavailable.")

        _cache.set(cache_key, data, ttl_seconds=60)
        return data

    # ── Stock Details ─────────────────────────────────────────────────────────

    async def get_stock_details(
        self,
        symbol: str,
        exchange: str | None = None,
        period: str = "1D",
    ) -> dict:
        """
        Returns full stock details for a given symbol.

        Raises:
            BadRequestException: Invalid period.
            NotFoundException: Symbol not found.
        """
        if period not in VALID_PERIODS:
            raise BadRequestException(
                f"Invalid period '{period}'. Valid: {', '.join(sorted(VALID_PERIODS))}"
            )
        sym = symbol.upper().strip()

        cache_key = f"stock:{sym}:{exchange}:{period}"
        if cached := _cache.get(cache_key):
            return cached

        try:
            data = await self._provider.get_stock_details(sym, exchange, period)
        except Exception as exc:
            logger.error("Market provider stock detail failed for %s: %s", sym, exc)
            raise ServiceUnavailableException("Market data service is temporarily unavailable.")

        if not data:
            raise NotFoundException(f"Symbol '{sym}' not found in market data.")

        _cache.set(cache_key, data, ttl_seconds=30)
        return data

    # ── Market Overview ───────────────────────────────────────────────────────

    async def get_market_overview(self, exchanges_param: str = "NSE,BSE") -> dict:
        """
        Returns index snapshot, top gainers/losers, and breadth indicators.

        Raises:
            BadRequestException: Any invalid exchange in the list.
        """
        exchanges = [e.strip().upper() for e in exchanges_param.split(",") if e.strip()]
        invalid = [e for e in exchanges if e not in VALID_EXCHANGES]
        if invalid:
            raise BadRequestException(
                f"Invalid exchange(s): {invalid}. Valid: {', '.join(sorted(VALID_EXCHANGES))}"
            )

        cache_key = f"overview:{','.join(sorted(exchanges))}"
        if cached := _cache.get(cache_key):
            return cached

        try:
            data = await self._provider.get_market_overview(exchanges)
        except Exception as exc:
            logger.error("Market provider overview failed: %s", exc)
            raise ServiceUnavailableException("Market data service is temporarily unavailable.")

        _cache.set(cache_key, data, ttl_seconds=60)
        return data

    # ── Trending ──────────────────────────────────────────────────────────────

    async def get_trending(
        self,
        exchange: str = "NSE",
        category: str = "all",
        limit: int = 10,
    ) -> dict:
        """
        Returns trending stocks for a given exchange and category.

        Raises:
            BadRequestException: Invalid exchange or category.
        """
        if exchange.upper() not in VALID_EXCHANGES:
            raise BadRequestException(
                f"Invalid exchange '{exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}"
            )
        if category.lower() not in VALID_CATEGORIES:
            raise BadRequestException(
                f"Invalid category '{category}'. Valid: {', '.join(sorted(VALID_CATEGORIES))}"
            )
        limit = min(max(limit, 1), 50)

        cache_key = f"trending:{exchange}:{category}:{limit}"
        if cached := _cache.get(cache_key):
            return cached

        try:
            data = await self._provider.get_trending(exchange, category, limit)
        except Exception as exc:
            logger.error("Market provider trending failed: %s", exc)
            raise ServiceUnavailableException("Market data service is temporarily unavailable.")

        _cache.set(cache_key, data, ttl_seconds=300)
        return data
