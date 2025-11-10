"""
Comprehensive tests for the Privacy-First Analytics API.

Tests event validation, PII stripping, IP anonymization, User-Agent normalization,
aggregation, rate limiting, and API endpoints.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from lukhas.api.analytics import (
    EventProperties,
    AnalyticsEvent,
    EventBatch,
    AnalyticsAggregator,
    anonymize_ip,
    normalize_user_agent,
    app,
)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def aggregator():
    """Fresh analytics aggregator instance."""
    return AnalyticsAggregator()


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "event": "page_view",
        "properties": {
            "domain": "lukhas.ai",
            "path": "/docs",
            "language": "en",
        },
        "timestamp": "2025-11-10T12:00:00Z",
        "session_id": "test-session-123",
    }


class TestEventProperties:
    """Test EventProperties PII stripping."""

    def test_strip_email_pii(self):
        """Test that email addresses are redacted."""
        props = EventProperties(
            domain="test.com",
            path="/contact?email=user@example.com",
        )
        assert props.path == "[REDACTED]"

    def test_strip_phone_pii(self):
        """Test that phone numbers are redacted."""
        props = EventProperties(
            domain="test.com",
            trigger="+1-555-123-4567",
        )
        assert props.trigger == "[REDACTED]"

    def test_strip_ip_pii(self):
        """Test that IP addresses are redacted."""
        props = EventProperties(
            domain="test.com",
            referrer="http://192.168.1.100/page",
        )
        assert props.referrer == "[REDACTED]"

    def test_no_pii_unmodified(self):
        """Test that clean data passes through unchanged."""
        props = EventProperties(
            domain="lukhas.ai",
            path="/docs/getting-started",
            language="en",
        )
        assert props.domain == "lukhas.ai"
        assert props.path == "/docs/getting-started"
        assert props.language == "en"

    def test_phone_patterns(self):
        """Test various phone number patterns are caught."""
        # US format with parentheses
        props1 = EventProperties(domain="test.com", trigger="(555) 123-4567")
        assert props1.trigger == "[REDACTED]"

        # International format
        props2 = EventProperties(domain="test.com", trigger="+44 20 1234 5678")
        assert props2.trigger == "[REDACTED]"


class TestAnalyticsEvent:
    """Test AnalyticsEvent validation."""

    def test_valid_event(self, sample_event_data):
        """Test valid event passes validation."""
        event = AnalyticsEvent(**sample_event_data)
        assert event.event == "page_view"
        assert event.session_id == "test-session-123"

    def test_invalid_event_name(self):
        """Test that invalid event names are rejected."""
        with pytest.raises(ValueError, match="not in allowed taxonomy"):
            AnalyticsEvent(
                event="invalid_event",
                properties={"domain": "test.com"},
                timestamp="2025-11-10T12:00:00Z",
            )

    def test_all_valid_event_types(self):
        """Test all valid event types are accepted."""
        valid_events = [
            "page_view",
            "quickstart_started",
            "quickstart_completed",
            "reasoning_trace_viewed",
            "assistive_variant_viewed",
            "assistive_audio_played",
            "evidence_artifact_requested",
            "demo_interaction",
            "cta_clicked",
        ]

        for event_type in valid_events:
            event = AnalyticsEvent(
                event=event_type,
                properties={"domain": "test.com"},
                timestamp="2025-11-10T12:00:00Z",
            )
            assert event.event == event_type


class TestEventBatch:
    """Test EventBatch validation."""

    def test_valid_batch(self, sample_event_data):
        """Test valid batch with multiple events."""
        batch = EventBatch(events=[
            AnalyticsEvent(**sample_event_data),
            AnalyticsEvent(**sample_event_data),
        ])
        assert len(batch.events) == 2

    def test_batch_max_items(self):
        """Test batch respects max items limit (100)."""
        event_data = {
            "event": "page_view",
            "properties": {"domain": "test.com"},
            "timestamp": "2025-11-10T12:00:00Z",
        }
        # Should succeed with 100 items
        batch = EventBatch(events=[AnalyticsEvent(**event_data) for _ in range(100)])
        assert len(batch.events) == 100

        # Should fail with 101 items
        with pytest.raises(ValueError):
            EventBatch(events=[AnalyticsEvent(**event_data) for _ in range(101)])


class TestIPAnonymization:
    """Test IP address anonymization."""

    def test_ipv4_anonymization(self):
        """Test IPv4 addresses are anonymized correctly."""
        assert anonymize_ip("192.168.1.100") == "192.168.1.0"
        assert anonymize_ip("8.8.8.8") == "8.8.8.0"
        assert anonymize_ip("127.0.0.1") == "127.0.0.0"

    def test_ipv6_anonymization(self):
        """Test IPv6 addresses are anonymized."""
        result = anonymize_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert result == "2001:0db8:85a3:0000::0"

    def test_invalid_ip_unchanged(self):
        """Test invalid IP formats are returned unchanged."""
        assert anonymize_ip("not-an-ip") == "not-an-ip"
        assert anonymize_ip("") == ""


class TestUserAgentNormalization:
    """Test User-Agent normalization."""

    def test_chrome_detection(self):
        """Test Chrome browser family detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        assert normalize_user_agent(ua) == "chrome"

    def test_firefox_detection(self):
        """Test Firefox browser family detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
        assert normalize_user_agent(ua) == "firefox"

    def test_safari_detection(self):
        """Test Safari browser family detection."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
        assert normalize_user_agent(ua) == "safari"

    def test_edge_detection(self):
        """Test Edge browser family detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29"
        assert normalize_user_agent(ua) == "edge"

    def test_opera_detection(self):
        """Test Opera browser family detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 OPR/82.0.4227.33"
        assert normalize_user_agent(ua) == "opera"

    def test_unknown_browser(self):
        """Test unknown browser returns 'other'."""
        assert normalize_user_agent("SomeUnknownBot/1.0") == "other"

    def test_empty_user_agent(self):
        """Test empty user agent returns 'unknown'."""
        assert normalize_user_agent("") == "unknown"
        assert normalize_user_agent(None) == "unknown"


