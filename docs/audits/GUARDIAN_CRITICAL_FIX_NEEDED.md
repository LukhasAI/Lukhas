# 🚨 CRITICAL: Guardian PDP Import Name Mismatch

**Date**: 2025-10-14
**Severity**: 🔴 HIGH - Blocks all Guardian functionality
**Fix Time**: ~2 minutes
**Owner**: Codex (hot-path adapters)

---

## The Issue

**Error**: `cannot import name 'PDP' from 'lukhas.adapters.openai.policy_pdp'`

**Root Cause**: Class was renamed from `PDP` to `GuardianPDP` but imports weren't updated consistently.

---

## Current State

### In `lukhas/adapters/openai/policy_pdp.py`:
```python
class GuardianPDP:  # ← Class is named GuardianPDP
    """Policy Decision Point: Evaluates a request context against a policy."""
```

### In `lukhas/adapters/openai/api.py`:
```python
# Line 38 - WRONG
from lukhas.adapters.openai.policy_pdp import PDP  # ❌ PDP doesn't exist

# Line 307 - CORRECT
from lukhas.adapters.openai.policy_pdp import GuardianPDP  # ✅ This is right

# Line 468 - WRONG
from lukhas.adapters.openai.policy_pdp import PDP, PolicyLoader  # ❌ PDP doesn't exist
```

---

## The Fix (2 lines)

### Option A: Update imports to use GuardianPDP

**File**: `lukhas/adapters/openai/api.py`

**Line 38**:
```python
# BEFORE
from lukhas.adapters.openai.policy_pdp import PDP

# AFTER
from lukhas.adapters.openai.policy_pdp import GuardianPDP as PDP
```

**Line 468**:
```python
# BEFORE
from lukhas.adapters.openai.policy_pdp import PDP, PolicyLoader

# AFTER
from lukhas.adapters.openai.policy_pdp import GuardianPDP as PDP, PolicyLoader
```

### Option B: Rename class back to PDP

**File**: `lukhas/adapters/openai/policy_pdp.py`

Change `class GuardianPDP:` back to `class PDP:`

---

## Testing

After fix, this should work:

```bash
# Test import
python3 -c "from lukhas.adapters.openai.policy_pdp import GuardianPDP as PDP; print('✅ Import works')"

# Test app initialization
python3 -c "from lukhas.adapters.openai.api import get_app; app = get_app(); print(f'PDP: {app.state.pdp}')"

# Run smoke test
python3 -m pytest tests/smoke/test_openai_facade.py::test_responses_minimal -xvs
```

---

## Impact When Fixed

### Immediately Available
- ✅ Guardian PDP initializes
- ✅ Policy enforcement active
- ✅ Smoke tests pass
- ✅ Guardian metrics generated
- ✅ Health reports include Guardian section

### Unblocks
- Claude: Full monitoring deployment
- Claude: Prometheus rules with real data
- Claude: Grafana dashboards populated
- Team: RC soak monitoring with Guardian metrics

---

## Temporary Workaround (For Testing Only)

```python
# In api.py, line 38, catch the specific error:
try:
    from lukhas.adapters.openai.policy_pdp import GuardianPDP as PDP
    GUARDIAN_AVAILABLE = True
except ImportError:
    try:
        from lukhas.adapters.openai.policy_pdp import PDP
        GUARDIAN_AVAILABLE = True
    except ImportError:
        GUARDIAN_AVAILABLE = False
        PDP = None
```

---

## Why This Matters

This is the **ONLY** blocker for:
1. Guardian policy enforcement
2. Complete monitoring deployment
3. RC soak period metrics
4. Security/denial metrics

**Fix effort**: 2 minutes
**Impact**: Unblocks entire Guardian + monitoring stack

---

## Recommended Action

**For Codex**:
1. Change line 38 in api.py: `from lukhas.adapters.openai.policy_pdp import GuardianPDP as PDP`
2. Change line 468 in api.py: `from lukhas.adapters.openai.policy_pdp import GuardianPDP as PDP, PolicyLoader`
3. Test: `pytest tests/smoke/test_openai_facade.py -v`
4. Commit as hot-fix

**For Claude**:
1. Monitor for this fix
2. Deploy monitoring immediately when it lands
3. Complete GA Guard Pack deployment

---

**Current Status**: 🔴 BLOCKED - 2-line fix needed
**Next Action**: Codex updates imports (2 min) → Claude deploys monitoring (20 min)

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>