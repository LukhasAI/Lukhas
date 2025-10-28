import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

CREATE = "scripts/todo_migration/create_issues.py"


def clean_artifacts():
    art = Path("artifacts")
    if art.exists():
        shutil.rmtree(art)


def write_inventory(path: Path, rows: list[dict[str, str]]) -> None:
    header = ["file", "line", "kind", "priority", "owner", "scope", "message"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_create_issues_dry_run_valid(tmp_path):
    clean_artifacts()
    csv_path = tmp_path / "todos.csv"
    file_path = tmp_path / "module.py"
    rows = [
        {
            "file": str(file_path),
            "line": "10",
            "kind": "TODO",
            "priority": "Med",
            "owner": "@owner",
            "scope": "prod",
            "message": "Add validation\nSecond line\x07",
        }
    ]
    write_inventory(csv_path, rows)

    subprocess.check_call(
        [
            sys.executable,
            CREATE,
            "--input",
            str(csv_path),
            "--repo",
            "lukhas/test",
            "--dry-run",
            "--out",
            "test_map.json",
        ]
    )

    outpath = Path("artifacts/test_map.json")
    assert outpath.exists(), "Expected sanitized mapping output"
    data = json.loads(outpath.read_text())
    key = f"{rows[0]['file']}:{rows[0]['line']}"
    assert key in data
    entry = data[key]
    assert entry["issue"] == 0
    assert entry["repo"] == "lukhas/test"
    assert entry["title"] == "[TODO] Add validation Second line"


def test_create_issues_invalid_scope_characters(tmp_path):
    clean_artifacts()
    csv_path = tmp_path / "todos.csv"
    rows = [
        {
            "file": str(tmp_path / "module.py"),
            "line": "5",
            "kind": "TODO",
            "priority": "HIGH",
            "owner": "@owner",
            "scope": "bad scope",
            "message": "Missing scope should fail",
        }
    ]
    write_inventory(csv_path, rows)

    with subprocess.Popen(
        [
            sys.executable,
            CREATE,
            "--input",
            str(csv_path),
            "--repo",
            "lukhas/test",
            "--dry-run",
            "--out",
            "test_map.json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        stdout, stderr = proc.communicate()
        assert proc.returncode == 1, stdout
        assert "invalid scope" in stderr

    assert not Path("artifacts/test_map.json").exists()


def test_create_issues_allows_security_scope_and_critical_priority(tmp_path):
    clean_artifacts()
    csv_path = tmp_path / "todos.csv"
    file_path = tmp_path / "module.py"
    rows = [
        {
            "file": str(file_path),
            "line": "12",
            "kind": "TODO",
            "priority": "CRITICAL",
            "owner": "@owner",
            "scope": "SECURITY",
            "message": "Handle auth token refresh",
        }
    ]
    write_inventory(csv_path, rows)

    subprocess.check_call(
        [
            sys.executable,
            CREATE,
            "--input",
            str(csv_path),
            "--repo",
            "lukhas/test",
            "--dry-run",
            "--out",
            "test_map.json",
        ]
    )

    outpath = Path("artifacts/test_map.json")
    assert outpath.exists()
    data = json.loads(outpath.read_text())
    key = f"{rows[0]['file']}:{rows[0]['line']}"
    assert data[key]["issue"] == 0
