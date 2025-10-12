# LUKHAS Reliability Tuning Guide

**Status**: Production-Ready | **Last Updated**: 2025-01-08 | **Owner**: Platform Team

---

## Overview

This guide provides comprehensive guidance for tuning LUKHAS reliability parameters defined in `configs/runtime/reliability.yaml`. Proper configuration ensures:

- **Resilience**: Graceful handling of transient failures
- **Performance**: Optimal throughput within SLO constraints
- **Stability**: Prevention of cascading failures and resource exhaustion

**Prerequisites**:
- Understanding of LUKHAS architecture (see `README.md`)
- Familiarity with HTTP status codes and retry strategies
- Access to monitoring/observability tools (Grafana dashboards)

---

## Configuration File Structure

### File Location

```
configs/runtime/reliability.yaml
```

**Note**: Changes require system restart. Always test in staging first!

### Core Sections

1. **Timeouts** - Connection and request timeout thresholds
2. **Backoff** - Exponential backoff parameters for retries
3. **Rate Limits** - Per-endpoint RPS (requests per second) caps

---

## Timeout Configuration

### Connection Timeout (`connect_ms`)

**Purpose**: Maximum time to establish TCP connection to downstream services.

**Default**: `1000ms` (1 second)

#### Tuning Guidelines

| Environment | Recommended Value | Rationale |
|-------------|-------------------|-----------|
| **Local Development** | 500-1000ms | Fast local network |
| **Internal Network** | 1000-2000ms | Low-latency datacenter network |
| **Cloud/External** | 2000-3000ms | Higher latency, potential cross-region |
| **Edge Computing** | 500-1500ms | Optimized for edge proximity |

#### Symptoms & Fixes

**Symptom**: Frequent `ConnectionTimeout` errors in logs  
**Diagnosis**: Network latency higher than threshold  
**Fix**: Increase `connect_ms` by 50-100% increments  
**Validation**: Monitor connection success rate in Grafana

**Symptom**: Slow request initiation, users seeing delays  
**Diagnosis**: Timeout too high, hangs waiting for dead connections  
**Fix**: Decrease `connect_ms`, ensure DNS resolution is fast  
**Validation**: Check p95 time-to-first-byte metric

---

### Read Timeout (`read_ms`)

**Purpose**: Maximum time to wait for complete HTTP response after connection established.

**Default**: `10000ms` (10 seconds)

#### Operation-Specific Requirements

| Operation | Target Latency | Recommended Min `read_ms` |
|-----------|----------------|---------------------------|
| **Consciousness Stream** | <250ms | 500ms (2× SLO buffer) |
| **Memory Orchestration** | <500ms | 1000ms (2× SLO buffer) |
| **Quantum Processing** | <1000ms | 2000ms (2× SLO buffer) |
| **Large Embeddings** | <2000ms | 5000ms (2.5× buffer) |
| **Multi-Turn Chat** | <5000ms | 10000ms (2× buffer) |

**Rule of Thumb**: `read_ms ≥ 2 × expected_latency` to account for variance.

#### Tuning Guidelines

```yaml
# Conservative (high reliability, slower fail-fast)
timeouts:
  read_ms: 15000  # 15 seconds

# Balanced (default)
timeouts:
  read_ms: 10000  # 10 seconds

# Aggressive (fast fail-fast, assumes low latency)
timeouts:
  read_ms: 5000   # 5 seconds
```

#### Symptoms & Fixes

**Symptom**: `ReadTimeout` errors for complex operations  
**Diagnosis**: Operations exceeding timeout threshold  
**Fix**: Increase `read_ms` OR optimize operation latency  
**Validation**: Check p95/p99 latency in load testing

**Symptom**: Requests hang indefinitely before failing  
**Diagnosis**: Timeout too high, masking backend issues  
**Fix**: Decrease `read_ms`, improve backend monitoring  
**Validation**: Test with `make load-smoke` to verify error handling

---

## Exponential Backoff Configuration

### Overview

