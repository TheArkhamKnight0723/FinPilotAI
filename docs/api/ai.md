# AI API Contract

> **Base URL:** `/api/v1/ai`
> **Version:** v1
> **Authentication:** All endpoints require `Authorization: Bearer <token>`
> **Last Updated:** 2026-07-29

---

## AI Response Conventions

All AI endpoints return responses in this consistent structure:

```json
{
  "success": true,
  "message": "...",
  "data": {
    "session_id": "sess_01J8XYZ...",
    "result": { ... },
    "model": "gemini-2.0-flash",
    "tokens_used": 1240,
    "latency_ms": 1840
  },
  "meta": { "timestamp": "ISO-8601" }
}
```

> **Note on Streaming:** Endpoints that support streaming return `text/event-stream` (SSE) when the `stream=true` query parameter is set. Each SSE chunk is a JSON line: `data: {"delta": "partial text..."}`.

---

## Endpoints

### 1. AI Chat

**`POST /api/v1/ai/chat`**

Sends a message to the FinPilot AI financial assistant and receives a context-aware response. Supports conversation history for multi-turn dialogue.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Streaming Supported** | Yes (`?stream=true`) |
| **Rate Limit** | 60 requests / hour / user |

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `stream` | boolean | false | Enable Server-Sent Events streaming |

#### Request Body

```json
{
  "message": "string (required, 1–4000 chars)",
  "session_id": "string (optional — provide to continue a conversation)",
  "context": {
    "portfolio_id": "string (optional — attach portfolio context to the query)",
    "symbol": "string (optional — attach a specific stock to the query)"
  }
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "AI response generated.",
  "data": {
    "session_id": "sess_01J8XYZABC123",
    "reply": "Based on your portfolio composition, your current equity exposure is 75%. Given your **aggressive** risk profile, this is within the recommended range of 70–80%. However, I notice your technology sector concentration is 40%, which may expose you to correlated downside risk...",
    "reply_markdown": true,
    "follow_up_suggestions": [
      "How can I diversify my tech exposure?",
      "What's the current outlook for NIFTY IT?",
      "Show me defensive stock recommendations"
    ],
    "sources": [
      { "type": "portfolio", "id": "pfl_01J8XYZABC123" },
      { "type": "market_data", "symbol": "^NSEI" }
    ],
    "model": "gemini-2.0-flash",
    "tokens_used": 842,
    "latency_ms": 1240
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Streaming Response (SSE chunks)

```
data: {"session_id":"sess_01J8XYZ...","delta":"Based on your portfolio"}
data: {"session_id":"sess_01J8XYZ...","delta":" composition, your"}
data: {"session_id":"sess_01J8XYZ...","delta":" current equity exposure is 75%."}
data: {"session_id":"sess_01J8XYZ...","done":true,"tokens_used":842}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `MESSAGE_TOO_LONG` | Message exceeds 4000 characters |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `404` | `SESSION_NOT_FOUND` | Provided session_id does not exist |
| `429` | `RATE_LIMIT_EXCEEDED` | Chat quota exhausted for this hour |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM provider is temporarily unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/chat" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current risk level of my portfolio?",
    "context": { "portfolio_id": "pfl_01J8XYZABC123" }
  }'
