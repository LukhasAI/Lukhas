# Gemini — Telemetry Contracts & Observability

## Primary Task
Implement comprehensive telemetry contract validation with observability hardening:
- Dynamic ID prevention for Prometheus cardinality explosion
- Metric contract validation with schema enforcement
- Distributed tracing with span correlation validation
- Alerting contract compliance with SLO alignment

**Output**: artifacts/{component}_telemetry_contracts_validation.json

## Specific Instructions

### Dynamic ID Prevention System
```python
import re
from typing import Dict, List, Set, Any, Optional

class TelemetryContractValidator:
    def __init__(self):
        self.dynamic_id_patterns = [
            # UUID patterns (various formats)
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",

            # Timestamp patterns
            r"\d{13,}",  # Unix timestamps (ms)
            r"\d{10}",   # Unix timestamps (s)
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO timestamps

            # Request/Session ID patterns
            r"req_[0-9a-zA-Z]+",
            r"sess_[0-9a-zA-Z]+",
            r"trace_[0-9a-fA-F]+",

            # Hash patterns
            r"[0-9a-f]{32}",  # MD5
            r"[0-9a-f]{40}",  # SHA1
            r"[0-9a-f]{64}",  # SHA256
        ]

        self.compiled_patterns = [re.compile(pattern) for pattern in self.dynamic_id_patterns]

    def validate_metric_labels(self, metric_name: str, labels: Dict[str, str]) -> Dict[str, Any]:
        """Validate metric labels for dynamic ID prevention."""
        violations = []
        cardinality_risk = 0

        for label_name, label_value in labels.items():
            # Check for dynamic ID patterns
            for pattern in self.compiled_patterns:
                if pattern.search(str(label_value)):
                    violations.append({
                        'type': 'dynamic_id_detected',
                        'label': label_name,
                        'value': str(label_value)[:50],  # Truncate for security
                        'pattern': pattern.pattern
                    })
                    cardinality_risk += 100  # High risk per dynamic ID

            # Check for high-cardinality indicators
            if len(str(label_value)) > 50:
                cardinality_risk += 10

            if any(char.isdigit() for char in str(label_value)) and len(str(label_value)) > 8:
                cardinality_risk += 5

        # Validate against allowed label patterns
        allowed_labels = self._get_allowed_labels(metric_name)
        for label_name in labels:
            if label_name not in allowed_labels:
                violations.append({
                    'type': 'unauthorized_label',
                    'label': label_name,
                    'allowed_labels': list(allowed_labels)
                })

        return {
            'metric_name': metric_name,
            'violations': violations,
            'cardinality_risk_score': min(cardinality_risk, 1000),  # Cap at 1000
            'validation_passed': len(violations) == 0,
            'label_count': len(labels)
        }

    def _get_allowed_labels(self, metric_name: str) -> Set[str]:
        """Get allowed labels for a specific metric."""
        # Metric-specific label allowlists
        metric_labels = {
            'matriz_tick_duration_seconds': {'component', 'status', 'lane'},
            'matriz_reflect_duration_seconds': {'component', 'status', 'lane'},
            'matriz_decide_duration_seconds': {'component', 'status', 'lane'},
            'http_requests_total': {'method', 'status_code', 'handler', 'lane'},
            'db_query_duration_seconds': {'operation', 'table', 'status'},
            'memory_fold_operations_total': {'operation', 'status', 'fold_type'}
        }

        return metric_labels.get(metric_name, {'component', 'status', 'lane'})
```

