#!/usr/bin/env python3
"""
Module: ledger_consistency.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""T4/0.01% Ledger Consistency Gate

Ensures that any module.manifest.json changed in a commit has at least one
corresponding entry in manifests/.ledger/* within ±1 minute of commit timestamp.

This prevents silent, non-provenance edits to manifests.

Usage:
    python scripts/ci/ledger_consistency.py [--commit-ref HEAD]

Exit codes:
    0 - All manifest changes have corresponding ledger entries
    1 - One or more manifests lack ledger entries (CI should fail)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple


class ManifestChange(NamedTuple):
    """Represents a changed manifest file."""
    path: Path
    module: str
    commit_timestamp: datetime


class LedgerEntry(NamedTuple):
    """Represents a ledger entry."""
    ledger_type: str  # scaffold, test_scaffold, coverage, bench
    module: str
    timestamp: datetime


def get_commit_timestamp(ref: str = "HEAD") -> datetime:
    """Get commit timestamp for given ref."""
    cmd = ["git", "log", "-1", "--format=%cI", ref]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return datetime.fromisoformat(result.stdout.strip())


def get_changed_manifests(ref: str = "HEAD") -> list[ManifestChange]:
    """Get all module.manifest.json files changed in the given commit."""
    commit_ts = get_commit_timestamp(ref)

    # Get changed files in this commit
    cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", ref]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    changed_files = result.stdout.strip().split("\n")
    manifests = []

    for file in changed_files:
        if file.endswith("module.manifest.json"):
            path = Path(file)
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                    module = data.get("module", path.parent.name)
                    manifests.append(ManifestChange(path, module, commit_ts))
                except Exception as e:
                    print(f"⚠️  Could not parse {path}: {e}", file=sys.stderr)

    return manifests


def read_ledger_entries(ledger_path: Path, ledger_type: str) -> list[LedgerEntry]:
    """Read all entries from a ledger file."""
    if not ledger_path.exists():
        return []

    entries = []
    for line in ledger_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            module = data.get("module", "")
            timestamp_str = data.get("timestamp", data.get("ts", ""))
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
                entries.append(LedgerEntry(ledger_type, module, timestamp))
        except Exception as e:
            print(f"⚠️  Could not parse ledger entry: {e}", file=sys.stderr)

    return entries


def check_ledger_consistency(
    manifests: list[ManifestChange],
    tolerance_minutes: int = 1
) -> tuple[list[str], list[str]]:
    """Check if all manifest changes have corresponding ledger entries.

    Returns:
        (valid_modules, invalid_modules)
    """
    ledger_dir = Path("manifests/.ledger")
    ledger_files = {
        "scaffold": ledger_dir / "scaffold.ndjson",
        "test_scaffold": ledger_dir / "test_scaffold.ndjson",
        "coverage": ledger_dir / "coverage.ndjson",
        "bench": ledger_dir / "bench.ndjson",
    }

    # Read all ledger entries
    all_entries: list[LedgerEntry] = []
    for ledger_type, ledger_path in ledger_files.items():
        all_entries.extend(read_ledger_entries(ledger_path, ledger_type))

    valid_modules = []
    invalid_modules = []

    tolerance = timedelta(minutes=tolerance_minutes)

    for manifest_change in manifests:
        # Find ledger entries for this module within tolerance window
        matching_entries = [
            entry for entry in all_entries
            if entry.module == manifest_change.module
            and abs(entry.timestamp - manifest_change.commit_timestamp) <= tolerance
        ]

        if matching_entries:
            valid_modules.append(manifest_change.module)
            print(f"✅ {manifest_change.module}: {len(matching_entries)} ledger entries within ±{tolerance_minutes}min")
        else:
            invalid_modules.append(manifest_change.module)
            print(f"❌ {manifest_change.module}: NO ledger entries within ±{tolerance_minutes}min of commit", file=sys.stderr)
            print(f"   Commit timestamp: {manifest_change.commit_timestamp.isoformat()}", file=sys.stderr)
            print(f"   Manifest path: {manifest_change.path}", file=sys.stderr)

    return valid_modules, invalid_modules


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that manifest changes have corresponding ledger entries"
    )
    parser.add_argument(
        "--commit-ref",
        default="HEAD",
        help="Git commit ref to check (default: HEAD)"
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=1,
        help="Tolerance window in minutes (default: 1)"
    )
    args = parser.parse_args()

    print(f"🔍 Checking ledger consistency for commit: {args.commit_ref}")
    print(f"   Tolerance window: ±{args.tolerance} minutes\n")

    # Get changed manifests
    manifests = get_changed_manifests(args.commit_ref)

    if not manifests:
        print("ℹ️  No module.manifest.json files changed in this commit")
        return 0

    print(f"📝 Found {len(manifests)} changed manifest(s)\n")

    # Check consistency
    valid, invalid = check_ledger_consistency(manifests, args.tolerance)

    print("\n📊 Results:")
    print(f"   ✅ Valid: {len(valid)}")
    print(f"   ❌ Invalid: {len(invalid)}")

    if invalid:
        print("\n❌ LEDGER CONSISTENCY CHECK FAILED", file=sys.stderr)
        print("   The following manifests lack ledger entries:", file=sys.stderr)
        for module in invalid:
            print(f"   - {module}", file=sys.stderr)
        print("\n   Fix: Ensure manifests are updated via scaffolding scripts", file=sys.stderr)
        print("        or manually add ledger entries to manifests/.ledger/", file=sys.stderr)
        return 1

    print("\n✅ LEDGER CONSISTENCY CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
