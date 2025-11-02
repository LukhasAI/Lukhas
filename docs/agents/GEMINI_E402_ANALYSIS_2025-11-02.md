# E402 Remaining Violations Analysis

**Date**: November 2, 2025
**Agent**: Gemini Code Assist
**Context**: Post-PR #836, which fixed 65 files.

---

## Summary

**Total:** 112 violations across 48 files

**Top Directories by Violation Count:**
- `candidate/`: 45 violations (defer)
- `core/`: 28 violations ⚠️ **HIGH PRIORITY**
- `lukhas/`: 15 violations ⚠️ **HIGH PRIORITY**
- `tests/`: 12 violations
- `matriz/`: 8 violations ⚠️ **HIGH PRIORITY**
- `tools/`: 4 violations

---

## Recommended Next Batch

Based on the analysis, the next batch should focus on the 21 files with violations in the `core/`, `lukhas/`, and `matriz/` directories. These are high-priority areas and represent a significant portion of the remaining issues outside of the deferred `candidate/` directory.

**Total files for next batch:** 21