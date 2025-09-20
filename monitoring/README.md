# LUKHAS AI Monitoring

Comprehensive monitoring and alerting configuration for LUKHAS AI production deployment.

## Files Overview

### Core Configuration
- **`prometheus-config.yml`** - Main Prometheus configuration with scrape targets
- **`alert-rules.yml`** - Comprehensive alerting rules for all LUKHAS components
- **`legacy_core_sunset_alerts.yml`** - Specific alerts for legacy core deprecation monitoring

### Python Modules
- **`drift_manager.py`** - Drift detection and management automation
- **`__init__.py`** - Python module initialization

## Key Metrics & Alerts

### Critical Alerts (Immediate Response)
- **LUKHASServiceDown** - Main service unavailable
- **GuardianSystemFailure** - Ethics/safety system compromised
- **MemoryCascadeDetected** - Memory system instability
- **HighErrorRate** - System error rate exceeded threshold
- **DriftThresholdExceeded** - Behavioral drift detected

### Warning Alerts (Monitor & Plan)
- **HighLatency** - Response time degradation
- **ResourceExhaustion** - CPU/Memory pressure
- **ConsciousnessCoherenceDown** - Consciousness system health
- **AuthenticationFailures** - Security-related failures

### Component-Specific Monitoring

#### Guardian System (5s scrape interval)
- Ethics validation latency
- Decision confidence scores
- Drift detection metrics
- Policy violation rates

#### Memory System (30s scrape interval)
- Memory fold health
- Cascade prevention metrics
- Storage utilization
- Retrieval performance

#### Consciousness System (30s scrape interval)
- Awareness level stability
- Coherence scores
- Processing thread utilization
- State transition metrics

#### Brain Hub Orchestration (10s scrape interval)
- Coordination latency
- Message queue depth
- Module interconnectivity
- Throughput metrics

## Quick Start

### Local Development
```bash
# Start Prometheus locally
docker run -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus-config.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Access Prometheus UI
open http://localhost:9090
```

### Production Deployment
```bash
# Deploy with Docker Compose
docker-compose -f monitoring/docker-compose.yml up -d

# Deploy to Kubernetes
kubectl apply -f monitoring/k8s/
```

## Alert Destinations

### Severity Levels
- **Critical** → PagerDuty + Slack #lukhas-alerts
- **Warning** → Slack #lukhas-monitoring
- **Info** → Grafana dashboard only

### Runbook Links
All alerts include runbook URLs for standardized response procedures:
- `https://docs.lukhas.ai/runbooks/`

## Dashboard Imports

### Grafana Dashboard IDs
- **LUKHAS Overview** - Dashboard ID: 12001
- **Guardian System** - Dashboard ID: 12002
- **Memory System** - Dashboard ID: 12003
- **Consciousness Metrics** - Dashboard ID: 12004

### Import Command
```bash
# Import all dashboards
curl -X POST http://grafana:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @monitoring/dashboards/lukhas-overview.json
```

## Key PromQL Queries

### System Health
```promql
# Overall system health
up{job="lukhas-ai"}

# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Guardian System
```promql
# Guardian decision rate by action
rate(guardian_decisions_total[5m]) by (action)

# Drift score trend
guardian_drift_score

# Ethics validation latency
histogram_quantile(0.95, rate(guardian_validation_duration_seconds_bucket[5m]))
```

### Memory System
```promql
# Active memory folds
memory_folds_active

# Memory cascade prevention rate
memory_cascade_prevention_rate

# Memory utilization
memory_usage_bytes / memory_limit_bytes
```

### Consciousness System
```promql
# Awareness level
consciousness_awareness_level

# Coherence score
consciousness_coherence_score

# Processing threads
consciousness_processing_threads_active
```

## Configuration Examples

### Adding New Scrape Target
```yaml
scrape_configs:
  - job_name: 'new-service'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['new-service:8080']
```

### Adding New Alert
```yaml
- alert: NewServiceDown
  expr: up{job="new-service"} == 0
  for: 2m
  labels:
    severity: warning
    component: new-service
  annotations:
    summary: "New service is unavailable"
    description: "New service has been down for {{ $value }} minutes"
```

## Troubleshooting

### Common Issues

#### Metrics Not Appearing
1. Check service is exposing metrics on `/metrics`
2. Verify firewall/network connectivity
3. Check Prometheus logs for scrape errors

#### Alerts Not Firing
1. Verify alert rule syntax with `promtool check rules`
2. Check AlertManager configuration
3. Verify notification channels (Slack, PagerDuty)

#### High Cardinality Warnings
1. Limit label values in custom metrics
2. Use recording rules for expensive queries
3. Consider metric sampling for high-volume data

### Debugging Commands
```bash
# Check Prometheus config
promtool check config monitoring/prometheus-config.yml

# Validate alert rules
promtool check rules monitoring/alert-rules.yml

# Test alert rule
promtool query instant prometheus:9090 'up{job="lukhas-ai"} == 0'
```

## Performance Optimization

### Scrape Intervals by Priority
- **Critical systems** (Guardian): 5s
- **Core systems** (API, Brain Hub): 10s
- **Standard systems**: 15s
- **Background systems**: 30s+

### Retention Policy
- **Raw metrics**: 15 days
- **5m aggregates**: 90 days
- **1h aggregates**: 1 year

### Recording Rules
Pre-computed expensive queries for dashboard performance:
```yaml
- record: lukhas:error_rate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

---

*For detailed monitoring setup and troubleshooting, see the full observability documentation at `/docs/monitoring/`.*