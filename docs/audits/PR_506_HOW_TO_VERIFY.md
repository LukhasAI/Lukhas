# PR #506 — How to Verify (Batch 5, parts 2–4)

Use this checklist to validate Batch 5 integration on a fresh checkout.

Prereqs:
- Python 3.10+
- Repo root on PYTHONPATH (tests ensure this)

Commands:
- make lane-guard
- make imports-guard
- make smoke
- python3 -m pytest -q tests/integration -k "(validator|matriz|router) and not api" --maxfail=1 --disable-warnings || true

Expectations:
- Lane guard: Contracts kept (0 broken)
- Import contracts: All kept (0 broken)
- Smoke: 100% pass
- Optional targeted pytest: May skip/fail unrelated API modules; import-smoke around MATRIZ should pass

Notes:
- This PR normalizes imports from `MATRIZ.*` to `matriz.*` to avoid case-sensitive import issues across platforms
- No public API changes; only import paths adjusted for stability
- Docs: fixed `//` path typos in Batch 5 guide to match actual move targets

Roll-forward plan:
- After merging, re-run the three gates on `main`
- Proceed with Batch 5 part 2 moves using corrected targets from docs/audits/INTEGRATION_GUIDE_05.md

