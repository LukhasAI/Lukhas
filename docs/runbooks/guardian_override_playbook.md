# Guardian Override Playbook

## Emergency Kill-Switch Activation

**When to use**: Only for critical incidents where Guardian is causing production issues

**Activation steps**:
1. Senior engineer authorization required
2. Create kill-switch file: `touch /tmp/guardian_emergency_disable`
3. OR set environment: `GUARDIAN_EMERGENCY_DISABLE=1`
4. Verify Guardian is disabled in logs
5. Document incident in #incidents Slack channel

**Deactivation**:
1. Remove kill-switch: `rm /tmp/guardian_emergency_disable`
2. Verify Guardian re-enabled
3. Post-incident review within 24 hours

## Dual-Approval Override Process

**Context**: Guardian blocks require two approvals for override

**Process**:
1. First approver reviews Guardian block decision
2. Documents override justification
3. Second independent approver reviews
4. Both approvers log approval in audit trail
5. Override logged to `reports/guardian/overrides.jsonl`

**Code integration**: Use existing `guardian.dual_approval_override()` method

## Incident Response Contacts
- On-call: [PagerDuty rotation]
- Ethics lead: [Contact]
- Security lead: [Contact]
