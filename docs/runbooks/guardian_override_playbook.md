---
status: wip
type: documentation
---
# Guardian Override Playbook

## 🚨 Emergency Guardian Override Process

**Use Case**: When Guardian safety enforcement blocks legitimate critical operations requiring emergency bypass.

**Authorization Level**: T4+ dual approval required

**Maximum Override Duration**: 4 hours

---

## Prerequisites

- [ ] **Two T4+ staff members available** (different individuals required)
- [ ] **Valid business justification** (documented in ticket)
- [ ] **Incident response active** (if emergency)
- [ ] **Override window ≤4 hours** (auto-expiry enforced)

---

## Step 1: Identify Override Need

### Guardian Block Scenarios
```bash
# Check Guardian decision logs
kubectl logs -l app=guardian -n lukhas --tail=100 | grep "BLOCKED"

# Sample blocked output:
# Guardian BLOCKED operation: plan_id=abc123, reason=PII_FINANCIAL_DUAL_RISK, tier=T5
```

### Verify Legitimate Block
- Confirm operation is business-critical
- Verify Guardian logic is correct but overly restrictive
- Ensure no security incident in progress

---

## Step 2: Initiate Dual Approval

### Code Location: `guardian/emit.py:L74-83`

```python
# Verify dual approval function
def verify_dual_approval(approver1_id: str, approver2_id: str, get_tier_fn):
    """Verify dual approval for critical Guardian overrides.

    Args:
        approver1_id: ΛiD of first approver (must be T4+)
        approver2_id: ΛiD of second approver (must be T4+)
        get_tier_fn: Function to retrieve approver tier level

    Raises:
        ValueError: If same approver used twice
        PermissionError: If approvers not T4+
    """
```

### Execute Override
```python
# Example override process
from guardian.emit import verify_dual_approval, emit_guardian_decision

# Step 1: Get approver IDs
approver1_id = "λid:alice.t4"  # T4+ staff member 1
approver2_id = "λid:bob.t4"    # T4+ staff member 2

# Step 2: Verify authorization
verify_dual_approval(approver1_id, approver2_id, get_user_tier)

# Step 3: Grant temporary override
override_decision = {
    "plan_id": "emergency_plan_001",
    "override_granted": True,
    "approver1_id": approver1_id,
    "approver2_id": approver2_id,
    "justification": "Emergency financial transaction processing failure",
    "retention_days": 30,
    "expires_at": datetime.utcnow() + timedelta(hours=4)
}

emit_guardian_decision(db, **override_decision)
```

---

## Step 3: Database Override Record

### Schema: `identity/consent/exemption_ledger.sql:L16-21`

```sql
-- Override record structure
INSERT INTO exemption_ledger (
    operation_type,
    risk_level,
    justification,
    override_requested,
    override_granted,
    approver1_id,        -- T4+ approver 1
    approver2_id,        -- T4+ approver 2
    retention_days,
    created_at
) VALUES (
    'PII_FINANCIAL_PROCESSING',
    'HIGH',
    'Emergency payment processing system failure requiring manual intervention',
    TRUE,
    TRUE,
    'λid:alice.t4',
    'λid:bob.t4',
    30,
    NOW()
);
```

---

## Step 4: Execute Protected Operation

```bash
# Set override environment variable
export LUKHAS_GUARDIAN_OVERRIDE="emergency_plan_001"
export GUARDIAN_OVERRIDE_EXPIRES="2024-01-15T18:00:00Z"

# Execute protected operation
lukhas execute --plan emergency_plan_001 --override-authorized

# Verify operation completion
lukhas status --plan emergency_plan_001
```

---

## Step 5: Post-Override Actions

### Immediate (Within 1 hour)
- [ ] **Document incident** in runbook
- [ ] **Monitor system behavior** for anomalies
- [ ] **Set override expiry reminder** (max 4 hours)

### Within 24 hours
- [ ] **Review Guardian rules** that triggered override
- [ ] **Update Guardian logic** if rules too restrictive
- [ ] **Conduct override retrospective** with approvers

### Within 1 week
- [ ] **Audit override usage** in exemption ledger
- [ ] **Update playbook** if process gaps identified
- [ ] **Train staff** on any process improvements

---

## Emergency Contacts

| Role | Contact | Tier |
|------|---------|------|
| Security Lead | security@lukhas.ai | T5 |
| Architecture Lead | arch@lukhas.ai | T4 |
| DevOps On-Call | devops@lukhas.ai | T4 |
| Incident Commander | incident@lukhas.ai | T4+ |

---

## Common Override Scenarios

### Financial Transaction Failures
```bash
# Scenario: Payment processing blocked by Guardian
# Guardian Error: PII_FINANCIAL_DUAL_RISK detected
# Business Impact: Customer payments failing
# Override Duration: 2 hours
# Required: T4+ Finance + T4+ Security approval
```

### Emergency Data Recovery
```bash
# Scenario: Data recovery blocked by retention limits
# Guardian Error: DATA_RETENTION_VIOLATION
# Business Impact: Critical data loss imminent
# Override Duration: 4 hours
# Required: T4+ Data + T4+ Legal approval
```

### Critical System Maintenance
```bash
# Scenario: Maintenance blocked by high-risk operation detection
# Guardian Error: SYSTEM_MODIFICATION_RISK
# Business Impact: System degradation without maintenance
# Override Duration: 3 hours
# Required: T4+ Engineering + T4+ Security approval
```

---

## Compliance & Auditing

### Override Audit Query
```sql
-- Review all overrides in last 30 days
SELECT
    operation_type,
    justification,
    approver1_id,
    approver2_id,
    created_at,
    retention_days
FROM exemption_ledger
WHERE override_granted = TRUE
  AND created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;
```

### Required Documentation
- Override justification (business impact)
- Dual approver verification (T4+ only)
- Time-bounded duration (≤4 hours)
- Post-override review within 24 hours

---

## Security Notes

⚠️ **CRITICAL**: Guardian overrides bypass all safety enforcement
⚠️ **TIME-LIMITED**: All overrides auto-expire (max 4 hours)
⚠️ **AUDITED**: Every override logged in immutable ledger
⚠️ **DUAL-APPROVAL**: Always requires two T4+ approvers

**Emergency Override Hotline**: +1-555-LUKHAS-911