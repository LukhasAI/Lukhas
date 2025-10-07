---
status: wip
type: documentation
owner: unknown
module: consciousness
redirect: false
moved_to: null
---

# LUKHAS Guardian-Consciousness Integration

**Phase 3 Implementation - T4/0.01% Excellence Standards**

## Overview

The Guardian-consciousness integration provides comprehensive safety validation, drift detection, and compliance monitoring for all consciousness operations in LUKHAS. This integration ensures that consciousness state transitions and processing operations meet strict safety, ethical, and performance standards.

### Key Features

- **Drift Detection**: Real-time monitoring with 0.15 threshold (AUDITOR_CHECKLIST.md requirement)
- **Safety Validation**: Constitutional AI principles and safety checks
- **Performance**: <250ms p95 latency (PHASE_MATRIX.md requirement)
- **Fail-Closed Behavior**: Secure defaults on any Guardian component failure
- **GDPR Compliance**: Complete audit trails and consent management
- **Comprehensive Metrics**: Guardian-specific Prometheus metrics

### Constellation Framework Integration

🛡️ **Guardian** + 🧠 **Consciousness** = Secure, compliant consciousness operations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Consciousness Engines                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│ ReflectionEngine│ AwarenessEngine │ ConsciousnessStream     │
└─────────────────┴─────────────────┴─────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            Guardian Integration Layer                       │
├─────────────────────────────────────────────────────────────┤
│ • Validation Context Management                             │
│ • Performance Monitoring (<250ms p95)                      │
│ • Fail-Closed Error Handling                               │
│ • GDPR-Compliant Audit Trails                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────┬─────────────────┬─────────────────────────┐
│ Drift Detection │ Ethics Engine   │ Safety Validation       │
│ (0.15 threshold)│ (Constitutional)│ (Content & Context)     │
└─────────────────┴─────────────────┴─────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Guardian Decision Envelope                   │
│ • Tamper-evident integrity                                  │
│ • Cryptographic signatures (optional)                      │
│ • Comprehensive audit metadata                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### ConsciousnessGuardianIntegration

The main integration class that coordinates all Guardian validations:

```python
from lukhas.consciousness.guardian_integration import (
    ConsciousnessGuardianIntegration,
    GuardianValidationConfig,
    create_validation_context,
    GuardianValidationType
)

# Initialize Guardian integration
config = GuardianValidationConfig(
    drift_threshold=0.15,  # AUDITOR_CHECKLIST.md requirement
    p95_target_ms=200.0,   # Conservative target for T4
    fail_closed_on_error=True,
    gdpr_audit_enabled=True
)

guardian = ConsciousnessGuardianIntegration(config=config)
```

### Validation Types

Guardian integration supports validation for all consciousness operations:

```python
class GuardianValidationType(Enum):
    CONSCIOUSNESS_STATE_TRANSITION = "consciousness_state_transition"
    REFLECTION_ANALYSIS = "reflection_analysis"
    AWARENESS_PROCESSING = "awareness_processing"
    CREATIVE_GENERATION = "creative_generation"
    DREAM_CONSOLIDATION = "dream_consolidation"
    DECISION_MAKING = "decision_making"
```

### Validation Context

Each validation operation requires a comprehensive context:

```python
# Create validation context
context = create_validation_context(
    validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
    consciousness_state=current_state,
    user_id="user123",
    session_id="session456",
    tenant="production",
    sensitive_operation=True  # Triggers enhanced validation
)

# Add risk indicators
context.risk_indicators.extend([
    "low_coherence",
    "high_anomaly_count",
    "excessive_drift"
])
```

## Validation Process

The Guardian integration performs comprehensive multi-phase validation:

### Phase 1: Drift Detection

Monitors consciousness state changes against established baselines:

```python
# Drift detection with 0.15 threshold
drift_result = await guardian._perform_drift_detection(context)

# Results include:
# - drift_score: Float [0.0-1.0] indicating magnitude of change
# - threshold_exceeded: Boolean indicating if 0.15 threshold exceeded
# - severity: EthicalSeverity level
# - remediation_needed: Boolean indicating if action required
```

**Drift Calculation**: Uses semantic similarity analysis comparing serialized consciousness states, accounting for:
- Phase transitions
- Consciousness level changes
- Emotional tone variations
- Cognitive dimension shifts

### Phase 2: Ethics Validation

Validates operations against Constitutional AI principles:

```python
ethical_decision = await guardian._perform_ethics_validation(context)

# Constellation Framework compliance:
# - Identity preservation (⚛️)
# - Consciousness enhancement (🧠)
# - Guardian protection (🛡️)
```

