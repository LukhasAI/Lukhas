# LUKHAS Core Wiring API Documentation

## Overview

Production API endpoints for consciousness, dreams, glyphs, and drift monitoring functionality. All endpoints are feature-flag gated and disabled by default for safety.

**Base URL**: `https://api.lukhas.ai` (production) or `http://localhost:8000` (development)

## Feature Flags

All endpoints require their respective feature flags to be enabled:

| Feature | Flag | Default | Required For |
|---------|------|---------|-------------|
| Dreams | `LUKHAS_DREAMS_ENABLED=1` | OFF | `/api/v1/dreams/*` |
| Parallel Dreams | `LUKHAS_PARALLEL_DREAMS=1` | OFF | `/api/v1/dreams/mesh` |
| GLYPHs | `LUKHAS_GLYPHS_ENABLED=1` | OFF | `/api/v1/glyphs/*` |
| Drift | `LUKHAS_DRIFT_ENABLED=1` | OFF | `/api/v1/drift/*` |

## Authentication

Most endpoints require Bearer token authentication:

```http
Authorization: Bearer YOUR_TOKEN_HERE
```

## Dreams API

### POST /api/v1/dreams/simulate

Simulate a dream based on seed and context.

**Requires**: `LUKHAS_DREAMS_ENABLED=1`

**Request Body**:
```json
{
  "seed": "morning_reflection",
  "context": {
    "mood": "calm",
    "time": "06:00"
  },
  "parallel": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "dream_id": "dream_abc123",
  "seed": "morning_reflection",
  "result": {
    "status": "simulated",
    "mode": "sequential",
    "context": {
      "mood": "calm",
      "time": "06:00"
    }
  },
  "metadata": {
    "timestamp": 1699564800.123,
    "engine_version": "0.1.0-alpha"
  }
}
```

**Error Responses**:
- `503`: Dreams subsystem not enabled
- `403`: Parallel dreams not enabled (if `parallel: true`)
- `500`: Simulation failed

---

### POST /api/v1/dreams/mesh

Run parallel dream mesh with multiple seeds and consensus.

**Requires**: `LUKHAS_DREAMS_ENABLED=1` AND `LUKHAS_PARALLEL_DREAMS=1`

**Request Body**:
```json
{
  "seeds": [
    "morning_gratitude",
    "evening_reflection",
    "midday_clarity"
  ],
  "consensus_threshold": 0.7
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "mesh_id": "mesh_1699564800",
  "seeds": ["morning_gratitude", "evening_reflection", "midday_clarity"],
  "consensus_threshold": 0.7,
  "dreams": [],
  "consensus": null,
  "metadata": {
    "timestamp": 1699564800.456,
    "mode": "parallel_mesh"
  }
}
```

**Error Responses**:
- `503`: Dreams subsystem not enabled
- `403`: Parallel dreams not enabled
- `500`: Mesh processing failed

---

### GET /api/v1/dreams/{dream_id}

Retrieve a dream by its ID.

**Requires**: `LUKHAS_DREAMS_ENABLED=1`

**Response** (200 OK):
```json
{
  "dream_id": "dream_abc123",
  "seed": "morning_reflection",
  "result": {...},
  "metadata": {...}
}
```

**Error Responses**:
- `503`: Dreams subsystem not enabled
- `404`: Dream not found
- `500`: Retrieval failed

---

### GET /api/v1/dreams/

Health check endpoint.

**Response** (200 OK):
```json
{
  "service": "dreams",
  "wrapper_available": true,
  "enabled": true,
  "parallel_enabled": false,
  "version": "0.1.0-alpha"
}
```

---

## GLYPHs API

### POST /api/v1/glyphs/encode

Encode a concept into a Universal Symbol GLYPH.

**Requires**: `LUKHAS_GLYPHS_ENABLED=1`

**Request Body**:
```json
{
  "concept": "morning_gratitude",
  "emotion": {
    "joy": 0.8,
    "calm": 0.6
  },
  "modalities": ["TEXT", "SYMBOL"],
  "domains": ["UNIVERSAL"],
  "source_module": "daily_reflection"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "symbol": {
    "concept": "morning_gratitude",
    "symbol_id": "sym_xyz789",
    "modalities": ["TEXT", "SYMBOL"],
    "domains": ["UNIVERSAL"],
    "emotion": {
      "joy": 0.8,
      "calm": 0.6
    },
    "source_module": "daily_reflection"
  }
}
```

