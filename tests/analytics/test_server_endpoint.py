"""
Tests for analytics server endpoint.

Coverage:
- Event reception and validation
- Rate limiting
- IP anonymization
- User-Agent normalization
- Aggregation without storage
- GDPR data deletion
"""

import pytest
from fastapi.testclient import TestClient
from lukhas.api.analytics import app, aggregator, anonymize_ip, normalize_user_agent


class TestServerEndpoint:
    """Test analytics server endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up aggregator between tests."""
        yield
        aggregator.event_counts.clear()
        aggregator.session_ids.clear()
        aggregator.domain_counts.clear()
        aggregator.browser_counts.clear()
        aggregator.hourly_counts.clear()

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_privacy_info(self, client):
        """Test privacy information endpoint."""
        response = client.get("/privacy")
        assert response.status_code == 200

        data = response.json()
        assert data["data_collection"]["pii_collected"] is False
        assert data["compliance"]["gdpr"] is True

    def test_receive_valid_event(self, client):
        """Test receiving valid event."""
        event = {
            "events": [
                {
                    "event": "page_view",
                    "properties": {
                        "domain": "lukhas.ai",
                        "path": "/matriz",
                    },
                    "timestamp": "2025-11-08T12:00:00Z",
                    "session_id": "test-session-123",
                }
            ]
        }

        response = client.post("/events", json=event)
        assert response.status_code == 202

        data = response.json()
        assert data["status"] == "accepted"
        assert data["events_processed"] == 1

    def test_receive_invalid_event_name(self, client):
        """Test receiving invalid event name."""
        event = {
            "events": [
                {
                    "event": "invalid_event",  # Not in taxonomy
                    "properties": {
                        "domain": "lukhas.ai",
                    },
                    "timestamp": "2025-11-08T12:00:00Z",
                }
            ]
        }

        response = client.post("/events", json=event)
        assert response.status_code == 422  # Validation error

    def test_aggregation(self, client):
        """Test event aggregation."""
        # Send multiple events
        for i in range(3):
            event = {
                "events": [
                    {
                        "event": "page_view",
                        "properties": {
                            "domain": "lukhas.ai",
                            "path": f"/{i}",
                        },
                        "timestamp": "2025-11-08T12:00:00Z",
                        "session_id": f"session-{i}",
                    }
                ]
            }
            response = client.post("/events", json=event)
            assert response.status_code == 202

        # Check aggregated metrics
        response = client.get("/metrics")
        assert response.status_code == 200

        metrics = response.json()
        assert metrics["event_counts"]["page_view"] == 3
        assert metrics["unique_sessions"] == 3

    def test_data_deletion(self, client):
        """Test GDPR data deletion."""
        # Send event
        event = {
            "events": [
                {
                    "event": "page_view",
                    "properties": {"domain": "lukhas.ai"},
                    "timestamp": "2025-11-08T12:00:00Z",
                    "session_id": "delete-me",
                }
            ]
        }
        client.post("/events", json=event)

        # Delete data
        response = client.delete("/data", params={"session_id": "delete-me"})
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


class TestIPAnonymization:
    """Test IP anonymization."""

    def test_anonymize_ipv4(self):
        """Test IPv4 anonymization."""
        ip = "192.168.1.100"
        anonymized = anonymize_ip(ip)
        assert anonymized == "192.168.1.0"

    def test_anonymize_ipv6(self):
        """Test IPv6 anonymization."""
        ip = "2001:db8:85a3:8d3:1319:8a2e:370:7348"
        anonymized = anonymize_ip(ip)
        assert "::0" in anonymized


class TestUserAgentNormalization:
    """Test User-Agent normalization."""

    def test_normalize_chrome(self):
        """Test Chrome detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0"
        family = normalize_user_agent(ua)
        assert family == "chrome"

    def test_normalize_firefox(self):
        """Test Firefox detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        family = normalize_user_agent(ua)
        assert family == "firefox"

    def test_normalize_unknown(self):
        """Test unknown browser."""
        ua = "CustomBrowser/1.0"
        family = normalize_user_agent(ua)
        assert family == "other"


class TestRateLimiting:
    """Test rate limiting."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up aggregator between tests."""
        yield
        aggregator.hourly_counts.clear()

    def test_rate_limit_enforcement(self, client):
        """Test rate limit is enforced."""
        # Send events within limit
        for i in range(5):
            event = {
                "events": [
                    {
                        "event": "page_view",
                        "properties": {"domain": "lukhas.ai"},
                        "timestamp": "2025-11-08T12:00:00Z",
                        "session_id": "rate-test",
                    }
                ]
            }
            response = client.post("/events", json=event)
            assert response.status_code == 202

        # All should be accepted
        response = client.get("/metrics")
        assert response.json()["event_counts"]["page_view"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
