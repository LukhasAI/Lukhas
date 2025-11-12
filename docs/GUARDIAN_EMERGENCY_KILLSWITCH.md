# Guardian Emergency Kill-Switch

## Overview

The Guardian Emergency Kill-Switch provides a **critical safety mechanism** for immediately disabling Guardian enforcement without code changes, API calls, or system restarts.

**Kill-Switch File Location:** `/tmp/guardian_emergency_disable`

When this file exists, all Guardian safety checks are bypassed:
- ✅ All drift detection returns 0.0 (no drift)
- ✅ All ethical evaluations allow actions
- ✅ All safety validation passes
- ⚠️ Constitutional AI enforcement is disabled

## Use Cases

### Production Incidents
- **Scenario:** Guardian incorrectly blocks critical business operations
- **Action:** Activate kill-switch immediately to restore operations
- **Follow-up:** File incident report and investigate root cause

### Emergency Deployments
- **Scenario:** Urgent hotfix needed but Guardian blocks deployment
- **Action:** Activate kill-switch for deployment window
- **Follow-up:** Deactivate immediately after deployment completes

### Testing & Development
- **Scenario:** Need to test Guardian behavior or validate bypass mechanisms
- **Action:** Activate kill-switch in test environment
- **Follow-up:** Verify Guardian re-activation after testing

### Guardian Misconfiguration
- **Scenario:** Guardian configuration error causes system-wide failures
- **Action:** Activate kill-switch while investigating and fixing configuration
- **Follow-up:** Validate fix in staging before deactivating in production

## Activation Methods

### Method 1: Command Line (Fastest)

```bash
# Activate with reason (RECOMMENDED)
echo "Incident #123: Guardian blocking production deployment" > /tmp/guardian_emergency_disable

# Or simple activation (touch command)
touch /tmp/guardian_emergency_disable
```

**Time to activate:** <1 second
**Requires:** Shell access to production servers

### Method 2: Programmatic Activation

```python
from governance.guardian.emergency_killswitch import activate_killswitch

# Activate with detailed reason for audit trail
activate_killswitch("Incident #456: Emergency maintenance window")
```

**Time to activate:** <2 seconds
**Requires:** Python environment and application code access

### Method 3: Configuration Management

```bash
# Ansible
ansible production -m file -a "path=/tmp/guardian_emergency_disable state=touch"

# Terraform (if managing temp files)
resource "local_file" "guardian_killswitch" {
  filename = "/tmp/guardian_emergency_disable"
  content  = "Terraform-managed emergency activation"
}
```

**Time to activate:** Depends on CM tool
**Requires:** Configuration management access

## Deactivation Methods

### Method 1: Command Line (Fastest)

```bash
# Remove kill-switch file
rm /tmp/guardian_emergency_disable
```

**Time to deactivate:** <1 second

### Method 2: Programmatic Deactivation

```python
from governance.guardian.emergency_killswitch import deactivate_killswitch

deactivate_killswitch()
```

**Time to deactivate:** <2 seconds

## Status Checking

### Command Line Check

```bash
# Check if kill-switch is active
if [ -f /tmp/guardian_emergency_disable ]; then
    echo "⚠️ Guardian kill-switch is ACTIVE"
    cat /tmp/guardian_emergency_disable
else
    echo "✅ Guardian is operational"
fi
```

### Programmatic Status Check

```python
from governance.guardian.emergency_killswitch import (
    is_emergency_killswitch_active,
    get_killswitch_status,
    read_killswitch_reason
)

# Simple boolean check
if is_emergency_killswitch_active():
    print("⚠️ Guardian is DISABLED")
    print(f"Reason: {read_killswitch_reason()}")

# Comprehensive status
status = get_killswitch_status()
print(f"Active: {status['active']}")
if status['active']:
    print(f"Reason: {status['reason']}")
    print(f"Activated at: {status['activated_at']}")
    print(f"Modified at: {status['modified_at']}")
```

