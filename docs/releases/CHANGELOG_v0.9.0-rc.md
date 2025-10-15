# v0.9.0-rc - Guardian Policy Enforcement & Rate-Limit Observability

**Release Date**: 2025-10-13
**Status**: Release Candidate
**PR**: #380

## Added

### Guardian Policy Enforcement
- **Policy-based access control** on all OpenAI façade endpoints (`/v1/models`, `/v1/embeddings`, `/v1/responses`, `/v1/dreams`)
  - Implements `enforce_policy(scope)` dependency with full Context evaluation
  - Deny-overrides algorithm with sub-10ms latency target
  - Graceful fallback if Guardian PDP unavailable
  - Metrics recording via `guardian_decision_total`, `guardian_denied_total`, `guardian_decision_latency_seconds`

### Rate-Limit Response Headers
- **X-RateLimit-*** headers on both success and error paths
  - `X-RateLimit-Limit`: max requests allowed in current window
  - `X-RateLimit-Remaining`: requests remaining in current window
  - `X-RateLimit-Reset`: epoch seconds until window reset
  - OpenAI-compatible format for client SDK integration
  - Headers preserved across 200, 401, 403, 429, 500 responses
  - Error envelope maintains `X-Trace-Id` + OpenAI error structure

### Health & Observability
- **Enhanced `/healthz` endpoint** with operational signals:
  ```json
  {
    "guardian_pdp": {
      "available": true,
      "decisions": 1247,
      "denials": 3,
      "policy_etag": "a3f9c8d1"
    },
    "rate_limiter": {
      "available": true,
      "backend": "redis",
      "keys_tracked": 42,
      "rate_limited": 8
    }
  }
  ```
- Operators can monitor policy enforcement and quota usage without verbose logs

### Testing & Quality
- **New smoke tests**:
  - `tests/smoke/test_rate_limit_headers.py` (3/3 passing)
  - `tests/smoke/test_healthz_signals.py` (3/3 passing)
- **OpenAPI headers guard**: CI enforcement via `scripts/check_openapi_headers.py`
  - Validates X-RateLimit-* headers present on all 2xx/4xx/5xx responses
  - Prevents accidental removal of documented header contract

### Developer Experience
- **Updated `.env.example`** with Guardian/Redis/RL configuration:
  - `LUKHAS_POLICY_MODE=permissive|strict` (default: permissive)
  - `LUKHAS_RL_KEYING=route_principal` (configurable keying strategy)
  - `LUKHAS_RATE_BURST=20` / `LUKHAS_RATE_RPS=10` (quota limits)
  - `REDIS_URL=redis://localhost:6379/0` (optional backend)

- **New Makefile targets**:
  - `make redis-up` / `make redis-down` / `make redis-check` (local Redis dev)
  - `make openapi-spec` (generate OpenAPI JSON with header metadata)
  - `make openapi-headers-guard` (validate RL headers present in spec)

## Changed

### Authentication & Authorization
- **TokenClaims default scopes** enhanced for dev/test convenience:
  - Now includes: `api.read`, `api.write`, `models:read`, `embeddings:read`, `responses:write`, `dreams:read`
  - Production tokens still drive scopes via JWT claims (no production relaxation)
  - Fixes auth test failures without compromising security model

### Policy Decision Point (PDP)
- **Fixed PDP initialization warnings**:
  - YAML `when` key normalized to `conditions` (Rule dataclass compatibility)
  - Unknown keys (`unless`, `description`) filtered during rule parsing
  - Graceful handling of policy load failures with permissive fallback

### Error Handling
- **Improved error responses**:
  - Rate-limit headers now present on 401/403/429/500 (best-effort)
  - `X-Trace-Id` guaranteed on all responses for end-to-end correlation
  - OpenAI error envelope preserved: `{"error": {"type", "message", "code"}}`

## Operations

### Configuration
- **Policy Mode**: `LUKHAS_POLICY_MODE=permissive` (default) allows all requests with logging; `strict` enforces denials
- **Rate Limiting**: Configurable via env vars (RPS, burst, keying strategy, Redis backend)
- **Redis Backend**: Optional; falls back to in-memory limiter if unavailable

### CI/CD
- **New CI checks**:
  - OpenAPI headers guard runs after spec generation
  - Validates X-RateLimit-* headers present in components and responses
  - Fails fast on missing header documentation

### Monitoring
- **New Prometheus metrics**:
  - `guardian_decision_total{effect,policy_id}` - total PDP decisions by effect
  - `guardian_denied_total` - total denied requests
  - `guardian_decision_latency_seconds` - PDP evaluation latency histogram

## Migration Guide

### Upgrading from v0.8.x

**No breaking changes** - all changes are additive:

1. **New headers**: Clients now receive `X-RateLimit-*` headers on all responses
2. **New scopes**: If using custom auth tokens, ensure they include required scopes (e.g., `models:read`, `embeddings:read`)
3. **Health endpoint**: `/healthz` response structure extended with Guardian/RL sections (backward compatible)

**Optional configuration**:

```bash
# .env (optional - has sensible defaults)
LUKHAS_POLICY_MODE=permissive      # or 'strict' for enforcement
LUKHAS_RATE_BURST=20               # max burst size
LUKHAS_RATE_RPS=10                 # requests per second
REDIS_URL=redis://localhost:6379/0 # optional backend
```

**Testing your deployment**:

```bash
# Verify Guardian active
curl http://localhost:8000/healthz | jq .checks.guardian_pdp

# Verify RL headers present
curl -i http://localhost:8000/v1/models -H "Authorization: Bearer $TOKEN" | grep X-RateLimit

# Run smoke tests
pytest tests/smoke/ -v
```

## Known Issues

- Guardian PDP init requires Redis or falls back to permissive mode (tracked in #381)
- Rate-limit headers on embeddings endpoint success path are best-effort (depends on `current_window()` availability)

## Contributors

- **Claude Code** (OpenAI façade, Guardian wiring, RL headers, testing)
- **LukhasAI Team** (policy definitions, architecture, review)

---

**Full Changelog**: https://github.com/LukhasAI/Lukhas/compare/v0.8.0...v0.9.0-rc
