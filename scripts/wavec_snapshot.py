#!/usr/bin/env python3
"""
WaveC Snapshot: capture a lightweight repo state for chaos/rollback analysis.

Produces a timestamped snapshot directory with:
- git HEAD, status, and diff summary
- python version and platform info
- optional import-linter report (best-effort)

Usage:
  python3 scripts/wavec_snapshot.py --out artifacts/wavec
"""
from __future__ import annotations
import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _run(cmd: list[str], cwd: str | None = None, timeout: int = 30) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True,
        )
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)


def create_snapshot(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snap = out_dir / f"wavec_{ts}"
    snap.mkdir(parents=True, exist_ok=True)

    # Git info
    code, head, _ = _run(["git", "rev-parse", "HEAD"])  # type: ignore[arg-type]
    (snap / "git_head.txt").write_text(head if code == 0 else "unknown")
    code, status, _ = _run(["git", "status", "--porcelain=v1"])
    (snap / "git_status.txt").write_text(status)
    code, diff, _ = _run(["git", "diff", "--stat", "-200"])
    (snap / "git_diffstat.txt").write_text(diff)

    # Env info
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
    }
    (snap / "env.json").write_text(json.dumps(env, indent=2))

    # Optional: import-linter
    code, out, err = _run(["import-linter", "--version"], timeout=10)
    if code == 0:
        _run(["import-linter"], timeout=60)
        # raw output capture is tricky without config; best-effort only
        (snap / "import_linter_info.txt").write_text("import-linter invoked (see CI artifacts)")
    else:
        (snap / "import_linter_info.txt").write_text(f"import-linter unavailable: {err}")

    return snap


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/wavec", help="Snapshot output directory")
    args = ap.parse_args()
    snap = create_snapshot(Path(args.out))
    print(f"[wavec] snapshot created: {snap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

