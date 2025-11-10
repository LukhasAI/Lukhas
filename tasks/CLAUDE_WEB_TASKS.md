# CLAUDE_WEB_TASKS — Test generation & validation tasks
> For Claude Code Web. Focus: generate robust tests (pytest), build failing repros first, follow LUKHΛS Test Surgeon system prompt.

## Purpose
Claude writes tests, fixes flaky tests, generates property-based tests, and writes PR bodies according to the strict PR template. Claude must never modify protected modules or widen exception handling.

---

## Global rules for Claude

* **Tests-first**: create a minimal failing test (repro) before any new tests.
* **Determinism**: freeze time, set `PYTEST_SEED=1337`; use `freezegun`, property-based Hypothesis with fixed seeds.
* **No network**: mock/stub all network/LLM/vector store/storage calls via fixtures.
* **Artifacts required**: `reports/junit.xml`, `reports/coverage.xml`, `reports/events.ndjson`, `mutmut` report.
* **PR template**: use `.github/pull_request_template.md` strict version.

---

## Work queue (start here)

**Top-15 targets** — create tests for each in priority order. (Scores are illustrative; use `reports/evolve_candidates.json` for live values.)

1. `serve/api/integrated_consciousness_api.py` — 85% goal
2. `serve/reference_api/public_api_reference.py` — 85%
3. `serve/extreme_performance_main.py` — 85%
4. `serve/agi_enhanced_consciousness_api.py` — 85%
5. `serve/agi_orchestration_api.py` — 85%
6. `serve/openai_routes.py` — 85% (streaming tests)
7. `serve/main.py` — 85% (middleware & OTEL test)
8. `serve/feedback_routes.py` — 85%
9. `serve/routes.py` — 85%
10. `serve/storage/trace_provider.py` — 85%
11. `lukhas/identity/webauthn_verify.py` — 85%
12. `lukhas/analytics/privacy_client.py` — 85% (PII tests)
13. `lukhas/api/features.py` — 85%
14. `lukhas/features/flags_service.py` — 85%
15. `matriz/consciousness/reflection/ethical_reasoning_system.py` — 70% (metamorphic tests)

---

## Per-target template (Claude must follow)

* **Task header**: file path, coverage goal, quick rationale.
* **Create**: `tests/unit/<path>/test_<module>.py` (or multiple test files if large).
* **Fixtures**: include deterministic `client()` fixture, `freeze_time`, `block_network` as in canonical `tests/conftest.py`.
* **Mocks**: demonstrate how to mock MATRIZ/LLM and trace store.
* **Property tests**: where applicable (MATRIZ), use Hypothesis with bounded strategies and seed.
* **Mutation tests**: run `mutmut run --paths-to-mutate <changed-module>`; include `mutmut` output in PR.
* **PR body**: include Root Cause, Risk Surface, Safe Change, Tests, Coverage delta, Mutation delta, Canary, Rollback.

---

## Example PR checklist (must be in PR body)

* [ ] Minimal repro test added (failing first)
* [ ] Tests making pass added
* [ ] Coverage non-decreasing for changed files
* [ ] Mutation score non-decreasing
* [ ] `reports/junit.xml`, `reports/coverage.xml`, `reports/events.ndjson` attached
* [ ] `confidence: 0..1` and assumptions listed

---

## Commands for Claude to run locally / in CI

```bash
# run single test
pytest -q tests/unit/serve/test_main.py --maxfail=1 --disable-warnings -q

# junit + coverage
pytest -q --junitxml=reports/junit.xml
pytest --cov=. --cov-report=xml:reports/coverage.xml

# normalize events (optional)
python tools/normalize_junit.py --in reports/junit.xml --out reports/events.ndjson

# mutation testing (expensive)
mutmut run --paths-to-mutate serve/main.py
mutmut results
```

---

## Handoff to humans

* After Claude opens a draft PR, tag **labot:review-needed** and add `claude:web` label.
* Human steward runs `make test && make heal && make policy` and reviews mutation delta before converting PR from draft to ready.
