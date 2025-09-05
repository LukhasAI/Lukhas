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

## Ruff per-file ignores added during CI fix (chore/ci-make-check)

- file: serve/ui/dashboard.py
	rule: I001
	reason: import-order formatting conflicts with packaging layout; short waiver to allow merge while UI import refactor is planned
	owner: @gonzalo
	added: 2025-09-05
	expires: 2025-09-12

- file: serve/extreme_performance_main.py
	rule: PLW0603,ARG001,ARG002
	reason: targeted global-usage patterns used intentionally for low-level perf probe; will be audited and narrowed later
	owner: @gonzalo
	added: 2025-09-05
	expires: 2026-03-01

- file: serve/orchestration_routes.py
	rule: PLW0603,PLR5501,ARG002
	reason: orchestration entrypoints rely on dynamic registration patterns; temporary waiver to unblock lane-local lint
	owner: @gonzalo
	added: 2025-09-05
	expires: 2026-03-01

- file: serve/storage/trace_provider.py
	rule: PLW0603
	reason: trace provider uses module-scoped singletons intentionally; will refactor to explicit factory pattern later
	owner: @gonzalo
	added: 2025-09-05
	expires: 2026-03-01