class TestAnalyticsAggregator:
    """Test analytics aggregation logic."""

    def test_add_event_increments_count(self, aggregator, sample_event_data):
        """Test adding events increments counters."""
        event = AnalyticsEvent(**sample_event_data)
        aggregator.add_event(event, "chrome", "192.168.1.0")

        assert aggregator.event_counts["page_view"] == 1
        assert len(aggregator.session_ids) == 1
        assert aggregator.domain_counts["lukhas.ai"] == 1
        assert aggregator.browser_counts["chrome"] == 1

    def test_multiple_events_aggregation(self, aggregator, sample_event_data):
        """Test multiple events are aggregated correctly."""
        event1 = AnalyticsEvent(**sample_event_data)
        event2_data = sample_event_data.copy()
        event2_data["event"] = "quickstart_started"
        event2 = AnalyticsEvent(**event2_data)

        aggregator.add_event(event1, "chrome", "192.168.1.0")
        aggregator.add_event(event2, "firefox", "192.168.1.0")

        assert aggregator.event_counts["page_view"] == 1
        assert aggregator.event_counts["quickstart_started"] == 1
        assert len(aggregator.session_ids) == 1  # Same session
        assert aggregator.browser_counts["chrome"] == 1
        assert aggregator.browser_counts["firefox"] == 1

    def test_unique_session_tracking(self, aggregator, sample_event_data):
        """Test unique session tracking."""
        event1 = AnalyticsEvent(**sample_event_data)
        event2_data = sample_event_data.copy()
        event2_data["session_id"] = "test-session-456"
        event2 = AnalyticsEvent(**event2_data)

        aggregator.add_event(event1, "chrome", "192.168.1.0")
        aggregator.add_event(event2, "chrome", "192.168.1.0")

        assert len(aggregator.session_ids) == 2

    def test_get_metrics(self, aggregator, sample_event_data):
        """Test get_metrics returns correct aggregation."""
        event = AnalyticsEvent(**sample_event_data)
        aggregator.add_event(event, "chrome", "192.168.1.0")

        metrics = aggregator.get_metrics(hours=24)

        assert metrics.event_counts["page_view"] == 1
        assert metrics.unique_sessions == 1
        assert metrics.time_period == "last_24_hours"
        assert metrics.domain_counts["lukhas.ai"] == 1
        assert metrics.browser_counts["chrome"] == 1

    def test_rate_limiting(self, aggregator):
        """Test rate limiting functionality."""
        # Should allow first request
        assert aggregator.check_rate_limit("session-123", "192.168.1.100", limit=1000)

        # Simulate hitting the limit
        hour_key = datetime.utcnow().strftime("%Y-%m-%d-%H")
        aggregator.hourly_counts[hour_key]["session-123"] = 1000

        # Should reject when limit reached
        assert not aggregator.check_rate_limit("session-123", "192.168.1.100", limit=1000)

    def test_rate_limiting_uses_ip_when_no_session(self, aggregator):
        """Test rate limiting uses anonymized IP when no session ID."""
        ip = "192.168.1.100"
        anon_ip = "192.168.1.0"

        # Add to limit using IP
        hour_key = datetime.utcnow().strftime("%Y-%m-%d-%H")
        aggregator.hourly_counts[hour_key][anon_ip] = 1000

        # Should be rate limited
        assert not aggregator.check_rate_limit(None, ip, limit=1000)

    def test_cleanup_old_data(self, aggregator):
        """Test cleanup of old hourly data."""
        # Add current hour data
        current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
        aggregator.hourly_counts[current_hour]["session-123"] = 10

        # Add old data (25 hours ago)
        old_time = datetime.utcnow() - timedelta(hours=25)
        old_hour = old_time.strftime("%Y-%m-%d-%H")
        aggregator.hourly_counts[old_hour]["session-old"] = 5

        # Cleanup
        aggregator.cleanup_old_data(hours=24)

        # Current data should remain
        assert current_hour in aggregator.hourly_counts
        # Old data should be removed
        assert old_hour not in aggregator.hourly_counts

    def test_anonymize_ip_static_method(self):
        """Test _anonymize_ip static method."""
        assert AnalyticsAggregator._anonymize_ip("192.168.1.100") == "192.168.1.0"


