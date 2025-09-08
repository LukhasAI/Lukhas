from fastapi.testclient import TestClient

import serve.main as sm


def test_healthz_degraded_when_voice_required_and_probe_fails(monkeypatch):
    # Force requirement and make the probe return False
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "true")
    monkeypatch.setattr(sm, "voice_core_available", lambda: False, raising=True)

    client = TestClient(sm.app)
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body.get("voice_mode") == "degraded"
    assert "degraded_reasons" in body and "voice" in body["degraded_reasons"]


def test_healthz_normal_when_probe_succeeds_and_not_required(monkeypatch):
    monkeypatch.delenv("LUKHAS_VOICE_REQUIRED", raising=False)
    monkeypatch.setattr(sm, "voice_core_available", lambda: True, raising=True)

    client = TestClient(sm.app)
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body.get("voice_mode") == "normal"
