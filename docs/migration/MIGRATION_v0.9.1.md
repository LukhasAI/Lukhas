# Migration Guide: v0.9.1

This guide details the changes introduced in version 0.9.1, focusing on the new Redis-based idempotency backend.

## Idempotency Backend

To enhance reliability and support multi-replica deployments, a new Redis-based idempotency store has been introduced. This replaces the previous in-memory-only implementation.

### Configuration Flags

Two new environment variables are available to configure the idempotency backend:

- `LUKHAS_IDEM_BACKEND`: Specifies the backend to use.
  - `redis`: (Default) Uses the new Redis-based store. Requires a running Redis instance.
  - `memory`: Falls back to the previous in-memory store. Suitable for local development or single-replica deployments.

- `LUKHAS_IDEM_TTL`: The time-to-live for idempotency keys, in seconds.
  - Default: `300` (5 minutes)

### New 409 Conflict Error Behavior

To prevent accidental replay of idempotent requests with different payloads, the system now performs a body hash comparison.

If a request is received with an `Idempotency-Key` that has already been used, but the request body is different from the original request, the server will respond with an HTTP `409 Conflict` error with the error type `idempotency_key_reuse`.

This ensures that clients cannot accidentally change the outcome of an operation by reusing an idempotency key with a new request body.
