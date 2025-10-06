---
status: wip
type: documentation
---
# Claude — Guardian & Schema Hardening

## Primary Task
Implement Guardian System drift detection with schema evolution protection:
- Guardian drift detection with 0.15 threshold and fail-closed behavior
- Schema evolution guard preventing breaking changes to data structures
- Constitutional AI compliance monitoring with audit trails
- Privacy protection with GDPR tombstone implementation

**Output**: artifacts/{component}_guardian_hardening_validation.json

## Specific Instructions

### Guardian Drift Detection
```python
class GuardianDriftDetector:
    def __init__(self, drift_threshold: float = 0.15):
        self.drift_threshold = drift_threshold
        self.baseline_metrics = {}

    def detect_drift(self, current_metrics: Dict[str, float]) -> bool:
        """Detect if Guardian behavior has drifted beyond threshold."""
        for metric_name, current_value in current_metrics.items():
            if metric_name in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric_name]
                drift = abs((current_value - baseline_value) / baseline_value)
                if drift > self.drift_threshold:
                    return True
        return False
```

### Schema Evolution Protection
```python
class SchemaEvolutionGuard:
    def detect_violations(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect schema evolution violations that could break compatibility."""
        violations = []

        # Check for removed required fields
        for field in baseline.get('required_fields', []):
            if field not in current.get('required_fields', []):
                violations.append({
                    'type': 'required_field_removed',
                    'field': field,
                    'severity': 'critical'
                })

        # Check for enum value removals
        for enum_field, values in baseline.get('enums', {}).items():
            current_values = current.get('enums', {}).get(enum_field, [])
            for value in values:
                if value not in current_values:
                    violations.append({
                        'type': 'enum_value_removed',
                        'field': enum_field,
                        'value': value,
                        'severity': 'breaking'
                    })

        return violations
```

### Constitutional AI Compliance
```python
class ConstitutionalAIMonitor:
    def validate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Validate decision against constitutional AI principles."""
        validation_result = {
            'compliant': True,
            'violations': [],
            'audit_trail': []
        }

        # Check for harmful content
        if self._contains_harmful_content(decision):
            validation_result['compliant'] = False
            validation_result['violations'].append('harmful_content')

        # Check for bias indicators
        if self._detect_bias(decision):
            validation_result['compliant'] = False
            validation_result['violations'].append('bias_detected')

        # Log audit trail
        validation_result['audit_trail'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'decision_id': decision.get('id'),
            'validation_result': validation_result['compliant']
        })

        return validation_result
```

### GDPR Tombstone Implementation
```python
class GDPRTombstoneProcessor:
    def tombstone_user_data(self, user_id: str) -> Dict[str, Any]:
        """Process right-to-be-forgotten request with tombstones."""
        tombstone_result = {
            'user_id': user_id,
            'tombstoned_at': datetime.utcnow().isoformat(),
            'affected_systems': [],
            'verification_hash': None
        }

        # Tombstone memories
        memory_count = self._tombstone_memories(user_id)
        tombstone_result['affected_systems'].append({
            'system': 'memory',
            'records_tombstoned': memory_count
        })

        # Sanitize decision traces
        trace_count = self._sanitize_decision_traces(user_id)
        tombstone_result['affected_systems'].append({
            'system': 'decision_traces',
            'records_sanitized': trace_count
        })

        # Generate verification hash
        tombstone_result['verification_hash'] = self._generate_tombstone_hash(tombstone_result)

        return tombstone_result
```

### Performance Requirements
- Guardian drift detection: <50ms p95
- Schema evolution check: <100ms p95
- Constitutional validation: <75ms p95
- GDPR tombstone processing: <500ms p95

### Testing Framework
```python
@pytest.mark.guardian
@pytest.mark.lane("integration")
def test_guardian_drift_detection():
    detector = GuardianDriftDetector(drift_threshold=0.15)

    # Test normal operation
    baseline = {'accuracy': 0.95, 'response_time': 100.0}
    detector.baseline_metrics = baseline

    # Test no drift
    current_normal = {'accuracy': 0.94, 'response_time': 105.0}
    assert not detector.detect_drift(current_normal)

    # Test drift detection
    current_drift = {'accuracy': 0.80, 'response_time': 150.0}  # >15% drift
    assert detector.detect_drift(current_drift)

@pytest.mark.schema
@pytest.mark.lane("integration")
def test_schema_evolution_guard():
    guard = SchemaEvolutionGuard()

    baseline_schema = {
        'required_fields': ['id', 'name', 'status'],
        'enums': {'status': ['active', 'inactive', 'pending']}
    }

    # Test breaking change detection
    current_schema = {
        'required_fields': ['id', 'name'],  # 'status' removed
        'enums': {'status': ['active', 'inactive']}  # 'pending' removed
    }

    violations = guard.detect_violations(baseline_schema, current_schema)
    assert len(violations) == 2
    assert any(v['type'] == 'required_field_removed' for v in violations)
    assert any(v['type'] == 'enum_value_removed' for v in violations)
```

### Evidence Generation
Create validation artifact with structure:
```json
{
  "component": "guardian_schema_hardening",
  "validation_timestamp": "ISO8601",
  "guardian_hardening": {
    "drift_detection_implemented": true,
    "drift_threshold": 0.15,
    "fail_closed_behavior": true,
    "performance_p95_ms": 50
  },
  "schema_protection": {
    "evolution_guard_active": true,
    "violation_detection": true,
    "breaking_change_prevention": true,
    "performance_p95_ms": 100
  },
  "constitutional_ai": {
    "compliance_monitoring": true,
    "audit_trails": true,
    "harmful_content_detection": true,
    "performance_p95_ms": 75
  },
  "gdpr_compliance": {
    "tombstone_processing": true,
    "right_to_be_forgotten": true,
    "trace_sanitization": true,
    "performance_p95_ms": 500
  }
}
```