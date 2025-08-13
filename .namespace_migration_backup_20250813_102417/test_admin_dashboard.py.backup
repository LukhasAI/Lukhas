from fastapi.testclient import TestClient

from lukhas_pwm.api.app import app


def _enable(monkeypatch):
    monkeypatch.setenv("FLAG_ADMIN_DASHBOARD", "true")
    monkeypatch.setenv("LUKHAS_API_KEY", "dev-key")


def test_admin_overview_renders(monkeypatch):
    _enable(monkeypatch)
    c = TestClient(app)
    r = c.get("/admin", headers={"x-api-key": "dev-key"})
    assert r.status_code == 200
    assert "Admin Overview" in r.text


def test_admin_exports(monkeypatch):
    _enable(monkeypatch)
    c = TestClient(app)
    r1 = c.get("/admin/summary.json", headers={"x-api-key": "dev-key"})
    assert r1.status_code == 200
    data = r1.json()
    assert "modes" in data and "tools" in data

    r2 = c.get("/admin/incidents.csv", headers={"x-api-key": "dev-key"})
    assert r2.status_code == 200
    assert "audit_id" in r2.text


def test_admin_requires_api_key(monkeypatch):
    _enable(monkeypatch)
    c = TestClient(app)
    r = c.get("/admin")
    assert r.status_code in (401, 404)
