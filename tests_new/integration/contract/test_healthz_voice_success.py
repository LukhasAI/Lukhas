import pytest
from fastapi.testclient import TestClient

CASES = [
    # (required_env, probe_ok, expected_mode, expect_voice_in_degraded)
    ("false", True, "normal", False),  # success path
    (" TRUE ", False, "degraded", True),  # required + whitespace/casing + fail -> degraded_reasons carries "voice"
    ("false", False, "degraded", False),  # not required + fail -> NO degraded_reasons["voice"]
]


@pytest.mark.parametrize("required_env,probe_ok,expected_mode,expect_voice_flag", CASES)
def test_healthz_voice_matrix(monkeypatch, required_env, probe_ok, expected_mode, expect_voice_flag):
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", required_env)
    monkeypatch.setattr("serve.main.voice_core_available", lambda: probe_ok)

    from serve.main import app

    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200

    data = r.json()
    assert data["voice_mode"] == expected_mode
    reasons = data.get("degraded_reasons", [])
    has_voice = isinstance(reasons, list) and ("voice" in reasons)
    assert has_voice == expect_voice_flag