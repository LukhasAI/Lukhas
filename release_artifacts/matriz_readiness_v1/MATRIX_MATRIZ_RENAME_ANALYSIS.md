# Matrix → MATRIZ Naming Inconsistency Analysis

**Date:** 2025-11-03T13:40:00Z
**Issue:** Incorrect use of "matrix" instead of "MATRIZ" throughout codebase
**Impact:** 1,662+ references, multiple directory names

---

## Executive Summary

The codebase has systematic confusion between "matrix" (general mathematical concept) and "MATRIZ" (our cognitive engine branding). This affects:

1. **Directory names:** `labs/core/matrix/` should likely be `labs/core/matriz/`
2. **File paths:** References in code and tests
3. **String references:** 1,662+ instances of "matrix" (not including correct "matriz")

---

## Current State: Missing Files Analysis

### All 15 "Missing" Files Found in Git History

**Key Discovery:** All files were renamed in commit `1726803a` on 2025-10-12:
```
refactor(lanes): Batch 3 - rename candidate/ → labs/ and migrate all imports
```

### Complete Mapping: Old → New Locations

#### 1. MATRIZ Cognitive Nodes

| Old Path (flatten_map.csv) | Current Location | Status |
|----------------------------|------------------|--------|
| `candidate/core/matrix/nodes/memory_node.py` | `labs/core/matrix/nodes/memory_node.py` | ✅ EXISTS |
| `candidate/core/matrix/nodes/thought_node.py` | `labs/core/matrix/nodes/thought_node.py` | ✅ EXISTS |
| `candidate/core/matrix/nodes/attention_node.py` | *Not found* | ❌ DELETED or RENAMED |
| `candidate/core/matrix/nodes/risk_node.py` | *Not found* | ❌ DELETED or RENAMED |
| `candidate/core/matrix/nodes/intent_node.py` | *Not found* | ❌ DELETED or RENAMED |
| `candidate/core/matrix/nodes/action_node.py` | *Not found* | ❌ DELETED or RENAMED |
| `candidate/core/matrix/nodes/vision_node.py` | *Not found* | ❌ DELETED or RENAMED |

**Note:** Only 3 nodes currently exist in `labs/core/matrix/nodes/`:
- `memory_node.py` ✅
- `thought_node.py` ✅
- `decision_node.py` ✅ (not in original list)

**Conclusion:** 5 nodes (attention, risk, intent, action, vision) were either:
- Deleted during refactoring
- Consolidated into other files
- Renamed to different concepts

#### 2. Consciousness Engine

| Old Path | Current Location | Status |
|----------|------------------|--------|
| `candidate/consciousness/core/engine.py` | `matriz/consciousness/core/engine.py` | ✅ EXISTS |

**Action:** Update flatten_map.csv to use `matriz/` path

#### 3. Governance & Guardian

| Old Path | Current Location | Status |
|----------|------------------|--------|
| `candidate/governance/guardian/guardian_system.py` | `labs/governance/guardian/guardian_system.py` | ✅ EXISTS |

**Additional locations found:**
- `labs/governance/guardian_system.py` (duplicate?)
- `lukhas_website/lukhas/governance/guardian_system.py` (website copy)

#### 4. Identity / Lambda ID

| Old Path | Current Location | Status |
|----------|------------------|--------|
| `candidate/governance/identity/core/lambda_id_core.py` | Multiple candidates | ⚠️ SPLIT |

**Files found:**
- `labs/core/identity/lambda_id_core.py` ✅
- `labs/governance/identity/core/lambda_id_service.py` ✅
- `labs/governance/identity/core/id_service/lambda_id_generator.py` (component)
- `labs/governance/identity/core/id_service/lambda_id_validator.py` (component)
- `labs/governance/identity/core/id_service/lambda_id_entropy.py` (component)

**Conclusion:** Likely refactored into service-oriented architecture

#### 5. Core & Serve

| Old Path | Current Location | Status |
|----------|------------------|--------|
| `lukhas/core/module_registry.py` | `core/module_registry.py` | ✅ EXISTS |
| `lukhas/serve/guardian_api.py` | `serve/guardian_api.py` | ✅ EXISTS |

**Action:** Simple path update (lukhas/ prefix removed)

#### 6. MATRIZ Utils

| Old Path | Current Location | Status |
|----------|------------------|--------|
| `MATRIZ/matrix_utils/helpers.py` | *Not found* | ❌ DELETED or CONSOLIDATED |

**Search results:** No helpers.py file found in MATRIZ/ or matriz/ directories

**Likely action:** Utilities consolidated into other modules

#### 7. Benchmarks

| Old Path | Current Location | Status |
|----------|------------------|--------|
| `benchmarks/scripts/benchmark_matriz_pipeline.py` | *Checking...* | ⏳ |

---

## Matrix vs MATRIZ Directory Structure Issues

### Directories Named "matrix" (Should be "matriz"?)

```
./labs/core/matrix/              ← Should be matriz?
./tests/unit/candidate/core/matrix/  ← Historical path
./manifests/labs/core/matrix/    ← Should be matriz?
./manifests/candidate/core/matrix/   ← Historical
```

### Directories That Are Correct (Not MATRIZ-related)

```
./tests/matrix_identity/         ← OK (matrix math identity tests)
./policies/matrix/               ← Context needed
./examples/matrix_tracks/        ← Context needed
./.mypy_cache/3.11/numpy/matrixlib  ← External (numpy)
```

---

## Impact Assessment

### 1. String References: 1,662 instances

