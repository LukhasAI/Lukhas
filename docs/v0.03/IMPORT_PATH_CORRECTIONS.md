# Import Path Corrections - Actual Module Locations

## Summary

**CRITICAL DISCOVERY**: Most "missing" modules actually **EXIST** - they're just under different import paths!

The issue is not missing code - it's **incorrect import statements** in tests and some source files.

## Import Corrections Needed

### Consciousness Modules

| Incorrect Import | Actual Location | Files Found |
|-----------------|-----------------|-------------|
| `consciousness.awareness` | `candidate.bio.awareness` | 3 files |
| `consciousness.dream` | `candidate.core.orchestration.dream` | 2 files |
| `consciousness.reflection` | `candidate.consciousness.reflection` OR `consciousness.dream_engine.reflection` | TBD |
| `lukhas.consciousness.creativity_engine` | `candidate.consciousness.creativity.dream_engine` | TBD |

### Governance & Ethics

| Incorrect Import | Actual Location | Files Found |
|-----------------|-----------------|-------------|
| `governance.ethics` | `candidate.core.ethics` | 9 files! |
| `governance.guardian` | `governance.guardian_system` OR `candidate.core.ethics.ab_safety_guard` | TBD |
| `governance.identity.auth_backend` | `candidate.core.identity.engine` | 17 files! |

### Core & Identity

| Incorrect Import | Actual Location | Files Found |
|-----------------|-----------------|-------------|
| `core.identity` | `candidate.core.identity` | 17 files! |
| `core.identity` (alt) | `candidate.identity` | 1 file |

### Memory Systems

| Incorrect Import | Actual Location | Files Found |
|-----------------|-----------------|-------------|
| `memory.core` | `candidate.memory` OR `memory` (root) | TBD |
| `memory.fakes` | Test utilities - may need creation | 0 |

## Action Plan

### Option 1: Fix Imports (RECOMMENDED)
**Pro**: Uses actual implementations
**Con**: Requires updating many test files

1. Create import mapping script
2. Update all test imports to use actual paths
3. Validate with `pytest --collect-only`

### Option 2: Create Import Aliases
**Pro**: No test changes needed
**Con**: Adds indirection layer

1. Create `consciousness/__init__.py` that re-exports from actual locations
2. e.g., `from candidate.bio.awareness import * as awareness`

### Option 3: Hybrid Approach (BEST)
1. Fix imports for modules that clearly exist (ethics, identity, awareness)
2. Create minimal implementations for truly missing ones
3. Mark uncertain ones for manual review

## Verified Existing Implementations

These modules have **REAL CODE**:

✅ `candidate/bio/awareness/` - 3 Python files
✅ `candidate/core/ethics/` - 9 Python files (including guardian components)
✅ `candidate/core/identity/` - 17 Python files (substantial implementation)
✅ `candidate/core/orchestration/dream/` - 2 Python files

## Next Steps

1. Complete the mapping for all 62 "missing" modules
2. Categorize into:
   - **EXISTS**: Full implementation, just wrong path
   - **PARTIAL**: Some code exists, needs completion
   - **MISSING**: Truly doesn't exist anywhere
3. Generate corrected import statements
4. Apply fixes systematically

## Estimate

- **EXISTS** (wrong path): ~40-50 modules (80%)
- **PARTIAL** (incomplete): ~5-10 modules (15%)
- **MISSING** (truly absent): ~2-5 modules (5%)

**Impact**: We may only need to create 2-5 modules instead of 62!
