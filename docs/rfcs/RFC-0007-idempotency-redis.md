# RFC-0007 — Redis Idempotency Backend

**Problem:** in-memory cache breaks across replicas; need exactly-once semantics across pods.
**Design:**

* **Key:** `idem:{route}:{tenant}:{idempotency_key}`
* **Value:** JSON { status_code, headers (filtered), body_sha256, created_at, ttl }
* **TTL:** default 300s; configurable `LUKHAS_IDEM_TTL`
* **Dedup Rule:** match `(route, idem_key, tenant)` → return stored response iff **same body hash** (to avoid **accidental replay with different body**). Emit 409 if body differs (configurable).
* **Headers persisted:** `X-Trace-Id`, `Content-Type`, `Cache-Control`, `Idempotency-Key`, rate-limit headers.
* **OTEL:** attributes `idem.hit`, `idem.key`, `idem.ttl_remaining`.
* **Fallback:** in-mem when `LUKHAS_IDEM_BACKEND=memory`.
