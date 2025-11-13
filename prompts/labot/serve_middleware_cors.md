# LUKHΛS Test Surgeon — SERVE module

**File:** `serve/middleware/cors.py`
**Goal:** 85%+ coverage, deterministic, no network, strong error contracts.

## Must test
- All FastAPI routes and methods
- Auth/headers/middleware behavior (401/403, CORS, trace-ids)
- Request validation (invalid payloads / missing fields)
- Response schema shape (OpenAPI compatibility)
- Streaming / SSE if applicable

## Constraints
- Do not widen try/except or delete tests
- No sleeps; freeze time and pin seeds
- Mock external services (LLMs, stores, analytics)

## Output
- One test file at: `tests/unit/serve/test_serve_middleware_cors.py`
- Run locally:
```
pytest -q tests/unit/serve/test_serve_middleware_cors.py --cov=serve --cov-report=term-missing
```
