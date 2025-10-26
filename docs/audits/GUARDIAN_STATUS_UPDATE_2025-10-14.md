# Guardian Status Update - 2025-10-14

**Current Branch**: `fix/guardian-yaml-compat` (commit `6aa1a219e`)
**Status**: 🔴 **Partially Fixed** - Still has issues

---

## What Was Fixed

### ✅ Normalization Functions Added
- `_normalize_rule()` function added to `policy_pdp.py`
- `_normalize_policy()` function added
- Handles legacy `when` → `conditions` mapping
- Provides defaults for missing fields

### ✅ Validation Scripts Added
- `scripts/validate_guardian_policy.py` - Validates YAML format
- `tests/guardian/test_policy_format_compat.py` - Tests compatibility

---

## Remaining Issues

### 1. 🔴 Incomplete Normalization
The normalization doesn't extract actions/resources from nested structures:

**Current YAML**:
```yaml
when:
  action: { route: "/v1/dreams", verb: "POST" }
  resource: { sensitivity: "restricted" }
```

**Result**:
- `actions: []` (empty - should extract from `when.action`)
- `resources: []` (empty - should extract from `when.resource`)
- Everything dumped into `conditions` dict

### 2. 🔴 PDP Import Scope Issue
In `lukhas/adapters/openai/api.py`:
- Line 38: `from lukhas.adapters.openai.policy_pdp import PDP` (in try/except)
- Line 311: `app.state.pdp = PDP(policy)` (references PDP)
- Error: "local variable 'PDP' referenced before assignment"

**Root Cause**: If ANY import fails in lines 37-46, PDP becomes None, but GUARDIAN_AVAILABLE might still be True.

### 3. 🔴 Validation Failures
```bash
$ python3 scripts/validate_guardian_policy.py
{
  "ok": false,
  "errors": [
    "actions must be a non-empty string or list of strings",
    "resources must be a non-empty string or list of strings"
  ]
}
```

---

## Impact on Monitoring

### What Works
- ✅ Prometheus recording rules ready (`lukhas/observability/rules/guardian-rl.rules.yml`)
- ✅ Grafana dashboard ready (`lukhas/observability/grafana/guardian-rl-dashboard.json`)
- ✅ Deployment scripts ready (`scripts/deploy_monitoring_post_390.sh`)
- ✅ Health audit framework ready

### What's Blocked
- ❌ Guardian PDP doesn't initialize → no Guardian metrics
- ❌ Smoke tests fail with 401 (auth not working)
- ❌ Health reports missing Guardian section
- ❌ Grafana panels will be empty (no data source)

---

## Required Fixes (Codex Lane)

### Option A: Fix Normalization (Recommended)
Update `_normalize_rule()` to extract actions/resources:

```python
def _normalize_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    # ... existing code ...

    # Extract actions from when.action
    when = data.get("when", {})
    if "action" in when:
        action_data = when["action"]
        if isinstance(action_data, dict):
            verb = action_data.get("verb", "")
            route = action_data.get("route", "")
            if verb:
                normalized["actions"] = [verb]
            if route:
                normalized["resources"] = [route]

    # Extract resources from when.resource
    if "resource" in when:
        resource_data = when["resource"]
        # Handle resource extraction...
```

### Option B: Update YAML Format
Change `configs/policy/guardian_policies.yaml` to explicit format:

```yaml
version: 1
rules:
  - id: allow-authenticated-responses
    effect: Allow
    subjects:
      any:
        - scopes_any: ["api.responses"]
    actions: ["POST"]
    resources: ["/v1/responses"]
    conditions: {}
    obligations: []
```

### Option C: Fix Import Scope
Ensure PDP is properly imported:

```python
# At module level
from lukhas.adapters.openai.policy_pdp import PDP, PolicyLoader

# In get_app()
if os.path.exists(policy_path):
    policy = PolicyLoader.load_from_file(policy_path)
    app.state.pdp = PDP(policy)
```

---

## Alternative: Deploy Without Guardian

Since the monitoring infrastructure is ready, we could:

1. **Deploy Prometheus rules anyway** - They'll return 0 values but won't break
2. **Deploy Grafana dashboard** - Panels will be empty but structure is there
3. **Document known issue** - Guardian metrics pending fix
4. **Focus on Rate Limiting metrics** - Those might still work

---

## Next Steps

### For Codex (Hot-Path Owner)
1. Fix normalization to properly extract actions/resources from `when` clause
2. Fix PDP import scope issue in api.py
3. Update YAML to explicit format if normalization too complex
4. Ensure smoke tests pass

### For Claude (Observability Owner)
1. Deploy monitoring infrastructure even with empty Guardian metrics
2. Focus on Rate Limiting and other operational metrics
3. Document Guardian metrics as "pending fix"
4. Be ready to validate once fix lands

---

## Test Commands (For Verification)

```bash
# Check if Guardian loads properly
python3 -c "
from lukhas.adapters.openai.policy_pdp import PolicyLoader
p = PolicyLoader.load_from_file('configs/policy/guardian_policies.yaml')
for r in p.rules:
    print(f'{r.id}: actions={r.actions}, resources={r.resources}')
"

# Check if PDP initializes
python3 -c "
from lukhas.adapters.openai.api import get_app
app = get_app()
print(f'PDP: {app.state.pdp}')
"

# Run smoke test
python3 -m pytest tests/smoke/test_openai_facade.py::test_responses_minimal -xvs

# Validate policy
python3 scripts/validate_guardian_policy.py
```

---

**Current Status**: 🔴 Guardian partially fixed but still not functional
**Blocking**: Full monitoring deployment with Guardian metrics
**Not Blocking**: Rate Limiting metrics, health monitoring, general observability

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>