Exponential backoff prevents thundering herd problems by gradually increasing wait time between retries.

**Formula**:
```
wait_time = base_s × (factor ^ attempt) ± (jitter × base_s)
```

### Parameters

#### Base Delay (`base_s`)

**Purpose**: Initial retry delay in seconds.

**Default**: `0.1s` (100ms)

**Tuning**:
```yaml
# Real-time applications (fast fail)
backoff:
  base_s: 0.05  # 50ms initial delay

# Standard applications (balanced)
backoff:
  base_s: 0.1   # 100ms initial delay

# Batch/background jobs (patient retry)
backoff:
  base_s: 0.5   # 500ms initial delay
```

#### Factor (`factor`)

**Purpose**: Multiplier for each subsequent retry attempt.

**Default**: `2.0` (doubles each retry)

**Standard Practice**: Keep at `2.0` for exponential growth. Other values:
- `1.5` - Slower growth, more retries in same time window
- `3.0` - Faster growth, aggressive backoff (rare use case)

**Retry Timeline Examples**:

```
factor=2.0, base=0.1s:
  Attempt 1: 100ms
  Attempt 2: 200ms
  Attempt 3: 400ms
  Attempt 4: 800ms
  Attempt 5: 1600ms
  Total: ~3.1 seconds

factor=1.5, base=0.1s:
  Attempt 1: 100ms
  Attempt 2: 150ms
  Attempt 3: 225ms
  Attempt 4: 337ms
  Attempt 5: 506ms
  Total: ~1.3 seconds
```

#### Jitter (`jitter`)

**Purpose**: Adds randomness to prevent synchronized retries.

**Default**: `0.1` (±10% random variance)

**Example with jitter=0.1**:
```
base=0.1s, jitter=0.1:
  Calculated delay: 100ms
  Actual delay: 90-110ms (random)
```

**Tuning**:
- `0.0` - No jitter (NOT RECOMMENDED, thundering herd risk)
- `0.1` - Standard jitter (10% variance)
- `0.2` - Higher jitter (20% variance, better for high-concurrency)

---

## Rate Limiting Configuration

### Purpose

Prevent service degradation by capping requests per second (RPS) per endpoint.

### Enforcement Behavior

When rate limit exceeded:
1. Returns `HTTP 429 Too Many Requests`
2. Includes `Retry-After` header (seconds to wait)
3. Tracked per API key for multi-tenant isolation

### Responses Endpoint (`responses_rps`)

**Endpoint**: `/v1/responses` (consciousness stream generation)

**Default**: `20 RPS` per API key

**Characteristics**:
- CPU-intensive (consciousness processing)
- Memory-intensive (symbolic reasoning)
- Target latency: <250ms (p95)

#### Capacity Planning

| Server Specs | Recommended RPS | Notes |
|--------------|-----------------|-------|
| **2 cores, 4GB RAM** | 5-10 RPS | Development/testing only |
| **4 cores, 8GB RAM** | 10-20 RPS | Small production |
| **8 cores, 16GB RAM** | 30-50 RPS | Standard production |
| **16+ cores, 32GB+ RAM** | 50-100 RPS | High-traffic production |

#### Tuning Process

1. **Baseline Load Test**:
   ```bash
   make load-smoke  # 5 VUs, 30s
   ```
   Monitor: p95 latency, CPU %, memory %

2. **Gradual Increase**:
   ```yaml
   rate_limits:
     responses_rps: 30  # +50% increase
   ```

3. **Stress Test**:
   ```bash
   make load-test  # 50 VUs, 2m
   ```

4. **Validation**:
   - p95 latency < 250ms ✓
   - CPU < 80% ✓
   - Memory stable ✓
   - Error rate < 1% ✓

5. **Repeat** until resource saturation

#### Symptoms & Fixes

**Symptom**: Frequent 429 errors, users rate-limited  
**Diagnosis**: RPS limit too low for traffic  
**Fix**: Increase `responses_rps` by 25-50%  
**Validation**: Monitor 429 rate, should drop to <0.1%

