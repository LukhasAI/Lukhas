# Post-Merge Monitoring Configuration

## Overview
This document defines monitoring metrics, SLOs, and alert thresholds for the T4 relay (TG-001/TG-002/TG-009) post-merge operational validation.

## Key Metrics & Thresholds

### Registry Service Performance
```yaml
metrics:
  - name: registry.save_checkpoint.latency.p95
    type: histogram
    unit: milliseconds
    threshold: 250ms
    alert: critical
    description: 95th percentile latency for checkpoint save operations

  - name: registry.verify.success_rate
    type: gauge
    unit: percentage
    threshold: 99.9%
    alert: critical
    description: Success rate for signature verification operations
```

### PQC Operations
```yaml
metrics:
  - name: pqc.sign.latency.p95
    type: histogram
    unit: milliseconds
    threshold_initial: 50ms
    threshold_target: 30ms
    alert: warning
    description: 95th percentile signing latency (Dilithium2)

  - name: pqc.verify.latency.p95
    type: histogram
    unit: milliseconds
    threshold: 10ms
    alert: warning
    description: 95th percentile verification latency

  - name: pqc.fallback.triggered
    type: counter
    unit: count
    threshold: 0
    alert: info
    description: Count of PQC fallback to HMAC (should be 0 after runner provisioned)
```

### No-Op Guard Operations
```yaml
metrics:
  - name: noop_guard.false_positive_rate
    type: gauge
    unit: percentage
    threshold: 0.2%
    alert: warning
    description: Rate of false positives (legitimate PRs blocked)
    calculation: FP / (FP + TN) * 100

  - name: noop_guard.true_positive_count
    type: counter
    unit: count
    description: Count of correctly blocked no-op PRs

  - name: noop_guard.audit_entries
    type: counter
    unit: count
    description: Total audit log entries
    source: docs/audits/noop_guard.log
```

### NodeSpec Validation
```yaml
metrics:
  - name: nodespec.validation_failures
    type: counter
    unit: count
    threshold: 0
    alert: critical
    description: Failed NodeSpec validations during promotion window
    context: Must be 0 for production promotions
```

## Dashboard Configuration

### Overview Dashboard
```
+-----------------------------------------+
| Registry Health                         |
| - Checkpoint latency: [GAUGE]          |
| - Verify success rate: [GAUGE]         |
| - Active registrations: [COUNTER]      |
+-----------------------------------------+
| PQC Operations                          |
| - Sign/verify latency: [GRAPH]         |
| - Fallback triggers: [COUNTER]         |
| - PQC artifact presence: [BADGE]       |
+-----------------------------------------+
| No-Op Guard                             |
| - False positive rate: [GAUGE]         |
| - Audit log size: [COUNTER]            |
| - Recent blocks: [TABLE]               |
+-----------------------------------------+
| Post-Merge Status                       |
| - Latest report: [JSON]                |
| - Gate status: [BADGES]                |
| - PR sequence: [LIST]                  |
+-----------------------------------------+
```

### Alert Configuration
```yaml
alerts:
  - name: RegistryLatencyHigh
    condition: registry.save_checkpoint.latency.p95 > 250ms
    severity: critical
    notification: pagerduty

  - name: PQCSignLatencyHigh
    condition: pqc.sign.latency.p95 > 50ms
    severity: warning
    notification: slack

  - name: NoOpGuardFalsePositives
    condition: noop_guard.false_positive_rate > 0.2%
    severity: warning
    notification: slack

  - name: NodeSpecValidationFailed
    condition: nodespec.validation_failures > 0
    severity: critical
    notification: pagerduty
```

## Data Sources

### Primary Sources
- `tmp/post_merge_report.json` - Post-merge validation results
- `docs/audits/noop_guard.log` - No-Op guard audit trail
- `.github/workflows/` artifacts - CI workflow outputs
- Registry service logs (when deployed)

### Collection Methods
```bash
# Post-merge report parsing
jq '.gates' tmp/post_merge_report.json

# No-Op guard metrics
grep -c "BLOCKED" docs/audits/noop_guard.log
grep -c "FALSE_POSITIVE" docs/audits/noop_guard.log

# PQC artifact check
ls -la .github/workflows/artifacts/pqc_*
```

## Observability Period

### Phase 1: Initial (0-72 hours)
- High-frequency monitoring (5-minute intervals)
- All alerts enabled
- Manual review of all incidents
- Daily status reports

### Phase 2: Stabilization (72 hours - 2 weeks)
- Normal monitoring (15-minute intervals)
- Tune alert thresholds based on Phase 1
- Weekly status reports

### Phase 3: Steady State (2+ weeks)
- Standard monitoring (30-minute intervals)
- Production-grade alerting
- Monthly reviews

## Runbook References

### High Latency Response
1. Check `tmp/post_merge_report.json` for recent failures
2. Review registry service logs
3. Investigate I/O bottlenecks (checkpoint file operations)
4. Consider async checkpoint writes if consistent

### False Positive Handling
1. Review `docs/audits/noop_guard.log` for specific case
2. Determine if legitimate small change
3. Add to whitelist if needed
4. Update guard logic if pattern detected

### PQC Fallback
1. Check for `pqc_fallback_marker.txt` artifact
2. Verify liboqs installation on runner
3. Check python-oqs bindings
4. Escalate to infrastructure team

## SLO Tracking

### Registry Service SLOs
- Availability: 99.9% uptime
- Latency: p95 < 250ms, p99 < 500ms
- Throughput: 50+ ops/sec

### PQC Operations SLOs
- Sign latency: p95 < 50ms (initial), target < 30ms
- Verify latency: p95 < 10ms
- Success rate: 100% (no fallbacks after runner provisioned)

### No-Op Guard SLOs
- False positive rate: < 0.2%
- True positive detection: > 95%
- Audit completeness: 100% of runs logged

## Review Schedule

- **Daily** (first 3 days): Full metrics review, incident tracking
- **Weekly** (first 2 weeks): Trend analysis, threshold tuning
- **Monthly**: SLO compliance review, dashboard updates

## Integration Points

### Prometheus Configuration
```yaml
scrape_configs:
  - job_name: 'lukhas-registry'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboards
- Dashboard ID: `lukhas-t4-postmerge`
- Refresh interval: 1m
- Time range: Last 24h (default)

## Revision History
- 2025-10-24: Initial version (post TG-009 merge)
