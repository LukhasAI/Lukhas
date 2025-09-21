from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# ΛTAG: performance_benchmark_test
ROOT = Path(__file__).resolve().parents[2]


def test_memory_benchmark_smoke_runs() -> None:
    cmd = [sys.executable, "-m", "benchmarks.memory_bench", "--smoke", "--json"]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert "benchmarks" in payload
    assert payload["benchmarks"], "Expected benchmark summaries"
