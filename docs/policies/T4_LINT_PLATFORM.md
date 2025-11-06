# T4 — Lint Platform Policy (v1.0)

T4 Lint Platform: treat linter findings as *first-class technical intent* and a prioritized backlog of fixes. Structured annotations in code are human-friendly; the Intent Registry is the authoritative catalog. The platform automates safe fixes, generates issues/PRs for planned work, and enforces quality rules in CI.

## Scope
Production lanes: `lukhas/`, `core/`, `api/`, `consciousness/`, `memory/`, `identity/`, `MATRIZ/`.
Excluded: `candidate/`, `labs/`, `archive/`, `quarantine/`, `.venv/`, `node_modules/`, `.git/`, `reports/`.

## Core idea
- **Annotation**: a single-line JSON inline annotation on the offending line: `TODO[T4-LINT-ISSUE]: {...}`.
- **Intent Registry**: structured DB of lint intents (status, owner, ticket, remediation plan).
- **Lifecycle**: `reserved` → `planned` → `committed` → `implemented` → `expired`.
- **Policy**: For categories requiring non-trivial refactor (e.g., F821 undefined-name), an `owner` + `ticket` is required before merging.
- **Autofix-first**: where a safe linter autofix exists (ruff/isort), run it automatically and propose PRs; only annotate if autofix is not available or if it is risky.

## Annotation schema (inline)
Example:
```python
# TODO[T4-LINT-ISSUE]: {"id":"t4-lint-01a2","code":"F821","reason":"undefined-name 'np'","suggestion":"Add import numpy as np or qualify name","owner":null,"ticket":null,"status":"reserved","created_at":"2025-10-XXT12:00:00Z"}
x = np.array([1,2,3])
```

Fields:
* `id` (required): `t4-lint-<hex>`
* `code` (required): linter code (F821, B008, SIM102, RUF012, etc.)
* `reason` (required): short description
* `suggestion` (optional): automated suggested change (or `"autofix:ruff"` when auto-fix applied)
* `owner`, `ticket` (required when status == `planned` or `committed`)
* `status` (required): `reserved|planned|committed|implemented|expired`
* `created_at`, `modified_at` timestamps populated by tools

## Policies & remediations (high level)

* `autofixable` codes (e.g., import sorting, many SIM/RUF fixes): run `ruff --fix`, `isort`, `python -m ruff` auto-fixers in CI and create PRs automatically.
* `surgical-refactor` codes (e.g., B008 default arg, RUF012 mutable-class-default): prefer scripted codemods (LibCST) that create safe PRs.
* `manual-review` codes (e.g., F821 undefined-name, B904 raise-without-from): annotate with status `reserved` and create a triage issue. If automated suggestion matches single-file pattern, propose PR with suggested fix for maintainer review.
* `education` codes (style/collapsible if): create playbooks for maintainers and optionally apply auto-simplification.

## Metrics

* Per-code counts, Annotation Quality Score, Autofix PR rate, Time-to-Implement, Staleness.

## Governance

* `reserved` items older than 30 days escalate to architecture guild.
* `planned`/`committed` require `owner` + `ticket`.
* Autofix PRs should be reviewed within 3 business days.

## Implementation notes

* Tools: `ruff`, `isort`, `libcst` (for codemods), `gh` CLI for PR automation, SQLite Intent Registry.
* Start with dry-run/autofix pipeline for 2–4 weeks.
