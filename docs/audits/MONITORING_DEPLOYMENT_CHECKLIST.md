# Monitoring Deployment Checklist - GA Guard Pack
**Date**: 2025-10-14
**Version**: v0.9.0-rc
**Owner**: Claude (Observability/CI)

---

## Prometheus Recording Rules Deployment

### 1. Validate Rules Syntax

```bash
# Local validation
promtool check rules lukhas/observability/rules/guardian-rl.rules.yml
```

**Expected**: `SUCCESS: 6 groups, 20 rules`

### 2. Deploy to Prometheus Server

**Option A: Direct file copy (staging/production)**
```bash
# Copy to Prometheus rules directory
sudo cp lukhas/observability/rules/guardian-rl.rules.yml \
  /etc/prometheus/rules.d/lukhas-guardian-rl.yml

# Reload Prometheus config
sudo systemctl reload prometheus
# OR via HTTP API:
curl -X POST http://localhost:9090/-/reload
```

**Option B: ConfigMap update (Kubernetes)**
```bash
kubectl create configmap prometheus-lukhas-rules \
  --from-file=guardian-rl.rules.yml=lukhas/observability/rules/guardian-rl.rules.yml \
  --dry-run=client -o yaml | kubectl apply -f -

# Trigger Prometheus reload
kubectl rollout restart deployment prometheus-server
```

### 3. Verify Rules Loaded

Navigate to Prometheus UI: `http://localhost:9090/rules`

**Expected recording rules**:
- `guardian:pdp_latency:p95`
- `guardian:pdp_latency:p99`
- `guardian:pdp_latency:p50`
- `guardian:denial_rate:ratio`
- `guardian:denial_rate:by_scope`
- `guardian:denial_rate:by_route`
- `guardian:denials:top_reasons`
- `rl:near_exhaustion:ratio`
- `rl:hit_rate:ratio`
- `rl:hit_rate:by_principal`
- `rl:hit_rate:by_route`
- `guardian:rule_eval_freq:by_rule`
- `guardian:deny_rules:top_triggered`
- `rl:utilization:avg`
- `rl:utilization:max`
- `rl:utilization:by_route`
- `lukhas:guardian_rl:health_score`
- `lukhas:traffic:requests_per_sec`

### 4. Smoke Test Queries

```promql
# Check denial rate (should return value)
guardian:denial_rate:ratio

# Check PDP p95 latency (should return value < 0.010)
guardian:pdp_latency:p95

# Check health score (should return 0-1 range)
lukhas:guardian_rl:health_score
```

---

## Grafana Dashboard Deployment

### 1. Validate Dashboard JSON

```bash
# Check JSON syntax
jq . lukhas/observability/grafana/guardian-rl-dashboard.json > /dev/null
echo "✅ Dashboard JSON valid"
```

### 2. Deploy via Grafana API

**Prerequisites**:
- Grafana API key with Editor or Admin role
- Export as: `export GRAFANA_API_KEY="your-api-key"`
- Set Grafana URL: `export GRAFANA_URL="http://localhost:3000"`

**Deployment**:
```bash
# Import dashboard
curl -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @lukhas/observability/grafana/guardian-rl-dashboard.json

# Expected response: {"id": 123, "slug": "guardian-rl-health", "status": "success", ...}
```

### 3. Alternative: UI Upload

1. Navigate to Grafana: `http://localhost:3000`
2. Click **Dashboards** → **Import**
3. Upload `lukhas/observability/grafana/guardian-rl-dashboard.json`
4. Select Prometheus datasource
5. Click **Import**

### 4. Verify Dashboard

Navigate to: `http://localhost:3000/d/guardian-rl-health`

**Expected panels**:
- Guardian PDP Latency (p50/p95/p99)
- Denial Rate (overall & by scope)
- Top Denial Reasons
- Rate Limit Hit Rate
- Near-Exhaustion Ratio
- Utilization by Route
- Combined Health Score

---

## Health Artifacts Validation

### 1. System Health Audit Script

