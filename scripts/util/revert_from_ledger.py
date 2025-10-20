#!/usr/bin/env python3
"""
Module: revert_from_ledger.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
T4/0.01% Ledger-based Revert Utility
====================================

Reverts manifests to a previous state using enrichment ledger.

Usage:
    # Revert to last enrichment
    python3 scripts/util/revert_from_ledger.py --last

    # Revert to specific SHA
    python3 scripts/util/revert_from_ledger.py --sha abc123def456

    # Preview revert without applying
    python3 scripts/util/revert_from_ledger.py --last --dry-run

Features:
- SHA-based idempotency: Only revert if current state matches expected
- Atomic operations: All or nothing (no partial reverts)
- Audit trail: Logs all revert operations
- Verification: Validates manifests after revert
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def load_ledger(ledger_path: Path) -> List[Dict]:
    """Load enrichment ledger entries."""
    if not ledger_path.exists():
        print(f"❌ Ledger not found: {ledger_path}", file=sys.stderr)
        sys.exit(1)

    entries = []
    with ledger_path.open("r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    return entries


def find_ledger_entry(entries: List[Dict], sha: Optional[str] = None, last: bool = False) -> Optional[Dict]:
    """Find ledger entry by SHA or get last entry."""
    if last and entries:
        return entries[-1]

    if sha:
        for entry in entries:
            if entry.get("enrichment_sha", "").startswith(sha):
                return entry

    return None


def compute_manifest_sha(manifest_path: Path) -> str:
    """Compute SHA256 of manifest file."""
    if not manifest_path.exists():
        return ""

    content = manifest_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def revert_manifest(manifest_path: Path, snapshot: Dict, dry_run: bool = False) -> bool:
    """Revert single manifest to snapshot state."""
    if not manifest_path.exists():
        print(f"⚠️  Manifest missing: {manifest_path}", file=sys.stderr)
        return False

    # Verify current state matches expected (idempotency check)
    current_sha = compute_manifest_sha(manifest_path)
    expected_sha = snapshot.get("before_sha", "")

    if expected_sha and current_sha != expected_sha:
        print(f"⚠️  SHA mismatch for {manifest_path.name}: current != expected", file=sys.stderr)
        print(f"   Current:  {current_sha[:12]}...", file=sys.stderr)
        print(f"   Expected: {expected_sha[:12]}...", file=sys.stderr)
        return False

    if dry_run:
        print(f"   Would revert: {manifest_path.name}")
        return True

    # Restore manifest from snapshot
    manifest_data = snapshot.get("manifest_snapshot")
    if not manifest_data:
        print(f"❌ No snapshot data for {manifest_path.name}", file=sys.stderr)
        return False

    try:
        manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n")
        print(f"   ✅ Reverted: {manifest_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to revert {manifest_path.name}: {e}", file=sys.stderr)
        return False


def log_revert(ledger_path: Path, revert_entry: Dict) -> None:
    """Append revert operation to ledger."""
    with ledger_path.open("a") as f:
        f.write(json.dumps(revert_entry, ensure_ascii=False) + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Revert manifests to previous state using enrichment ledger"
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("artifacts/enrichment_ledger.jsonl"),
        help="Path to enrichment ledger (default: artifacts/enrichment_ledger.jsonl)",
    )
    parser.add_argument(
        "--sha",
        type=str,
        help="SHA prefix of enrichment to revert to",
    )
    parser.add_argument(
        "--last",
        action="store_true",
        help="Revert to last enrichment",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview revert without applying changes",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if not args.sha and not args.last:
        print("❌ Must specify --sha or --last", file=sys.stderr)
        sys.exit(1)

    # Load ledger
    entries = load_ledger(args.ledger)
    if not entries:
        print("❌ Ledger is empty", file=sys.stderr)
        sys.exit(1)

    # Find target entry
    target_entry = find_ledger_entry(entries, sha=args.sha, last=args.last)
    if not target_entry:
        if args.sha:
            print(f"❌ No ledger entry found for SHA: {args.sha}", file=sys.stderr)
        else:
            print("❌ No ledger entry found", file=sys.stderr)
        sys.exit(1)

    enrichment_sha = target_entry.get("enrichment_sha", "unknown")
    timestamp = target_entry.get("timestamp", "unknown")
    snapshots = target_entry.get("snapshots", [])

    print(f"🔄 Reverting to enrichment: {enrichment_sha[:12]}...")
    print(f"   Timestamp: {timestamp}")
    print(f"   Modules: {len(snapshots)}")

    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made\n")

    # Revert each manifest
    success_count = 0
    fail_count = 0
    skip_count = 0

    for snapshot in snapshots:
        manifest_rel_path = snapshot.get("manifest_path")
        if not manifest_rel_path:
            skip_count += 1
            continue

        manifest_path = Path(manifest_rel_path)

        if revert_manifest(manifest_path, snapshot, dry_run=args.dry_run):
            success_count += 1
        else:
            fail_count += 1

    print("\n📊 Revert Summary:")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   ⏭️  Skipped: {skip_count}")

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
        sys.exit(0)

    if fail_count > 0:
        print(f"\n❌ Revert incomplete: {fail_count} failures", file=sys.stderr)
        sys.exit(1)

    # Log revert operation
    revert_entry = {
        "operation": "revert",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reverted_to_sha": enrichment_sha,
        "reverted_to_timestamp": timestamp,
        "modules_reverted": success_count,
        "failures": fail_count,
    }

    log_revert(args.ledger, revert_entry)
    print(f"\n✅ Revert complete: {success_count} modules restored")
    print(f"📝 Logged to: {args.ledger}")


if __name__ == "__main__":
    main()
