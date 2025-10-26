# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Analytics Module - Claude AI Context

**Module**: analytics
**Purpose**: Analytics, metrics collection, and data visualization
**Lane**: L2 (Integration)
**Language**: Python
**Last Updated**: 2025-10-18

---

## Module Overview

The analytics module provides comprehensive analytics capabilities for LUKHAS, including consciousness metrics collection, performance reporting, data visualization, and Prometheus metrics integration.

### Key Features
- **Consciousness Metrics**: Track awareness, coherence, and processing metrics
- **Performance Analytics**: System performance monitoring and reporting
- **Dashboard Integration**: Analytics dashboards with real-time data
- **Prometheus Metrics**: Native Prometheus metrics export
- **Event Recording**: Consciousness event tracking and analysis
- **Alert Generation**: Analytics-driven alerting

### Constellation Framework Integration
- **🧠 Flow Star (Consciousness)**: Consciousness metrics and analytics
- **✦ Trail Star (Memory)**: Historical analytics and trend analysis
- **🛡️ Watch Star (Guardian)**: Compliance and ethics analytics

---

## Architecture

### Core Analytics Components

#### Entrypoints (from manifest)
```python
from analytics import (
    ANALYTICS_DOMAINS,           # Available analytics domains
    METRICS_AVAILABLE,           # Available metrics list
    collect_consciousness_metrics,  # Collect consciousness data
    create_analytics_alert,      # Create analytics-based alerts
    generate_performance_report, # Generate performance reports
    get_analytics_dashboard,     # Get dashboard configuration
    get_analytics_status,        # Get analytics system status
    get_prometheus_metrics,      # Get Prometheus metrics
    record_consciousness_event,  # Record consciousness events
    record_performance_metric,   # Record performance metrics
)
```

---

## Analytics Domains

**ANALYTICS_DOMAINS** covers:
- **Consciousness Analytics**: Awareness levels, coherence scores, processing metrics
- **Memory Analytics**: Fold health, cascade rates, storage utilization
- **Identity Analytics**: Authentication patterns, token usage, security metrics
- **Guardian Analytics**: Ethics validation, drift detection, compliance metrics
- **MATRIZ Analytics**: Pipeline performance, node execution times
- **API Analytics**: Request patterns, latency, throughput

---

## Key Functions

### 1. Consciousness Metrics Collection
```python
from analytics import collect_consciousness_metrics

metrics = collect_consciousness_metrics()
# Returns:
# {
#   'awareness_level': float,
#   'coherence_score': float,
#   'active_engines': int,
#   'processing_latency': float
# }
```

### 2. Performance Reporting
```python
from analytics import generate_performance_report

report = generate_performance_report(
    start_time=datetime.now() - timedelta(hours=24),
    end_time=datetime.now()
)
```

### 3. Event Recording
```python
from analytics import record_consciousness_event

record_consciousness_event(
    event_type='awareness_spike',
    metadata={'level': 0.95, 'duration': '5s'}
)
```

### 4. Prometheus Integration
```python
from analytics import get_prometheus_metrics

# Export metrics in Prometheus format
metrics = get_prometheus_metrics()
```

### 5. Dashboard Access
```python
from analytics import get_analytics_dashboard

dashboard = get_analytics_dashboard(
    domain='consciousness'
)
```

### 6. Analytics Alerts
```python
from analytics import create_analytics_alert

alert = create_analytics_alert(
    metric='consciousness_coherence',
    threshold=0.8,
    severity='warning'
)
```

---

## Metrics Available

**METRICS_AVAILABLE** includes:

### Consciousness Metrics
- `consciousness_awareness_level` - Current awareness level
- `consciousness_coherence_score` - Coherence metric
- `consciousness_processing_latency` - Processing time
- `consciousness_active_engines` - Number of active engines

### Performance Metrics
- `system_cpu_usage` - CPU utilization
- `system_memory_usage` - Memory utilization
- `api_request_latency` - API response times
- `api_request_count` - Request throughput

### Memory Metrics
- `memory_fold_count` - Total memory folds
- `memory_cascade_rate` - Cascade prevention rate
- `memory_storage_usage` - Storage utilization

### Guardian Metrics
- `guardian_drift_score` - Current drift detection score
- `guardian_validation_rate` - Ethics validation success rate
- `guardian_policy_violations` - Policy violation count

---

## Module Structure

```
analytics/
├── __init__.py                    # Module initialization with all entrypoints
├── README.md                      # Analytics overview
├── config/                        # Configuration
│   ├── config.yaml
│   ├── environment.yaml
│   └── logging.yaml
├── docs/                          # Documentation
│   ├── README.md
│   ├── architecture.md
│   └── troubleshooting.md
├── schema/                        # Analytics schemas
└── tests/                         # Test suites
    ├── conftest.py
    ├── test_analytics_unit.py
    └── test_analytics_integration.py
```

---

## Integration Points

### Prometheus Integration
- Native Prometheus metrics export
- Custom metrics registration
- Label-based metric organization
- Automatic metric collection intervals

### Dashboard Systems
- Grafana dashboard templates
- Real-time data streaming
- Customizable visualizations
- Domain-specific dashboards

### Alert Integration
- Metrics-based alert generation
- Threshold monitoring
- Anomaly detection
- Integration with monitoring/alerting systems

---

## Development Guidelines

### 1. Adding New Metrics
```python
from analytics import record_performance_metric

# Record custom metric
record_performance_metric(
    name='my_custom_metric',
    value=123.45,
    labels={'component': 'my_feature'}
)
```

### 2. Creating Analytics Reports
```python
from analytics import generate_performance_report

# Generate custom report
report = generate_performance_report(
    domains=['consciousness', 'memory'],
    metrics=['coherence_score', 'fold_count'],
    aggregation='hourly'
)
```

### 3. Accessing Dashboards
```python
from analytics import get_analytics_dashboard

# Get domain-specific dashboard
dashboard = get_analytics_dashboard(
    domain='matriz',
    refresh_interval=5  # seconds
)
```

---

## MATRIZ Pipeline Integration

This module operates within the MATRIZ cognitive framework:

- **M (Memory)**: Historical analytics and trend storage
- **A (Attention)**: Focus on critical metrics and anomalies
- **T (Thought)**: Analysis and pattern recognition in metrics
- **R (Risk)**: Risk assessment through analytics
- **I (Intent)**: Intentional metric collection and reporting
- **A (Action)**: Automated responses to analytics insights

---

## Performance Targets

- **Metrics Collection**: <50ms per collection cycle
- **Dashboard Refresh**: <1s for real-time updates
- **Report Generation**: <5s for 24-hour reports
- **Prometheus Export**: <100ms for full metrics export

---

## Related Modules

- **Monitoring** ([../monitoring/](../monitoring/)) - System monitoring and alerting
- **Consciousness** ([../consciousness/](../consciousness/)) - Consciousness metrics source
- **Memory** ([../memory/](../memory/)) - Memory metrics source
- **Guardian** ([../governance/](../governance/)) - Ethics and compliance analytics

---

## Documentation

- **README**: [analytics/README.md](README.md) - Analytics overview
- **Docs**: [analytics/docs/](docs/) - Architecture and guides
- **Tests**: [analytics/tests/](tests/) - Analytics test suites
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#analytics)

---

**Status**: Integration Lane (L2)
**Manifest**: ✓ module.manifest.json (schema v3.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**Last Updated**: 2025-10-18


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
