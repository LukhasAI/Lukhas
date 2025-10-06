---
status: wip
type: documentation
---
# Authorization Telemetry Smoke Tests

This directory contains comprehensive smoke tests that validate authorization operations properly emit OpenTelemetry spans with the required observability data as specified in Matrix contracts.

## Overview

The telemetry smoke tests ensure that:

1. **Span Emission**: Authorization operations emit `authz.check` spans
2. **Span Attributes**: Spans contain proper authorization context (tier, scope, result)
3. **Span Structure**: Spans follow OpenTelemetry data model standards
4. **Error Handling**: Failed authorization emits proper error spans
5. **Performance**: Telemetry overhead is minimal and reasonable

## Test Structure

```
tests/telemetry/
├── __init__.py                    # Module initialization
├── conftest.py                    # pytest fixtures for telemetry testing
├── test_authz_spans.py           # Core span emission smoke tests
├── test_authz_attributes.py      # Detailed attribute validation tests
├── test_authz_integration.py     # End-to-end integration tests
├── pytest.ini                    # pytest configuration
├── requirements.txt               # Test dependencies
└── README.md                      # This file
```

## Test Categories

### 1. Smoke Tests (`test_authz_spans.py`)

Basic validation that authorization operations emit telemetry:

- `test_authz_check_span_emission` - Verifies spans are emitted
- `test_authz_span_attributes_allow` - Tests ALLOW decision spans
- `test_authz_span_attributes_deny` - Tests DENY decision spans
- `test_authz_span_mfa_stepup` - Tests MFA step-up scenarios
- `test_authz_span_service_account` - Tests service account authorization
- `test_authz_span_performance_tracking` - Tests performance metrics
- `test_authz_span_error_handling` - Tests error scenarios

### 2. Attribute Validation (`test_authz_attributes.py`)

Detailed validation of span attributes:

- `test_authz_span_required_lukhas_attributes` - Required LUKHAS attributes
- `test_authz_span_scope_formatting` - Scope formatting validation
- `test_authz_span_subject_patterns` - Subject pattern validation
- `test_authz_span_tier_consistency` - Tier consistency checks
- `test_authz_span_decision_values` - Decision value standardization
- `test_authz_span_capability_id_masking` - Security masking validation
- `test_authz_span_contract_sha_presence` - Contract auditability
- `test_authz_span_region_tracking` - Region information tracking

### 3. Integration Tests (`test_authz_integration.py`)

End-to-end workflow validation:

- `test_end_to_end_authorization_with_telemetry` - Complete workflows
- `test_middleware_handler_integration_with_telemetry` - Middleware integration
- `test_shadow_mode_telemetry_emission` - Shadow mode testing
- `test_authorization_with_opa_policy_integration` - OPA integration
- `test_authorization_matrix_test_integration` - Test matrix compatibility
- `test_concurrent_authorization_telemetry` - Concurrent request handling
- `test_authorization_error_propagation_with_telemetry` - Error propagation

## Required Span Attributes

Authorization spans must include these attributes per Matrix contract specifications:

### Core Authorization Context
- `lukhas.subject` - Identity making the request
- `lukhas.tier` - Authorization tier (guest, friend, trusted, etc.)
- `lukhas.tier_num` - Numeric tier level (0-5)
- `lukhas.scopes` - Comma-separated list of granted scopes
- `lukhas.module` - Target module (memoria, etc.)
- `lukhas.action` - Requested action/operation
- `lukhas.decision` - Authorization result ("allow" or "deny")
- `lukhas.reason` - Human-readable decision reason

### Security & Auditability
- `lukhas.policy_sha` - SHA hash of applied policy
- `lukhas.contract_sha` - SHA hash of module contract
- `lukhas.capability_id` - Masked capability token identifier
- `lukhas.mfa_used` - Whether MFA was used
- `lukhas.region` - Request region

### Performance Tracking
- `lukhas.decision_time_ms` - Authorization decision time in milliseconds

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r tests/telemetry/requirements.txt
```

### Running All Telemetry Tests

```bash
cd tests/telemetry
python -m pytest -v -m telemetry
```

### Running Specific Test Categories

Smoke tests only:
```bash
python -m pytest -v test_authz_spans.py
```

Attribute validation:
```bash
python -m pytest -v test_authz_attributes.py
```

Integration tests:
```bash
python -m pytest -v -m "telemetry and integration"
```

### Running with Coverage

```bash
coverage run -m pytest -v -m telemetry
coverage report --show-missing
```

## CI/CD Integration

Telemetry smoke tests are integrated into the CI/CD pipeline via `.github/workflows/telemetry-smoke-tests.yml`:

- **Trigger**: On changes to authorization middleware, policies, or telemetry tests
- **Matrix**: Python 3.9 and 3.11
- **Schedule**: Daily runs at 6 AM UTC to catch environment drift
- **Artifacts**: Test results and coverage reports

### Pipeline Stages

1. **Smoke Tests**: Basic span emission validation
2. **Integration Tests**: End-to-end workflow testing
3. **Coverage**: Code coverage analysis (PR only)
4. **Performance**: Telemetry overhead validation (scheduled)

## Fixtures and Utilities

### Key Fixtures (`conftest.py`)

- `telemetry_capture` - Captures OpenTelemetry spans for testing
- `test_subjects` - Predefined test subjects for different authorization scenarios
- `authz_test_scenarios` - Common authorization test scenarios
- `span_validator` - Utilities for validating span structure and attributes
- `matrix_contract_loader` - Loads Matrix contracts for testing

### Test Utilities

- `temp_span_dump()` - Creates temporary files with span data for compatibility testing
- `CapturedSpan` - Data class for captured span information
- `TelemetryCapture` - Container for captured telemetry data

## Matrix Contract Compliance

Tests validate compliance with Matrix contract telemetry specifications:

```json
{
  "telemetry": {
    "opentelemetry_semconv_version": "1.37.0",
    "spans": [
      {
        "name": "authz.check",
        "attrs": ["lukhas.subject", "lukhas.tier", "lukhas.decision"]
      }
    ]
  }
}
```

## Performance Expectations

- **Authorization latency**: < 100ms for typical requests
- **Telemetry overhead**: < 5% additional latency
- **Span emission**: < 10ms additional overhead
- **Memory usage**: < 1MB additional per 1000 spans

## Troubleshooting

### Common Issues

1. **Missing OpenTelemetry spans**: Check that tracer provider is properly configured
2. **Attribute validation failures**: Verify authorization middleware is emitting all required attributes
3. **Integration test failures**: Ensure OPA is available and authorization test matrices exist
4. **Performance test failures**: Check system load and authorization latency targets

### Debug Mode

Enable debug logging:
```bash
export OTEL_LOG_LEVEL=debug
python -m pytest -v -s test_authz_spans.py::test_authz_check_span_emission
```

### Manual Span Inspection

Inspect captured spans in tests:
```python
def test_debug_spans(telemetry_capture):
    # ... run authorization ...

    for span in telemetry_capture.spans:
        print(f"Span: {span.name}")
        print(f"Attributes: {span.attributes}")
        print(f"Status: {span.status}")
```

## Contributing

When adding new authorization features:

1. Add corresponding telemetry tests
2. Update required attributes list if new context is needed
3. Ensure Matrix contracts specify telemetry requirements
4. Validate CI/CD pipeline passes
5. Update this README if test structure changes