---
status: wip
type: documentation
---
# T4 Audit Execution TODO Board (Supersedes Multi‑Agent TODO)

Source of truth: docs/audits/AUDIT_PLAN.md

- This board operationalizes the audit plan into actionable checklists.
- It supersedes agents/T4_MULTI_AGENT_TODO_SYSTEM.md for day‑to‑day execution.

Quick Links
- Audit Plan: docs/audits/AUDIT_PLAN.md
- Baseline Audit: docs/audits/BASELINE_AUDIT.md
- Quick Commands: README.md and Makefile targets

Ownership Model
- Codex: Mechanical edits, CLI execution, hooks, hygiene in stable lanes, minimal surgical fixes.
- Claude Code: Config consolidation, reasoning/triage, type‑safety priorities, pytest env diagnosis, MΛTRIZ schema + validation design.
- Jules Agents: Continue domain workstreams; coordinate via this board and the audit plan.

Status Summary (update daily)
- Overall: 75% → Target 95% T4 Ready
- Today’s Focus: Phase 0–2
- Blockers: None reported

Phased Checklist (in order)

0) Environment Reset — Owner: Codex
- [ ] Deactivate any active venv
- [ ] Remove .venv, caches (__pycache__, .mypy_cache, .ruff_cache, .pytest_cache)
- [ ] Recreate .venv; upgrade pip/wheel
- [ ] Install minimal toolchain: ruff, mypy, pytest, pytest‑dotenv
- [ ] Install project deps (requirements.txt)
- [ ] Ensure .env exists (fallback to .env.example)

Commands
```
deactivate 2>/dev/null || true
rm -rf .venv .mypy_cache .ruff_cache .pytest_cache __pycache__
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf htmlcov coverage.xml test-results.xml
python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip wheel
pip install ruff mypy pytest pytest-dotenv
[ -f requirements.txt ] && pip install -r requirements.txt || true
cp -n .env.example .env 2>/dev/null || true
```

Acceptance
- [ ] `.venv` present, `ruff --version`, `mypy --version`, `pytest --version` succeed

1) Tooling & Config Consolidation — Owner: Claude Code
- [ ] Add mypy.ini (pragmatic settings)
- [ ] Align .vscode settings to Ruff formatter; pytest enabled; .env wired
- [ ] Simplify pre‑commit to Ruff + MyPy + gitleaks (plan to remove Black/Flake8/Pylint)
- [ ] Remove redundant linter configs from pyproject/CI (with diff)

Acceptance
- [ ] Pre‑commit runs Ruff+format, MyPy, gitleaks locally

2) Quick Mechanical Fixes — Owner: Codex
- [ ] Fix blatant syntax errors from baseline audit (no broad refactors)
  - Example: candidate/governance/identity/auth_utils/shared_logging.py → top‑level return becomes `get_logger()` function
- [ ] Run `ruff check --fix . && ruff format .` on stable lanes first (lukhas/, serve/)

Acceptance
- [ ] Ruff clean on stable lanes; no E9/F821 in stable lanes

3) MyPy Triage & Surgical Fix Plan — Owner: Claude Code
- [ ] Run `mypy .`; list top 10 high‑risk issues (None handling, wrong signatures, missing attrs)
- [ ] Propose ≤20‑line diffs per file; hand off to Codex

Acceptance
- [ ] Top 10 triaged with one‑liner fixes and rationale

4) Stable Lane Hygiene & Lane Integrity — Owner: Codex
- [ ] Eliminate direct candidate/ imports from stable lanes; use facades/dynamic loading with fallbacks
- [ ] Keep lane guard and import‑linter green

Acceptance
- [ ] No cross‑lane imports in lukhas/; lane guard passes

5) Test Posture & Coverage — Owner: Claude Code (lead) + Codex (execute)
- [ ] Ensure pytest env stable; `.env` loaded via pytest‑dotenv
- [ ] Mark slow/integration; keep gates reasonable (≥85% now)
- [ ] Add minimal tests where critical paths lack coverage

Acceptance
- [ ] pytest green with coverage reports (htmlcov, coverage.xml)

6) Security & Secrets — Owner: Claude Code (lead) + Codex (hooks)
- [ ] Validate gitleaks config; SARIF path valid; redact enabled
- [ ] Replace hardcoded creds in tests with `os.getenv("TEST_*", "dummy")`

Acceptance
- [ ] gitleaks clean; tests do not emit secrets

7) MΛTRIZ Minimal Viable Artifacts — Owner: Claude Code (lead) + Codex (implement)
- [ ] Define typed dataclasses for node schema (TYPE/STATE/LINKS/EVOLVES_TO/TRIGGERS/REFLECTIONS)
- [ ] Provide JSON Schema for node validation
- [ ] Add round‑trip/evolution unit tests (markers: consciousness, smoke)

Acceptance
- [ ] Schema + tests merged; tests green

8) Commit & CI — Owner: Codex
- [ ] Commit by theme; enable pre‑commit; ensure lint/type/tests run in CI

Acceptance
- [ ] CI green on lint, type, tests, gitleaks

Daily Standup Template
- Completed: …
- In Progress: …
- Blockers/Risks: …
- Next 24h: …

Readiness Targets
- Performance: P95 API <25ms
- Security: 0 vulns, <0.15 drift
- Testing: 95%+ coverage (path from 85%)
- Operations: 99.99% uptime, full observability

Notes
- For detailed rationale and configs, see docs/audits/AUDIT_PLAN.md.
- Keep this board concise; link to diffs or PRs for details.