**Symptom**: p95 latency increasing, CPU saturation  
**Diagnosis**: RPS limit too high, system overloaded  
**Fix**: Decrease `responses_rps` by 20-30%  
**Validation**: Latency returns to SLO (<250ms)

---

### Embeddings Endpoint (`embeddings_rps`)

**Endpoint**: `/v1/embeddings` (vector embeddings generation)

**Default**: `50 RPS` per API key

**Characteristics**:
- Memory-intensive (vector operations)
- Typically faster than consciousness streams
- Target latency: <500ms (p95)

#### Capacity Planning

| Server Specs | Recommended RPS | Notes |
|--------------|-----------------|-------|
| **CPU-only** | 30-50 RPS | Standard processing |
| **GPU-accelerated** | 100-200 RPS | Batch optimized |
| **TPU-accelerated** | 200-500 RPS | High-throughput |

#### Tuning Guidelines

```yaml
# CPU-only deployment
rate_limits:
  embeddings_rps: 50

# GPU deployment (e.g., NVIDIA T4)
rate_limits:
  embeddings_rps: 150

# TPU deployment (e.g., Cloud TPU v4)
rate_limits:
  embeddings_rps: 300
```

---

## Load Testing Workflows

### Pre-Tuning Baseline

```bash
# 1. Start LUKHAS in dev mode
make dev

# 2. Run smoke test (quick validation)
make load-smoke

# 3. Analyze results
cat load/results/*.json | jq '.metrics.http_req_duration'
```

Expected baseline:
- **p50**: 80-120ms
- **p95**: 200-300ms
- **p99**: 400-600ms
- **Error rate**: <0.5%

### Post-Tuning Validation

```bash
# 1. Apply config changes
vim configs/runtime/reliability.yaml

# 2. Restart server
make dev

# 3. Run extended test
make load-extended  # 10m, ramping to 100 VUs

# 4. Check for degradation
# - p95 should remain <500ms
# - Memory should stabilize (no leaks)
# - Error rate should stay <1%
```

### Stress Testing (Find Limits)

```bash
# Run spike test (sudden load)
make load-spike  # 0 → 200 → 0 VUs

# Observations:
# - System recovers after spike? ✓
# - 429 rate limiting activates? ✓
# - No crashes or OOM kills? ✓
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Load test in staging with production-like traffic
- [ ] Validate all SLOs met (p95 latency targets)
- [ ] Verify rate limits prevent resource exhaustion
- [ ] Test graceful degradation under 429 responses
- [ ] Document baseline metrics for comparison

### Configuration Template

```yaml
# Production-Ready Configuration (8 cores, 16GB RAM)
timeouts:
  connect_ms: 2000      # Allow higher cloud latency
  read_ms: 10000        # Standard for complex operations

backoff:
  base_s: 0.1           # Standard exponential backoff
  factor: 2.0
  jitter: 0.1

rate_limits:
  responses_rps: 40     # Conservative for stable service
  embeddings_rps: 80    # 2× responses (embeddings faster)
```

### Monitoring & Alerting

**Key Metrics**:
1. **p95 Latency** (consciousness streams): Alert if >300ms
2. **Error Rate**: Alert if >1%
3. **429 Rate**: Alert if >5% (rate limits too aggressive)
4. **CPU Utilization**: Alert if >85% sustained
5. **Memory Usage**: Alert if >90%

**Grafana Dashboard Queries**:
```promql
# p95 latency (consciousness streams)
histogram_quantile(0.95, http_request_duration_seconds_bucket{endpoint="/v1/responses"})

# 429 rate
rate(http_requests_total{status="429"}[5m]) / rate(http_requests_total[5m])

# CPU utilization
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

---

## Troubleshooting Common Issues

### Issue: High 429 Rate

**Symptoms**:
- Users frequently rate-limited
- `Retry-After` headers in responses
- Client retries causing more 429s

