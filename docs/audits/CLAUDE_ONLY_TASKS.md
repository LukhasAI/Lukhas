---
status: wip
type: documentation
---
You are Claude Code operating on the LUKHAS repo. Execute the full next-phase plan in a single session.
Style: plan → TODO checklist → execute in small diffs (≤20 lines/file) → run gates after each block → append to progress log.
Do NOT refactor APIs; only minimal, surgical changes.

Assumptions
	•	venv active and working; tools installed (ruff, mypy, pytest, pytest-dotenv).
	•	These files exist: ruff.toml, mypy.ini, .vscode/settings.json, pytest.ini.
	•	Stable lanes: lukhas/** (primary), serve/** (as needed).
	•	Work from repo root. Keep each commit focused: git add -A && git commit -m "<Block>: <summary>".

Output protocol (very important)
	1.	Start with a short PLAN and a numbered TODO list (bullets, 1–2 lines each).
	2.	For each block: list changed files, show only minimal diffs (≤20 lines/file).
	3.	After each block: run the gate commands and paste last 30 lines of output.
	4.	Maintain a concise log in docs/audits/CLAUDE_PROGRESS.md with: Timestamp · Task · Files changed · Gate result.
	5.	End by printing a single JSON status line:

{ "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool> }


⸻

BLOCK 0 — Sanity + progress log
	•	Create or update docs/audits/CLAUDE_PROGRESS.md (append-only).
	•	Print versions:

which python
python --version
ruff --version
mypy --version
pytest --version



Gate: versions print successfully.

⸻

BLOCK 1 — Ruff config finalization (strict on stable, relaxed elsewhere)
	•	Edit ruff.toml to include (merge if present):

[lint.per-file-ignores]
"**/__init__.py" = ["F401","F403"]
"tests/**" = ["ANN","S101"]
"candidate/**" = ["ANN"]
"tools/**" = ["ANN"]
"enterprise/**" = ["ANN"]


	•	Ensure DTZ rules remain selected. Show only the ruff.toml hunks changed.

Run gates:

ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
ruff check .

Paste last 30 lines from each.

⸻

BLOCK 2 — MyPy runtime-risk fixes (stable lanes only)

Targets and constraints:
	•	lukhas/core/common/exceptions.py
	•	~36: add param/return annotations to public functions.
	•	~251: fix None / float division with guard or default.
	•	lukhas/governance/auth_governance_policies.py
	•	~66: don’t assign None to list[str] (init to [] or use Optional[list[str]] + guard).
	•	lukhas/identity/passkey/registry.py & lukhas/governance/consent_ledger/registry.py
	•	Minimal arg/return annotations (e.g., str, dict[str, Any], -> None).
	•	Scan lukhas/** for .symbol on possibly-None objects; add a guard or assert.

Diff limit: ≤20 lines per file; no API refactors.

Gate:

mypy lukhas

Paste last 30 lines.

⸻

BLOCK 3 — Named lint fixes (stable lanes)
	•	lukhas/bio/__init__.py: sort __all__ (RUF022).
	•	lukhas/bio/core/bio_symbolic.py: ensure all __init__ → -> None; replace datetime.now() with datetime.now(timezone.utc) and import timezone.
	•	lukhas/branding_bridge.py: move inner imports to top-level; wrap long lines (~126, ~375) with parentheses (no backslashes).

Gate:

ruff check lukhas

Paste last 30 lines.

⸻

BLOCK 4 — Tests & coverage (stable lanes)

Create small tests (≤30 lines each), avoid heavy fixtures:
	•	tests/conftest.py: insert repo root into sys.path for consistent imports.
	•	tests/core/test_time_tz.py: assert UTC timestamps in touched stable paths.
	•	tests/governance/test_policies_min.py: default/empty policy path is deterministic and non-crashing.
	•	tests/matriz/test_orchestrator_smoke.py: if importable, create minimal smoke (instantiate orchestrator or validate exposed object); skip if module unavailable.

Gate:

pytest --cov=lukhas --cov-report=term-missing -q

Paste summary and last 30 lines. Compute coverage % for lukhas and log it.

⸻

BLOCK 5 — Lane guard (import-linter)

Create linter.ini:

[importlinter]
root_package = lukhas
include_external_packages = False

[contract: no_lukhas_to_candidate]
name = No lukhas -> candidate imports
type = forbidden
source_modules = lukhas
forbidden_modules = candidate

Gate:

lint-imports --config=linter.ini

If violations exist, list the smallest facade/dynamic-loader patch per file (≤20 lines), do not implement yet—just list.

⸻

BLOCK 6 — Security hygiene (pre-commit + gitleaks)
	•	Ensure .pre-commit-config.yaml has Ruff + Ruff-format + MyPy + Gitleaks (--redact). If missing, update and show diff.

Gate:

pre-commit run --all-files

If the environment blocks execution, print the hooks that would run and expected exit behavior, then mark as informational.

⸻

BLOCK 7 — Final gates & status line

Run in order:

ruff check --fix lukhas && ruff format lukhas && ruff check lukhas
mypy lukhas
pytest --cov=lukhas --cov-report=term-missing -q
lint-imports --config=linter.ini
ruff check .

Output a single JSON line:

{ "ruff_stable_ok": <bool>, "mypy_ok": <bool>, "pytest": { "passed": X, "failed": Y, "errors": Z, "skipped": S }, "coverage_stable": "<int>%", "lane_guard_ok": <bool> }

Then list changed files (no diffs) and append the status to docs/audits/CLAUDE_PROGRESS.md.

⸻

Guardrails (T4)
	•	Keep edits ≤20 lines/file; multiple files allowed.
	•	Prefer Optional[...] + guard instead of signature refactors.
	•	Enforce UTC consistently; add import timezone as needed.
	•	If third-party stubs missing, install types-* and add to dev deps (minimal diff).
	•	If a gate fails, stop, report the failure succinctly (10 lines), propose exactly one minimal fix, apply it, and re-run the failed gate only.

⸻