### Guardian System Status

```python
from lukhas_website.lukhas.governance.guardian import GuardianSystemImpl

guardian = GuardianSystemImpl()
status = guardian.get_status()

print(f"Ethics Status: {status['ethics_status']}")
print(f"Safety Status: {status['safety_status']}")
print(f"Constitutional AI: {status['constitutional_ai']}")
print(f"Emergency Killswitch: {status['emergency_killswitch']}")
```

## Incident Response Runbook

### Step 1: Assess Situation (30 seconds)

**Questions to answer:**
- Is Guardian blocking critical operations?
- What is the business impact (revenue, users, SLA)?
- Can the issue wait for normal debugging?
- Is this a Guardian bug or correct enforcement?

**Decision Matrix:**
| Impact | Urgency | Action |
|--------|---------|--------|
| High | Critical | Activate kill-switch immediately |
| High | Non-critical | Debug Guardian first, kill-switch as backup |
| Low | Any | Do not activate, debug Guardian issue |

### Step 2: Activate Kill-Switch (10 seconds)

```bash
# SSH to production servers
ssh production-server-1

# Activate with incident number
echo "Incident #$(date +%Y%m%d-%H%M%S): [Brief description]" > /tmp/guardian_emergency_disable

# Verify activation
if [ -f /tmp/guardian_emergency_disable ]; then
    echo "✅ Kill-switch activated"
else
    echo "❌ Kill-switch activation FAILED"
fi
```

**Critical:** If operating multiple servers, activate on ALL servers running Guardian.

### Step 3: Verify Operations Restored (1 minute)

**Check these indicators:**
- [ ] Application health checks passing
- [ ] User operations completing successfully
- [ ] Error rates returning to normal
- [ ] Guardian logs show bypass messages

**Expected log messages:**
```
WARNING: Guardian emergency kill-switch is ACTIVE
INFO: Drift detection bypassed (killswitch active)
INFO: Ethics evaluation bypassed (killswitch active)
INFO: Safety validation bypassed (killswitch active)
```

### Step 4: Document Incident (2 minutes)

**Required documentation:**
- Incident ticket number
- Timestamp of activation
- Reason for activation
- Systems affected
- Business impact prevented
- Who authorized activation

**Example incident note:**
```
Incident: #2025-001
Activated: 2025-11-12T14:23:45Z
Reason: Guardian drift detection falsely flagging production traffic
Impact: 500+ users unable to complete checkout flow
Authorized: SRE on-call (Alice Smith)
Kill-switch file: /tmp/guardian_emergency_disable
```

### Step 5: Debug Guardian Issue (While Kill-Switch Active)

**Parallel investigation tasks:**
1. Collect Guardian logs from incident timeframe
2. Review Guardian configuration changes
3. Analyze false positive patterns
4. Test Guardian fixes in staging environment
5. Prepare Guardian configuration update

**Do NOT deactivate kill-switch until fix is validated.**

### Step 6: Prepare Guardian Fix (30-60 minutes)

**Fix validation checklist:**
- [ ] Fix tested in local development environment
- [ ] Fix tested in staging environment with production-like load
- [ ] Fix code reviewed by Guardian system owner
- [ ] Rollback plan prepared if fix fails
- [ ] Monitoring dashboards ready to track Guardian behavior

### Step 7: Deactivate Kill-Switch (30 seconds)

**Deactivation procedure:**
```bash
# SSH to production servers
ssh production-server-1

# Document deactivation reason
echo "Deactivating at $(date -Iseconds): Guardian fix deployed and validated" >> /tmp/guardian_deactivation_log

# Remove kill-switch file
rm /tmp/guardian_emergency_disable

# Verify deactivation
if [ ! -f /tmp/guardian_emergency_disable ]; then
    echo "✅ Kill-switch deactivated - Guardian ACTIVE"
else
    echo "❌ Kill-switch deactivation FAILED"
fi
```

