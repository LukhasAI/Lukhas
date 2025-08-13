import json


def test_backup_manifest_schema(tmp_path):
    # Minimal fake manifest resembling scripts/backup_create.py output
    manifest = {
        "version": 1,
        "tag": "test",
        "created_utc": "2025-08-10T00:00:00Z",
        "files": [{"path": "lukhas/api/app.py", "sha256": "x" * 64}],
        "bundle": {
            "path": "out/test.tar.zst",
            "sha256": "y" * 64,
            "algo": "zstd",
        },
    }
    p = tmp_path / "m.json"
    p.write_text(json.dumps(manifest))
    data = json.loads(p.read_text())

    assert data["version"] == 1
    assert isinstance(data["files"], list)
    assert set(data["bundle"].keys()) == {"path", "sha256", "algo"}


def test_last_success_placeholder(tmp_path, monkeypatch):
    # Simulate .lukhas_backup/last_success.json content used by ops health API
    payload = {
        "last_s3_tar": "s3://bucket/backups/test.tar.zst",
        "last_s3_manifest": "s3://bucket/backups/test.tar.zst.manifest.json",
        "last_success_utc": "2025-08-10T00:00:00Z",
    }
    state_dir = tmp_path / ".lukhas_backup"
    state_dir.mkdir()
    f = state_dir / "last_success.json"
    f.write_text(json.dumps(payload))

    # simple read check
    loaded = json.loads(f.read_text())
    assert "last_s3_tar" in loaded and "last_s3_manifest" in loaded
