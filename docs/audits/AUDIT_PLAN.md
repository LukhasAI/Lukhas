# T4 Audit Execution Plan — Codex vs Claude Code Ownership

This plan adds an explicit Environment Reset and assigns clear ownership for each phase.

Phased Execution (in order)

0) Environment Reset (Owner: Codex)
• Deactivate any active venv and remove local caches/artifacts.
• Create a fresh .venv, install minimal toolchain (ruff, mypy, pytest, pytest-dotenv), then project deps.

1) Tooling & Config Consolidation (Owner: Claude Code)
• Adopt Ruff as formatter+lint, add mypy.ini, align VS Code settings; simplify pre-commit to Ruff+MyPy(+gitleaks).
• Remove Black/Flake8/Pylint config and CI steps (with a clear diff plan).

2) Quick Mechanical Fixes (Owner: Codex)
• Apply safe syntax fixes flagged in baseline audit (no broad refactors). Example: convert top-level return to a function in `candidate/logging/shared_logging.py` (or equivalent helper).
• Run “ruff check --fix . && ruff format .” on stable lanes first (lukhas/, serve/), avoid risky candidate churn.

3) MyPy Triage and Surgical Fix Plan (Owner: Claude Code)
• Run “mypy .”, list top 10 high-risk issues (None/Optionals, wrong signatures, missing attrs) with one-liner fixes (<20 lines/file).
• Hand off patches to Codex for application.

4) Stable Lane Hygiene & Lane Integrity (Owner: Codex)
• Ensure stable lane avoids direct candidate/ imports; prefer facades/dynamic loading with safe fallbacks.
• Keep lane guard and import-linter checks green.

5) Test Posture & Coverage (Owner: Claude Code lead; Codex executes)
• Ensure pytest env stability; confirm .env usage; mark slow/integration tests.
• Achieve ≥85% gate now; plan the path to 95%+.

6) Security & Secrets (Owner: Claude Code lead; Codex wires hooks)
• Validate gitleaks configuration and SARIF path; ensure tests use os.getenv("TEST_*", "dummy").
• Keep redaction on; no secrets printed.

7) MΛTRIZ Minimal Viable Artifacts (Owner: Claude Code lead; Codex implements)
• Define typed dataclasses for node schema (TYPE/STATE/LINKS/EVOLVES_TO/TRIGGERS/REFLECTIONS) and a JSON Schema.
• Add small round‑trip/evolution tests (markers: consciousness, smoke).

8) Commit & CI (Owner: Codex)
• Commit by theme; ensure pre-commit hooks run; verify CI passes (lint, type, tests, gitleaks).

Environment Reset — Commands (Codex)

```bash
# Deactivate if active
deactivate 2>/dev/null || true

# Remove venvs, caches, coverage artifacts
rm -rf .venv .mypy_cache .ruff_cache .pytest_cache __pycache__
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf htmlcov coverage.xml test-results.xml

# Fresh venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel
python -m pip install -U setuptools

# Minimal toolchain
pip install ruff mypy pytest pytest-dotenv

# Project deps
[ -f requirements.txt ] && pip install -r requirements.txt || true

# Ensure .env exists
cp -n .env.example .env 2>/dev/null || true
```

Acceptance Criteria
• Codex: Ruff clean + formatted in stable lanes, MyPy runs, pre-commit hooks (Ruff/MyPy/gitleaks) active, syntax hotspots fixed.
• Claude Code: Config diffs applied, MyPy triage + proposals merged, pytest env stable, MΛTRIZ schema + tests landed.
• pre-commit run --all-files passes
• ruff check . returns 0

—

Appendix: Config Snippets and Task Packs

1) ruff.toml (drop-in)

Save as ruff.toml at repo root.

# Ruff as the single source of truth (lint + formatter)
target-version = "py39"  # adjust if your code is 3.10/3.11
line-length = 100
extend-exclude = [
  ".*build*/", ".*dist*/", ".*venv*/", ".git/", ".mypy_cache/", ".ruff_cache/",
  "node_modules/", "reports/", "scripts/generated/", "MATRIZ/**/*.json"
]

[lint]
select = [
  "E",    # pycodestyle errors
  "F",    # pyflakes
  "W",    # pycodestyle warnings
  "I",    # isort (import order)
  "UP",   # pyupgrade (modernize syntax)
  "B",    # flake8-bugbear (bug-prone patterns)
  "DTZ",  # flake8-datetimez (tz-aware)
  "Q",    # flake8-quotes
  "SIM",  # flake8-simplify
  "RUF",  # ruff-specific
  "ARG",  # flake8-unused-arguments
  "ANN",  # flake8-annotations (lightweight)
  "PLC",  # pylint conventions (select ones Ruff supports)
  "PERF", # performance anti-patterns
]
ignore = [
  # relax annotations on tests and dunder inits for now
  "ANN101", "ANN102", "ANN401",
  # allow __init__ to re-export w/out noise
  "F401",
]

