from fastapi.testclient import TestClient

from lukhas_pwm.api.app import app


def test_openapi_endpoint_serves_json():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "openapi" in data
    assert data.get("info", {}).get("title") == "LUKHΛS PWM API"
