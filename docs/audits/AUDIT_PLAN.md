---
status: wip
type: documentation
---
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