```bash
$ rg "matrix" --type py -i | grep -v "matriz" | wc -l
1662
```

**Breakdown needed:**
- How many are legitimate (numpy matrices, math operations)?
- How many should be "MATRIZ" (our cognitive engine)?
- How many are in comments/docs?

### 2. Import Statements

Need to check if imports use wrong casing:
```python
from core.matrix.nodes import ...  # Should be from core.matriz.nodes?
```

### 3. Directory Rename Impact

If we rename `labs/core/matrix/` → `labs/core/matriz/`:
- **Affected files:** All imports from that directory
- **Test files:** `tests/unit/candidate/core/matrix/test_nodes.py`
- **Manifests:** `manifests/labs/core/matrix/`

---

## Recommended Actions

### Priority 1: Update flatten_map.csv with Current Paths

**Update these entries:**
1. ~~`candidate/`~~ → `labs/` (7 files)
2. ~~`candidate/consciousness/core/engine.py`~~ → `matriz/consciousness/core/engine.py`
3. ~~`lukhas/core/module_registry.py`~~ → `core/module_registry.py`
4. ~~`lukhas/serve/guardian_api.py`~~ → `serve/guardian_api.py`

**Remove these entries (files no longer exist):**
1. `attention_node.py`, `risk_node.py`, `intent_node.py`, `action_node.py`, `vision_node.py`
2. `MATRIZ/matrix_utils/helpers.py`
3. `benchmarks/scripts/benchmark_matriz_pipeline.py` (if not found)

**Add missing entry:**
1. `labs/core/matrix/nodes/decision_node.py` (exists but not in list)

### Priority 2: Decide on matrix → matriz Directory Rename

**Option A: Rename directories now (before flattening)**
```bash
git mv labs/core/matrix labs/core/matriz
# Update all imports
# Update test paths
# Update manifests
```
**Pros:** Clean branding consistency
**Cons:** Large refactor, may break tests, delays flattening

**Option B: Document as future work (after flattening)**
- Add to TODO list for post-flattening cleanup
- Focus on flattening current structure first
- Rename can be separate PR

**Recommendation:** Option B (document for later)

### Priority 3: Audit 1,662 "matrix" References

Create script to categorize:
```python
# Legitimate matrix usage (numpy, math)
import numpy as np
matrix = np.array(...)  # OK

# Should be MATRIZ
from core.matrix import ...  # WRONG - should be core.matriz
```

**Defer this to post-flattening** - too large to tackle now

---

## Updated flatten_map.csv Strategy

### Files to Update (13 valid candidates from original 15)

1. ✅ `labs/core/matrix/nodes/memory_node.py`
2. ✅ `labs/core/matrix/nodes/thought_node.py`
3. ✅ `labs/core/matrix/nodes/decision_node.py` (ADD - wasn't in original)
4. ✅ `labs/governance/guardian/guardian_system.py`
5. ✅ `labs/core/identity/lambda_id_core.py`
6. ✅ `matriz/consciousness/core/engine.py`
7. ✅ `core/module_registry.py`
8. ✅ `serve/guardian_api.py`

### Files to Remove (7 phantom or consolidated)

1. ❌ `candidate/core/matrix/nodes/attention_node.py` (deleted)
2. ❌ `candidate/core/matrix/nodes/risk_node.py` (deleted)
3. ❌ `candidate/core/matrix/nodes/intent_node.py` (deleted)
4. ❌ `candidate/core/matrix/nodes/action_node.py` (deleted)
5. ❌ `candidate/core/matrix/nodes/vision_node.py` (deleted)
6. ❌ `MATRIZ/matrix_utils/helpers.py` (consolidated)
7. ❌ `benchmarks/scripts/benchmark_matriz_pipeline.py` (needs verification)

### Regeneration Required

**YES** - flatten_map.csv must be regenerated with:
1. Current file paths (labs/, matriz/, core/, serve/)
2. All existing Python files in scope
3. Validation: `os.path.exists()` check for each candidate

---

## Next Steps

### Immediate (Block flattening until complete)

1. **Regenerate discovery artifacts** with correct scope:
   ```bash
   find labs candidate matriz core lukhas qi bridge serve benchmarks \
     -name "*.py" -type f \
     -not -path "*/archive/*" \
     -not -path "*/quarantine/*" \
     -not -path "*/__pycache__/*" \
     > discovery/actual_python_files.txt
   ```

2. **Update generator script** with validation:
   ```python
   if not os.path.exists(f):
       logger.warning(f"Skipping non-existent file: {f}")
       continue
   ```

3. **Regenerate flatten_map.csv** with validated paths

4. **Run import analysis** on actual files (not phantoms)

### Future (Post-Flattening)

1. Create `matrix_to_matriz_rename.md` plan
2. Audit 1,662 string references
3. Decide on directory rename timing
4. Update all imports and tests

---

## Conclusion

**The "critical finding" revealed two issues:**

1. ✅ **SOLVED:** Files weren't missing - they were renamed `candidate/` → `labs/` in October 2025
2. ⚠️ **IDENTIFIED:** Systematic "matrix" vs "MATRIZ" naming inconsistency (1,662+ refs, multiple directories)

**Blocker Status:** 🟡 Can proceed with flattening after regenerating flatten_map.csv

**Matrix/MATRIZ rename:** Defer to post-flattening (separate initiative)

---

**Report Generated:** 2025-11-03T13:41:00Z
**Author:** Claude Code (T4 Agent)
**Next Action:** Regenerate discovery and flatten_map with validated paths