**Critical:** Deactivate on ALL servers where it was activated.

### Step 8: Monitor Guardian Re-activation (15 minutes)

**Monitoring checklist:**
- [ ] Guardian status shows "active" for all components
- [ ] Drift detection running without false positives
- [ ] Ethics evaluation working correctly
- [ ] Safety validation passing appropriately
- [ ] No spike in Guardian-blocked operations
- [ ] Application health checks remain green

**If ANY issues detected:** Re-activate kill-switch and continue debugging.

### Step 9: Post-Incident Review (1 hour within 24 hours)

**Required analysis:**
1. Root cause of Guardian issue
2. Why Guardian protection failed (false positive)
3. What triggered the need for kill-switch
4. How to prevent similar incidents
5. Guardian configuration improvements needed
6. Kill-switch usage metrics and timing

**Deliverable:** Incident report with action items for Guardian improvements.

## Security Considerations

### Access Control

**File System Permissions:**
- `/tmp/guardian_emergency_disable` is world-writable (standard /tmp behavior)
- Any user with shell access can activate kill-switch
- Recommend: Monitor /tmp directory for unauthorized kill-switch activations

**Recommended Production Security:**
```bash
# Alert if kill-switch file created by non-authorized user
# Add to cron or monitoring system
if [ -f /tmp/guardian_emergency_disable ]; then
    owner=$(stat -f '%Su' /tmp/guardian_emergency_disable)
    if [ "$owner" != "app_user" ] && [ "$owner" != "sre_user" ]; then
        echo "🚨 ALERT: Kill-switch activated by unauthorized user: $owner"
        # Send alert to security team
    fi
fi
```

### Audit Trail

**All kill-switch operations are logged:**
- Activation: `CRITICAL` level log with reason and timestamp
- Status checks: `WARNING` level log each time Guardian is bypassed
- Deactivation: `INFO` level log with previous reason and timestamp

**Log monitoring recommendations:**
```bash
# Alert if kill-switch active for >5 minutes
find /tmp/guardian_emergency_disable -mmin +5 2>/dev/null && \
    echo "⚠️ Guardian kill-switch active for extended period"

# Daily kill-switch usage report
grep "emergency kill-switch" /var/log/application.log | \
    grep -E "(ACTIVATED|DEACTIVATED)" | \
    awk '{print $1, $2, $3}' > /tmp/killswitch_usage_report.txt
```

### Compliance Impact

**When kill-switch is active:**
- ❌ Guardian ethical enforcement is disabled
- ❌ Constitutional AI protections are bypassed
- ❌ Drift detection is not monitoring behavior changes
- ❌ Safety validation is not blocking unsafe content

**Required for compliance:**
1. Document every kill-switch activation in compliance log
2. Limit kill-switch activation to documented incidents
3. Review kill-switch usage in quarterly compliance audits
4. Implement alerting for kill-switch usage in production

## Monitoring & Alerting

### Production Monitoring Setup

**Required alerts:**

1. **Kill-Switch Activated Alert** (Critical)
   ```yaml
   alert: GuardianKillswitchActive
   expr: guardian_killswitch_active == 1
   for: 1m
   severity: critical
   annotations:
     summary: "Guardian emergency kill-switch is ACTIVE"
     description: "Guardian safety checks are bypassed. Investigate immediately."
   ```

2. **Kill-Switch Active >5 Minutes** (High)
   ```yaml
   alert: GuardianKillswitchExtended
   expr: guardian_killswitch_active == 1
   for: 5m
   severity: high
   annotations:
     summary: "Guardian kill-switch active for >5 minutes"
     description: "Kill-switch should be temporary. Investigate root cause."
   ```

3. **Kill-Switch Activation Count** (Info)
   ```yaml
   alert: GuardianKillswitchUsagePattern
   expr: increase(guardian_killswitch_activations[24h]) > 3
   severity: info
   annotations:
     summary: "Multiple Guardian kill-switch activations detected"
     description: "Investigate Guardian stability issues."
   ```

