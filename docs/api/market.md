# Market Data API Contract

> **Base URL:** `/api/v1/market`
> **Version:** v1
> **Authentication:** Some endpoints are public; others require a Bearer token.
> **Last Updated:** 2026-07-29

---

## Endpoints

### 1. Search Stock

**`GET /api/v1/market/search`**

Searches for stocks, ETFs, and mutual funds by symbol or company name. Supports fuzzy matching.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 60 seconds |

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `q` | string | Yes | Search query (symbol or company name, min 2 chars) |
| `exchange` | string | No | Filter by exchange: `NSE`, `BSE`, `NASDAQ`, `NYSE` |
| `type` | string | No | Asset type: `equity`, `etf`, `mutual_fund`, `crypto` |
| `limit` | integer | No | Results per page, default `10`, max `50` |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Search results retrieved.",
  "data": {
    "results": [
      {
        "symbol": "TCS",
        "name": "Tata Consultancy Services Ltd.",
        "exchange": "NSE",
        "asset_type": "equity",
        "current_price": 3845.20,
        "currency": "INR",
        "change": 45.30,
        "change_pct": 1.19,
        "market_cap": "14.02T"
      },
      {
        "symbol": "TCS.BSE",
        "name": "Tata Consultancy Services Ltd.",
        "exchange": "BSE",
        "asset_type": "equity",
        "current_price": 3844.80,
        "currency": "INR",
        "change": 44.90,
        "change_pct": 1.18,
        "market_cap": "14.02T"
      }
    ],
    "total": 2,
    "query": "TCS"
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `QUERY_TOO_SHORT` | Search query is less than 2 characters |
| `400` | `INVALID_EXCHANGE` | Exchange value not in allowed list |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many requests |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/market/search?q=TCS&exchange=NSE&limit=5" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 2. Get Stock Details

**`GET /api/v1/market/stocks/{symbol}`**

Returns comprehensive details about a specific stock including price, fundamentals, and technical indicators.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 30 seconds |

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `symbol` | string | Stock ticker symbol (e.g. `RELIANCE`, `AAPL`) |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `exchange` | string | Auto-detected | Exchange: `NSE`, `BSE`, `NASDAQ` |
| `period` | string | `1D` | Historical price window: `1D`, `1W`, `1M`, `3M`, `6M`, `1Y`, `5Y` |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Stock details retrieved.",
  "data": {
    "stock": {
      "symbol": "RELIANCE",
      "name": "Reliance Industries Limited",
      "exchange": "NSE",
      "asset_type": "equity",
      "sector": "Energy",
      "industry": "Oil & Gas Refining & Marketing",
      "price": {
        "current": 2680.50,
        "open": 2640.00,
        "high": 2695.00,
        "low": 2628.75,
        "previous_close": 2620.00,
        "change": 60.50,
        "change_pct": 2.31
      },
      "volume": {
        "current": 4520000,
        "average_10d": 3800000
      },
      "market_data": {
        "market_cap": "18.15T",
        "pe_ratio": 28.4,
        "pb_ratio": 2.3,
        "eps": 94.24,
        "dividend_yield": 0.34,
        "52_week_high": 3024.90,
        "52_week_low": 2220.30,
        "beta": 0.97
      },
      "currency": "INR",
      "historical_prices": [
        { "date": "2026-07-28", "open": 2600.00, "close": 2620.00, "high": 2650.00, "low": 2590.00, "volume": 3900000 }
      ]
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_SYMBOL` | Symbol format is invalid |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `404` | `SYMBOL_NOT_FOUND` | Symbol not found in market data |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many requests |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/market/stocks/RELIANCE?exchange=NSE&period=1M" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 3. Market Overview

**`GET /api/v1/market/overview`**

Returns a snapshot of major indices, top gainers, top losers, and market breadth indicators.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 60 seconds |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `exchanges` | string | `NSE,BSE` | Comma-separated exchanges to include |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Market overview retrieved.",
  "data": {
    "overview": {
      "market_status": "open",
      "last_updated": "2026-07-29T17:25:00Z",
      "indices": [
        {
          "name": "NIFTY 50",
          "symbol": "^NSEI",
          "value": 24853.15,
          "change": 185.30,
          "change_pct": 0.75
        },
        {
          "name": "SENSEX",
          "symbol": "^BSESN",
          "value": 81420.60,
          "change": 563.80,
          "change_pct": 0.70
        },
        {
          "name": "NIFTY Bank",
          "symbol": "^NSEBANK",
          "value": 52314.80,
          "change": -120.50,
          "change_pct": -0.23
        }
      ],
      "top_gainers": [
        { "symbol": "ADANIENT", "name": "Adani Enterprises", "change_pct": 4.82 }
      ],
      "top_losers": [
        { "symbol": "ZOMATO", "name": "Zomato Ltd", "change_pct": -3.15 }
      ],
      "market_breadth": {
        "advances": 1348,
        "declines": 621,
        "unchanged": 108
      }
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `503` | `MARKET_DATA_UNAVAILABLE` | External market feed is unreachable |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/market/overview?exchanges=NSE,BSE" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 4. Trending Stocks

**`GET /api/v1/market/trending`**

Returns a curated list of trending and most-discussed stocks based on volume, price movement, and news activity.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 5 minutes |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `exchange` | string | `NSE` | Exchange to filter by |
| `category` | string | `all` | `all`, `gainers`, `losers`, `volume`, `52w_high`, `52w_low` |
| `limit` | integer | `10` | Number of results, max `50` |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Trending stocks retrieved.",
  "data": {
    "category": "gainers",
    "exchange": "NSE",
    "stocks": [
      {
        "rank": 1,
        "symbol": "ADANIENT",
        "name": "Adani Enterprises Ltd.",
        "current_price": 3124.50,
        "change_pct": 4.82,
        "volume": 8920000,
        "reason": "Q1 results beat estimates by 18%"
      },
      {
        "rank": 2,
        "symbol": "TATAMOTORS",
        "name": "Tata Motors Ltd.",
        "current_price": 986.40,
        "change_pct": 3.65,
        "volume": 12450000,
        "reason": "EV sales milestone announced"
      }
    ],
    "total": 2,
    "generated_at": "2026-07-29T17:00:00Z"
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_CATEGORY` | Category not in allowed enum |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `503` | `MARKET_DATA_UNAVAILABLE` | External market feed is unreachable |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/market/trending?exchange=NSE&category=gainers&limit=10" \
  -H "Authorization: Bearer eyJhbGci..."
```