**Root Causes**:
1. Rate limits too low for traffic
2. Single user/key causing burst traffic
3. Client not respecting `Retry-After` header

**Solutions**:
```yaml
# Option 1: Increase rate limits
rate_limits:
  responses_rps: 60  # +50% increase

# Option 2: Implement per-user quotas (application-level)
# Option 3: Add burst allowance (future feature)
```

**Validation**:
```bash
# Monitor 429 rate over time
watch -n 5 'curl -s http://localhost:8000/metrics | grep http_requests_total'
```

---

### Issue: Timeout Errors Under Load

**Symptoms**:
- `ReadTimeout` exceptions in logs
- p95/p99 latency exceeding timeout
- Intermittent failures under high traffic

**Root Causes**:
1. Backend operations slower than expected
2. Resource contention (CPU/memory)
3. Timeout values too aggressive

**Solutions**:
```yaml
# Immediate: Increase timeouts
timeouts:
  read_ms: 15000  # +50% buffer

# Long-term: Optimize backend operations
# - Profile slow endpoints
# - Add caching where appropriate
# - Scale horizontally (add instances)
```

**Debugging**:
```bash
# Check slow requests
grep "ReadTimeout" logs/lukhas.log | tail -20

# Profile with load test
make load-extended
# Review percentile distribution in k6 output
```

---

### Issue: Memory Exhaustion

**Symptoms**:
- OOM (Out of Memory) kills
- Swap usage increasing
- p95 latency degrading over time (GC pressure)

**Root Causes**:
1. Rate limits too high for available memory
2. Memory leak in application code
3. Insufficient connection pooling

**Solutions**:
```yaml
# Immediate: Reduce rate limits
rate_limits:
  responses_rps: 20   # Reduce by 30-50%
  embeddings_rps: 40

# Enable connection pooling (if not already)
connection_pool:
  max_connections: 50  # Prevent unlimited connections
  max_keepalive_ms: 10000
```

**Monitoring**:
```bash
# Watch memory usage during load test
while true; do
  ps aux | grep python | awk '{print $4}' | head -1
  sleep 5
done
```

---

### Issue: Cascading Failures

**Symptoms**:
- Single failure causing widespread errors
- Recovery takes minutes after issue resolved
- Retry storms overwhelming downstream services

**Root Causes**:
1. No circuit breaker enabled
2. Retry logic too aggressive (no backoff jitter)
3. All clients retry simultaneously

**Solutions**:
```yaml
# Enable circuit breaker (future feature)
circuit_breaker:
  failure_threshold: 5
  recovery_timeout_s: 30
  half_open_requests: 3

# Ensure jitter is enabled
backoff:
  jitter: 0.2  # Increase jitter to 20%
```

**Validation**:
```bash
# Simulate downstream failure
# Kill dependency, observe graceful degradation
# Expect: 503 errors, then circuit open, then recovery
```

---

## Advanced Topics

### Multi-Tenant Rate Limiting

**Scenario**: Different API keys need different rate limits.

**Solution** (application-level):
```python
# lukhas/api/middleware/rate_limit.py
rate_limits = {
    "free-tier": {"responses_rps": 5, "embeddings_rps": 10},
    "pro-tier": {"responses_rps": 50, "embeddings_rps": 100},
    "enterprise": {"responses_rps": 200, "embeddings_rps": 500},
}
```

**Configuration** (future YAML support):
```yaml
rate_limits:
  tiers:
    free:
      responses_rps: 5
      embeddings_rps: 10
    pro:
      responses_rps: 50
      embeddings_rps: 100
    enterprise:
      responses_rps: 200
      embeddings_rps: 500
```

---

### Dynamic Configuration Reloading

**Current**: Requires restart after config changes.

**Future Feature**: Hot reload via signal.

```bash
# Send SIGHUP to reload config
kill -HUP $(cat lukhas.pid)
```

**Planned Implementation**:
- Watch `configs/runtime/reliability.yaml` for changes
- Validate new config before applying
- Reload without dropping connections

---

