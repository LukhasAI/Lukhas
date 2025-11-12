# Guardian Structure Consolidation Audit
**Date**: 2025-11-12
**Phase**: Phase 2 - Structure Consolidation
**Status**: Audit Complete ✅

## Executive Summary

Comprehensive audit of 47+ Guardian files across 21 directory locations identifying canonical implementations, duplicates, bridges, and scattered components requiring consolidation.

### Key Findings

- **Canonical Production**: 4 files (900 lines) in `lukhas_website/lukhas/governance/guardian/`
- **Experimental Labs**: 13 files (7,564 lines) in `labs/governance/guardian/`
- **Bridge Modules**: 8 files (Phase 1 + legacy bridges)
- **Scattered Implementations**: 3 substantial files (1,432 lines) requiring relocation
- **Test Files**: Multiple test suites across 3 test directories

### Consolidation Impact

- **Files to Relocate**: 3 substantial implementations (policies, reflector, serializers)
- **Bridges to Document**: 8 bridge modules requiring deprecation markers
- **Import Paths**: All imports validated and working after Phase 1

## Guardian File Inventory

### 1. CANONICAL PRODUCTION (lukhas_website/lukhas/governance/guardian/)

**Status**: ✅ Source of Truth for Production

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `__init__.py` | 119 | Module exports and public API | Canonical ✅ |
| `core.py` | 72 | Core types (DriftResult, EthicalDecision, etc.) | Canonical ✅ |
| `guardian_impl.py` | 340 | GuardianSystemImpl implementation | Canonical ✅ |
| `guardian_wrapper.py` | 369 | Wrapper functions (detect_drift, evaluate_ethics, etc.) | Canonical ✅ |
| **TOTAL** | **900** | **Production Guardian System** | **Complete** |

**Features**:
- ✅ Complete Guardian System implementation
- ✅ MATRIZ instrumentation (@instrument decorators)
- ✅ Feature flag support (GUARDIAN_ACTIVE)
- ✅ Dry-run mode by default
- ✅ Emergency kill-switch integration
- ✅ Constitutional AI principles
- ✅ Drift threshold: 0.15

**Import Pattern**: `from lukhas_website.lukhas.governance.guardian import ...`

---

### 2. EXPERIMENTAL LABS (labs/governance/guardian/)

**Status**: 🔬 Development/Experimental

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `__init__.py` | 16 | Module exports | Experimental |
| `core.py` | 97 | Core types (incomplete vs production) | Experimental |
| `debug_interface.py` | 895 | Debug and introspection tools | Experimental |
| `drift_detector.py` | 1,342 | Advanced drift detection algorithms | Experimental |
| `guardian.py` | 103 | Guardian orchestration | Experimental |
| `guardian_system.py` | 1,057 | System integration | Experimental |
| `guardian_validator.py` | 311 | Validation framework | Experimental |
| `monitoring_dashboard.py` | 1,158 | Real-time monitoring UI | Experimental |
| `pwm_workspace_guardian.py` | 381 | PWM workspace protection | Experimental |
| `repair_system.py` | 616 | Self-repair mechanisms | Experimental |
| `security_event_monitor.py` | 995 | Security event detection | Experimental |
| `sentinel.py` | 211 | Sentinel monitoring | Experimental |
| `workspace_guardian.py` | 382 | Workspace protection | Experimental |
| **TOTAL** | **7,564** | **Experimental Features** | **Active Development** |

**Purpose**: Development lane for Guardian feature research before production promotion.

**Import Pattern**: `from labs.governance.guardian import ...`

**Action**: ✅ **KEEP** - Active development, not duplicates

---

### 3. BRIDGE MODULES (governance/guardian/)

**Status**: 🌉 Import Redirects (Phase 1)

Created in Phase 1 to resolve import path issues. Enable imports via `governance.guardian.*` pattern.

| File | Lines | Purpose | Target | Status |
|------|-------|---------|--------|--------|
| `__init__.py` | 16 | Module initialization | Bridge logic | Phase 1 ✅ |
| `core.py` | 54 | Core types bridge | → lukhas_website.lukhas.governance.guardian.core | Phase 1 ✅ |
| `guardian_impl.py` | 33 | Implementation bridge | → lukhas_website.lukhas.governance.guardian.guardian_impl | Phase 1 ✅ |
| `guardian_wrapper.py` | 50 | Wrapper bridge | → lukhas_website.lukhas.governance.guardian.guardian_wrapper | Phase 1 ✅ |

**Pattern**: Try production → Try labs → Raise ImportError

