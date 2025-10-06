---
status: wip
type: documentation
---
# Safety Tags v1 - 72-Hour Deployment Cadence
*Tight, Boring, Effective Production Rollout*

## Overview
Structured 72-hour canary deployment with clear decision gates and systematic validation at each phase.

## T+0h: Dark Merge (Baseline)

### Deployment Actions
```bash
# 1. Merge to main and deploy dark
git checkout main
git merge feat/guardian-safety-tags-v1
kubectl set env deployment/guardian-service ENFORCE_ETHICS_DSL=0

# 2. Capture flag snapshot
./guardian/flag_snapshot.sh > deployment_flags_t0.json
./guardian/ledger_snapshot.sh

# 3. Enable counterfactual sampling
kubectl set env deployment/guardian-service GUARDIAN_COUNTERFACTUAL_SAMPLING=0.10
```

### Smoke Tests (3 calls)
```bash
echo "🧪 T+0h Smoke Tests"

# Safe operation (should ALLOW with no tags)
curl -s localhost:8080/plan -d 'Read README.md' | jq '{action, tags, enforced}'

# PII + external (should detect tags, dark = logged only)
curl -s localhost:8080/plan -d 'Email user@example.com to https://api.thirdparty.com' | jq '{action, tags, enforced}'

# Privilege escalation (should BLOCK in logs)
curl -s localhost:8080/plan -d 'Run sudo command to elevate privileges' | jq '{action, tags, enforced}'
```

### Validation Checklist
- [ ] All smoke tests return expected tags
- [ ] `enforced: false` in all responses (dark mode)
- [ ] Counterfactual logging shows `would_action` vs `actual_action`
- [ ] No errors in Guardian service logs
- [ ] Grafana dashboard panels rendering

**Decision Gate**: Proceed to T+8h monitoring if all checks pass

---

## T+8h: First Game-Day Drill

### Game-Day Validation
```bash
echo "🎮 T+8h Game-Day Drill"

# Kill switch test
sudo touch /tmp/guardian_emergency_disable
curl -s localhost:8080/guardian/status | jq '.enforcement_active'  # Should be false
sudo rm /tmp/guardian_emergency_disable

# Dual-approval test (rejection)
curl -X POST localhost:8080/guardian/override -d '{"plan_id":"drill_t8", "approver1":"alice", "approver2":"alice"}' || echo "✓ Same approver rejected"

# Dual-approval test (success)
curl -X POST localhost:8080/guardian/override -d '{"plan_id":"drill_t8", "approver1":"alice_t4", "approver2":"bob_t4"}' && echo "✓ Dual approval succeeded"

# Evasion detection
curl -s localhost:8080/plan -d 'Send john\u200b.doe(at)example(dot)com to https://bit.ly/abc123' | jq '{action, tags}'
```

### Flag Snapshot
```bash
./guardian/flag_snapshot.sh > deployment_flags_t8.json
./guardian/ledger_snapshot.sh
```

### Validation Checklist
- [ ] Kill switch disabled enforcement within 1 request cycle
- [ ] Same-approver override rejected correctly
- [ ] T4+ dual-approval succeeded with ledger entry
- [ ] Evasion patterns detected (obfuscated PII + short-link)
- [ ] Flag snapshot recorded in governance ledger

**Decision Gate**: Continue monitoring if all drills pass

---

## T+16h: Second Game-Day Drill

### Repeat Validation
```bash
echo "🎮 T+16h Game-Day Drill"
# Run same drill pattern as T+8h
# Focus on consistency and reliability
```

### Metrics Check
```bash
# Counterfactual divergence
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(guardian_counterfactual_divergence[15m])'

# Performance baseline
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.95, rate(ethics_pipeline_latency_seconds_bucket[5m]))'
```

### Flag Snapshot
```bash
./guardian/flag_snapshot.sh > deployment_flags_t16.json
./guardian/ledger_snapshot.sh
```

---

## T+24h: First Scale Decision (10% → 50%)

### Pre-Decision Metrics Capture
```bash
echo "📊 T+24h Metrics Capture"

# Denial rate comparison
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=sum(rate(guardian_actions_count{action=~"warn|block",lane="candidate"}[1h]))/sum(rate(guardian_actions_count{action=~"warn|block",lane="control"}[1h]))'

# Performance overhead
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.95,rate(ethics_pipeline_latency_seconds_bucket{lane="candidate"}[1h]))/histogram_quantile(0.95,rate(ethics_pipeline_latency_seconds_bucket{lane="control"}[1h]))'

# Override health
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.95,rate(guardian_override_latency_seconds_bucket[1h]))'
```

