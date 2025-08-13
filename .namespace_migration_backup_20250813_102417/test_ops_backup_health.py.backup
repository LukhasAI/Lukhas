import json

from fastapi.testclient import TestClient

from lukhas_pwm.api.app import app


def test_backup_health_reads_last_success(tmp_path, monkeypatch):
    # Prepare fake state dir
    state_dir = tmp_path / ".lukhas_backup"
    state_dir.mkdir()
    (state_dir / "last_success.json").write_text(
        json.dumps(
            {
                "last_s3_tar": "s3://bucket/backups/x.tar.zst",
                "last_s3_manifest": "s3://bucket/backups/x.tar.zst.manifest.json",
                "last_success_utc": "2025-08-10T00:00:00Z",
            }
        )
    )

    monkeypatch.setenv("LUKHAS_BACKUP_STATE", str(state_dir))
    monkeypatch.setenv("LUKHAS_API_KEY", "k")

    c = TestClient(app)
    r = c.get("/ops/backup/health", headers={"x-api-key": "k"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["last_success"]["last_s3_manifest"].startswith("s3://")


def test_backup_health_freshness(tmp_path, monkeypatch):
    state_dir = tmp_path / ".lukhas_backup"
    state_dir.mkdir()
    (state_dir / "last_success.json").write_text(
        json.dumps(
            {
                "last_s3_tar": "s3://bucket/backups/x.tar.zst",
                "last_s3_manifest": "s3://bucket/backups/x.tar.zst.manifest.json",
                "timestamp_utc": "1999-01-01T00:00:00Z",
            }
        )
    )

    monkeypatch.setenv("LUKHAS_BACKUP_STATE", str(state_dir))
    monkeypatch.setenv("BACKUP_MAX_AGE_MINUTES", "1")
    monkeypatch.setenv("LUKHAS_API_KEY", "k")

    c = TestClient(app)
    r = c.get("/ops/backup/health", headers={"x-api-key": "k"})
    assert r.status_code == 200
    data = r.json()
    # Likely stale; ensure fields present
    assert "fresh" in data
    assert "age_minutes" in data