**Action**: ✅ **KEEP** - Required for import path resolution

---

### 4. SCATTERED ROOT GOVERNANCE FILES (governance/)

**Status**: ⚠️ Requires Consolidation

Substantial implementations scattered in root `governance/` directory that should be in `lukhas_website/lukhas/governance/guardian/`.

#### A. Substantial Implementations (RELOCATE)

| File | Lines | Purpose | Canonical Location | Action |
|------|-------|---------|-------------------|--------|
| `guardian_policies.py` | 609 | Guardian policies engine | `lukhas_website/lukhas/governance/guardian/policies.py` | **RELOCATE** ⚠️ |
| `guardian_reflector.py` | 759 | Guardian reflection system | `lukhas_website/lukhas/governance/guardian/reflector.py` | **RELOCATE** ⚠️ |
| `guardian_serializers.py` | 64 | Basic serializers (INCOMPLETE) | See lukhas_website version (500+ lines) | **DEPRECATE** 🗑️ |
| **TOTAL** | **1,432** | **Scattered Implementations** | - | - |

**Issue**: These are substantial implementations that should be part of the canonical Guardian module in `lukhas_website/lukhas/governance/guardian/`.

**Recommendation**:
1. `guardian_policies.py` → Move to `lukhas_website/lukhas/governance/guardian/policies.py`
2. `guardian_reflector.py` → Move to `lukhas_website/lukhas/governance/guardian/reflector.py`
3. `guardian_serializers.py` → Deprecate (incomplete, full version exists in lukhas_website)

#### B. Legacy Bridges (DEPRECATE)

| File | Lines | Purpose | Target | Action |
|------|-------|---------|--------|--------|
| `guardian_sentinel.py` | 6 | Bridge to labs | → `labs.governance.guardian_sentinel` | **DEPRECATE** 🗑️ |
| `guardian_shadow_filter.py` | 6 | Bridge to labs | → `labs.governance.guardian_shadow_filter` | **DEPRECATE** 🗑️ |
| `guardian_system.py` | 6 | Bridge to labs | → `labs.governance.guardian_system` | **DEPRECATE** 🗑️ |
| `guardian_system_integration.py` | 20 | Shim module | Legacy import redirect | **DEPRECATE** 🗑️ |

**Issue**: Legacy bridges pointing to labs implementations. Superseded by Phase 1 bridge modules.

**Action**: Add deprecation warnings and mark for removal in Phase 3.

---

### 5. SPECIALIZED GUARDIAN IMPLEMENTATIONS

**Status**: ℹ️ Domain-Specific (Keep)

Guardian integrations in other system components:

| Location | File | Lines | Purpose | Action |
|----------|------|-------|---------|--------|
| `lukhas_website/lukhas/governance/` | `guardian_bridge.py` | - | Guardian bridge logic | KEEP ✅ |
| `lukhas_website/lukhas/governance/` | `guardian_serializers.py` | 500+ | FULL serialization system | KEEP ✅ (Canonical) |
| `lukhas_website/lukhas/governance/` | `guardian_system.py` | - | System coordination | KEEP ✅ |
| `lukhas_website/lukhas/consciousness/` | `guardian_integration.py` | - | Consciousness integration | KEEP ✅ |
| `lukhas_website/lukhas/core/` | `guardian_sentinel.py` | - | Core sentinel | KEEP ✅ |
| `labs/core/governance/` | `guardian_integration.py` | - | Labs integration | KEEP ✅ |
| `labs/core/governance/` | `guardian_system_2.py` | - | Next-gen system | KEEP 🔬 |
| `labs/core/governance/` | `guardian_testing_framework.py` | - | Testing framework | KEEP ✅ |
| `governance/ethics/` | `guardian_kill_switch.py` | - | Emergency kill-switch | KEEP ✅ (Critical) |
| `observability/` | `guardian_metrics.py` | - | Metrics collection | KEEP ✅ |

**Action**: ✅ **KEEP** - Domain-specific integrations, not duplicates

---

### 6. TEST INFRASTRUCTURE

**Status**: ✅ Test Coverage

| Location | Purpose | Action |
|----------|---------|--------|
| `tests/guardian/` | Guardian unit tests | KEEP ✅ |
| `tests/unit/governance/guardian/` | Component unit tests | KEEP ✅ |
| `tests/integration/governance/guardian/` | Integration tests | KEEP ✅ |
| `docs/examples/` | `guardian_usage.py` | KEEP ✅ (Documentation) |

---

