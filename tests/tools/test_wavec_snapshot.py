import os
from pathlib import Path

from scripts.wavec_snapshot import create_snapshot


def test_create_snapshot_tmpdir(tmp_path: Path) -> None:
    out = tmp_path / "wavec"
    snap = create_snapshot(out)
    assert snap.exists()
    # basic expected files exist
    assert (snap / "git_head.txt").exists()
    assert (snap / "git_status.txt").exists()
    assert (snap / "git_diffstat.txt").exists()
    assert (snap / "env.json").exists()
