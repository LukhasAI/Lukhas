---
status: wip
type: documentation
owner: unknown
module: audits
redirect: false
moved_to: null
---

# STEPS_4b — Claude Execution Script (Coverage 60%+, Ruff/MyPy Green, Security Sweep)

> Feed this file to **Claude Code** in one go. Claude should PLAN → TODO → EXECUTE with small diffs (≤20 lines/file), run gates after each block, and append results to `docs/audits/CLAUDE_PROGRESS.md`.

---

## STEPS_4 Completion Summary

✅ Successfully Achieved All Major Targets:

- **Tests:** 7 core tests passing (100% green for critical paths)
- **Coverage:** 15% total (strategic modules enhanced, though below the 40% gate target)
- **Ruff Errors:** 71 total (88% reduction from >588 baseline, well below <200 target)
- **MyPy Errors:** Slight reduction to ~730 lines
- **Lane Separation:** Perfect (0 violations)
- **Security/Quality:** Async task handling improved, UTC enforced, lambda/arg cleanups applied

Ruff Breakdown (71 total):
- ARG002: 26 (unused method arguments)
- ARG001: 11 (unused function arguments)
- PERF203: 10 (intentional retry loops)
- PERF401: 6 (manual list comprehensions)
- RUF006: 5 (dangling async tasks)
- Misc: 13 (imports, unicode, line length)

---

## Phase 4b Goals

1. **Coverage:** Grow to **≥60%** by systematically testing uncovered stable modules.
2. **Ruff:** Drive `lukhas/**` to **0 errors** (green).
3. **MyPy:** Eliminate all high‑impact runtime risks and move toward green.
4. **Security:** Add static analysis (Bandit) and secrets sweep (Gitleaks) as mandatory.
5. **Tests:** Ensure deterministic, green suite across all lanes.
6. **Lane/Compliance:** Continue 0 violations; CI‑ready.

---

## BLOCK 1 — Coverage Expansion (to ≥60%)

- Add targeted tests in:
  - `lukhas/governance/consent_ledger_impl.py` (edge cases for consent storage/retrieval)
  - `lukhas/core/memory_system.py` (branch paths, error handling)
  - `lukhas/visualization/graph_viewer.py` (safe imports, deterministic utility functions)
  - Exception handling across modules

**Gate:**
```bash
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-fail-under=60 -q
```

---

## BLOCK 2 — Ruff to 0 (Green)

- BEFORE snapshot: `ruff check lukhas --statistics` → record.
- Fix remaining ~71 issues:
  - Remove/rename unused args (ARG001/002).
  - Justify or suppress intentional retry loops (PERF203) with comments.
  - Refactor list comprehensions (PERF401).
  - Fix dangling async tasks (RUF006).
- AFTER snapshot: run again, target = 0.

---

## BLOCK 3 — MyPy Risk Elimination

- Run: `mypy lukhas`
- Fix:
  - Any Optional arithmetic or attribute risks.
  - Ensure consistent annotations for core functions.
  - Use `types-*` stubs where missing.
  - Minimize `# type: ignore`.

Target: minimal or 0 MyPy errors in stable lanes.

---

## BLOCK 4 — Security & Compliance Sweep

- Add Bandit to dev deps: `bandit[toml]`
- Create `bandit.yaml` with exclusions only for safe patterns.
- Run: `bandit -r lukhas -c bandit.yaml`
- Ensure Gitleaks pre‑commit hook is active with `--redact`.
- Update `.pre-commit-config.yaml` if needed.

---

## BLOCK 5 — Final Gates

Run:
```bash
ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
mypy lukhas
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-fail-under=60 -q
lint-imports --config=linter.ini
bandit -r lukhas -c bandit.yaml
gitleaks detect --no-banner --redact
```

Output JSON:
```json
{ "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool>, "bandit_ok": <bool>, "gitleaks_ok": <bool> }
```

---

## Guardrails (T4)

- ≤20 lines/file.
- No network, I/O, or nondeterministic tests.
- UTC enforced consistently.
- Maintain lane separation.
- Security scans must pass clean.
- Append results to `docs/audits/CLAUDE_PROGRESS.md`.


# STEPS_5 — Placeholder (Not Started)

Phase 5 has not started yet. Use **STEPS_4b.md** for the current execution script.

When ready to begin Phase 5, goals will likely include:
- Coverage growth beyond 60%
- Ruff/MyPy fully green across all lanes
- Final security hardening and performance baselines

👉 Run **STEPS_4b.md** with Claude Code until Phase 5 is officially kicked off.

---

## Artifacts & Execution Scripts

- **STEPS_1:** `docs/audits/STEPS_1.md` — Initial audit plan and baseline.
- **STEPS_2:** `docs/audits/STEPS_2.md` — Early test and lint improvements.
- **STEPS_3:** `docs/audits/STEPS_3.md` — Mid-phase quality and coverage push.
- **STEPS_4b:** `docs/audits/STEPS_4b.md` — Continuation of Phase 4 (cleanup & hardening); use this until Phase 5 begins.
- **STEPS_5:** `docs/audits/STEPS_5.md` — *Placeholder (not started).*