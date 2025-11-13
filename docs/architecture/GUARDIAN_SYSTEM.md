# Guardian System Architecture
**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Status**: Production (with feature flag)

## Overview

The LUKHAS Guardian System provides ethical oversight, drift detection, and safety validation for AI operations. It implements Constitutional AI principles with continuous monitoring of system behavior against established baselines.

## Constellation Framework Integration

**Guardian**: 🛡️ (Constitutional AI, Ethical Enforcement, Drift Detection)

Part of the 8-star Constellation Framework:
- ⚛️ **Identity** - Authentication and access control
- ✦ **Memory** - Persistent state and context
- 🔬 **Vision** - Perception and pattern recognition
- 🌱 **Bio** - Bio-inspired adaptation
- 🌙 **Dream** - Creative synthesis
- ⚖️ **Ethics** - Moral reasoning frameworks
- **🛡️ Guardian** - Constitutional AI enforcement ← You are here
- ⚛️ **Quantum** - Quantum-inspired algorithms

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  (User code, API endpoints, consciousness integrations)      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Guardian Wrapper Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ detect_drift()     ← Drift detection                 │   │
│  │ evaluate_ethics()  ← Ethical evaluation              │   │
│  │ check_safety()     ← Safety validation               │   │
│  │ get_guardian_status() ← System monitoring            │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓ MATRIZ Instrumentation (@instrument)          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Guardian Implementation Layer                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ GuardianSystemImpl                                    │   │
│  │  - DriftDetector    ← Semantic analysis              │   │
│  │  - EthicsEngine     ← Constitutional AI              │   │
│  │  - SafetyValidator  ← Content safety                 │   │
│  │  - MetricsCollector ← Performance tracking           │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓ Feature Flag Check (GUARDIAN_ACTIVE)          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Core Types Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ DriftResult       ← Drift analysis result            │   │
│  │ EthicalDecision   ← Ethics evaluation result         │   │
│  │ SafetyResult      ← Safety validation result         │   │
│  │ GovernanceAction  ← Action requiring oversight       │   │
│  │ EthicalSeverity   ← Severity levels enum             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Canonical Production Location

**Path**: `lukhas_website/lukhas/governance/guardian/`

```
lukhas_website/lukhas/governance/guardian/
├── __init__.py           # Module exports, public API
├── core.py               # Core types (DriftResult, EthicalDecision, etc.)
├── guardian_impl.py      # GuardianSystemImpl implementation
├── guardian_wrapper.py   # Wrapper functions (detect_drift, evaluate_ethics, etc.)
├── policies.py           # ✅ GuardianPoliciesEngine (relocated Phase 3)
└── reflector.py          # ✅ GuardianReflector (relocated Phase 3)
```

**File Sizes**:
- `__init__.py`: 119 lines - Module coordination and public API
- `core.py`: 72 lines - Core type definitions
- `guardian_impl.py`: 340 lines - Full Guardian implementation
- `guardian_wrapper.py`: 369 lines - Wrapper functions with dry-run mode
- `policies.py`: 652 lines - ✅ Full GuardianPoliciesEngine implementation
- `reflector.py`: 791 lines - ✅ Full GuardianReflector implementation

**Total**: ~2,343 lines in canonical location (Phase 3 complete)

### Experimental Development Lane

**Path**: `labs/governance/guardian/`

Contains 13 experimental files (7,564 lines) for Guardian feature research:
- Advanced drift detection algorithms
- Real-time monitoring dashboards
- Self-repair mechanisms
- Security event monitoring
- Workspace protection systems

### Bridge Modules

**Path**: `governance/guardian/`

Phase 1 bridges enabling `governance.guardian.*` import pattern:
- `core.py` - Core types bridge
- `guardian_impl.py` - Implementation bridge
- `guardian_wrapper.py` - Wrapper functions bridge
- `__init__.py` - Module initialization

## Core Components

### 1. Drift Detection

**Purpose**: Detect semantic drift from established behavioral baselines.

