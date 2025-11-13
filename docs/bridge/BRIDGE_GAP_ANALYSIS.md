# Bridge Gap Analysis - Root Cause of Smoke Test Failures

**Date:** 2025-11-03
**Issue:** 211 smoke test collection errors
**Root Cause:** Missing bridge module exports for 786 labs/* modules

---

## Executive Summary

The automation script revealed that **the files exist** but aren't accessible due to missing bridge module exports. When tests import `consciousness.dream.expand.mesh`, the file exists at `labs/consciousness/dream/expand/mesh.py` but the bridge at `consciousness/dream/expand/__init__.py` doesn't expose it.

**Key Insight:** We don't need to create stub files - we need to add exports to existing bridge `__init__.py` files.

---

## The Pattern

### Current Structure:
```
labs/consciousness/dream/expand/mesh.py  ← File EXISTS
consciousness/dream/expand/__init__.py   ← Bridge EXISTS but doesn't export mesh
```

### What Tests Do:
```python
from consciousness.dream.expand import mesh  # ❌ ModuleNotFoundError
```

### Why It Fails:
The bridge `__init__.py` uses `bridge()` function to dynamically import from `labs.*`, but individual modules like `mesh` must be explicitly added as fallback stubs.

---

## Scale of the Problem

### Total Gaps: **786 modules**

**Distribution by category:**
- consciousness/* - ~150 modules
- memory/* - ~120 modules
- governance/* - ~80 modules
- core/* - ~100 modules
- bridge/* - ~60 modules
- qi/* - ~50 modules
- emotion/* - ~40 modules
- identity/* - ~30 modules
- Other - ~156 modules

---

## High-Impact Missing Bridges (Top 20)

These cause the most test failures (count = number of test failures):

| Count | Module | Location |
|-------|--------|----------|
| 7 | lukhas.identity | lukhas/identity/__init__.py |
| 7 | governance.ethics | governance/ethics/__init__.py |
| 6 | memory.backends | memory/backends/__init__.py |
| 5 | labs.governance.guardian_system_integration | N/A (needs creation) |
| 5 | aka_qualia.core | aka_qualia/core.py (needs creation) |
| 4 | qi.compliance | qi/compliance.py (needs creation) |
| 4 | governance.guardian_system | governance/__init__.py |
| 4 | candidate.consciousness | candidate/consciousness/__init__.py |
| 3 | tiers | tiers/__init__.py (needs creation) |
| 3 | monitoring.drift_manager | monitoring/drift_manager.py (needs creation) |
| 3 | memory.adaptive_memory | memory/__init__.py |
| 3 | labs.core.orchestration.async_orchestrator | core/orchestration/__init__.py |
| 3 | governance.schema_registry | governance/__init__.py |
| 3 | core.security.auth | core/security/__init__.py |
| 3 | cognitive_core.reasoning.contradiction_integrator | cognitive_core/reasoning/__init__.py |
| 2 | qi.bio | qi/__init__.py |
| 2 | memory.indexer | memory/__init__.py |
| 2 | lukhas_website.core | lukhas_website/core/__init__.py |
| 2 | ethics.core | ethics/core.py (needs creation) |
| 2 | core.matriz | core/__init__.py |

---

## Fix Strategy

### Phase 1: Quick Wins (Target: Fix Top 5)
Focus on modules with 5+ failures each:

1. **lukhas.identity** (7 failures)
   - Check if `lukhas/identity/` exists in labs
   - Add bridge in `lukhas/__init__.py`

2. **governance.ethics** (7 failures)
   - Check `labs/governance/ethics/`
   - Add to `governance/__init__.py`

3. **memory.backends** (6 failures)
   - Check `labs/memory/backends/`
   - Add to `memory/__init__.py`

4. **labs.governance.guardian_system_integration** (5 failures)
   - Direct labs import - may just need the module to exist

5. **aka_qualia.core** (5 failures)
   - Check if `labs/aka_qualia/core.py` exists
   - Create `aka_qualia/core.py` bridge

### Phase 2: Medium Impact (Target: Fix Next 10)
Modules with 3-4 failures each

### Phase 3: Long Tail (Remaining 786)
Use automation script to bulk-create remaining bridges

---

## Automated Fix Approach

### Option A: Targeted Bridge Addition Script

```python
#!/usr/bin/env python3
"""
Add missing module exports to existing bridge __init__.py files.
Reads high-impact missing modules and adds try/except import stubs.
"""

HIGH_IMPACT = [
    ("lukhas.identity", "lukhas/__init__.py"),
    ("governance.ethics", "governance/__init__.py"),
    ("memory.backends", "memory/__init__.py"),
    # ... etc
]

for module_name, bridge_file in HIGH_IMPACT:
    # Check if labs version exists
    labs_path = f"labs/{module_name.replace('.', '/')}.py"
    if Path(labs_path).exists() or Path(labs_path.replace('.py', '')).is_dir():
        # Add to bridge
        add_bridge_export(bridge_file, module_name)
```

### Option B: Bulk Bridge Generator

Generate complete bridge `__init__.py` files based on actual `labs/*` structure:

```python
def generate_bridge_init(bridge_dir: Path, labs_dir: Path):
    """Generate complete bridge __init__.py from labs/* contents."""
    modules = [f.stem for f in labs_dir.glob("*.py") if f.stem != "__init__"]

    template = '''"""Bridge for {module}."""
from __future__ import annotations

from _bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=("labs.{module}",),
    deprecation="Import from public API instead."
)

globals().update(_exports)
del _mod, _exports

# Individual module exports
{exports}
'''
    # Generate exports for each module...
```

---

## Expected Outcomes

### Phase 1 (Top 5 fixes):
- **Expected reduction:** 28 errors → ~180 errors (15% improvement)
- **Time estimate:** 30 minutes
- **Risk:** Low (only touching 5 bridge files)

### Phase 2 (Next 10 fixes):
- **Expected reduction:** 180 → ~140 errors (25% total improvement)
- **Time estimate:** 1 hour
- **Risk:** Low-Medium

### Phase 3 (Bulk automation):
- **Expected reduction:** 140 → <50 errors (75% total improvement)
- **Time estimate:** 2-3 hours (script development + testing)
- **Risk:** Medium (bulk changes require careful testing)

---

## Lessons Learned

1. **Stubs aren't the answer** - The automation script's stub generation approach was wrong. We don't need to create new files, we need to expose existing files.

2. **Bridge pattern is powerful but incomplete** - The `bridge()` function dynamically imports from labs, but individual modules need explicit exports.

3. **Scale matters** - 786 missing exports is too large for manual fixes. Automation is essential.

4. **Discovery > Fixing** - Finding the right problem (bridge gaps) is more valuable than applying the wrong solution (creating stubs).

---

## Tools Created

1. **`scripts/find_bridge_gaps.py`** - Identifies all 786 gaps
2. **`release_artifacts/matriz_readiness_v1/discovery/bridge_gaps.txt`** - Complete list

---

## Next Actions

**Immediate (Today):**
1. Create `scripts/fix_high_impact_bridges.py` targeting top 20
2. Run and test on top 5 first
3. Commit and re-run smoke tests
4. Measure error reduction

**Short-term (This Week):**
1. Develop bulk bridge generator
2. Test on subset of modules
3. Roll out to all 786 gaps
4. Target: <10 collection errors

**Long-term (Next Sprint):**
1. Add pre-commit hook to detect bridge gaps
2. Auto-generate bridges when new labs/* modules added
3. Document bridge pattern in architecture docs

---

**Status:** Analysis complete. Ready for Phase 1 implementation.
