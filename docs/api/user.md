# User API Contract

> **Base URL:** `/api/v1/users`
> **Version:** v1
> **Authentication:** All endpoints require `Authorization: Bearer <token>` unless stated otherwise.
> **Last Updated:** 2026-07-29

---

## Standard Response Envelope

```json
{
  "success": true | false,
  "data": { ... },
  "message": "Human-readable message",
  "error": "Error code (on failure only)",
  "meta": { "timestamp": "ISO-8601" }
}
```

---

## Endpoints

### 1. Get Profile

**`GET /api/v1/users/me/profile`**

Returns the full profile of the currently authenticated user.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Request Headers

```
Authorization: Bearer <access_token>
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "User profile retrieved.",
  "data": {
    "profile": {
      "id": "usr_01J8XYZABC123",
      "full_name": "Aryan Sharma",
      "email": "aryan@example.com",
      "phone": "+91-9876543210",
      "avatar_url": "https://cdn.finpilot.ai/avatars/usr_01J8XYZABC123.jpg",
      "date_of_birth": "1999-05-15",
      "country": "IN",
      "currency": "INR",
      "risk_preference": "moderate",
      "investment_goals": ["wealth_growth", "retirement"],
      "is_verified": true,
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
| `401` | `UNAUTHORIZED` | Token missing, invalid, or expired |
| `404` | `PROFILE_NOT_FOUND` | User profile not found |

#### Example Request

```bash
curl -X GET https://api.finpilot.ai/api/v1/users/me/profile \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### 2. Update Profile

**`PATCH /api/v1/users/me/profile`**

Updates one or more fields of the authenticated user's profile. All fields are optional.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Request Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body (all fields optional)

```json
{
  "full_name": "string (2–100 chars)",
  "phone": "string (E.164 format, e.g. +919876543210)",
  "date_of_birth": "string (YYYY-MM-DD)",
  "country": "string (ISO 3166-1 alpha-2, e.g. IN)",
  "currency": "string (ISO 4217, e.g. INR)",
  "investment_goals": ["wealth_growth", "retirement", "emergency_fund", "education"]
}
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Profile updated successfully.",
  "data": {
    "profile": {
      "id": "usr_01J8XYZABC123",
      "full_name": "Aryan K. Sharma",
      "phone": "+91-9876543210",
      "country": "IN",
      "currency": "INR",
      "updated_at": "2026-07-29T17:35:00Z"
    }
  },
  "meta": { "timestamp": "2026-07-29T17:35:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Invalid field values |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `409` | `NO_CHANGES_DETECTED` | Request body matches existing data |

#### Example Request

```bash
curl -X PATCH https://api.finpilot.ai/api/v1/users/me/profile \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Aryan K. Sharma",
    "currency": "INR"
  }'
```

---

### 3. Update Risk Preference

**`PUT /api/v1/users/me/risk-preference`**

Sets the user's investment risk tolerance level. Used by the AI engine for personalized recommendations.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |

#### Request Body

```json
{
  "risk_preference": "string (required, one of: conservative | moderate | aggressive)"
}
```

#### Risk Levels Explained

| Value | Description |
|---|---|
| `conservative` | Prefers capital preservation; low-risk instruments (bonds, FDs) |
| `moderate` | Balanced approach; mix of equities and debt |
| `aggressive` | Seeks high returns; comfortable with high-risk equities, crypto |

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Risk preference updated.",
  "data": {
    "user_id": "usr_01J8XYZABC123",
    "risk_preference": "aggressive",
    "updated_at": "2026-07-29T17:35:00Z"
  },
  "meta": { "timestamp": "2026-07-29T17:35:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_RISK_LEVEL` | Value not in allowed enum |
| `401` | `UNAUTHORIZED` | Token invalid or expired |

#### Example Request

```bash
curl -X PUT https://api.finpilot.ai/api/v1/users/me/risk-preference \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{ "risk_preference": "aggressive" }'
```

---

### 4. Delete Account

**`DELETE /api/v1/users/me`**

Permanently deletes the authenticated user's account and all associated data. This action is irreversible.

| Property | Value |
|---|---|
| **Authentication Required** | Yes |
| **Confirmation Required** | Yes (via request body) |

#### Request Body

```json
{
  "password": "string (required — current password to confirm identity)",
  "confirmation": "DELETE_MY_ACCOUNT"
}
```

> **⚠️ Warning:** This is a hard delete. All portfolios, preferences, AI history, and personal data are permanently erased.

#### Success Response `200 OK`

```json
{
  "success": true,
  "message": "Account permanently deleted. We are sorry to see you go.",
  "data": {
    "deleted_user_id": "usr_01J8XYZABC123",
    "deleted_at": "2026-07-29T17:40:00Z"
  },
  "meta": { "timestamp": "2026-07-29T17:40:00Z" }
}
```

#### Error Responses

| Status | Code | Description |
|---|---|---|
| `400` | `INVALID_CONFIRMATION` | Confirmation string does not match |
| `401` | `UNAUTHORIZED` | Token invalid or expired |
| `401` | `INVALID_CREDENTIALS` | Password is incorrect |

#### Example Request

```bash
curl -X DELETE https://api.finpilot.ai/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "password": "SecurePass@123",
    "confirmation": "DELETE_MY_ACCOUNT"
  }'
```
