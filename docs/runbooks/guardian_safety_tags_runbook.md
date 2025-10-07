---
status: wip
type: documentation
owner: unknown
module: runbooks
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Guardian Safety Tags Runbook
*Task 13: Production Operations Guide*

## Overview

The Guardian Safety Tags system provides semantic tagging and ethics enforcement for LUKHAS AI operations. This runbook covers monitoring, troubleshooting, and emergency procedures.

## Service Level Objectives (SLOs)

### Performance SLOs
- **Tag Enrichment Latency**: P99 < 2ms, P95 < 1ms
- **Ethics Pipeline Latency**: P99 < 20ms, P95 < 10ms
- **Guardian Evaluation**: P99 < 50ms, P95 < 25ms
- **Availability**: 99.9% uptime (4.3 minutes downtime/month)

### Accuracy SLOs
- **Tag Miss Rate**: < 1% on golden test set
- **False Positive Rate**: < 5% for PII/financial detection
- **Critical → BLOCK Rate**: > 80% (safety threshold)

### A/B Testing SLOs
- **Lane Consistency**: < 0.1% cross-contamination
- **Rollback Detection**: < 10 minutes to detect degradation
- **Auto-rollback Trigger**: < 5 minutes to disable enforcement

## Key Metrics Dashboard

**Grafana Dashboard**: `Guardian — Safety Tags`
**URL**: `https://grafana.lukhas.ai/d/guardian-safety-tags`

### Critical Panels to Monitor

1. **High/Critical Risk Rate**
   - **Alert if**: > 2x baseline for 10 minutes
   - **Query**: `sum by (band) (rate(guardian_risk_band{band=~"high|critical", lane=~"$lane"}[5m]))`

2. **Actions over Time**
   - **Watch for**: Sudden spikes in BLOCK actions
   - **Query**: `sum by (action) (rate(guardian_actions_count{lane=~"$lane"}[5m]))`

3. **Critical → BLOCK %**
   - **Alert if**: < 80% for 10 minutes (triggers auto-rollback)
   - **Query**: `100 * sum(rate(guardian_actions_count{action="block", lane=~"$lane"}[5m])) / sum(rate(guardian_risk_band{band="critical", lane=~"$lane"}[5m]))`

4. **P99 Ethics Pipeline**
   - **Alert if**: > 20ms for 5 minutes
   - **Query**: `histogram_quantile(0.99, sum by (le) (rate(guardian_pipeline_ms_bucket{lane=~"$lane"}[5m])))`

5. **A/B Denial Delta**
   - **Watch for**: > 50% increase in candidate vs control
   - **Query**: `(sum(rate(guardian_actions_count{action=~"warn|require_human|block", lane="candidate"}[5m])) - sum(rate(guardian_actions_count{action=~"warn|require_human|block", lane="control"}[5m]))) / sum(rate(guardian_actions_count{action=~"warn|require_human|block", lane="control"}[5m]))`

## Emergency Procedures

### 1. Complete System Disable (Break Glass)

**When**: Critical safety failure, mass false positives, or system instability

```bash
# Create emergency kill switch file
sudo touch /tmp/guardian_emergency_disable

# Verify all enforcement disabled
curl -s http://localhost:8080/guardian/status | jq '.enforcement_active'
# Should return: false
```

**Recovery**: Remove kill switch file and monitor for 10 minutes before declaring healthy.

### 2. Auto-Rollback Response

**When**: Safety Tags system triggers automatic rollback

**Symptoms**:
- Alert: "GUARDIAN AUTO-ROLLBACK: Critical safety degradation detected"
- Dashboard shows Critical → BLOCK % < 80%
- Candidate lane enforcement automatically disabled

**Response**:
1. **Investigate Root Cause**
   ```bash
   # Check recent safety tag changes
   git log --oneline --since="1 hour ago" candidate/core/ethics/safety_tags.py

   # Review detection accuracy
   grep -i "tag.*confidence.*0\.[0-4]" /var/log/guardian/safety_tags.log
   ```

2. **Analyze Detection Issues**
   ```bash
   # Check for new evasion patterns
   python3 /tmp/analyze_recent_misses.py

   # Review confidence distributions
   curl -s http://localhost:9090/api/v1/query?query=guardian_tags_confidence_bucket | jq
   ```

3. **Manual Recovery** (after fixes):
   ```python
   from candidate.core.ethics.ab_safety_guard import get_safety_guard
   safety_guard = get_safety_guard()
   safety_guard.reset_rollback(operator_id="your_lambda_id")
   ```

### 3. Performance Degradation

**When**: P99 latency > 20ms or P95 > 10ms

**Investigation**:
```bash
# Check tag enrichment bottlenecks
grep "enrichment.*[5-9][0-9]ms\|enrichment.*[1-9][0-9][0-9]ms" /var/log/guardian/safety_tags.log

# Review cache hit rates
curl -s http://localhost:8080/guardian/metrics | grep safety_tags_cache

# Check database connection pool
curl -s http://localhost:8080/guardian/health/db
```

**Mitigation**:
- Scale tag enricher instances
- Increase cache size/TTL
- Review complex regex patterns in detectors

### 4. High False Positive Rate

**When**: False positive rate > 5% on validation set

