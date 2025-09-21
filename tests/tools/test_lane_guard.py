from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

# ΛTAG: lane_guard_enforcement_test
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "ci" / "lane_guard.sh"


@pytest.mark.skipif(shutil.which("importlinter") is None, reason="importlinter not installed")
def test_lane_guard_script_executes() -> None:
    env = os.environ.copy()
    env.setdefault("LUKHAS_LANE", "prod")
    proc = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