**Error Responses**:
- `503`: GLYPHs subsystem not enabled
- `400`: Invalid request (emotion out of range, etc.)
- `500`: Encoding failed

---

### POST /api/v1/glyphs/bind

Bind a GLYPH to a memory with authorization checks.

**Requires**: `LUKHAS_GLYPHS_ENABLED=1`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN_HERE (optional)
```

**Request Body**:
```json
{
  "glyph_data": {
    "concept": "important_insight",
    "emotion": {
      "joy": 0.7
    }
  },
  "memory_id": "mem_abc123",
  "user_id": "user_xyz"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "binding_id": "bind_def456",
  "glyph_data": {
    "concept": "important_insight",
    "emotion": {"joy": 0.7}
  },
  "memory_id": "mem_abc123",
  "user_id": "user_xyz",
  "timestamp": 1699564800.789
}
```

**Error Responses**:
- `503`: GLYPHs subsystem not enabled
- `400`: Invalid GLYPH data (missing concept, invalid emotion, etc.)
- `500`: Binding failed

---

### GET /api/v1/glyphs/bindings/{binding_id}

Retrieve a GLYPH binding by ID.

**Requires**: `LUKHAS_GLYPHS_ENABLED=1`

**Response** (200 OK):
```json
{
  "binding_id": "bind_def456",
  "glyph_data": {...},
  "memory_id": "mem_abc123",
  "user_id": "user_xyz",
  "timestamp": 1699564800.789
}
```

**Error Responses**:
- `503`: GLYPHs subsystem not enabled
- `404`: Binding not found
- `500`: Retrieval failed

---

### POST /api/v1/glyphs/validate

Validate GLYPH data structure and content.

**Note**: This endpoint does NOT require `LUKHAS_GLYPHS_ENABLED`.

**Request Body**:
```json
{
  "glyph_data": {
    "concept": "test",
    "emotion": {
      "joy": 0.5
    }
  }
}
```

**Response** (200 OK):
```json
{
  "valid": true,
  "error": null
}
```

Or if invalid:
```json
{
  "valid": false,
  "error": "Emotion value 'joy' must be between 0.0 and 1.0"
}
```

---

### GET /api/v1/glyphs/stats

Get GLYPH subsystem statistics.

**Requires**: `LUKHAS_GLYPHS_ENABLED=1`

**Response** (200 OK):
```json
{
  "enabled": true,
  "available": true,
  "stats": {
    "glyphs_created": 42,
    "symbols_translated": 38,
    "cross_module_links": 15,
    "compression_ratio": 0.85
  }
}
```

---

### GET /api/v1/glyphs/

Health check endpoint.

**Response** (200 OK):
```json
{
  "service": "glyphs",
  "wrapper_available": true,
  "enabled": true,
  "version": "0.1.0-alpha"
}
```

---

## Drift Monitoring API

### POST /api/v1/drift/update

Update drift monitoring with new intent/action pair.

**Requires**: `LUKHAS_DRIFT_ENABLED=1`

**Request Body**:
```json
{
  "user_id": "user_123",
  "intent": [1.0, 0.0, 0.5],
  "action": [0.9, 0.1, 0.4],
  "lane": "experimental"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "user_id": "user_123",
  "drift": 0.123,
  "ema": 0.089,
  "guardian": "allow",
  "lane": "experimental",
  "timestamp": 1699564800.123
}
```

**Guardian Status**:
- `allow`: Drift below warning threshold
- `warn`: Drift above warning threshold
- `block`: Drift above blocking threshold

**Error Responses**:
- `503`: Drift subsystem not enabled
- `400`: Vector length mismatch
- `500`: Update failed

---

### GET /api/v1/drift/{user_id}

Get current drift score for a user.

**Requires**: `LUKHAS_DRIFT_ENABLED=1`

**Response** (200 OK):
```json
{
  "user_id": "user_123",
  "drift_ema": 0.089,
  "guardian_status": "allow",
  "lane": "experimental",
  "sample_count": 42,
  "last_updated": 1699564800.123
}
```

**Error Responses**:
- `503`: Drift subsystem not enabled
- `404`: No drift data for user
- `500`: Retrieval failed

---

### GET /api/v1/drift/{user_id}/trends

Get drift trend history for a user.

**Requires**: `LUKHAS_DRIFT_ENABLED=1`

**Query Parameters**:
- `limit` (default: 100): Number of history entries to return
- `offset` (default: 0): Offset for pagination

**Response** (200 OK):
```json
{
  "user_id": "user_123",
  "lane": "experimental",
  "history": [
    {
      "drift": 0.123,
      "ema": 0.089,
      "guardian": "allow",
      "lane": "experimental",
      "timestamp": 1699564800.123,
      "user_id": "user_123"
    },
    ...
  ],
  "stats": {
    "total_samples": 150,
    "returned_samples": 100,
    "offset": 0,
    "limit": 100,
    "current_ema": 0.089,
    "avg_drift": 0.112,
    "max_drift": 0.345,
    "min_drift": 0.001,
    "avg_ema": 0.095,
    "warn_count": 5,
    "block_count": 0
  }
}
```

**Error Responses**:
- `503`: Drift subsystem not enabled
- `404`: No drift history for user
- `500`: Retrieval failed

---

### GET /api/v1/drift/config/{lane}

Get drift configuration for a specific lane.

**Note**: This endpoint does NOT require `LUKHAS_DRIFT_ENABLED`.

**Lanes**: `experimental`, `candidate`, `prod`

**Response** (200 OK):
```json
{
  "lane": "experimental",
  "warn_threshold": 0.30,
  "block_threshold": 0.50,
  "alpha": 0.2,
  "window": 64
}
```

**Error Responses**:
- `404`: Unknown lane
- `500`: Retrieval failed

---

### GET /api/v1/drift/

Health check endpoint.

**Response** (200 OK):
```json
{
  "service": "drift",
  "enabled": true,
  "available": true,
  "active_monitors": 3,
  "total_history_entries": 450,
  "version": "2.0.0"
}
```

---

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `403 Forbidden`: Feature not enabled or insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Subsystem not enabled

---

## Rate Limiting

All endpoints include rate limiting headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1699564860
```

