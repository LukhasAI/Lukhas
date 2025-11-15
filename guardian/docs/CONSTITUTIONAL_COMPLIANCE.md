# Guardian Constitutional Compliance Framework

## Overview

The Guardian Constitutional Compliance Framework provides constitutional AI compliance enforcement and identity verification for the LUKHAS Guardian system. This framework integrates with the core Constitutional AI validator to ensure all Guardian identity operations comply with democratic principles including transparency, accountability, fairness, and human autonomy.

**Addresses**: LukhasAI/Lukhas#560 - Constitutional AI compliance implementation

## Architecture

### Components

1. **GuardianConstitutionalCompliance** - Main compliance system
2. **Constitutional AI Validator Integration** - Integration with core constitutional AI validation
3. **Compliance Reporting** - Report generation and metrics tracking
4. **Audit Trail Management** - Complete audit trail recording and retrieval

### Data Flow

```
Identity Operation Request
          ↓
Guardian Compliance Check
          ↓
Constitutional AI Validation
          ↓
Compliance Status Determination
          ↓
Audit Trail Recording
          ↓
Metrics Update
```

## Core Classes

### GuardianConstitutionalCompliance

Main compliance system that orchestrates constitutional AI validation for Guardian operations.

**Key Methods**:

- `initialize_compliance_system()` - Initialize with Constitutional AI validator
- `verify_identity_compliance(identity_id, operation_context)` - Verify operation compliance
- `generate_compliance_report(start_date, end_date)` - Generate compliance reports
- `get_identity_audit_trail(identity_id)` - Retrieve complete audit trail
- `get_compliance_metrics()` - Get current compliance metrics
- `shutdown_compliance_system()` - Graceful shutdown

### GuardianComplianceCheck

Record of a single compliance verification with constitutional validation details.

**Fields**:
- `check_id` - Unique compliance check identifier
- `decision_category` - Category of Guardian decision
- `identity_id` - Identity being verified
- `compliance_status` - Overall compliance status
- `constitutional_score` - Constitutional AI validation score
- `principles_validated` - Map of constitutional principles to compliance
- `oversight_required` - Whether human oversight is required
- `audit_trail` - List of audit events for this check

### ComplianceReport

Comprehensive compliance report for a time period.

**Fields**:
- `report_id` - Unique report identifier
- `total_checks` - Total number of compliance checks
- `compliant_count` - Number of compliant operations
- `review_required_count` - Number requiring review
- `non_compliant_count` - Number of non-compliant operations
- `checks_by_category` - Breakdown by decision category
- `compliance_by_principle` - Compliance rate per principle
- `critical_violations` - List of critical violations
- `recommendations` - System recommendations
- `areas_for_improvement` - Identified improvement areas

## Enums

### ComplianceStatus

- `COMPLIANT` - Fully compliant with constitutional principles
- `REVIEW_REQUIRED` - Requires human oversight review
- `NON_COMPLIANT` - Does not meet compliance standards
- `EMERGENCY_OVERRIDE` - Emergency override approved

### GuardianDecisionCategory

- `IDENTITY_VERIFICATION` - Identity verification operations
- `ACCESS_CONTROL` - Access control decisions
- `DATA_GOVERNANCE` - Data governance operations
- `EMERGENCY_RESPONSE` - Emergency response actions
- `POLICY_ENFORCEMENT` - Policy enforcement decisions
- `AUDIT_REVIEW` - Audit review operations

## Usage Examples

### Basic Identity Verification

```python
from guardian import guardian_constitutional_compliance

# Initialize system
await guardian_constitutional_compliance.initialize_compliance_system()

# Verify identity operation
operation_context = {
    "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
    "user_consent": True,
    "data_minimization": True,
    "data_purpose": "identity_authentication",
    "security_measures": ["encryption", "multi_factor"],
    "reasoning": "User authentication for system access",
    "decision_criteria": {"valid_credentials": True},
    "guardian_reviewer": "guardian_officer_001",
}

check = await guardian_constitutional_compliance.verify_identity_compliance(
    identity_id="user_12345",
    operation_context=operation_context
)

print(f"Compliance Status: {check.compliance_status.value}")
print(f"Constitutional Score: {check.constitutional_score:.2f}")
print(f"Oversight Required: {check.oversight_required}")
```

### Generating Compliance Reports

```python
from datetime import datetime, timedelta, timezone

# Generate report for last 24 hours
start_date = datetime.now(timezone.utc) - timedelta(days=1)
end_date = datetime.now(timezone.utc)

report = await guardian_constitutional_compliance.generate_compliance_report(
    start_date=start_date,
    end_date=end_date
)

print(f"Total Checks: {report.total_checks}")
print(f"Compliant: {report.compliant_count}")
print(f"Non-Compliant: {report.non_compliant_count}")
print(f"Recommendations: {report.recommendations}")
```

