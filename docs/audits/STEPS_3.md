# Lukhas Audit Plan

## Overview

This document outlines the audit plan for the Lukhas project. It details the phases, objectives, and acceptance criteria to ensure code quality and project standards.

## Phases

- STEPS_1: Initial setup and configuration
- STEPS_2: Core functionality implementation
- STEPS_3: Advanced features and optimizations

## Acceptance Criteria (global)

- `pytest` green; coverage for `lukhas` ≥ target per phase (30–40% in STEPS_2; 40%+ in STEPS_3).
- Code adheres to PEP8 standards
- Documentation is complete and clear
- No critical or high severity issues remain unresolved

## Deliverables

- Test reports
- Coverage reports
- Audit summary document

## Timeline

| Phase    | Start Date | End Date   |
|----------|------------|------------|
| STEPS_1  | 2024-01-01 | 2024-01-15 |
| STEPS_2  | 2024-01-16 | 2024-02-15 |
| STEPS_3  | 2024-02-16 | 2024-03-15 |

## Notes

Please ensure all tests are run in a clean environment and results are reproducible.

# STEPS_3 — Claude Execution Script (Fix 3 Failing Tests, Coverage → 40%+, Ruff↓, MyPy↓)

> Feed this entire file to **Claude Code** in one go. Claude should PLAN → TODO → EXECUTE with small diffs (≤20 lines/file), running gates after each block and appending to `docs/audits/CLAUDE_PROGRESS.md`.

---
## 0) Assumptions
- Phase 2 finished: coverage ≈ 13%, lane guard OK, Ruff ≈ 8xx in `lukhas/**`, MyPy ≈ 7xx.
- You have: `ruff.toml`, `mypy.ini`, `.coveragerc`, `pytest.ini` (now with `--cov-fail-under=40`), `.pre-commit-config.yaml`, `linter.ini`.
- Stable lanes: `lukhas/**` (primary), `serve/**` (as needed). Non‑stable: `candidate/**`, `enterprise/**`, `tools/**`.

## Output protocol
1) Start with a brief PLAN + numbered TODO.
2) For each block: list files changed and show minimal diffs (≤20 lines/file).
3) After each block: run the gate command(s) and paste the last 30 lines.
4) Append a row in `docs/audits/CLAUDE_PROGRESS.md`: Timestamp · Task · Files changed · Gate result.
5) End with a single JSON line (see Block 5).

---
## BLOCK 1 — Fix the 3 failing tests (fast triage, minimal edits)
**Goal:** Bring tests to green (0 failed). No refactors; surgical fixes only.

Steps:
- Run: `pytest -q -x` (stop at first failure); paste last 30 lines.
- For each failure:
  - If import/path: add missing `__init__.py`, or ensure `tests/conftest.py` inserts repo root to `sys.path`.
  - If fixture missing: create a small local fixture in the failing test file.
  - If time/UTC: enforce `datetime.now(timezone.utc)` and import `timezone`.
  - If secrets: replace with `os.getenv("TEST_*", "dummy")`.
  - Keep each file diff ≤20 lines.
- Repeat until 0 failed.

**Gate:** `pytest -q` → all tests pass.

---
## BLOCK 2 — Coverage boost to ≥40% (tiny, deterministic tests)
**Goal:** Add small tests that touch uncovered stable paths (no I/O, no network); ≤30 lines/test.

Create/extend:
1) `tests/core/test_exceptions_paths.py` — exercise both None and non‑None branches in exceptions utilities.
2) `tests/governance/test_policies_defaults.py` — empty/default policy decisions are deterministic and non‑crashing.
3) `tests/bridge/test_branding_imports.py` — import `lukhas/branding_bridge.py` and call one pure function to cover long‑line wrapped code.
4) `tests/bio/test_bio_symbolic_tz.py` — ensure UTC timestamp creation via `datetime.now(timezone.utc)` on at least one stable path.

**Gate:**  
`pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-fail-under=40 -q`

**Acceptance:** `coverage_stable ≥ 40%` (gate enforced) and tests remain green.

---
## BLOCK 3 — Ruff reduction in `lukhas/**` (target −300)
**Goal:** Drop Ruff errors by ~300 focusing on high-yield codes; no broad refactors.

- BEFORE snapshot: run `ruff check lukhas --statistics` and record the total & top codes in `docs/audits/CLAUDE_PROGRESS.md`.
- Apply patterns:
  - `ANN201/ANN204` → add return annotations (`-> None` if no return), add minimal arg types (`str`, `int`, `dict[str, Any]`), import `Any`.
  - `DTZ005` → replace `datetime.now()` with `datetime.now(timezone.utc)`; add `from datetime import timezone`.
  - `PLC0415` → move inner imports to top; use `try/except ImportError` at top and guard usage.
  - `RUF022` → sort `__all__` lists lexicographically.
  - `E501` → line‑length is 120; wrap remaining offenders with parentheses.
- Keep each file diff ≤20 lines; batch multiple files.

**Gate:**  
Run `ruff check lukhas --statistics` again (AFTER). Paste the summary and explicitly note the delta vs BEFORE.

---
## BLOCK 4 — MyPy targeted clean (runtime‑risk first)
**Goal:** Reduce real risk; don’t chase every aesthetic warning.

Steps:
- Run: `mypy lukhas` and list the first 20 errors.
- Fix categories:
  - Optional arithmetic/attrs: guard `None` before use; tighten types where obvious.
  - Incompatible assignment (`list[str]` vs `None`): init to `[]` or use `Optional[list[str]]` + guard.
  - Missing third‑party types: prefer `types-*` stubs; only use `# type: ignore[...]` for unavoidable cases.
- Limit changes ≤20 lines/file.

**Gate:**  
`mypy lukhas` — paste last 30 lines; expect a noticeable reduction.

---
## BLOCK 5 — Final gates & status line
Run in order:
```bash
ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
mypy lukhas
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-fail-under=40 -q
lint-imports --config=linter.ini
ruff check .
```

Output a single JSON line:
```
{ "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool> }
```
Then list changed files (no diffs) and append the status to `docs/audits/CLAUDE_PROGRESS.md`.

---
## Guardrails (T4)
- Keep edits ≤20 lines/file; split across files.
- Prefer `Optional[...]` + guard over signature refactors.
- Maintain UTC policy consistently.
- Avoid adding heavy test fixtures; keep tests deterministic and fast.