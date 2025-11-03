# Known Issues - Pre-Audit Baseline (2025-11-03)

**Branch:** `chore/audit-bootstrap`
**Status:** DOCUMENTED - Issues exist but are pre-existing technical debt
**Audit Impact:** These issues are orthogonal to flattening analysis

---

## Executive Summary

This document captures pre-existing code quality issues identified during the pre-audit verification. These issues exist in the current codebase and are **NOT introduced by the flattening process**. They represent technical debt that should be addressed in a separate effort.

### Issue Categories

| Category | Count | Severity | Action |
|----------|-------|----------|--------|
| SyntaxErrors | ~230 | HIGH | Fix in follow-up PR |
| F821 (undefined-name) | 635 | MEDIUM | Fix missing imports |
| E402 (import-not-at-top) | 3,956 | LOW | Refactor gradually |
| E501 (line-too-long) | 27,536 | LOW | Format with Black |
| Invalid Syntax (ruff) | 1,971 | HIGH | Fix in follow-up PR |
| Other E/F errors | 1,394 | LOW-MEDIUM | Address opportunistically |

**Total Ruff Errors:** 34,462
**Auto-Fixed:** 85 errors (this commit)

---

## 1. Syntax Errors (~230 instances)

### Description
Python compilation failures scattered across labs/, products/, and other directories.

### Common Patterns
- f-string syntax errors (mismatched braces)
- EOF while scanning triple-quoted strings
- Unicode decode errors
- Unexpected characters after line continuation

### Example Locations
- Distribution: labs/ (majority), products/, various experimental modules
- These files fail `python -m compileall`

### Remediation Plan
1. Run `python -m compileall <file>` on each affected file
2. Fix syntax manually or move to archive/ if truly experimental/deprecated
3. Target: Reduce to 0 SyntaxErrors in production code (lukhas/, matriz/, core/)

### Impact on Flattening Audit
**MINIMAL** - These files likely won't be flatten candidates due to syntax issues. GPT-Pro should skip files that fail compilation.

---

## 2. F821: Undefined Name (635 instances)

### Description
References to undefined variables/classes, typically missing imports.

### Common Patterns
```python
# Missing import
EventBus  # F821: undefined
# Should be:
from orchestration.event_bus import EventBus

# Missing typing import
Sequence, Mapping, Callable  # F821
# Should be:
from typing import Sequence, Mapping, Callable
```

### Top Offenders
- `EventBus` (multiple files)
- `LukhosIDManager`
- Quantum-related classes (`QuantumSuperpositionEngine`, `QuantumMeasurement`)
- Bio-inspired classes (`ProtonGradient`, `QIAttentionGate`, `CristaFilter`)
- Typing imports (`Sequence`, `Mapping`, `Callable`)

### Remediation Plan
1. Add missing imports at module top
2. Use `ruff check --select=F821 --fix` where auto-fixable
3. Manual review for complex cases

### Impact on Flattening Audit
**LOW** - Most F821 errors are in experimental code. Core MATRIZ modules are cleaner.

---

## 3. E402: Module Import Not at Top (3,956 instances)

### Description
Import statements appearing after code execution (violates PEP 8).

### Common Pattern
```python
# Bad
def foo():
    pass

import bar  # E402

# Good
import bar

def foo():
    pass
```

### Remediation Plan
1. Move imports to module top
2. Use `isort` to organize imports
3. Fix gradually (low priority)

### Impact on Flattening Audit
**NONE** - Import location doesn't affect flattening analysis.

---

## 4. E501: Line Too Long (27,536 instances)

### Description
Lines exceeding configured line length (typically 88 or 100 characters).

### Remediation Plan
1. Run `black --line-length 100 .` (already partially applied)
2. Manual review for complex cases
3. Consider increasing line length limit to 120 for this codebase

### Impact on Flattening Audit
**NONE** - Cosmetic issue, doesn't affect functionality or flattening.

---

## 5. Invalid Syntax (ruff reports 1,971)

### Description
Ruff's parser detects syntax issues that may overlap with Python's SyntaxError detection.

### Remediation Plan
Same as SyntaxError remediation (Section 1).

---

## 6. Other E/F Errors (1,394 total)

### Breakdown
- 88 E702 (multiple-statements-on-one-line-semicolon)
- 76 E701 (multiple-statements-on-one-line-colon)
- 70 F811 (redefined-while-unused)
- 43 F401 (unused-import) **[85 fixed in this commit]**
- 22 E741 (ambiguous-variable-name)
- 17 F405 (undefined-local-with-import-star-usage)
- Various others (<15 each)

### Remediation Plan
Address opportunistically during code review and refactoring.

---

## Progress Report

### Fixed in This Commit
- **85 auto-fixable errors** (F401, F841, E702, E722)
- Commit: `2c38bf331` - "fix(lint): apply ruff auto-fixes"

### Remaining Work
- **34,462 total errors** (down from ~34,547)
- **Priority 1:** 230 SyntaxErrors + 635 F821 = **865 critical errors**
- **Priority 2:** 1,971 invalid-syntax issues
- **Priority 3:** 3,956 E402 import-location issues
- **Low Priority:** 27,536 E501 line-length issues

---

## Audit Instructions for GPT-Pro

When performing the flattening audit:

1. **Skip files with SyntaxErrors** - They are not viable flatten candidates
2. **Document F821 errors** - Note undefined names as potential import issues
3. **Ignore E402/E501** - These don't affect flattening analysis
4. **Focus on structural analysis** - Import dependencies, module depth, public APIs

### Audit Scope Clarification

- **labs/** - Production code, should be audited (despite quality issues)
- **products/** - Production deployments, should be audited
- **archive/** - Skip entirely (known deprecated code)
- **quarantine/** - Skip entirely (syntax errors, out of scope)

---

## Follow-Up Tasks

1. **Immediate (Pre-Audit)**
   - ✅ Document known issues (this file)
   - ✅ Apply auto-fixes (85 errors fixed)
   - ⏳ Push fixes to chore/audit-bootstrap

2. **Post-Audit (Separate PR)**
   - Fix 230 SyntaxErrors
   - Fix 635 F821 undefined-name errors
   - Fix 1,971 invalid-syntax errors
   - Target: <100 critical errors before v1.0

3. **Long-Term (Technical Debt)**
   - Reduce E402 import issues
   - Apply Black formatting consistently
   - Establish pre-commit hooks for quality gates

---

## Conclusion

These issues represent **pre-existing technical debt** and do NOT block the flattening audit. The audit can proceed with the understanding that:

1. Some files will be excluded due to syntax errors
2. Undefined names may indicate missing dependencies
3. The core MATRIZ/lukhas modules are higher quality than labs/products

**Recommendation:** Proceed with dry-run audit, document quality issues in audit report, and create follow-up PRs to address critical errors.

---

**Last Updated:** 2025-11-03T16:00:00Z
**Next Review:** After GPT-Pro audit completion
