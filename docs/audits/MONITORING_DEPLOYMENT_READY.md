# 🚨 Monitoring Deployment Ready - Waiting for Guardian Fix

**Status**: 🟡 **READY TO DEPLOY** (blocked on Guardian fix)
**Owner**: Claude (Observability/CI)
**Trigger**: Merge of #390 or any PR fixing Guardian YAML/PDP initialization

---

## Current Blocker

### Issue: Guardian PDP Initialization Fails

**Error**: `Failed to initialize Guardian PDP: local variable 'PDP' referenced before assignment`

**Root Cause**: Multiple issues:
1. **Import scope issue** in `lukhas/adapters/openai/api.py` (line 38-46)
2. **YAML normalization** puts everything in `conditions` instead of parsing properly:
   - `actions` array is empty (should parse from `when.action`)
   - `resources` array is empty (should parse from `when.resource`)
   - `subjects` dict is empty (should parse from `unless.subject`)

**Impact**:
- Guardian PDP never initializes → falls back to permissive mode
- Auth tests fail with 401
- No Guardian metrics generated
- Grafana panels empty

---

## ✅ What's Ready

### 1. Monitoring Artifacts
- **Prometheus Rules**: `lukhas/observability/rules/guardian-rl.rules.yml` (18 rules)
- **Grafana Dashboard**: `lukhas/observability/grafana/guardian-rl-dashboard.json`
- **Health Audit Integration**: Guardian + RL sections ready in health scripts

### 2. Deployment Automation
- **Script**: `./scripts/deploy_monitoring_post_390.sh` (fully automated)
- **Watch Script**: `./scripts/watch_for_guardian_fix.sh` (monitors for fix)
- **Checklist**: `GUARDIAN_FIX_MONITORING_CHECKLIST.md` (step-by-step guide)

### 3. Documentation
- **Deployment Guide**: `docs/audits/MONITORING_DEPLOYMENT_CHECKLIST.md`
- **Issue Analysis**: `docs/gonzo/issues/GUARDIAN_POLICY_YAML_FORMAT_MISMATCH.md`
- **Coordination Status**: `docs/gonzo/COORDINATION_UPDATE_2025-10-14.md`

---

## 🚀 One-Command Deployment

Once Guardian fix merges:

```bash
# Option 1: Automated deployment
git pull && ./scripts/deploy_monitoring_post_390.sh

# Option 2: Watch and auto-deploy
./scripts/watch_for_guardian_fix.sh  # Runs in background, auto-triggers on fix
```

---

## Quick Validation Commands

```bash
# Test if Guardian fixed (should load without errors)
python3 -c "from lukhas.adapters.openai.api import get_app; app = get_app(); print(f'Guardian: {app.state.pdp}')"

# Run smoke test (should pass when fixed)
python3 -m pytest tests/smoke/test_openai_facade.py::test_responses_minimal -xvs

# Check health report
python3 scripts/system_health_audit.py && jq '.guardian' docs/audits/health/latest.json
```

---

## Deployment Timeline (After Fix)

| Time | Action | Command |
|------|--------|---------|
| T+0 | Pull latest | `git pull --ff-only` |
| T+1m | Validate Guardian | `pytest tests/smoke/test_openai_facade.py -v` |
| T+2m | Run health audit | `python3 scripts/system_health_audit.py` |
| T+5m | Deploy Prometheus rules | `sudo cp lukhas/observability/rules/*.yml /etc/prometheus/rules.d/` |
| T+8m | Deploy Grafana dashboard | Upload via UI or API |
| T+10m | Verify metrics | Query Prometheus for `guardian:*` metrics |
| T+12m | Post GitHub comment | Metrics summary on #390 |
| T+15m | Update runbook | Check boxes in POST_RELEASE_v0.9.0-rc_RUNBOOK.md |
| T+20m | **Complete** ✅ | RC soak monitoring begins |

---

## Expected Metrics (Post-Deployment)

### Guardian PDP
- **Denial Rate**: 5-10% (normal range)
- **P95 Latency**: <5ms (well under 10ms SLO)
- **Active Rules**: 3-12 (depending on final YAML)
- **Policy Version**: v1.x.x

### Rate Limiting
- **Hit Rate**: <5% (normal operations)
- **Near-Exhaustion**: 0-5 principals
- **P95 Check Latency**: <2ms

### Health Score
- **Target**: >0.8 (combining Guardian + RL health)

---

## Communication Plan

### On Successful Deployment

1. **Comment on #390**:
```markdown
✅ Monitoring deployed successfully!
- Guardian PDP: Active (X rules loaded)
- Denial Rate: X.X%
- P95 Latency: X.Xms
- Dashboard: [Live Link](http://localhost:3000/d/guardian-rl-health)
```

2. **Update PR #382**:
```markdown
📊 Monitoring Live - 15m Baseline:
- Guardian Denial %: X.X%
- PDP P95: X.Xms
- [Prometheus](http://localhost:9090) | [Grafana](http://localhost:3000)
```

3. **Team Status Update**:
- Mark monitoring deployment complete in TEAM_STATUS.md
- Update phase to "RC Soak Monitoring"

---

## Contingency Plans

### If PDP Still Fails After Fix
1. Check for circular imports in policy_pdp.py
2. Verify Rule dataclass has all required fields with defaults
3. Test with minimal YAML (just one allow rule)
4. Fall back to permissive mode + document in known issues

### If Metrics Don't Appear
1. Check Prometheus scrape config includes lukhas endpoints
2. Verify metrics endpoint returns Guardian metrics
3. Check for metric name conflicts
4. Manually test recording rules with promtool

### If Dashboard Empty
1. Verify datasource connection
2. Check query time ranges
3. Test queries directly in Prometheus
4. Import dashboard with different UID if conflicts

---

## Final Checklist

### Pre-Deployment (Now)
- [x] Monitoring artifacts created
- [x] Deployment scripts ready
- [x] Documentation complete
- [x] Issue #390 documented
- [x] Team coordination updated

### Post-Fix Deployment (Waiting)
- [ ] Guardian PDP initializes
- [ ] Smoke tests pass
- [ ] Prometheus rules deployed
- [ ] Grafana dashboard imported
- [ ] Metrics visible
- [ ] GitHub comments posted
- [ ] Runbook updated

### RC Soak (48-72h)
- [ ] Baseline metrics collected
- [ ] Alert previews configured
- [ ] Performance SLOs met
- [ ] No critical issues

---

**Current Action**: 🔍 **MONITORING** for Guardian fix merge

**Next Action**: 🚀 **DEPLOY** immediately when fix detected

**ETA**: ~20 minutes after Guardian fix merges

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>