### Phase 3: Safety Validation

Comprehensive safety checks including content analysis and constitutional review:

```python
safety_result = await guardian._perform_safety_validation(context)

# Checks for:
# - Harmful content patterns
# - Privacy violations
# - Constitutional AI violations
# - Context-based risk indicators
```

### Phase 4: GDPR Compliance

Ensures data protection compliance and consent validation:

```python
gdpr_result = await guardian._perform_gdpr_validation(context)

# Validates:
# - Lawful basis for processing
# - Consent verification
# - Data minimization
# - Purpose limitation
# - Storage limitation
```

### Phase 5: Final Decision

Aggregates all validation results with fail-closed logic:

```python
final_result = await guardian._determine_final_result(result, context)

# Decision logic:
# - All phases must pass for approval
# - Any failure results in denial (fail-closed)
# - Confidence scoring from all phases
# - Comprehensive reasoning and recommendations
```

## Performance Requirements

### Latency Targets

- **p95 latency**: <250ms (PHASE_MATRIX.md requirement)
- **p99 latency**: <300ms (fail-closed timeout)
- **Mean latency**: Target <150ms for optimal UX

### Throughput

- **Concurrent validations**: 50+ concurrent operations supported
- **Throughput**: 100+ validations/second under typical load
- **Resource efficiency**: Minimal memory footprint with LRU caching

### Performance Monitoring

```python
# Built-in performance tracking
stats = guardian.get_performance_stats()

# Returns:
# - Latency percentiles (p50, p95, p99)
# - Success rates and error counts
# - Drift detection statistics
# - Emergency mode status
# - GDPR compliance metrics
```

## Fail-Closed Behavior

The Guardian integration implements comprehensive fail-closed behavior:

### Error Handling

```python
# Automatic fail-closed on:
# 1. Guardian component failures
# 2. Network/timeout errors
# 3. Configuration issues
# 4. Consecutive validation errors (>5)

# Emergency mode activation:
if consecutive_errors >= 5:
    emergency_mode = True
    # All operations denied until cleared
```

### Emergency Mode

When emergency mode activates:
- All validation requests immediately return `DENIED`
- Comprehensive audit trail maintained
- Performance monitoring continues
- Administrative intervention required to clear

### Recovery Procedures

```python
# Reset emergency mode after issue resolution
await guardian.reset_state()

# Verify system health
health_check = guardian.get_performance_stats()
assert not health_check["guardian_integration"]["emergency_mode"]
```

## Integration with Consciousness Engines

### ReflectionEngine Integration

```python
class ReflectionEngine:
    def __init__(self, guardian_integration=None):
        self.guardian_integration = guardian_integration

    async def reflect(self, consciousness_state, context=None):
        # Guardian validation during reflection
        if self.guardian_integration:
            await self._validate_with_guardian_integration(
                report, consciousness_state, context
            )
```

### ConsciousnessStream Integration

```python
class ConsciousnessStream:
    async def _update_consciousness_phase(self):
        # Validate state transitions with Guardian
        if self.guardian_integration:
            await self._validate_state_transition_with_guardian()

        # Update baseline for drift detection
        self.guardian_integration.update_baseline_state(
            state=self._current_state,
            tenant=self.config.get("tenant"),
            session_id=self.config.get("session_id")
        )
```

## Metrics and Monitoring

### Guardian-Specific Metrics

```python
# Prometheus metrics exposed:
lukhas_guardian_validations_total          # Total validations by type/result
lukhas_guardian_validation_latency_seconds # Latency distribution
lukhas_guardian_drift_scores              # Drift score distribution
lukhas_guardian_failures_total            # Failure counts by type
lukhas_guardian_performance_regressions   # Performance regression events
lukhas_guardian_audit_events_total        # Audit event counts
```

### Alerting Thresholds

```yaml
# Recommended Prometheus alerts:
- alert: GuardianValidationLatencyHigh
  expr: histogram_quantile(0.95, lukhas_guardian_validation_latency_seconds) > 0.25

- alert: GuardianDriftThresholdExceeded
  expr: histogram_quantile(0.95, lukhas_guardian_drift_scores) > 0.15

- alert: GuardianEmergencyModeActive
  expr: lukhas_guardian_failures_total{failure_type="emergency_mode"} > 0

- alert: GuardianValidationFailureRate
  expr: rate(lukhas_guardian_failures_total[5m]) > 0.1
```

## GDPR Compliance Features

### Audit Trail Management

