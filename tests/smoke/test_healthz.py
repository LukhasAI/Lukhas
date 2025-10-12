import os, json
import pytest

# Expect: lukhas.adapters.openai.api.get_app() -> ASGI app (FastAPI/Starlette)
@pytest.mark.asyncio
async def test_health_and_readyz():
    from starlette.testclient import TestClient
    from lukhas.adapters.openai.api import get_app
    app = get_app()
    client = TestClient(app)
    r = client.get("/healthz");  assert r.status_code == 200 and r.json().get("status") in {"ok","healthy"}
    r = client.get("/readyz");   assert r.status_code == 200 and r.json().get("status") in {"ready","ok"}

def test_metrics_surface():
    from starlette.testclient import TestClient
    from lukhas.adapters.openai.api import get_app
    app = get_app()
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "process_cpu_seconds_total" in r.text or "http_requests_total" in r.text
