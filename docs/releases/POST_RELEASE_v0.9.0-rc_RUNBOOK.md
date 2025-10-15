# v0.9.0-rc Post-Release Runbook

**Release**: v0.9.0-rc (Guardian Policy Enforcement + Rate-Limit Observability)
**Released**: 2025-10-13
**Status**: RC → GA in 48-72h

---

## 🚀 15-Minute RC Sanity Check (Do Now)

### 1. Boot Locally (Permissive Mode)

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
export LUKHAS_POLICY_MODE=permissive
uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000
```

### 2. Smoke Journey

```bash
bash scripts/smoke_test_openai_facade.sh
```

**Expected**: ✅ All smoke tests pass

### 3. Headers Guard + Spec Validation

```bash
make openapi-headers-guard

# Verify header definitions exist
python3 - <<'PY'
import json
spec = json.load(open("docs/openapi/lukhas-openapi.json"))
headers = sorted(spec.get("components", {}).get("headers", {}).keys())
print("OpenAPI Headers:", headers)
assert "X-RateLimit-Limit" in headers
assert "X-RateLimit-Remaining" in headers
assert "X-RateLimit-Reset" in headers
print("✅ All required headers present")
PY
```

### 4. Health Signals Quick Check

```bash
curl -s http://localhost:8000/healthz | jq '.checks | {guardian_pdp, rate_limiter}'
```

**Expected Output**:
```json
{
  "guardian_pdp": {
    "available": true,
    "decisions": 0,
    "denials": 0,
    "policy_etag": "a3f9c8d1"
  },
  "rate_limiter": {
    "available": true,
    "backend": "in-memory",
    "keys_tracked": 0,
    "rate_limited": 0
  }
}
```

✅ **Criteria**: X-RateLimit-* headers everywhere, X-Trace-Id present, Guardian & RL signals visible in /healthz

---

## 📊 24-Hour Staging Soak (Automated + Manual)

### Metrics to Watch (Prometheus)

#### Guardian Metrics

```promql
# Decision rate (should be > 0 if traffic flowing)
rate(guardian_decision_total[5m])

# Denial rate (alert if >1% for 10m)
100 * (rate(guardian_denied_total[5m]) / (rate(guardian_decision_total{effect="allow"}[5m]) + rate(guardian_decision_total{effect="deny"}[5m])))

# PDP latency p95 (target <10ms)
histogram_quantile(0.95, rate(guardian_decision_latency_seconds_bucket[5m]))
```

#### Rate-Limit Metrics

```promql
# Rate-limited requests
rate(rate_limit_exceeded_total[5m])

# Remaining quota
rate_limiter_remaining

# 429 responses
rate(http_server_requests_seconds_count{status="429"}[5m])
```

### Synthetic Checks

**200 Response Check**:
```bash
curl -i http://staging.lukhas.ai/v1/models \
  -H "Authorization: Bearer sk-staging-test" \
  | grep -E "X-RateLimit|X-Trace-Id"
```

**401 Error Check**:
```bash
curl -i http://staging.lukhas.ai/v1/models \
  | grep -E "X-RateLimit|X-Trace-Id"
```

**Health Endpoint Check**:
```bash
curl -s http://staging.lukhas.ai/healthz \
  | jq '.checks | {guardian_pdp, rate_limiter}' \
  | grep -E "policy_etag|keys_tracked|backend"
```

### Alert Validation

Deploy alert rules and verify they fire correctly:

```bash
# Deploy alerts to Prometheus
kubectl apply -f lukhas/observability/alerts/guardian-rl.alerts.yml

# Trigger test denial (403)
curl -X POST http://staging.lukhas.ai/v1/embeddings \
  -H "Authorization: Bearer sk-restricted-token" \
  -H "Content-Type: application/json" \
  -d '{"input": "test", "model": "lukhas-matriz"}'

# Check Alertmanager for HighGuardianDenialRate after 10m
```

---

## 👥 Team Assignments (Next 48h)

### Codex: Phase-B Lint + Auth Fixtures

**Objective**: Reduce Ruff diagnostics to ≤150 across `lukhas core MATRIZ`

```bash
# Current baseline
ruff check lukhas core MATRIZ --no-cache --output-format=concise | wc -l