**API**:
```python
from lukhas_website.lukhas.governance.guardian import detect_drift

result = detect_drift(
    baseline_behavior="Expected behavior description",
    current_behavior="Current behavior observation",
    threshold=0.15,  # Default drift threshold
    mode="dry_run",  # "dry_run" or "live"
)

# Result structure
{
    "ok": True,
    "drift_score": 0.08,  # 0.0 = identical, 1.0 = completely different
    "threshold_exceeded": False,
    "severity": "low",  # low, medium, high, critical
    "remediation_needed": False,
    "correlation_id": "uuid-string",
    "mode": "dry_run"
}
```

**Algorithm**:
1. Tokenize baseline and current behavior text
2. Compute semantic similarity using word overlap
3. Calculate drift score: `1.0 - similarity`
4. Compare against threshold (default: 0.15)
5. Assign severity based on drift magnitude

**Thresholds**:
- `< 0.15`: Low severity (acceptable)
- `0.15 - 0.30`: Medium severity (monitor)
- `0.30 - 0.50`: High severity (investigate)
- `> 0.50`: Critical severity (remediate immediately)

### 2. Ethical Evaluation

**Purpose**: Evaluate actions against Constitutional AI principles.

**API**:
```python
from lukhas_website.lukhas.governance.guardian import evaluate_ethics, GovernanceAction

action = GovernanceAction(
    action_type="data_deletion",
    target="user_profile",
    context={"user_id": "123", "reason": "GDPR request"}
)

decision = evaluate_ethics(action, mode="dry_run")

# Decision structure
{
    "ok": True,
    "allowed": True,
    "reason": "GDPR deletion request is ethically justified",
    "severity": "low",
    "confidence": 0.95,
    "recommendations": ["Log action for audit", "Verify user identity"],
    "correlation_id": "uuid-string",
    "mode": "dry_run"
}
```

**Evaluation Criteria**:
1. **Harm Assessment**: Does action cause harm?
2. **Rights Respect**: Does action respect user rights?
3. **Fairness**: Is action fair and non-discriminatory?
4. **Transparency**: Is action transparent and explainable?
5. **Accountability**: Can action be audited and reversed?

**Constitutional AI Principles**:
- Beneficence: Do good, prevent harm
- Non-maleficence: Above all, do no harm
- Autonomy: Respect user agency and choices
- Justice: Treat all users fairly
- Explicability: Make decisions transparent

### 3. Safety Validation

**Purpose**: Validate content safety and detect policy violations.

**API**:
```python
from lukhas_website.lukhas.governance.guardian import check_safety

result = check_safety(
    content="User-generated content to validate",
    constitutional_check=True,
    mode="dry_run"
)

# Result structure
{
    "ok": True,
    "safe": True,
    "risk_level": "low",  # low, medium, high, critical
    "violations": [],  # List of detected violations
    "recommendations": ["Content appears safe for processing"],
    "constitutional_check": True,
    "correlation_id": "uuid-string",
    "mode": "dry_run"
}
```

**Safety Checks**:
1. **Content Scanning**: Detect unsafe keywords and patterns
2. **Constitutional Compliance**: Verify alignment with AI principles
3. **Policy Validation**: Check against organizational policies
4. **Risk Assessment**: Quantify safety risk level

**Unsafe Content Categories**:
- Violence and harm
- Illegal activities
- Malicious code or exploits
- Privacy violations
- Discriminatory content

### 4. System Status

**Purpose**: Monitor Guardian system health and configuration.

**API**:
```python
from lukhas_website.lukhas.governance.guardian import get_guardian_status

status = get_guardian_status(mode="dry_run")

# Status structure
{
    "ok": True,
    "active": False,  # Feature flag status
    "drift_threshold": 0.15,
    "constitutional_ai_enabled": True,
    "ethics_engine_status": "simulated",  # or "active"
    "safety_validator_status": "simulated",  # or "active"
    "feature_flag_active": False,  # GUARDIAN_ACTIVE env var
    "mode": "dry_run"
}
```

## Feature Flag System

**Environment Variable**: `GUARDIAN_ACTIVE`