### Retrieving Audit Trails

```python
# Get complete audit trail for an identity
audit_trail = await guardian_constitutional_compliance.get_identity_audit_trail(
    identity_id="user_12345"
)

for event in audit_trail:
    print(f"{event['timestamp']}: {event['action']} - {event.get('compliance_status', 'N/A')}")
```

### Emergency Override Handling

```python
# Emergency operation with override
emergency_context = {
    "decision_category": GuardianDecisionCategory.EMERGENCY_RESPONSE,
    "urgency_level": "emergency",
    "override_approved": True,
    "emergency_justification": "Critical security threat detected",
    "security_measures": ["immediate_lockdown", "audit_logging"],
    "reasoning": "Emergency response to active threat",
}

check = await guardian_constitutional_compliance.verify_identity_compliance(
    identity_id="system_emergency",
    operation_context=emergency_context
)

# Emergency overrides get special status
assert check.compliance_status == ComplianceStatus.EMERGENCY_OVERRIDE
assert check.emergency_context is True
```

## Constitutional Principles Validated

The Guardian compliance system validates operations against these Constitutional AI principles:

1. **Democratic Governance** - Stakeholder involvement and oversight
2. **Human Autonomy** - Preserves human decision-making authority
3. **Transparency** - Clear documentation and reasoning
4. **Accountability** - Clear responsibility and appeals process
5. **Fairness** - Equal treatment and bias mitigation
6. **Privacy** - Data minimization and security
7. **Consent** - Informed, freely given, withdrawable consent
8. **Non-Discrimination** - No protected class discrimination
9. **Proportionality** - Response proportional to risk
10. **Explainability** - Decision logic is explainable

## Compliance Thresholds

- **Compliance Threshold**: 0.7 - Minimum constitutional score for automatic compliance
- **Oversight Threshold**: 0.6 - Below this score requires human oversight
- **Critical Violation**: < 0.5 - Tracked as critical violation in reports

## Audit Trail

Every compliance check creates an audit trail entry containing:

- Timestamp (ISO 8601 format)
- Action performed
- Identity ID
- Compliance status
- Constitutional score
- Validation ID (links to Constitutional AI validator)

Audit trails are:
- Immutable once recorded
- Sorted by timestamp (most recent first)
- Retrievable per identity
- Included in compliance reports

## Metrics Tracking

The system tracks comprehensive compliance metrics:

- **Total Checks** - Total number of compliance verifications
- **Compliant Checks** - Count of compliant operations
- **Review Required** - Count requiring human oversight
- **Non-Compliant** - Count of non-compliant operations
- **Average Constitutional Score** - Mean validation score
- **Compliance Rate** - Percentage of compliant operations
- **Oversight Rate** - Percentage requiring oversight

## Integration with Constitutional AI Validator

The Guardian compliance system integrates seamlessly with the core Constitutional AI validator:

```
Guardian Operation
       ↓
GuardianConstitutionalCompliance.verify_identity_compliance()
       ↓
Create ConstitutionalValidationContext
       ↓
ConstitutionalAIValidator.validate_identity_decision()
       ↓
Evaluate Constitutional Principles
       ↓
Return ConstitutionalValidationResult
       ↓
Map to GuardianComplianceCheck
       ↓
Record Audit Trail & Update Metrics
```

## Error Handling

The system includes robust error handling:

- **Fallback Compliance Check** - Used when constitutional validator is unavailable
- **Exception Logging** - All errors logged with context
- **Graceful Degradation** - System continues with reduced functionality
- **Oversight Flagging** - Errors automatically flag for human review

## Testing

Comprehensive test suite available in `guardian/tests/test_constitutional_compliance.py`:

- Unit tests for all compliance functions
- Integration tests with Constitutional AI validator
- End-to-end workflow tests
- Edge case and error handling tests
- Metrics and reporting tests

Run tests:
```bash
pytest guardian/tests/test_constitutional_compliance.py -v
```

## Future Enhancements

1. **Machine Learning Integration** - ML-based compliance prediction
2. **Real-time Dashboard** - Live compliance monitoring dashboard
3. **Advanced Analytics** - Trend analysis and anomaly detection
4. **Multi-tenancy** - Support for multiple Guardian instances
5. **Compliance Templates** - Pre-configured templates for common operations

## References

- Constitutional AI Compliance Module: `core/identity/constitutional_ai_compliance.py`
- Guardian Constitutional Tests: `guardian/tests/test_constitutional_compliance.py`
- Issue #560: [Constitutional AI compliance TODO](https://github.com/LukhasAI/Lukhas/issues/560)

## License

Part of the LUKHAS AI platform. See LICENSE file for details.

## Support

For issues or questions:
- GitHub Issues: https://github.com/LukhasAI/Lukhas/issues
- Guardian Team: guardian-compliance-officer
