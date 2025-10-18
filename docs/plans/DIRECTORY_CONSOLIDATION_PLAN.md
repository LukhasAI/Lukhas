---
title: Directory Consolidation Plan
date: 2025-10-18
status: ready-for-execution
priority: medium
estimated_cleanup: 132 directories
---

# Directory Consolidation Plan

## Executive Summary

After Phase 5B flattening, we have **132 directories** containing only 1-3 files that are candidates for deletion or consolidation. This cleanup will improve repository navigation and reduce clutter.

## Breakdown

| Category | Count | Action |
|----------|-------|--------|
| Empty `__init__.py` only | 40 | DELETE |
| `.gitkeep` only | 2 | DELETE |
| Labs shims (empty `__init__.py`) | 90 | DELETE |
| Sparse test directories | 86 | CONSOLIDATE |
| Sparse product directories | 5 | REVIEW |
| **TOTAL** | **132** | - |

---

## Category 1: Empty `__init__.py` Only (40 directories)

### Safe to Delete Immediately

These directories contain only empty or near-empty `__init__.py` files and serve no purpose.

```bash
# Bio awareness shims (4 dirs)
bio/awareness/advanced_quantum_bio/
bio/awareness/awareness/
bio/awareness/enhanced_awareness/
bio/awareness/quantum_bio_components/

# Bio core shims (7 dirs)
bio/core/memory/
bio/core/memory/quantum_memory_manager/
bio/core/oscillator/
bio/core/oscillator/orchestrator/
bio/core/oscillator/quantum_inspired_layer/
bio/core/voice/
bio/core/voice/quantum_voice_enhancer/

# Bio symbolic shims (2 dirs)
bio/symbolic/glyph_id_hash/
bio/symbolic/symbolic_world/

# Bridge legacy (1 dir)
bridge/api_legacy/commercial/

# Core shims (1 dir)
core/matriz/

# Deployment shims (1 dir)
deployment/platforms/memory_services/memory_services/

# Governance shims (3 dirs)
governance/extended/audit_logger/
governance/extended/compliance_hooks/
governance/extended/policy_manager/

# Memory backend shim (1 dir)
memory/backends/filesystem/
```

**Deletion Command**:
```bash
# Remove bio shims
rm -rf bio/awareness/advanced_quantum_bio \
       bio/awareness/awareness \
       bio/awareness/enhanced_awareness \
       bio/awareness/quantum_bio_components \
       bio/core/memory \
       bio/core/oscillator \
       bio/core/voice \
       bio/symbolic/glyph_id_hash \
       bio/symbolic/symbolic_world

# Remove other shims
rm -rf bridge/api_legacy/commercial \
       core/matriz \
       deployment/platforms/memory_services/memory_services \
       governance/extended/audit_logger \
       governance/extended/compliance_hooks \
       governance/extended/policy_manager \
       memory/backends/filesystem
```

---

## Category 2: .gitkeep Only (2 directories)

These directories exist only to preserve directory structure in git but contain no actual files.

```bash
docs/reports_root/autofix/
load/results/
```

**Recommendation**: **DELETE** - Not needed after flattening

**Deletion Command**:
```bash
rm -rf docs/reports_root/autofix load/results
```

---

## Category 3: Labs Shims (90 directories)

These are empty `__init__.py` files in the `labs/` development lane. Most are leftover shims from incomplete experiments.

### High Priority Deletions (20 dirs)

```bash
labs/bio/symbolic/bio/
labs/bio/symbolic/bio/core/
labs/bio/symbolic/qi_attention/
labs/bio/symbolic/quantum_attention/
labs/core/orchestration/brain/context/
labs/core/orchestration/brain/meta/
labs/core/orchestration/brain/meta/cognition/
labs/core/orchestration/brain/meta/integrations/
labs/core/orchestration/brain/meta/learning/
labs/core/orchestration/brain/nodes/
labs/core/orchestration/brain/output/
labs/core/orchestration/brain/symbolic_ai/
labs/memory/core/brain/core/
labs/memory/core/chain/
labs/memory/core/expansion/
labs/memory/core/logging/
labs/memory/core/tracker/
labs/memory/interfaces/base/
labs/memory/interfaces/connector/
labs/orchestration/brain/attention/
```

**Deletion Command** (first 20):
```bash
rm -rf labs/bio/symbolic/bio \
       labs/bio/symbolic/qi_attention \
       labs/bio/symbolic/quantum_attention \
       labs/core/orchestration/brain/context \
       labs/core/orchestration/brain/meta \
       labs/core/orchestration/brain/nodes \
       labs/core/orchestration/brain/output \
       labs/core/orchestration/brain/symbolic_ai \
       labs/memory/core/chain \
       labs/memory/core/expansion \
       labs/memory/core/logging \
       labs/memory/core/tracker \
       labs/memory/interfaces/base \
       labs/memory/interfaces/connector \
       labs/orchestration/brain/attention
```

**Full List Available**: See analysis output for all 90 directories

---

## Category 4: Sparse Test Directories (86 dirs)

Test directories with only a single test file. These should be **consolidated** into parent directories.

### Examples:

```
tests/contract/contract/test_step_result_contract.py
  → Move to: tests/contract/test_step_result_contract.py

tests/contract/golden/test_system_reality.py
  → Move to: tests/contract/test_system_reality.py

tests/unit/golden/test_system_reality.py
  → Move to: tests/unit/test_system_reality.py
```

