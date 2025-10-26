import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from products.experience.dashboard.core.meta import dashboard_server as server


@pytest.fixture
def client(tmp_path: Path):
    server.DASHBOARD_CONFIG["metrics_path"] = tmp_path / "metrics.json"
    server.DASHBOARD_CONFIG["history_path"] = tmp_path / "history.jsonl"
    server.DASHBOARD_CONFIG["snapshots_path"] = tmp_path / "snapshots.jsonl"
    server.DASHBOARD_CONFIG["guardian_log_path"] = tmp_path / "guardian.jsonl"
    server.DASHBOARD_CONFIG["auth_token"] = "secret"
    server.DASHBOARD_CONFIG["enable_auth"] = True

    server.history_store = server.DashboardHistoryStore(server.DASHBOARD_CONFIG["history_path"])

    # Seed snapshot and guardian data
    with open(server.DASHBOARD_CONFIG["snapshots_path"], "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": "2024-01-01T12:00:00+00:00", "drift_score": 0.4}) + "\n")
        handle.write(json.dumps({"timestamp": "2024-01-01T12:30:00+00:00", "drift_score": 0.8}) + "\n")
    with open(server.DASHBOARD_CONFIG["guardian_log_path"], "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": "2024-01-01T12:31:00+00:00"}) + "\n")

    return TestClient(server.app)


def auth_headers():
    return {"Authorization": "Bearer secret"}


def test_metrics_flow_and_history(client: TestClient, tmp_path: Path):
    payload = {
        "average_drift": 0.5,
        "triad_coherence": 0.9,
        "entropy_level": 0.2,
        "persona_distribution": {"Navigator": 3, "Guardian": 1},
        "total_evaluations": 10,
    }

    response = client.post("/api/meta/metrics", json=payload, headers=auth_headers())
    assert response.status_code == 200

    response = client.get("/api/meta/metrics", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["triad_coherence"] == 0.9

    history_response = client.get("/api/meta/history", headers=auth_headers())
    assert history_response.json()["count"] >= 1

    drift_response = client.get("/api/meta/drift/analysis", headers=auth_headers())
    assert drift_response.status_code == 200
    assert drift_response.json()["heatmap"]

    guardian_response = client.get("/api/meta/guardian", headers=auth_headers())
    assert guardian_response.status_code == 200
    assert guardian_response.json()["interventions"] == 1

    export_response = client.post("/api/meta/export", headers=auth_headers())
    assert export_response.status_code == 200
    exported_path = Path(export_response.json()["path"])
    assert exported_path.exists()