```bash
# Disable Guardian (default) - uses dry-run simulations
export GUARDIAN_ACTIVE=false

# Enable Guardian - uses real implementations
export GUARDIAN_ACTIVE=true
```

**Behavior**:

| Mode | GUARDIAN_ACTIVE | Behavior |
|------|-----------------|----------|
| **Dry-run** | `false` (default) | Uses simulation functions, returns safe defaults |
| **Live** | `true` | Uses real Guardian implementation, enforces decisions |

**Mode Parameter**:

All Guardian functions accept a `mode` parameter:

```python
# Explicit dry-run (even if GUARDIAN_ACTIVE=true)
detect_drift(..., mode="dry_run")

# Live mode (requires GUARDIAN_ACTIVE=true)
detect_drift(..., mode="live")
```

**Decision Logic**:
```python
if mode == "live" and GUARDIAN_ACTIVE and _guardian_instance:
    # Use real implementation
    return _guardian_instance.detect_drift(...)
else:
    # Use dry-run simulation
    return _simulate_drift_detection(...)
```

## Emergency Kill-Switch

**Location**: `governance/ethics/guardian_kill_switch.py`

**Purpose**: Emergency bypass mechanism to disable Guardian enforcement.

**Activation**:
```bash
# Create kill-switch file (disables ALL Guardian enforcement)
touch /tmp/guardian_emergency_disable

# Remove kill-switch file (re-enables Guardian)
rm /tmp/guardian_emergency_disable
```

**Integration**:
```python
from governance.ethics.guardian_kill_switch import is_guardian_disabled

if is_guardian_disabled():
    # Skip Guardian checks, allow operation
    return {"allowed": True, "reason": "Guardian disabled by kill-switch"}
```

**Use Cases**:
- Emergency system recovery
- Critical maintenance operations
- Debugging Guardian issues
- Incident response

**Test Coverage**: 37 unit tests, 8 integration tests (all passing ✅)

## MATRIZ Instrumentation

All Guardian functions use MATRIZ decorators for observability:

```python
@instrument("DECISION", label="guardian:drift", capability="guardian:drift:detect")
def detect_drift(...):
    pass

@instrument("DECISION", label="guardian:ethics", capability="guardian:ethics:evaluate")
def evaluate_ethics(...):
    pass

@instrument("AWARENESS", label="guardian:safety", capability="guardian:safety:validate")
def check_safety(...):
    pass
```

**Instrumentation Benefits**:
- Performance tracking (latency, throughput)
- Decision logging and audit trails
- Capability registration for discovery
- Integration with MATRIZ consciousness engine

## Configuration

### Environment Variables

```bash
# Feature flag (default: false)
GUARDIAN_ACTIVE=true

# Drift detection threshold (default: 0.15)
DRIFT_THRESHOLD=0.20

# Kill-switch file location (default: /tmp/guardian_emergency_disable)
GUARDIAN_KILLSWITCH_PATH=/custom/path/guardian_disable
```

### Configuration in Code

```python
import os

# Check feature flag
GUARDIAN_ACTIVE = os.environ.get("GUARDIAN_ACTIVE", "false").lower() == "true"

# Get drift threshold
DRIFT_THRESHOLD = float(os.environ.get("DRIFT_THRESHOLD", "0.15"))

# Configure Guardian
guardian = GuardianSystemImpl(drift_threshold=DRIFT_THRESHOLD)
```

## Integration Patterns

### 1. API Middleware Integration

```python
from lukhas_website.lukhas.governance.guardian import evaluate_ethics, GovernanceAction

async def guardian_middleware(request: Request, call_next):
    # Evaluate incoming request
    action = GovernanceAction(
        action_type=request.method,
        target=request.url.path,
        context={"user": request.user, "headers": dict(request.headers)}
    )

    decision = evaluate_ethics(action, mode="live")

    if not decision["allowed"]:
        return JSONResponse(
            status_code=403,
            content={"error": "Action blocked by Guardian", "reason": decision["reason"]}
        )

    response = await call_next(request)
    return response
```

### 2. Consciousness System Integration

