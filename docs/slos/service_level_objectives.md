---
status: wip
type: documentation
owner: unknown
module: slos
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# LUKHAS AI Service Level Objectives (SLOs)

## Overview

This document defines the Service Level Objectives (SLOs) for the LUKHAS AI system, including error budgets, monitoring queries, and alerting thresholds.

## Core SLOs

### 1. API Availability SLO
- **Target**: 99.9% availability (monthly)
- **Error Budget**: 0.1% (43.2 minutes/month)
- **SLI Query**: `sum(rate(http_requests_total{status!~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`
- **Threshold**: < 99.9% triggers alert

### 2. Memory Recall Latency SLO
- **Target**: 95% of requests < 100ms
- **Error Budget**: 5% can exceed 100ms
- **SLI Query**: `histogram_quantile(0.95, rate(memory_recall_duration_seconds_bucket[5m]))`
- **Threshold**: > 0.1 seconds triggers alert

### 3. MATRIZ Pipeline Latency SLO
- **Target**: 95% of requests < 250ms
- **Error Budget**: 5% can exceed 250ms
- **SLI Query**: `histogram_quantile(0.95, rate(matriz_pipeline_duration_seconds_bucket[5m]))`
- **Threshold**: > 0.25 seconds triggers alert

### 4. Guardian Decision Latency SLO
- **Target**: 99% of decisions < 5ms
- **Error Budget**: 1% can exceed 5ms
- **SLI Query**: `histogram_quantile(0.99, rate(guardian_decision_duration_seconds_bucket[5m]))`
- **Threshold**: > 0.005 seconds triggers alert

### 5. Consciousness Processing SLO
- **Target**: 90% of queries processed successfully
- **Error Budget**: 10% failure rate
- **SLI Query**: `sum(rate(consciousness_queries_total{status="success"}[5m])) / sum(rate(consciousness_queries_total[5m]))`
- **Threshold**: < 90% success triggers alert

## Error Budget Tracking

### Monthly Error Budget Calculations
```promql
# API Availability Budget Remaining
(1 - (1 - 0.999) * (days_in_month * 24 * 60) /
sum(increase(http_requests_total{status=~"5.."}[30d]))) * 100

# Memory Latency Budget Remaining
(1 - sum(rate(memory_recall_duration_seconds_bucket{le="0.1"}[30d])) /
sum(rate(memory_recall_duration_seconds_count[30d]))) * 100

# MATRIZ Pipeline Budget Remaining
(1 - sum(rate(matriz_pipeline_duration_seconds_bucket{le="0.25"}[30d])) /
sum(rate(matriz_pipeline_duration_seconds_count[30d]))) * 100
```

## Alerting Rules

### Critical Alerts (Page immediately)
```yaml
- name: lukhas_critical_slos
  rules:
  - alert: APIAvailabilityBelowSLO
    expr: sum(rate(http_requests_total{status!~"5.."}[5m])) / sum(rate(http_requests_total[5m])) < 0.999
    for: 2m
    labels:
      severity: critical
      service: lukhas-api
    annotations:
      summary: "API availability below SLO (99.9%)"

  - alert: MemoryRecallLatencyBelowSLO
    expr: histogram_quantile(0.95, rate(memory_recall_duration_seconds_bucket[5m])) > 0.1
    for: 1m
    labels:
      severity: critical
      service: lukhas-memory
    annotations:
      summary: "Memory recall P95 latency above 100ms SLO"

  - alert: MATRIZPipelineLatencyBelowSLO
    expr: histogram_quantile(0.95, rate(matriz_pipeline_duration_seconds_bucket[5m])) > 0.25
    for: 1m
    labels:
      severity: critical
      service: lukhas-matriz
    annotations:
      summary: "MATRIZ pipeline P95 latency above 250ms SLO"
```

### Warning Alerts (Investigate within hours)
```yaml
- name: lukhas_warning_slos
  rules:
  - alert: ErrorBudgetBurnRateHigh
    expr: rate(http_requests_total{status=~"5.."}[1h]) > 0.001
    for: 5m
    labels:
      severity: warning
      service: lukhas-api
    annotations:
      summary: "Error budget burning too fast"

  - alert: GuardianLatencyElevated
    expr: histogram_quantile(0.99, rate(guardian_decision_duration_seconds_bucket[5m])) > 0.003
    for: 2m
    labels:
      severity: warning
      service: lukhas-guardian
    annotations:
      summary: "Guardian decision latency elevated"
```

## Dashboards

### SLO Dashboard Panels
1. **API Availability Trend** - 7-day rolling availability
2. **Error Budget Burn Rate** - Current vs target burn rate
3. **Latency Heatmaps** - P50, P95, P99 latencies over time
4. **SLO Compliance Status** - Green/yellow/red status indicators
5. **Error Budget Remaining** - Days remaining at current burn rate

### Grafana Dashboard JSON
Reference: `ops/grafana/lukhas_slo_dashboard.json`

## Error Budget Policies

### Budget Exhaustion Actions
- **>50% budget consumed**: Increase monitoring, review trends
- **>80% budget consumed**: Implement immediate fixes, halt risky deployments
- **100% budget consumed**: Freeze all deployments until SLO compliance restored

### Review Schedule
- **Weekly**: SLO performance review in team meeting
- **Monthly**: Error budget assessment and SLO target adjustment
- **Quarterly**: Full SLO framework review

## Implementation Notes

- All metrics use Prometheus with 5-minute evaluation intervals
- Error budgets calculated over rolling 30-day windows
- Alerts route to PagerDuty for critical, Slack for warnings
- SLO compliance tracked in monthly reliability reports

---

*Generated: 2025-09-22*
*Next Review: 2025-10-22*