### Consolidation Strategy:

1. **Identify parent directory** for each sparse test dir
2. **Move test file** to parent directory
3. **Delete empty directory**

**Script to Consolidate**:
```bash
# For each sparse test directory
find tests -type d -name "*" | while read dir; do
  count=$(find "$dir" -maxdepth 1 -type f -name "test_*.py" | wc -l)
  if [ "$count" -eq 1 ]; then
    testfile=$(find "$dir" -maxdepth 1 -type f -name "test_*.py")
    parent=$(dirname "$dir")
    mv "$testfile" "$parent/"
    rmdir "$dir" 2>/dev/null || true
  fi
done
```

---

## Category 5: Sparse Products (5 dirs)

Products directories with minimal content. **REVIEW BEFORE DELETION**.

```
products/core/ (327 bytes)
products/enterprise/economic/core/ (477 bytes)
products/experience/dashboard/core/backend/infrastructure/ (54 bytes)
products/experience/modules/ (384 bytes)
products/experience/voice/bridge/interfaces/input/ (219 bytes)
```

**Recommendation**: **REVIEW CONTENTS FIRST** - May contain important initialization code

---

## Execution Plan

### Phase 1: Safe Deletions (Low Risk)
**Target**: 42 directories (empty `__init__.py` + `.gitkeep`)

```bash
# 1. Delete empty __init__.py directories
rm -rf bio/awareness/advanced_quantum_bio \
       bio/awareness/awareness \
       bio/awareness/enhanced_awareness \
       bio/awareness/quantum_bio_components \
       bio/core/memory \
       bio/core/oscillator \
       bio/core/voice \
       bio/symbolic/glyph_id_hash \
       bio/symbolic/symbolic_world \
       bridge/api_legacy/commercial \
       core/matriz \
       deployment/platforms/memory_services/memory_services \
       governance/extended/audit_logger \
       governance/extended/compliance_hooks \
       governance/extended/policy_manager \
       memory/backends/filesystem

# 2. Delete .gitkeep directories
rm -rf docs/reports_root/autofix load/results

# 3. Commit
git add -A
git commit -m "chore(cleanup): remove 42 empty shim directories

Removed directories containing only empty __init__.py or .gitkeep files:
- 15 bio shims (awareness, core, symbolic)
- 3 governance/extended shims
- 2 .gitkeep placeholders
- 22 other empty shims

Phase 5B follow-up cleanup after lukhas/ flattening.
"
```

### Phase 2: Labs Cleanup (Medium Risk)
**Target**: 90 labs shim directories

```bash
# Remove all 90 labs shim directories
# (Generate full list with Python script)
python3 - <<'PY'
from pathlib import Path

labs_shims = [
    "labs/bio/symbolic/bio",
    "labs/bio/symbolic/qi_attention",
    "labs/bio/symbolic/quantum_attention",
    # ... (all 90 directories)
]

print("rm -rf " + " \\\n       ".join(labs_shims))
PY

# Commit
git commit -m "chore(cleanup): remove 90 empty labs shim directories"
```

### Phase 3: Test Consolidation (Low Risk)
**Target**: 86 test directories

```bash
# Run consolidation script
python3 scripts/consolidate_sparse_tests.py

# Commit
git commit -m "refactor(tests): consolidate 86 sparse test directories

Moved single test files to parent directories to reduce nesting.
"
```

### Phase 4: Products Review (Manual)
**Target**: 5 product directories

```bash
# Review each manually
cat products/core/__init__.py
cat products/enterprise/economic/core/__init__.py
# ... etc

# Delete if empty, keep if has code
```

---

## Impact Analysis

### Before Cleanup:
- Directories with 1-3 files: **132**
- Cluttered navigation
- Confusing empty directories

### After Cleanup:
- Directories removed: **~130** (after products review)
- Cleaner structure
- Easier navigation
- Reduced confusion

### Risk Assessment:

| Phase | Risk | Mitigation |
|-------|------|------------|
| Phase 1 (Empty shims) | **Low** | Only empty files, git tracks changes |
| Phase 2 (Labs shims) | **Low-Medium** | Labs is development lane, experimental |
| Phase 3 (Test consolidation) | **Low** | Tests still exist, just moved up |
| Phase 4 (Products review) | **Medium** | Manual review required |

---

## Validation

After each phase:

```bash
# Check no imports broken
python3 -c "import core; import memory; import governance"

# Run smoke tests
pytest tests/smoke/ -v

# Validate manifests
python3 scripts/validate_module_manifests.py
```

---

## Rollback Plan

If issues arise:

```bash
# Revert last commit
git reset --hard HEAD^

# Or revert specific commit
git revert <commit-hash>
```

---

## Timeline

- **Phase 1**: 15 minutes (safe deletions)
- **Phase 2**: 20 minutes (labs cleanup)
- **Phase 3**: 30 minutes (test consolidation)
- **Phase 4**: 20 minutes (products review)

**Total**: ~1.5 hours

---

## Recommendation

**Start with Phase 1** (42 directories) - safest, highest impact.

Execute immediately:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout -b chore/directory-cleanup
# Run Phase 1 commands above
git push origin chore/directory-cleanup
```

After validating Phase 1 success, proceed to Phase 2-4.

---

**Status**: Ready for execution
**Estimated cleanup**: 130+ directories
**Estimated time**: 1.5 hours
