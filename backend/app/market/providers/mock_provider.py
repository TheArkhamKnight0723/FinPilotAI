"""
FinPilot AI – Mock Market Provider
A self-contained market data provider seeded with realistic Indian market data.
Implements BaseMarketProvider so it can be replaced by a live provider
(Yahoo Finance, Alpha Vantage, NSE, etc.) with zero changes to the service layer.

TODO: Replace with a live provider (e.g. YahooFinanceProvider) before production.
"""

import random
from datetime import UTC, datetime, timedelta

from app.market.base_provider import BaseMarketProvider

# ── Static data fixtures ──────────────────────────────────────────────────────

_STOCKS: list[dict] = [
    {"symbol": "RELIANCE",  "name": "Reliance Industries Limited",         "exchange": "NSE", "sector": "Energy",      "industry": "Oil & Gas", "price": 2680.50, "pe": 28.4, "pb": 2.3, "eps": 94.24, "div_yield": 0.34, "beta": 0.97, "mktcap": "18.15T", "week52_h": 3024.90, "week52_l": 2220.30},
    {"symbol": "TCS",       "name": "Tata Consultancy Services Ltd.",       "exchange": "NSE", "sector": "Technology",  "industry": "IT Services", "price": 3845.20, "pe": 32.1, "pb": 14.2, "eps": 119.78, "div_yield": 1.45, "beta": 0.78, "mktcap": "14.02T", "week52_h": 4255.00, "week52_l": 3200.00},
    {"symbol": "HDFCBANK",  "name": "HDFC Bank Limited",                   "exchange": "NSE", "sector": "Finance",     "industry": "Banking", "price": 1720.30, "pe": 19.8, "pb": 2.6, "eps": 86.88, "div_yield": 1.10, "beta": 0.82, "mktcap": "13.10T", "week52_h": 1880.00, "week52_l": 1420.00},
    {"symbol": "INFY",      "name": "Infosys Limited",                     "exchange": "NSE", "sector": "Technology",  "industry": "IT Services", "price": 1580.75, "pe": 25.6, "pb": 7.3, "eps": 61.75, "div_yield": 2.10, "beta": 0.74, "mktcap": "6.57T",  "week52_h": 1960.00, "week52_l": 1350.00},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Limited",                  "exchange": "NSE", "sector": "Finance",     "industry": "Banking", "price": 1245.60, "pe": 17.4, "pb": 2.4, "eps": 71.59, "div_yield": 0.80, "beta": 1.05, "mktcap": "8.75T",  "week52_h": 1390.00, "week52_l": 980.00},
    {"symbol": "BAJFINANCE","name": "Bajaj Finance Limited",               "exchange": "NSE", "sector": "Finance",     "industry": "NBFC", "price": 7240.50, "pe": 42.3, "pb": 9.8, "eps": 171.17, "div_yield": 0.28, "beta": 1.35, "mktcap": "4.35T",  "week52_h": 8190.00, "week52_l": 5800.00},
    {"symbol": "TATAMOTORS","name": "Tata Motors Limited",                 "exchange": "NSE", "sector": "Auto",        "industry": "Automobiles", "price": 986.40, "pe": 14.2, "pb": 3.1, "eps": 69.47, "div_yield": 0.50, "beta": 1.42, "mktcap": "3.62T",  "week52_h": 1180.00, "week52_l": 750.00},
    {"symbol": "ADANIENT",  "name": "Adani Enterprises Limited",           "exchange": "NSE", "sector": "Conglomerate","industry": "Diversified", "price": 3124.50, "pe": 98.2, "pb": 8.4, "eps": 31.82, "div_yield": 0.06, "beta": 1.68, "mktcap": "3.55T",  "week52_h": 3650.00, "week52_l": 2010.00},
    {"symbol": "ZOMATO",    "name": "Zomato Limited",                      "exchange": "NSE", "sector": "Consumer",    "industry": "Food Delivery", "price": 248.60, "pe": 180.0, "pb": 12.5, "eps": 1.38, "div_yield": 0.00, "beta": 1.85, "mktcap": "2.20T",  "week52_h": 320.00, "week52_l": 185.00},
    {"symbol": "NIFTYBEES", "name": "Nippon India ETF Nifty BeES",        "exchange": "NSE", "sector": "ETF",         "industry": "Index Fund", "price": 248.30, "pe": 22.4, "pb": 4.1, "eps": 11.08, "div_yield": 0.90, "beta": 1.00, "mktcap": "N/A",    "week52_h": 280.00, "week52_l": 200.00},
    {"symbol": "WIPRO",     "name": "Wipro Limited",                       "exchange": "NSE", "sector": "Technology",  "industry": "IT Services", "price": 570.25, "pe": 22.8, "pb": 4.2, "eps": 25.01, "div_yield": 0.18, "beta": 0.80, "mktcap": "2.96T",  "week52_h": 680.00, "week52_l": 490.00},
    {"symbol": "LTIM",      "name": "LTIMindtree Limited",                 "exchange": "NSE", "sector": "Technology",  "industry": "IT Services", "price": 5840.00, "pe": 36.5, "pb": 10.2, "eps": 160.00, "div_yield": 0.55, "beta": 0.85, "mktcap": "1.73T",  "week52_h": 7100.00, "week52_l": 4800.00},
]