## Consolidation Plan

### Phase 2.1: Relocate Scattered Implementations

**Timeline**: Week 2, Days 1-2

1. **Move guardian_policies.py**
   ```bash
   git mv governance/guardian_policies.py \
          lukhas_website/lukhas/governance/guardian/policies.py
   ```
   - Update imports throughout codebase
   - Update documentation references
   - Run test suite

2. **Move guardian_reflector.py**
   ```bash
   git mv governance/guardian_reflector.py \
          lukhas_website/lukhas/governance/guardian/reflector.py
   ```
   - Update imports throughout codebase
   - Update documentation references
   - Run test suite

3. **Deprecate incomplete guardian_serializers.py**
   - Add deprecation warning pointing to `lukhas_website.lukhas.governance.guardian_serializers`
   - Mark for removal in Phase 3

### Phase 2.2: Mark Legacy Bridges for Deprecation

**Timeline**: Week 2, Day 3

Add deprecation markers to legacy bridges:

```python
"""
DEPRECATED: This module is a legacy bridge and will be removed in a future release.

Use the canonical import path instead:
    from lukhas_website.lukhas.governance.guardian import ...

Or use the new bridge pattern:
    from governance.guardian import ...
"""
import warnings
warnings.warn(
    "governance.guardian_system is deprecated. "
    "Use lukhas_website.lukhas.governance.guardian instead.",
    DeprecationWarning,
    stacklevel=2
)
```

**Files to mark**:
- [ ] `governance/guardian_sentinel.py`
- [ ] `governance/guardian_shadow_filter.py`
- [ ] `governance/guardian_system.py`
- [ ] `governance/guardian_system_integration.py`
- [ ] `governance/guardian_serializers.py`

### Phase 2.3: Update Documentation

**Timeline**: Week 2, Days 4-5

1. **Create Guardian Architecture Documentation**
   - File: `docs/architecture/GUARDIAN_SYSTEM.md`
   - Content:
     - Module structure and layout
     - Canonical import paths
     - Feature flag usage
     - Kill-switch integration
     - Testing guidelines

2. **Update Developer Import Guide**
   - File: `docs/development/GUARDIAN_IMPORTS.md`
   - Content:
     - Correct import patterns
     - Bridge module explanation
     - Lane isolation rules
     - Migration guide from legacy imports

3. **Update CLAUDE.md Context**
   - Add Guardian module structure section
   - Document canonical locations
   - Add import patterns

### Phase 2.4: Validation

**Timeline**: Week 2, Day 5

- [ ] Run full test suite: `make test`
- [ ] Run Guardian-specific tests: `pytest tests/guardian/ tests/unit/governance/guardian/ tests/integration/governance/guardian/`
- [ ] Validate all imports: `make imports-guard`
- [ ] Validate lane boundaries: `make lane-guard`
- [ ] Run smoke tests: `make smoke`
- [ ] Test kill-switch integration

---

## Import Path Reference

### ✅ CORRECT Import Patterns

```python
# Production Guardian (Canonical)
from lukhas_website.lukhas.governance.guardian import (
    DriftResult,
    EthicalDecision,
    EthicalSeverity,
    GovernanceAction,
    SafetyResult,
)
from lukhas_website.lukhas.governance.guardian import (
    check_safety,
    detect_drift,
    evaluate_ethics,
    get_guardian_status,
)
from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

# Via Bridge (Convenience)
from governance.guardian.core import DriftResult, EthicalDecision
from governance.guardian.guardian_wrapper import detect_drift, evaluate_ethics
from governance.guardian.guardian_impl import GuardianSystemImpl

# Labs Experimental
from labs.governance.guardian import ...
```

### ⚠️ DEPRECATED Import Patterns

```python
# DEPRECATED - Legacy bridges
from governance.guardian_system import GuardianSystem  # Use lukhas_website or bridge
from governance.guardian_sentinel import GuardianSentinel  # Use lukhas_website or bridge
from governance.guardian_shadow_filter import GuardianShadowFilter  # Use lukhas_website or bridge
from governance.guardian_serializers import ...  # Use lukhas_website version (full implementation)
```

---

## Guardian Module Layout (Target State)

