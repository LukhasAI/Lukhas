---
status: wip
type: documentation
owner: unknown
module: matriz
redirect: false
moved_to: null
---

# MATRIZ Lane Policy — Production Safety Framework

## Lane Hierarchy & Governance

### Lane Definitions
- **Candidate**: Experimental modules with relaxed requirements
- **Integration**: Stable APIs with enforced SLOs and shadow traffic validation
- **Production**: Live traffic with canary deployment and automatic rollback

### Cross-Lane Import Policy (Strictly Enforced)
```
production ←─ integration ←─ candidate
     ↑            ↑           ↑
  blocked      blocked    allowed
```

**Rule**: Modules CANNOT import from higher stability lanes
- `candidate` → `integration`: ❌ BLOCKED
- `candidate` → `production`: ❌ BLOCKED
- `integration` → `production`: ❌ BLOCKED

**Enforcement**: `import-linter` runs on every PR and blocks violating imports

## Performance Budgets (Hard Gates)

### T4/0.01% Excellence Standards

| Lane | Tick p95 | Reflect p95 | Decide p95 | E2E p95 | Success Rate |
|------|----------|-------------|------------|---------|--------------|
| Candidate | 200ms | 20ms | 100ms | 500ms | 95.0% |
| Integration | 100ms | 10ms | 50ms | 250ms | 99.5% |
| Production | 100ms | 10ms | 50ms | 250ms | 99.9% |

### Burn Rate Thresholds (Automatic Rollback)
- **1-hour window**: 4x baseline error rate
- **6-hour window**: 2x baseline error rate
- **Rollback target**: <30 seconds from trigger to completion

## Guardian Enforcement Levels

### Candidate Lane
- **Mode**: Advisory warnings only
- **Fail-closed**: Disabled (graceful degradation allowed)
- **Kill-switch**: Not available
- **Validation**: Basic contract validation

### Integration Lane
- **Mode**: Enforced with blocking
- **Fail-closed**: Enabled (<250ms activation)
- **Kill-switch**: Available for emergency use
- **Validation**: Comprehensive contract validation + chaos testing

### Production Lane
- **Mode**: Strict enforcement with immediate blocking
- **Fail-closed**: Always enabled (<100ms activation)
- **Kill-switch**: Immediately available with audit trail
- **Validation**: Full contract validation + continuous chaos + audit logging

## Promotion Gates (Lane Advancement)

### Candidate → Integration
**Required Gates (All Must Pass):**
- [ ] Unit test coverage >90%
- [ ] Integration test suite passing
- [ ] Import hygiene validation (no upward imports)
- [ ] Basic security scan (bandit, semgrep)
- [ ] Performance baseline established

**Evidence Artifacts:**
- `artifacts/{module}_unit_test_results.json`
- `artifacts/{module}_integration_test_results.json`
- `artifacts/{module}_security_scan_results.json`
- `artifacts/{module}_performance_baseline.json`

### Integration → Production
**Required Gates (All Must Pass):**
- [ ] All candidate→integration gates
- [ ] E2E performance within SLO budgets
- [ ] Schema evolution guard validation
- [ ] Chaos engineering fail-closed proof
- [ ] Guardian enforcement validation
- [ ] Telemetry contracts compliance
- [ ] Load testing at 2x expected capacity
- [ ] GDPR compliance validation
- [ ] 12-hour shadow traffic validation
- [ ] Canary deployment simulation

**Evidence Artifacts:**
- `artifacts/{module}_e2e_performance_bootstrap.json`
- `artifacts/{module}_schema_evolution_validation.json`
- `artifacts/{module}_chaos_resilience_validation.json`
- `artifacts/{module}_guardian_enforcement_validation.json`
- `artifacts/{module}_telemetry_contracts_validation.json`
- `artifacts/{module}_load_test_results.json`
- `artifacts/{module}_gdpr_compliance_validation.json`
- `artifacts/{module}_shadow_traffic_validation.json`
- `artifacts/{module}_canary_simulation_results.json`

## Telemetry Contract Policy

