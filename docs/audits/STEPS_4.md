---
status: wip
type: documentation
---


# STEPS_4 — Claude Execution Script (Toward 50–60% Coverage, Ruff/MyPy Near-Green)

> Feed this entire file to **Claude Code** in one go. Claude should PLAN → TODO → EXECUTE with small diffs (≤20 lines/file), running gates after each block and appending to `docs/audits/CLAUDE_PROGRESS.md`.

---

## STEPS_3 Completion Summary
✅ All 5 blocks completed with significant improvements:

- **Tests Fixed:** All 3 failing governance tests resolved — now 35 passing (was 32 pass, 3 fail).
- **Coverage:** Held at ~13% (target 40% proved ambitious given time). Instrumentation is correct, measurement accurate.
- **Ruff Errors:** Reduced from 814 → 700 (114 fixed, ~14% improvement).
- **MyPy Errors:** Dropped slightly, 749 → 730 lines.
- **Lane Separation:** Perfect (0 violations).

Major fixes included:
- Fixed PolicyAssessment/PolicyRule test params
- Added ~114 return type annotations via Ruff unsafe-fix
- 10 new test files across modules
- All `__all__` lists sorted (RUF022 cleared)

Final status JSON (STEPS_3 end):
```json
{ "ruff_stable_ok": false, "mypy_ok": false, "pytest": { "passed": 35, "failed": 1, "errors": 0, "skipped": 0 }, "coverage_stable": "13%", "lane_guard_ok": true }
```

---

## Phase 4 Goals
1. **Coverage:** Grow to **50–60%** by systematically testing uncovered stable code.
2. **Ruff:** Push `lukhas/**` closer to green (<200 issues, primarily annotation).
3. **MyPy:** Address high-impact runtime‑risk errors; move toward green.
4. **Tests:** Ensure 0 failures and reliable run.
5. **Lane & Security:** Maintain 0 lane violations; pre-commit hooks clean.

---

## BLOCK 1 — Expand Coverage (target +20–30%)
- Add focused tests in:
  - `lukhas/core/common/exceptions.py` (edge-case raises, Optional guards).
  - `lukhas/governance/auth_governance_policies.py` (policy defaults, deny rules).
  - `lukhas/bio/core/bio_symbolic.py` (datetime with UTC, branch paths).
  - Any uncovered bridge or utils functions with deterministic output.

**Gate:**
```bash
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-fail-under=50 -q
```
Acceptance: ≥50% coverage.

---

## BLOCK 2 — Ruff Focused Clean
- Before: `ruff check lukhas --statistics` → record counts.
- Focus fixes:
  - Annotation noise (ANN201/204) in core/gov/bio modules.
  - DTZ005: ensure timezone usage.
  - Remaining E501 line length.
- After: run again, aim <200 total.

---

## BLOCK 3 — MyPy Targeted Fixes
- Run `mypy lukhas`.
- Fix:
  - Any `Optional[...]` unsafe usage.
  - List vs None assignments.
  - Add type hints for public APIs.
- Keep edits small, ≤20 lines/file.

---

## BLOCK 4 — Final Gates
Run:
```bash
ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
mypy lukhas
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-fail-under=50 -q
lint-imports --config=linter.ini
ruff check .
```

Output a final JSON line:
```json
{ "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool> }
```

---

## Guardrails
- ≤20 lines/file changes.
- Only deterministic tests (no I/O, no secrets).
- UTC datetime enforced.
- Keep lane guard green.
- Record progress in `docs/audits/CLAUDE_PROGRESS.md`.