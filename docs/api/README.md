# FinPilot AI – API Contract Documentation

> **Version:** v1 | **Base URL:** `/api/v1` | **Last Updated:** 2026-07-29

This directory contains the complete REST API contract for the FinPilot AI backend.
All endpoints are versioned under `/api/v1/` and follow a consistent JSON response envelope.

---

## Response Envelope Standard

Every API response — success or failure — uses this consistent structure:

```json
{
  "success": true,
  "message": "Human-readable description",
  "data": { ... },
  "error": "ERROR_CODE (failures only)",
  "meta": {
    "timestamp": "2026-07-29T17:30:00Z"
  }
}
```

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## API Documents

| Document | Base Path | Description |
|---|---|---|
| [auth.md](./auth.md) | `/api/v1/auth` | Registration, login, logout, token refresh |
| [user.md](./user.md) | `/api/v1/users` | Profile management and account settings |
| [portfolio.md](./portfolio.md) | `/api/v1/portfolios` | Portfolio and holdings management |
| [market.md](./market.md) | `/api/v1/market` | Stock search, details, indices, trending |
| [news.md](./news.md) | `/api/v1/news` | Financial news and market headlines |
| [ai.md](./ai.md) | `/api/v1/ai` | AI chat, analysis, suggestions, planning |

---

## Complete Endpoint Index

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | No | Create a new user account |
| POST | `/api/v1/auth/login` | No | Authenticate and receive JWT tokens |
| POST | `/api/v1/auth/logout` | Yes | Revoke access and refresh tokens |
| POST | `/api/v1/auth/refresh` | No | Refresh an expired access token |
| GET | `/api/v1/auth/me` | Yes | Get current authenticated user |

### Users (`/api/v1/users`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/users/me/profile` | Yes | Retrieve full user profile |
| PATCH | `/api/v1/users/me/profile` | Yes | Update user profile fields |
| PUT | `/api/v1/users/me/risk-preference` | Yes | Set investment risk tolerance |
| DELETE | `/api/v1/users/me` | Yes | Permanently delete user account |

### Portfolios (`/api/v1/portfolios`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/portfolios` | Yes | Create a new portfolio |
| GET | `/api/v1/portfolios/{id}` | Yes | Get portfolio with all holdings |
| PATCH | `/api/v1/portfolios/{id}` | Yes | Update portfolio metadata or holdings |
| DELETE | `/api/v1/portfolios/{id}/holdings/{hid}` | Yes | Remove a holding from portfolio |
| GET | `/api/v1/portfolios/{id}/summary` | Yes | Get analytical portfolio summary |

### Market Data (`/api/v1/market`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/market/search` | Yes | Search stocks by symbol or name |
| GET | `/api/v1/market/stocks/{symbol}` | Yes | Get full stock details and history |
| GET | `/api/v1/market/overview` | Yes | Market indices and breadth snapshot |
| GET | `/api/v1/market/trending` | Yes | Trending and top movers |

### News (`/api/v1/news`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/news/latest` | Yes | Paginated latest financial news feed |
| GET | `/api/v1/news/stocks/{symbol}` | Yes | News articles for a specific stock |
| GET | `/api/v1/news/headlines` | Yes | Top market-moving headlines |

### AI Endpoints (`/api/v1/ai`)

| Method | Endpoint | Auth | Streaming | Description |
|---|---|---|---|---|
| POST | `/api/v1/ai/chat` | Yes | Yes | AI financial assistant chat |
| POST | `/api/v1/ai/portfolio-analysis` | Yes | No | Deep portfolio analysis |
| POST | `/api/v1/ai/risk-analysis` | Yes | No | Risk profile and stress test |
| POST | `/api/v1/ai/investment-suggestions` | Yes | No | Personalised stock recommendations |
| POST | `/api/v1/ai/goal-planning` | Yes | No | Financial goal roadmap |
| POST | `/api/v1/ai/devils-advocate` | Yes | No | Counter-analysis and bear case |
| POST | `/api/v1/ai/explain-news` | Yes | No | Plain-English news explanation |

---

## Common HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | OK – Request succeeded |
| `201` | Created – Resource successfully created |
| `400` | Bad Request – Invalid input |
| `401` | Unauthorized – Authentication required or failed |
| `403` | Forbidden – Authenticated but not authorized |
| `404` | Not Found – Resource does not exist |
| `409` | Conflict – Duplicate resource |
| `422` | Unprocessable Entity – Semantic validation failure |
| `429` | Too Many Requests – Rate limit exceeded |
| `500` | Internal Server Error – Unexpected server failure |
| `503` | Service Unavailable – External dependency is down |
