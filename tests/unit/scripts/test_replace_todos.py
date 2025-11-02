import json
import shutil
import subprocess
import sys
from pathlib import Path

REPLACE = "scripts/todo_migration/replace_todos_with_issues.py"


def clean_artifacts():
    art = Path("artifacts")
    if art.exists():
        shutil.rmtree(art)


def test_replace_todo_dry_run(tmp_path):
    clean_artifacts()
    f = tmp_path / "mod.py"
    f.write_text(
        "# TODO [SCOPE:PROD] : Fix this\n"
        "print('hi')\n"
    )

    mapfile = tmp_path / "map.json"
    key = f"{f!s}:1"
    mapping = {key: {"issue": 123, "repo": "org/repo", "title": "Fix TODO"}}
    Path("artifacts").mkdir(exist_ok=True)
    mapfile.write_text(json.dumps(mapping))

    # dry-run
    subprocess.check_call([sys.executable, REPLACE, "--map", str(mapfile)])
    # Dry-run should not modify the file contents
    assert (
        f.read_text()
        == "# TODO [SCOPE:PROD] : Fix this\nprint('hi')\n"
    ), "Dry-run unexpectedly altered the file"
    log = Path("artifacts/replace_todos_log.json")
    assert log.exists(), "Expected replace_todos_log.json"
    data = json.loads(log.read_text())
    # Expect an entry for our file (even if only dry-run)
    assert any(entry.get("file") == str(f) for entry in data), f"No log entry for {f}"
