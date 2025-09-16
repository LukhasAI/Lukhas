from candidate.bridge.api.validation import ValidationErrorType, ValidationResult, ValidationSeverity


def test_validation_result_summary_counts():
    v = ValidationResult(is_valid=True)
    # Add two errors of different types and severities
    v.add_error(ValidationErrorType.MISSING_FIELD, "missing a", field="a", severity=ValidationSeverity.ERROR)
    v.add_error(ValidationErrorType.INVALID_VALUE, "bad x", field="x", severity=ValidationSeverity.CRITICAL)
    # Add a warning
    v.add_warning("watch y", field="y")

    s = v.summary()
    assert s["is_valid"] is False
    assert s["errors"] == 2
    assert s["warnings"] == 1
    assert s["error_counts"][ValidationErrorType.MISSING_FIELD.value] == 1
    assert s["error_counts"][ValidationErrorType.INVALID_VALUE.value] == 1
    # Severity counts include ERROR and CRITICAL
    assert s["severity_counts"][ValidationSeverity.ERROR.value] == 1
    assert s["severity_counts"][ValidationSeverity.CRITICAL.value] == 1