_STOCK_MAP: dict[str, dict] = {s["symbol"]: s for s in _STOCKS}

_INDICES = [
    {"name": "NIFTY 50",   "symbol": "^NSEI",    "value": 24853.15, "change": 185.30,  "change_pct": 0.75},
    {"name": "SENSEX",     "symbol": "^BSESN",   "value": 81420.60, "change": 563.80,  "change_pct": 0.70},
    {"name": "NIFTY Bank", "symbol": "^NSEBANK", "value": 52314.80, "change": -120.50, "change_pct": -0.23},
    {"name": "NIFTY IT",   "symbol": "^CNXIT",   "value": 38740.00, "change": 310.60,  "change_pct": 0.81},
]


def _add_intraday_noise(base_price: float) -> dict:
    """Simulate OHLC from a base price with small random offsets."""
    rng = random.Random(int(base_price * 100))  # deterministic seed per price
    open_ = round(base_price * (1 - rng.uniform(0.005, 0.015)), 2)
    high = round(base_price * (1 + rng.uniform(0.005, 0.020)), 2)
    low = round(base_price * (1 - rng.uniform(0.005, 0.015)), 2)
    prev_close = round(base_price * (1 - rng.uniform(0.002, 0.010)), 2)
    return {
        "current": base_price,
        "open": open_,
        "high": high,
        "low": low,
        "previous_close": prev_close,
        "change": round(base_price - prev_close, 2),
        "change_pct": round(((base_price - prev_close) / prev_close) * 100, 2),
    }


def _generate_price_history(base_price: float, days: int) -> list[dict]:
    """Generate synthetic OHLCV history."""
    history = []
    rng = random.Random(int(base_price))
    price = base_price
    for i in range(days):
        date = (datetime.now(UTC) - timedelta(days=days - i)).strftime("%Y-%m-%d")
        change = price * rng.uniform(-0.025, 0.025)
        open_ = round(price, 2)
        close = round(price + change, 2)
        high = round(max(open_, close) * (1 + rng.uniform(0, 0.01)), 2)
        low = round(min(open_, close) * (1 - rng.uniform(0, 0.01)), 2)
        volume = rng.randint(500_000, 10_000_000)
        history.append({"date": date, "open": open_, "close": close, "high": high, "low": low, "volume": volume})
        price = close
    return history


_PERIOD_DAYS = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}