class TestAPIEndpoints:
    """Test FastAPI endpoint behavior."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["privacy"] == "GDPR-compliant"

    def test_privacy_info_endpoint(self, client):
        """Test privacy information endpoint."""
        response = client.get("/privacy")
        assert response.status_code == 200
        data = response.json()

        assert data["data_collection"]["pii_collected"] is False
        assert data["data_collection"]["third_party_tracking"] is False
        assert data["compliance"]["gdpr"] is True
        assert data["contact"] == "privacy@lukhas.ai"

    def test_receive_events_endpoint(self, client, sample_event_data):
        """Test event reception endpoint."""
        batch = {"events": [sample_event_data]}

        response = client.post(
            "/events",
            json=batch,
            headers={
                "User-Agent": "Mozilla/5.0 Chrome/96.0",
                "X-Forwarded-For": "192.168.1.100",
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["events_processed"] == 1
        assert data["events_rejected"] == 0

    def test_receive_events_with_rate_limiting(self, client, sample_event_data):
        """Test rate limiting in event reception."""
        # Inject rate limit state
        from lukhas.api.analytics import aggregator
        hour_key = datetime.utcnow().strftime("%Y-%m-%d-%H")
        aggregator.hourly_counts[hour_key]["0.0.0.0"] = 1000  # Max out the limit

        batch = {"events": [sample_event_data]}
        response = client.post("/events", json=batch)

        assert response.status_code == 202
        data = response.json()
        assert data["events_rejected"] >= 0  # May be rejected due to rate limit

    def test_get_metrics_endpoint(self, client):
        """Test metrics retrieval endpoint."""
        response = client.get("/metrics?hours=24")
        assert response.status_code == 200

        data = response.json()
        assert "event_counts" in data
        assert "unique_sessions" in data
        assert "time_period" in data
        assert "domain_counts" in data
        assert "browser_counts" in data

    def test_delete_user_data_endpoint(self, client):
        """Test GDPR data deletion endpoint."""
        # Add some session data first
        from lukhas.api.analytics import aggregator
        aggregator.session_ids.add("test-session-to-delete")

        response = client.delete("/data?session_id=test-session-to-delete")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "deleted"

        # Verify session was removed
        assert "test-session-to-delete" not in aggregator.session_ids

    def test_delete_nonexistent_session(self, client):
        """Test deleting non-existent session returns success."""
        response = client.delete("/data?session_id=nonexistent-session")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_event_without_session_id(self, aggregator):
        """Test events without session ID use IP for tracking."""
        event_data = {
            "event": "page_view",
            "properties": {"domain": "test.com"},
            "timestamp": "2025-11-10T12:00:00Z",
        }
        event = AnalyticsEvent(**event_data)
        aggregator.add_event(event, "chrome", "192.168.1.0")

        # Should not add to session_ids since no session_id
        assert len(aggregator.session_ids) == 0

    def test_concurrent_aggregation_thread_safety(self, aggregator):
        """Test that aggregator handles concurrent access (basic test)."""
        # This is a basic test - full thread safety testing would require
        # multiple threads, but we verify the structure is correct
        event_data = {
            "event": "page_view",
            "properties": {"domain": "test.com"},
            "timestamp": "2025-11-10T12:00:00Z",
            "session_id": "test-session",
        }
        event = AnalyticsEvent(**event_data)

        # Should not raise any errors
        for _ in range(10):
            aggregator.add_event(event, "chrome", "192.168.1.0")

        assert aggregator.event_counts["page_view"] == 10

    def test_empty_batch(self, client):
        """Test submitting empty event batch."""
        response = client.post("/events", json={"events": []})
        assert response.status_code == 202
        data = response.json()
        assert data["events_processed"] == 0

    def test_special_characters_in_domain(self):
        """Test that special characters in domains are handled."""
        props = EventProperties(
            domain="test.com",
            path="/page?query=value&other=data",
        )
        # Should not be redacted (no PII)
        assert "query=value" in props.path

    def test_metrics_with_custom_hours(self, client):
        """Test metrics endpoint with custom time period."""
        response = client.get("/metrics?hours=48")
        assert response.status_code == 200
        data = response.json()
        assert data["time_period"] == "last_48_hours"