# Target: ≤150 (currently ~250-300)
```

**Tasks**:
1. Converge on `pyproject.toml` only (remove local `ruff.toml` files)
2. Focus on prod lanes: `lukhas/`, `core/`, `MATRIZ/`
3. Reduce priority violations:
   - E402 (module level import not at top)
   - E701/E702 (multiple statements on one line)
   - E722 (bare except)
   - F401 (unused import)
   - F402 (import shadowing)
4. Ensure smoke/unit tests use `authz_headers` fixture from `tests/conftest.py`
5. Update CI: lower `ruff-phaseA` threshold to **≤250** diagnostics

**Deliverable**: PR reducing diagnostics by ≥100, all tests passing

---

### Claude Code: Ops Polish

**Objective**: Production-ready monitoring and health reporting

**Tasks**:

1. **Deploy Grafana Dashboard**:
   ```bash
   # Import dashboard JSON
   curl -X POST http://grafana:3000/api/dashboards/db \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $GRAFANA_API_KEY" \
     -d @lukhas/observability/grafana/guardian-rl-dashboard.json
   ```

2. **Deploy Prometheus Alerts**:
   ```bash
   # Copy to Prometheus config
   cp lukhas/observability/alerts/guardian-rl.alerts.yml \
      /etc/prometheus/rules/

   # Reload Prometheus
   curl -X POST http://localhost:9090/-/reload
   ```

3. **Wire /healthz Signals into Health Report**:
   - Update `scripts/report_health.py` (or equivalent) to include:
     - Guardian: `policy_etag`, `decisions`, `denials`
     - Rate-limiter: `backend`, `keys_tracked`, `rate_limited`
   - Generate both JSON and Markdown outputs
   - Add to CI artifact uploads

4. **Test Query Script**:
   ```bash
   # Set Prometheus URL
   export PROMETHEUS_URL=http://localhost:9090

   # Query denial rate
   ./scripts/query_guardian_deny_rate.sh

   # Expected: ✅ OK: Denial rate within acceptable range (<1%)
   ```

**Deliverable**: Dashboards live, alerts deployed, health report includes Guardian/RL sections

---

### Jules: Guardian/Redis Integration

**Objective**: Exercise Redis backend and quota resolver

**Tasks**:

1. **Validate Remaining Write Endpoints**:
   ```bash
   # Check for endpoints missing enforce_policy()
   rg "def (post|put|patch|delete)" lukhas/adapters/openai/api.py \
     | grep -v "enforce_policy"
   ```

   If any found, add `Depends(enforce_policy("scope"))` wiring

2. **Redis Rate-Limit Path Testing**:
   ```bash
   # Start Redis
   make redis-up

   # Configure Redis backend
   export REDIS_URL=redis://localhost:6379/0
   export LUKHAS_RATE_BACKEND=redis

   # Burst test
   for i in {1..25}; do
     curl -s http://localhost:8000/v1/models \
       -H "Authorization: Bearer sk-burst-test" \
       -o /dev/null -w "%{http_code}\n"
   done

   # Expected: 200 x20, then 429 x5
   ```

3. **Quota Resolver → Limiter Linkage**:
   - Implement per-route quota multipliers from `configs/quotas.yaml`
   - Example: `/v1/embeddings` gets 2x burst, `/v1/responses` gets 0.5x
   - Wire into `RateLimiter` via route-based key resolution

4. **End-to-End Tests** (one per endpoint):
   ```python
   # tests/e2e/test_redis_rate_limit.py
   def test_embeddings_redis_rate_limit():
       """Verify /v1/embeddings respects Redis rate limits."""
       # Configure Redis backend
       # Make burst + 1 requests
       # Assert 429 on overflow
       # Verify X-RateLimit-Remaining decrements
   ```

**Deliverable**: Redis path validated, quota resolver wired, 4 E2E tests added

---

### Copilot: DX (Documentation)

**Objective**: 30-second quickstart for developers

**Tasks**:

1. **Update Root README** ([README.md](../../README.md)):

   Add section after installation:

   ```markdown
   ## 🚀 Quick Start (30 seconds)

   ### Start the API Server

   \`\`\`bash
   uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000
   \`\`\`

   ### Test Embeddings Endpoint

   \`\`\`bash
   curl -X POST http://localhost:8000/v1/embeddings \
     -H "Authorization: Bearer sk-test-token" \
     -H "Content-Type: application/json" \
     -d '{"input": "Hello, LUKHAS!", "model": "lukhas-matriz"}'
   \`\`\`

   ### Check Rate-Limit Headers

   \`\`\`bash
   curl -i http://localhost:8000/v1/models \
     -H "Authorization: Bearer sk-test-token" \
     | grep X-RateLimit
   \`\`\`

   **Response includes**:
   - `X-RateLimit-Limit`: Max requests per window
   - `X-RateLimit-Remaining`: Requests remaining
   - `X-RateLimit-Reset`: Window reset time (epoch seconds)
   - `X-Trace-Id`: Correlation ID for debugging

   See [API Documentation](docs/api/openai-facade.md) for full reference.
   \`\`\`

2. **SDK Usage Snippets** (add to [docs/api/openai-facade.md](../../docs/api/openai-facade.md)):

   ```python
   # Python SDK with X-Trace-Id correlation
   import httpx

   response = httpx.post(
       "http://localhost:8000/v1/embeddings",
       headers={"Authorization": "Bearer sk-test-token"},
       json={"input": "test", "model": "lukhas-matriz"}
   )

   # Extract rate-limit headers
   limit = response.headers.get("X-RateLimit-Limit")
   remaining = response.headers.get("X-RateLimit-Remaining")
   reset = response.headers.get("X-RateLimit-Reset")
   trace_id = response.headers.get("X-Trace-Id")

   print(f"Quota: {remaining}/{limit}, Reset: {reset}, Trace: {trace_id}")
   ```

3. **Migration Guide** (add to CHANGELOG):

   Link from release notes to [docs/migrations/v0.9.0.md](../../docs/migrations/v0.9.0.md) with:
   - Breaking changes (none)
   - New headers behavior
   - Guardian permissive → strict mode migration
   - Redis backend setup guide

**Deliverable**: README updated with quickstart, SDK snippets published, migration guide complete

---

## ✅ GA Readiness Gates

Before promoting v0.9.0-rc → v0.9.0 (GA), verify:

- [x] **CI**: compat-enforce=0, openapi-headers-guard passing
- [x] **Smoke**: >95% pass with `LUKHAS_POLICY_MODE=permissive`
- [ ] **Ruff**: ≤150 diagnostics on prod lanes (`lukhas core MATRIZ`)
- [ ] **Ops**: Grafana dashboards deployed, Prometheus alerts firing correctly
- [ ] **Docs**: README quickstart live, migration guide linked in release notes
- [ ] **24h Soak**: No critical alerts, denial rate <1%, p95 latency <10ms
- [ ] **Redis**: Failover tested, quota resolver validated

**Approval**: Requires sign-off from Platform + Security teams

---

## 🚨 Known Risks & Mitigations

### Risk 1: Scope Enforcement Too Strict

**Symptom**: 403 responses in staging due to missing scopes

**Mitigation**:
- Tests use `authz_headers` fixture with default scopes
- Permissive mode logs denials without blocking
- Rollback: `export LUKHAS_POLICY_MODE=permissive`

### Risk 2: Redis Backend Instability

**Symptom**: Rate limiter falls back to in-memory (not distributed)

**Mitigation**:
- Graceful fallback already implemented
- Monitor `rate_limiter_backend_healthy` metric
- Alert fires if Redis down >2m

### Risk 3: OpenAPI Spec Drift

**Symptom**: Headers missing from generated spec

**Mitigation**:
- CI guard script (`openapi-headers-guard`) prevents merges
- OpenAPI diff workflow flags breaking changes
- Manual verification in 15-min sanity check

---

## 🔄 Quick Rollback Procedure

If staging becomes unstable:

### Option 1: Revert Squash Merge

```bash
# Find merge commit SHA
git log --oneline --grep="guardian" -n 5