### Geographic Distribution

**Scenario**: Multi-region deployment with varying latencies.

**Regional Configs**:
```yaml
# us-east-1 (low latency)
timeouts:
  connect_ms: 1000
  read_ms: 8000

# eu-west-1 (moderate latency)
timeouts:
  connect_ms: 2000
  read_ms: 12000

# ap-southeast-1 (higher latency)
timeouts:
  connect_ms: 3000
  read_ms: 15000
```

**Deployment**:
```bash
# Deploy region-specific configs
kubectl apply -f configs/runtime/reliability-${REGION}.yaml
```

---

## Testing Configuration Validator

Create a test suite to validate reliability config:

```python
# tests/config/test_reliability_config.py
import yaml
import pytest

def test_reliability_config_valid():
    """Ensure reliability.yaml is valid and within safe ranges."""
    with open("configs/runtime/reliability.yaml") as f:
        config = yaml.safe_load(f)
    
    # Timeout validation
    assert 100 <= config["timeouts"]["connect_ms"] <= 10000, \
        "connect_ms must be 100-10000ms"
    assert 1000 <= config["timeouts"]["read_ms"] <= 30000, \
        "read_ms must be 1000-30000ms"
    
    # Backoff validation
    assert 0.01 <= config["backoff"]["base_s"] <= 5.0, \
        "base_s must be 0.01-5.0 seconds"
    assert 1.0 <= config["backoff"]["factor"] <= 5.0, \
        "factor must be 1.0-5.0"
    assert 0.0 <= config["backoff"]["jitter"] <= 1.0, \
        "jitter must be 0.0-1.0"
    
    # Rate limit validation
    assert 1 <= config["rate_limits"]["responses_rps"] <= 1000, \
        "responses_rps must be 1-1000"
    assert 1 <= config["rate_limits"]["embeddings_rps"] <= 1000, \
        "embeddings_rps must be 1-1000"

def test_reliability_config_slo_compatible():
    """Ensure timeouts allow meeting SLOs."""
    with open("configs/runtime/reliability.yaml") as f:
        config = yaml.safe_load(f)
    
    # read_ms must allow for 2× SLO buffer
    SLO_E2E_MS = 250
    assert config["timeouts"]["read_ms"] >= (SLO_E2E_MS * 2), \
        f"read_ms must be >= {SLO_E2E_MS * 2}ms for SLO compliance"
```

**Run Validation**:
```bash
pytest tests/config/test_reliability_config.py -v
```

---

## Summary

**Quick Reference**:

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| `connect_ms` | 1000ms | 100-10000ms | Connection timeout |
| `read_ms` | 10000ms | 1000-30000ms | Request timeout |
| `base_s` | 0.1s | 0.01-5.0s | Initial retry delay |
| `factor` | 2.0 | 1.0-5.0 | Retry growth rate |
| `jitter` | 0.1 | 0.0-1.0 | Retry randomness |
| `responses_rps` | 20 | 1-1000 | Consciousness stream rate limit |
| `embeddings_rps` | 50 | 1-1000 | Embeddings rate limit |

**Tuning Workflow**:
1. Baseline load test → Document metrics
2. Adjust one parameter at a time
3. Load test → Compare metrics
4. Validate SLOs met
5. Deploy to staging
6. Gradual production rollout with monitoring

**Key Monitoring**:
- p95/p99 latency (vs SLO)
- Error rate (target: <1%)
- 429 rate (target: <5%)
- CPU/memory utilization

---

**Related Documentation**:
- [OpenAPI Quickstart](../openai/QUICKSTART.md) - API usage examples
- [API Error Handling](../openai/API_ERRORS.md) - Error codes and strategies
- [Service Level Objectives](../openai/SLOs.md) - Performance targets
- [Load Testing Guide](../../load/README.md) - k6 scenarios and usage
- [Operational Runbook](./OPERATIONAL_RUNBOOK.md) - Production operations

**Questions or Issues?** Open an issue or contact the platform team.