**Response**:
1. **Immediate**: Adjust detector confidence thresholds
2. **Short-term**: Add exclusion patterns for known false positives
3. **Long-term**: Retrain/tune detection algorithms

**Example Confidence Adjustment**:
```python
# In safety_tags.py PIIDetector.detect()
if confidence > 0.85:  # Raised from 0.7 to reduce FP
    return SafetyTag(...)
```

## Monitoring Playbooks

### High Error Rate Alert

**Alert**: `guardian_errors_total > 10/min`

**Runbook**:
1. Check Guardian service logs: `kubectl logs -f deployment/guardian-service`
2. Verify database connectivity: `curl -s http://guardian:8080/health/db`
3. Check ethics DSL compilation errors: `grep -i "dsl.*error" /var/log/guardian/*.log`
4. If ethics DSL issues: Validate rule syntax in safety_tag_rules.yaml

### Tag Detection Miss Rate High

**Alert**: `tag_miss_rate > 1% on golden set`

**Runbook**:
1. Run golden test suite: `LUKHAS_EVASION_TESTS=1 pytest tests/ethics/test_tags_evasion.py`
2. Identify failing patterns: `python3 scripts/analyze_golden_failures.py`
3. Update detectors for new evasion techniques
4. Deploy with A/B testing: Update candidate lane only initially

### Circuit Breaker Open

**Alert**: `guardian_circuit_state{lane="candidate"} == 1`

**Runbook**:
1. Check recent failures: `curl -s http://localhost:8080/guardian/circuit/status`
2. Review error logs: `grep -A5 -B5 "Circuit failure" /var/log/guardian/*.log`
3. Fix underlying issue (DB timeout, service unavailable, etc.)
4. Circuit auto-recovers after 5 minutes; monitor closely

## Deployment Procedures

### Canary Deployment

1. **Deploy to Candidate Lane Only**
   ```bash
   # Update candidate lane configuration
   kubectl set env deployment/guardian-service LANE=candidate ENFORCE_ETHICS=1

   # Control lane remains unchanged
   kubectl get deployment/guardian-service-control -o yaml | grep ENFORCE_ETHICS
   # Should show: ENFORCE_ETHICS=0 (logging only)
   ```

2. **Monitor Key Metrics** (15 minutes minimum)
   - A/B Denial Delta < 50%
   - P99 latency < 20ms
   - No circuit breaker trips
   - Critical → BLOCK rate > 80%

3. **Graduate to Full Production**
   ```bash
   # Enable for both lanes
   kubectl set env deployment/guardian-service-control ENFORCE_ETHICS=1
   ```

### Rollback Procedure

```bash
# Immediate rollback
kubectl rollout undo deployment/guardian-service

# Or disable enforcement
kubectl set env deployment/guardian-service ENFORCE_ETHICS=0

# Emergency disable all lanes
kubectl exec -it guardian-service -- touch /tmp/guardian_emergency_disable
```

## Operator Probes & Tools

### CLI Tools Available

```bash
# Collapse simulator (deterministic)
make collapse
python3 -m lukhas.tools.collapse_simulator --scenario ethical --seed 42 --json

# Drift dream test (reproducible)
make oneiric-drift-test
python3 -m oneiric_core.tools.drift_dream_test --symbol LOYALTY --user sid-demo --seed 42 --json

# Available scenarios: ethical, resource, compound
# Available symbols: LOYALTY, TRUST, FREEDOM, JUSTICE, WISDOM
```

**Usage**: Both CLIs are deterministic (fixed seed = identical output) and emit telemetry counters for monitoring.

## Log Analysis

### Key Log Patterns

```bash
# Tag detection accuracy
grep "confidence.*0\.[0-4]" /var/log/guardian/safety_tags.log

# Performance issues
grep -E "enrichment.*[1-9][0-9]ms|evaluation.*[2-9][0-9]ms" /var/log/guardian/*.log

# Auto-rollback triggers
grep -i "auto-rollback\|rollback triggered" /var/log/guardian/*.log

# Dual-approval overrides
grep -i "dual.*approval\|override.*approved" /var/log/guardian/*.log

# CLI tool usage
grep -E "collapse_simulator|drift_dream_test" /var/log/guardian/tools.log
```

### Structured Query Examples

```bash
# Recent high-confidence PII detections
jq 'select(.confidence > 0.9 and .tag == "pii")' /var/log/guardian/safety_tags.jsonl | head -10

# Guardian band distributions
jq 'select(.component == "guardian") | .band' /var/log/guardian/*.jsonl | sort | uniq -c

# Failed override attempts
jq 'select(.override_requested == true and .override_approved == false)' /var/log/guardian/*.jsonl
```

## Contact Information

- **On-Call**: `@guardian-oncall` in Slack
- **Team**: `@lukhas-ethics-team`
- **Escalation**: `@lukhas-platform-leads`

**Emergency Contact**: `+1-XXX-XXX-XXXX` (24/7 hotline)

## Related Documentation

- [Safety Tags Architecture](../ethics/tags.md)
- [Guardian Drift Bands Design](../ethics/guardian.md)
- [A/B Testing Safety Guide](../testing/ab_safety.md)
- [Prometheus Metrics Reference](../monitoring/guardian_metrics.md)

---
*Last Updated: 2025-09-19 | Version: 1.0.0*