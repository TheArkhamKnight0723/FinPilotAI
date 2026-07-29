# Portfolio API Contract

> **Base URL:** `/api/v1/portfolios`
> **Version:** v1
> **Authentication:** All endpoints require `Authorization: Bearer <token>`
> **Last Updated:** 2026-07-29

---

## Data Models

### Portfolio Object

```json
{
  "id": "pfl_01J8XYZABC123",
  "user_id": "usr_01J8XYZABC123",
  "name": "My Growth Portfolio",
  "description": "Long-term wealth accumulation",
  "currency": "INR",
  "total_value": 285000.00,
  "total_invested": 250000.00,
  "total_gain_loss": 35000.00,
  "total_gain_loss_pct": 14.0,
  "holdings": [ ... ],
  "created_at": "2026-07-29T17:30:00Z",
  "updated_at": "2026-07-29T17:30:00Z"
}
```

### Holding Object

```json
{
  "id": "hld_01J8XYZ789",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "name": "Reliance Industries Ltd.",
  "asset_type": "equity",
  "quantity": 10,
  "average_buy_price": 2450.00,
  "current_price": 2680.50,
  "current_value": 26805.00,
  "total_invested": 24500.00,
  "gain_loss": 2305.00,
  "gain_loss_pct": 9.41,
  "added_at": "2026-07-29T17:30:00Z"
}
```

---

## Endpoints

### 1. Create Portfolio

**`POST /api/v1/portfolios`**

Creates a new investment portfolio for the authenticated user.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Request Body

```json
{
  "name": "string (required, 2–100 chars)",
  "description": "string (optional, max 500 chars)",
  "currency": "string (optional, ISO 4217, default: INR)"
}
```

#### Success Response `201 Created`

```json
{
  "success": true,
  "message": "Portfolio created successfully.",
  "data": {
    "portfolio": {
      "id": "pfl_01J8XYZABC123",
      "user_id": "usr_01J8XYZABC123",
      "name": "My Growth Portfolio",
      "description": "Long-term wealth accumulation",
      "currency": "INR",
      "total_value": 0.00,
      "holdings_count": 0,
      "created_at": "2026-07-29T17:30:00Z"
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Invalid or missing fields |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `409` | `PORTFOLIO_NAME_TAKEN` | A portfolio with this name already exists |
| `422` | `PORTFOLIO_LIMIT_REACHED` | User has reached the maximum portfolio count |

#### Example Request

```bash
curl -X POST https://api.finpilot.ai/api/v1/portfolios \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Growth Portfolio",
    "description": "Long-term wealth accumulation",
    "currency": "INR"
  }'
```

---

### 2. Get Portfolio

**`GET /api/v1/portfolios/{portfolio_id}`**

Retrieves a specific portfolio with all holdings and real-time valuation.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `portfolio_id` | string | Unique portfolio ID (e.g. `pfl_01J8XYZABC123`) |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `include_history` | boolean | false | Include historical performance data |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Portfolio retrieved.",
  "data": {
    "portfolio": {
      "id": "pfl_01J8XYZABC123",
      "name": "My Growth Portfolio",
      "currency": "INR",
      "total_value": 285000.00,
      "total_invested": 250000.00,
      "total_gain_loss": 35000.00,
      "total_gain_loss_pct": 14.0,
      "holdings": [
        {
          "id": "hld_01J8XYZ789",
          "symbol": "RELIANCE",
          "exchange": "NSE",
          "name": "Reliance Industries Ltd.",
          "asset_type": "equity",
          "quantity": 10,
          "average_buy_price": 2450.00,
          "current_price": 2680.50,
          "current_value": 26805.00,
          "gain_loss": 2305.00,
          "gain_loss_pct": 9.41
        }
      ],
      "holdings_count": 1,
      "created_at": "2026-07-29T17:30:00Z",
      "updated_at": "2026-07-29T17:30:00Z"
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `403` | `FORBIDDEN` | Portfolio belongs to another user |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio ID does not exist |

#### Example Request

```bash
curl -X GET "https://api.finpilot.ai/api/v1/portfolios/pfl_01J8XYZABC123" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 3. Update Portfolio