class MockMarketProvider(BaseMarketProvider):
    """
    Self-contained mock market data provider.
    No external API calls — useful for development, CI, and hackathon demos.
    """

    async def search(
        self,
        query: str,
        exchange: str | None,
        asset_type: str | None,
        limit: int,
    ) -> dict:
        q = query.upper().strip()
        results = [
            s for s in _STOCKS
            if q in s["symbol"] or q in s["name"].upper()
        ]
        if exchange:
            results = [s for s in results if s["exchange"].upper() == exchange.upper()]

        results = results[:limit]
        return {
            "results": [
                {
                    "symbol": s["symbol"],
                    "name": s["name"],
                    "exchange": s["exchange"],
                    "asset_type": "etf" if s["sector"] == "ETF" else "equity",
                    "current_price": s["price"],
                    "currency": "INR",
                    "change": _add_intraday_noise(s["price"])["change"],
                    "change_pct": _add_intraday_noise(s["price"])["change_pct"],
                    "market_cap": s["mktcap"],
                }
                for s in results
            ],
            "total": len(results),
            "query": query,
        }

    async def get_stock_details(
        self,
        symbol: str,
        exchange: str | None,
        period: str,
    ) -> dict:
        stock = _STOCK_MAP.get(symbol.upper())
        if not stock:
            return {}  # caller converts empty dict to 404

        days = _PERIOD_DAYS.get(period, 30)
        price_data = _add_intraday_noise(stock["price"])
        history = _generate_price_history(stock["price"], days)

        return {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "exchange": stock["exchange"],
            "asset_type": "etf" if stock["sector"] == "ETF" else "equity",
            "sector": stock["sector"],
            "industry": stock["industry"],
            "price": price_data,
            "volume": {
                "current": random.randint(1_000_000, 15_000_000),
                "average_10d": random.randint(800_000, 12_000_000),
            },
            "market_data": {
                "market_cap": stock["mktcap"],
                "pe_ratio": stock["pe"],
                "pb_ratio": stock["pb"],
                "eps": stock["eps"],
                "dividend_yield": stock["div_yield"],
                "52_week_high": stock["week52_h"],
                "52_week_low": stock["week52_l"],
                "beta": stock["beta"],
            },
            "currency": "INR",
            "historical_prices": history,
        }

    async def get_market_overview(self, exchanges: list[str]) -> dict:
        sorted_by_change = sorted(_STOCKS, key=lambda s: _add_intraday_noise(s["price"])["change_pct"], reverse=True)
        gainers = sorted_by_change[:3]
        losers = sorted_by_change[-3:]

        return {
            "market_status": "open",
            "last_updated": datetime.now(UTC).isoformat(),
            "indices": _INDICES,
            "top_gainers": [
                {"symbol": s["symbol"], "name": s["name"], "change_pct": _add_intraday_noise(s["price"])["change_pct"]}
                for s in gainers
            ],
            "top_losers": [
                {"symbol": s["symbol"], "name": s["name"], "change_pct": _add_intraday_noise(s["price"])["change_pct"]}
                for s in losers
            ],
            "market_breadth": {"advances": 1348, "declines": 621, "unchanged": 108},
        }

    async def get_trending(
        self,
        exchange: str,
        category: str,
        limit: int,
    ) -> dict:
        stocks = [s for s in _STOCKS if s["exchange"].upper() == exchange.upper() or exchange.upper() == "ALL"]

        if category in ("gainers", "all"):
            ranked = sorted(stocks, key=lambda s: _add_intraday_noise(s["price"])["change_pct"], reverse=True)
        elif category == "losers":
            ranked = sorted(stocks, key=lambda s: _add_intraday_noise(s["price"])["change_pct"])
        else:
            ranked = stocks  # volume / 52w etc — use as-is for mock

        ranked = ranked[:limit]
        return {
            "category": category,
            "exchange": exchange,
            "stocks": [
                {
                    "rank": i + 1,
                    "symbol": s["symbol"],
                    "name": s["name"],
                    "current_price": s["price"],
                    "change_pct": _add_intraday_noise(s["price"])["change_pct"],
                    "volume": random.randint(1_000_000, 15_000_000),
                    "reason": "High trading activity",
                }
                for i, s in enumerate(ranked)
            ],
            "total": len(ranked),
            "generated_at": datetime.now(UTC).isoformat(),
        }
