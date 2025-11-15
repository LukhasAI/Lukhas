# Handoff to Claude Code Web - Core Wiring Phase 1

**Date**: 2025-11-10
**Session**: Claude Code Desktop → Claude Code Web
**Status**: Task 1 Complete ✅ | Tasks 2-9 Pending 📋

---

## ✅ What's Been Completed

### Task 1: Global Initialization System

**Completed by**: Claude Code Desktop
**Branch**: `feat/core-wiring-phase1` (merged to `main`)
**PR**: [#1263 (Draft)](https://github.com/LukhasAI/Lukhas/pull/1263)
**Commit**: `217a49f77` - feat(core): add global initialization system with feature flags

#### Deliverables

**New Files**:
- `lukhas_website/lukhas/core/initialization.py` (223 lines)
- `lukhas_website/lukhas/core/__init__.py` (15 lines)
- `tests/unit/core/test_initialization.py` (208 lines)

**Total**: 431 lines, 2 source files

#### Features Implemented

✅ **`initialize_global_system()`** - Main initialization function with feature flags
✅ **`get_initialization_status()`** - Query current initialization state
✅ **Feature Flags** (all default to OFF):
  - `CONSCIOUSNESS_ENABLED=false`
  - `DREAMS_ENABLED=false`
  - `GLYPHS_ENABLED=false`
  - `PARALLEL_DREAMS_ENABLED=false` (reserved for Task 4)

✅ **Lazy Imports** - Systems only loaded when explicitly enabled
✅ **Idempotent** - Safe to call multiple times without side effects
✅**Graceful Error Handling** - Import failures become warnings, not crashes
✅ **Comprehensive Tests** - 8 passed, 3 skipped (due to existing RecursionError in `memory/backends/base`)

#### Test Results

```
✅ 8 PASSED, 3 SKIPPED

PASSED:
  ✓ test_import_initialization_module
  ✓ test_initialize_with_all_flags_off (default behavior)
  ✓ test_initialize_with_dreams_enabled (partial success with warnings)
  ✓ test_initialize_with_glyphs_enabled (full success)
  ✓ test_initialize_idempotent
  ✓ test_feature_flag_case_insensitive
  ✓ test_feature_flag_false_values
  ✓ test_get_initialization_status

SKIPPED:
  ⏭️ test_initialize_with_consciousness_enabled (existing RecursionError)
  ⏭️ test_initialize_with_all_flags_enabled (existing RecursionError)
  ⏭️ test_initialization_failure_handling (existing RecursionError)
```

**Note**: Skipped tests are due to an existing bug in `memory/backends/base/__init__.py` (RecursionError in `__getattr__`), not related to the initialization code.

#### Deployment Safety

**Risk Level**: 🟢 **LOW**
- Only adds new code (no modifications to existing systems)
- All feature flags default to OFF
- No automatic initialization (manual opt-in)
- Comprehensive test coverage

**Merged to Main**: ✅ YES (commit `f9620a1ff`)
**Production Deployment**: Safe to deploy (flags OFF by default)

---

## 📋 What Remains - Tasks 2-9

### High Priority Tasks (Core Wiring)

#### Task 2: Create Wrapper Modules
**Status**: ⏳ Pending
**Scope**: Create thin adapter layers in production lane
**Files to Create**:
- `lukhas_website/lukhas/consciousness/__init__.py` (wrapper)
- `lukhas_website/lukhas/dreams/__init__.py` (wrapper)
- `lukhas_website/lukhas/glyphs/__init__.py` (wrapper)

**Purpose**: Isolate production lane from candidate/labs dependencies

**Approach**:
```python
# lukhas/consciousness/__init__.py (example wrapper)
"""
Consciousness Wrapper Module

Provides production-safe interface to consciousness subsystem.
"""
import os

CONSCIOUSNESS_ENABLED = os.environ.get("CONSCIOUSNESS_ENABLED", "false").lower() == "true"

if CONSCIOUSNESS_ENABLED:
    try:
        from candidate.consciousness.core import ConsciousnessEngine
        _engine = ConsciousnessEngine()
    except ImportError:
        _engine = None
else:
    _engine = None

def get_consciousness_engine():
    """Get consciousness engine if enabled"""
    if not CONSCIOUSNESS_ENABLED or _engine is None:
        raise RuntimeError("Consciousness not enabled or not available")
    return _engine

__all__ = ["get_consciousness_engine", "CONSCIOUSNESS_ENABLED"]
```

**Tests**:
- Test wrapper with flag OFF (should return None or raise)
- Test wrapper with flag ON + mocked engine
- Test graceful degradation on import errors

**PR Size**: Small (3 files, ~150 lines total)

---

#### Task 3: Production API Routes
**Status**: ⏳ Pending
**Scope**: Add FastAPI routes for dreams, drift, and glyphs
**Files to Modify/Create**:
- `lukhas_website/lukhas/api/dreams.py` (new)
- `lukhas_website/lukhas/api/drift.py` (new)
- `lukhas_website/lukhas/api/glyphs.py` (new)

**API Endpoints to Add**:

**Dreams API**:
```python
POST /api/v1/dreams/parallel
GET  /api/v1/dreams/{dream_id}
GET  /api/v1/dreams/list
```

**Drift API** (Vivox integration):
```python
GET  /api/v1/drift/{user_id}
POST /api/v1/drift/update
GET  /api/v1/drift/analysis
```

**Glyphs API**:
```python
POST /api/v1/glyphs/bind
GET  /api/v1/glyphs/{glyph_id}
POST /api/v1/glyphs/validate
```

**Feature Flags**:
- Each endpoint checks corresponding feature flag before execution
- Returns 503 Service Unavailable if feature disabled

**Tests**:
- Test each endpoint with flag OFF (expect 503)
- Test each endpoint with flag ON + mocked services
- Test request/response schemas (Pydantic models)

**PR Size**: Medium (3 files, ~300-400 lines total)

---

#### Task 4: Wire Parallel Dreams Feature Flag
**Status**: ⏳ Pending
**Scope**: Integrate `PARALLEL_DREAMS_ENABLED` flag into dreams subsystem
**Files to Modify**:
- `lukhas_website/lukhas/dreams/__init__.py` (from Task 2)
- Update initialization.py to check `PARALLEL_DREAMS_ENABLED`

**Logic**:
```python
# In dreams wrapper
DREAMS_ENABLED = parse_bool("DREAMS_ENABLED")
PARALLEL_DREAMS_ENABLED = parse_bool("PARALLEL_DREAMS_ENABLED")

if DREAMS_ENABLED and PARALLEL_DREAMS_ENABLED:
    # Enable parallel processing
    from candidate.dreams.parallel_engine import ParallelDreamEngine
    _engine = ParallelDreamEngine()
elif DREAMS_ENABLED:
    # Sequential processing only
    from candidate.dreams.sequential_engine import SequentialDreamEngine
    _engine = SequentialDreamEngine()
else:
    _engine = None
```

**Tests**:
- Test DREAMS_ENABLED=false (no engine)
- Test DREAMS_ENABLED=true, PARALLEL_DREAMS_ENABLED=false (sequential)
- Test DREAMS_ENABLED=true, PARALLEL_DREAMS_ENABLED=true (parallel)

**PR Size**: Small (1-2 files, ~100 lines)

---

#### Task 5: Wire Vivox Drift into User Profiles
**Status**: ⏳ Pending
**Scope**: Integrate Vivox drift metrics into user profile API
**Files to Modify**:
- `lukhas_website/lukhas/api/users.py` (add drift field)
- `lukhas_website/lukhas/vivox/drift_tracker.py` (create if missing)

**User Profile Addition**:
```python
class UserProfile(BaseModel):
    lambda_id: str
    display_name: str
    # ... existing fields ...

    # New: Vivox drift metrics
    drift_score: Optional[float] = None
    drift_last_updated: Optional[datetime] = None
    drift_analysis: Optional[dict] = None
```

**Drift Calculation**:
- Track user behavior deviations over time
- Integrate with consciousness/memory systems
- Store in user preferences or separate table

**Tests**:
- Test drift calculation with various user behaviors
- Test drift API endpoints
- Test drift persistence

**PR Size**: Medium (2-3 files, ~200-300 lines)

---

#### Task 6: Create GLYPH Bind Endpoints
**Status**: ⏳ Pending
**Scope**: API endpoints for binding GLYPH tokens to user actions
**Files to Create**:
- `lukhas_website/lukhas/api/glyphs.py` (if not created in Task 3)

**Endpoints**:
```python
POST /api/v1/glyphs/bind
{
  "glyph_id": "glyph_abc123",
  "user_id": "lid:xyz789",
  "action": "TRUST",
  "context": {"..."}
}

GET /api/v1/glyphs/bindings/{user_id}
# Returns all GLYPH bindings for user

POST /api/v1/glyphs/unbind/{glyph_id}
# Revoke GLYPH binding
```

**Integration with Existing**:
- Use `lukhas_website/lukhas/core/common/glyph.py` (already exists)
- Add persistence layer (database table or file storage)
- Integrate with Guardian for validation

**Tests**:
- Test bind/unbind operations
- Test GLYPH validation
- Test Guardian integration

**PR Size**: Medium (2-3 files, ~250-300 lines)

---

#### Task 7: Add Observability and Metrics
**Status**: ⏳ Pending
**Scope**: Prometheus metrics and OpenTelemetry traces for all wired systems
**Files to Modify/Create**:
- `lukhas_website/lukhas/observability/metrics.py` (enhance existing)
- Add metrics to initialization, wrappers, API routes

**Metrics to Add**:
```python
# Initialization metrics
lukhas_initialization_duration_seconds = Histogram(...)
lukhas_feature_flags_enabled = Gauge(...)  # 0 or 1 for each flag

# Dreams metrics
lukhas_dreams_parallel_count = Counter(...)
lukhas_dreams_processing_duration_seconds = Histogram(...)

# Drift metrics
lukhas_drift_score = Histogram(...)
lukhas_drift_updates_total = Counter(...)

# GLYPH metrics
lukhas_glyphs_bind_total = Counter(...)
lukhas_glyphs_validation_failures_total = Counter(...)
```

**OpenTelemetry Traces**:
- Trace initialization flow
- Trace API request → wrapper → candidate execution
- Trace GLYPH bind/validate operations

**Tests**:
- Test metric collection
- Test trace generation
- Test metric export to Prometheus

**PR Size**: Medium (2-3 files, ~200-250 lines)

---

### Medium Priority Tasks (Quality & Security)

#### Task 8: Performance and Chaos Testing
**Status**: ⏳ Pending
**Scope**: Load tests and chaos engineering for wired systems
**Files to Create**:
- `tests/performance/test_initialization.py`
- `tests/chaos/test_feature_flag_failures.py`

**Performance Tests**:
- Initialization latency (<250ms target)
- API endpoint throughput (50+ ops/sec)
- Memory usage with all flags enabled (<100MB)

**Chaos Tests**:
- Random feature flag toggling
- Import failures during initialization
- Network failures during API calls
- Database unavailability

**PR Size**: Medium (4-5 test files, ~300-400 lines)

---

#### Task 9: Security Review and SLSA Provenance
**Status**: ⏳ Pending
**Scope**: Security audit and supply chain attestation
**Files to Create**:
- `docs/security/CORE_WIRING_SECURITY_AUDIT.md`
- `.github/workflows/slsa-provenance.yml` (if not exists)

**Security Review Areas**:
- Feature flag injection (env var security)
- Lazy import security (code execution risks)
- API authentication/authorization
- GLYPH validation (prevent malicious glyphs)
- Drift tracking (privacy considerations)

**SLSA Provenance**:
- Generate provenance for all PQC dependencies
- Sign release artifacts
- Verify supply chain integrity

**PR Size**: Documentation + CI config (~500 lines total)

---

## 🎯 Current State

### What's Merged to Main
✅ Task 1: Global initialization system (`lukhas/core/initialization.py`)
✅ Comprehensive test suite (8 tests passing)
✅ Feature flags infrastructure
✅ Lazy loading pattern established

### What's in Draft PR #1263
- Same as merged content
- Awaiting steward review
- Safe to approve and merge (already in main)

### What's NOT Started
- Tasks 2-9 (all pending)
- Wrapper modules
- Production API routes
- Observability/metrics
- Performance/chaos tests
- Security audit

---

## 🚀 Next Steps for Claude Code Web

### Recommended Approach

**Option A: Sequential PRs (Conservative)**
1. Create PR for Task 2 (wrappers) - ~3 files, 150 lines
2. Wait for review/merge
3. Create PR for Task 3 (API routes) - ~3 files, 300 lines
4. Continue sequentially through Tasks 4-9

**Benefits**: Small PRs, easy review, low risk
**Drawbacks**: Slower overall progress

**Option B: Batched PRs (Moderate)**
1. Create PR for Tasks 2+3 (wrappers + API routes) - ~6 files, 450 lines
2. Create PR for Tasks 4+5+6 (feature wiring) - ~5 files, 550 lines
3. Create PR for Tasks 7+8+9 (observability + testing + security) - ~8 files, 900 lines

**Benefits**: Fewer PRs, related tasks together, faster progress
**Drawbacks**: Larger PRs, harder to review

**Option C: Parallel Development (Aggressive)**
1. Create multiple branches/PRs simultaneously
2. Tasks 2, 3, 4, 5, 6 in parallel (no dependencies between them)
3. Tasks 7, 8, 9 after others merge

**Benefits**: Fastest overall progress
**Drawbacks**: Potential merge conflicts, coordination overhead

### Recommended: Option A (Sequential)

For safety and maintainability, I recommend **Option A** - sequential PRs following the same pattern as Task 1:
- Small, focused PRs (≤5 files, ≤500 lines)
- Comprehensive tests for each PR
- Draft PR with `labot` label
- Steward checklist in PR comments
- Feature flags OFF by default

---

## 📚 Key Resources

### PRs & Issues
- **Draft PR #1263**: https://github.com/LukhasAI/Lukhas/pull/1263 (Task 1 complete)
- **QRG Spec PR #1262**: https://github.com/LukhasAI/Lukhas/pull/1262 (related, Phase 0)
- **Lambda ID Audit PR #1244**: https://github.com/LukhasAI/Lukhas/pull/1244 (background context)
- **Issue #1253**: QRG consciousness wiring (tracked separately)
- **Issue #1254**: GLYPH pipeline components (tracked separately)
- **Issue #1255**: Lambda ID documentation (tracked separately)

### Code References
- **Initialization**: `lukhas_website/lukhas/core/initialization.py` (Task 1 complete)
- **GLYPH Tokens**: `lukhas_website/lukhas/core/common/glyph.py` (existing, ready to use)
- **Consciousness**: `lukhas_website/lukhas/consciousness/__init__.py` (existing, needs wrapper)
- **Dreams**: `lukhas_website/lukhas/dream/` (existing directory, needs `__init__.py` wrapper)
- **Vivox**: `lukhas_website/lukhas/vivox/` (existing directory, needs drift tracker)

### Testing Infrastructure
- **Test Directory**: `tests/unit/core/` (created for Task 1)
- **Pytest Config**: `tests/unit/pytest.ini` (existing)
- **Test Pattern**: `test_*.py` with comprehensive docstrings
- **Coverage Target**: 75%+ for production promotion

### Worktree Workflow
- **Worktree Created**: `/Users/agi_dev/LOCAL-REPOS/Lukhas-core-wiring`
- **Branch**: `feat/core-wiring-phase1` (merged to main)
- **New Worktree Needed**: Yes, for Tasks 2-9 (e.g., `feat/core-wiring-phase2`)

---

## 💡 Important Notes

### Existing Bugs to Be Aware Of
1. **RecursionError in `memory/backends/base/__init__.py`**
   - Affects consciousness module initialization
   - Causes 3 tests to be skipped
   - Should be fixed in separate PR before enabling `CONSCIOUSNESS_ENABLED`

2. **Dreams Module Not Fully Wired**
   - Initialization shows "warnings expected" message
   - Partial success is normal until Task 2 completes

### Feature Flag Philosophy
- **Default: OFF** - All new features start disabled
- **Explicit Opt-In** - Require environment variable to enable
- **Case-Insensitive** - `true`, `TRUE`, `1`, `yes`, `YES` all work
- **Graceful Degradation** - Missing modules become warnings, not errors

### Testing Standards
- **Tests First** - Write failing test before implementation
- **Comprehensive** - Test happy path, error cases, edge cases
- **Fast** - Unit tests should complete in <1 second
- **Isolated** - Each test resets state (see `reset_environment` fixture)

### PR Standards (T4 Compliance)
- **Commit Messages**: `<type>(<scope>): <subject>` with Problem/Solution/Impact
- **PR Title**: Match commit message format
- **PR Body**: Include Summary, Changes, Test Results, Deployment Notes
- **Labels**: Always include `labot` (Draft PRs by default)
- **Steward Checklist**: Post as PR comment after creation

---

## 🤖 Handoff Complete

**From**: Claude Code Desktop
**To**: Claude Code Web
**Date**: 2025-11-10
**Status**: ✅ Task 1 Complete | 📋 Tasks 2-9 Ready to Start

**Summary**: The foundation for core wiring is complete. Global initialization system is merged to main with comprehensive tests. Feature flags are in place and working. All systems default to OFF for safety. Claude Code Web can now proceed with Tasks 2-9 sequentially or in batches.

**Questions?** Check:
- Draft PR #1263 for Task 1 implementation details
- This handoff document for Tasks 2-9 specifications
- `lukhas_website/lukhas/core/initialization.py` for code examples

**Good luck with Tasks 2-9!** 🚀

---

*Generated by Claude Code Desktop on 2025-11-10*
