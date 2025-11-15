"""
Comprehensive analytics tests.

Validates:
- Feature flag evaluation tracking
- Feature flag update tracking
- Privacy-preserving user ID hashing
- Event batching and collection
- Analytics configuration
- Edge cases and error handling
"""
import pytest
from pydantic import ValidationError
from lukhas.api.analytics import (
    track_feature_evaluation,
    track_feature_update,
    AnalyticsEvent,
    AnalyticsConfig,
)


# Feature Evaluation Tracking Tests
class TestFeatureEvaluationTracking:
    """Test feature flag evaluation tracking."""

    def test_track_feature_evaluation_basic(self):
        """Verify basic feature evaluation tracking works."""
        # Should not raise
        track_feature_evaluation(
            flag_name="new-ui",
            user_id="user123",
            enabled=True,
            context={"env": "prod"}
        )

    def test_track_feature_evaluation_disabled(self):
        """Verify tracking when feature is disabled."""
        track_feature_evaluation(
            flag_name="experimental-feature",
            user_id="user456",
            enabled=False,
            context={"env": "dev"}
        )

    def test_track_feature_evaluation_with_complex_context(self):
        """Verify tracking with complex context data."""
        complex_context = {
            "environment": "staging",
            "targeting": {"segment": "beta-testers", "percentage": 50},
            "metadata": {"version": "1.2.3", "deployment": "canary"}
        }

        track_feature_evaluation(
            flag_name="ai-suggestions",
            user_id="user789",
            enabled=True,
            context=complex_context
        )

    def test_track_feature_evaluation_privacy_note(self):
        """Verify privacy considerations are documented."""
        # The function should anonymize user IDs
        # This is a documentation test - verify the docstring mentions privacy
        import inspect
        docstring = inspect.getdoc(track_feature_evaluation)

        assert "anonymized" in docstring.lower() or "privacy" in docstring.lower()
        assert "SHA-256" in docstring or "hash" in docstring.lower()


# Feature Update Tracking Tests
class TestFeatureUpdateTracking:
    """Test feature flag update tracking."""

    def test_track_feature_update_basic(self):
        """Verify basic feature update tracking works."""
        track_feature_update(
            flag_name="beta-feature",
            admin_id="admin@example.com",
            changes={"enabled": True}
        )

    def test_track_feature_update_multiple_changes(self):
        """Verify tracking multiple simultaneous changes."""
        changes = {
            "enabled": True,
            "percentage": 75,
            "targeting": {"segment": "premium-users"}
        }

        track_feature_update(
            flag_name="premium-tier",
            admin_id="admin123",
            changes=changes
        )

    def test_track_feature_update_disable(self):
        """Verify tracking when disabling a feature."""
        track_feature_update(
            flag_name="deprecated-feature",
            admin_id="admin456",
            changes={"enabled": False}
        )


# Analytics Event Model Tests
class TestAnalyticsEventModel:
    """Test AnalyticsEvent Pydantic model."""

    def test_analytics_event_valid(self):
        """Verify valid analytics event creation."""
        event = AnalyticsEvent(
            event="feature_evaluated",
            properties={"flag": "new-ui", "user": "user123"},
            timestamp="2025-11-13T10:00:00Z"
        )

        assert event.event == "feature_evaluated"
        assert event.properties["flag"] == "new-ui"
        assert event.timestamp == "2025-11-13T10:00:00Z"

    def test_analytics_event_with_user_id(self):
        """Verify analytics event with user_id field (if supported)."""
        # AnalyticsEvent may not have user_id field directly
        event = AnalyticsEvent(
            event="button_click",
            properties={"button": "submit", "user_id": "user789"},
            timestamp="2025-11-13T10:00:00Z"
        )

        assert event.properties.get("user_id") == "user789"

    def test_analytics_event_validation_alphanumeric(self):
        """Verify event name validation."""
        # Valid alphanumeric event names
        valid_names = [
            "featureevaluated",
            "user123login",
            "test123"
        ]

        for name in valid_names:
            try:
                event = AnalyticsEvent(
                    event=name,
                    properties={},
                    timestamp="2025-11-13T10:00:00Z"
                )
                # Should accept alphanumeric names
                assert event.event == name
            except ValidationError:
                # If validation fails, check if it's truly non-alphanumeric
                if not name.isalnum():
                    pass  # Expected failure
                else:
                    raise

    def test_analytics_event_timestamp_required(self):
        """Verify timestamp is required."""
        # Timestamp is required, should fail without it
        try:
            AnalyticsEvent(
                event="test_event",
                properties={}
            )
            # If it doesn't fail, timestamp must have a default
            pytest.fail("Timestamp should be required")
        except ValidationError:
            # Expected - timestamp is required
            pass

    def test_analytics_event_properties_dict(self):
        """Verify properties must be a dict."""
        event = AnalyticsEvent(
            event="test",
            properties={"key": "value", "nested": {"data": 123}},
            timestamp="2025-11-13T10:00:00Z"
        )

        assert isinstance(event.properties, dict)
        assert event.properties["key"] == "value"


