# 🛡️ v0.9.0-rc: Guardian Policy Enforcement + Rate-Limit Observability

> **Status**: Release Candidate
> **Focus**: Production-ready policy enforcement and OpenAI-compatible rate-limit headers
> **Testing**: 14/14 tests passing (Guardian PDP, RL headers, auth, health signals)

---

## 🎯 What's New

### Policy-Based Access Control
LUKHAS now enforces **attribute-based access control (ABAC)** across all OpenAI façade endpoints via Guardian PDP:

- ✅ **Deny-overrides algorithm** with sub-10ms latency target
- ✅ **Full context evaluation**: scopes, roles, resources, actions, IP, tenant
- ✅ **Graceful degradation**: permissive mode if PDP unavailable
- ✅ **Prometheus metrics**: decision counts, denials, latency histograms

Endpoints protected: `/v1/models`, `/v1/embeddings`, `/v1/responses`, `/v1/dreams`

### OpenAI-Compatible Rate-Limit Headers
All responses (success **and** error) now include:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1697123456
```

- ✅ Present on 200, 401, 403, 429, 500 responses
- ✅ Preserves OpenAI error envelope + `X-Trace-Id`
- ✅ CI-enforced via OpenAPI headers guard
- ✅ Works with Redis or in-memory backends

### Enhanced Health Endpoint
`/healthz` now exposes **operational signals** for dashboards and alerting:

```json
{
  "status": "ok",
  "checks": {
    "guardian_pdp": {
      "available": true,
      "decisions": 1247,
      "denials": 3,
      "policy_etag": "a3f9c8d1"
    },
    "rate_limiter": {
      "available": true,
      "backend": "redis",
      "keys_tracked": 42,
      "rate_limited": 8
    }
  }
}
```

---

## 📦 Installation & Upgrade

### Docker (Recommended)

```bash
docker pull lukhasai/lukhas:v0.9.0-rc
docker run -p 8000:8000 \
  -e LUKHAS_POLICY_MODE=permissive \
  -e REDIS_URL=redis://redis:6379/0 \
  lukhasai/lukhas:v0.9.0-rc
```

### From Source

```bash
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
git checkout v0.9.0-rc
pip install -e .
uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000
```

### Configuration

Create `.env` with optional overrides:

```bash
# Policy enforcement (default: permissive)
LUKHAS_POLICY_MODE=permissive

# Rate limiting (default: 10 RPS, 20 burst)
LUKHAS_RATE_RPS=10
LUKHAS_RATE_BURST=20

# Optional Redis backend (default: in-memory)
REDIS_URL=redis://localhost:6379/0
```

---

## 🧪 Verification

### Quick Smoke Test

```bash
# Check health signals
curl http://localhost:8000/healthz | jq '.checks | {guardian, rate_limiter}'

# Verify rate-limit headers
curl -i http://localhost:8000/v1/models \
  -H "Authorization: Bearer sk-test-token" \
  | grep -E "X-RateLimit|X-Trace-Id"

# Run full test suite
pytest tests/smoke/ -v
```

**Expected output**:
```
✅ 3/3 rate-limit header tests passing
✅ 3/3 healthz signal tests passing
✅ 8/8 Guardian PDP tests passing
```

### Integration Testing

```bash
# Test policy denial
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Authorization: Bearer sk-restricted-token" \
  -H "Content-Type: application/json" \
  -d '{"input": "test", "model": "lukhas-matriz"}'

# Should return 403 if policy denies:
# {
#   "error": {
#     "type": "forbidden",
#     "message": "Forbidden by policy: insufficient scope",
#     "code": "policy_denied"
#   }
# }
```

---

## 📊 Metrics & Monitoring

### New Prometheus Metrics

Add these panels to your Grafana dashboards:

```promql
# Guardian decision rate
rate(guardian_decision_total[5m])

# Denial percentage
rate(guardian_denied_total[5m]) / rate(guardian_decision_total[5m]) * 100

# PDP latency p95
histogram_quantile(0.95, rate(guardian_decision_latency_seconds_bucket[5m]))

# Rate-limit exhaustion
rate_limiter_remaining < 10
```

### Alerting Rules

```yaml
# High denial rate
- alert: HighPolicyDenialRate
  expr: rate(guardian_denied_total[5m]) > 1
  for: 5m
  annotations:
    summary: "High policy denial rate detected"

# Rate limit exhaustion
- alert: RateLimitExhaustion
  expr: rate_limiter_remaining < 10
  for: 3m
  annotations:
    summary: "Rate limit nearly exhausted"
```

---

## 🔧 Developer Tools

### New Makefile Targets

```bash
make redis-up              # Start local Redis for testing
make redis-down            # Stop local Redis
make redis-check           # Verify Redis connectivity
make openapi-spec          # Generate OpenAPI JSON with headers
make openapi-headers-guard # Validate RL headers in spec
```

### CI Integration

Add to your CI pipeline:

```yaml
- name: Validate OpenAPI headers
  run: |
    python3 scripts/generate_openapi.py
    python3 scripts/check_openapi_headers.py
```

---

## 🚨 Breaking Changes

**None** - this release is fully backward compatible:

- Rate-limit headers are **additive** (existing clients ignore unknown headers)
- Guardian policy enforcement defaults to **permissive mode** (logs but allows all)
- Health endpoint structure is **extended** (existing fields unchanged)

---

## 📚 Documentation

- **Full Changelog**: [CHANGELOG_v0.9.0-rc.md](docs/releases/CHANGELOG_v0.9.0-rc.md)
- **Guardian Setup Guide**: [docs/guardian/README.md](docs/guardian/README.md)
- **Rate Limiting Guide**: [docs/rate-limiting/README.md](docs/rate-limiting/README.md)
- **API Reference**: [docs/api/openai-facade.md](docs/api/openai-facade.md)

---

## 🐛 Known Issues

1. **Guardian PDP init warning**: If Redis unavailable, PDP falls back to permissive mode (tracked in #381)
2. **Rate-limit headers on embeddings**: Success-path headers are best-effort depending on backend availability

Report issues: https://github.com/LukhasAI/Lukhas/issues

---

## 👥 Contributors

Special thanks to:
- **Claude Code** for Guardian wiring, RL headers implementation, and comprehensive testing
- **LukhasAI Team** for architecture, policy definitions, and code review

This release includes contributions via:
- PR #380: Guardian Policy Enforcement + RL Headers
- 6 commits with T4-compliant messages
- 14/14 tests passing (100% success rate)

---

## 🔜 Next Steps

### Post-Release Tasks

1. **Tag Production Release**:
   ```bash
   git tag v0.9.0
   git push origin v0.9.0
   ```

2. **Deploy to Staging**:
   ```bash
   kubectl apply -f k8s/staging/deployment.yaml
   bash scripts/smoke_test_openai_facade.sh staging
   ```

3. **Monitor Key Metrics** (first 48h):
   - Guardian denial rate < 1%
   - PDP latency p95 < 10ms
   - Rate-limit exhaustion alerts

### Upcoming Features (v0.10.0)

- [ ] Guardian audit log persistence (PostgreSQL/S3)
- [ ] Dynamic quota adjustment via admin API
- [ ] Multi-tenancy isolation with per-tenant policies
- [ ] Redis Sentinel support for HA

---

**Installation Issues?** Check our [Troubleshooting Guide](docs/troubleshooting.md) or join our [Discord](https://discord.gg/lukhasai).

**Ready for Production?** See our [Production Deployment Checklist](docs/production-checklist.md).

---

🤖 *Release generated with [Claude Code](https://claude.com/claude-code)*
