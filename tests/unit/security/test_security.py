# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.authentication
# criticality: P1

import pytest

from candidate.bridge.api.validation import SecurityValidator, ValidationErrorType


@pytest.mark.tier3
@pytest.mark.security
@pytest.mark.unit
class TestSecurityValidator:
    """
    Tests for the SecurityValidator class.
    """

    @pytest.fixture
    def validator(self):
        return SecurityValidator()

    @pytest.mark.parametrize("content", [
        "<script>alert('XSS')</script>",
        "javascript:alert('pwned')",
        "eval('1+1')",
        "DROP TABLE users;"
    ])
    def test_detects_dangerous_patterns(self, validator: SecurityValidator, content: str):
        """Tests that dangerous patterns are correctly identified."""
        issues = validator.validate_content_security(content)
        assert len(issues) > 0
        assert issues[0]["type"] == ValidationErrorType.SECURITY_VIOLATION.value

    def test_no_issues_for_safe_content(self, validator: SecurityValidator):
        """Tests that safe content passes validation."""
        issues = validator.validate_content_security("This is a safe string.")
        assert len(issues) == 0

    def test_detects_phi_in_healthcare_context(self, validator: SecurityValidator):
        """Tests that PHI is detected in a healthcare context."""
        content = "Patient SSN is 123-45-6789."
        issues = validator.validate_content_security(content, context="healthcare")
        assert len(issues) > 0
        assert issues[0]["type"] == ValidationErrorType.HIPAA_VIOLATION.value