```
lukhas_website/lukhas/governance/guardian/    # CANONICAL PRODUCTION
├── __init__.py                               # Module exports (119 lines)
├── core.py                                   # Core types (72 lines)
├── guardian_impl.py                          # GuardianSystemImpl (340 lines)
├── guardian_wrapper.py                       # Wrapper functions (369 lines)
├── policies.py                               # [TO BE MOVED] Policies engine (609 lines)
├── reflector.py                              # [TO BE MOVED] Reflection system (759 lines)
└── [Future additions from labs promotion]

labs/governance/guardian/                      # EXPERIMENTAL DEVELOPMENT
├── core.py                                   # Experimental core types
├── drift_detector.py                         # Advanced drift algorithms
├── guardian_system.py                        # System integration experiments
├── monitoring_dashboard.py                   # Dashboard UI
└── [13 total experimental files]

governance/guardian/                           # BRIDGE MODULES
├── __init__.py                               # Bridge initialization
├── core.py                                   # Types bridge
├── guardian_impl.py                          # Implementation bridge
└── guardian_wrapper.py                       # Wrapper bridge

governance/                                    # LEGACY (TO DEPRECATE)
├── guardian_sentinel.py                      # [DEPRECATE] Bridge to labs
├── guardian_shadow_filter.py                 # [DEPRECATE] Bridge to labs
├── guardian_system.py                        # [DEPRECATE] Bridge to labs
├── guardian_system_integration.py            # [DEPRECATE] Shim
└── guardian_serializers.py                   # [DEPRECATE] Incomplete (use lukhas_website)
```

---

## File Status Summary

### ✅ Canonical (Keep - Source of Truth)
- `lukhas_website/lukhas/governance/guardian/*` (4 files, 900 lines)
- `lukhas_website/lukhas/governance/guardian_serializers.py` (500+ lines, full implementation)

### 🔬 Experimental (Keep - Active Development)
- `labs/governance/guardian/*` (13 files, 7,564 lines)

### 🌉 Bridges (Keep - Required for Imports)
- `governance/guardian/*` (4 files, Phase 1 bridges)

### ⚠️ Relocate to Canonical
- `governance/guardian_policies.py` → `lukhas_website/lukhas/governance/guardian/policies.py`
- `governance/guardian_reflector.py` → `lukhas_website/lukhas/governance/guardian/reflector.py`

### 🗑️ Deprecate (Legacy)
- `governance/guardian_sentinel.py` (bridge to labs)
- `governance/guardian_shadow_filter.py` (bridge to labs)
- `governance/guardian_system.py` (bridge to labs)
- `governance/guardian_system_integration.py` (shim)
- `governance/guardian_serializers.py` (incomplete, superseded)

### ✅ Domain-Specific (Keep)
- Integration files in consciousness, core, observability
- Kill-switch implementation
- Test infrastructure
- Documentation examples

---

## Metrics

### File Distribution
- **Total Guardian Files**: 47+
- **Guardian Directories**: 21 locations
- **Canonical Production**: 4 files (900 lines)
- **Experimental Labs**: 13 files (7,564 lines)
- **Bridges**: 8 files (~200 lines)
- **To Relocate**: 3 files (1,432 lines)
- **To Deprecate**: 5 files (~100 lines)

### Code Volume
- **Production Guardian**: 900 lines
- **Experimental Guardian**: 7,564 lines (8.4x production)
- **Scattered Implementations**: 1,432 lines (needs consolidation)
- **Total Guardian Code**: ~10,000 lines

### Test Coverage
- **Unit Tests**: tests/guardian/, tests/unit/governance/guardian/
- **Integration Tests**: tests/integration/governance/guardian/
- **Kill-Switch Tests**: 37 unit tests, 8 integration tests (all passing ✅)

---

## Next Steps

1. ✅ **Audit Complete** (This Document)
2. ⏭️ **Phase 2.1**: Relocate scattered implementations (guardian_policies, guardian_reflector)
3. ⏭️ **Phase 2.2**: Add deprecation markers to legacy bridges
4. ⏭️ **Phase 2.3**: Update documentation (architecture, imports)
5. ⏭️ **Phase 2.4**: Validation (tests, imports, lane-guard)
6. ⏭️ **Phase 2 PR**: Commit and merge Phase 2 changes

---

## References

- **Phase 1 Report**: `docs/GUARDIAN_MODULE_STRUCTURE_AUDIT_2025-11-12.md`
- **Phase 1 PR**: #1356 (Merged ✅)
- **Kill-Switch Implementation**: `governance/ethics/guardian_kill_switch.py`
- **Test Results**: All integration tests passing after Phase 1
- **Import Validation**: All imports working via bridges and direct paths

---

**Report Generated**: 2025-11-12
**Audit Status**: ✅ Complete
**Next Phase**: Phase 2.1 - Relocate Scattered Implementations
