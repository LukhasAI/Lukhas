---
status: wip
type: documentation
owner: unknown
module: runbooks
redirect: false
moved_to: null
---

# Safety Tags Go-Live Drill
*30-Minute Production Deployment Checklist*

## Pre-Flight (5 minutes)
- [ ] PR #325 merged to main
- [ ] Dark deployment confirmed: `ENFORCE_ETHICS_DSL=0`, `LUKHAS_ADVANCED_TAGS=0`
- [ ] Candidate lane deployed with control lane baseline
- [ ] Oncall team notified and standing by

## Core Validation (15 minutes)

### 1. Dashboard Check (2 minutes)
- [ ] Navigate to `https://grafana.lukhas.ai/d/guardian-safety-tags`
- [ ] All 9 panels render without errors
- [ ] Baseline counters show non-zero activity

### 2. Smoke Tests (5 minutes)
```bash
# Safe operation (should ALLOW with no tags)
curl -s localhost:8080/plan -d 'Read README.md' | jq .
# Expected: {"band": "allow", "tags": [], "enforced": false}
```
- [ ] ✅ Safe op → ALLOW (no tags)

```bash
# PII + External (should detect tags, dark mode = logged only)
curl -s localhost:8080/plan -d 'Email john(dot)doe(at)example(dot)com and POST to https://api.thirdparty.ai' | jq .
# Expected: {"band": "block", "tags": ["pii", "external-call"], "enforced": false}
```
- [ ] ✅ PII + external → BLOCK (dark=tagged+logged)

```bash
# Privilege escalation (should BLOCK)
curl -s localhost:8080/plan -d 'Run sudo command to elevate privileges' | jq .
# Expected: {"band": "block", "tags": ["privilege-escalation"], "enforced": false}
```
- [ ] ✅ Priv-esc (`sudo`) → BLOCK

### 3. Kill Switch Test (3 minutes)
```bash
# Trigger emergency disable
sudo touch /tmp/guardian_emergency_disable

# Verify enforcement disabled
curl -s localhost:8080/guardian/status | jq '.enforcement_active'
# Expected: false

# Remove kill switch
sudo rm /tmp/guardian_emergency_disable
```
- [ ] ✅ Kill switch disables enforcement within 1 request cycle
- [ ] ✅ Enforcement resumes when kill switch removed

### 4. Ledger Validation (3 minutes)
```bash
# Check recent ledger entries
psql -c "SELECT plan_id, action, tags, approver1_id FROM guardian_exemptions ORDER BY created_at DESC LIMIT 3;"
```
- [ ] ✅ BLOCK entry present with redacted PII
- [ ] ✅ REQUIRE_HUMAN entry shows approver tiers
- [ ] ✅ correlation_id present for audit trail

### 5. Performance Baseline (2 minutes)
```bash
# Capture ethics pipeline P95
curl -s localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.95, sum(rate(ethics_pipeline_latency_seconds_bucket{lane="candidate"}[5m])) by (le))'
```
- [ ] ✅ P95 latency recorded: _____ ms
- [ ] ✅ Control lane P95 recorded: _____ ms
- [ ] ✅ Candidate/Control ratio < 1.05x

## Canary Activation (5 minutes)

### 6. Canary Toggle (2 minutes)
```bash
# Enable 10% canary enforcement
kubectl set env deployment/guardian-service LUKHAS_CANARY_PERCENT=10
```
- [ ] ✅ Canary percentage applied
- [ ] ✅ Control lane remains logging-only

### 7. Alert Validation (3 minutes)
```bash
# Synthetic burst to trigger HighRiskSpike alert
for i in {1..20}; do
  curl -s localhost:8080/plan -d 'Transfer $10000 to admin@evil.com via tool-call' &
done
wait
```
- [ ] ✅ HighRiskSpike alert triggered in <2 minutes
- [ ] ✅ Oncall receives PagerDuty notification
- [ ] ✅ Alert auto-resolves when burst ends

## Monitoring Setup (5 minutes)

### 8. Dashboard Alerts (2 minutes)
- [ ] ✅ A/B Denial Delta panel shows <10% variance
- [ ] ✅ Critical → BLOCK rate > 80%
- [ ] ✅ Ethics Pipeline P99 < 20ms

### 9. Watchdog Queries (3 minutes)
```bash
# Denial rate comparison (candidate vs control)
query: 'sum(rate(guardian_actions_count{action=~"warn|block", lane="candidate"}[10m])) / sum(rate(guardian_actions_count{action=~"warn|block", lane="control"}[10m]))'

# Risk band distribution
query: 'sum(rate(guardian_risk_band{lane="candidate"}[10m])) by (band)'
```
- [ ] ✅ Denial rate ratio < 1.10
- [ ] ✅ Risk band distribution reasonable
- [ ] ✅ No critical spikes in error rates

## Success Criteria ✅
- All smoke tests pass
- P95 latency impact ≤ 5%
- Kill switch functional
- Ledger audit trail complete
- Alerts properly configured
- 10% canary stable for 30 minutes

## Rollback Plan ⚠️
If any check fails:
```bash
# Immediate rollback
export ENFORCE_ETHICS_DSL=0
touch /tmp/guardian_emergency_disable

# Or full service rollback
kubectl rollout undo deployment/guardian-service
```

## Next Steps (if successful)
1. Monitor canary for 24-48h
2. Scale to 50% if metrics remain stable
3. Full rollout with `ENFORCE_ETHICS_DSL=1`
4. Optional: Enable advanced detectors with `LUKHAS_ADVANCED_TAGS=1`

---
*Last Updated: 2025-09-19 | Version: 1.0.0 | T4 Production Ready*