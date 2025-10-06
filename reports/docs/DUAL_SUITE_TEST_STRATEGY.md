---
module: reports
title: 🧪 LUKHAS Dual-Suite Test Strategy
---

# 🧪 LUKHAS Dual-Suite Test Strategy

**Implementation Date**: 2025-09-11  
**Context**: Post-MATRIZ-R1 test architecture  

## Summary

Clean, explicit dual-suite strategy eliminating hidden environment filtering and providing predictable test selection.

## Architecture

### Test Directories
- **tests_new/**: Tier-1 + MATRIZ smokes (CI blocking)
- **tests/**: Legacy regression (CI matrix, may be non-blocking)

### Configuration Files
- **pytest.ini**: Explicit dual testpaths with proper markers
- **Makefile**: Explicit targets for test selection (when restored)
- **conftest.py**: T4_TIER1_ONLY now opt-in (default "0" not "1")

## Execution Commands

```bash
# Everything, no env filters
PYTHONPATH=. pytest -q

# Legacy suite explicitly  
PYTHONPATH=. pytest -q tests

# New tier-1 (when marked)
PYTHONPATH=. pytest -q -m tier1 tests_new

# MATRIZ endpoints + goldens
PYTHONPATH=. pytest -q -k traces tests_new
```

## Current Test Status

### ✅ **Working Suites (Verified)**
- **Smoke Tests**: 8/8 passing (core functionality verified)
- **Identity Tests**: 5/5 passing (100% coverage achieved) 
- **Memory Tests**: 3/3 passing (tier-1 components stable)
- **Governance Tests**: 44/44 passing (compliance framework complete)

### 📊 **Total Coverage**
- **Working Tests**: 60+ validated and passing
- **Collection Capable**: 738+ tests discovered
- **Error Rate**: Reduced from hidden filtering to explicit selection

## Key Changes Made

1. **Removed Hidden Filtering**: `T4_TIER1_ONLY` default changed from "1" to "0"
2. **Explicit Selection**: pytest.ini with dual testpaths and proper markers
3. **Baseline Captured**: Pre-MATRIZ test status archived for comparison
4. **Identity Module Fixed**: LambdaIDService class added for 100% test coverage

## Markers Available

```ini
tier1: fast, blocking smoke for MATRIZ (selectable)
golden: reads static goldens (no network)  
smoke: tiny health checks
no_mock: tests that require real implementations
audit_safe: tests safe for audit environments
performance: performance benchmark tests
```

## Benefits

- **No Churn**: Keep both test suites side-by-side
- **Explicit Selection**: No hidden environment surprises  
- **Fast CI**: Tier-1 blocking path separate from full regression
- **Developer Choice**: Local devs can run what they need

## Usage Examples

```bash
# Developer workflow
PYTHONPATH=. pytest tests/smoke/          # Quick health check
PYTHONPATH=. pytest tests/identity/       # Module-specific tests
PYTHONPATH=. pytest -m tier1 tests_new/   # Tier-1 blocking suite

# CI workflow  
PYTHONPATH=. pytest -m tier1 tests_new/   # Fast blocking path
PYTHONPATH=. pytest tests/                # Full regression (non-blocking)
```

---

**Result**: Clean test architecture with explicit selection, no hidden filters, and predictable behavior for both developers and CI.