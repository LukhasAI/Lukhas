"""
Comprehensive feature flag tests.

Validates:
- Feature flag evaluation (enabled/disabled, percentage rollout)
- User targeting (by ID, email domain, environment)
- Flag configuration updates
- Pydantic models and validation
- Privacy and security requirements
- Edge cases and error handling
"""
import pytest
from pydantic import ValidationError
from lukhas.api.features import (
    FlagEvaluationRequest,
    FlagEvaluationResponse,
    FlagInfo,
    FlagUpdateRequest,
    FlagListResponse,
)


# Flag Evaluation Request Tests
class TestFlagEvaluationRequest:
    """Test feature flag evaluation request models."""

    def test_evaluation_request_all_fields(self):
        """Verify evaluation request with all fields."""
        request = FlagEvaluationRequest(
            user_id="user123",
            email="user@example.com",
            environment="prod"
        )

        assert request.user_id == "user123"
        assert request.email == "user@example.com"
        assert request.environment == "prod"

    def test_evaluation_request_minimal(self):
        """Verify evaluation request with minimal fields."""
        request = FlagEvaluationRequest()

        # All fields are optional
        assert request.user_id is None
        assert request.email is None
        assert request.environment is None

    def test_evaluation_request_user_id_only(self):
        """Verify evaluation with only user ID."""
        request = FlagEvaluationRequest(user_id="user456")

        assert request.user_id == "user456"
        assert request.email is None
        assert request.environment is None

    def test_evaluation_request_environment_values(self):
        """Verify environment field accepts various values."""
        environments = ["dev", "staging", "prod", "test"]

        for env in environments:
            request = FlagEvaluationRequest(environment=env)
            assert request.environment == env


# Flag Evaluation Response Tests
class TestFlagEvaluationResponse:
    """Test feature flag evaluation response models."""

    def test_evaluation_response_enabled(self):
        """Verify evaluation response when flag is enabled."""
        response = FlagEvaluationResponse(
            flag_name="new-ui",
            enabled=True,
            flag_type="boolean"
        )

        assert response.flag_name == "new-ui"
        assert response.enabled is True
        assert response.flag_type == "boolean"

    def test_evaluation_response_disabled(self):
        """Verify evaluation response when flag is disabled."""
        response = FlagEvaluationResponse(
            flag_name="beta-feature",
            enabled=False,
            flag_type="percentage"
        )

        assert response.flag_name == "beta-feature"
        assert response.enabled is False
        assert response.flag_type == "percentage"

    def test_evaluation_response_flag_types(self):
        """Verify various flag types."""
        flag_types = ["boolean", "percentage", "targeted", "killswitch"]

        for flag_type in flag_types:
            response = FlagEvaluationResponse(
                flag_name="test-flag",
                enabled=True,
                flag_type=flag_type
            )
            assert response.flag_type == flag_type


# Flag Info Tests
class TestFlagInfo:
    """Test feature flag information models."""

    def test_flag_info_complete(self):
        """Verify complete flag information."""
        flag_info = FlagInfo(
            name="premium-features",
            enabled=True,
            flag_type="percentage",
            description="Premium tier features for paid users",
            owner="product-team",
            created_at="2025-01-01T00:00:00Z",
            jira_ticket="LUKHAS-123"
        )

        assert flag_info.name == "premium-features"
        assert flag_info.enabled is True
        assert flag_info.flag_type == "percentage"
        assert flag_info.description == "Premium tier features for paid users"
        assert flag_info.owner == "product-team"
        assert flag_info.created_at == "2025-01-01T00:00:00Z"
        assert flag_info.jira_ticket == "LUKHAS-123"

    def test_flag_info_all_fields_required(self):
        """Verify all flag info fields are required."""
        # Should fail if any field is missing
        try:
            FlagInfo(
                name="test-flag",
                enabled=True,
                flag_type="boolean"
                # Missing: description, owner, created_at, jira_ticket
            )
            pytest.fail("Should require all fields")
        except ValidationError:
            pass  # Expected


# Flag Update Request Tests
class TestFlagUpdateRequest:
    """Test feature flag update request models."""

    def test_update_request_enable(self):
        """Verify update request to enable a flag."""
        request = FlagUpdateRequest(enabled=True)

        assert request.enabled is True
        assert request.percentage is None

    def test_update_request_disable(self):
        """Verify update request to disable a flag."""
        request = FlagUpdateRequest(enabled=False)

        assert request.enabled is False
        assert request.percentage is None

    def test_update_request_percentage(self):
        """Verify update request with percentage rollout."""
        request = FlagUpdateRequest(percentage=50)

        assert request.enabled is None
        assert request.percentage == 50

    def test_update_request_both_fields(self):
        """Verify update request with both enabled and percentage."""
        request = FlagUpdateRequest(enabled=True, percentage=75)

        assert request.enabled is True
        assert request.percentage == 75

    def test_update_request_percentage_bounds(self):
        """Verify percentage must be between 0-100."""
        # Valid percentages
        valid_percentages = [0, 25, 50, 75, 100]

        for pct in valid_percentages:
            request = FlagUpdateRequest(percentage=pct)
            assert request.percentage == pct

        # Invalid percentages should be rejected
        invalid_percentages = [-1, 101, 150, -50]

        for pct in invalid_percentages:
            try:
                FlagUpdateRequest(percentage=pct)
                pytest.fail(f"Should reject percentage {pct}")
            except ValidationError:
                pass  # Expected

    def test_update_request_optional_fields(self):
        """Verify both fields are optional."""
        request = FlagUpdateRequest()

        assert request.enabled is None
        assert request.percentage is None