```

---

### 2. Portfolio Analysis

**`POST /api/v1/ai/portfolio-analysis`**

Triggers a deep AI-driven analysis of a user's portfolio, evaluating performance, risk exposure, sector concentration, and opportunities.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Processing Time** | 5–15 seconds |
| **Rate Limit** | 10 requests / hour / user |

#### Request Body

```json
{
  "portfolio_id": "string (required)",
  "analysis_type": "string (optional, default: full) — one of: full | performance | risk | allocation"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Portfolio analysis complete.",
  "data": {
    "portfolio_id": "pfl_01J8XYZABC123",
    "analysis_type": "full",
    "generated_at": "2026-07-29T17:30:00Z",
    "summary": "Your portfolio shows strong momentum with 14% gains YTD. However, over-concentration in IT (40%) creates elevated systematic risk.",
    "performance": {
      "period_return_pct": 14.0,
      "benchmark_return_pct": 11.2,
      "alpha": 2.8,
      "beta": 1.12,
      "sharpe_ratio": 1.48,
      "max_drawdown_pct": -6.4
    },
    "risk_assessment": {
      "overall_risk_score": 6.8,
      "risk_level": "moderate-high",
      "concentration_risk": "high",
      "liquidity_risk": "low",
      "currency_risk": "none"
    },
    "allocation_analysis": {
      "sector_concentration_warning": "Technology sector at 40% exceeds recommended 25% cap.",
      "recommended_rebalancing": [
        { "action": "reduce", "symbol": "TCS", "reason": "Overweight in IT sector" },
        { "action": "add", "symbol": "HDFCBANK", "reason": "Underweight in financials" }
      ]
    },
    "opportunities": [
      "Consider adding dividend-yielding PSU stocks to reduce volatility.",
      "Infrastructure sector is showing momentum — NTPC and L&T warrant attention."
    ],
    "model": "gemini-2.0-flash",
    "tokens_used": 2140
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_ANALYSIS_TYPE` | Analysis type not in allowed enum |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `403` | `FORBIDDEN` | Portfolio belongs to another user |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio not found |
| `422` | `PORTFOLIO_EMPTY` | Portfolio has no holdings to analyze |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM provider unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/portfolio-analysis" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{ "portfolio_id": "pfl_01J8XYZABC123", "analysis_type": "full" }'
```

---

### 3. Risk Analysis

**`POST /api/v1/ai/risk-analysis`**

Generates a detailed risk profile for the user combining their portfolio composition, market conditions, and declared risk preference.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Rate Limit** | 10 requests / hour / user |

#### Request Body

```json
{
  "portfolio_id": "string (required)",
  "include_stress_test": "boolean (optional, default: false)"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Risk analysis generated.",
  "data": {
    "portfolio_id": "pfl_01J8XYZABC123",
    "risk_profile": {
      "overall_score": 6.8,
      "label": "Moderate-High",
      "user_preference": "aggressive",
      "alignment": "under-risked",
      "breakdown": {
        "market_risk": 7.2,
        "concentration_risk": 8.0,
        "liquidity_risk": 2.1,
        "valuation_risk": 5.5,
        "macro_risk": 4.8
      }
    },
    "stress_test": {
      "enabled": true,
      "scenarios": [
        {
          "name": "2008 Global Financial Crisis replay",
          "estimated_portfolio_decline_pct": -42.0
        },
        {
          "name": "COVID-19 March 2020 crash replay",
          "estimated_portfolio_decline_pct": -28.5
        },
        {
          "name": "10% INR depreciation",
          "estimated_portfolio_decline_pct": -3.2
        }
      ]
    },
    "recommendations": [
      "Add 2–3 defensive large-cap stocks to buffer against volatility.",
      "Reduce ZOMATO position — high beta stock with negative FCF.",
      "Consider 10% allocation to gold ETF as a hedge."
    ],
    "model": "gemini-2.0-flash"
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `403` | `FORBIDDEN` | Portfolio belongs to another user |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio not found |
| `422` | `PORTFOLIO_EMPTY` | No holdings available for analysis |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/risk-analysis" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{ "portfolio_id": "pfl_01J8XYZABC123", "include_stress_test": true }'
```

---

### 4. Investment Suggestions

**`POST /api/v1/ai/investment-suggestions`**

Generates personalised stock and instrument recommendations tailored to the user's risk profile, goals, and existing holdings.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Rate Limit** | 10 requests / hour / user |

#### Request Body

```json
{
  "portfolio_id": "string (required)",
  "budget": "number (optional — available investment amount in portfolio currency)",
  "focus": "string (optional) — one of: growth | dividend | value | momentum | all"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Investment suggestions generated.",
  "data": {
    "portfolio_id": "pfl_01J8XYZABC123",
    "focus": "growth",
    "budget_used": 50000.00,
    "suggestions": [
      {
        "rank": 1,
        "symbol": "BAJFINANCE",
        "name": "Bajaj Finance Limited",
        "exchange": "NSE",
        "current_price": 7240.50,
        "suggested_quantity": 3,
        "estimated_investment": 21721.50,
        "rationale": "Strong loan book growth of 28% YoY, improving NIM, and diversifying into insurance aligns with your growth-oriented profile.",
        "risk_level": "moderate",
        "upside_potential_pct": 18.0,
        "time_horizon": "12–18 months"
      },
      {
        "rank": 2,
        "symbol": "NIFTYBEES",
        "name": "Nippon India ETF Nifty BeES",
        "exchange": "NSE",
        "current_price": 248.30,
        "suggested_quantity": 115,
        "estimated_investment": 28554.50,
        "rationale": "Provides broad NIFTY 50 exposure at low cost, reducing single-stock risk in your portfolio.",
        "risk_level": "low",
        "upside_potential_pct": 12.0,
        "time_horizon": "24 months"
      }
    ],
    "disclaimer": "These are AI-generated suggestions for informational purposes only. Not financial advice. Please consult a SEBI-registered investment advisor.",
    "model": "gemini-2.0-flash"
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_FOCUS` | Focus value not in allowed enum |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `404` | `PORTFOLIO_NOT_FOUND` | Portfolio not found |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/investment-suggestions" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{ "portfolio_id": "pfl_01J8XYZABC123", "budget": 50000, "focus": "growth" }'
```

---

### 5. Goal Planning

**`POST /api/v1/ai/goal-planning`**

Creates an AI-generated financial goal roadmap — calculating required monthly SIP, asset mix, and projected timeline to achieve a stated financial goal.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Rate Limit** | 10 requests / hour / user |

#### Request Body

```json
{
  "goal_name": "string (required, e.g. 'Retirement', 'House Down Payment')",
  "target_amount": "number (required, in user's base currency)",
  "target_date": "string (required, ISO 8601 date, e.g. 2035-12-31)",
  "current_savings": "number (optional, default: 0)",
  "monthly_investment_capacity": "number (optional — user's available monthly budget)"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Goal plan generated.",
  "data": {
    "goal": {
      "name": "Early Retirement",
      "target_amount": 50000000,
      "currency": "INR",
      "target_date": "2040-12-31",
      "years_to_goal": 14,
      "current_savings": 500000
    },
    "plan": {
      "required_monthly_sip": 82400,
      "projected_return_rate_pct": 12.0,
      "recommended_asset_allocation": {
        "equity_mutual_funds": 60,
        "index_etfs": 20,
        "debt_funds": 15,
        "gold": 5
      },
      "milestone_projections": [
        { "year": 2028, "projected_value": 7200000 },
        { "year": 2032, "projected_value": 18500000 },
        { "year": 2036, "projected_value": 34800000 },
        { "year": 2040", "projected_value": 50200000 }
      ],
      "key_risks": [
        "Inflation erosion above 7% p.a.",
        "Market downturns requiring goal timeline extension"
      ],
      "ai_advice": "At ₹82,400/month SIP across diversified equity and debt instruments with a 12% CAGR assumption, you are on track for early retirement by 2040. Starting a ELSS fund component will also provide ₹1.5L annual tax deduction under 80C."
    },
    "disclaimer": "Projections are based on historical return assumptions and are not guaranteed. Consult a SEBI-registered financial advisor.",
    "model": "gemini-2.0-flash"
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_TARGET_DATE` | Target date is in the past |
| `400` | `VALIDATION_ERROR` | Missing required fields |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/goal-planning" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "goal_name": "Early Retirement",
    "target_amount": 50000000,
    "target_date": "2040-12-31",
    "current_savings": 500000,
    "monthly_investment_capacity": 80000
  }'
```

---

### 6. Devil's Advocate Analysis

**`POST /api/v1/ai/devils-advocate`**

Provides a critical counter-analysis for a stock or portfolio decision. The AI argues against the position, surfacing hidden risks, bearish signals, and contrarian viewpoints.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Rate Limit** | 15 requests / hour / user |

#### Request Body

```json
{
  "subject_type": "string (required) — one of: stock | portfolio | decision",
  "subject_id": "string (required) — portfolio_id, symbol, or free-text decision description",
  "bullish_thesis": "string (optional) — user's stated bullish reasoning (max 1000 chars)"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Devil's advocate analysis generated.",
  "data": {
    "subject_type": "stock",
    "subject": "ZOMATO",
    "bullish_thesis_provided": "Zomato has strong brand recall and growing order volume.",
    "counter_analysis": {
      "overall_stance": "bearish",
      "summary": "Despite brand strength, Zomato faces structural profitability challenges that the market may be mispricing.",
      "key_bear_arguments": [
        {
          "argument": "Negative Free Cash Flow",
          "detail": "Zomato continues to burn cash despite operational improvements, with FCF at -₹480Cr in Q4 FY26.",
          "severity": "high"
        },
        {
          "argument": "Intense Competition",
          "detail": "Swiggy's IPO has intensified the delivery wars with deep discounting likely to resume.",
          "severity": "high"
        },
        {
          "argument": "Premium Valuation",
          "detail": "Trading at 180x forward P/E — any growth miss will trigger a significant de-rating.",
          "severity": "medium"
        },
        {
          "argument": "Regulatory Overhang",
          "detail": "Gig worker classification laws and platform regulation bills are pending in Parliament.",
          "severity": "medium"
        }
      ],
      "risk_to_bull_case": "If quick commerce growth slows or Swiggy aggressively captures market share, Zomato's valuation premium collapses fast.",
      "recommendation": "Consider reducing position size to limit downside exposure while the profitability trajectory remains unclear."
    },
    "model": "gemini-2.0-flash",
    "tokens_used": 1680
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_SUBJECT_TYPE` | Subject type not in allowed enum |
| `400` | `VALIDATION_ERROR` | Required fields missing |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `404` | `SUBJECT_NOT_FOUND` | Portfolio or symbol not found |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/devils-advocate" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "subject_type": "stock",
    "subject_id": "ZOMATO",
    "bullish_thesis": "Zomato has strong brand recall and growing order volume."
  }'
```

---

### 7. News Explanation

**`POST /api/v1/ai/explain-news`**

Takes a financial news article and provides a plain-English explanation of what the news means, how it impacts the market or specific stocks, and what action (if any) an investor should consider.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Rate Limit** | 30 requests / hour / user |

#### Request Body

```json
{
  "news_id": "string (optional — ID from /api/v1/news/* endpoints)",
  "text": "string (optional — raw news text or headline, max 3000 chars)",
  "portfolio_id": "string (optional — to personalise impact analysis to user's holdings)"
}
```

> Either `news_id` or `text` must be provided.

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "News explanation generated.",
  "data": {
    "original_headline": "RBI holds repo rate at 6.5%; signals dovish pivot",
    "plain_english_summary": "The RBI (India's central bank) decided to keep its main interest rate unchanged at 6.5%. More importantly, they hinted they may start cutting rates in the future — this is called a 'dovish pivot'. Lower interest rates in the future are generally good for stocks, especially banks and real estate companies.",
    "market_impact": {
      "overall": "Positive for equities, especially rate-sensitive sectors.",
      "sectors_affected": [
        { "sector": "Banking & Finance", "impact": "positive", "reason": "Net interest margins stabilize; credit demand may accelerate." },
        { "sector": "Real Estate", "impact": "positive", "reason": "Lower future rates reduce home loan EMIs, boosting demand." },
        { "sector": "IT Exports", "impact": "neutral", "reason": "RBI policy has limited direct impact on IT sector." }
      ]
    },
    "portfolio_impact": {
      "portfolio_id": "pfl_01J8XYZABC123",
      "holdings_impacted": [
        { "symbol": "HDFCBANK", "impact": "positive", "detail": "Expected NIM expansion in next 2 quarters." },
        { "symbol": "TCS", "impact": "neutral", "detail": "Minimal direct exposure to domestic rate cycle." }
      ]
    },
    "suggested_actions": [
      "No immediate action required. Monitor RBI's next MPC meeting for rate cut confirmation.",
      "Consider adding HDFCBANK or ICICIBANK to benefit from anticipated rate cycle reversal."
    ],
    "confidence_level": "high",
    "model": "gemini-2.0-flash",
    "tokens_used": 980
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `MISSING_INPUT` | Neither `news_id` nor `text` was provided |
| `400` | `TEXT_TOO_LONG` | Text exceeds 3000 character limit |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `404` | `NEWS_NOT_FOUND` | `news_id` not found in the system |
| `503` | `AI_SERVICE_UNAVAILABLE` | LLM unavailable |

#### Example Request

```bash
curl -X POST "https://api.finpilot.ai/api/v1/ai/explain-news" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "news_id": "nws_01J8XYZABC123",
    "portfolio_id": "pfl_01J8XYZABC123"
  }'
```
