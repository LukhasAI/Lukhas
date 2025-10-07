---
status: wip
type: documentation
owner: unknown
module: audits
redirect: false
moved_to: null
---

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
- Keep edits ≤20 lines/file; split across files instead of large changes.
- Prefer `Optional[...]` + guards to avoid breaking APIs.
- Maintain UTC timestamp policy; import `timezone` as needed.
- Use `types-*` stubs to reduce MyPy noise; only resort to `# type: ignore[...]` for library edge cases.
- Add tests that are tiny and deterministic; no network or I/O.