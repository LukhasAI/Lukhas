"""
Tests for privacy-first analytics client.

Coverage:
- PII detection and redaction
- Consent checking
- Event batching
- Circuit breaker
- IP anonymization
- User-Agent normalization
"""

import pytest
from datetime import datetime
from lukhas.analytics.privacy_client import (
    PrivacyAnalyticsClient,
    PIIDetector,
    IPAnonymizer,
    UserAgentNormalizer,
    ConsentMode,
    ConsentCategory,
    CircuitBreakerState,
)


class TestPIIDetector:
    """Test PII detection and redaction."""

    def test_detect_email(self):
        """Test email detection."""
        text = "Contact me at user@example.com"
        assert PIIDetector.detect_pii(text) is True

    def test_detect_phone(self):
        """Test phone number detection."""
        text = "Call me at +1-555-0100"
        assert PIIDetector.detect_pii(text) is True

    def test_detect_ip(self):
        """Test IP address detection."""
        text = "Server at 192.168.1.1"
        assert PIIDetector.detect_pii(text) is True

    def test_detect_credit_card(self):
        """Test credit card detection."""
        text = "Card: 4111-1111-1111-1111"
        assert PIIDetector.detect_pii(text) is True

    def test_detect_ssn(self):
        """Test SSN detection."""
        text = "SSN: 123-45-6789"
        assert PIIDetector.detect_pii(text) is True

    def test_no_pii(self):
        """Test clean text."""
        text = "This is a clean message"
        assert PIIDetector.detect_pii(text) is False

    def test_redact_email(self):
        """Test email redaction."""
        text = "Contact user@example.com"
        redacted = PIIDetector.redact_pii(text)
        assert "[EMAIL_REDACTED]" in redacted
        assert "user@example.com" not in redacted

    def test_redact_phone(self):
        """Test phone redaction."""
        text = "Call +1-555-0100"
        redacted = PIIDetector.redact_pii(text)
        assert "[PHONE_REDACTED]" in redacted

    def test_sanitize_properties(self):
        """Test property sanitization."""
        properties = {
            "clean": "safe text",
            "email": "user@example.com",
            "nested": {
                "phone": "+1-555-0100",
            },
        }

        sanitized = PIIDetector.sanitize_properties(properties)

        assert sanitized["clean"] == "safe text"
        assert "[EMAIL_REDACTED]" in sanitized["email"]
        assert "[PHONE_REDACTED]" in sanitized["nested"]["phone"]


class TestIPAnonymizer:
    """Test IP anonymization."""

    def test_anonymize_ipv4(self):
        """Test IPv4 anonymization."""
        ip = "192.168.1.100"
        anonymized = IPAnonymizer.anonymize_ipv4(ip)
        assert anonymized == "192.168.1.0"

    def test_anonymize_ipv6(self):
        """Test IPv6 anonymization."""
        ip = "2001:db8:85a3:8d3:1319:8a2e:370:7348"
        anonymized = IPAnonymizer.anonymize_ipv6(ip)
        assert "::0" in anonymized


class TestUserAgentNormalizer:
    """Test User-Agent normalization."""

    def test_normalize_chrome(self):
        """Test Chrome detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        normalized = UserAgentNormalizer.normalize(ua)
        assert normalized == "chrome"

    def test_normalize_firefox(self):
        """Test Firefox detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        normalized = UserAgentNormalizer.normalize(ua)
        assert normalized == "firefox"

    def test_normalize_safari(self):
        """Test Safari detection."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        normalized = UserAgentNormalizer.normalize(ua)
        assert normalized == "safari"

    def test_normalize_unknown(self):
        """Test unknown browser."""
        ua = "CustomBrowser/1.0"
        normalized = UserAgentNormalizer.normalize(ua)
        assert normalized == "other"


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_initial_state_closed(self):
        """Test initial state is closed."""
        cb = CircuitBreakerState()
        assert cb.state == "closed"
        assert cb.should_allow_request() is True

    def test_open_after_failures(self):
        """Test circuit opens after threshold."""
        cb = CircuitBreakerState()

        # Record failures
        for _ in range(5):
            cb.record_failure(failure_threshold=5)

        assert cb.state == "open"
        assert cb.should_allow_request() is False

    def test_close_on_success(self):
        """Test circuit closes on success."""
        cb = CircuitBreakerState()

        # Open circuit
        for _ in range(5):
            cb.record_failure(failure_threshold=5)

        # Recover
        cb.record_success()

        assert cb.state == "closed"
        assert cb.failure_count == 0


class TestPrivacyAnalyticsClient:
    """Test privacy analytics client."""

    def test_initialization(self):
        """Test client initialization."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")

        assert client.endpoint == "https://test.com/events"
        assert client._consent[ConsentCategory.ANALYTICS] == ConsentMode.DENIED
        assert client._consent[ConsentCategory.FUNCTIONAL] == ConsentMode.GRANTED

    def test_set_consent(self):
        """Test consent management."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")

        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        assert client.has_analytics_consent() is True

    def test_track_without_consent(self):
        """Test tracking fails without consent."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")

        # No consent granted
        result = client.track("page_view", {"domain": "lukhas.ai"})

        assert result is False

    def test_track_with_consent(self):
        """Test tracking succeeds with consent."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")

        # Grant consent
        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        # Track event
        result = client.track("page_view", {"domain": "lukhas.ai", "path": "/"})

        assert result is True
        assert len(client._current_batch.events) == 1

    def test_track_invalid_event(self):
        """Test tracking invalid event fails."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")
        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        with pytest.raises(ValueError, match="not in allowed taxonomy"):
            client.track("invalid_event", {"domain": "lukhas.ai"})

    def test_pii_redaction_in_tracking(self):
        """Test PII is automatically redacted."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")
        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        # Track with PII
        client.track(
            "page_view",
            {
                "domain": "lukhas.ai",
                "referrer": "https://example.com?email=user@example.com",
            },
        )

        event = client._current_batch.events[0]
        assert "[EMAIL_REDACTED]" in event["properties"]["referrer"]

    def test_batching(self):
        """Test event batching."""
        client = PrivacyAnalyticsClient(
            endpoint="https://test.com/events",
            batch_size=3,
        )
        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        # Track 3 events (should trigger batch)
        for i in range(3):
            client.track("page_view", {"domain": "lukhas.ai", "path": f"/{i}"})

        # Current batch should be empty (queued)
        assert len(client._current_batch.events) == 0
        assert len(client._pending_batches) == 1

    def test_export_data(self):
        """Test data export."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")
        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        client.track("page_view", {"domain": "lukhas.ai"})

        data = client.export_data()

        assert "events" in data
        assert "consent" in data
        assert "exported_at" in data
        assert len(data["events"]) == 1

    def test_clear_data(self):
        """Test data deletion."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")
        client.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

        client.track("page_view", {"domain": "lukhas.ai"})
        assert len(client._current_batch.events) == 1

        client.clear_data()
        assert len(client._current_batch.events) == 0
        assert len(client._pending_batches) == 0


class TestConsentModes:
    """Test consent mode handling."""

    def test_default_denied(self):
        """Test default consent is denied."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")

        assert client.get_consent(ConsentCategory.ANALYTICS) == ConsentMode.DENIED
        assert client.get_consent(ConsentCategory.MARKETING) == ConsentMode.DENIED

    def test_functional_always_granted(self):
        """Test functional consent is always granted."""
        client = PrivacyAnalyticsClient(endpoint="https://test.com/events")

        assert client.get_consent(ConsentCategory.FUNCTIONAL) == ConsentMode.GRANTED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