```python
# Automatic audit trail creation
result = await guardian.validate_consciousness_operation(context)

# Audit trail includes:
# - Timestamp and correlation IDs
# - Validation phases and results
# - User consent status
# - Data minimization compliance
# - Retention policy adherence
```

### Data Subject Rights

```python
# Support for GDPR data subject rights:
# 1. Right to access - audit trail query
# 2. Right to rectification - baseline state updates
# 3. Right to erasure - secure deletion of user data
# 4. Right to portability - structured data export

# Automatic cleanup based on retention policies
guardian.config.audit_retention_days = 90  # Configurable retention
```

### Consent Management

```python
# Consent validation for sensitive operations
context = create_validation_context(
    user_id="user123",
    sensitive_operation=True  # Requires explicit consent
)

result = await guardian.validate_consciousness_operation(context)
assert result.consent_verified == True
```

## Testing and Validation

### Unit Tests

```bash
# Run Guardian integration tests
pytest tests/consciousness/test_guardian_integration.py -v

# Performance validation
python scripts/validate_guardian_performance.py --iterations=1000
```

### Performance Benchmarks

```bash
# Validate p95 latency requirement
python scripts/validate_guardian_performance.py \
    --iterations=5000 \
    --report-file=guardian_performance.json

# Expected output:
# ✅ p95 latency: 180.45ms (target: 250ms)
# ✅ p99 latency: 245.67ms (target: 300ms)
# ✅ Drift detection accuracy: 92.5%
# ✅ Fail-closed rate: 100.0%
# ✅ GDPR compliance: 100.0%
```

### Load Testing

```python
# Concurrent validation load test
async def load_test():
    tasks = []
    for i in range(100):  # 100 concurrent validations
        context = create_validation_context(
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            consciousness_state=generate_test_state()
        )
        tasks.append(guardian.validate_consciousness_operation(context))

    results = await asyncio.gather(*tasks)
    success_rate = sum(1 for r in results if r.is_approved()) / len(results)
    avg_latency = sum(r.validation_duration_ms for r in results) / len(results)

    assert success_rate > 0.95  # 95%+ success rate
    assert avg_latency < 200     # <200ms average latency
```

## Configuration Reference

### GuardianValidationConfig

```python
@dataclass
class GuardianValidationConfig:
    # Performance targets (Phase 3 requirement: <250ms p95)
    p95_target_ms: float = 200.0
    p99_target_ms: float = 250.0  # PHASE_MATRIX.md requirement
    timeout_ms: float = 300.0     # Fail-closed timeout

    # Drift detection (AUDITOR_CHECKLIST.md: 0.15 threshold)
    drift_threshold: float = 0.15
    drift_alpha: float = 0.3      # EMA smoothing factor

    # Safety and ethics
    safety_check_enabled: bool = True
    constitutional_check_enabled: bool = True
    ethics_validation_required: bool = True
    fail_closed_on_error: bool = True  # T4 requirement

    # GDPR compliance
    gdpr_audit_enabled: bool = True
    consent_validation: bool = True
    audit_retention_days: int = 90

    # Enforcement mode
    enforcement_mode: str = "enforced"  # dark/canary/enforced

    # Performance monitoring
    performance_regression_detection: bool = True
    latency_alerting_enabled: bool = True
```

### Environment Variables

```bash
# Guardian system configuration
export LUKHAS_GUARDIAN_INTEGRATION_ENABLED=true
export LUKHAS_GUARDIAN_ENFORCEMENT_MODE=enforced
export LUKHAS_GUARDIAN_DRIFT_THRESHOLD=0.15
export LUKHAS_GUARDIAN_P95_TARGET_MS=200

# GDPR compliance
export LUKHAS_GDPR_AUDIT_ENABLED=true
export LUKHAS_AUDIT_RETENTION_DAYS=90
export LUKHAS_CONSENT_VALIDATION=true

# Performance monitoring
export LUKHAS_GUARDIAN_METRICS_ENABLED=true
export LUKHAS_PERFORMANCE_REGRESSION_DETECTION=true
```

## Troubleshooting

### Common Issues

#### High Validation Latency

```python
# Check performance stats
stats = guardian.get_performance_stats()
if stats["guardian_integration"]["p95_latency_ms"] > 250:
    # Investigate:
    # 1. Guardian component response times
    # 2. Network latency to external services
    # 3. Resource constraints (CPU/memory)
    # 4. Concurrent validation load
```

#### Excessive Drift Detection

