# Prometheus Monitoring Guide for LUKHAS AI

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-01-08

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Available Metrics](#available-metrics)
- [Quick Start](#quick-start)
- [Prometheus Setup](#prometheus-setup)
- [Grafana Dashboards](#grafana-dashboards)
- [Custom Metrics](#custom-metrics)
- [Query Examples](#query-examples)
- [Alerting Rules](#alerting-rules)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

LUKHAS AI uses **Prometheus** for comprehensive system monitoring and observability. The monitoring stack provides real-time insights into:

- **Router Performance**: Signal processing, cascade prevention, rule matching
- **Network Health**: Coherence scores, active nodes, connectivity
- **Bio-Symbolic Processing**: Pattern recognition, adaptation tracking
- **MATRIZ Operations**: Cognitive engine performance metrics (planned)
- **API Performance**: Request latency, throughput, error rates (planned)

### Key Features

✅ **Duplicate-Tolerant Registry**: No `ValueError: Duplicated timeseries` errors
✅ **Centralized Metrics**: Single `LUKHAS_REGISTRY` for all components
✅ **Test-Friendly**: Works seamlessly with pytest collection
✅ **Production-Ready**: Optimized for <250ms p95 latency monitoring
✅ **Multi-Lane Support**: Metrics from candidate/, core/, and lukhas/ lanes

---

## Architecture

### Centralized Registry Pattern

```
┌──────────────────────────────────────┐
│     observability/__init__.py        │
│  (Central Import & Registry Setup)   │
└───────────────┬──────────────────────┘
                │
        ┌───────▼───────────┐
        │ prometheus_registry│
        │  LUKHAS_REGISTRY   │
        └────────┬───────────┘
                 │
     ┌───────────┼───────────┬─────────┐
     │           │           │         │
┌────▼─────┐ ┌──▼────┐ ┌────▼────┐ ┌──▼────┐
│  Router  │ │Network│ │   Bio   │ │MATRIZ │
│ Metrics  │ │Metrics│ │ Metrics │ │Metrics│
└──────────┘ └───────┘ └─────────┘ └───────┘
```

### Metrics Flow

1. **Definition**: Metrics defined using factory functions (`counter`, `gauge`, `histogram`)
2. **Registration**: Automatically registered to `LUKHAS_REGISTRY`
3. **Caching**: Duplicate metric requests return cached instance
4. **Collection**: Prometheus scrapes `/metrics` endpoint
5. **Visualization**: Grafana queries Prometheus for dashboards
6. **Alerting**: Prometheus AlertManager triggers notifications

---

## Available Metrics

### Router Metrics

Defined in [core/metrics.py](../../core/metrics.py):

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `lukhas_router_no_rule_total` | Counter | Signals that matched no routing rule | `signal_type`, `producer_module` |
| `lukhas_router_signal_processing_seconds` | Histogram | Signal processing time | `signal_type`, `routing_strategy` |
| `lukhas_router_cascade_preventions_total` | Counter | Signals blocked by cascade prevention | `producer_module` |

**Example Usage**:
```python
from core.metrics import router_no_rule_total, router_signal_processing_time

# Increment counter
router_no_rule_total.labels(
    signal_type="consciousness_event",
    producer_module="dream_engine"
).inc()

# Record processing time
with router_signal_processing_time.labels(
    signal_type="memory_consolidation",
    routing_strategy="bio_adaptive"
).time():
    # ... process signal ...
    pass
```

### Network Health Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `lukhas_network_coherence_score` | Gauge | Current network coherence (0-1 scale) |
| `lukhas_network_active_nodes` | Gauge | Number of active cognitive nodes |

**Example Usage**:
```python
from core.metrics import network_coherence_score, network_active_nodes

# Update coherence score
network_coherence_score.set(0.87)

# Update active nodes count
network_active_nodes.set(12)
```

### Bio-Symbolic Processing Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `lukhas_bio_processor_signals_total` | Counter | Total signals processed | `pattern_type` |
| `lukhas_bio_processor_adaptations_total` | Counter | Total adaptations applied | `adaptation_rule` |

**Example Usage**:
```python
from core.metrics import bio_processor_signals_total, bio_processor_adaptations_total

# Track bio-symbolic processing
bio_processor_signals_total.labels(pattern_type="quantum_entanglement").inc()
bio_processor_adaptations_total.labels(adaptation_rule="coherence_boost").inc()
```

### MATRIZ Metrics (Planned)

Future metrics for MATRIZ cognitive engine:

```python
# Planned MATRIZ metrics
matriz_operations_total = counter(
    "matriz_operations_total",
    "Total MATRIZ cognitive operations",
    labelnames=("operation_type", "status")
)

matriz_operation_duration_ms = histogram(
    "matriz_operation_duration_milliseconds",
    "MATRIZ operation latency (ms)",
    labelnames=("operation_type",),
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000]
)

active_thoughts = gauge(
    "matriz_active_thoughts",
    "Number of active thoughts in MATRIZ"
)
```

---

## Quick Start

### 1. Verify Prometheus is Available

```python
from core.metrics import PROMETHEUS_AVAILABLE

if PROMETHEUS_AVAILABLE:
    print("✅ Prometheus client installed")
else:
    print("❌ Install prometheus-client: pip install prometheus-client")
```

### 2. Add Metrics to Your Code

```python
from observability import counter, histogram, gauge

# Define your metric (duplicate-tolerant)
my_requests_total = counter(
    name="lukhas_my_requests_total",
    documentation="Total requests to my component",
    labelnames=("method", "status")
)

# Use the metric
my_requests_total.labels(method="POST", status="success").inc()
```

### 3. Expose Metrics Endpoint

For FastAPI applications:

```python
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from observability import LUKHAS_REGISTRY

app = FastAPI()

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(LUKHAS_REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )
```

For Flask applications:

```python
from flask import Flask, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from observability import LUKHAS_REGISTRY

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(LUKHAS_REGISTRY),
        mimetype=CONTENT_TYPE_LATEST
    )
```

### 4. Test Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

Expected output:
```prometheus
# HELP lukhas_router_no_rule_total Signals that matched no routing rule
# TYPE lukhas_router_no_rule_total counter
lukhas_router_no_rule_total{signal_type="consciousness_event",producer_module="dream_engine"} 42.0

# HELP lukhas_network_coherence_score Current network coherence score (0-1)
# TYPE lukhas_network_coherence_score gauge
lukhas_network_coherence_score 0.87
```

---

## Prometheus Setup

### Installation

**macOS** (Homebrew):
```bash
brew install prometheus
```

**Ubuntu/Debian**:
```bash
sudo apt-get install prometheus
```

**Docker**:
```bash
docker pull prom/prometheus
```

### Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s       # Scrape metrics every 15 seconds
  evaluation_interval: 15s   # Evaluate alerting rules every 15 seconds
  external_labels:
    cluster: 'lukhas-production'
    environment: 'production'

# Scrape configurations
scrape_configs:
  # LUKHAS API server
  - job_name: 'lukhas-api'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          service: 'lukhas-api'
          team: 'consciousness'

  # LUKHAS Dream Engine
  - job_name: 'lukhas-dream-engine'
    static_configs:
      - targets: ['localhost:8001']
        labels:
          service: 'dream-engine'
          team: 'consciousness'

  # LUKHAS MATRIZ Engine
  - job_name: 'lukhas-matriz'
    static_configs:
      - targets: ['localhost:8002']
        labels:
          service: 'matriz'
          team: 'cognitive'

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

# Load alerting rules
rule_files:
  - "alerts.yml"
```

### Start Prometheus

```bash
# macOS/Linux
prometheus --config.file=prometheus.yml

# Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

Access Prometheus UI at `http://localhost:9090`

---

## Grafana Dashboards

### Installation

**macOS** (Homebrew):
```bash
brew install grafana
brew services start grafana
```

**Ubuntu/Debian**:
```bash
sudo apt-get install -y grafana
sudo systemctl start grafana-server
```

**Docker**:
```bash
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  grafana/grafana
```

Access Grafana at `http://localhost:3000` (default login: admin/admin)

### Add Prometheus Data Source

1. Navigate to **Configuration → Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL: `http://localhost:9090`
5. Click **Save & Test**

### Dashboard: LUKHAS System Overview

Create a new dashboard with these panels:

#### Panel 1: Network Coherence Score

**Query**:
```promql
lukhas_network_coherence_score
```

**Visualization**: Gauge
- **Min**: 0
- **Max**: 1
- **Thresholds**:
  - Red: < 0.5 (poor coherence)
  - Yellow: 0.5 - 0.8 (moderate)
  - Green: > 0.8 (excellent)

#### Panel 2: Active Cognitive Nodes

**Query**:
```promql
lukhas_network_active_nodes
```

**Visualization**: Stat
- Display as: Current value
- Color mode: Value

#### Panel 3: Router Signal Processing Rate

**Query**:
```promql
rate(lukhas_router_signal_processing_seconds_count[5m])
```

**Visualization**: Graph
- Unit: ops/s (operations per second)
- Legend: {{signal_type}}

#### Panel 4: Router Processing Latency (p95)

**Query**:
```promql
histogram_quantile(0.95,
  rate(lukhas_router_signal_processing_seconds_bucket[5m])
)
```

**Visualization**: Graph
- Unit: seconds (s)
- Alert threshold: 0.25s (250ms target)

#### Panel 5: Bio-Symbolic Adaptations

**Query**:
```promql
rate(lukhas_bio_processor_adaptations_total[5m])
```

**Visualization**: Bar gauge
- Group by: {{adaptation_rule}}

#### Panel 6: Cascade Prevention Events

**Query**:
```promql
sum(rate(lukhas_router_cascade_preventions_total[5m])) by (producer_module)
```

**Visualization**: Time series
- Legend: {{producer_module}}

### Dashboard JSON Export

```json
{
  "dashboard": {
    "title": "LUKHAS System Overview",
    "tags": ["lukhas", "consciousness", "matriz"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Network Coherence Score",
        "type": "gauge",
        "targets": [
          {
            "expr": "lukhas_network_coherence_score",
            "legendFormat": "Coherence"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 1,
            "thresholds": {
              "steps": [
                { "value": 0, "color": "red" },
                { "value": 0.5, "color": "yellow" },
                { "value": 0.8, "color": "green" }
              ]
            }
          }
        },
        "gridPos": { "x": 0, "y": 0, "w": 6, "h": 8 }
      },
      {
        "id": 2,
        "title": "Active Cognitive Nodes",
        "type": "stat",
        "targets": [
          {
            "expr": "lukhas_network_active_nodes",
            "legendFormat": "Nodes"
          }
        ],
        "gridPos": { "x": 6, "y": 0, "w": 6, "h": 8 }
      },
      {
        "id": 3,
        "title": "Router Signal Processing Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(lukhas_router_signal_processing_seconds_count[5m])",
            "legendFormat": "{{signal_type}}"
          }
        ],
        "yaxes": [
          { "format": "ops", "label": "Operations/sec" }
        ],
        "gridPos": { "x": 12, "y": 0, "w": 12, "h": 8 }
      },
      {
        "id": 4,
        "title": "Router Processing Latency (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(lukhas_router_signal_processing_seconds_bucket[5m]))",
            "legendFormat": "p95 latency"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [0.25], "type": "gt" },
              "query": { "params": ["A", "5m", "now"] }
            }
          ]
        },
        "gridPos": { "x": 0, "y": 8, "w": 12, "h": 8 }
      }
    ],
    "refresh": "10s",
    "time": { "from": "now-1h", "to": "now" }
  }
}
```

Save this to `lukhas_dashboard.json` and import to Grafana.

---

## Custom Metrics

### Adding New Metrics

```python
# my_component.py
from observability import counter, histogram, gauge, summary

# Counter: monotonically increasing
my_component_requests = counter(
    name="lukhas_my_component_requests_total",
    documentation="Total requests to my component",
    labelnames=("method", "endpoint", "status")
)

# Gauge: can go up or down
my_component_queue_size = gauge(
    name="lukhas_my_component_queue_size",
    documentation="Current queue size"
)

# Histogram: distribution of values
my_component_latency = histogram(
    name="lukhas_my_component_latency_seconds",
    documentation="Request latency in seconds",
    labelnames=("endpoint",),
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Summary: similar to histogram, with quantiles
my_component_request_size = summary(
    name="lukhas_my_component_request_size_bytes",
    documentation="Request size in bytes"
)

# Usage examples
def handle_request(method: str, endpoint: str):
    start_time = time.time()

    try:
        # Process request
        result = process(endpoint)

        # Success metrics
        my_component_requests.labels(
            method=method,
            endpoint=endpoint,
            status="success"
        ).inc()

    except Exception as e:
        # Error metrics
        my_component_requests.labels(
            method=method,
            endpoint=endpoint,
            status="error"
        ).inc()
        raise

    finally:
        # Always record latency
        latency = time.time() - start_time
        my_component_latency.labels(endpoint=endpoint).observe(latency)

    # Update queue size
    my_component_queue_size.set(get_current_queue_size())

    return result
```

### Metric Naming Conventions

Follow Prometheus best practices:

- **Prefix**: `lukhas_` for all LUKHAS metrics
- **Subsystem**: Component name (e.g., `lukhas_router_`, `lukhas_matriz_`)
- **Suffix**:
  - `_total` for counters
  - `_seconds` for durations
  - `_bytes` for sizes
  - No suffix for gauges
- **Examples**:
  - ✅ `lukhas_api_requests_total`
  - ✅ `lukhas_matriz_operation_duration_seconds`
  - ✅ `lukhas_memory_consolidation_bytes`
  - ❌ `request_count` (no prefix)
  - ❌ `lukhas_api_time` (unclear unit)

### Label Best Practices

- Use **low-cardinality labels** (avoid user IDs, timestamps)
- ✅ Good labels: `method`, `status`, `endpoint`, `component`
- ❌ Bad labels: `user_id`, `request_id`, `timestamp`, `dream_content`

```python
# GOOD: Low cardinality (3 methods × 5 endpoints × 2 statuses = 30 series)
requests.labels(method="POST", endpoint="/dream/process", status="success").inc()

# BAD: High cardinality (millions of unique user_ids × dream_ids)
requests.labels(user_id="user_12345", dream_id="dream_67890").inc()
```

---

## Query Examples

### PromQL Basics

Access Prometheus at `http://localhost:9090/graph`

#### Current Values

```promql
# Network coherence right now
lukhas_network_coherence_score

# Active nodes count
lukhas_network_active_nodes
```

#### Rate of Change

```promql
# Requests per second (5-minute average)
rate(lukhas_router_no_rule_total[5m])

# Adaptations per second by rule
rate(lukhas_bio_processor_adaptations_total[5m])
```

#### Aggregations

```promql
# Total requests across all signal types
sum(lukhas_router_no_rule_total)

# Requests grouped by signal type
sum by (signal_type) (lukhas_router_no_rule_total)

# Average coherence across all nodes
avg(lukhas_network_coherence_score)
```

#### Percentiles

```promql
# p50 (median) latency
histogram_quantile(0.50,
  rate(lukhas_router_signal_processing_seconds_bucket[5m])
)

# p95 latency (95% of requests faster than this)
histogram_quantile(0.95,
  rate(lukhas_router_signal_processing_seconds_bucket[5m])
)

# p99 latency
histogram_quantile(0.99,
  rate(lukhas_router_signal_processing_seconds_bucket[5m])
)
```

#### Comparisons

```promql
# Coherence > 0.8
lukhas_network_coherence_score > 0.8

# Latency violations (>250ms target)
histogram_quantile(0.95,
  rate(lukhas_router_signal_processing_seconds_bucket[5m])
) > 0.25
```

---

## Alerting Rules

Create `alerts.yml`:

```yaml
groups:
  - name: lukhas_alerts
    interval: 30s
    rules:
      # Network coherence alerts
      - alert: LowNetworkCoherence
        expr: lukhas_network_coherence_score < 0.5
        for: 5m
        labels:
          severity: warning
          team: consciousness
        annotations:
          summary: "Network coherence below 50%"
          description: "Coherence score is {{ $value }}, indicating potential instability"

      - alert: CriticalNetworkCoherence
        expr: lukhas_network_coherence_score < 0.3
        for: 2m
        labels:
          severity: critical
          team: consciousness
        annotations:
          summary: "CRITICAL: Network coherence below 30%"
          description: "Immediate intervention required. Coherence: {{ $value }}"

      # Latency SLO alerts
      - alert: RouterLatencySLOViolation
        expr: histogram_quantile(0.95, rate(lukhas_router_signal_processing_seconds_bucket[5m])) > 0.25
        for: 10m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "Router p95 latency exceeds 250ms target"
          description: "Current p95 latency: {{ $value }}s"

      - alert: RouterLatencyCritical
        expr: histogram_quantile(0.95, rate(lukhas_router_signal_processing_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          summary: "CRITICAL: Router p95 latency > 1s"
          description: "System severely degraded. p95: {{ $value }}s"

      # Active nodes alerts
      - alert: FewActiveNodes
        expr: lukhas_network_active_nodes < 3
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "Low number of active cognitive nodes"
          description: "Only {{ $value }} nodes active, expect at least 3"

      # Cascade prevention spike
      - alert: HighCascadePreventions
        expr: rate(lukhas_router_cascade_preventions_total[5m]) > 10
        for: 10m
        labels:
          severity: warning
          team: consciousness
        annotations:
          summary: "High rate of cascade preventions"
          description: "Cascade prevention rate: {{ $value }}/sec"
```

### AlertManager Configuration

Create `alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'lukhas-ops'

  routes:
    - match:
        severity: critical
      receiver: 'lukhas-critical'
      continue: true

    - match:
        team: consciousness
      receiver: 'consciousness-team'

receivers:
  - name: 'lukhas-ops'
    slack_configs:
      - channel: '#lukhas-ops'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'lukhas-critical'
    slack_configs:
      - channel: '#lukhas-critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'

  - name: 'consciousness-team'
    slack_configs:
      - channel: '#consciousness-team'
```

---

## Production Deployment

### Docker Compose Stack

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: lukhas-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    restart: unless-stopped
    networks:
      - lukhas-monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: lukhas-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    restart: unless-stopped
    networks:
      - lukhas-monitoring
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    container_name: lukhas-alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    restart: unless-stopped
    networks:
      - lukhas-monitoring

  # Optional: Node Exporter for host metrics
  node-exporter:
    image: prom/node-exporter:latest
    container_name: lukhas-node-exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    ports:
      - "9100:9100"
    restart: unless-stopped
    networks:
      - lukhas-monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  lukhas-monitoring:
    driver: bridge
```

### Start Monitoring Stack

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

Access:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **AlertManager**: http://localhost:9093

---

## Troubleshooting

### No Metrics Appearing

**Problem**: `/metrics` endpoint returns empty or no LUKHAS metrics

**Solutions**:
1. Check Prometheus client is installed:
   ```bash
   pip install prometheus-client
   ```

2. Verify metrics are being incremented:
   ```python
   from core.metrics import router_no_rule_total
   router_no_rule_total.labels(signal_type="test", producer_module="test").inc()
   ```

3. Check metrics endpoint:
   ```bash
   curl http://localhost:8000/metrics | grep lukhas
   ```

### Duplicate Timeseries Errors

**Problem**: `ValueError: Duplicated timeseries in CollectorRegistry`

**Solution**: LUKHAS uses duplicate-tolerant registry - this should NOT happen. If it does:

1. Ensure you're using the centralized factories:
   ```python
   # CORRECT
   from observability import counter
   my_metric = counter("lukhas_my_metric", "My metric")

   # WRONG (will cause duplicates)
   from prometheus_client import Counter
   my_metric = Counter("lukhas_my_metric", "My metric")
   ```

2. Clear the cache if needed:
   ```python
   from observability.prometheus_registry import _CACHE
   _CACHE.clear()
   ```

### Metrics Not Updating in Grafana

**Problem**: Grafana shows old data or no data

**Solutions**:
1. Check Prometheus is scraping:
   - Go to Prometheus UI → Status → Targets
   - Verify target is "UP"

2. Check scrape interval:
   ```yaml
   # prometheus.yml
   scrape_interval: 15s  # Reduce if needed
   ```

3. Verify query in Prometheus UI first before using in Grafana

4. Refresh Grafana dashboard or reduce time range

### High Cardinality Issues

**Problem**: Too many time series, Prometheus performance degraded

**Solutions**:
1. Review labels - remove high-cardinality labels (user IDs, timestamps)
2. Use recording rules to pre-aggregate:
   ```yaml
   # prometheus.yml
   rule_files:
     - "recording_rules.yml"
   ```

3. Set retention limits:
   ```bash
   prometheus --storage.tsdb.retention.time=15d
   ```

---

## Performance Targets

Based on MATRIZ specifications:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Latency (p95)** | <250ms | >250ms for 10min |
| **Throughput** | >50 ops/sec | <25 ops/sec for 5min |
| **Network Coherence** | >0.8 | <0.5 for 5min |
| **Active Nodes** | ≥3 nodes | <3 nodes for 5min |
| **Metrics Endpoint** | <100ms | >500ms |

---

## Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Dashboards**: https://grafana.com/docs/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Best Practices**: https://prometheus.io/docs/practices/naming/

**Implementation Files**:
- [observability/prometheus_registry.py](../../observability/prometheus_registry.py) - Central registry
- [core/metrics.py](../../core/metrics.py) - Core metrics definitions
- [observability/__init__.py](../../observability/__init__.py) - Metric factories

---

**Last Updated**: 2025-01-08
**Version**: 1.0.0
**Status**: ✅ Production Ready

🤖 Generated with Claude Code
