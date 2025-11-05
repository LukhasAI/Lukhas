"""
Test metrics tracking and Prometheus endpoint enhancements.

Validates that:
- Request counts are tracked correctly
- Latency metrics are captured
- Prometheus format is valid
- Health checks include dependency validation
"""

import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client():
    """Create a test client for the OpenAI façade."""
    # app imported directly from serve.main
    return TestClient(app)


AUTH_HEADERS = GOLDEN_AUTH_HEADERS


def test_metrics_track_requests(client):
    """Verify that metrics track request counts."""
    # Make a request to /v1/models
    response = client.get("/v1/models", headers=AUTH_HEADERS)
    assert response.status_code == 200

    # Check metrics endpoint
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    metrics_text = metrics_response.text

    # Should include lukhas_requests_total
    assert "lukhas_requests_total" in metrics_text


def test_metrics_track_latency(client):
    """Verify that latency metrics are captured."""
    # Make a few requests
    for _ in range(3):
        client.get("/v1/models", headers=AUTH_HEADERS)

    # Check metrics
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text

    # Should include latency metrics
    assert "http_request_duration_ms" in metrics_text


def test_healthz_includes_checks(client):
    """Verify healthz includes dependency checks."""
    response = client.get("/healthz")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "matriz" in data
    assert "memory" in data


def test_readyz_validates_dependencies(client):
    """Verify readyz includes comprehensive dependency validation."""
    response = client.get("/readyz")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["ready", "not_ready"]


def test_metrics_prometheus_format(client):
    """Verify metrics are in valid Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200

    metrics_text = response.text
    lines = metrics_text.strip().split("\n")

    # Should have HELP and TYPE declarations
    help_lines = [l for l in lines if l.startswith("# HELP")]
    type_lines = [l for l in lines if l.startswith("# TYPE")]

    assert len(help_lines) > 0, "Should have HELP declarations"
    assert len(type_lines) > 0, "Should have TYPE declarations"

    # Should have actual metric values
    metric_lines = [l for l in lines if l and not l.startswith("#")]
    assert len(metric_lines) > 0, "Should have metric values"
