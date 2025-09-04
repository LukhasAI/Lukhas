# Suppressions ledger

This ledger records intentional lint/analysis suppressions, rationale, owner, and expiry.

## PERF203 - import-time probe pattern (serve/main.py)

- Owner: @lukhas-dev
- Rationale: The `/healthz` endpoint uses a lightweight, import-only probe to check presence of optional voice subsystems without triggering heavy initialization or side effects. The pattern intentionally catches broad ImportError/Exception to keep the probe safe and fast in minimal environments.
- Files: `serve/main.py`
- Suppression added: 2025-09-04
- Expires: 2026-03-01

---

- file: serve/main.py
	rule: PERF203
	reason: lightweight import-only health probe for voice readiness; avoids heavy imports & side effects
	owner: @gonzalo
	added: 2025-09-04
	expires: 2026-03-01
