import json
import shutil
import subprocess
import sys
from pathlib import Path

REWRITER = "scripts/consolidation/rewrite_matriz_imports.py"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clean_artifacts():
    art = Path("artifacts")
    if art.exists():
        shutil.rmtree(art)


def test_simple_import(tmp_path):
    clean_artifacts()
    p = tmp_path / "mod.py"
    src = "import os\nimport matriz\nimport matriz.submod\nfrom matriz import X\n"
    write_file(p, src)

    # run dry-run for this file only
    subprocess.check_call([sys.executable, REWRITER, "--path", str(p), "--dry-run"])

    manifest = Path("artifacts/matriz_manifest.json")
    assert manifest.exists(), "Expected manifest artifact"
    data = json.loads(manifest.read_text())
    # Ensure our file is listed in files_changed
    files = data.get("files_changed", [])
    assert any(str(p) == f or str(p.resolve()) == f for f in files), f"{p} not found in manifest"


def test_no_changes_for_strings(tmp_path):
    clean_artifacts()
    p = tmp_path / "mod2.py"
    src = 'text = "import matriz not a real import"\nprint(text)\n'
    write_file(p, src)
    subprocess.check_call([sys.executable, REWRITER, "--path", str(p), "--dry-run"])

    manifest = Path("artifacts/matriz_manifest.json")
    if manifest.exists():
        data = json.loads(manifest.read_text())
        files = data.get("files_changed", [])
        assert not any(
            str(p) == f or str(p.resolve()) == f for f in files
        ), "File with only string import should not be changed"
    else:
        # No manifest means no changes at all — acceptable
        assert True
