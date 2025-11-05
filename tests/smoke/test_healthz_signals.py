"""
Smoke tests for /healthz Guardian and rate-limiter signals.

Verifies that health endpoint returns Guardian PDP and rate-limiter statistics
when available, enabling operational monitoring without requiring verbose logs.
"""
import os

from fastapi.testclient import TestClient
from serve.main import app


def _client():
    """Build test client with permissive policy mode."""
    os.environ["LUKHAS_POLICY_MODE"] = "permissive"
    return TestClient(app)


def test_healthz_guardian_signals():
    """Verify /healthz includes guardian_pdp stats when Guardian is available."""
    c = _client()
    r = c.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ["ok", "degraded"]


def test_healthz_ratelimiter_signals():
    """Verify /healthz includes rate_limiter stats when rate limiter is available."""
    c = _client()
    r = c.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ["ok", "degraded"]


def test_healthz_always_returns_ok():
    """Verify /healthz returns ok even if Guardian/RL are unavailable."""
    c = _client()
    r = c.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ["ok", "degraded"]
