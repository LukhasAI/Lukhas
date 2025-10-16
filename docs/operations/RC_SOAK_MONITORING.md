# RC Soak Test Monitoring Guide

**Status**: Active | **Version**: 0.9.0 | **Duration**: 6 hours

---

## 🎯 Objectives

Monitor Guardian PDP & Rate Limiting v0.9.0 stability under sustained load:

- **PDP latency p95**: < 10ms
- **Guardian denial rate**: < 1%
- **RL 429 rate**: Low & stable
- **No cascading failures**

---

## 🚀 Quick Start

### 1. **Start OpenAI Façade**

```bash
# Disable Guardian PDP for baseline testing
export LUKHAS_API_URL=http://localhost:8000
export LUKHAS_POLICY_PATH=/nonexistent

# Start façade
source .venv/bin/activate
uvicorn lukhas.adapters.openai.api:get_app --factory --host 0.0.0.0 --port 8000
```

### 2. **Baseline Health Check**

```bash
# Test authentication & rate limits
curl -s -H "Authorization: Bearer sk-lukhas-test-12345678" \
  http://localhost:8000/v1/models | jq '.'

# Expected response:
# {
#   "object": "list",
#   "data": [...]
# }
```

### 3. **Monitor Headers**

```bash
# Check OpenAI parity headers
curl -sI -H "Authorization: Bearer sk-lukhas-test-12345678" \
  http://localhost:8000/v1/models | grep -iE 'x-request-id|x-ratelimit'

# Expected headers:
# x-request-id: <trace-id>
# x-trace-id: <trace-id>
# x-ratelimit-limit-requests: 40
# x-ratelimit-remaining-requests: 39
# x-ratelimit-reset-requests: <epoch>
```

---

## 📊 Monitoring Workflow (6-Hour Soak)

### **Phase 1: Baseline (0-30 min)**

```bash
# Sustained load test (10 req/s)
for i in {1..1800}; do
  curl -s -H "Authorization: Bearer sk-lukhas-test-12345678" \
    http://localhost:8000/v1/models > /dev/null &
  sleep 0.1
done

# Monitor response times
time curl -s -H "Authorization: Bearer sk-lukhas-test-12345678" \
  http://localhost:8000/v1/models > /dev/null
```

**Success Criteria**:
- ✅ All requests 200 OK
- ✅ Response time < 100ms
- ✅ No 429 rate limit errors

### **Phase 2: Burst Load (30-90 min)**

```bash
# Burst test (50 req/s for 60s)
for i in {1..3000}; do
  curl -s -H "Authorization: Bearer sk-lukhas-test-12345678" \
    http://localhost:8000/v1/models > /dev/null &
  sleep 0.02
done
```

**Success Criteria**:
- ✅ Rate limiting triggers appropriately
- ✅ 429 responses include `Retry-After` header
- ✅ No cascading failures (500 errors)

### **Phase 3: Multi-Tenant Routing (90-180 min)**

```bash
# Test org/project header routing
curl -s -H "Authorization: Bearer sk-lukhas-test-12345678" \
  -H "OpenAI-Organization: org_test" \
  -H "OpenAI-Project: proj_test" \
  http://localhost:8000/v1/models | jq '.'
```

**Success Criteria**:
- ✅ Headers accepted
- ✅ No authentication errors
- ✅ Project ID threaded through to logs

### **Phase 4: Long-Term Stability (180-360 min)**

```bash
# Sustained low load (1 req/s)
for i in {1..10800}; do
  curl -s -H "Authorization: Bearer sk-lukhas-test-12345678" \
    http://localhost:8000/v1/models > /dev/null
  sleep 1
done
```

**Success Criteria**:
- ✅ No memory leaks (check with `ps aux | grep uvicorn`)
- ✅ Consistent response times
- ✅ No dropped connections

---

## 📈 Grafana Dashboard (Optional)

If Prometheus/Grafana are configured:

```bash
# Export Prometheus endpoint
export PROMETHEUS_URL=http://localhost:9090

# View Guardian PDP metrics
curl -s "${PROMETHEUS_URL}/api/v1/query?query=guardian_pdp_latency_p95" | jq '.'

# View rate limit metrics
curl -s "${PROMETHEUS_URL}/api/v1/query?query=rate_limit_429_total" | jq '.'
```

**Dashboard Panels**:
1. **PDP Latency** - Histogram with p50/p95/p99
2. **Guardian Denial Rate** - Counter divided by total requests
3. **Rate Limit 429s** - Counter over time
4. **Request Throughput** - Requests/second gauge

---

## 🎯 SLO Validation

After 6 hours, verify:

| Metric | Target | Pass/Fail |
|--------|--------|-----------|
| PDP latency p95 | < 10ms | ⏳ Pending |
| Guardian denial rate | < 1% | ⏳ Pending |
| RL 429 rate | Low & stable | ⏳ Pending |
| Zero 500 errors | Yes | ⏳ Pending |
| Memory stable | Yes | ⏳ Pending |

---

## 📸 Reporting

1. **Take Grafana screenshot** (if available)
2. **Post to PR #382** with summary:

```markdown
## RC Soak Results (6h)

**Status**: ✅ PASS / ❌ FAIL / ⚠️ DEGRADED

**Metrics**:
- PDP latency p95: X.Xms
- Guardian denial rate: X.X%
- RL 429 rate: X requests/min
- Total requests: X,XXX
- Errors: X (X%)

**Screenshot**: [link]

**Notes**: [Any observations]
```

---

## 🛑 Emergency Stop

```bash
# Kill façade if issues arise
pkill -f "uvicorn.*lukhas.adapters.openai"

# Check logs for errors
tail -100 /tmp/lukhas_facade_soak.log
```

---

**Last Updated**: 2025-10-16  
**Next Review**: After 6h soak completion  
**Related**: PR #382 (Guardian/RL v0.9.0), PR #406 (OpenAI parity)
