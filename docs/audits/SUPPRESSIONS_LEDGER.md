# Suppressions ledger

This ledger records intentional lint/analysis suppressions, rationale, owner, and expiry.

## PERF203 - import-time probe pattern (serve/main.py)

	rule: PERF203
	reason: lightweight import-only probe for voice readiness
	owner: @gonzalo
	line: 128
	added: 2025-09-04
	expires: 2026-03-01

- file: serve/ui/dashboard.py
	rule: E501,W291
	reason: Inline HTML/CSS in template; to be refactored later
	owner: @gonzalo
	added: 2025-09-04
	expires: 2026-03-01