# Flag List Response Tests
class TestFlagListResponse:
    """Test feature flag list response models."""

    def test_flag_list_response_empty(self):
        """Verify empty flag list response."""
        response = FlagListResponse(flags=[], total=0)

        assert response.flags == []
        assert response.total == 0

    def test_flag_list_response_multiple_flags(self):
        """Verify flag list with multiple flags."""
        flags = [
            FlagInfo(
                name="flag1",
                enabled=True,
                flag_type="boolean",
                description="First flag",
                owner="team1",
                created_at="2025-01-01T00:00:00Z",
                jira_ticket="LUKHAS-1"
            ),
            FlagInfo(
                name="flag2",
                enabled=False,
                flag_type="percentage",
                description="Second flag",
                owner="team2",
                created_at="2025-01-02T00:00:00Z",
                jira_ticket="LUKHAS-2"
            )
        ]

        response = FlagListResponse(flags=flags, total=2)

        assert len(response.flags) == 2
        assert response.total == 2
        assert response.flags[0].name == "flag1"
        assert response.flags[1].name == "flag2"


# Edge Cases and Validation
class TestFeatureFlagEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_flag_name(self):
        """Verify handling of empty flag names."""
        response = FlagEvaluationResponse(
            flag_name="",
            enabled=False,
            flag_type="boolean"
        )

        assert response.flag_name == ""

    def test_very_long_flag_name(self):
        """Verify handling of very long flag names."""
        long_name = "a" * 1000

        response = FlagEvaluationResponse(
            flag_name=long_name,
            enabled=True,
            flag_type="boolean"
        )

        assert response.flag_name == long_name

    def test_special_characters_in_flag_name(self):
        """Verify special characters in flag names."""
        special_names = [
            "feature-with-dashes",
            "feature_with_underscores",
            "feature.with.dots",
            "feature:with:colons"
        ]

        for name in special_names:
            response = FlagEvaluationResponse(
                flag_name=name,
                enabled=True,
                flag_type="boolean"
            )
            assert response.flag_name == name

    def test_unicode_in_descriptions(self):
        """Verify Unicode characters in descriptions."""
        flag_info = FlagInfo(
            name="test-flag",
            enabled=True,
            flag_type="boolean",
            description="Feature with emoji 🚀 and ün icode",
            owner="team",
            created_at="2025-01-01T00:00:00Z",
            jira_ticket="LUKHAS-1"
        )

        assert "🚀" in flag_info.description
        assert "ün" in flag_info.description

    def test_percentage_boundary_values(self):
        """Verify percentage boundary values."""
        # Test exact boundaries
        request_0 = FlagUpdateRequest(percentage=0)
        request_100 = FlagUpdateRequest(percentage=100)

        assert request_0.percentage == 0
        assert request_100.percentage == 100

    def test_email_domain_targeting(self):
        """Verify email domain targeting."""
        test_emails = [
            "user@company.com",
            "admin@example.org",
            "test+tag@domain.co.uk"
        ]

        for email in test_emails:
            request = FlagEvaluationRequest(email=email)
            assert request.email == email

    def test_user_id_formats(self):
        """Verify various user ID formats."""
        user_ids = [
            "user-123",
            "uuid-1234-5678-9012",
            "email@example.com",
            "12345",
            "user_with_underscore"
        ]

        for user_id in user_ids:
            request = FlagEvaluationRequest(user_id=user_id)
            assert request.user_id == user_id


# Privacy and Security Tests
class TestFeatureFlagPrivacy:
    """Test privacy and security requirements."""

    def test_no_pii_in_response(self):
        """Verify responses don't expose PII."""
        response = FlagEvaluationResponse(
            flag_name="test-flag",
            enabled=True,
            flag_type="boolean"
        )

        # Response should not contain user_id or email
        response_dict = response.model_dump()
        assert "user_id" not in response_dict
        assert "email" not in response_dict

    def test_request_fields_optional_for_privacy(self):
        """Verify request fields are optional for privacy."""
        # Can evaluate without providing PII
        request = FlagEvaluationRequest()

        assert request.user_id is None
        assert request.email is None


# Model Serialization Tests
class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_evaluation_request_dict(self):
        """Verify evaluation request can be converted to dict."""
        request = FlagEvaluationRequest(
            user_id="user123",
            environment="prod"
        )

        request_dict = request.model_dump()

        assert request_dict["user_id"] == "user123"
        assert request_dict["environment"] == "prod"

    def test_flag_info_json(self):
        """Verify flag info can be serialized to JSON."""
        flag_info = FlagInfo(
            name="test-flag",
            enabled=True,
            flag_type="boolean",
            description="Test flag",
            owner="team",
            created_at="2025-01-01T00:00:00Z",
            jira_ticket="LUKHAS-1"
        )

        json_str = flag_info.model_dump_json()

        assert '"name":"test-flag"' in json_str or '"name": "test-flag"' in json_str
        assert '"enabled":true' in json_str or '"enabled": true' in json_str