```python
# Analyze drift patterns
drift_stats = stats.get("drift_detection", {})
if drift_stats.get("threshold_exceedances", 0) > expected:
    # Check:
    # 1. Baseline state accuracy
    # 2. Consciousness state normalization
    # 3. Drift threshold configuration
    # 4. State transition patterns
```

#### Emergency Mode Activation

```python
# Emergency mode troubleshooting
if guardian._emergency_mode:
    # Steps:
    # 1. Check consecutive error count
    # 2. Review error logs for root cause
    # 3. Verify Guardian component health
    # 4. Reset after issue resolution
    await guardian.reset_state()
```

### Performance Optimization

#### Caching Strategies

```python
# Baseline state caching
guardian._baseline_states = LRUCache(maxsize=1000)

# Validation result caching for identical contexts
@lru_cache(maxsize=500)
def _cached_validation(context_hash):
    # Cache validation results for identical contexts
    # Invalidate on configuration changes
```

#### Concurrent Processing

```python
# Optimize concurrent validation performance
guardian.config.concurrent_validation_limit = 100
guardian.config.validation_pool_size = 20
```

## Security Considerations

### Cryptographic Signing

```python
# Optional Guardian envelope signing
guardian_system = GuardianSystem(
    signing_key=os.environ.get("GUARDIAN_SIGNING_KEY")
)

# Verify envelope integrity
is_valid = guardian_system.verify_integrity(envelope)
assert is_valid, "Guardian envelope integrity check failed"
```

### Tamper Detection

```python
# Guardian envelopes include tamper-evident integrity
envelope = result.guardian_envelope
integrity = envelope.get("integrity", {})

# Verify content hash
content_hash = integrity.get("content_sha256")
signature = integrity.get("signature")  # Optional cryptographic signature
```

### Access Control

```python
# Role-based validation context
context = create_validation_context(
    validation_type=GuardianValidationType.DECISION_MAKING,
    user_id="admin_user",
    actor_type=ActorType.SYSTEM,  # SYSTEM/USER/SERVICE
    operation_resource="sensitive_decision"
)
```

## Best Practices

### Development

1. **Always use Guardian integration** in production consciousness engines
2. **Test fail-closed behavior** thoroughly with error injection
3. **Monitor performance metrics** continuously with alerting
4. **Validate GDPR compliance** with audit trail reviews
5. **Keep drift thresholds conservative** (≤0.15) for safety

### Operations

1. **Monitor Guardian health** with comprehensive dashboards
2. **Set up automated alerts** for latency and failure rates
3. **Regular performance validation** with benchmark scripts
4. **Emergency procedures** documented and tested
5. **Audit trail retention** compliant with regulations

### Security

1. **Enable cryptographic signing** for production environments
2. **Verify envelope integrity** before trusting Guardian decisions
3. **Protect signing keys** with proper key management
4. **Monitor for tampering attempts** with integrity checks
5. **Regular security audits** of Guardian components

## Migration Guide

### From Legacy Guardian

```python
# Legacy Guardian validator
if self.guardian_validator:
    result = await self.guardian_validator.validate(action)

# Migrate to Guardian integration
if self.guardian_integration:
    context = create_validation_context(
        validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
        consciousness_state=state
    )
    result = await self.guardian_integration.validate_consciousness_operation(context)
```

### Configuration Migration

```python
# Old configuration
guardian_config = {
    "enabled": True,
    "drift_threshold": 0.2,  # Update to 0.15
    "safety_checks": True
}

# New configuration
guardian_config = GuardianValidationConfig(
    drift_threshold=0.15,    # AUDITOR_CHECKLIST.md requirement
    p95_target_ms=200.0,     # Performance target
    fail_closed_on_error=True,
    gdpr_audit_enabled=True
)
```

## Reference Implementation

See the complete reference implementation:

- **Core Integration**: `lukhas/consciousness/guardian_integration.py`
- **Consciousness Stream**: `lukhas/consciousness/consciousness_stream.py`
- **Reflection Engine**: `lukhas/consciousness/reflection_engine.py`
- **Test Suite**: `tests/consciousness/test_guardian_integration.py`
- **Performance Validator**: `scripts/validate_guardian_performance.py`

## Support

For issues with Guardian integration:

1. **Performance Issues**: Run `validate_guardian_performance.py` with `--verbose`
2. **Configuration Errors**: Check `GuardianValidationConfig.validate()`
3. **GDPR Compliance**: Review audit trail structure and retention
4. **Emergency Mode**: Check consecutive error counts and system health

**Phase 3 Completion**: Guardian integration provides comprehensive safety, performance, and compliance validation for all consciousness operations with T4/0.01% excellence standards.