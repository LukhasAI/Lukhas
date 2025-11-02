#!/usr/bin/env python3
"""WaveC snapshot helper.

Captures a lightweight repository snapshot with git metadata, environment context,
and an optional signed manifest for rollback analysis. Operators can invoke the
script directly:

    python3 scripts/wavec_snapshot.py --out artifacts/wavec

"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import hmac
import json
import platform
import subprocess
import sys
import time
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _run(cmd: Sequence[str], cwd: str | None = None, timeout: int = 30) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as exc:  # pragma: no cover - defensive logging
        return 1, "", str(exc)


def write_snapshot(memory_state: Any, out_path: str, key_env: str = "WAVEC_SIGN_KEY") -> dict[str, Any]:
    """Serialize *memory_state* to ``out_path`` (JSON), gzip it, and sign with HMAC."""
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(memory_state, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    gz = gzip.compress(payload)
    sha = hashlib.sha256(gz).hexdigest()
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError(f"Missing signing key: {key_env}")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    path.write_bytes(payload)
    gz_path = path.with_suffix(path.suffix + ".gz")
    gz_path.write_bytes(gz)
    meta = {"sha256": sha, "sig": sig, "timestamp": now_iso()}
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def verify_snapshot(gz_path: str, key_env: str = "WAVEC_SIGN_KEY") -> bool:
    gz = Path(gz_path).read_bytes()
    sha = hashlib.sha256(gz).hexdigest()
    meta_path = Path(gz_path).with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta["sha256"] != sha:
        raise RuntimeError("Snapshot SHA mismatch")
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError("Missing signing key")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    if sig != meta["sig"]:
        raise RuntimeError("Signature mismatch")
    return True


def create_snapshot(out_dir: Path, *, sign: bool = True, key_env: str = "WAVEC_SIGN_KEY") -> Path:
    """Create a WaveC snapshot directory and optionally sign the manifest."""
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_dir = out_dir / f"wavec_{timestamp}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    code, head, _ = _run(["git", "rev-parse", "HEAD"])
    (snapshot_dir / "git_head.txt").write_text(head if code == 0 else "unknown", encoding="utf-8")

    _, status, _ = _run(["git", "status", "--porcelain=v1"])
    (snapshot_dir / "git_status.txt").write_text(status, encoding="utf-8")

    _, diffstat, _ = _run(["git", "diff", "--stat", "-200"])
    (snapshot_dir / "git_diffstat.txt").write_text(diffstat, encoding="utf-8")

    env_info = {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
    }
    (snapshot_dir / "env.json").write_text(json.dumps(env_info, indent=2), encoding="utf-8")

    manifest = {
        "timestamp": now_iso(),
        "git": {
            "head": head.strip() if code == 0 else "unknown",
            "status_path": "git_status.txt",
            "diffstat_path": "git_diffstat.txt",
        },
        "env_path": "env.json",
    }
    state_path = snapshot_dir / "state.json"
    state_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if sign and os.environ.get(key_env):
        write_snapshot(manifest, str(state_path), key_env=key_env)

    return snapshot_dir


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a WaveC snapshot")
    parser.add_argument("--out", default="artifacts/wavec", help="Snapshot output directory")
    parser.add_argument("--no-sign", action="store_true", help="Skip signing the manifest")
    parser.add_argument(
        "--key-env",
        default="WAVEC_SIGN_KEY",
        help="Environment variable holding the signing key",
    )
    args = parser.parse_args(argv)

    sign = not args.no_sign
    snapshot_dir = create_snapshot(Path(args.out), sign=sign, key_env=args.key_env)
    print(f"[wavec] snapshot created: {snapshot_dir}")
    meta_path = Path(snapshot_dir / "state.json.meta.json")
    if meta_path.exists():
        print("[wavec] manifest signed", flush=True)
    elif sign:
        print("[wavec] signing skipped (missing key)", flush=True)
    else:
        print("[wavec] manifest unsigned", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