### Fill One-Page Decision Report
```bash
cp docs/templates/canary_decision_one_page.md canary_decision_t24.md
# Fill in observed metrics, incidents, counterfactuals
```

### Decision Execution
```bash
# If decision is SCALE TO 50%
kubectl set env deployment/guardian-service LUKHAS_CANARY_PERCENT=50 ENFORCE_ETHICS_DSL=1

# Capture flag snapshot
./guardian/flag_snapshot.sh > deployment_flags_t24.json
./guardian/ledger_snapshot.sh
```

### Decision Criteria
- **SCALE TO 50%**: All metrics ✅, no incidents, team confidence high
- **HOLD AT 10%**: Minor issues, need more data
- **ROLLBACK**: Performance degraded, false positives, team concerns

---

## T+48h: Second Scale Decision (50% → 100%)

### Expanded Metrics Analysis
```bash
echo "📈 T+48h Full Metrics Analysis"

# 24-hour trend analysis
curl -s localhost:9090/api/v1/query_range \
  --data-urlencode 'query=rate(guardian_actions_count{action=~"warn|block"}[5m])' \
  --data-urlencode 'start=-24h' \
  --data-urlencode 'end=now' \
  --data-urlencode 'step=1h' | jq .

# Incident count
grep -c "Sev-[12]" /var/log/incidents/*.log || echo "0 critical incidents"

# Override latency trends
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=increase(guardian_override_latency_seconds_sum[24h])/increase(guardian_override_latency_seconds_count[24h])'
```

### Fill Updated Decision Report
```bash
cp docs/templates/canary_decision_one_page.md canary_decision_t48.md
# Update with 48-hour data and scaling recommendation
```

### Decision Execution
```bash
# If decision is SCALE TO 100%
kubectl set env deployment/guardian-service LUKHAS_CANARY_PERCENT=100 ENFORCE_ETHICS_DSL=1

# Optional: Enable advanced evasion hardening
kubectl set env deployment/guardian-service LUKHAS_ADVANCED_TAGS=1

# Final flag snapshot
./guardian/flag_snapshot.sh > deployment_flags_t48.json
./guardian/ledger_snapshot.sh
```

---

## T+72h: Close-Out & Retro

### Final State Capture
```bash
echo "🏁 T+72h Close-Out"

# Tag final release
git tag -a safety-tags-v1-production -m "Safety Tags v1 Production Deployment Complete"
git push origin safety-tags-v1-production

# Archive dashboard screenshots
curl -s "https://grafana.lukhas.ai/render/d/guardian-safety-tags?width=1920&height=1080" > dashboard_final_t72.png

# Final flag snapshot
./guardian/flag_snapshot.sh > deployment_flags_final.json
./guardian/ledger_snapshot.sh
```

### Retrospective Template
```markdown
# Safety Tags v1 Deployment Retro

## Deployment Summary
- Duration: T+0h → T+72h
- Final State: ___% rollout, ENFORCE_ETHICS_DSL=___, LUKHAS_ADVANCED_TAGS=___
- Incidents: ___ total, ___ critical
- Decision Gates: T+24h: ____, T+48h: ____

## Metrics Achieved
- Max denial delta: ___% (target: ≤10%)
- Max P95 overhead: ___× (target: ≤1.05×)
- Average override latency: ___min (target: <5min)
- Uptime: ___% (target: >99.9%)

## What Went Well
1. ________________________________
2. ________________________________
3. ________________________________

## What to Tighten Next
1. ________________________________
2. ________________________________
3. ________________________________

## Action Items
- [ ] Update SLO thresholds based on observed performance
- [ ] Enhance monitoring for edge cases discovered
- [ ] Document lessons learned in runbook
- [ ] Schedule quarterly review of evasion patterns
```

---

## Quick Reference Commands

### Status Check (any time)
```bash
# Current deployment state
kubectl get deployment/guardian-service -o yaml | grep -A5 env:

# Flag snapshot
./guardian/flag_snapshot.sh

# Key metrics
curl -s localhost:9090/api/v1/query --data-urlencode 'query=up{job="guardian-service"}'
```

### Emergency Rollback
```bash
# Immediate rollback
kubectl set env deployment/guardian-service ENFORCE_ETHICS_DSL=0
touch /tmp/guardian_emergency_disable

# Full service rollback
kubectl rollout undo deployment/guardian-service
```

### Success Indicators
- ✅ Smoke tests pass at each gate
- ✅ Game-day drills successful every 8h
- ✅ Metrics within thresholds
- ✅ No critical incidents
- ✅ Team confidence maintained
- ✅ Flag snapshots recorded for audit

---
*Cadence: Tight, Boring, Effective | T4 Production Excellence*