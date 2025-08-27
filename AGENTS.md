# Repository Guidelines

## Project Structure & Modules
- Source lanes: `candidate/` (experimental) and `lukhas/` (stable). Always confirm your lane before coding.
- Key folders: `agents/` (agent configs), `docs/` (architecture, guides), `branding/` (policy, tone), `tests/` (pytest), `tools/` (analysis, CI helpers), `serve/` (API), `scripts/` (ops), `api/` (audit server).
- Entrypoints: `main.py`, `production_main.py`, API apps in `lukhas.api.app` and `serve.main`.

## Build, Run, Test
- Setup: `make bootstrap` (installs deps + hooks) or `make install` then `make setup-hooks`.
- Run API (dev): `make dev` (serve `serve.main`) or `make api` (serve `lukhas.api.app`).
- Main system: `python main.py --consciousness-active`.
- Tests: `make test` (pytest), `make test-cov` (coverage), `make smoke` (smoke checks).
- Quality gates: `make fix && make lint && make test && npm run policy:all`.

## Coding Style & Naming
- Python: Black (line length 88), Ruff, isort, Flake8, MyPy; security via Bandit. Use `make format`, `make lint`, `make fix`.
- Conventions: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE`.
- Keep public APIs typed; prefer small, cohesive modules respecting the lane boundaries.

## Testing Guidelines
- Framework: pytest. Patterns: files `test_*.py` or `*_test.py`; classes `Test*`; functions `test_*`.
- Location: `tests/` mirrors module paths.
- Targets: Aim ≥85% test pass rate; add coverage with `make test-cov`. Mark slow/integration with `@pytest.mark.slow` / `integration`.

## Commit & Pull Requests
- Commits: follow Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`, `chore(deps):`). Prefer small, scoped changes per lane.
- PRs: include clear description, linked issues, test evidence (logs or screenshots), and note lane (`candidate` vs `lukhas`). Ensure quality gates pass and policy checks are green.

## Security, Policy & Branding
- Run: `make security` (scan) or `make security-audit` (reports). Sensitive changes require audit notes in PRs.
- Policy/brand: `npm run policy:all`. Use “LUKHAS AI”, “quantum-inspired”, “bio-inspired”. Avoid superlatives and “production-ready” claims without approval.

## Agent-Specific Notes
- Coordinate via `agents/` configs and follow collaboration rules: check existing work, document progress, respect lanes, maintain ≥85% test pass rate.

## References
- Workspace guide: [agents/README.md](agents/README.md)
- Architecture: [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Claude agents: [CLAUDE.md](CLAUDE.md)
- Branding policy: [branding/policy/BRANDING_POLICY.md](branding/policy/BRANDING_POLICY.md)
- Tone system: [branding/tone/LUKHAS_3_LAYER_TONE_SYSTEM.md](branding/tone/LUKHAS_3_LAYER_TONE_SYSTEM.md)
- Agent quick commands: [agents/AGENT_QUICK_REFERENCE.md](agents/AGENT_QUICK_REFERENCE.md)
