import os
import subprocess
import sys
from pathlib import Path

import yaml

from diagnostics.entropy_radar import load_brief_metrics, render_entropy_radar


def create_brief(path: Path, name: str, entropy: float, delta: float) -> None:
    data = {
        "module": {"name": name},
        "symbolic": {"entropy": entropy, "collapse_delta": delta},
    }
    path.write_text(yaml.safe_dump(data))


def test_load_brief_metrics(tmp_path):
    brief = tmp_path / "mod.brief.yaml"
    create_brief(brief, "mod", 0.5, 0.2)
    metrics = load_brief_metrics(str(tmp_path))
    assert metrics == {"mod": {"entropy": 0.5, "collapse_delta": 0.2}}


def test_render_entropy_radar(tmp_path):
    out_dir = tmp_path / "plots"
    path = render_entropy_radar("mod", {"entropy": 0.5, "collapse_delta": 0.2}, out_dir)
    assert path.exists()
    assert path.suffix == ".svg"


def test_cli_drift_only(tmp_path):
    lukhas_dir = tmp_path / "lukhas"
    lukhas_dir.mkdir()
    create_brief(lukhas_dir / "mod.brief.yaml", "mod", 0.1, 0.0)

    env = dict(**os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]))
    result = subprocess.run(
        [sys.executable, "-m", "lukhas.diagnostics.entropy_radar", "--drift-only"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
    )
    assert result.returncode == 0
    plots = list((tmp_path / "lukhas" / "diagnostics" / "plots").glob("*.svg"))
    assert plots == []