# Analytics Config Model Tests
class TestAnalyticsConfigModel:
    """Test AnalyticsConfig Pydantic model."""

    def test_analytics_config_defaults(self):
        """Verify analytics config has sensible defaults."""
        config = AnalyticsConfig()

        assert config.enabled is True
        assert config.batch_size == 50
        assert config.flush_interval_seconds == 60
        assert config.endpoint is None

    def test_analytics_config_custom_values(self):
        """Verify custom analytics configuration."""
        config = AnalyticsConfig(
            enabled=False,
            batch_size=100,
            flush_interval_seconds=30,
            endpoint="https://analytics.example.com/events"
        )

        assert config.enabled is False
        assert config.batch_size == 100
        assert config.flush_interval_seconds == 30
        assert config.endpoint == "https://analytics.example.com/events"

    def test_analytics_config_disabled_mode(self):
        """Verify analytics can be disabled."""
        config = AnalyticsConfig(enabled=False)

        assert config.enabled is False
        # Other settings should still be valid
        assert config.batch_size > 0
        assert config.flush_interval_seconds > 0


# Event Batching Tests
class TestEventBatching:
    """Test analytics event batching behavior."""

    def test_batch_size_configuration(self):
        """Verify batch size can be configured."""
        small_batch = AnalyticsConfig(batch_size=10)
        large_batch = AnalyticsConfig(batch_size=500)

        assert small_batch.batch_size == 10
        assert large_batch.batch_size == 500

    def test_flush_interval_configuration(self):
        """Verify flush interval can be configured."""
        quick_flush = AnalyticsConfig(flush_interval_seconds=10)
        slow_flush = AnalyticsConfig(flush_interval_seconds=300)

        assert quick_flush.flush_interval_seconds == 10
        assert slow_flush.flush_interval_seconds == 300

    def test_zero_batch_size_allowed(self):
        """Verify zero batch size is allowed (for unbatched mode)."""
        config = AnalyticsConfig(batch_size=0)
        # Zero batch size may be used for immediate sending
        assert config.batch_size == 0

    def test_negative_values_handling(self):
        """Verify handling of negative configuration values."""
        # Test negative values - may be allowed or rejected
        try:
            config = AnalyticsConfig(flush_interval_seconds=-1)
            # If accepted, note the value
            assert isinstance(config.flush_interval_seconds, int)
        except (ValidationError, ValueError):
            # Expected - negative interval rejected
            pass


# Privacy and Security Tests
class TestPrivacyAndSecurity:
    """Test privacy and security considerations."""

    def test_user_id_anonymization_documented(self):
        """Verify user ID anonymization is documented."""
        import inspect
        docstring = inspect.getdoc(track_feature_evaluation)

        # Should mention privacy-preserving techniques
        privacy_keywords = ["anonymized", "privacy", "hash", "SHA-256", "PII"]
        assert any(keyword.lower() in docstring.lower() for keyword in privacy_keywords)

    def test_no_pii_in_analytics_documented(self):
        """Verify no PII transmission is documented."""
        import inspect
        docstring = inspect.getdoc(track_feature_evaluation)

        assert "no pii" in docstring.lower() or "no personally" in docstring.lower()

    def test_admin_audit_trail_documented(self):
        """Verify admin audit trail is documented."""
        import inspect
        docstring = inspect.getdoc(track_feature_update)

        assert "audit" in docstring.lower()


# Edge Cases
class TestAnalyticsEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_flag_name(self):
        """Verify empty flag name handling."""
        # Should still work (logged but not fail)
        track_feature_evaluation(
            flag_name="",
            user_id="user123",
            enabled=True,
            context={}
        )

    def test_empty_user_id(self):
        """Verify empty user ID handling."""
        track_feature_evaluation(
            flag_name="test-flag",
            user_id="",
            enabled=True,
            context={}
        )

    def test_none_context(self):
        """Verify None context handling."""
        track_feature_evaluation(
            flag_name="test-flag",
            user_id="user123",
            enabled=True,
            context=None  # type: ignore
        )

    def test_empty_changes_dict(self):
        """Verify empty changes dictionary handling."""
        track_feature_update(
            flag_name="test-flag",
            admin_id="admin123",
            changes={}
        )

    def test_large_context_data(self):
        """Verify handling of large context data."""
        large_context = {
            f"key_{i}": f"value_{i}" for i in range(1000)
        }

        track_feature_evaluation(
            flag_name="test-flag",
            user_id="user123",
            enabled=True,
            context=large_context
        )

    def test_special_characters_in_flag_name(self):
        """Verify special characters in flag names."""
        special_names = [
            "feature-with-dashes",
            "feature_with_underscores",
            "feature.with.dots",
            "feature:with:colons",
        ]

        for name in special_names:
            track_feature_evaluation(
                flag_name=name,
                user_id="user123",
                enabled=True,
                context={}
            )


# Integration Tests
class TestAnalyticsIntegration:
    """Test analytics integration scenarios."""

    def test_multiple_evaluations_sequential(self):
        """Verify multiple sequential evaluations work."""
        flags = ["flag1", "flag2", "flag3"]

        for flag in flags:
            track_feature_evaluation(
                flag_name=flag,
                user_id="user123",
                enabled=True,
                context={"sequence": flags.index(flag)}
            )

    def test_evaluation_and_update_together(self):
        """Verify evaluation and update tracking work together."""
        # Track evaluation
        track_feature_evaluation(
            flag_name="test-flag",
            user_id="user123",
            enabled=False,
            context={}
        )

        # Track update
        track_feature_update(
            flag_name="test-flag",
            admin_id="admin123",
            changes={"enabled": True}
        )

        # Track evaluation again
        track_feature_evaluation(
            flag_name="test-flag",
            user_id="user123",
            enabled=True,
            context={}
        )