### Metrics to Track

**Prometheus metrics:**
```python
# Guardian kill-switch status (0 = inactive, 1 = active)
guardian_killswitch_active = Gauge('guardian_killswitch_active',
                                    'Guardian emergency kill-switch status')

# Kill-switch activation count
guardian_killswitch_activations = Counter('guardian_killswitch_activations_total',
                                          'Total Guardian kill-switch activations')

# Kill-switch duration histogram
guardian_killswitch_duration_seconds = Histogram('guardian_killswitch_duration_seconds',
                                                  'Duration of kill-switch activations')
```

### Dashboard Components

**Grafana dashboard panels:**
1. Current kill-switch status (big number panel, red when active)
2. Kill-switch activation timeline (time series)
3. Kill-switch activation count (per day/week)
4. Average kill-switch duration
5. Kill-switch reason (text panel, latest activation reason)
6. Guardian component status (all components show "disabled" when kill-switch active)

## Testing Procedures

### Development Environment Testing

```bash
# Test kill-switch activation
cd /Users/agi_dev/LOCAL-REPOS/Lukhas-guardian-killswitch

# Run comprehensive test suite
pytest tests/unit/governance/guardian/test_emergency_killswitch.py -v

# Run Guardian integration tests with kill-switch
pytest tests/integration/guardian/ -v -k killswitch

# Test kill-switch in local development
python3 << 'EOF'
from governance.guardian.emergency_killswitch import activate_killswitch, is_emergency_killswitch_active, deactivate_killswitch

# Test activation
activate_killswitch("Development testing")
assert is_emergency_killswitch_active(), "Kill-switch should be active"

# Test Guardian bypass
from lukhas_website.lukhas.governance.guardian import GuardianSystemImpl
guardian = GuardianSystemImpl()
status = guardian.get_status()
assert status['ethics_status'] == 'disabled_by_killswitch', "Guardian should be disabled"

# Test deactivation
deactivate_killswitch()
assert not is_emergency_killswitch_active(), "Kill-switch should be inactive"

print("✅ All kill-switch tests passed")
EOF
```

### Staging Environment Testing

```bash
# Deploy kill-switch feature to staging
# Test realistic incident scenario

# 1. Simulate Guardian blocking operation (before kill-switch)
# 2. Activate kill-switch
echo "Staging test: Simulated incident" > /tmp/guardian_emergency_disable

# 3. Verify Guardian bypass
curl http://staging-api/guardian/status | jq '.emergency_killswitch.active'
# Should return: true

# 4. Verify operations succeed
# (Run previously blocked operations)

# 5. Deactivate kill-switch
rm /tmp/guardian_emergency_disable

# 6. Verify Guardian re-activation
curl http://staging-api/guardian/status | jq '.emergency_killswitch.active'
# Should return: false
```

### Production Pre-Deployment Checklist

- [ ] Kill-switch tested in development environment
- [ ] Kill-switch tested in staging environment
- [ ] Monitoring alerts configured for kill-switch activation
- [ ] Runbook documented and reviewed by SRE team
- [ ] Kill-switch file path documented in incident response procedures
- [ ] Access control reviewed (who can activate/deactivate)
- [ ] Compliance team notified of kill-switch capability
- [ ] Post-incident review template includes kill-switch analysis
- [ ] Rollback plan prepared if kill-switch causes issues

## FAQ

### Q: When should I activate the kill-switch?

**A:** Activate when Guardian is blocking critical business operations and:
1. Immediate fix is not possible (complex Guardian debugging needed)
2. Business impact is high (revenue loss, SLA violation, major user impact)
3. No alternative workaround available
4. Incident commander or SRE on-call authorizes activation

**Do NOT activate** for non-critical issues that can wait for proper debugging.

### Q: How long can the kill-switch stay active?