**`PATCH /api/v1/portfolios/{portfolio_id}`**

Updates portfolio metadata or adds/modifies holdings.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `portfolio_id` | string | Unique portfolio ID |

#### Request Body (all fields optional)

```json
{
  "name": "string (2–100 chars)",
  "description": "string (max 500 chars)",
  "holdings": [
    {
      "symbol": "string (required)",
      "exchange": "string (e.g. NSE, BSE, NASDAQ)",
      "quantity": "number (required, positive)",
      "average_buy_price": "number (required, positive)",
      "asset_type": "string (equity | mutual_fund | etf | crypto | bond)"
    }
  ]
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Portfolio updated successfully.",
  "data": {
    "portfolio": {
      "id": "pfl_01J8XYZABC123",
      "name": "My Growth Portfolio – Updated",
      "holdings_count": 2,
      "total_value": 312000.00,
      "updated_at": "2026-07-29T17:45:00Z"
    }
  },
  "meta": { "timestamp": "2026-07-29T17:45:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Invalid field values |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `403` | `FORBIDDEN` | Portfolio belongs to another user |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio ID not found |
| `422` | `INVALID_SYMBOL` | Stock symbol not found in market data |

#### Example Request

```bash
curl -X PATCH "https://api.finpilot.ai/api/v1/portfolios/pfl_01J8XYZABC123" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {
        "symbol": "TCS",
        "exchange": "NSE",
        "quantity": 5,
        "average_buy_price": 3800.00,
        "asset_type": "equity"
      }
    ]
  }'
```

---

### 4. Delete Holding

**`DELETE /api/v1/portfolios/{portfolio_id}/holdings/{holding_id}`**

Removes a specific holding from a portfolio.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `portfolio_id` | string | Unique portfolio ID |
| `holding_id` | string | Unique holding ID |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Holding removed from portfolio.",
  "data": {
    "deleted_holding_id": "hld_01J8XYZ789",
    "portfolio_id": "pfl_01J8XYZABC123",
    "remaining_holdings": 1,
    "updated_total_value": 258500.00
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `403` | `FORBIDDEN` | Resource belongs to another user |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio ID not found |
| `404` | `HOLDING_NOT_FOUND` | Holding ID not found in portfolio |

#### Example Request

```bash
curl -X DELETE \
  "https://api.finpilot.ai/api/v1/portfolios/pfl_01J8XYZABC123/holdings/hld_01J8XYZ789" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 5. Portfolio Summary

**`GET /api/v1/portfolios/{portfolio_id}/summary`**

Returns a high-level analytical summary including asset allocation, sector distribution, top performers, and risk metrics.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `portfolio_id` | string | Unique portfolio ID |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `period` | string | `1M` | Performance window: `1W`, `1M`, `3M`, `6M`, `1Y`, `ALL` |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Portfolio summary retrieved.",
  "data": {
    "summary": {
      "portfolio_id": "pfl_01J8XYZABC123",
      "total_value": 285000.00,
      "total_invested": 250000.00,
      "total_gain_loss": 35000.00,
      "total_gain_loss_pct": 14.0,
      "period_return_pct": 4.2,
      "asset_allocation": {
        "equity": 75.0,
        "mutual_fund": 15.0,
        "etf": 5.0,
        "cash": 5.0
      },
      "sector_distribution": {
        "Technology": 40.0,
        "Energy": 25.0,
        "Finance": 20.0,
        "Consumer": 15.0
      },
      "top_performers": [
        { "symbol": "TCS", "gain_pct": 18.5 },
        { "symbol": "INFY", "gain_pct": 12.3 }
      ],
      "bottom_performers": [
        { "symbol": "ZOMATO", "gain_pct": -5.4 }
      ],
      "risk_score": 6.8,
      "diversification_score": 8.1,
      "period": "1M"
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_PERIOD` | Period value not in allowed list |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `403` | `FORBIDDEN` | Portfolio belongs to another user |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio not found |

#### Example Request

```bash
curl -X GET \
  "https://api.finpilot.ai/api/v1/portfolios/pfl_01J8XYZABC123/summary?period=3M" \
  -H "Authorization: Bearer eyJhbGci..."
```
