---
status: wip
type: documentation
owner: unknown
module: audits
redirect: false
moved_to: null
---

<!-- Auditable ledger for temporary lint/test waivers. Each entry must include: file, rule, justification, approver, date, and duration. -->
# SUPPRESSIONS LEDGER

This file records short, auditable waivers for linter/test rules that are temporarily suppressed
to unblock merges or CI runs. Entries are small, explicit, and time-limited. Do NOT use this as
an excuse for permanent suppressions — create a proper code change or documented exception instead.

Format (one entry per line, YAML-like):

- file: "serve/ui/dashboard.py"
  rule: "I001"
  justification: "Accept project-local import order for UI bundle to reduce churn; will follow up with standardized isort run in next sprint."
  approver: "team-lead@example.com"
  date: "2025-09-05"
  expires: "2025-10-05"

Add new entries by creating a PR that updates this file. CI requires a SUPPRESSIONS_LEDGER entry for any
per-file ignore added to pyproject.toml's [tool.ruff.lint.per-file-ignores]. The ledger ensures waivers are
short-lived and auditable.
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

- file: tests/core/test_matriz_consciousness_integration.py
	rule: W291,W292,W293
	reason: Generated/multi-line test file contains trailing/blank-line whitespace; low-risk. Will clean in follow-up.
	owner: @gonzalo
	added: 2025-09-05
	expires: 2025-12-01
