"""
Unit tests for rate-limit metrics export.

Verifies that Prometheus metrics for rate-limiting are properly exported
and contain expected series names.

Phase 3: Added for rate-limit metrics validation.
"""
from fastapi.testclient import TestClient
from adapters.openai.api import get_app

METRIC_KEYS = (
    "lukhas_ratelimit_limit_requests",
    "lukhas_ratelimit_remaining_requests",
    "lukhas_ratelimit_reset_requests_seconds",
    "lukhas_ratelimit_exceeded_total",
)


def test_metrics_surface_basic_ratelimit_series():
    """Verify rate-limit metrics appear in /metrics endpoint."""
    app = app
    client = TestClient(app)

    # Trigger a couple of calls to ensure gauges update
    client.get("/v1/models", headers={"Authorization": "Bearer testtoken"})
    client.get("/v1/models", headers={"Authorization": "Bearer testtoken"})

    r = client.get("/metrics")
    assert r.status_code == 200, f"Metrics endpoint failed: {r.status_code}"

    text = r.text

    # Check for presence of rate-limit metrics
    # We don't assert exact label values to avoid flakiness
    for k in METRIC_KEYS:
        # Should find either HELP, TYPE, or actual metric lines
        found = (
            f"# HELP {k}" in text or
            f"# TYPE {k}" in text or
            f"{k}{{" in text
        )
        assert found, f"Missing metric: {k}"


def test_metrics_endpoint_includes_standard_lukhas_metrics():
    """Verify existing LUKHAS metrics are still present."""
    app = app
    client = TestClient(app)

    # Make a request to generate some metrics
    client.get("/v1/models", headers={"Authorization": "Bearer test"})

    r = client.get("/metrics")
    assert r.status_code == 200

    text = r.text

    # Standard LUKHAS metrics should still be there
    assert "http_requests_total" in text or "lukhas_requests_total" in text

    # Prometheus format basics
    assert "# HELP" in text
    assert "# TYPE" in text
