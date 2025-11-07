#!/usr/bin/env python3
"""T4/0.01% Module Coverage Collection
Runs pytest with coverage, updates manifest, ledgers results.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def utc() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def run_pytest_cov(module_dir: Path, package: str) -> Path:
    """Run pytest with coverage and return XML path."""
    xml = module_dir / "coverage.xml"
    # Use sys.executable to ensure we use the same Python environment
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(module_dir / "tests"),
        f"--cov={package}",
        "--cov-report=xml:coverage.xml",
        "-q",
    ]
    res = subprocess.run(cmd, cwd=module_dir, capture_output=True, text=True)
    if res.returncode not in (0, 5):  # 5 = no tests collected
        print(res.stdout, res.stderr)
        raise SystemExit(res.returncode)
    if not xml.exists():
        # no tests collected → treat as 0
        xml.write_text('<?xml version="1.0"?><coverage line-rate="0.0"></coverage>')
    return xml


def parse_pct(xml_path: Path) -> float:
    """Parse coverage percentage from XML."""
    root = ET.parse(xml_path).getroot()
    rate = root.attrib.get("line-rate", "0")
    try:
        return round(100.0 * float(rate), 2)
    except Exception as e:
        logger.debug(f"Expected optional failure: {e}")
        return 0.0


def update_manifest(manifest: Path, pct: float):
    """Update manifest with coverage observation."""
    data = json.loads(manifest.read_text())
    data.setdefault("testing", {})
    data["testing"]["coverage_observed"] = pct
    data["testing"]["observed_at"] = utc()
    manifest.write_text(json.dumps(data, indent=2) + "\n")


def ledger_append(ledger: Path, rec: dict):
    """Append record to coverage ledger."""
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Collect module coverage and update manifest"
    )
    ap.add_argument("--module", required=True, help="path or name of module dir")
    args = ap.parse_args()

    root = Path(".").resolve()
    # Try as path first, then search for manifest
    mdir = root / args.module
    if not mdir.exists():
        try:
            mdir = next(root.rglob(f"{args.module}/module.manifest.json")).parent
        except StopIteration:
            raise SystemExit(f"❌ Module not found: {args.module}")

    manifest = mdir / "module.manifest.json"
    if not manifest.exists():
        raise SystemExit(f"❌ No manifest at {manifest}")

    # Package FQN from manifest, fallback to folder name
    manifest_data = json.loads(manifest.read_text())
    pkg = manifest_data.get("module", mdir.name)

    # Check if tests exist
    if not (mdir / "tests").exists():
        print(f"= {pkg}: no tests/ directory (skipped)")
        return 0

    xml = run_pytest_cov(mdir, pkg)
    pct = parse_pct(xml)
    update_manifest(manifest, pct)
    ledger_append(
        root / "manifests/.ledger/coverage.ndjson",
        {"ts": utc(), "module": pkg, "coverage": pct, "xml": str(xml)},
    )
    print(f"✅ {pkg}: coverage_observed={pct}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