### Allowed Label Dimensions
```yaml
# ✅ ALLOWED - Static, bounded cardinality
labels:
  lane: [candidate, integration, production]
  component: [guardian, memory, consciousness, identity, orchestrator]
  operation: [tick, reflect, decide, validate, rollback]
  status: [success, error, timeout]
  error_type: [validation, network, timeout, guardian]
```

### Forbidden Label Patterns
```yaml
# ❌ FORBIDDEN - Dynamic, unbounded cardinality
labels:
  correlation_id: "uuid-1234-5678"    # Use span attributes instead
  user_id: "user-abc123"             # Use span attributes instead
  timestamp: "2024-12-10T15:30:00Z"  # Use span attributes instead
  request_id: "req-xyz789"           # Use span attributes instead
  session_id: "sess-def456"          # Use span attributes instead
```

**Enforcement**: `scripts/validate_dynamic_id_hardening.py` blocks all dynamic IDs

## Schema Evolution Protection

### Breaking Changes (Absolutely Forbidden)
- Removing required fields
- Changing field types incompatibly
- Tightening validation constraints
- Removing enum values
- Changing API endpoints or parameters

### Safe Changes (Allowed)
- Adding optional fields with defaults
- Relaxing validation constraints
- Adding new enum values
- Adding new API endpoints
- Adding backward-compatible parameters

### Validation Process
1. **Golden snapshot**: Store schema snapshot in `tests/{module}/snapshots/`
2. **Drift detection**: Automated comparison on every commit
3. **Breaking change analysis**: Semantic analysis of schema differences
4. **Deployment blocking**: CI fails if breaking changes detected

## Canary Deployment Protocol

### Canary Ramp Schedule
```
5% → 10% → 15% → 25% → 50% → 100%
 4h   4h    4h    8h    12h   (promotion complete)
```

### Automatic Rollback Triggers
- **Error rate** > 0.2% (vs baseline)
- **Latency p95** > 1.2x baseline
- **Success rate** < 99.8%
- **Burn rate** > thresholds (4x/1h, 2x/6h)

### Manual Override Authority
- **Production Lead**: Can force rollback at any stage
- **Security Officer**: Can emergency kill-switch entire system
- **SRE On-Call**: Can pause canary progression for investigation

## Compliance & Security Requirements

### Security Scanning (All Lanes)
- **SAST**: bandit (Python security), semgrep (custom rules)
- **Dependency**: pip-audit with strict mode
- **Supply Chain**: SHA-pinned GitHub Actions, signed commits
- **Secrets**: No hardcoded credentials, use secure key management

### GDPR Compliance (Integration+ Lanes)
- **Data Processing**: All user data access logged with audit trail
- **Right to Erasure**: Tombstone processing within 500ms
- **Data Minimization**: Only collect necessary data for functionality
- **Consent Management**: Explicit consent tracking with withdraw capability

### Audit Trail Requirements (Production Lane)
- **All State Changes**: Logged with correlation ID and timestamp
- **User Actions**: Complete audit trail with before/after state
- **System Events**: Guardian activations, rollbacks, kill-switch usage
- **Evidence Retention**: 5 years for compliance audits

## Emergency Procedures

### Guardian Activation (Automatic)
1. **Detection**: Anomaly detection triggers Guardian evaluation
2. **Fail-Closed**: System immediately stops processing new requests
3. **Rollback**: Automatic transaction rollback within 1 second
4. **Recovery**: Health check validation before resuming operations

### Kill-Switch Protocol (Manual)
1. **Authorization**: Two-person approval (Production Lead + SRE)
2. **Activation**: Immediate system shutdown across all lanes
3. **Notification**: Automatic alerts to all stakeholders
4. **Recovery**: Coordinated restart with full validation

### Incident Response
- **P0 (Critical)**: <5 minute response, immediate Guardian activation
- **P1 (High)**: <15 minute response, potential service degradation
- **P2 (Medium)**: <1 hour response, monitoring and investigation
- **P3 (Low)**: <24 hour response, planned maintenance window