---

## OpenAPI/Swagger Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Testing Examples

### cURL Examples

```bash
# Simulate a dream
curl -X POST http://localhost:8000/api/v1/dreams/simulate \
  -H "Content-Type: application/json" \
  -d '{"seed": "test", "context": {"mood": "calm"}}'

# Encode a GLYPH
curl -X POST http://localhost:8000/api/v1/glyphs/encode \
  -H "Content-Type: application/json" \
  -d '{"concept": "gratitude", "emotion": {"joy": 0.8}}'

# Update drift
curl -X POST http://localhost:8000/api/v1/drift/update \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "intent": [1.0, 0.0], "action": [0.9, 0.1]}'

# Get drift score
curl http://localhost:8000/api/v1/drift/user_123
```

### Python Examples

```python
import requests

# Simulate a dream
response = requests.post(
    "http://localhost:8000/api/v1/dreams/simulate",
    json={"seed": "test", "context": {"mood": "calm"}}
)
dream = response.json()

# Encode a GLYPH
response = requests.post(
    "http://localhost:8000/api/v1/glyphs/encode",
    json={"concept": "gratitude", "emotion": {"joy": 0.8}}
)
symbol = response.json()

# Update drift
response = requests.post(
    "http://localhost:8000/api/v1/drift/update",
    json={
        "user_id": "user_123",
        "intent": [1.0, 0.0],
        "action": [0.9, 0.1]
    }
)
drift_result = response.json()
```

---

## Related Documentation

- [Wrapper Modules](../wrappers/WRAPPER_MODULES.md)
- [Feature Flags Guide](../operations/FEATURE_FLAGS.md)
- [Core Architecture](../../labs/core/README.md)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/LukhasAI/Lukhas/issues
- Documentation: https://docs.lukhas.ai
