# RFC-0008 — Multi-Tenant Quotas (hierarchical)

**Problem:** current limiter isolates `{route}:{principal}`; add **org-level ceilings**, burst smoothing, and formal headers.
**Design:**

* **Hierarchy:** org → token → route
* **Algo:** sliding-window or token-bucket; per-key bucket with burst `B`, rate `R/s`.
* **Config:** `configs/quotas.yaml`
* **Decision:** effective limit is **min(org, token, route)** at check time.
* **Headers:**

  * `X-RateLimit-Limit: <limit>`
  * `X-RateLimit-Remaining: <remaining>`
  * `X-RateLimit-Reset: <unix_epoch_seconds>`
* **OTEL:** `rl.key`, `rl.remaining`, `rl.limited=true/false`.