**A:** **Maximum: 1 hour** for production systems. If Guardian fix takes longer:
1. Document extended kill-switch usage
2. Get approval from engineering leadership
3. Implement temporary monitoring to compensate for disabled Guardian
4. Escalate Guardian issue as P0 incident

### Q: What if kill-switch file is deleted by system cleanup?

**A:** The `/tmp` directory may be cleaned by system processes:
- Some systems clear `/tmp` on reboot
- Some systems run periodic `/tmp` cleanup (tmpwatch, systemd-tmpfiles)

**Protection strategy:**
```bash
# Option 1: Touch file periodically to update timestamp
watch -n 60 'touch /tmp/guardian_emergency_disable'

# Option 2: Use persistent location (requires code change)
# KILLSWITCH_PATH = "/var/run/guardian_emergency_disable"

# Option 3: Monitor and re-create if deleted
while true; do
    if [ ! -f /tmp/guardian_emergency_disable ]; then
        echo "Incident continues: $(date)" > /tmp/guardian_emergency_disable
    fi
    sleep 10
done
```

### Q: Can I activate kill-switch for specific Guardian components only?

**A:** No. The current implementation is **all-or-nothing**:
- Kill-switch active = ALL Guardian components bypassed
- Kill-switch inactive = ALL Guardian components active

**Feature request:** Granular kill-switch (per-component) could be added in future versions.

### Q: What happens to in-flight requests when kill-switch is activated?

**A:** Guardian checks happen **per-request**:
- Requests in progress before activation: Use Guardian (with enforcement)
- Requests after activation: Bypass Guardian (no enforcement)
- No restart or connection reset required

### Q: How do I test kill-switch without affecting production?

**A:** Use the mock kill-switch path in tests:
```python
from unittest.mock import patch

with patch('governance.guardian.emergency_killswitch.KILLSWITCH_PATH', '/tmp/test_killswitch'):
    # Your test code here
    # Uses /tmp/test_killswitch instead of /tmp/guardian_emergency_disable
```

### Q: Is the kill-switch logged in application logs?

**A:** Yes. Every kill-switch check logs:
- `WARNING` level: "Guardian emergency kill-switch is ACTIVE"
- Includes: reason, timestamp, kill-switch file path

Additionally:
- `CRITICAL` level on activation
- `INFO` level on deactivation

### Q: What if multiple servers have different kill-switch states?

**A:** **This is a problem!** Kill-switch should be consistent across all servers:

**Symptoms:**
- Some servers bypass Guardian, others enforce
- Inconsistent user experience
- Some requests blocked, others allowed

**Resolution:**
```bash
# Check kill-switch status on all servers
ansible production -m shell -a "test -f /tmp/guardian_emergency_disable && echo ACTIVE || echo INACTIVE"

# Activate on all servers
ansible production -m file -a "path=/tmp/guardian_emergency_disable state=touch"

# Deactivate on all servers
ansible production -m file -a "path=/tmp/guardian_emergency_disable state=absent"
```

## Version History

- **v1.0.0** (2025-11-12): Initial implementation
  - Basic kill-switch activation/deactivation
  - Integration with Guardian drift detection, ethics, and safety checks
  - Comprehensive test suite (35+ tests)
  - Production-ready documentation and runbook

## Related Documentation

- [Guardian System Architecture](../docs/architecture/guardian.md)
- [Constitutional AI Implementation](../docs/architecture/constitutional_ai.md)
- [Incident Response Procedures](../docs/operations/incident_response.md)
- [Production Runbooks](../docs/operations/runbooks.md)

## Support & Contact

**For kill-switch issues:**
- Development: Check `tests/unit/governance/guardian/test_emergency_killswitch.py`
- Production: Follow incident response runbook above
- Questions: Contact Guardian system maintainers

**Emergency contacts:**
- SRE On-Call: [Your on-call system]
- Guardian Team: [Team contact]
- Security Team: [Security contact for compliance questions]
