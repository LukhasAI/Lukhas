# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Grafana Module - LUKHAS Visualization & Dashboards

**Module**: grafana
**Lane**: L2 Integration
**Team**: Core
**Purpose**: Grafana dashboards and visualization configuration for LUKHAS system monitoring

---

## Overview

The grafana module provides pre-configured Grafana dashboards, data source configurations, and visualization panels for comprehensive LUKHAS AI system monitoring. This module integrates with Prometheus, OpenTelemetry, and other data sources to provide real-time visibility into system health, performance, and behavior.

**Key Features**:
- Pre-configured LUKHAS dashboards
- Prometheus data source integration
- OpenTelemetry trace visualization
- Custom panel configurations
- Alert visualization
- Multi-environment support

---

## Architecture

### Module Structure

```
grafana/
├── README.md                    # Module overview
├── module.manifest.json         # Module metadata
├── provisioning/
│   ├── dashboards/
│   │   └── lukhas.yml          # Dashboard provisioning config
│   ├── datasources/            # Data source configurations
│   └── notifiers/              # Alert notification configs
├── dashboards/                  # Dashboard JSON definitions
├── config/
│   ├── config.yaml             # Grafana configuration
│   ├── environment.yaml        # Environment-specific settings
│   └── logging.yaml            # Logging configuration
├── docs/                        # Documentation
└── tests/                       # Configuration tests
```

---

## Core Components

### 1. Dashboard Provisioning

**Configuration**: `provisioning/dashboards/lukhas.yml`

Automatic dashboard loading on Grafana startup:

```yaml
apiVersion: 1

providers:
  - name: 'LUKHAS Dashboards'
    orgId: 1
    folder: 'LUKHAS AI'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards
      foldersFromFilesStructure: true
```

---

### 2. Pre-Configured Dashboards

#### System Overview Dashboard
- **Purpose**: High-level system health and performance
- **Metrics**:
  - Overall system uptime
  - Request rate (req/sec)
  - Error rate (%)
  - Average latency (ms)
  - Resource utilization (CPU, memory)

#### Consciousness Dashboard
- **Purpose**: Consciousness module monitoring
- **Panels**:
  - Awareness level over time
  - Dream state distribution
  - Consciousness drift detection
  - Integration coherence score
  - Processing latency percentiles

#### Memory Dashboard
- **Purpose**: Memory system health and performance
- **Panels**:
  - Memory fold count (current/max: 1000)
  - Cascade prevention success rate (target: 99.7%)
  - Fold creation/deletion rate
  - Memory retrieval latency
  - Vector search performance

#### Identity Dashboard
- **Purpose**: Authentication and identity metrics
- **Panels**:
  - Authentication success/failure rate
  - Active sessions
  - WebAuthn usage
  - Namespace distribution
  - Token lifecycle (creation, renewal, expiration)

#### Guardian Dashboard
- **Purpose**: Safety and ethics monitoring
- **Panels**:
  - Violation detection count
  - Drift detection alerts
  - Constitutional AI compliance
  - Guardian response time
  - Policy enforcement rate

#### MATRIZ Pipeline Dashboard
- **Purpose**: MATRIZ pipeline observability
- **Panels**:
  - Stage latency breakdown (Memory, Attention, Thought, Risk, Intent, Action)
  - Pipeline throughput
  - Stage error rates
  - End-to-end pipeline latency (<250ms target)

#### API Performance Dashboard
- **Purpose**: API endpoint monitoring
- **Panels**:
  - Request rate by endpoint
  - Latency percentiles (p50, p95, p99)
  - Error rate by status code
  - Throughput heatmap
  - Slow queries

---

### 3. Data Source Configuration

#### Prometheus Data Source

```yaml
apiVersion: 1

datasources:
  - name: LUKHAS Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
      httpMethod: POST
    editable: false
```

#### OpenTelemetry Data Source

```yaml
datasources:
  - name: LUKHAS Traces
    type: tempo
    access: proxy
    url: http://tempo:3200
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        filterByTraceID: true
      serviceMap:
        datasourceUid: prometheus
```

---

### 4. Custom Panels

#### Constellation Framework Panel
- **Visualization**: Radar chart showing 8 constellation stars
- **Metrics**:
  - ⚛️ Anchor (Identity): Auth success rate
  - ✦ Trail (Memory): Fold utilization
  - 🔬 Horizon (Vision): Prediction accuracy
  - 🛡️ Watch (Guardian): Violation detection
  - 🌊 Flow (Adaptation): Adaptation rate
  - ⚡ Spark (Creativity): Creative response %
  - 🎭 Persona (Personality): Personality consistency
  - 🔮 Oracle (Prediction): Oracle accuracy

