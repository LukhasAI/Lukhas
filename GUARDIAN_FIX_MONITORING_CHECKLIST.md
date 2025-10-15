# 🚀 Guardian Fix (#390) → Immediate Monitoring Deployment

**Owner**: Claude (Observability/CI)
**Trigger**: The moment #390 (or its PR) merges to `main`
**ETA**: ~20 minutes after merge

---

## Phase 1: Immediate Validation (2 min)

```bash
# 1. Pull latest and verify Guardian fix
git pull --ff-only

# 2. Quick smoke test (should pass now)
pytest tests/smoke/test_openai_facade.py::test_responses_minimal -v

# 3. Verify Guardian loads
python3 -c "
from lukhas.adapters.openai.policy_pdp import PolicyLoader
p = PolicyLoader.load_from_file('configs/policy/guardian_policies.yaml')
print(f'✅ Guardian loaded {len(p.rules)} rules')
"
```

---

## Phase 2: Run Deployment Script (5 min)

```bash
# Execute automated deployment
./scripts/deploy_monitoring_post_390.sh
```

**Script will**:
1. ✅ Update to latest main
2. ✅ Run health audit → verify Guardian section
3. ✅ Run OpenAPI headers guard
4. ✅ Run facade smoke tests
5. ✅ Extract Guardian metrics
6. ✅ Generate deployment summary

---

## Phase 3: Deploy Prometheus Rules (5 min)

### Option A: Direct Server Deploy
```bash
# Copy rules to Prometheus
sudo cp lukhas/observability/rules/guardian-rl.rules.yml \
  /etc/prometheus/rules.d/lukhas-guardian-rl.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### Option B: Kubernetes ConfigMap
```bash
kubectl create configmap prometheus-lukhas-rules \
  --from-file=guardian-rl.rules.yml=lukhas/observability/rules/guardian-rl.rules.yml \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment prometheus-server
```

### Verify Rules Loaded
Navigate to: `http://localhost:9090/rules`

Check for:
- `guardian:pdp_latency:p95`
- `guardian:denial_rate:ratio`
- `rl:hit_rate:ratio`
- `lukhas:guardian_rl:health_score`

---

## Phase 4: Deploy Grafana Dashboard (5 min)

### Via Grafana UI
1. Navigate to Grafana: `http://localhost:3000`
2. Click **Dashboards** → **Import**
3. Upload: `lukhas/observability/grafana/guardian-rl-dashboard.json`
4. Select Prometheus datasource
5. Click **Import**

### Via API (if configured)
```bash
curl -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @lukhas/observability/grafana/guardian-rl-dashboard.json
```

### Verify Dashboard
Navigate to: `http://localhost:3000/d/guardian-rl-health`

---

## Phase 5: Post Metrics Comment (3 min)

### 1. Get Current Metrics
```bash
# From health report
jq '.guardian' docs/audits/health/latest.json
jq '.rate_limiting' docs/audits/health/latest.json
```

### 2. Query Prometheus (if available)
```promql
# Denial rate (15m)
guardian:denial_rate:ratio[15m]

# PDP p95 latency
guardian:pdp_latency:p95

# Health score
lukhas:guardian_rl:health_score
```

### 3. Post Comment on #390
```markdown
## ✅ Guardian Monitoring Deployed

Following the fix, monitoring has been successfully deployed:

### 📊 Current Metrics (15m)
- **Guardian Denial Rate**: X.X% (target <15%)
- **PDP P95 Latency**: X.Xms (SLO <10ms)
- **Rate Limit Hit Rate**: X.X% (target <5%)
- **Health Score**: X.XX (0-1 scale)

### 🔗 Live Dashboards
- Prometheus: http://localhost:9090/graph?g0.expr=guardian%3Adenial_rate%3Aratio
- Grafana: http://localhost:3000/d/guardian-rl-health

### ✅ Validation
- [x] Guardian PDP initialized successfully
- [x] 18 recording rules active in Prometheus
- [x] Grafana dashboard rendering data
- [x] Health artifacts include Guardian/RL sections
- [x] Smoke tests passing (X/X)

🤖 Generated with Claude Code
```

---

## Phase 6: Update Runbook (2 min)

Edit: `docs/releases/POST_RELEASE_v0.9.0-rc_RUNBOOK.md`

Check these boxes:
- [ ] Prometheus recording rules deployed
- [ ] Grafana dashboard imported
- [ ] Guardian metrics visible
- [ ] Rate limiting metrics visible
- [ ] Health artifacts validated
- [ ] PR Health Badge workflow active
- [ ] Baseline metrics documented

---

## Quick Commands Reference

```bash
# All-in-one validation
git pull && ./scripts/deploy_monitoring_post_390.sh

# Quick Guardian check
python3 -c "from lukhas.adapters.openai.api import get_app; app = get_app(); print(f'Guardian PDP: {app.state.pdp}')"

# Facade smoke test
pytest tests/smoke/test_openai_facade.py -v

# Health audit
python3 scripts/system_health_audit.py && jq '.guardian' docs/audits/health/latest.json

# Check all metrics exist
curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data[]' | grep -E "guardian|lukhas_guardian|lukhas_ratelimit"
```

---

## Success Criteria

### Must Have ✅
- [ ] Guardian PDP initializes (not None)
- [ ] Smoke tests pass (especially auth tests)
- [ ] Health report has Guardian section
- [ ] At least 10 recording rules visible in Prometheus

### Should Have 🟡
- [ ] Grafana dashboard shows data (not empty panels)
- [ ] Denial rate metric < 15%
- [ ] PDP latency < 10ms
- [ ] Rate limit hit rate < 5%

### Nice to Have 🟢
- [ ] All 18 recording rules active
- [ ] Health score > 0.8
- [ ] PR Health Badge appears on next PR
- [ ] Alert previews configured (no-page mode)

---

## Troubleshooting

### If Guardian Still Fails
```bash
# Check policy syntax
python3 -c "
import yaml
with open('configs/policy/guardian_policies.yaml') as f:
    policy = yaml.safe_load(f)
    print('Rules:', [r.get('id') for r in policy.get('rules', [])])
"

# Check for import errors
python3 -c "
from lukhas.adapters.openai.policy_models import Rule
print('Rule fields:', Rule.__dataclass_fields__.keys())
"
```

### If Prometheus Rules Don't Load
```bash
# Validate syntax
promtool check rules lukhas/observability/rules/guardian-rl.rules.yml

# Check Prometheus logs
journalctl -u prometheus -n 50
```

### If Grafana Dashboard Empty
```bash
# Check datasource
curl http://localhost:3000/api/datasources

# Test query directly
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=guardian:denial_rate:ratio'
```

---

## Communication

### When Complete

1. **Comment on #390**: Post metrics + validation results
2. **Update PR #382**: Add metrics snapshot comment
3. **Slack/Discord** (if configured): "GA Guard Pack monitoring deployed ✅"
4. **Update TEAM_STATUS.md**: Mark monitoring deployment complete

### Metrics Links for Comments

```markdown
[Guardian Denial Rate](http://localhost:9090/graph?g0.expr=guardian%3Adenial_rate%3Aratio)
[PDP P95 Latency](http://localhost:9090/graph?g0.expr=guardian%3Apdp_latency%3Ap95)
[Health Score](http://localhost:9090/graph?g0.expr=lukhas%3Aguardian_rl%3Ahealth_score)
[Grafana Dashboard](http://localhost:3000/d/guardian-rl-health)
```

---

**Status**: 🟡 **READY** - Waiting for #390 merge trigger
**Owner**: Claude
**Time to Deploy**: ~20 minutes after merge

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>