### Metric Contract Schema Enforcement
```python
class MetricContractSchema:
    def __init__(self):
        self.contracts = {
            'matriz_tick_duration_seconds': {
                'type': 'histogram',
                'help': 'Time spent in MATRIZ tick operation',
                'required_labels': ['component', 'lane'],
                'optional_labels': ['status'],
                'buckets': [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
                'slo_target_ms': 100
            },
            'matriz_reflect_duration_seconds': {
                'type': 'histogram',
                'help': 'Time spent in MATRIZ reflect operation',
                'required_labels': ['component', 'lane'],
                'optional_labels': ['status'],
                'buckets': [0.001, 0.002, 0.005, 0.01, 0.025, 0.05, 0.1],
                'slo_target_ms': 10
            },
            'http_requests_total': {
                'type': 'counter',
                'help': 'Total HTTP requests',
                'required_labels': ['method', 'status_code', 'handler'],
                'optional_labels': ['lane']
            }
        }

    def validate_metric_contract(self, metric_name: str, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metric against its contract."""
        if metric_name not in self.contracts:
            return {
                'valid': False,
                'error': f'No contract defined for metric: {metric_name}'
            }

        contract = self.contracts[metric_name]
        violations = []

        # Validate metric type
        if metric_config.get('type') != contract['type']:
            violations.append(f"Type mismatch: expected {contract['type']}, got {metric_config.get('type')}")

        # Validate required labels
        provided_labels = set(metric_config.get('labels', []))
        required_labels = set(contract['required_labels'])
        missing_labels = required_labels - provided_labels
        if missing_labels:
            violations.append(f"Missing required labels: {list(missing_labels)}")

        # Validate histogram buckets
        if contract['type'] == 'histogram':
            provided_buckets = metric_config.get('buckets', [])
            expected_buckets = contract.get('buckets', [])
            if provided_buckets != expected_buckets:
                violations.append(f"Bucket mismatch: expected {expected_buckets}")

        return {
            'metric_name': metric_name,
            'valid': len(violations) == 0,
            'violations': violations,
            'contract': contract
        }
```

### Distributed Tracing Validation
```python
class DistributedTracingValidator:
    def __init__(self):
        self.required_span_attributes = {
            'service.name',
            'service.version',
            'deployment.environment',
            'matriz.component',
            'matriz.lane'
        }

    def validate_span_correlation(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate span correlation and trace continuity."""
        validation_result = {
            'valid': True,
            'violations': [],
            'trace_continuity': True,
            'span_count': len(spans)
        }

        if not spans:
            validation_result['valid'] = False
            validation_result['violations'].append('No spans provided')
            return validation_result

        # Validate trace ID consistency
        trace_ids = {span.get('trace_id') for span in spans}
        if len(trace_ids) > 1:
            validation_result['valid'] = False
            validation_result['violations'].append(f'Multiple trace IDs found: {trace_ids}')

        # Validate parent-child relationships
        span_ids = {span.get('span_id') for span in spans}
        parent_ids = {span.get('parent_span_id') for span in spans if span.get('parent_span_id')}

        # Check for orphaned spans (parent_id not in span_ids)
        orphaned = parent_ids - span_ids
        if orphaned:
            validation_result['trace_continuity'] = False
            validation_result['violations'].append(f'Orphaned spans with parent IDs: {orphaned}')

        # Validate required attributes
        for i, span in enumerate(spans):
            missing_attrs = self.required_span_attributes - set(span.get('attributes', {}).keys())
            if missing_attrs:
                validation_result['valid'] = False
                validation_result['violations'].append(
                    f'Span {i} missing attributes: {missing_attrs}'
                )

        return validation_result

    def validate_matriz_span_semantics(self, span: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MATRIZ-specific span semantics."""
        attributes = span.get('attributes', {})
        violations = []

        # Validate MATRIZ operation spans
        operation_name = span.get('operation_name', '')
        if operation_name.startswith('matriz.'):
            # Validate operation-specific attributes
            if 'matriz.tick.duration_ms' not in attributes and operation_name == 'matriz.tick':
                violations.append('MATRIZ tick span missing duration_ms attribute')

            if 'matriz.component' not in attributes:
                violations.append('MATRIZ span missing component attribute')

            # Validate performance annotations
            if 'performance.slo_target_ms' not in attributes:
                violations.append('MATRIZ span missing SLO target annotation')

        return {
            'span_id': span.get('span_id'),
            'valid': len(violations) == 0,
            'violations': violations
        }
```

