# SLO Budgets (Façade)

Service Level Objectives for the Lukhas OpenAI-compatible façade.

## Latency Budgets

### `/v1/responses`
- **p95**: ≤ 1200ms
- **p99**: ≤ 2500ms

### `/v1/embeddings`
- **p95**: ≤ 800ms
- **p99**: ≤ 1500ms

### `/v1/dreams`
- **p95**: ≤ 2000ms (longer due to consciousness processing)
- **p99**: ≤ 5000ms

## Availability

- **Target**: 99.9% uptime (8.76 hours downtime per year)
- **Measurement**: Health check responses (`/healthz`)

## Error Rate

- **Target**: < 0.1% of requests result in 5xx errors
- **Excludes**: 4xx errors (client errors)

## Enforcement

### Development

**Smoke Tests** (`tests/smoke/test_healthz.py`):
- Warns if p95 > budget
- Does not block builds

### Production

**Load Testing** (nightly):
- Runs `load/resp_scenario.js` with 50 VUs for 2 minutes
- Posts p95 to `docs/audits/load_report.md`
- Alerts if budget exceeded for 3 consecutive runs

## Monitoring

### Metrics Exposed

Via `/metrics` endpoint (Prometheus format):

```
# Response time histogram
lukhas_responses_latency_ms_bucket{le="500"} 1234
lukhas_responses_latency_ms_bucket{le="1000"} 2345
lukhas_responses_latency_ms_bucket{le="1200"} 2890
lukhas_responses_latency_ms_count 3000
lukhas_responses_latency_ms_sum 1234567

# Request count
lukhas_requests_total{endpoint="/v1/responses",status="200"} 2950
lukhas_requests_total{endpoint="/v1/responses",status="429"} 30
lukhas_requests_total{endpoint="/v1/responses",status="500"} 20
```

### Grafana Dashboards

Import dashboard from `monitoring/grafana/dashboards/facade_slos.json` (coming soon).

## Budget Adjustment Process

SLO budgets are reviewed quarterly. To propose changes:

1. Gather p95/p99 data for 30+ days
2. Document use case requirements
3. Submit PR updating `configs/observability/slo_budgets.yaml`
4. Platform team reviews and approves

## Incident Response

When SLOs are breached:

1. **Alert fires** (PagerDuty/Slack)
2. **On-call engineer** investigates
3. **Postmortem** created within 48 hours
4. **Action items** tracked to completion

See [Incident Response Runbook](./incident_response.md) (coming soon).

## Related Documentation

- [API Rate Limits](../API_ERRORS.md) - Rate limiting and backoff
- [Load Testing Guide](../../load/README.md) - Running load tests locally
- [Reliability Configuration](../../configs/runtime/reliability.yaml) - Timeout and backoff settings