#### Drift Detection Panel
- **Visualization**: Time series with threshold lines
- **Features**:
  - Current drift value
  - Drift threshold (0.15)
  - Historical trend
  - Alert annotations
  - Realignment events

#### Memory Cascade Prevention Panel
- **Visualization**: Gauge + time series
- **Metrics**:
  - Current cascade prevention rate (target: 99.7%)
  - Cascade events count
  - Prevention success/failure
  - Fold limit proximity (visual warning)

---

### 5. Alert Visualization

Grafana visualizes alerts from Prometheus Alertmanager:

- **Alert State**: Firing, pending, resolved
- **Severity**: Critical, warning, info
- **Component**: System component triggering alert
- **Duration**: How long alert has been active
- **Labels**: Alert metadata and tags

**Alert Dashboard Panels**:
- Active alerts summary
- Alert history timeline
- Alert frequency heatmap
- MTTR (Mean Time To Resolve)

---

## Configuration

### Main Configuration (`config/config.yaml`)

```yaml
grafana:
  server:
    protocol: http
    http_port: 3000
    domain: localhost

  database:
    type: postgres
    host: postgres:5432
    name: grafana
    user: grafana
    password: ${GRAFANA_DB_PASSWORD}

  security:
    admin_user: admin
    admin_password: ${GRAFANA_ADMIN_PASSWORD}
    secret_key: ${GRAFANA_SECRET_KEY}

  auth:
    disable_login_form: false
    oauth_auto_login: false

  dashboards:
    default_home_dashboard_path: /etc/grafana/dashboards/system-overview.json

  alerting:
    enabled: true
    execute_alerts: true

  unified_alerting:
    enabled: true
```

### Environment Configuration (`config/environment.yaml`)

```yaml
environments:
  development:
    server:
      root_url: "http://localhost:3000"
    alerting:
      execute_alerts: false

  staging:
    server:
      root_url: "https://grafana-staging.lukhas.ai"
    alerting:
      execute_alerts: true

  production:
    server:
      root_url: "https://grafana.lukhas.ai"
      enforce_domain: true
    security:
      cookie_secure: true
      strict_transport_security: true
    alerting:
      execute_alerts: true
      max_attempts: 3
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM grafana/grafana:latest

# Copy provisioning configurations
COPY provisioning/ /etc/grafana/provisioning/

# Copy dashboards
COPY dashboards/ /etc/grafana/dashboards/

# Copy configuration
COPY config/config.yaml /etc/grafana/grafana.ini

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:3000/api/health || exit 1
```

### Docker Compose

```yaml
version: '3.8'

services:
  grafana:
    image: lukhas/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SERVER_ROOT_URL=https://grafana.lukhas.ai
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_DATABASE_URL=${GRAFANA_DB_URL}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./provisioning:/etc/grafana/provisioning
      - ./dashboards:/etc/grafana/dashboards
    depends_on:
      - prometheus
      - tempo

volumes:
  grafana-data:
```

---

## Dashboard Access

### Default Dashboards

After deployment, access dashboards at:

- **System Overview**: `http://localhost:3000/d/system-overview`
- **Consciousness**: `http://localhost:3000/d/consciousness`
- **Memory**: `http://localhost:3000/d/memory`
- **Identity**: `http://localhost:3000/d/identity`
- **Guardian**: `http://localhost:3000/d/guardian`
- **MATRIZ Pipeline**: `http://localhost:3000/d/matriz`
- **API Performance**: `http://localhost:3000/d/api`

---

## Performance Targets

- **Dashboard Load Time**: <2 seconds
- **Panel Refresh**: Every 15 seconds (configurable)
- **Query Timeout**: 60 seconds max
- **Data Retention**: 90 days (configurable)

---

## Observability

**Required Spans**:
- `lukhas.grafana.operation`

**Metrics**:
- Dashboard view count
- Panel query duration
- Data source query rate
- Alert evaluation time

---

## Related Modules

- **prometheus/**: Metrics data source
- **monitoring/**: Alert definitions
- **telemetry/**: Observability data collection
- **brain/**: System orchestration metrics

---

## Quick Reference

| Component | Purpose | Default Port |
|-----------|---------|--------------|
| Grafana Server | Dashboard UI | 3000 |
| Prometheus Data Source | Metrics | 9090 |
| Tempo Data Source | Traces | 3200 |
| Loki Data Source | Logs | 3100 |

**Module Status**: L2 Integration
**Schema Version**: 1.0.0
**Last Updated**: 2025-10-18
**Philosophy**: Visibility drives improvement—make every metric beautiful and actionable.


## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
