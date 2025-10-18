import json
from pathlib import Path

from governance.oversight.consolidate_guardian_governance import (
    consolidate_guardian_governance,
)


def test_consolidation_writes_registry_and_report(tmp_path, monkeypatch):
    # Create fake source trees with a couple of files
    src1 = tmp_path / "candidate/core/governance"
    src1.mkdir(parents=True)
    (src1 / "policy.py").write_text("POLICY = True\n")
    (src1 / "__init__.py").write_text("")

    src2 = tmp_path / "lukhas/governance"
    src2.mkdir(parents=True)
    (src2 / "enforcer.py").write_text("def enforce():\n    return True\n")

    # Ensure CWD scanning sees our temp sources
    monkeypatch.chdir(tmp_path)
    # Set target dir to under tmp
    target = tmp_path / "guardian/governance"
    monkeypatch.setenv("LUKHAS_GUARDIAN_TARGET_DIR", str(target))

    summary = consolidate_guardian_governance()
    assert summary["module_count"] >= 2
    assert Path(summary["target_dir"]).exists()

    reg = target / "registry.json"
    rep = target / "CONSOLIDATION_REPORT.md"
    assert reg.exists() and rep.exists()
    data = json.loads(reg.read_text())
    assert data["module_count"] == len(data["modules"]) and data["modules"]
    # Check a known module was indexed
    assert any(m["name"] == "policy" for m in data["modules"])
