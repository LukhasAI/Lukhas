---
status: updated
type: documentation
---
# Test Suite Known Issues

> Last Updated: 2025-01-13  
> Status: 7546/7574 tests collectable (99.6% success rate)  
> Collection Errors: 226 remaining (down from 435, 48% reduction)

## ✅ Recently Resolved Issues

### ISSUE-000: Test Infrastructure Failures (P0)
**Status:** ✅ RESOLVED (2025-01-13)  
**Impact:** Massive - 435 collection errors → 226 collection errors

**What Was Fixed:**
1. Invalid pytest.ini configuration - Removed invalid timeout option and --maxfail=1
2. Missing dependencies - Installed all dev requirements via uv
3. Pydantic V1→V2 migration - Migrated 5 validators in aka_qualia/models.py
4. Test execution method - Documented requirement to use python -m pytest

**Resolution:** See commits 08f9d8db and 9aaa3d4e

---

## 🟠 High Priority Issues (P1)

### ISSUE-100: urllib3.util Import Errors (14 occurrences)
**Status:** 🔴 Active | **Priority:** P1  
Tests using deprecated urllib3 API

### ISSUE-101: lukhas.orchestrator Module Structure (7 occurrences)
**Status:** 🟡 Active | **Priority:** P1  
Module path changed or tests reference old structure

### ISSUE-102: lukhas.features Module References (7 occurrences)
**Status:** 🟡 Active | **Priority:** P1  
Module may have been renamed or relocated

## 🟡 Medium Priority Issues (P2)

### ISSUE-200: aka_qualia.core Experimental References (5 occurrences)
**Status:** 🟡 Active | **Priority:** P2  
Tests reference aka_qualia.core structure that may have changed

### ISSUE-201: Candidate Consciousness Module Integration (4 occurrences)
**Status:** 🟡 Active | **Priority:** P2  
Experimental features in candidate/ not fully integrated

### ISSUE-202: Redis Dependency Configuration
**Status:** 🟡 Active | **Priority:** P2  
Redis library not installed or not imported properly

## 📊 Summary

| Priority | Total | Resolved | Active |
|----------|-------|----------|--------|
| P0       | 1     | 1        | 0      |
| P1       | 3     | 0        | 3      |
| P2       | 3     | 0        | 3      |
| **Total**| **7** | **1**    | **6**  |

## 🎯 Next Actions
1. Fix urllib3.util imports (ISSUE-100)
2. Update lukhas.orchestrator paths (ISSUE-101)
3. Resolve lukhas.features imports (ISSUE-102)

*Full details: See TEST_STATUS.md*