[lint.per-file-ignores]
"**/__init__.py" = ["F401", "F403"]
"tests/**" = ["ANN", "S101"]  # tests are less strict

[lint.isort]
known-first-party = ["lukhas", "matriz"]
combine-as-imports = true

[format]
# Ruff’s formatter (no Black) — deterministic, fast
quote-style = "double"
indent-style = "space"
line-ending = "lf"
docstring-code-format = true
skip-magic-trailing-comma = false

Why this set? It enforces correctness (E/F), modern Python (UP), import hygiene (I), catches foot-guns (B, ARG), and optimizes for speed and clarity. We keep annotation rules light and relax tests to avoid churn.

⸻

2) mypy.ini (drop-in)

[mypy]
python_version = 3.9
warn_unused_ignores = True
warn_redundant_casts = True
warn_unreachable = True
no_implicit_optional = True
check_untyped_defs = True
disallow_incomplete_defs = True
ignore_missing_imports = True

# tighten later (team scale):
# disallow_untyped_defs = True
# strict_optional = True

[mypy-tests.*]
disallow_untyped_defs = False
ignore_missing_imports = True


⸻

3) VS Code settings (drop-in)

Save as .vscode/settings.json (create folder if missing).

{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-q"],
  "python.testing.cwd": "${workspaceFolder}",
  "python.envFile": "${workspaceFolder}/.env",

  // Formatter/Linter = Ruff
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "always",
    "source.organizeImports": "always"
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "ruff.lint.run": "onSave",
  "ruff.format.run": "onSave",

  // Pylance type hints are fine, MyPy runs via CLI/CI
  "python.analysis.typeCheckingMode": "basic",

  // Disable other formatters/linters
  "python.formatting.provider": "none",
  "python.linting.enabled": false
}

Then disable Black/Flake8/Pylint extensions in VS Code (or keep them off per-project with the above).

⸻

4) pytest.ini (drop-in)

[pytest]
testpaths = tests
addopts = -q
env_files = .env
filterwarnings =
    ignore::DeprecationWarning

Install pytest-dotenv so .env loads automatically.

⸻

A) Improved ruff.toml (drop-in replacement)

```toml
# Ruff as the single source of truth (lint + formatter)
target-version = "py39"  # adjust if your code is 3.10/3.11
line-length = 100
extend-exclude = [
  ".*build*/", ".*dist*/", ".*venv*/", ".git/", ".mypy_cache/", ".ruff_cache/",
  "node_modules/", "reports/", "scripts/generated/", "MATRIZ/**/*.json"
]

[lint]
select = [
  "E",    # pycodestyle errors
  "F",    # pyflakes
  "W",    # pycodestyle warnings
  "I",    # isort (import order)
  "UP",   # pyupgrade (modernize syntax)
  "B",    # flake8-bugbear (bug-prone patterns)
  "DTZ",  # flake8-datetimez (tz-aware)
  "Q",    # flake8-quotes
  "SIM",  # flake8-simplify
  "RUF",  # ruff-specific
  "ARG",  # flake8-unused-arguments
  "ANN",  # flake8-annotations (lightweight)
  "PLC",  # pylint conventions (select ones Ruff supports)
  "PERF", # performance anti-patterns
]
ignore = [
  # relax annotations on tests and dunder inits for now
  "ANN101", "ANN102", "ANN401",
  # allow __init__ to re-export w/out noise
  "F401",
]

[lint.per-file-ignores]
"**/__init__.py" = ["F401", "F403"]
"tests/**" = ["ANN", "S101"]  # tests are less strict

[lint.isort]
known-first-party = ["lukhas", "matriz"]
combine-as-imports = true

[format]
# Ruff’s formatter (no Black) — deterministic, fast
quote-style = "double"
indent-style = "space"
line-ending = "lf"
docstring-code-format = true
skip-magic-trailing-comma = false
```

⸻

B) Pre-commit with gitleaks (drop-in)

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
        additional_dependencies: []
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.17.0
    hooks:
      - id: gitleaks
        args: ["--redact", "--report-format", "sarif", "--report-path", "gitleaks.sarif"]
```

⸻

C) VS Code workspace addition

```json
"python.testing.unittestEnabled": false
```

⸻

D) Import-linter (lane guard config)

```ini
[importlinter]
# Example import-linter config for lane guard

[importlinter:local_package]
module = lukhas

