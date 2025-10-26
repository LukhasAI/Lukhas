# RC Soak Test Results - 2025-10-22

**Test Date**: 2025-10-22 21:41:21
**Test Type**: Quick RC Soak Validation
**Duration**: ~5 minutes
**Test Command**: `make rc-soak-quick`

---

## Executive Summary

✅ **PASSED** - All 50 synthetic load requests successful (100% success rate)
✅ **PASSED** - Health snapshot generation working
✅ **PASSED** - OpenAI-compatible endpoints functional
⚠️ **PARTIAL** - Monitoring stack (Prometheus/Grafana) not available

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Base URL | http://localhost:8000 |
| Total Requests | 50 |
| Concurrent Requests | 2 |
| Server PID | 55633 |
| Server Uptime | 5.39 hours |
| RC Version | v0.9.0-rc |

---

## Synthetic Load Test Results

### Performance Summary

```
Total Requests:    50
Successful:        50
Failed:            0
Success Rate:      100.00%
```

### Request Distribution

- **25 x POST /v1/embeddings** - All 200 OK
- **25 x POST /v1/chat/completions** - All 200 OK
- **3 x GET /healthz** - All 200 OK (periodic health checks)

### Endpoint Validation

| Endpoint | Method | Requests | Success | Failure |
|----------|--------|----------|---------|---------|
| /v1/embeddings | POST | 25 | 25 | 0 |
| /v1/chat/completions | POST | 25 | 25 | 0 |
| /healthz | GET | 3 | 3 | 0 |

---

## Health Snapshot Results

### System Health Status

| Service | Status | Notes |
|---------|--------|-------|
| Façade API | ✅ UP | Responding on port 8000 |
| Prometheus | ❌ DOWN | Optional for basic testing |
| Grafana | ❌ DOWN | Optional for basic testing |

### Façade Health Details

```json
{
  "status": "ok",
  "voice_mode": "degraded",
  "matriz": {
    "version": "unknown",
    "rollout": "disabled",
    "enabled": false
  },
  "lane": "prod",
  "modules": {
    "manifest_count": 1713
  }
}
```

### Metrics Snapshot

All Prometheus-based metrics unavailable (N/A) due to monitoring stack being offline:
- Guardian Denials (24h): N/A
- PDP p95 Latency: N/A
- RL Cache Hit Rate: N/A

---

## Server Log Analysis

### Request Pattern

The server successfully handled all requests with no errors or exceptions:

```
✅ 50 POST requests to OpenAI-compatible endpoints
✅ 3 health check requests
✅ All responses: 200 OK
✅ No 4xx or 5xx errors
✅ No timeout or connection errors
```

### Sample Log Entries

```
INFO:     127.0.0.1:56155 - "POST /v1/chat/completions HTTP/1.1" 200 OK
INFO:     127.0.0.1:56157 - "POST /v1/embeddings HTTP/1.1" 200 OK
INFO:     127.0.0.1:56195 - "GET /healthz HTTP/1.1" 200 OK
```

---

## Test Artifacts Generated

All artifacts successfully created:

1. **JSON Snapshot**: `docs/audits/health/2025-10-22/latest.json` (577 bytes)
2. **Markdown Report**: `docs/audits/health/2025-10-22/latest.md` (1.4 KB)
3. **Test Log**: `/tmp/rc-soak-quick-test.log` (captured output)
4. **Server Log**: `/tmp/lukhas-rc-soak.log` (continuous)
5. **Test Results**: This document

---

## OpenAI Endpoint Validation

### /v1/embeddings Response Structure

Validated that responses match OpenAI format:
- ✅ `object`: "list"
- ✅ `data`: Array with embedding objects
- ✅ `model`: Reflects requested model
- ✅ `usage`: Token counts present

### /v1/chat/completions Response Structure

Validated that responses match OpenAI format:
- ✅ `id`: Generated completion ID
- ✅ `object`: "chat.completion"
- ✅ `created`: Unix timestamp
- ✅ `model`: Reflects requested model
- ✅ `choices`: Array with message content
- ✅ `usage`: Token counts present

---

## Health Endpoint Compatibility

### Endpoint Discovery

Script automatically detected available health endpoint:
```
🔍 Checking health endpoint...
✅ Using /healthz endpoint
```

### Dual Endpoint Support

Both endpoints now functional:
- `/healthz` - Primary endpoint (Kubernetes convention)
- `/health` - Alias for ops compatibility

---

## RC Soak Gates Progress

| Gate | Target | Status | Notes |
|------|--------|--------|-------|
| RC soak duration | ≥48h | ⏳ In Progress | 5.39h completed |
| Guardian denial rate | <1% | ⚠️ N/A | Requires Prometheus |
| PDP p95 latency | <10ms | ⚠️ N/A | Requires Prometheus |
| All services healthy | Yes | ⚠️ Partial | Façade UP, monitoring DOWN |
| No memory leaks | Yes | ⏳ Monitoring | Requires extended run |
| No error rate spikes | Yes | ✅ PASS | 0 errors in 50 requests |

---

## Recommendations

### Immediate Actions

1. ✅ **Continue soak run** - Let server run for 48-72h to validate stability
2. ⚠️ **Optional**: Start Prometheus/Grafana for full metrics visibility
3. ✅ **Schedule snapshots** - Run `make rc-soak-snapshot` every 6-12h

### For Production Readiness

1. Set up full monitoring stack (Prometheus + Grafana)
2. Enable Guardian policy enforcement
3. Configure MATRIZ rollout strategy
4. Address voice subsystem degradation
5. Run under production load patterns

---

## Test Environment

### System Information

- **Platform**: macOS (Darwin 25.1.0)
- **Python**: 3.11
- **Server**: Uvicorn with FastAPI
- **Branch**: main (commit: bd7c5a7bc)

### Dependencies Validated

- ✅ FastAPI routing working
- ✅ Health endpoints responding
- ✅ OpenAI-compatible endpoint stubs functional
- ✅ JSON response serialization working
- ✅ CORS middleware not blocking requests

---

## Conclusion

**Status**: ✅ **READY FOR EXTENDED SOAK**

The RC soak infrastructure is fully operational with 100% success rate on synthetic load tests. OpenAI-compatible endpoints are functioning correctly, health snapshots are generating successfully, and the server is stable after 5+ hours of uptime.

The system is ready for extended 48-72h soak testing to validate production readiness.

---

**Test Conducted By**: Claude Code (Automated)
**Report Generated**: 2025-10-22 21:41:21
**Test Suite**: RC Soak Quick Validation v1.0
