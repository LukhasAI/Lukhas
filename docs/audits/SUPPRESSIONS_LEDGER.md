# Suppressions ledger

This ledger records intentional lint/analysis suppressions, rationale, owner, and expiry.

## PERF203 - import-time probe pattern (serve/main.py)

- file: serve/main.py
	rule: PERF203
	reason: lightweight import-only probe for voice readiness
	owner: @gonzalo
	line: 128
	added: 2025-09-04
	expires: 2026-03-01
