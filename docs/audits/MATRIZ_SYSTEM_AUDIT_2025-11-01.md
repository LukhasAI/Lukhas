---
status: wip
type: audit
owner: codex
module: MATRIZ
updated: 2025-11-01
---

# MATRIZ System Audit — Connectivity & Capability (2025-11-01)

This audit captures objective results from health/smoke runs, targeted MATRIZ tests, and import scans. Each actionable issue is tagged as TODO NOW and linked to the responsible file.

## Execution Summary
- make doctor — PASS with warnings (duplicate make targets; import-linter root config gaps)
- make smoke — PASS (10/10)
- make smoke-matriz — PASS (traces router)
- python3 -m pytest -q tests/matriz --maxfail=1 — FAIL at first import
- python3 -m pytest -q tests/integration/test_matriz* --maxfail=1 — FAIL at first import
- python3 scripts/consolidation/check_import_health.py --verbose — FAIL in repo root; worktree path passes (see lane-guard script)

## Test Failures (Actionable)
- TODO NOW tests/matriz/test_async_orchestrator_e2e.py:9 — ModuleNotFoundError: labs.core.orchestration.async_orchestrator [OPEN]
  - Action: add ProviderRegistry-backed adapter or conditional skip; avoid direct labs import

- TODO NOW tests/integration/test_matriz_complete_thought_loop.py:28 — ModuleNotFoundError: consciousness.matriz_thought_loop [PARTIAL]
  - Update: Added `consciousness/matriz_thought_loop.py` and package `consciousness/__init__.py`. Import still failing under pytest; likely path/package discovery issue in test runner. Follow-up: ensure repo root on PYTHONPATH during collection or adjust conftest for these tests.

## Bridges expecting consciousness.matriz_thought_loop
The following tests reference consciousness.matriz_thought_loop and may fail without a shim:

```
tests/bridges/test_consciousness_extension_bridges.py:27
tests/bridges/test_phase9_contracts.py:13
tests/bridges/test_top_missing_contracts.py:15-16
tests/soak/test_guardian_matriz_throughput.py:35
tests/bridges/test_chatgpt_bridges.py:21,35,50,103,110
tests/matriz/test_e2e_perf.py:36
tests/lint/test_lane_imports.py:70
tests/integration/test_orchestrator_matriz_roundtrip.py:32
tests/integration/test_matriz_complete_thought_loop.py:28
```

- TODO NOW tests/* (above) — Provide shim module exposing MATRIZProcessingContext/MATRIZThoughtLoop or refactor imports.

## Tests importing labs.* (sample)
Many tests import labs.* directly. Representative sample:

```
tests/matriz/test_async_orchestrator_e2e.py:9
tests/matriz/test_behavioral_e2e.py:12
tests/orchestration/test_async_orchestrator_metrics.py:12
tests/bridges/test_vector_store.py:23
tests/bridge/test_vector_store_adapter.py:7
tests/bridge/test_jwt_adapter_high_priority.py:4
tests/bridge/test_qrs_manager.py:20
tests/integration/governance/test_guardian_system_integration.py:10
tests/integration/orchestration/test_orchestration_coverage.py:42
tests/memory/test_memory_compression.py:13
tests/memory/test_memory_properties_hypothesis.py:55
tests/test_memory_integration.py:2-3
```

- TODO NOW tests/* (labs imports) — Replace direct labs import with ProviderRegistry or add conditional skips in CI profile.

## Production-lane direct matriz imports
Direct lowercase matriz imports appear in production lanes (core/ serve/). These should migrate to uppercase MATRIZ or lazy guards:

```
core/trace.py:13 — from matriz.node_contract import GLYPH
core/symbolic/dast_engine.py:214 — from matriz.core.memory_system import get_memory_system (inside try)
serve/main.py:14 — import matriz
serve/main.py:57 — from matriz.orchestration.service_async import (...)
```

- TODO NOW core/trace.py:13 — Replace with `from MATRIZ.node_contract import GLYPH` or lazy import adapter. [DONE]
- TODO NOW core/symbolic/dast_engine.py — Replace with `from MATRIZ.core.memory_system import get_memory_system`; keep try/except guard; document lane compliance. [DONE]
- TODO NOW serve/main.py — Replace matriz with MATRIZ and/or lazy import; guard availability. [PARTIAL]
  - Update: Prefer `MATRIZ` for traces router with fallback; optional async orchestrator seam still uses legacy path under try.

## Import-Health Observations
- Root exec of `check_import_health.py` fails due to missing deps/PYTHONPATH; worktree-lane-guard script succeeds by creating a venv and minimal deps.
- TODO NOW scripts/consolidation/check_import_health.py — Add guidance when deps missing; print “use scripts/run_lane_guard_worktree.sh”.

## Capability Snapshot
- MATRIZ traces router smoke: PASS
- Broader MATRIZ E2E/unit paths: blocked on labs/consciousness shims and provider wiring

## Next Actions (Suggested)
1) Migrate production-lane matriz imports (core/trace.py, core/symbolic/dast_engine.py, serve/main.py)
2) Add consciousness.matriz_thought_loop compatibility shim exporting required symbols (or refactor tests to new entrypoint)
3) Introduce ProviderRegistry-backed adapters for common labs.* usages in tests; add conditional skips where needed
4) Enhance import-health script UX and point to worktree-lane-guard path

## Command Log (evidence)
```
make doctor
make smoke
make smoke-matriz
python3 -m pytest -q tests/matriz --maxfail=1 --disable-warnings
python3 -m pytest -q tests/integration/test_matriz* --maxfail=1 --disable-warnings
python3 scripts/consolidation/check_import_health.py --verbose
rg -n "^(from|import)\s+(matriz|MATRIZ)\b" core lukhas serve -S
rg -n "^(from|import)\s+labs\b" tests
```
