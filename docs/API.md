# API Specification

## Base URL

```
Production:  https://api.yourdomain.com
Development: http://localhost:8000
```

---

## Authentication

All endpoints require a Bearer token in the `Authorization` header unless noted otherwise.

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Audio Streaming (WebSocket)

**`WS /api/v1/audio/stream`**

Real-time audio streaming for speech-to-text transcription and AI processing.

#### Connection

```
ws://localhost:8000/api/v1/audio/stream?token=<access_token>
```

#### Client → Server Messages

| Field | Type | Description |
|---|---|---|
| `type` | string | `"audio_chunk"` or `"end_stream"` |
| `data` | string (base64) | Raw audio chunk (PCM 16-bit, 16kHz, mono) |
| `session_id` | string | Unique session identifier |

```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio...",
  "session_id": "sess_abc123"
}
```

#### Server → Client Messages

**Partial transcription:**
```json
{
  "type": "transcription_partial",
  "text": "satu nasi goreng",
  "is_final": false
}
```

**Resolved order:**
```json
{
  "type": "order_resolved",
  "order": {
    "session_id": "sess_abc123",
    "items": [
      {
        "product_id": 42,
        "sku": "FOOD-NG-001",
        "name": "Nasi Goreng Spesial",
        "quantity": 1,
        "unit_price": 25000,
        "subtotal": 25000
      }
    ],
    "total": 25000,
    "odoo_order_id": null,
    "status": "draft"
  }
}
```

**Error:**
```json
{
  "type": "error",
  "code": "STT_TIMEOUT",
  "message": "Speech-to-text engine timed out"
}
```

---

### 2. Create Draft Order

**`POST /api/v1/orders`**

Creates a draft sales order in Odoo from resolved items.

#### Request Body

```json
{
  "session_id": "sess_abc123",
  "items": [
    {
      "product_id": 42,
      "quantity": 1
    },
    {
      "product_id": 15,
      "quantity": 2
    }
  ],
  "customer_email": "customer@example.com"
}
```

#### Response — `201 Created`

```json
{
  "order_id": "ORD-2026-0001",
  "odoo_order_id": 1847,
  "status": "draft",
  "items": [
    {
      "product_id": 42,
      "sku": "FOOD-NG-001",
      "name": "Nasi Goreng Spesial",
      "quantity": 1,
      "unit_price": 25000,
      "subtotal": 25000
    },
    {
      "product_id": 15,
      "sku": "DRINK-ET-003",
      "name": "Es Teh Manis",
      "quantity": 2,
      "unit_price": 8000,
      "subtotal": 16000
    }
  ],
  "total": 41000,
  "created_at": "2026-09-25T12:30:00Z"
}
```

---

### 3. Update Order

**`PATCH /api/v1/orders/{order_id}`**

Updates an existing draft order (add/remove/modify items).

#### Request Body

```json
{
  "items": [
    {
      "product_id": 42,
      "quantity": 2
    }
  ]
}
```

#### Response — `200 OK`

Returns the updated order object (same schema as Create).

---

### 4. Confirm & Pay Order

**`POST /api/v1/orders/{order_id}/confirm`**

Validates payment and triggers post-payment workflows.

#### Request Body

```json
{
  "payment_method": "qris",
  "payment_reference": "TXN-20260925-001",
  "amount": 41000
}
```

#### Response — `200 OK`

```json
{
  "order_id": "ORD-2026-0001",
  "status": "confirmed",
  "payment": {
    "method": "qris",
    "reference": "TXN-20260925-001",
    "status": "success"
  },
  "post_payment": {
    "inventory_deducted": true,
    "accounting_logged": true,
    "kitchen_printed": true,
    "email_sent": true
  },
  "confirmed_at": "2026-09-25T12:31:15Z"
}
```

---

### 5. Get Order Details

**`GET /api/v1/orders/{order_id}`**

#### Response — `200 OK`

Returns the full order object with current status.

---

### 6. List Orders

**`GET /api/v1/orders`**

#### Query Parameters

| Param | Type | Default | Description |
|---|---|---|---|
| `status` | string | `all` | Filter: `draft`, `confirmed`, `cancelled` |
| `date_from` | string (ISO) | — | Start date filter |
| `date_to` | string (ISO) | — | End date filter |
| `limit` | int | 50 | Page size |
| `offset` | int | 0 | Pagination offset |

---

### 7. Health Check

**`GET /api/v1/health`** *(no auth required)*

```json
{
  "status": "healthy",
  "services": {
    "stt": "up",
    "ai_agent": "up",
    "vector_db": "up",
    "odoo": "up"
  },
  "version": "1.0.0"
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|---|---|---|
| `AUTH_INVALID` | 401 | Invalid or expired token |
| `ORDER_NOT_FOUND` | 404 | Order ID does not exist |
| `ORDER_ALREADY_CONFIRMED` | 409 | Cannot modify a confirmed order |
| `PAYMENT_FAILED` | 402 | Payment processing failed |
| `STT_TIMEOUT` | 504 | STT engine did not respond in time |
| `ODOO_UNREACHABLE` | 502 | Cannot connect to Odoo instance |
| `RAG_NO_MATCH` | 422 | Could not match spoken items to products |

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| WebSocket connections | 100 concurrent per instance |
| REST endpoints | 1000 req/min per token |