[importlinter:ban]
ban = candidate
message = "Direct imports from candidate/ are forbidden in stable lanes; use facades or dynamic loading."
```


⸻

5) Claude Code — Task Pack (architectural/config & reasoning)

File: CLAUDE_CODE_TASKS.md
	1.	Create / update repo configs
	•	Create ruff.toml, mypy.ini, .vscode/settings.json, pytest.ini with the exact contents provided above.
	•	If pyproject.toml includes [tool.black], [tool.pylint], [tool.flake8], or black in tool.poetry.group.dev, remove those sections and dev deps.
	•	Output a diff summary.
	2.	Purge conflicting tooling
	•	Search the repo for any Black/Flake8/Pylint config fragments or CI steps (GitHub Actions, pre-commit).
	•	Remove or comment them, replacing with Ruff + MyPy equivalents.
	•	If .pre-commit-config.yaml exists, leave only Ruff + MyPy hooks (see Codex task for concrete hooks); show final YAML.
	3.	Pytest env diagnosis
	•	Run pytest -q (assume fresh venv & minimal deps).
	•	If imports fail, detect root cause (missing __init__.py, wrong PYTHONPATH, relative imports).
	•	Propose the smallest fix (prefer adding __init__.py / import path correctness over sys.path hacks).
	•	Report findings and apply surgical changes.
	4.	Type-safety hot spots
	•	Run mypy . and list the top 10 actionable errors that could cause runtime bugs (None handling, wrong return types, missing attrs on unions).
	•	For each, propose a one-liner fix (guard/annotation) and apply to the file. Keep diffs under 20 lines per file.
	5.	Test stability & minimal secrets
	•	Ensure tests read .env via pytest.ini + pytest-dotenv.
	•	If any test references a hardcoded credential, replace with os.getenv("TEST_*", "dummy") pattern.
	•	Confirm no real secrets are printed/logged by tests.
	6.	Doc nudge
	•	Append a short “Tooling & Testing” section to README.md: Ruff(+formatter) policy, MyPy usage, how to run tests locally, and the .env expectation.

⸻

6) Codex — Task Pack (CLI + mechanical edits)

File: CODEX_TASKS.md

Run these in VS Code terminal from repo root. Replace pyproject.toml/requirements*.txt to match your repo.

0) Fresh environment

# 0.1 nuke old venv & caches
deactivate 2>/dev/null || true
rm -rf .venv .mypy_cache .ruff_cache .pytest_cache

# 0.2 create clean venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel

# 0.3 minimal dev toolchain
pip install ruff mypy pytest pytest-dotenv

1) Project deps (pick your manager)

# If requirements.txt exists:
[ -f requirements.txt ] && pip install -r requirements.txt || true

# If pyproject.toml/poetry:
# pip install poetry && poetry export -f requirements.txt --output requirements.lock --without-hashes
# pip install -r requirements.lock

2) Remove Black/Flake8/Pylint from repo & env

# Uninstall tools (from venv)
pip uninstall -y black flake8 pylint

# Remove common config fragments if present
sed -i.bak '/\[tool.black\]/,/^\[/d' pyproject.toml 2>/dev/null || true
sed -i.bak '/\[tool.flake8\]/,/^\[/d' pyproject.toml 2>/dev/null || true
sed -i.bak '/\[tool.pylint\]/,/^\[/d' pyproject.toml 2>/dev/null || true

# Pre-commit: keep only Ruff + MyPy (create or replace)
cat > .pre-commit-config.yaml <<'YAML'
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
        additional_dependencies: []
YAML

pre-commit install || true

3) Add configs

# Write ruff.toml
cat > ruff.toml <<'TOML'
<PASTE THE ruff.toml FROM ABOVE>
TOML

# Write mypy.ini
cat > mypy.ini <<'INI'
<PASTE THE mypy.ini FROM ABOVE>
INI

# VS Code settings
mkdir -p .vscode
cat > .vscode/settings.json <<'JSON'
<PASTE THE settings.json FROM ABOVE>
JSON

# pytest.ini
cat > pytest.ini <<'INI'
<PASTE THE pytest.ini FROM ABOVE>
INI

4) First pass: format + lint + type

ruff check --fix .
ruff format .
mypy .
pytest -q

If pytest fails due to env, ensure .env exists. Example:

cp -n .env.example .env 2>/dev/null || true

5) Prune unused packages (optional, careful)

# list installed
pip freeze > .tools/pip-freeze.before.txt

# detect obvious orphans (manual review recommended)
pip install pip-check-reqs pip-autoremove
pip-check-reqs || true

# example: autoremove a clearly unused lib (adjust names after review)
# pip-autoremove <package> -y

6) Commit

git add -A
git commit -m "Tooling: switch to Ruff(+formatter) + MyPy; VSCode/pytest configs; remove Black/Flake8/Pylint"


⸻

Notes & T4 cautions
	•	Ruff formatter is excellent now; still, if you later see style bikeshedding, add Black back in CI only. For solo dev, Ruff alone is perfect.
	•	Mypy: start pragmatic (ignore_missing_imports = True) to avoid churn; tighten per-module as you stabilize.
	•	Pytest env: the majority of “pytest doesn’t run” cases are (a) missing .env, (b) missing __init__.py making packages non-importable, (c) PYTHONPATH confusion. The provided pytest.ini + pytest-dotenv + VS Code settings eliminates (a) & (c). If you hit (b), add __init__.py at the package root(s) (lukhas/, matriz/, etc.).
	•	Dep pruning: tools can over-eagerly flag; prefer manual review + gradual pruning.
	•	Security: since you’re solo & private, .env is fine. When you scale, switch to a vault and enforce pre-commit + CI checks.

⸻
