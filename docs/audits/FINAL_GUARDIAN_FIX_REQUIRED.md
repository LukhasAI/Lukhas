# Final Guardian Fix Required

**Date**: 2025-10-14
**Severity**: 🔴 CRITICAL
**Location**: `lukhas/adapters/openai/policy_pdp.py` line 61
**Fix Time**: 1 minute

---

## The Problem

The `Rule` dataclass REQUIRES these fields but the normalization doesn't provide them:
- `subjects` (Dict[str, Any])
- `actions` (List[str])
- `resources` (List[str])
- `obligations` (List[Dict[str, Any]])

**Error**: `TypeError: __init__() missing 4 required positional arguments: 'subjects', 'actions', 'resources', and 'obligations'`

---

## The Fix

### Option A: Provide defaults when creating Rule (SIMPLEST - 1 line fix)

**File**: `lukhas/adapters/openai/policy_pdp.py`
**Line**: 61

```python
# BEFORE (line 61)
normalized_rules.append(Rule(**filtered_dict))

# AFTER
normalized_rules.append(Rule(
    id=filtered_dict.get('id', 'unknown'),
    effect=filtered_dict.get('effect', 'deny'),
    subjects=filtered_dict.get('subjects', {}),
    actions=filtered_dict.get('actions', []),
    resources=filtered_dict.get('resources', []),
    conditions=filtered_dict.get('conditions', {}),
    obligations=filtered_dict.get('obligations', [])
))
```

### Option B: Make Rule fields optional with defaults

**File**: `lukhas/adapters/openai/policy_models.py`

```python
@dataclass
class Rule:
    """Represents a single policy rule."""
    id: str
    effect: str  # "Allow" | "Deny"
    subjects: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    obligations: List[Dict[str, Any]] = field(default_factory=list)
```

### Option C: Ensure filtered_dict has all required keys

**File**: `lukhas/adapters/openai/policy_pdp.py`
**Lines**: 57-61

```python
# Ensure all required fields exist
filtered_dict.setdefault('subjects', {})
filtered_dict.setdefault('actions', [])
filtered_dict.setdefault('resources', [])
filtered_dict.setdefault('obligations', [])
normalized_rules.append(Rule(**filtered_dict))
```

---

## Testing After Fix

```bash
# Test policy loads
python3 -c "
from lukhas.adapters.openai.policy_pdp import PolicyLoader
p = PolicyLoader.load_from_file('configs/policy/guardian_policies.yaml')
print(f'✅ Loaded {len(p.rules)} rules')
"

# Test PDP initializes
python3 -c "
from lukhas.adapters.openai.api import get_app
app = get_app()
print(f'✅ PDP: {app.state.pdp}')
"

# Run smoke test
python3 -m pytest tests/smoke/test_openai_facade.py::test_responses_minimal -xvs
```

---

## Impact When Fixed

This is the FINAL blocker. Once fixed:
1. ✅ Guardian PDP initializes
2. ✅ Policy enforcement active
3. ✅ Smoke tests pass
4. ✅ Guardian metrics available
5. ✅ Full monitoring deployment unblocked
6. ✅ RC soak monitoring begins

---

## Recommendation

Use **Option A** - it's the simplest, most explicit fix that doesn't change the dataclass contract.

---

**Current Status**: 🔴 One line away from working
**Next**: Apply fix → Guardian works → Deploy monitoring

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>