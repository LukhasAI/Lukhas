# STEPS_1 — Claude Execution Script (Long-Context Plan)

> Purpose: This file is fed **directly to Claude** (Codex has a smaller context). It contains the full next-phase plan with precise edits, runbooks, and acceptance gates. Keep changes **surgical** and diffs ≤20 lines per file.

---
## 0) Assumptions
- Fresh venv and toolchain are already installed and working.
- `ruff.toml`, `mypy.ini`, `.vscode/settings.json`, `pytest.ini` exist per AUDIT_PLAN.md.
- Stable lanes: `lukhas/**` (primary), `serve/**` (as needed).

## 1) MyPy Targeted Runtime-Risk Fixes (stable lanes only)
Prioritize **None ops**, **union attribute access**, **incompatible assignments**, **missing annotations on public APIs**.

### Files & Actions
1. `lukhas/core/common/exceptions.py`
   - Around line ~36: add parameter and return type annotations for public functions.
   - Around line ~251: fix `None / float` division by guarding `None` or using a default.
   - **Constraint:** keep total diff ≤20 lines.
2. `lukhas/governance/auth_governance_policies.py`
   - Around ~66: avoid assigning `None` to `list[str]`. Prefer `[]` or use `Optional[list[str]]` and guard before use.
3. `lukhas/identity/passkey/registry.py`
   - Add minimal annotations for function arguments/returns (`str`, `dict[str, Any]`, `-> None` where applicable).
4. `lukhas/governance/consent_ledger/registry.py`
   - Same pattern as passkey registry (minimal, pragmatic annotations).
5. Any `x.symbol` or similar where `x` can be `None`
   - Add a guard (`if x is None: return ...` or raise) or assert.
6. `lukhas/bio/core/bio_symbolic.py`
   - Ensure all `__init__` have `-> None`.
   - Replace `datetime.now()` with `datetime.now(timezone.utc)` and import `timezone` where needed.

### Acceptance
- `mypy lukhas` exits 0 **or** only reports third‑party stub noise (allowed by `ignore_missing_imports = True`).

---
## 2) Ruff Config Finalization (strict on stable, relaxed elsewhere)
- Keep ANN strict for `lukhas/**`.
- Relax annotations in noisy lanes to avoid churn.

### Edits to `ruff.toml`
- Update `[lint.per-file-ignores]`:
  ```
  [lint.per-file-ignores]
  "**/__init__.py" = ["F401","F403"]
  "tests/**" = ["ANN","S101"]
  "candidate/**" = ["ANN"]
  "tools/**" = ["ANN"]
  "enterprise/**" = ["ANN"]
  ```
- Ensure `DTZ` remains enabled (timezone-safe datetime).

### Acceptance
- `ruff check lukhas` returns 0 after `--fix` + `format`.
- Repo‑wide `ruff check .` yields only permitted warnings from relaxed lanes.

---
## 3) Tests & Coverage Boost (fast, focused)
Add **small** tests; avoid heavy fixtures. Use `.env` via `pytest.ini`.

### New tests to create
1. `tests/matriz/test_orchestrator_smoke.py`
   - Instantiate orchestrator (happy path), execute a no‑op plan, assert basic response shape.
   - If API client is exposed, hit `/system/trace` and validate structure (count, list of traces).
2. `tests/governance/test_policies_min.py`
   - Policies with default/empty scopes do not crash; verify deterministic decision.
3. `tests/core/test_time_tz.py`
   - Assert all timestamps produced in stable code paths are `timezone.utc`.

### Command
- `pytest --cov=lukhas --cov-report=term-missing -q`

### Acceptance
- Coverage (stable lanes) ≥ 70% now; leave TODO to raise to 80/85 in follow‑up.
- No test logs leak secrets; any secret usage in tests must be `os.getenv("TEST_*", "dummy")`.

---
## 4) Lane Guard (import‑linter)
- Ensure no `lukhas` → `candidate` direct imports.

### Config (`linter.ini`)
```
[importlinter]
root_package = lukhas
include_external_packages = False

[contract: no_lukhas_to_candidate]
name = No lukhas -> candidate imports
type = forbidden
source_modules = lukhas
forbidden_modules = candidate
```
### Command
- `lint-imports --config=linter.ini`

### Acceptance
- Exit code 0; any violation must be refactored to a facade/dynamic loader in `lukhas`.

---
## 5) Security Hygiene
- Pre‑commit has Ruff + MyPy + Gitleaks. Keep `--redact` on.