# Revert (replace <sha> with merge commit)
git revert <sha> -m 1
git push origin main
```

### Option 2: Toggle to Permissive Mode

```bash
# Set environment variable (no code change)
export LUKHAS_POLICY_MODE=permissive

# Restart service
kubectl rollout restart deployment/lukhas-openai-facade
```

### Option 3: Feature Flag (if implemented)

```bash
# Disable Guardian enforcement via LaunchDarkly/Split
curl -X PATCH https://api.launchdarkly.com/flags/guardian-enforcement \
  -H "Authorization: $LD_API_KEY" \
  -d '{"enabled": false}'
```

---

## 📞 Contacts & Escalation

- **Platform Team**: @codex, @claude-code
- **Security Team**: @jules (Guardian policies)
- **On-Call**: PagerDuty rotation (use runbook links in alerts)
- **Slack**: #lukhas-releases, #lukhas-incidents

---

## 📈 Success Metrics (48h post-release)

**Availability**:
- Uptime: >99.9%
- p95 latency: <500ms (API), <10ms (Guardian PDP)

**Security**:
- Guardian denial rate: <1%
- No policy load failures
- Zero unauthorized access (401/403 logged correctly)

**Rate-Limiting**:
- 429 responses: <0.1% of requests
- X-RateLimit-* headers: present on 100% of responses
- Redis backend: 100% uptime

**Developer Experience**:
- Smoke tests: 100% passing
- CI gates: 0 false positives
- Documentation: quickstart tested by 3+ users

---

**Next Review**: 2025-10-15 (48h post-release)
**GA Promotion Target**: 2025-10-16 (pending gates)