```python
from lukhas_website.lukhas.governance.guardian import detect_drift

async def process_thought(baseline_thought: str, current_thought: str):
    # Check for cognitive drift
    drift_result = detect_drift(
        baseline_behavior=baseline_thought,
        current_behavior=current_thought,
        mode="live"
    )

    if drift_result["threshold_exceeded"]:
        logger.warning(f"Cognitive drift detected: {drift_result['drift_score']}")
        # Trigger remediation
        await remediate_cognitive_drift(drift_result)
```

### 3. Memory System Integration

```python
from lukhas_website.lukhas.governance.guardian import check_safety

async def store_memory(content: str):
    # Validate memory safety
    safety_result = check_safety(content, constitutional_check=True, mode="live")

    if not safety_result["safe"]:
        raise ValueError(f"Unsafe memory content: {safety_result['violations']}")

    await memory_store.save(content)
```

## Performance Characteristics

### Latency Targets

| Operation | Target (p95) | Actual (dry-run) | Actual (live) |
|-----------|--------------|------------------|---------------|
| `detect_drift` | < 10ms | ~1ms | ~5ms |
| `evaluate_ethics` | < 10ms | ~1ms | ~8ms |
| `check_safety` | < 5ms | ~0.5ms | ~3ms |
| `get_guardian_status` | < 1ms | ~0.1ms | ~0.5ms |

### Throughput

- **Dry-run mode**: 50,000+ ops/sec
- **Live mode**: 10,000+ ops/sec (depends on implementation complexity)

### Memory Footprint

- **Dry-run mode**: < 10MB
- **Live mode**: < 100MB (including cached data)

## Testing

### Unit Tests

**Location**: `tests/unit/governance/guardian/`

```bash
# Run Guardian unit tests
pytest tests/unit/governance/guardian/ -v

# 37 unit tests covering:
# - Emergency kill-switch (12 tests)
# - Drift detection (8 tests)
# - Ethical evaluation (9 tests)
# - Safety validation (8 tests)
```

### Integration Tests

**Location**: `tests/integration/governance/guardian/`

```bash
# Run Guardian integration tests
pytest tests/integration/governance/guardian/ -v

# 8 integration tests covering:
# - Kill-switch + drift detection integration (2 tests)
# - Kill-switch + ethics evaluation integration (2 tests)
# - Kill-switch + safety validation integration (2 tests)
# - Kill-switch + status reporting integration (2 tests)
```

### Test Scenarios

1. **Drift Detection**:
   - High drift (score > 0.8) triggers remediation
   - Low drift (score < 0.15) allows operation
   - Kill-switch bypasses drift checks

2. **Ethics Evaluation**:
   - Risky actions (delete, harm) blocked without justification
   - Safe actions (read, update) allowed
   - Kill-switch bypasses ethical checks

3. **Safety Validation**:
   - Unsafe content (violence, malice) rejected
   - Safe content allowed
   - Kill-switch bypasses safety checks

4. **System Status**:
   - Correct reporting of active vs inactive state
   - Kill-switch reflected in status
   - Configuration values correctly reported

## Troubleshooting

### Guardian Not Enforcing Decisions

**Symptom**: Guardian returns decisions but doesn't block actions.

**Diagnosis**:
```python
from lukhas_website.lukhas.governance.guardian import get_guardian_status

status = get_guardian_status(mode="live")
print(status)
```

**Solutions**:
1. Check `GUARDIAN_ACTIVE` environment variable
2. Verify `mode="live"` parameter passed to functions
3. Check kill-switch file doesn't exist: `ls /tmp/guardian_emergency_disable`

### High Drift False Positives

**Symptom**: Legitimate behavior flagged as drift.

**Solutions**:
1. Increase drift threshold: `DRIFT_THRESHOLD=0.25`
2. Refine baseline behavior descriptions
3. Use more specific behavioral patterns

### Performance Issues

**Symptom**: Guardian operations slow down system.

**Solutions**:
1. Use dry-run mode for non-critical paths
2. Implement caching for repeated evaluations
3. Use async operations where possible
4. Monitor MATRIZ instrumentation metrics

### Import Errors