```bash
# Run health audit
python3 scripts/system_health_audit.py

# Expected outputs:
# - docs/audits/health/latest.json
# - docs/audits/health/latest.md
```

### 2. Verify Guardian Section

```bash
# Check for Guardian metrics in health report
jq '.guardian' docs/audits/health/latest.json

# Expected:
# {
#   "pdp_available": true,
#   "denial_rate_15m": 0.05,
#   "p95_latency_ms": 3.2,
#   "active_rules": 12,
#   "policy_version": "v1.2.0"
# }
```

### 3. Verify Rate Limiting Section

```bash
# Check for RL metrics in health report
jq '.rate_limiting' docs/audits/health/latest.json

# Expected:
# {
#   "backend": "redis",
#   "hit_rate_15m": 0.02,
#   "near_exhaustion_count": 3,
#   "p95_check_latency_ms": 1.5
# }
```

---

## CI/CD Integration Validation

### 1. PR Health Badge

**Check workflow file exists**:
```bash
ls .github/workflows/pr-health-badge.yml
```

**Trigger manually** (optional):
```bash
gh workflow run pr-health-badge.yml
```

**Verify badge appears** on next PR merge.

### 2. OpenAPI Headers Guard

```bash
# Run guard locally
make openapi-headers-guard

# Expected: ✅ All OpenAPI specs have required headers
```

### 3. Smoke Tests

```bash
# Run facade smoke
bash scripts/smoke_test_openai_facade.sh

# Expected: "All smoke tests passed! ✓"
```

---

## Post-Deployment Monitoring

### 1. Baseline Metrics (First 24h)

**Collect baseline data**:
```promql
# Average denial rate over 24h
avg_over_time(guardian:denial_rate:ratio[24h])

# P95 latency over 24h
avg_over_time(guardian:pdp_latency:p95[24h])

# RL hit rate over 24h
avg_over_time(rl:hit_rate:ratio[24h])
```

**Document in**: `docs/audits/BASELINE_METRICS_v0.9.0-rc.md`

### 2. Alert Preview (No-Page Mode)

**Guardian Denial Rate High** (warning only):
```yaml
alert: GuardianDenialRateHigh
expr: guardian:denial_rate:ratio > 0.15
for: 15m
labels:
  severity: warning
  component: guardian
annotations:
  summary: "Guardian denial rate {{ $value | humanizePercentage }} above 15% threshold"
```

**Rate Limit Near-Exhaustion** (warning only):
```yaml
alert: RateLimitNearExhaustion
expr: rl:near_exhaustion:ratio > 0.30
for: 10m
labels:
  severity: warning
  component: rate_limiting
annotations:
  summary: "{{ $value | humanizePercentage }} of principals near rate limit exhaustion"
```

**Add to**: `lukhas/observability/rules/guardian-rl.alerts.yml` (future PR)

---

## Rollback Procedure

If issues arise after deployment:

### 1. Remove Recording Rules

```bash
# Remove rules file
sudo rm /etc/prometheus/rules.d/lukhas-guardian-rl.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### 2. Archive Dashboard

In Grafana UI:
1. Navigate to Guardian/RL dashboard
2. Click **Dashboard settings** (gear icon)
3. Click **Delete dashboard**
4. Confirm

### 3. Revert Health Scripts

```bash
# Revert to previous version
git checkout HEAD~1 scripts/system_health_audit.py
```

---

## Completion Checklist

- [ ] Prometheus rules validated with `promtool`
- [ ] Rules deployed to Prometheus server
- [ ] All 18 recording rules visible in Prometheus UI
- [ ] Dashboard deployed to Grafana
- [ ] All dashboard panels render with data
- [ ] Health audit script generates Guardian/RL sections
- [ ] PR Health Badge workflow exists and runs
- [ ] OpenAPI headers guard passes
- [ ] Facade smoke tests pass
- [ ] Baseline metrics documented (24h soak)
- [ ] Alert definitions drafted (no-page mode)
- [ ] Rollback procedure tested (dry-run)

---

**Status**: 🟢 Ready for Deployment
**Next**: RC Soak Period (48-72h) → GA Promotion
