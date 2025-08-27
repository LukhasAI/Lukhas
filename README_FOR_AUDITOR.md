# Lukhas — Auditor Guide (Phase 2)

**Intent:** Integration readiness, not feature behavior changes.

## Lanes & Source of Truth
See `ops/matriz.yaml` for lanes, owners, promotion rules, and invariants.

## Indexes (reports/deep_search/)
- `FILE_INDEX.txt` — all files
- `PY_INDEX.txt` — all Python files
- `IMPORT_SAMPLES.txt` — first 3 import lines per .py
- `WRONG_CORE_IMPORTS.txt` — legacy `from core.*` uses
- `CANDIDATE_USED_BY_LUKHAS.txt` — cross-lane imports (candidate -> lukhas)
- `SYMLINKS.txt` — symlinks present
- `ZERO_BYTES.txt` — 0-byte files
- `IMPORT_CYCLES.txt` — detected import cycles

## Smoke Tests
`tests/smoke/test_imports_light.py` imports lane root packages and asserts load.

## Known Notes
- Archive/quarantine may contain dead code — excluded by invariants.
- Some `UP006/UP035` modernizations pending; nightly autofix annotates `TODO[T4-AUTOFIX]`.

