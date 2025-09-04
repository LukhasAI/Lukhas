### Voice readiness (Option D focused) — 2025-09-04
- pytest (tests/contract/test_healthz_voice_required.py): 2 passed
- ruff (serve/main.py, tests/contract/test_healthz_voice_required.py): 0 issues
- mypy (serve/main.py, scoped flags): success (follow-imports=skip, ignore-missing-imports)

Suppression:
- serve/main.py: PERF203 waived inline (expires 2026-03-01). Rationale: intentional import-only voice readiness probe.
