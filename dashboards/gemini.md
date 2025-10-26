# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Dashboards Module - LUKHAS Dashboard Definitions

**Module**: dashboards
**Lane**: L2 Integration
**Team**: Core
**Purpose**: Grafana dashboard JSON definitions and configurations for LUKHAS monitoring

---

## Overview

The dashboards module contains Grafana dashboard JSON definitions specifically designed for LUKHAS AI system monitoring. These dashboards provide pre-configured visualizations, panels, and queries optimized for LUKHAS components, making it easy to monitor system health, performance, and behavior out of the box.

**Key Features**:
- Production-ready dashboard definitions (JSON)
- LUKHAS-specific panel configurations
- Pre-configured queries for common metrics
- Multi-environment dashboard variants
- Dashboard templates and variables

---

## Architecture

###Module Structure

```
dashboards/
├── README.md                    # Module overview
├── module.manifest.json         # Module metadata
├── lukhas_ops.json             # Operations dashboard
├── lukhas_drift_ema.json       # Drift detection dashboard (EMA-based)
├── lukhas_unrouted_signals.json # Unrouted signals monitoring
├── config/
│   ├── config.yaml             # Dashboard configuration
│   ├── environment.yaml        # Environment-specific settings
│   └── logging.yaml            # Logging configuration
├── docs/                        # Documentation
└── tests/                       # Dashboard tests
```

---

## Core Dashboards

### 1. Operations Dashboard (`lukhas_ops.json`)

**Purpose**: High-level operational overview of LUKHAS system.

**Panels**:
- System uptime and availability
- Request rate across all services
- Error rate and error distribution
- Resource utilization (CPU, memory, network)
- Service health status matrix
- Active alerts summary

**Refresh**: 30 seconds
**Time Range**: Last 6 hours (configurable)

**Usage**:
```bash
# Import to Grafana
curl -X POST http://grafana:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @lukhas_ops.json
```

---

### 2. Drift Detection Dashboard (`lukhas_drift_ema.json`)

**Purpose**: Monitoring consciousness drift using Exponential Moving Average (EMA) detection.

**Panels**:
- Current drift value with threshold line (0.15)
- EMA drift trend over time
- Drift spike detection
- Realignment events timeline
- Drift distribution histogram
- Trinity Framework compliance status

**Key Metrics**:
- `lukhas_consciousness_drift` (current drift)
- `lukhas_drift_ema` (smoothed drift trend)
- `lukhas_drift_realignment_events` (realignment count)

**Alert Thresholds**:
- Warning: drift > 0.12
- Critical: drift > 0.15

---

### 3. Unrouted Signals Dashboard (`lukhas_unrouted_signals.json`)

**Purpose**: Monitoring signals that failed to route through LUKHAS components.

**Panels**:
- Unrouted signal count over time
- Signals by source component
- Routing failure reasons breakdown
- Signal latency before timeout
- Recovery rate for retried signals

**Key Metrics**:
- `lukhas_signals_unrouted_total` (total unrouted)
- `lukhas_signals_routing_failures` (routing failures by reason)
- `lukhas_signals_retry_success_rate` (retry success percentage)

**Use Case**: Debugging integration issues and signal flow problems.

---

## Dashboard Configuration

### Variables and Templates

Dashboards support variables for multi-environment deployment:

```json
{
  "templating": {
    "list": [
      {
        "name": "environment",
        "type": "custom",
        "options": ["production", "staging", "development"]
      },
      {
        "name": "cluster",
        "type": "query",
        "query": "label_values(up, cluster)"
      },
      {
        "name": "service",
        "type": "query",
        "query": "label_values(up{cluster=\"$cluster\"}, job)"
      }
    ]
  }
}
```

**Usage**: Select environment, cluster, and service from dashboard dropdowns to filter metrics.

---

### Panel Query Examples

#### Consciousness Drift Panel
```json
{
  "targets": [
    {
      "expr": "lukhas_consciousness_drift",
      "legendFormat": "Current Drift",
      "refId": "A"
    },
    {
      "expr": "lukhas_drift_ema{alpha=0.1}",
      "legendFormat": "EMA Drift (α=0.1)",
      "refId": "B"
    }
  ],
  "alert": {
    "conditions": [
      {
        "evaluator": {
          "type": "gt",
          "params": [0.15]
        }
      }
    ]
  }
}
```

#### Memory Fold Usage Panel
```json
{
  "targets": [
    {
      "expr": "lukhas_memory_fold_count / lukhas_memory_fold_limit",
      "legendFormat": "Fold Usage %"
    }
  ],
  "thresholds": [
    {"value": 0.80, "color": "yellow"},
    {"value": 0.95, "color": "red"}
  ]
}
```

---

## Deployment

### Import Dashboards to Grafana

#### Manual Import (UI)
1. Open Grafana → Dashboards → Import
2. Upload dashboard JSON file
3. Select data source (Prometheus)
4. Import

#### Automated Import (API)
```bash
#!/bin/bash
for dashboard in dashboards/*.json; do
  curl -X POST http://grafana:3000/api/dashboards/import \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
    -d @"$dashboard"
done
```

#### Provisioning (Auto-load on startup)
```yaml
# grafana/provisioning/dashboards/lukhas.yml
apiVersion: 1

providers:
  - name: 'LUKHAS Dashboards'
    folder: 'LUKHAS AI'
    type: file
    options:
      path: /etc/grafana/dashboards/lukhas
```

Place dashboard JSON files in `/etc/grafana/dashboards/lukhas/` and Grafana will auto-load them.

---

## Configuration

```yaml
dashboards:
  auto_import: true
  import_path: "./dashboards/*.json"
  default_data_source: "LUKHAS Prometheus"

  refresh_intervals:
    - "5s"
    - "15s"
    - "30s"
    - "1m"
    - "5m"

  time_ranges:
    - "5m"
    - "15m"
    - "1h"
    - "6h"
    - "24h"
    - "7d"
```

---

## Customization

### Adding New Panel

```json
{
  "panels": [
    {
      "id": 1,
      "title": "Custom Metric Panel",
      "type": "graph",
      "targets": [
        {
          "expr": "your_prometheus_query_here",
          "legendFormat": "{{label}}"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
    }
  ]
}
```

### Modifying Existing Dashboard

1. Edit dashboard in Grafana UI
2. Save dashboard
3. Export JSON via "Share" → "Export" → "Save to file"
4. Replace JSON file in `dashboards/` directory
5. Commit to version control

---

## Observability

**Required Spans**:
- `lukhas.dashboards.operation`

**Metrics**:
- Dashboard view count
- Panel query duration
- Import success/failure rate

---

## Related Modules

- **grafana/**: Grafana instance configuration
- **prometheus/**: Metrics data source
- **monitoring/**: Alert definitions
- **alerts/**: Alert rule definitions

---

## Quick Reference

| Dashboard | Purpose | Key Metrics |
|-----------|---------|-------------|
| `lukhas_ops.json` | Operations overview | Uptime, request rate, errors |
| `lukhas_drift_ema.json` | Drift detection | Drift value, EMA trend, realignments |
| `lukhas_unrouted_signals.json` | Signal routing | Unrouted count, failure reasons |

---

**Module Status**: L2 Integration
**Schema Version**: 1.0.0
**Last Updated**: 2025-10-18
**Philosophy**: Dashboards make the invisible visible—design for clarity, not complexity.


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
