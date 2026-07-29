# News API Contract

> **Base URL:** `/api/v1/news`
> **Version:** v1
> **Authentication:** All endpoints require `Authorization: Bearer <token>`
> **Last Updated:** 2026-07-29

---

## News Article Object

```json
{
  "id": "nws_01J8XYZABC123",
  "title": "RBI holds repo rate at 6.5%; signals dovish pivot",
  "summary": "The Reserve Bank of India kept its benchmark repo rate unchanged...",
  "url": "https://source.com/article/rbi-rate-hold",
  "source": "Economic Times",
  "author": "Priya Nair",
  "published_at": "2026-07-29T10:00:00Z",
  "image_url": "https://cdn.source.com/images/rbi.jpg",
  "sentiment": "positive",
  "sentiment_score": 0.72,
  "related_symbols": ["HDFCBANK", "ICICIBANK", "BANKBARODA"],
  "tags": ["RBI", "monetary policy", "interest rates", "banking"],
  "category": "economy"
}
```

---

## Endpoints

### 1. Latest Financial News

**`GET /api/v1/news/latest`**

Returns a paginated feed of the latest financial and market news from curated sources.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 5 minutes |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | Page number |
| `limit` | integer | `20` | Results per page, max `50` |
| `category` | string | `all` | Filter: `all`, `economy`, `markets`, `corporate`, `global`, `crypto` |
| `sentiment` | string | `all` | Filter: `all`, `positive`, `negative`, `neutral` |
| `language` | string | `en` | Language code (ISO 639-1) |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Latest news retrieved.",
  "data": {
    "articles": [
      {
        "id": "nws_01J8XYZABC123",
        "title": "RBI holds repo rate at 6.5%; signals dovish pivot",
        "summary": "The Reserve Bank of India kept its benchmark repo rate unchanged at 6.5%...",
        "url": "https://economictimes.com/article/rbi-rate-hold",
        "source": "Economic Times",
        "published_at": "2026-07-29T10:00:00Z",
        "image_url": "https://cdn.et.com/images/rbi.jpg",
        "sentiment": "positive",
        "sentiment_score": 0.72,
        "related_symbols": ["HDFCBANK", "ICICIBANK"],
        "category": "economy"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 248,
      "total_pages": 13,
      "has_next": true,
      "has_prev": false
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_CATEGORY` | Category not in allowed list |
| `400` | `INVALID_SENTIMENT` | Sentiment filter value invalid |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many requests |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/news/latest?category=economy&limit=10&page=1" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 2. Stock-Specific News

**`GET /api/v1/news/stocks/{symbol}`**

Returns news articles specifically about a given stock or company.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 5 minutes |

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `symbol` | string | Stock ticker symbol (e.g. `RELIANCE`, `INFY`) |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | Page number |
| `limit` | integer | `10` | Results per page, max `30` |
| `from_date` | string | 7 days ago | Start date (ISO 8601, e.g. `2026-07-22`) |
| `to_date` | string | today | End date (ISO 8601) |
| `sentiment` | string | `all` | Filter: `positive`, `negative`, `neutral`, `all` |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Stock news retrieved.",
  "data": {
    "symbol": "RELIANCE",
    "company_name": "Reliance Industries Limited",
    "overall_sentiment": "positive",
    "avg_sentiment_score": 0.68,
    "articles": [
      {
        "id": "nws_01J8XYZ456",
        "title": "Reliance Jio 5G subscriber base crosses 200 million",
        "summary": "Reliance Jio announced that its 5G network has crossed 200 million subscribers...",
        "url": "https://businessstandard.com/article/jio-5g-200m",
        "source": "Business Standard",
        "published_at": "2026-07-29T08:30:00Z",
        "sentiment": "positive",
        "sentiment_score": 0.84,
        "tags": ["Jio", "5G", "telecom", "subscribers"]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 34,
      "total_pages": 4,
      "has_next": true
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_DATE_RANGE` | Date range is invalid or exceeds 90 days |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `404` | `SYMBOL_NOT_FOUND` | Symbol not recognized |

#### Example Request

```bash
curl -X GET \
  "https://api.finpilot.ai/api/v1/news/stocks/RELIANCE?limit=5&sentiment=positive" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 3. Market Headlines

**`GET /api/v1/news/headlines`**

Returns a concise list of the top 10–15 major market-moving headlines for quick consumption. Optimized for dashboard widgets.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Cache TTL** | 3 minutes |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `exchange` | string | `NSE` | Primary exchange context: `NSE`, `BSE`, `GLOBAL` |
| `limit` | integer | `10` | Number of headlines, max `15` |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Market headlines retrieved.",
  "data": {
    "exchange": "NSE",
    "generated_at": "2026-07-29T17:20:00Z",
    "headlines": [
      {
        "id": "nws_01J8XYZ999",
        "title": "NIFTY 50 hits fresh all-time high above 24,900",
        "source": "Mint",
        "published_at": "2026-07-29T12:00:00Z",
        "url": "https://livemint.com/nifty-ath",
        "sentiment": "positive",
        "sentiment_score": 0.91,
        "impact": "high",
        "related_symbols": ["^NSEI"]
      },
      {
        "id": "nws_01J8XYZ998",
        "title": "Infosys Q1 FY27 revenue misses street estimates by 3%",
        "source": "CNBC TV18",
        "published_at": "2026-07-29T11:30:00Z",
        "url": "https://cnbctv18.com/infy-q1",
        "sentiment": "negative",
        "sentiment_score": -0.58,
        "impact": "high",
        "related_symbols": ["INFY"]
      }
    ],
    "total": 10
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_EXCHANGE` | Exchange not in allowed list |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `503` | `NEWS_FEED_UNAVAILABLE` | External news provider is unreachable |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/news/headlines?exchange=NSE&limit=10" \
  -H "Authorization: Bearer eyJhbGci..."
```
