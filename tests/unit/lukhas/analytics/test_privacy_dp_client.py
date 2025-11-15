"""
Comprehensive test suite for differential privacy PrivacyClient.

Tests differential privacy mechanisms, anonymization, privacy budget tracking,
and GDPR compliance features.

Coverage target: >85%
"""

import warnings
from datetime import datetime
from unittest.mock import patch

import numpy as np
import pytest

from lukhas.analytics.privacy_client import (
    AggregateStats,
    DPMechanism,
    PIIAnonymizer,
    PrivacyClient,
)


# ============================================================================
# Test PIIAnonymizer
# ============================================================================


class TestPIIAnonymizer:
    """Tests for PII anonymization utilities."""

    def test_anonymize_removes_email(self):
        """Test email field is removed."""
        event = {"email": "user@example.com", "action": "click"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "email" not in anonymized
        assert "action" in anonymized

    def test_anonymize_removes_user_id(self):
        """Test user_id field is removed."""
        event = {"user_id": "12345", "action": "view"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "user_id" not in anonymized
        assert "action" in anonymized

    def test_anonymize_removes_ip(self):
        """Test IP address fields are removed."""
        event = {"ip": "192.168.1.1", "ip_address": "10.0.0.1", "action": "login"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "ip" not in anonymized
        assert "ip_address" not in anonymized
        assert "action" in anonymized

    def test_anonymize_removes_multiple_pii_fields(self):
        """Test multiple PII fields are removed."""
        event = {
            "email": "test@test.com",
            "phone": "555-1234",
            "ssn": "123-45-6789",
            "action": "signup"
        }
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "email" not in anonymized
        assert "phone" not in anonymized
        assert "ssn" not in anonymized
        assert "action" in anonymized

    def test_anonymize_generalizes_timestamp(self):
        """Test timestamps are generalized to hour granularity."""
        event = {"timestamp": "2024-01-15T14:23:45.123456"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "timestamp" in anonymized
        # Should be generalized to hour
        assert anonymized["timestamp"] == "2024-01-15T14:00:00"

    def test_anonymize_generalizes_datetime_object(self):
        """Test datetime objects are generalized."""
        dt = datetime(2024, 1, 15, 14, 23, 45, 123456)
        event = {"created_at": dt}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "created_at" in anonymized
        assert "14:00:00" in anonymized["created_at"]
        assert "14:23:45" not in anonymized["created_at"]

    def test_anonymize_hashes_id_fields(self):
        """Test fields ending in _id are hashed."""
        event = {"session_id": "abc123xyz", "action": "click"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "session_id" in anonymized
        # Should be hashed (16 char hex)
        assert anonymized["session_id"] != "abc123xyz"
        assert len(anonymized["session_id"]) == 16

    def test_anonymize_redacts_email_in_text(self):
        """Test email patterns in text are redacted."""
        event = {"message": "Contact me at user@example.com for details"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "[EMAIL_REDACTED]" in anonymized["message"]
        assert "user@example.com" not in anonymized["message"]

    def test_anonymize_redacts_ip_in_text(self):
        """Test IP patterns in text are redacted."""
        event = {"log": "Request from 192.168.1.100"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "[IP_REDACTED]" in anonymized["log"]
        assert "192.168.1.100" not in anonymized["log"]

    def test_anonymize_redacts_phone_in_text(self):
        """Test phone patterns in text are redacted."""
        event = {"note": "Call me at (555) 123-4567"}
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert "[PHONE_REDACTED]" in anonymized["note"]
        assert "555" not in anonymized["note"]

    def test_anonymize_preserves_safe_fields(self):
        """Test safe fields are preserved."""
        event = {
            "action": "click",
            "category": "button",
            "count": 5,
            "enabled": True
        }
        anonymized = PIIAnonymizer.anonymize_event(event)

        assert anonymized == event

    def test_hash_identifier_is_deterministic(self):
        """Test hashing produces consistent results."""
        hash1 = PIIAnonymizer._hash_identifier("test123")
        hash2 = PIIAnonymizer._hash_identifier("test123")
        assert hash1 == hash2

    def test_hash_identifier_is_different_for_different_values(self):
        """Test different values produce different hashes."""
        hash1 = PIIAnonymizer._hash_identifier("value1")
        hash2 = PIIAnonymizer._hash_identifier("value2")
        assert hash1 != hash2


# ============================================================================
# Test DPMechanism
# ============================================================================


class TestDPMechanism:
    """Tests for differential privacy noise mechanisms."""

    def test_laplace_noise_adds_noise(self):
        """Test Laplace mechanism adds noise to value."""
        value = 100.0
        noisy_value, noise = DPMechanism.add_laplace_noise(
            value, sensitivity=1.0, epsilon=1.0
        )

        assert noisy_value != value
        assert noisy_value == value + noise

    def test_laplace_noise_scale_depends_on_epsilon(self):
        """Test smaller epsilon produces more noise."""
        np.random.seed(42)
        _, noise_low_privacy = DPMechanism.add_laplace_noise(
            100.0, sensitivity=1.0, epsilon=0.1
        )

        np.random.seed(42)
        _, noise_high_privacy = DPMechanism.add_laplace_noise(
            100.0, sensitivity=1.0, epsilon=10.0
        )

        # Lower epsilon (more privacy) should have larger scale
        # Both noise values will be the same in magnitude due to seed,
        # but the scale (sensitivity/epsilon) is what matters
        # With same random draw, noise = scale * draw
        # So noise_low should be 100x larger than noise_high
        assert abs(noise_low_privacy) > abs(noise_high_privacy)

    def test_laplace_noise_scale_depends_on_sensitivity(self):
        """Test higher sensitivity produces more noise."""
        np.random.seed(42)
        _, noise_low_sens = DPMechanism.add_laplace_noise(
            100.0, sensitivity=1.0, epsilon=1.0
        )

        np.random.seed(42)
        _, noise_high_sens = DPMechanism.add_laplace_noise(
            100.0, sensitivity=10.0, epsilon=1.0
        )

        assert abs(noise_high_sens) > abs(noise_low_sens)

    def test_gaussian_noise_adds_noise(self):
        """Test Gaussian mechanism adds noise to value."""
        value = 100.0
        noisy_value, noise = DPMechanism.add_gaussian_noise(
            value, sensitivity=1.0, epsilon=1.0, delta=1e-5
        )

        assert noisy_value != value
        assert noisy_value == value + noise

    def test_gaussian_noise_scale_depends_on_epsilon(self):
        """Test smaller epsilon produces more noise in Gaussian mechanism."""
        np.random.seed(42)
        _, noise_low_privacy = DPMechanism.add_gaussian_noise(
            100.0, sensitivity=1.0, epsilon=0.1, delta=1e-5
        )

        np.random.seed(42)
        _, noise_high_privacy = DPMechanism.add_gaussian_noise(
            100.0, sensitivity=1.0, epsilon=10.0, delta=1e-5
        )

        assert abs(noise_low_privacy) > abs(noise_high_privacy)

    def test_gaussian_noise_scale_depends_on_delta(self):
        """Test smaller delta produces more noise."""
        np.random.seed(42)
        _, noise_low_delta = DPMechanism.add_gaussian_noise(
            100.0, sensitivity=1.0, epsilon=1.0, delta=1e-10
        )

        np.random.seed(42)
        _, noise_high_delta = DPMechanism.add_gaussian_noise(
            100.0, sensitivity=1.0, epsilon=1.0, delta=1e-3
        )

        # Lower delta (more privacy) needs more noise
        assert abs(noise_low_delta) > abs(noise_high_delta)


# ============================================================================
# Test PrivacyClient
# ============================================================================


class TestPrivacyClient:
    """Tests for PrivacyClient with differential privacy."""

    def test_init_default_params(self):
        """Test client initializes with default parameters."""
        client = PrivacyClient()

        assert client.epsilon == 1.0
        assert client.delta == 1e-5
        assert client.mechanism == "laplace"
        assert client.max_budget == 10.0
        assert client.privacy_budget_used == 0.0
        assert len(client.events) == 0

    def test_init_custom_params(self):
        """Test client initializes with custom parameters."""
        client = PrivacyClient(
            epsilon=0.5,
            delta=1e-6,
            mechanism="gaussian",
            max_budget=5.0
        )

        assert client.epsilon == 0.5
        assert client.delta == 1e-6
        assert client.mechanism == "gaussian"
        assert client.max_budget == 5.0

    def test_init_invalid_epsilon(self):
        """Test initialization fails with invalid epsilon."""
        with pytest.raises(ValueError, match="epsilon must be positive"):
            PrivacyClient(epsilon=0)

        with pytest.raises(ValueError, match="epsilon must be positive"):
            PrivacyClient(epsilon=-1)

    def test_init_invalid_delta(self):
        """Test initialization fails with invalid delta."""
        with pytest.raises(ValueError, match="delta must be in"):
            PrivacyClient(delta=0)

        with pytest.raises(ValueError, match="delta must be in"):
            PrivacyClient(delta=1.5)

    def test_init_invalid_mechanism(self):
        """Test initialization fails with invalid mechanism."""
        with pytest.raises(ValueError, match="mechanism must be"):
            PrivacyClient(mechanism="invalid")

    def test_log_event_stores_event(self):
        """Test logging event stores it."""
        client = PrivacyClient()
        client.log_event({"action": "click"})

        assert len(client.events) == 1
        assert "action" in client.events[0]

    def test_log_event_anonymizes_by_default(self):
        """Test logging anonymizes PII by default."""
        client = PrivacyClient()
        client.log_event({"email": "user@test.com", "action": "click"})

        assert len(client.events) == 1
        assert "email" not in client.events[0]
        assert "action" in client.events[0]

    def test_log_event_can_skip_anonymization(self):
        """Test can disable anonymization."""
        client = PrivacyClient()
        client.log_event({"email": "user@test.com"}, anonymize=False)

        assert "email" in client.events[0]

    def test_log_event_adds_timestamp(self):
        """Test logging adds logged_at timestamp."""
        client = PrivacyClient()
        client.log_event({"action": "click"})

        assert "_logged_at" in client.events[0]

    def test_get_stats_count(self):
        """Test getting noisy count."""
        client = PrivacyClient(epsilon=1.0)

        # Log 10 events
        for i in range(10):
            client.log_event({"action": "click"})

        stats = client.get_stats("count")

        assert stats.aggregation_type == "count"
        assert isinstance(stats.value, float)
        # Should be close to 10, but noisy
        assert 0 <= stats.value <= 50  # Wide range due to noise
        assert stats.epsilon_used == 1.0
        assert stats.sensitivity == 1.0

    def test_get_stats_count_updates_budget(self):
        """Test count query updates privacy budget."""
        client = PrivacyClient(epsilon=1.0)
        client.log_event({"action": "click"})

        assert client.privacy_budget_used == 0.0

        client.get_stats("count")

        assert client.privacy_budget_used == 1.0

    def test_get_stats_sum(self):
        """Test getting noisy sum."""
        client = PrivacyClient(epsilon=1.0)

        # Log events with numeric values
        for i in range(5):
            client.log_event({"amount": 0.5})  # Sum should be 2.5

        stats = client.get_stats("sum", column="amount")

        assert stats.aggregation_type == "sum"
        assert isinstance(stats.value, float)
        # Should be close to 2.5, but noisy
        assert -5 <= stats.value <= 10
        assert stats.count == 5

    def test_get_stats_mean(self):
        """Test getting noisy mean."""
        client = PrivacyClient(epsilon=1.0)

        # Log events
        for i in range(10):
            client.log_event({"score": 0.7})

        stats = client.get_stats("mean", column="score")

        assert stats.aggregation_type == "mean"
        assert isinstance(stats.value, float)
        # Should be close to 0.7, but noisy
        assert -1 <= stats.value <= 2
        assert stats.epsilon_used == 1.0

    def test_get_stats_histogram(self):
        """Test getting noisy histogram."""
        client = PrivacyClient(epsilon=1.0)

        # Log events with categorical values
        for _ in range(5):
            client.log_event({"browser": "chrome"})
        for _ in range(3):
            client.log_event({"browser": "firefox"})

        stats = client.get_stats("histogram", column="browser")

        assert stats.aggregation_type == "histogram"
        assert isinstance(stats.value, dict)
        assert "chrome" in stats.value
        assert "firefox" in stats.value
        # Values should be noisy but non-negative
        assert stats.value["chrome"] >= 0
        assert stats.value["firefox"] >= 0

    def test_get_stats_invalid_aggregation_type(self):
        """Test invalid aggregation type raises error."""
        client = PrivacyClient()

        with pytest.raises(ValueError, match="Invalid aggregation_type"):
            client.get_stats("invalid")

    def test_get_stats_requires_column_for_mean(self):
        """Test mean requires column parameter."""
        client = PrivacyClient()
        client.log_event({"value": 1})

        with pytest.raises(ValueError, match="requires column"):
            client.get_stats("mean")

    def test_get_stats_requires_column_for_sum(self):
        """Test sum requires column parameter."""
        client = PrivacyClient()
        client.log_event({"value": 1})

        with pytest.raises(ValueError, match="requires column"):
            client.get_stats("sum")

    def test_get_stats_requires_column_for_histogram(self):
        """Test histogram requires column parameter."""
        client = PrivacyClient()
        client.log_event({"category": "a"})

        with pytest.raises(ValueError, match="requires column"):
            client.get_stats("histogram")

    def test_get_stats_custom_epsilon(self):
        """Test using custom epsilon for query."""
        client = PrivacyClient(epsilon=1.0)
        client.log_event({"action": "click"})

        stats = client.get_stats("count", epsilon=0.5)

        assert stats.epsilon_used == 0.5
        assert client.privacy_budget_used == 0.5

    def test_get_stats_warns_on_budget_exceeded(self):
        """Test warning when budget is nearly exhausted."""
        client = PrivacyClient(epsilon=1.0, max_budget=2.0)
        client.log_event({"action": "click"})

        # Use up most of budget
        client.get_stats("count", epsilon=1.5)

        # This should trigger warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.get_stats("count", epsilon=1.0)

            assert len(w) == 1
            assert "budget nearly exhausted" in str(w[0].message).lower()

    def test_get_stats_with_empty_data(self):
        """Test queries on empty dataset."""
        client = PrivacyClient()

        stats = client.get_stats("count")

        # Should return noisy zero
        assert stats.value >= 0
        assert stats.count >= 0

    def test_get_stats_sum_with_no_matching_column(self):
        """Test sum with non-existent column."""
        client = PrivacyClient()
        client.log_event({"action": "click"})

        stats = client.get_stats("sum", column="nonexistent")

        assert stats.value == 0.0
        assert stats.count == 0

    def test_check_privacy_budget_returns_remaining(self):
        """Test checking privacy budget."""
        client = PrivacyClient(epsilon=1.0, max_budget=10.0)

        assert client.check_privacy_budget() == 10.0

        client.get_stats("count")

        assert client.check_privacy_budget() == 9.0

    def test_check_privacy_budget_warns_when_low(self):
        """Test warning when budget is low."""
        client = PrivacyClient(epsilon=1.0, max_budget=2.0)
        client.privacy_budget_used = 1.5

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            remaining = client.check_privacy_budget()

            assert len(w) == 1
            assert "budget low" in str(w[0].message).lower()
            assert remaining == 0.5

    def test_clear_local_data_removes_events(self):
        """Test clearing data removes all events."""
        client = PrivacyClient()

        for i in range(10):
            client.log_event({"action": "click"})

        assert len(client.events) == 10

        client.clear_local_data()

        assert len(client.events) == 0

    def test_clear_local_data_resets_budget(self):
        """Test clearing data resets privacy budget."""
        client = PrivacyClient()
        client.log_event({"action": "click"})
        client.get_stats("count")

        assert client.privacy_budget_used > 0

        client.clear_local_data()

        assert client.privacy_budget_used == 0.0

    def test_get_privacy_report(self):
        """Test privacy transparency report."""
        client = PrivacyClient(epsilon=1.0, delta=1e-5, max_budget=10.0)

        report = client.get_privacy_report()

        assert "privacy_parameters" in report
        assert report["privacy_parameters"]["epsilon"] == 1.0
        assert report["privacy_parameters"]["delta"] == 1e-5
        assert report["privacy_parameters"]["mechanism"] == "laplace"

        assert "budget_status" in report
        assert report["budget_status"]["used"] == 0.0
        assert report["budget_status"]["remaining"] == 10.0

        assert "data_status" in report
        assert report["data_status"]["events_stored"] == 0

        assert "compliance" in report
        assert "privacy" in report["compliance"]["gdpr_article_25"].lower()

    def test_multiple_queries_compose_budget(self):
        """Test multiple queries compose privacy budget."""
        client = PrivacyClient(epsilon=1.0)
        client.log_event({"action": "click", "score": 0.5})

        client.get_stats("count", epsilon=0.5)
        assert client.privacy_budget_used == 0.5

        client.get_stats("sum", column="score", epsilon=0.3)
        assert client.privacy_budget_used == 0.8

        client.get_stats("count", epsilon=0.2)
        assert client.privacy_budget_used == 1.0

    def test_laplace_vs_gaussian_mechanism(self):
        """Test both Laplace and Gaussian mechanisms work."""
        # Test Laplace
        client_laplace = PrivacyClient(mechanism="laplace")
        for i in range(10):
            client_laplace.log_event({"action": "click"})
        stats_laplace = client_laplace.get_stats("count")
        assert stats_laplace.value >= 0

        # Test Gaussian
        client_gaussian = PrivacyClient(mechanism="gaussian")
        for i in range(10):
            client_gaussian.log_event({"action": "click"})
        stats_gaussian = client_gaussian.get_stats("count")
        assert stats_gaussian.value >= 0

    def test_numeric_extraction_clips_values(self):
        """Test numeric values are clipped to [0, 1]."""
        client = PrivacyClient()

        # Values outside [0, 1]
        client.log_event({"value": 5.0})
        client.log_event({"value": -2.0})
        client.log_event({"value": 0.5})

        values = client._extract_numeric_column("value")

        # Should be clipped
        assert all(0 <= v <= 1 for v in values)
        assert 1.0 in values  # 5.0 clipped to 1.0
        assert 0.0 in values  # -2.0 clipped to 0.0
        assert 0.5 in values

    def test_numeric_extraction_ignores_non_numeric(self):
        """Test non-numeric values are ignored."""
        client = PrivacyClient()

        client.log_event({"value": "text"})
        client.log_event({"value": None})
        client.log_event({"value": 0.5})

        values = client._extract_numeric_column("value")

        assert len(values) == 1
        assert values[0] == 0.5


# ============================================================================
# Integration Tests
# ============================================================================


class TestPrivacyClientIntegration:
    """Integration tests for complete workflows."""

    def test_full_analytics_workflow(self):
        """Test complete analytics workflow with privacy."""
        client = PrivacyClient(epsilon=1.0, max_budget=5.0)

        # Log various events
        events = [
            {"user_id": "user1", "action": "view", "score": 0.8},
            {"user_id": "user2", "action": "click", "score": 0.6},
            {"user_id": "user3", "action": "view", "score": 0.9},
            {"user_id": "user1", "action": "click", "score": 0.7},
        ]

        for event in events:
            client.log_event(event)

        # Verify PII removed
        for stored_event in client.events:
            assert "user_id" not in stored_event

        # Get statistics
        count_stats = client.get_stats("count", epsilon=1.0)
        assert count_stats.value >= 0

        mean_stats = client.get_stats("mean", column="score", epsilon=1.0)
        assert mean_stats.value is not None

        histogram_stats = client.get_stats("histogram", column="action", epsilon=1.0)
        assert isinstance(histogram_stats.value, dict)

        # Check budget
        assert client.privacy_budget_used == 3.0
        assert client.check_privacy_budget() == 2.0

    def test_gdpr_compliance_workflow(self):
        """Test GDPR right to erasure workflow."""
        client = PrivacyClient()

        # Log events
        for i in range(50):
            client.log_event({"action": "click"})

        # Run queries
        client.get_stats("count")

        assert len(client.events) == 50
        assert client.privacy_budget_used > 0

        # User requests data deletion (GDPR Article 17)
        client.clear_local_data()

        assert len(client.events) == 0
        assert client.privacy_budget_used == 0.0

    def test_privacy_budget_exhaustion(self):
        """Test behavior when privacy budget is exhausted."""
        client = PrivacyClient(epsilon=1.0, max_budget=2.0)
        client.log_event({"action": "click"})

        # Use budget
        client.get_stats("count", epsilon=0.8)
        client.get_stats("count", epsilon=0.8)

        # Budget should be nearly exhausted
        assert client.privacy_budget_used == 1.6

        # This should warn
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.get_stats("count", epsilon=0.8)
            assert len(w) == 1

        # Budget exceeded but still works (warning only)
        assert abs(client.privacy_budget_used - 2.4) < 0.001  # Floating point comparison
