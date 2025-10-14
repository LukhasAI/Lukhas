# Issue: Guardian Policy YAML Format Mismatch

**Date**: 2025-10-14
**Severity**: 🔴 High (blocks smoke tests)
**Owner**: Codex (hot-path adapter lane)
**Lane**: `lukhas/adapters/openai/` (hot-path, off-limits for Claude)

---

## Symptom

Smoke tests fail with:
```
WARNING lukhas.adapters.openai.api:api.py:317 Failed to initialize Guardian PDP:
__init__() missing 4 required positional arguments: 'subjects', 'actions', 'resources', and 'obligations'
```

Tests expecting 200 get 401 (auth failures because Guardian PDP not initialized).

---

## Root Cause

**Policy YAML format** (`configs/policy/guardian_policies.yaml`) doesn't match **Rule dataclass** expectations (`lukhas/adapters/openai/policy_models.py`).

### YAML Format (line 3-12):
```yaml
rules:
  - id: deny-sensitive-dreams
    when:  # ❌ Should be parsed to 'actions' + 'resources'
      action: { route: "/v1/dreams", verb: "POST" }
      resource: { sensitivity: "restricted" }
    unless:  # ❌ Should be parsed to 'conditions' (negated)
      subject:  # ❌ Should be 'subjects' (plural)
        scopes: ["dreams:restricted"]
    effect: deny
  - id: allow-default
    effect: allow  # ❌ Missing required fields
```

### Rule Dataclass (policy_models.py:37-45):
```python
@dataclass
class Rule:
    id: str
    effect: str  # "Allow" | "Deny"
    subjects: Dict[str, Any]  # ✅ Required
    actions: List[str]        # ✅ Required
    resources: List[str]      # ✅ Required
    conditions: Dict[str, Any]  # ✅ Required
    obligations: List[Dict[str, Any]]  # ✅ Required
```

### Policy Normalization Logic (policy_pdp.py:27-39):
```python
# Normalize rules: map 'when' to 'conditions' and filter unknown keys
for r in raw_rules:
    rule_dict = dict(r)
    # If YAML has 'when' but Rule expects 'conditions', rename the key
    if "when" in rule_dict and "conditions" not in rule_dict:
        rule_dict["conditions"] = rule_dict.pop("when")  # ⚠️ Partial fix
    # Remove keys that Rule doesn't accept (like 'unless')
    valid_keys = {"id", "effect", "subjects", "actions", "resources", "conditions", "obligations"}
    filtered_dict = {k: v for k, v in rule_dict.items() if k in valid_keys}
    normalized_rules.append(Rule(**filtered_dict))  # ❌ FAILS HERE
```

**Problem**: The normalization only handles `when` → `conditions`, but doesn't:
1. Extract `actions` from `when.action`
2. Extract `resources` from `when.resource`
3. Parse `unless` → `conditions` (negated logic)
4. Convert `subject` → `subjects`
5. Provide default empty lists for missing required fields

---

## Impact

- ✅ Guardian PDP **never initializes** (always falls back to permissive mode)
- ✅ All Guardian metrics **return zero** (PDP not active)
- ✅ Smoke tests expecting auth **fail with 401**
- ✅ Recording rules **can't test** (no source metrics)
- ✅ Grafana dashboard **shows empty panels**

---

## Fix Options

### Option A: Update YAML to match Rule schema (RECOMMENDED)

**New format** (explicit fields):
```yaml
version: 1
tenant_id: "default"
rules:
  - id: deny-sensitive-dreams
    effect: Deny
    subjects:
      any:
        - scopes_any: ["dreams:restricted"]  # Only allow if has this scope
    actions: ["POST"]
    resources: ["/v1/dreams"]
    conditions:
      data_classification_max: "internal"  # Block restricted data
    obligations: []

  - id: allow-authenticated-responses
    effect: Allow
    subjects:
      any:
        - scopes_any: ["api.responses", "responses:write"]
    actions: ["POST"]
    resources: ["/v1/responses"]
    conditions: {}
    obligations: []

  - id: allow-models-read
    effect: Allow
    subjects:
      any:
        - scopes_any: ["api.read", "models:read"]
    actions: ["GET"]
    resources: ["/v1/models"]
    conditions: {}
    obligations: []

  - id: default-deny
    effect: Deny
    subjects:
      any: [{}]  # Match all
    actions: ["*"]
    resources: ["*"]
    conditions: {}
    obligations: []
```

**Pros**:
- Works with existing Rule dataclass
- No code changes needed
- Matches PR #380 design

**Cons**:
- More verbose YAML
- Need to migrate existing policy

---

### Option B: Improve normalization logic (COMPLEX)

**Update `Policy.__init__` to fully parse YAML**:
```python
def _normalize_rule(self, raw_rule: Dict[str, Any]) -> Rule:
    """Converts flexible YAML format to strict Rule dataclass."""
    rule_id = raw_rule.get("id", "unknown")
    effect = raw_rule.get("effect", "Deny").capitalize()

    # Parse 'when' clause → actions + resources
    when = raw_rule.get("when", {})
    actions = self._extract_actions(when.get("action", {}))
    resources = self._extract_resources(when.get("resource", {}))

    # Parse 'unless' clause → conditions (negated)
    unless = raw_rule.get("unless", {})
    subjects = self._extract_subjects(unless.get("subject", {}))
    conditions = self._extract_conditions(when, unless)

    # Default empty obligations
    obligations = raw_rule.get("obligations", [])

    return Rule(
        id=rule_id,
        effect=effect,
        subjects=subjects or {"any": [{}]},  # Default match-all
        actions=actions or ["*"],
        resources=resources or ["*"],
        conditions=conditions or {},
        obligations=obligations
    )
```

**Pros**:
- Keeps YAML concise
- Backward compatible

**Cons**:
- Complex parsing logic
- Need helper methods for extracting fields
- Risk of bugs in normalization

---

## Recommended Action

**Use Option A** (update YAML) because:
1. It's what PR #380 intended (the Rule dataclass design was the "canonical" format)
2. Zero code risk (just data changes)
3. Clearer for policy authors
4. Matches Guardian design doc

**Steps**:
1. Update `configs/policy/guardian_policies.yaml` with explicit schema
2. Add smoke test for policy loading: `pytest tests/unit/test_guardian_policy_loading.py`
3. Re-run facade smoke tests
4. Commit as hot-path fix

---

## Testing Checklist

After fix:
- [ ] `python3 -c "from lukhas.adapters.openai.policy_pdp import PolicyLoader; p = PolicyLoader.load_from_file('configs/policy/guardian_policies.yaml'); print(f'Loaded {len(p.rules)} rules')"`
- [ ] `pytest tests/smoke/test_openai_facade.py -v` (should pass)
- [ ] `python3 scripts/system_health_audit.py` → Guardian section populated
- [ ] Guardian metrics visible in Prometheus

---

## Lane Ownership

- **This issue**: Codex lane (hot-path adapter code + policy format)
- **Blocked tasks**: Claude lane (Prometheus rules deploy, Grafana dashboard, health artifacts)
- **Coordination**: Once Codex fixes this, Claude can deploy monitoring stack

---

**Status**: 🔴 Blocking
**Assigned**: Codex
**Priority**: P0 (unblocks GA Guard Pack operationalization)
