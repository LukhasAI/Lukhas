---
status: wip
type: documentation
---
# /full-diagnostic
Goal: run a comprehensive diagnostic suite on ~/Lukhas to surface all broken areas (memory, imports, logic) before MATRIZ planning.

## Steps
1) Environment prep
   - Ensure venv active, install requirements + test requirements.
2) Categorize errors
   - Run: pytest -q --maxfail=50 --disable-warnings | tee reports/deep_search/PYTEST_RAW.txt
   - Parse output: categorize into ImportError, MemoryError, AssertionError, Other.
   - Write structured report to reports/deep_search/DIAGNOSTIC_REPORT.md
3) Memory focus
   - Run targeted tests in lukhas/memory and candidate/memory
   - Note: imports working? functions callable? Save results to reports/deep_search/MEMORY_STATUS.md
4) Output in chat
   - Summary table: Error type | Count | Top examples
   - Green/Yellow/Red status per lane (from ops/matriz.yaml + test results)
   - Next 3 recommended fixes (smallest impact first)

## Acceptance criteria
- All results written under reports/deep_search/
- Chat output shows concise triage, not full tracebacks
- No structural changes — diagnostic onlyjus11
