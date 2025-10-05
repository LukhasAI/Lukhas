#!/usr/bin/env python3
"""T4/0.01% Benchmark Results Collection
Runs pytest-benchmark, updates manifest with p50/p95/p99, ledgers results.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import hashlib
import platform
from pathlib import Path
from datetime import datetime, timezone

try:
    import numpy as np
except ImportError:
    print("❌ numpy not installed. Run: pip install numpy")
    sys.exit(1)


def utc():
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def env_fingerprint() -> str:
    """Generate environment fingerprint for reproducibility."""
    data = {
        "python": platform.python_version(),
        "os": platform.system(),
        "arch": platform.machine(),
        "cpu": platform.processor(),
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def run_bench(module_dir: Path) -> Path | None:
    """Run pytest-benchmark and return JSON path."""
    bench_dir = module_dir / "tests" / "benchmarks"
    if not bench_dir.exists():
        return None

    out = module_dir / "bench.json"
    cmd = [
        "pytest",
        str(bench_dir),
        "--benchmark-only",
        "--benchmark-json=bench.json",
        "-q",
    ]
    res = subprocess.run(cmd, cwd=module_dir, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout, res.stderr)
        raise SystemExit(res.returncode)
    return out if out.exists() else None


def parse_percentiles(bench_json: Path) -> dict:
    """Parse p50/p95/p99 from benchmark JSON."""
    data = json.loads(bench_json.read_text())
    stats = [b.get("stats", {}) for b in data.get("benchmarks", [])]
    samples = []

    for s in stats:
        if "data" in s and s["data"]:
            samples.extend(s["data"])
        elif "mean" in s:
            samples.append(s["mean"])

    if not samples:
        return {}

    # Convert seconds to milliseconds
    p50 = np.percentile(samples, 50) * 1000
    p95 = np.percentile(samples, 95) * 1000
    p99 = np.percentile(samples, 99) * 1000

    return {
        "latency_p50_ms": round(p50, 2),
        "latency_p95_ms": round(p95, 2),
        "latency_p99_ms": round(p99, 2),
    }


def update_manifest(manifest: Path, observed: dict):
    """Update manifest with benchmark observations."""
    d = json.loads(manifest.read_text())
    perf = d.setdefault("performance", {})
    obs = perf.setdefault("observed", {})
    obs.update(observed)
    obs["observed_at"] = utc()
    obs["env_fingerprint"] = env_fingerprint()
    manifest.write_text(json.dumps(d, indent=2) + "\n")
    return d.get("module", manifest.parent.name), observed


def ledger(ledger_path: Path, rec: dict):
    """Append record to benchmark ledger."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Run benchmarks and update manifest with observed metrics"
    )
    ap.add_argument("--module", required=True, help="path or name of module dir")
    args = ap.parse_args()

    root = Path(".").resolve()
    mdir = root / args.module
    if not mdir.exists():
        try:
            mdir = next(root.rglob(f"{args.module}/module.manifest.json")).parent
        except StopIteration:
            raise SystemExit(f"❌ Module not found: {args.module}")

    manifest = mdir / "module.manifest.json"
    if not manifest.exists():
        raise SystemExit(f"❌ No manifest for {mdir}")

    bench_json = run_bench(mdir)
    if bench_json is None:
        print(f"= {mdir.name}: no benchmarks (skipped)")
        return 0

    pct = parse_percentiles(bench_json)
    if not pct:
        print(f"= {mdir.name}: no samples in bench.json")
        return 0

    mod, _ = update_manifest(manifest, pct)
    ledger(
        Path("manifests/.ledger/bench.ndjson"), {"ts": utc(), "module": mod, **pct}
    )
    print(
        f"✅ {mod}: observed p50={pct['latency_p50_ms']} "
        f"p95={pct['latency_p95_ms']} p99={pct['latency_p99_ms']} ms"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
