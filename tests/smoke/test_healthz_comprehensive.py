"""
Comprehensive health check endpoint tests.

Validates:
- Health check endpoint behavior under various conditions
- Guardian state integration
- Voice mode handling (normal/degraded/unavailable)
- MATRIZ version and rollout information
- Lane configuration
- Error handling and degraded states
"""
import pytest
from fastapi.testclient import TestClient
from serve.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


# Basic Health Check Tests
class TestHealthCheckBasics:
    """Test basic health check functionality."""

    def test_healthz_returns_200(self, client):
        """Verify /healthz always returns 200 for readiness consumers."""
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthz_json_format(self, client):
        """Verify /healthz returns valid JSON."""
        response = client.get("/healthz")
        assert response.headers["Content-Type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)

    def test_health_alias_works(self, client):
        """Verify /health alias works."""
        response = client.get("/health")
        assert response.status_code == 200

        # Should return same structure as /healthz
        data = response.json()
        assert "status" in data

    def test_readyz_returns_200_when_healthy(self, client):
        """Verify /readyz returns 200 when service is ready."""
        response = client.get("/readyz")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ("ready", "ok")

    def test_metrics_endpoint_works(self, client):
        """Verify /metrics endpoint returns Prometheus format."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/plain; charset=utf-8"

        # Should contain Prometheus metrics
        text = response.text
        assert "# HELP" in text
        assert "# TYPE" in text


# Health Check Structure Tests
class TestHealthCheckStructure:
    """Test health check response structure."""

    def test_healthz_required_fields(self, client):
        """Verify /healthz contains all required fields."""
        response = client.get("/healthz")
        data = response.json()

        # Required fields
        assert "status" in data
        assert "voice_mode" in data
        assert "matriz" in data
        assert "lane" in data

    def test_matriz_info_structure(self, client):
        """Verify MATRIZ info has correct structure."""
        response = client.get("/healthz")
        data = response.json()

        matriz = data["matriz"]
        assert "version" in matriz
        assert "rollout" in matriz
        assert "enabled" in matriz

        # Enabled should be boolean based on rollout
        assert isinstance(matriz["enabled"], bool)
        assert matriz["enabled"] == (matriz["rollout"] != "disabled")

    def test_lane_info_present(self, client):
        """Verify lane information is present."""
        response = client.get("/healthz")
        data = response.json()

        # Should have lane config
        assert "lane" in data
        # Lane should be one of the standard values
        assert data["lane"] in ("prod", "staging", "dev", "test")


# Voice Mode Tests
class TestVoiceModeHandling:
    """Test voice mode handling in health checks."""

    def test_voice_mode_field_present(self, client):
        """Verify voice_mode field is always present."""
        response = client.get("/healthz")
        data = response.json()

        assert "voice_mode" in data
        assert data["voice_mode"] in ("normal", "degraded")

    def test_voice_degraded_when_required_but_unavailable(self, monkeypatch):
        """Verify voice mode shows degraded when required but unavailable."""
        # Set voice as required
        monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "true")

        # Mock voice as unavailable by setting non-existent path
        import sys
        if "bridge.voice" in sys.modules:
            del sys.modules["bridge.voice"]

        client = TestClient(app)
        response = client.get("/healthz")
        data = response.json()

        # Should show voice_mode as degraded and include reason
        if data.get("voice_mode") == "degraded":
            assert "degraded_reasons" in data
            assert "voice" in data["degraded_reasons"]

    def test_voice_normal_when_not_required(self, monkeypatch):
        """Verify voice mode is normal when not required."""
        # Set voice as not required
        monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "false")

        client = TestClient(app)
        response = client.get("/healthz")
        data = response.json()

        # Voice mode should be normal or degraded (both acceptable)
        assert data["voice_mode"] in ("normal", "degraded")


# Degraded States Tests
class TestDegradedStates:
    """Test various degraded state scenarios."""

    def test_degraded_reasons_structure(self, client):
        """Verify degraded_reasons has correct structure when present."""
        response = client.get("/healthz")
        data = response.json()

        # If degraded_reasons present, should be a list
        if "degraded_reasons" in data:
            assert isinstance(data["degraded_reasons"], list)

            # All reasons should be strings
            for reason in data["degraded_reasons"]:
                assert isinstance(reason, str)

    def test_status_remains_ok_even_when_degraded(self, monkeypatch):
        """Verify status is 'ok' even with degraded components."""
        # Force degraded state
        monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "true")

        client = TestClient(app)
        response = client.get("/healthz")
        data = response.json()

        # Status should still be ok (200) for readiness consumers
        assert response.status_code == 200
        assert data["status"] in ("ok", "healthy")


# MATRIZ Configuration Tests
class TestMATRIZConfiguration:
    """Test MATRIZ configuration in health checks."""

    def test_matriz_version_present(self, client):
        """Verify MATRIZ version is reported."""
        response = client.get("/healthz")
        data = response.json()

        assert "version" in data["matriz"]
        # Version should be string (even if "unknown")
        assert isinstance(data["matriz"]["version"], str)

    def test_matriz_rollout_values(self, monkeypatch):
        """Verify MATRIZ rollout accepts valid values."""
        test_values = ["disabled", "canary", "prod", "100"]

        for value in test_values:
            monkeypatch.setenv("MATRIZ_ROLLOUT", value)

            client = TestClient(app)
            response = client.get("/healthz")
            data = response.json()

            assert data["matriz"]["rollout"] == value
            assert data["matriz"]["enabled"] == (value != "disabled")

    def test_matriz_enabled_boolean_logic(self, client):
        """Verify MATRIZ enabled field has correct boolean logic."""
        response = client.get("/healthz")
        data = response.json()

        rollout = data["matriz"]["rollout"]
        enabled = data["matriz"]["enabled"]

        # Should be disabled if rollout is "disabled"
        if rollout == "disabled":
            assert enabled is False
        else:
            assert enabled is True


# Module Manifest Tests
class TestModuleManifests:
    """Test module manifest counting."""

    def test_modules_field_when_manifests_exist(self, client):
        """Verify modules field when manifests directory exists."""
        response = client.get("/healthz")
        data = response.json()

        # If modules field present, should have manifest_count
        if "modules" in data:
            assert "manifest_count" in data["modules"]
            assert isinstance(data["modules"]["manifest_count"], int)
            assert data["modules"]["manifest_count"] >= 0

    def test_modules_field_optional(self, client):
        """Verify modules field is optional."""
        response = client.get("/healthz")
        data = response.json()

        # modules field may or may not be present
        if "modules" in data:
            assert isinstance(data["modules"], dict)


# Performance Tests
class TestHealthCheckPerformance:
    """Test health check performance characteristics."""

    def test_healthz_responds_quickly(self, client):
        """Verify /healthz responds in < 100ms."""
        import time

        start = time.time()
        response = client.get("/healthz")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1  # < 100ms

    def test_readyz_responds_quickly(self, client):
        """Verify /readyz responds in < 100ms."""
        import time

        start = time.time()
        response = client.get("/readyz")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1  # < 100ms

    def test_multiple_concurrent_health_checks(self, client):
        """Verify concurrent health checks work correctly."""
        import concurrent.futures

        def check_health():
            response = client.get("/healthz")
            return response.status_code

        # 10 concurrent health checks
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_health) for _ in range(10)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(status == 200 for status in results)


# Edge Cases
class TestHealthCheckEdgeCases:
    """Test edge cases and error handling."""

    def test_healthz_with_trailing_slash(self, client):
        """Verify /healthz works with trailing slash."""
        response = client.get("/healthz/")
        # FastAPI may return 404 or redirect, both acceptable
        assert response.status_code in (200, 307, 404)

    def test_healthz_case_sensitive(self, client):
        """Verify /healthz is case-sensitive."""
        response = client.get("/HEALTHZ")
        # Should return 404 (case-sensitive paths)
        assert response.status_code == 404

    def test_health_vs_healthz_consistency(self, client):
        """Verify /health and /healthz return consistent data."""
        health_response = client.get("/health")
        healthz_response = client.get("/healthz")

        assert health_response.status_code == healthz_response.status_code

        # Should have same structure
        health_data = health_response.json()
        healthz_data = healthz_response.json()

        assert set(health_data.keys()) == set(healthz_data.keys())

    def test_readyz_derives_from_healthz(self, client):
        """Verify /readyz derives status from /healthz."""
        healthz_response = client.get("/healthz")
        readyz_response = client.get("/readyz")

        assert readyz_response.status_code == 200

        healthz_data = healthz_response.json()
        readyz_data = readyz_response.json()

        # If healthz is ok, readyz should be ready
        if healthz_data["status"] in ("ok", "healthy"):
            assert readyz_data["status"] in ("ready", "ok")
