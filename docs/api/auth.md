# Authentication API Contract

> **Base URL:** `/api/v1/auth`
> **Version:** v1
> **Last Updated:** 2026-07-29

---

## Standard Response Envelope

All API responses follow this consistent JSON envelope:

```json
{
  "success": true | false,
  "data": { ... },
  "message": "Human-readable message",
  "error": "Error detail (only on failure)",
  "meta": { "timestamp": "ISO-8601" }
}
```

---

## Endpoints

### 1. Register

**`POST /api/v1/auth/register`**

Creates a new user account in the system.

| Property | Value |
|---|---|
| **Authentication Required** | No |
| **Rate Limit** | 10 requests / hour / IP |

#### Request Body

```json
{
  "full_name": "string (required, 2–100 chars)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars, 1 uppercase, 1 digit, 1 special char)",
  "confirm_password": "string (required, must match password)"
}
```

#### Success Response `201 Created`

```json
{
  "success": true,
  "message": "Account created successfully. Please verify your email.",
  "data": {
    "user": {
      "id": "usr_01J8XYZABC123",
      "full_name": "Aryan Sharma",
      "email": "aryan@example.com",
      "is_verified": false,
      "created_at": "2026-07-29T17:30:00Z"
    }
  },
  "meta": {
    "timestamp": "2026-07-29T17:30:00Z"
  }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Missing or invalid fields |
| `409` | `EMAIL_ALREADY_EXISTS` | Email is already registered |
| `422` | `PASSWORD_MISMATCH` | Passwords do not match |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many registration attempts |

#### Error Response Example

```json
{
  "success": false,
  "error": "EMAIL_ALREADY_EXISTS",
  "message": "An account with this email already exists.",
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Example Request

```bash
curl -X POST https://api.finpilot.ai/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Aryan Sharma",
    "email": "aryan@example.com",
    "password": "SecurePass@123",
    "confirm_password": "SecurePass@123"
  }'
```

---

### 2. Login

**`POST /api/v1/auth/login`**

Authenticates a user and returns a JWT access token and refresh token.

| Property | Value |
|---|---|
| **Authentication Required** | No |
| **Rate Limit** | 20 requests / 15 min / IP |

#### Request Body

```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "usr_01J8XYZABC123",
      "full_name": "Aryan Sharma",
      "email": "aryan@example.com",
      "is_verified": true
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Missing fields |
| `401` | `INVALID_CREDENTIALS` | Email or password is incorrect |
| `403` | `ACCOUNT_NOT_VERIFIED` | Email verification pending |
| `423` | `ACCOUNT_LOCKED` | Account temporarily locked after failed attempts |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many login attempts |

#### Example Request

```bash
curl -X POST https://api.finpilot.ai/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aryan@example.com",
    "password": "SecurePass@123"
  }'
```

---

### 3. Logout

**`POST /api/v1/auth/logout`**

Invalidates the current access and refresh tokens (server-side token revocation).

| Property | Value |
|---|---|
| **Authentication Required** | Yes (Bearer Token) |

#### Request Headers

```
Authorization: Bearer <access_token>
```

#### Request Body

```json
{
  "refresh_token": "string (required)"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Logged out successfully.",
  "data": null,
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `UNAUTHORIZED` | Missing or invalid token |
| `400` | `INVALID_TOKEN` | Refresh token not provided or malformed |

#### Example Request

```bash
curl -X POST https://api.finpilot.ai/api/v1/auth/logout \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{ "refresh_token": "eyJhbGci..." }'
```

---

### 4. Refresh Token

**`POST /api/v1/auth/refresh`**

Issues a new access token using a valid refresh token.

| Property | Value |
|---|---|
| **Authentication Required** | No (uses refresh token) |
| **Rate Limit** | 30 requests / hour / user |

#### Request Body

```json
{
  "refresh_token": "string (required)"
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Token refreshed successfully.",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_TOKEN` | Token is malformed |
| `401` | `TOKEN_EXPIRED` | Refresh token has expired |
| `401` | `TOKEN_REVOKED` | Refresh token has been revoked |

#### Example Request

```bash
curl -X POST https://api.finpilot.ai/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{ "refresh_token": "eyJhbGci..." }'
```

---

### 5. Get Current User

**`GET /api/v1/auth/me`**

Returns the currently authenticated user's profile from the JWT claims.

| Property | Value |
|---|---|
| **Authentication Required** | Yes (Bearer Token) |

#### Request Headers

```
Authorization: Bearer <access_token>
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Current user retrieved.",
  "data": {
    "user": {
      "id": "usr_01J8XYZABC123",
      "full_name": "Aryan Sharma",
      "email": "aryan@example.com",
      "is_verified": true,
      "risk_preference": "moderate",
      "created_at": "2026-07-29T17:30:00Z",
      "last_login": "2026-07-29T17:30:00Z"
    }
  },
  "meta": { "timestamp": "2026-07-29T17:30:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `UNAUTHORIZED` | Token missing or invalid |
| `401` | `TOKEN_EXPIRED` | Access token has expired |

#### Example Request

```bash
curl -X GET https://api.finpilot.ai/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGci..."
```
