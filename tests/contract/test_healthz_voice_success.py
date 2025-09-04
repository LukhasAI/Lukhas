import os

from fastapi.testclient import TestClient

import serve.main as sm


def test_healthz_success_path(monkeypatch):
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "false")
    monkeypatch.setattr(sm, "voice_core_available", lambda: True, raising=True)

    client = TestClient(sm.app)
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body.get("voice_mode") == "normal"
    assert "degraded_reasons" not in body


def test_healthz_required_casing_and_whitespace(monkeypatch):
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "  TRUE  ")
    monkeypatch.setattr(sm, "voice_core_available", lambda: False, raising=True)

    client = TestClient(sm.app)
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body.get("voice_mode") == "degraded"
    assert "degraded_reasons" in body and "voice" in body["degraded_reasons"]
