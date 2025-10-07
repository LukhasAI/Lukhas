---
status: stable
type: misc
owner: unknown
module: v0.03
redirect: false
moved_to: null
---

![Status: Stable](https://img.shields.io/badge/status-stable-green)

# Final Import Assessment - What's REALLY Missing

## Current Status

**Collection Errors**: 173 (down from 182)
**Error Types**:
1. ModuleNotFoundError: Modules that don't exist anywhere
2. ImportError (cannot import name): Module exists but missing specific exports

## Category 1: ModuleNotFoundError (True Missing Modules)

These modules genuinely don't exist and need creation:

1. **bridge.api.analysis** - API analysis utilities
   - Likely needs: drift scoring, user analytics
   - Referenced by: `bridge/api/main.py`

2. **consciousness.dream** - Dream consciousness processing
   - Alternative exists: `candidate/core/orchestration/dream` (2 files)
   - **ACTION**: Create import alias OR fix imports

3. **candidate.cognitive_core** - Cognitive core for candidate lane
   - May exist as: `candidate/core/cognitive` OR scattered in `candidate/consciousness`
   - **ACTION**: Search more carefully or create

## Category 2: ImportError (Missing Exports)

These modules exist but are missing specific classes/functions:

1. **branding.APPROVED_TERMS**
   - Module exists: `branding/__init__.py`
   - Missing: `APPROVED_TERMS` constant
   - **ACTION**: Add export to branding/__init__.py

2. **core.metrics.router_cascade_preventions_total**
   - Module exists: `core/metrics/__init__.py`
   - Missing: Prometheus metric
   - **ACTION**: Add metric definition

3. **core.policy_guard.PolicyGuard**
   - Module exists: `lukhas/core/policy_guard/__init__.py`
   - Missing: `PolicyGuard` class
   - **ACTION**: Implement PolicyGuard or import from elsewhere

## Recommended Actions

### Quick Wins (Fix in <1 hour)

1. **Create Import Aliases** for consciousness.dream:
   ```python
   # consciousness/dream/__init__.py
   from candidate.core.orchestration.dream import *
   ```

2. **Add Missing Exports** to existing modules:
   ```python
   # branding/__init__.py
   APPROVED_TERMS = ["lukhas", "matriz", "constellation"]  # Add this

   # core/metrics/__init__.py
   from prometheus_client import Counter
   router_cascade_preventions_total = Counter(...)  # Add this
   ```

3. **Implement or Import** PolicyGuard:
   ```python
   # lukhas/core/policy_guard/__init__.py
   from governance.policy import PolicyGuard  # If exists elsewhere
   # OR implement minimal version
   ```

### Medium Effort (1-2 hours)

4. **bridge.api.analysis** - Create minimal implementation:
   - `drift_score.py`: User drift tracking
   - `analytics.py`: API usage analytics
   - Basic functionality to unblock tests

5. **candidate.cognitive_core** - Check if code exists elsewhere:
   - Search in `candidate/consciousness/cognitive`
   - Search in `cognitive_core/`
   - Create alias or minimal implementation

## Updated GPT-5 Request

Instead of 62 modules, we need:

### Critical (Must Have - 5 modules)
1. bridge.api.analysis (if no alternative found)
2. Missing exports in existing modules (APPROVED_TERMS, metrics, PolicyGuard)

### Nice to Have (Can be aliases - 10 modules)
3-12. Consciousness/governance modules that likely exist under different paths

### Total Effort

- **Manual fixes**: ~15 missing exports in existing modules
- **New modules needed**: ~2-5 (not 62!)
- **Import aliases**: ~10-15 modules

**Estimated time**: 2-3 hours vs 20+ hours for 62 modules

## Next Step

Run comprehensive search to find where code ACTUALLY exists:
```bash
grep -r "class PolicyGuard" . --include="*.py"
grep -r "APPROVED_TERMS" . --include="*.py"
grep -r "router_cascade" . --include="*.py"
```

Then create targeted fixes instead of bulk module creation.
