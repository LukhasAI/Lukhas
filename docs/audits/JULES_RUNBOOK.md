JULES_RUNBOOK.md
# JULES_RUNBOOK

A safety-first playbook to let **Jules** (your code agent) auto-generate tests and apply surgical autofixes while preserving architecture and behavior.

## 0) Goals
- Raise **coverage** fast with small, deterministic tests.
- Reduce **Ruff/Mypy** issues without changing semantics.
- Enforce **lane boundaries** and contracts (/healthz, MATRIZ trace).
- Keep change risk low (≤20 lines/file; no public API changes).

## 1) Guardrails (Hard Constraints)
- **Branch**: `feat/jules-tests-and-autofix` only.
- **Write allowlist**: `tests/**`, `docs/**`, `.github/**`, and code under `lukhas/**`, `serve/**`.
- **Denylist**: `candidate/**`, `enterprise/**`, `MATRIZ/**`, `tools/release/**`, secrets (`.env`, `*.pem`, `*.key`).
- **Patch budget**: ≤20 changed lines per file; no behavior changes; no API signature changes.
- **Determinism**: no network; fixed seeds; UTC time freezer; tmp paths only.
- **Gates** (must pass locally):
  - `ruff check --fix . && ruff format .`
  - `mypy .`
  - `import-linter`
  - `gitleaks detect --no-banner --redact || true`
  - `pytest -q --maxfail=1 --disable-warnings --cov=lukhas --cov-report=term-missing`

## 2) Sequence (T4 Recommended)
1. **Mini-Deep-Search Audit (1 hour cap)**
   - Confirm invariants: public APIs, data schemas, lane rules, /healthz+MATRIZ contracts.
   - Identify top 10 files by fan-in and hotspots to *exclude from autofix* (high risk).
2. **Pass A — Tests only**
   - Generate smoke, golden, and contract tests for `lukhas/**` and `serve/**` (no prod code edits).
3. **Pass B — Autofix (surgical)**
   - Apply ruff/mypy-safe diffs on low-risk files; one directory at a time.
4. **Review & Merge**
   - Human review, then merge behind a feature flag if needed.

## 3) Make Targets
```Makefile
make jules-gate:
	python -V
	ruff check --fix .
	ruff format .
	mypy .
	import-linter
	gitleaks detect --no-banner --redact || true
	pytest -q --maxfail=1 --disable-warnings --cov=lukhas --cov-report=term-missing

make jules-tests:
	pytest -q -m "smoke or golden" --maxfail=1 --disable-warnings

make jules-full:
	make jules-gate && make jules-tests
```

## 4) Prompts for Jules
### A) Generate Missing Tests (stable lanes)
```
You are writing pytest tests ONLY.
Rules:
- Write under tests/** mirroring package paths (e.g., tests/lukhas/… ).
- No production edits in this task.
- Use pytest style; deterministic; no network; use tmp_path.
- Public APIs only; add @pytest.mark.smoke for import/constructor tests; @pytest.mark.golden for stable outputs; @pytest.mark.matriz for trace paths.
- Add shared fixtures in tests/conftest.py; avoid globals.
- Prefer small tests covering edge/None/error paths; target +10% coverage by quick wins.
Deliverables: (1) file list, (2) full contents per file, (3) zero ruff/mypy issues.
```

### B) Golden & Contract Tests
```
Create golden/contract tests for:
- /healthz handler (200 + schema).
- MATRIZ trace endpoint (trace id propagation; minimal schema).
- Core serialization/deserialization functions in lukhas.*
Store goldens under tests/golden/<area>/*.json. Use schema + snapshot compare; normalize timestamps/ids.
```

### C) Autofix (Ruff/Mypy — surgical)
```
Task: DIFFS ONLY to reduce ruff/mypy errors without semantic changes.
Scope: lukhas/**, serve/**. Per-file budget ≤20 lines.
Allowed: add `-> None` to __init__, sort __all__, move imports to top-level, annotate Optional/Iterable, enforce tz-aware datetime, guard OTEL calls.
Forbidden: change behavior, signatures, or external APIs.
Each diff must include: file path, before/after unified hunks.
Ensure changed files pass: ruff, mypy.
```

### D) TODO/FIXME Sweep → Patches + Backlog
```
Scan lukhas/** and serve/** for TODO/FIXME.
- Group: (A) trivial <20 lines; (B) small <50 lines; (C) refactor.
- Provide diffs for (A). For (B)/(C), write docs/audits/TODO_BACKLOG.md with risks and test ideas.
```

### E) Lane Guard
```
Run import-linter. If violations exist, propose minimal diffs to move helpers or add adapters under lukhas/bridge/.
```

## 5) Suppressions & Waivers (Your Concern About Over-Fixing)
- Prefer **targeted `# noqa: <RULE>`** on the specific line with a short reason and **expiry tag**: `# noqa: ANN201  # reason=legacy interface; expires=2026-03-01`.
- For file-level noise, use **`per-file-ignores` in ruff.toml** bound to directories and with comments.
- Maintain **`docs/audits/SUPPRESSIONS_LEDGER.md`** listing each suppression, reason, owner, and expiry.
- Create a **Defer rubric**: Defer if (a) the rule forces large refactors, (b) the module is a hotspot with high fan-in, (c) behavior risk > low and no tests yet.

## 6) Acceptance Criteria
- Coverage +10% vs. baseline on `lukhas/**`.
- All gates green on changed files; zero lane violations.
- No public API/behavior changes.
- Patch size within budget; each change traceable to a test or rule.

## 7) Rollback Plan
- If any gate fails or diffs exceed budget, revert the commit set; open PR with logs and partial diffs for human triage.

## 8) Appendices
- **Invariants** (fill before running Jules): public APIs, data schemas, /healthz response shape, MATRIZ trace contract, lane rules.
- **Exclusions**: list top 10 high fan-in files to skip in Pass B.

---