### Alerting Contract Compliance
```python
class AlertingContractValidator:
    def __init__(self):
        self.alert_contracts = {
            'MATRIZ_TickLatencyHigh': {
                'query': 'histogram_quantile(0.95, rate(matriz_tick_duration_seconds_bucket[5m])) > 0.1',
                'for': '2m',
                'severity': 'warning',
                'slo_alignment': 'matriz_tick_slo'
            },
            'MATRIZ_DecisionFailureRateHigh': {
                'query': 'rate(matriz_decide_errors_total[5m]) / rate(matriz_decide_total[5m]) > 0.001',
                'for': '1m',
                'severity': 'critical',
                'slo_alignment': 'matriz_reliability_slo'
            }
        }

    def validate_alert_configuration(self, alert_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate alert configuration against contract."""
        if alert_name not in self.alert_contracts:
            return {
                'valid': False,
                'error': f'No contract defined for alert: {alert_name}'
            }

        contract = self.alert_contracts[alert_name]
        violations = []

        # Validate query
        if config.get('query') != contract['query']:
            violations.append(f"Query mismatch")

        # Validate duration
        if config.get('for') != contract['for']:
            violations.append(f"Duration mismatch: expected {contract['for']}")

        # Validate severity
        if config.get('severity') != contract['severity']:
            violations.append(f"Severity mismatch: expected {contract['severity']}")

        return {
            'alert_name': alert_name,
            'valid': len(violations) == 0,
            'violations': violations,
            'contract_compliance': True if len(violations) == 0 else False
        }
```

### Performance Requirements
- Dynamic ID validation: <50ms per metric
- Contract schema validation: <25ms per metric
- Span correlation validation: <100ms per trace
- Alert contract validation: <30ms per alert

### Testing Framework
```python
@pytest.mark.telemetry
@pytest.mark.lane("integration")
def test_dynamic_id_prevention():
    validator = TelemetryContractValidator()

    # Test UUID detection
    result = validator.validate_metric_labels(
        'http_requests_total',
        {'request_id': 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'method': 'GET'}
    )
    assert not result['validation_passed']
    assert any(v['type'] == 'dynamic_id_detected' for v in result['violations'])

    # Test valid labels
    result = validator.validate_metric_labels(
        'http_requests_total',
        {'method': 'GET', 'status_code': '200', 'handler': 'api'}
    )
    assert result['validation_passed']
    assert result['cardinality_risk_score'] == 0

@pytest.mark.telemetry
@pytest.mark.lane("integration")
def test_metric_contract_validation():
    schema = MetricContractSchema()

    # Test valid metric configuration
    config = {
        'type': 'histogram',
        'labels': ['component', 'lane', 'status'],
        'buckets': [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    }

    result = schema.validate_metric_contract('matriz_tick_duration_seconds', config)
    assert result['valid']
```

### Evidence Generation
Create validation artifact with structure:
```json
{
  "component": "telemetry_contracts_validation",
  "validation_timestamp": "ISO8601",
  "dynamic_id_prevention": {
    "patterns_validated": 8,
    "cardinality_protection": true,
    "detection_accuracy": 1.0,
    "performance_ms": 45
  },
  "metric_contracts": {
    "contracts_defined": 15,
    "schema_enforcement": true,
    "validation_coverage": 1.0,
    "performance_ms": 20
  },
  "distributed_tracing": {
    "span_correlation_validated": true,
    "trace_continuity_checked": true,
    "semantics_validated": true,
    "performance_ms": 85
  },
  "alerting_contracts": {
    "alert_rules_validated": 12,
    "slo_alignment_verified": true,
    "compliance_rate": 1.0,
    "performance_ms": 25
  }
}
```