### Commands
- `pre-commit install`
- `pre-commit run --all-files`
- (Optional local) `gitleaks detect --no-banner --redact`

### Acceptance
- No blocking secret findings; tests use dummy env values.

---
## 6) Runbook (in order)
```
# Lint + format (stable)
ruff check --fix lukhas && ruff format lukhas && ruff check lukhas

# Types (stable)
mypy lukhas

# Tests + coverage
pytest --cov=lukhas --cov-report=term-missing -q

# Lane guard
lint-imports --config=linter.ini

# Full repo (sanity)
ruff check .
```

---
## 7) Acceptance Gates (single-line status)
Print:
```
{ ruff_stable_ok: <bool>, mypy_ok: <bool>, pytest: { passed: X, failed: Y, errors: Z, skipped: S }, coverage_stable: <int_percent>, lane_guard_ok: <bool> }
```

---
## 8) Notes (T4 guardrails)
- Keep diffs minimal; avoid refactors.
- Prefer guards / Optional typing over broad API changes.
- Enforce UTC consistently; document deviations.
- If third‑party stubs are missing (e.g., yaml), install `types-*` and add to dev deps.
```

# STEPS_2 — Claude Execution Script (Config Normalize, Type Stubs, Coverage to 30–40%)

> Feed this whole file to **Claude Code**. It plans first, then executes all blocks end‑to‑end. Keep edits **≤20 lines per file** and avoid API refactors.

---
## 0) Assumptions
- Phase 1 is complete: tests pass; lane guard OK; coverage instrumentation fixed.
- You have: `ruff.toml`, `mypy.ini`, `.coveragerc`, `pytest.ini`, `.pre-commit-config.yaml`.
- Stable lanes: `lukhas/**` (primary), `serve/**` (as needed). Non‑stable lanes: `candidate/**`, `tools/**`, `enterprise/**`.

## Output protocol (unchanged)
1. Start with a brief **PLAN** + numbered TODO list.
2. For each block, list files changed and show minimal diffs (≤20 lines/file).
3. After each block, run the **gate commands** and paste the **last 30 lines**.
4. Append to `docs/audits/CLAUDE_PROGRESS.md`: Timestamp · Task · Files changed · Gate result.
5. End with **one JSON line** status:
   ```
   { "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool> }
   ```

---
## BLOCK 1 — Ruff Config Normalize (cut noise; keep stable strict)
**Goal:** Reduce ~860 Ruff errors by relaxing annotation rules outside stable lanes and raising line length where needed, while **keeping `lukhas/**` strict**.

1) Edit `ruff.toml`:
   - Ensure these remain selected: `E,F,W,I,UP,B,DTZ,Q,SIM,RUF,ARG,PLC,PERF,C4,RET`.
   - Raise line length to 120 to reduce E501 churn:
     ```toml
     line-length = 120
     ```
   - Per‑file ignores (merge if present):
     ```toml
     [lint.per-file-ignores]
     "**/__init__.py" = ["F401","F403"]
     "tests/**" = ["ANN","S101"]
     "candidate/**" = ["ANN"]
     "tools/**" = ["ANN"]
     "enterprise/**" = ["ANN"]
     ```
   - Keep `DTZ` rules enabled.

**Gate:**
```bash
ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
ruff check .
```

---
## BLOCK 2 — MyPy Type Stubs + Top Errors (stable only)
**Goal:** Remove third‑party stub noise and fix the top real type errors.

1) Dev stubs (add to dev deps; minimal diff):
   - If missing, install and add to `requirements-dev.txt` (create if absent):
     ```
     types-PyYAML
     types-requests
     types-setuptools
     ```
   - If repo uses other libs that complain, prefer `types-*` packages first.

2) Targeted fixes (≤20 lines/file):
   - `lukhas/core/common/exceptions.py`: ensure public fns have parameter/return annotations; guard Optional values before arithmetic.
   - `lukhas/governance/auth_governance_policies.py`: avoid assigning `None` to `list[str]` (init `[]` or use `Optional[list[str]]` + guard).
   - `lukhas/identity/passkey/registry.py` and `lukhas/governance/consent_ledger/registry.py`: minimal arg/return annotations (`str`, `dict[str, Any]`, `-> None`).
   - Any `.symbol` (or similar) access on possibly‑None objects → add guard or `assert`.

**Gate:**
```bash
mypy lukhas
```

---
## BLOCK 3 — Coverage to 30–40% (stable lanes)
**Goal:** Add tiny tests that touch uncovered, safe code paths. Keep each test ≤30 lines.

Create or amend:
1) `tests/core/test_exceptions_paths.py` — cover at least 2 branches in exceptions module (e.g., path where Optional is None and non‑None).
2) `tests/governance/test_policies_defaults.py` — construct a minimal policy/config and assert deterministic decision on empty scopes.
3) `tests/core/test_time_tz.py` — assert UTC usage for any timestamp creators in stable code paths.
4) (Optional) `tests/bridge/test_branding_imports.py` — import `lukhas/branding_bridge.py` and exercise a simple function to cover top‑level imports and one long‑line path broken into multiple lines.

**Command:**
```bash
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered -q
```

**Acceptance:**
- Coverage for `lukhas` ≥ 30% (aim 30–40% in this block).
- Tests remain fast and deterministic; no real secrets used (use `os.getenv("TEST_*", "dummy")`).

---
## BLOCK 4 — Lane Guard in CI (no lukhas → candidate)
**Goal:** Ensure contract is enforced automatically.

1) Create `linter.ini` in repo root if missing:
   ```ini
   [importlinter]
   root_package = lukhas
   include_external_packages = False

   [contract: no_lukhas_to_candidate]
   name = No lukhas -> candidate imports
   type = forbidden
   source_modules = lukhas
   forbidden_modules = candidate
   ```
2) Add a CI step (GitHub Actions snippet) into your existing workflow file (show only minimal diff):
   ```yaml
   - name: Import Linter (lane contract)
     run: |
       pip install import-linter
       lint-imports --config=linter.ini
   ```

**Gate:**
```bash
lint-imports --config=linter.ini
```

---
## BLOCK 5 — Pre-commit tighten (Ruff+Format+MyPy+Gitleaks)
Ensure hooks exist and are green locally (or list what would run if environment blocks execution).

1) `.pre-commit-config.yaml` should contain:
   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.6.7
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format
     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v1.10.0
       hooks:
         - id: mypy
     - repo: https://github.com/gitleaks/gitleaks
       rev: v8.18.4
       hooks:
         - id: gitleaks
           args: ["protect","--staged","--redact"]
   ```

