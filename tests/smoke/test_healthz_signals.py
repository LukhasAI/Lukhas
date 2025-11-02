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
    assert body["status"] == "ok"
    assert "checks" in body

    # Guardian signals are optional (depend on Guardian availability)
    if "guardian_pdp" in body["checks"]:
        guardian = body["checks"]["guardian_pdp"]
        assert "available" in guardian
        if guardian["available"]:
            assert "decisions" in guardian
            assert "denials" in guardian
            assert "policy_etag" in guardian


def test_healthz_ratelimiter_signals():
    """Verify /healthz includes rate_limiter stats when rate limiter is available."""
    c = _client()
    r = c.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "checks" in body

    # Rate limiter signals are optional (depend on limiter configuration)
    if "rate_limiter" in body["checks"]:
        rl = body["checks"]["rate_limiter"]
        assert "available" in rl
        if rl["available"]:
            assert "backend" in rl
            assert "keys_tracked" in rl
            assert "rate_limited" in rl


def test_healthz_always_returns_ok():
    """Verify /healthz returns ok even if Guardian/RL are unavailable."""
    c = _client()
    r = c.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "checks" in body
    assert body["checks"]["api"] is True
