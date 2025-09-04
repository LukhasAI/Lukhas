# Suppressions ledger

This ledger records intentional lint/analysis suppressions, rationale, owner, and expiry.

## PERF203 - import-time probe pattern (serve/main.py)

- Owner: @lukhas-dev
- Rationale: The `/healthz` endpoint uses a lightweight, import-only probe to check presence of optional voice subsystems without triggering heavy initialization or side effects. The pattern intentionally catches broad ImportError/Exception to keep the probe safe and fast in minimal environments.
- Files: `serve/main.py`
- Suppression added: 2025-09-04
- Expires: 2026-03-01
