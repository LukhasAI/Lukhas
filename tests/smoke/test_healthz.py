import json
import os

import pytest


# Expect: adapters.openai.api.app -> ASGI app (FastAPI/Starlette)
@pytest.mark.asyncio
async def test_health_and_readyz():
    from serve.main import app
    from starlette.testclient import TestClient
    # app imported directly from serve.main
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("status") in {"ok", "healthy"}

    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json().get("status") in {"ready", "ok"}

def test_metrics_surface():
    from serve.main import app
    from starlette.testclient import TestClient
    # app imported directly from serve.main
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "process_cpu_seconds_total" in r.text or "http_requests_total" in r.text


def test_healthz_details():
    """Verify that the /healthz endpoint returns the expected detailed information."""
    from serve.main import app
    from starlette.testclient import TestClient
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "voice_mode" in data
    assert "matriz" in data
    assert "version" in data["matriz"]
    assert "rollout" in data["matriz"]
    assert "lane" in data
