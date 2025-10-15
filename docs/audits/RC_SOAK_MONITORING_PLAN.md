# RC Soak Period Monitoring Plan — v0.9.0-rc

**Version**: v0.9.0-rc
**Duration**: 48-72 hours
**Start**: After Guardian YAML fix + monitoring deployment
**Owner**: Claude (Observability/CI)

---

## Overview

This document defines the monitoring strategy for the v0.9.0-rc soak period to validate Guardian PDP and Rate Limiting performance before GA promotion.

---

## Prerequisites (Must Complete First)

- [ ] Guardian YAML format fixed (#390)
- [ ] Prometheus recording rules deployed
- [ ] Grafana dashboard deployed
- [ ] Smoke tests passing
- [ ] Health artifacts validated
- [ ] PR Health Badge verified

---

## Phase 1: Baseline Collection (First 6 Hours)

### Metrics to Capture

#### Guardian PDP Performance
```promql
# P95 latency baseline
avg_over_time(guardian:pdp_latency:p95[6h])

# P99 latency baseline
avg_over_time(guardian:pdp_latency:p99[6h])

# P50 latency baseline
avg_over_time(guardian:pdp_latency:p50[6h])

# Decision rate (decisions/sec)
rate(lukhas_guardian_decision_total[6h])
```

**Expected Baselines**:
- P95 latency: <10ms (SLO target)
- P99 latency: <20ms
- P50 latency: <5ms
- Decision rate: 10-100 decisions/sec (depends on traffic)

---

#### Guardian Denial Rate
```promql
# Overall denial rate
avg_over_time(guardian:denial_rate:ratio[6h])

# Denial rate by scope
avg_over_time(guardian:denial_rate:by_scope[6h])

# Top denial reasons
topk(5, sum(rate(lukhas_guardian_denied_total[6h])) by (reason))
```

**Expected Baselines**:
- Overall denial rate: 5-15% (depends on policy strictness)
- Top reasons should align with policy intent

---

#### Rate Limiting
```promql
# Hit rate (429 rejections)
avg_over_time(rl:hit_rate:ratio[6h])

# Near-exhaustion ratio
avg_over_time(rl:near_exhaustion:ratio[6h])

# Utilization
avg_over_time(rl:utilization:avg[6h])
max_over_time(rl:utilization:max[6h])
```

**Expected Baselines**:
- Hit rate: <5% (healthy traffic pattern)
- Near-exhaustion: <30% of principals
- Avg utilization: 20-60%
- Max utilization: <90%

---

#### Combined Health Score
```promql
# Overall system health
avg_over_time(lukhas:guardian_rl:health_score[6h])
```

**Expected Baseline**: >0.85 (85% health score)

---

### Baseline Documentation

After 6 hours, document baselines in: `docs/audits/BASELINE_METRICS_v0.9.0-rc.md`

**Template**:
```markdown
# Baseline Metrics — v0.9.0-rc

**Collection Period**: [start] to [end] (6 hours)
**Traffic Volume**: [req/sec avg]

## Guardian PDP
- P50 latency: [value]ms
- P95 latency: [value]ms
- P99 latency: [value]ms
- Decision rate: [value] decisions/sec
- Denial rate: [value]%

## Rate Limiting
- Hit rate: [value]%
- Near-exhaustion: [value]%
- Avg utilization: [value]%
- Max utilization: [value]%

## Health Score
- Combined: [value] (0-1 scale)

## Notes
[Any anomalies or observations]
```

---

## Phase 2: Continuous Monitoring (24-72 Hours)

### Daily Health Checks

**Every 24 hours**, run:
```bash
# System health audit
python3 scripts/system_health_audit.py

# Check outputs
cat docs/audits/health/latest.md
jq . docs/audits/health/latest.json
```

**Verify**:
- [ ] Guardian section present with metrics
- [ ] RL section present with metrics
- [ ] Version stamp matches v0.9.0-rc
- [ ] No error indicators

---

### Prometheus Query Checklist

**Run these queries daily** via Prometheus UI or API:

```bash
# 1. PDP latency trend (should be stable)
guardian:pdp_latency:p95

# 2. Denial rate trend (should be consistent)
guardian:denial_rate:ratio

# 3. Rate limit hit rate (should be low)
rl:hit_rate:ratio

# 4. Near-exhaustion count (should be manageable)
count(
  lukhas_ratelimit_remaining_requests / lukhas_ratelimit_limit_requests < 0.2
)

# 5. Health score (should stay >0.8)
lukhas:guardian_rl:health_score

# 6. Traffic volume (for context)
rate(http_requests_total[5m])
```

---

### Grafana Dashboard Review

**Dashboard**: `http://localhost:3000/d/guardian-rl-health`

**Daily Review** (5 minutes):
1. Check all panels render with data
2. Verify no red zones in latency panels
3. Check denial rate trends (should be stable, not spiking)
4. Review top denial reasons (should align with policy)
5. Verify rate limit utilization is healthy (<80% avg)
6. Check health score stays green (>0.8)

**Screenshot** dashboard daily and save to: `docs/audits/grafana-snapshots/rc-day-[N].png`

---

## Phase 3: Alert Preview (No-Page Mode)

### Alert Definitions (Warning Only)

Create: `lukhas/observability/rules/guardian-rl.alerts.yml`

```yaml
groups:
  - name: guardian_pdp_alerts
    interval: 60s
    rules:
      # PDP latency degradation
      - alert: GuardianPDPLatencyHigh
        expr: guardian:pdp_latency:p95 > 0.010
        for: 15m
        labels:
          severity: warning
          component: guardian_pdp
        annotations:
          summary: "Guardian PDP p95 latency {{ $value | humanizeDuration }} exceeds 10ms SLO"
          description: "PDP is taking longer than expected to make decisions. Check for policy complexity or resource constraints."

      # Denial rate spike
      - alert: GuardianDenialRateHigh
        expr: guardian:denial_rate:ratio > 0.15
        for: 15m
        labels:
          severity: warning
          component: guardian_pdp
        annotations:
          summary: "Guardian denial rate {{ $value | humanizePercentage }} exceeds 15% threshold"
          description: "Check top denial reasons and verify policy is not overly restrictive."

  - name: rate_limiter_alerts
    interval: 60s
    rules:
      # Rate limit near-exhaustion
      - alert: RateLimitNearExhaustion
        expr: rl:near_exhaustion:ratio > 0.30
        for: 10m
        labels:
          severity: warning
          component: rate_limiting
        annotations:
          summary: "{{ $value | humanizePercentage }} of principals near rate limit exhaustion"
          description: "Many principals are close to hitting rate limits. Consider capacity adjustments."

      # High hit rate (many 429s)
      - alert: RateLimitHitRateHigh
        expr: rl:hit_rate:ratio > 0.10
        for: 15m
        labels:
          severity: warning
          component: rate_limiting
        annotations:
          summary: "Rate limit hit rate {{ $value | humanizePercentage }} exceeds 10%"
          description: "Many requests are being rate-limited. Review quota configuration."

  - name: combined_health_alerts
    interval: 120s
    rules:
      # Health score degradation
      - alert: GuardianRLHealthLow
        expr: lukhas:guardian_rl:health_score < 0.70
        for: 20m
        labels:
          severity: warning
          component: guardian_rl
        annotations:
          summary: "Guardian/RL combined health score {{ $value }} below 70%"
          description: "System health is degraded. Check PDP latency, denial rate, and RL hit rate."
```

**Deployment** (after baseline collection):
```bash
# Validate alerts
promtool check rules lukhas/observability/rules/guardian-rl.alerts.yml

# Deploy to Prometheus
sudo cp lukhas/observability/rules/guardian-rl.alerts.yml \
  /etc/prometheus/rules.d/lukhas-guardian-rl-alerts.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

**Verify** alerts are loaded:
- Navigate to: `http://localhost:9090/alerts`
- Should see 5 new alerts in "Inactive" state (no pages sent)

**Track firing history**:
```bash
# Check if any alerts fired
promtool query instant http://localhost:9090 'ALERTS{alertname=~"Guardian.*|RateLimit.*"}'
```

**Document**: Save alert firing history to `docs/audits/rc-alert-history.md`

---

## Phase 4: Performance Regression Detection

### Automated Daily Checks

**Script**: Create `scripts/rc_soak_health_check.sh`

```bash
#!/bin/bash
set -euo pipefail

DATE=$(date +%Y-%m-%d)
REPORT_DIR="docs/audits/rc-soak"
mkdir -p "$REPORT_DIR"

echo "📊 RC Soak Health Check - $DATE"

# 1. PDP latency check (must be <10ms p95)
P95=$(promtool query instant http://localhost:9090 'guardian:pdp_latency:p95' | awk '{print $2}')
if (( $(echo "$P95 > 0.010" | bc -l) )); then
  echo "⚠️  WARNING: PDP p95 latency ${P95}s exceeds 10ms SLO"
fi

# 2. Denial rate check (should be stable)
DENIAL_RATE=$(promtool query instant http://localhost:9090 'guardian:denial_rate:ratio' | awk '{print $2}')
echo "✓ Denial rate: $(echo "$DENIAL_RATE * 100" | bc)%"

# 3. RL hit rate check (should be <10%)
HIT_RATE=$(promtool query instant http://localhost:9090 'rl:hit_rate:ratio' | awk '{print $2}')
if (( $(echo "$HIT_RATE > 0.10" | bc -l) )); then
  echo "⚠️  WARNING: RL hit rate $(echo "$HIT_RATE * 100" | bc)% exceeds 10%"
fi

# 4. Health score check (must be >0.8)
HEALTH=$(promtool query instant http://localhost:9090 'lukhas:guardian_rl:health_score' | awk '{print $2}')
if (( $(echo "$HEALTH < 0.80" | bc -l) )); then
  echo "❌ FAIL: Health score $HEALTH below 80%"
  exit 1
fi

echo "✅ All checks passed"

# Save report
cat > "$REPORT_DIR/$DATE.md" <<EOF
# RC Soak Health - $DATE

**PDP p95 latency**: ${P95}s
**Denial rate**: $(echo "$DENIAL_RATE * 100" | bc)%
**RL hit rate**: $(echo "$HIT_RATE * 100" | bc)%
**Health score**: $HEALTH

**Status**: PASS
EOF
```

**Run daily**:
```bash
chmod +x scripts/rc_soak_health_check.sh
./scripts/rc_soak_health_check.sh
```

---

## Phase 5: Traffic Pattern Analysis

### Query Traffic Patterns

```promql
# 1. Peak traffic hours
max_over_time(lukhas:traffic:requests_per_sec[1h])

# 2. Traffic by endpoint
sum(rate(http_requests_total[1h])) by (handler)

# 3. PDP decisions by outcome
sum(rate(lukhas_guardian_decision_total[1h])) by (outcome)

# 4. RL hits by principal (top 10)
topk(10, sum(rate(lukhas_ratelimit_exceeded_total[1h])) by (principal))

# 5. Denial patterns by time of day
sum(rate(lukhas_guardian_denied_total[1h])) by (hour_of_day)
```

**Document patterns** in: `docs/audits/RC_TRAFFIC_PATTERNS_v0.9.0-rc.md`

---

## Success Criteria (Promote to GA)

### Must Pass All

- [ ] **Duration**: 48-72 hours continuous operation
- [ ] **PDP Latency**: P95 <10ms for 95% of time period
- [ ] **Denial Rate**: Stable (no unexplained spikes >2x baseline)
- [ ] **RL Hit Rate**: <10% average
- [ ] **Health Score**: >0.80 for 95% of time period
- [ ] **Alerts**: No critical alerts fired
- [ ] **Smoke Tests**: 100% pass rate (checked daily)
- [ ] **No Regressions**: No performance degradation vs. baseline

### Optional (Nice to Have)

- [ ] **Traffic Volume**: >1000 requests during soak period
- [ ] **Denial Diversity**: Top 5 denial reasons cover <80% (indicates policy coverage)
- [ ] **RL Principal Count**: >10 unique principals tested
- [ ] **Zero Downtime**: No restarts or service interruptions

---

## Go/No-Go Decision

**After 48-72 hours**, review all criteria.

### GO (Promote to GA)
If **all must-pass criteria** met:
1. Update version to `v0.9.0` (remove `-rc`)
2. Create GA release notes
3. Tag release: `git tag v0.9.0`
4. Deploy to production
5. Archive RC soak reports

### NO-GO (Extend Soak or Fix Issues)
If **any must-pass criteria** failed:
1. Document failure reasons
2. Create issues for remediation
3. Extend soak period OR
4. Rollback to previous stable version

---

## Rollback Plan

If critical issues arise during soak:

### Immediate Rollback (< 5 minutes)
```bash
# 1. Revert Prometheus rules
sudo rm /etc/prometheus/rules.d/lukhas-guardian-rl.yml
sudo rm /etc/prometheus/rules.d/lukhas-guardian-rl-alerts.yml
curl -X POST http://localhost:9090/-/reload

# 2. Revert Grafana dashboard
curl -X DELETE "${GRAFANA_URL}/api/dashboards/uid/guardian-rl-health" \
  -H "Authorization: Bearer ${GRAFANA_API_KEY}"

# 3. Revert to previous release
git checkout v0.8.3  # Previous stable
git push origin main --force  # ⚠️ Requires approval

# 4. Notify team
gh issue create --title "RC Rollback: v0.9.0-rc" \
  --body "Critical issue during soak period. Rolled back to v0.8.3."
```

### Post-Rollback
- [ ] Document root cause
- [ ] Create fix issues
- [ ] Schedule new RC after fixes
- [ ] Update team status

---

## Daily Checklist Template

**Copy to**: `docs/audits/rc-soak/YYYY-MM-DD-checklist.md`

```markdown
# RC Soak Daily Check — [DATE]

**Day**: [N] of soak period
**Reviewer**: [Name]

## Metrics Review
- [ ] PDP p95 latency: ___ms (target <10ms)
- [ ] Denial rate: ___%  (baseline: __%)
- [ ] RL hit rate: ___% (target <10%)
- [ ] Health score: ___ (target >0.8)
- [ ] Traffic volume: ___ req/sec

## Grafana Dashboard
- [ ] All panels rendering
- [ ] No red zones
- [ ] Screenshot saved

## Health Artifacts
- [ ] Ran system_health_audit.py
- [ ] Guardian section present
- [ ] RL section present
- [ ] No errors

## Alerts
- [ ] Checked /alerts page
- [ ] Alerts fired: [none / list]
- [ ] Alert history documented

## Smoke Tests
- [ ] Ran facade smoke tests
- [ ] All passing
- [ ] Auth working correctly

## Issues/Notes
[Any observations or concerns]

## Status
✅ PASS / ⚠️ WARNINGS / ❌ FAIL

---
Reviewer Signature: _______________
```

---

## Automation (Optional)

### Cron Job for Daily Checks

```cron
# Run health check daily at 9 AM
0 9 * * * cd /path/to/Lukhas && ./scripts/rc_soak_health_check.sh | mail -s "RC Soak Health - $(date +\%Y-\%m-\%d)" team@lukhas.ai
```

### Slack/Discord Notifications

**Webhook integration** for alert notifications:
```bash
# Add to alert annotations
webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

## Post-Soak Report Template

**File**: `docs/releases/RC_SOAK_REPORT_v0.9.0-rc.md`

```markdown
# RC Soak Period Report — v0.9.0-rc

**Duration**: [start] to [end] ([N] hours)
**Status**: ✅ PASS / ❌ FAIL

## Executive Summary
[1-2 sentences on overall health]

## Baseline Metrics
[Copy from BASELINE_METRICS_v0.9.0-rc.md]

## Soak Period Metrics
- **PDP p95 latency**: [avg] (SLO: <10ms)
- **Denial rate**: [avg]% (baseline: [X]%)
- **RL hit rate**: [avg]% (target: <10%)
- **Health score**: [avg] (target: >0.8)
- **Traffic volume**: [total requests]

## Alerts Fired
[List of alerts + timestamps]

## Issues Encountered
[List + resolutions]

## Regression Tests
[Any performance regressions noted]

## Go/No-Go Decision
✅ GO / ❌ NO-GO

**Justification**: [Why]

## Next Steps
[GA promotion OR remediation plan]

---
Reviewed by: _______________
Date: _______________
```

---

## Contact & Escalation

**Owner**: Claude (Observability/CI)
**Backup**: Codex (hot-path troubleshooting)

**Escalation**:
1. Check Grafana dashboard for visual indicators
2. Review `docs/audits/health/latest.md` for system status
3. Check alert firing history
4. If critical: engage rollback plan
5. Document in GitHub issue

---

**Status**: 📋 Ready to execute after Guardian YAML fix (#390)
**Next**: Deploy monitoring stack → start baseline collection