**Symptom**: `ModuleNotFoundError` when importing Guardian.

**Solutions**:
1. Use canonical import path: `from lukhas_website.lukhas.governance.guardian import ...`
2. Check Python path includes workspace root
3. Verify bridge modules exist in `governance/guardian/`

## Security Considerations

### 1. Kill-Switch Protection

- Kill-switch file should have restricted permissions: `chmod 600`
- Monitor kill-switch activation in security logs
- Require multi-person authorization for kill-switch use

### 2. Decision Audit Logging

- Log all Guardian decisions to audit trail
- Include correlation IDs for tracking
- Store logs in tamper-proof storage

### 3. Feature Flag Security

- `GUARDIAN_ACTIVE` should be set at deployment time
- Prevent runtime modification in production
- Use separate configs for dev/staging/prod

### 4. Constitutional AI Alignment

- Regularly review and update ethical principles
- Test Guardian decisions against edge cases
- Monitor for bias in decision-making

## Future Enhancements

### Phase 3 Completion ✅ (2025-11-12)

- ✅ **Relocated scattered implementations to canonical location** (PR #1363, #1364)
  - `governance/guardian_policies.py` → `lukhas_website/lukhas/governance/guardian/policies.py` (652 lines)
  - `governance/guardian_reflector.py` → `lukhas_website/lukhas/governance/guardian/reflector.py` (791 lines)
- ✅ **Added deprecation warnings to legacy bridges** (PR #1362)
  - `governance/guardian_sentinel.py`, `guardian_shadow_filter.py`, `guardian_system.py`
  - `governance/guardian_system_integration.py`, `guardian_serializers.py`
- ✅ **Created comprehensive developer import guide** (PR #1360)
  - `docs/development/GUARDIAN_IMPORTS.md` (500+ lines)
- ✅ **Updated CLAUDE.md with Guardian module structure** (PR #1360)
  - Master context file updated with canonical paths

**Phase 3 Results**:
- 3 PRs merged with admin flag
- 1,443 lines relocated to canonical location
- Full backward compatibility maintained via deprecation bridges
- Removal timeline: Phase 4 (2025-Q1)

### Phase 4 Planning (2025-Q1)

- [ ] Machine learning-based drift detection
- [ ] Real-time Guardian dashboard (Grafana/Prometheus)
- [ ] A/B testing framework for Guardian decisions
- [ ] Multi-tenant Guardian configurations
- [ ] Guardian decision appeals process
- [ ] Automated remediation strategies
- [ ] Integration with external compliance frameworks

## References

- **Phase 1 PR**: #1356 - Import path fixes and syntax errors
- **Phase 2 PR**: #1360 - Audit and bridge modules
- **Phase 3 PRs**:
  - #1362 - Deprecation warnings for legacy bridges
  - #1363 - GuardianPoliciesEngine relocation to canonical location
  - #1364 - GuardianReflector relocation to canonical location
- **Phase 1 Audit**: `docs/GUARDIAN_MODULE_STRUCTURE_AUDIT_2025-11-12.md`
- **Phase 2 Audit**: `docs/GUARDIAN_STRUCTURE_CONSOLIDATION_AUDIT_2025-11-12.md`
- **Import Guide**: `docs/development/GUARDIAN_IMPORTS.md`
- **Kill-Switch Documentation**: `docs/GUARDIAN_EMERGENCY_KILLSWITCH.md`
- **Integration Test Report**: `docs/GUARDIAN_KILLSWITCH_INTEGRATION_TEST_REPORT.md`

## Related Systems

- **MATRIZ Cognitive Engine**: Cognitive processing and orchestration
- **Identity System (ΛiD)**: Authentication and access control
- **Memory System**: Persistent state and context
- **Ethics Engine**: Moral reasoning frameworks
- **Consciousness System**: Self-awareness and meta-cognition

---

**Document Status**: ✅ Complete (Phase 3 Final)
**Last Reviewed**: 2025-11-12
**Phase 3 Completion**: 2025-11-12
**Next Review**: Phase 4 planning (2025-Q1)
**Maintainer**: LUKHAS AI Governance Team
