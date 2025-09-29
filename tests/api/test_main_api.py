#!/usr/bin/env python3
"""
Tests for LUKHAS Main API Router
Production Schema v1.0.0

Tests API wiring, endpoint discovery, and integration between components.
"""

import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

from lukhas.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_environment():
    """Mock production environment"""
    with patch.dict(os.environ, {
        'GUARDIAN_MODE': 'production',
        'LUKHAS_MODE': 'test'
    }):
        yield


class TestMainAPIRouting:
    """Test main API routing and discovery"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "LUKHAS AI"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "timestamp" in data

        # Check expected endpoints are listed
        endpoints = data["endpoints"]
        assert "/health" in endpoints.values()
        assert "/status" in endpoints.values()
        assert "/identity" in endpoints.values()
        assert "/orchestration" in endpoints.values()

    def test_health_endpoint(self, client):
        """Test basic health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "lukhas-api"
        assert "timestamp" in data

    def test_detailed_health_endpoint(self, client, mock_environment):
        """Test detailed health endpoint with component status"""
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "guardian" in data

        # Check components are reported
        components = data["components"]
        assert "guardian" in components
        assert "identity" in components
        assert "orchestration" in components

        # Guardian should be in production mode
        guardian = data["guardian"]
        assert guardian["mode"] == "production"

    def test_status_endpoint(self, client):
        """Test API status endpoint"""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.json()
        assert data["api"] == "lukhas-ai"
        assert data["status"] == "operational"
        assert "endpoints" in data
        assert "environment" in data

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200

        # Should return Prometheus format
        content = response.text
        assert "lukhas_api_requests_total" in content or "# HELP" in content


class TestAPIRouterIntegration:
    """Test integration with mounted routers"""

    def test_webauthn_router_mounted(self, client):
        """Test WebAuthn router is properly mounted"""
        # Test health endpoint
        response = client.get("/identity/webauthn/health")
        assert response.status_code == 200

    def test_orchestration_router_mounted(self, client):
        """Test Orchestration router is properly mounted"""
        # Test health endpoint
        response = client.get("/orchestration/health")
        assert response.status_code == 200

    def test_openapi_schema_includes_all_routes(self, client):
        """Test OpenAPI schema includes all mounted routes"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        # Check main API paths
        assert "/" in paths
        assert "/health" in paths
        assert "/status" in paths

        # Check WebAuthn paths are included
        webauthn_paths = [p for p in paths if p.startswith("/identity/webauthn")]
        assert len(webauthn_paths) > 0

        # Check Orchestration paths are included
        orchestration_paths = [p for p in paths if p.startswith("/orchestration")]
        assert len(orchestration_paths) > 0

    def test_cors_headers(self, client):
        """Test CORS headers are set"""
        response = client.options("/")

        # Should have CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in [h.lower() for h in headers]


class TestErrorHandling:
    """Test error handling"""

    def test_404_handler(self, client):
        """Test custom 404 handler"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert data["error"] == "endpoint_not_found"
        assert "available_endpoints" in data


class TestPerformanceMetrics:
    """Test performance metrics collection"""

    def test_request_metrics_collected(self, client):
        """Test that requests generate metrics"""
        # Make some requests
        client.get("/")
        client.get("/health")
        client.get("/status")

        # Check metrics endpoint
        response = client.get("/metrics")
        content = response.text

        # Should have request counters
        assert "lukhas_api_requests_total" in content


class TestGuardianIntegration:
    """Test Guardian integration"""

    def test_guardian_status_in_health_check(self, client, mock_environment):
        """Test Guardian status is included in health check"""
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "guardian" in data

        guardian_data = data["guardian"]
        assert "mode" in guardian_data
        assert "implementation" in guardian_data
        assert "enabled" in guardian_data

    def test_environment_variables_reflected(self, client):
        """Test environment variables are reflected in status"""
        with patch.dict(os.environ, {
            'GUARDIAN_MODE': 'staging',
            'LUKHAS_MODE': 'test'
        }):
            response = client.get("/status")
            assert response.status_code == 200

            data = response.json()
            env = data["environment"]
            assert env["guardian_mode"] == "staging"
            assert env["lukhas_mode"] == "test"


class TestEndpointDiscovery:
    """Test API endpoint discovery"""

    def test_all_required_endpoints_available(self, client):
        """Test all required endpoints are available"""
        required_endpoints = [
            "/",
            "/health",
            "/health/detailed",
            "/status",
            "/metrics",
            "/identity/webauthn/health",
            "/orchestration/health"
        ]

        for endpoint in required_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} not available"

    def test_documentation_endpoints(self, client):
        """Test documentation endpoints are available"""
        docs_endpoints = [
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

        for endpoint in docs_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Documentation endpoint {endpoint} not available"


@pytest.mark.integration
class TestAPIIntegrationFlow:
    """Integration tests for full API flow"""

    def test_identity_to_orchestration_flow(self, client):
        """Test flow from identity to orchestration"""
        # 1. Check identity health
        response = client.get("/identity/webauthn/health")
        assert response.status_code == 200

        # 2. Check orchestration health
        response = client.get("/orchestration/health")
        assert response.status_code == 200

        # 3. Check overall system health
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "degraded"]  # Either is acceptable

    def test_metrics_and_observability(self, client):
        """Test metrics and observability endpoints"""
        # Generate some traffic
        endpoints = ["/", "/health", "/status"]
        for endpoint in endpoints:
            client.get(endpoint)

        # Check metrics were collected
        response = client.get("/metrics")
        assert response.status_code == 200

        content = response.text
        assert "lukhas_api_requests_total" in content