**Gate:**
```bash
pre-commit run --all-files || true
```
If blocked by environment, print the hooks that would run and mark as informational.

---
## BLOCK 6 — Final gates & status line
Run in order:
```bash
ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
mypy lukhas
pytest --cov=lukhas --cov-config=.coveragerc --cov-report=term-missing:skip-covered -q
lint-imports --config=linter.ini
ruff check .
```

Output a single JSON line:
``` 
{ "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool> }
```
Then list changed files (no diffs) and append the status to `docs/audits/CLAUDE_PROGRESS.md`.

---
## Notes (T4 guardrails)
- Keep edits ≤20 lines/file; split across files.
- Prefer `Optional[...]` + guards to avoid breaking APIs.
- Maintain UTC timestamp policy; import `timezone` as needed.
- Use `types-*` stubs to reduce MyPy noise; only resort to `# type: ignore[...]` for library edge cases.
- Add tests that are tiny and deterministic; no network or I/O.
```

# LUKHAS — Baseline Deep Search Audit Plan (Master)

This is the **master plan**. It links to the execution scripts used with Claude.

## Artifacts & Execution Scripts
- **STEPS_1:** `docs/audits/STEPS.md` — Long-context execution script (initial pass: env, Ruff+MyPy setup, pytest stabilisation).
- **STEPS_2:** `docs/audits/STEPS_2.md` — Config normalisation, type stubs, coverage to 30–40%, CI lane guard, pre-commit.
- **STEPS_3:** `docs/audits/STEPS_3.md` — Fix failing tests, push coverage to 35–40%, reduce Ruff/MyPy.

## Acceptance Criteria (global)
- `ruff check .` passes on stable lanes (`lukhas/**`), repo-wide shows only permitted warnings in relaxed lanes.
- `mypy lukhas` has no runtime-risk errors; third-party typing noise tolerated until stubs added.
- `pytest` green; coverage for `lukhas` ≥ target per phase (30–40% in STEPS_2; 35–40% in STEPS_3).
- Lane contract (`lukhas → candidate`) enforced by import-linter (CI gate).
- `pre-commit run --all-files` clean (Ruff, Ruff-format, MyPy, Gitleaks).

## Notes
- Keep edits ≤20 lines per file; avoid API refactors in these phases.
- Enforce UTC timestamps (`datetime.now(timezone.utc)`).
- Use `Optional[...]` guards rather than widening types where behaviour is unclear.
