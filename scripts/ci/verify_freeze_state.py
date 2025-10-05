#!/usr/bin/env python3
"""T4/0.01% Freeze Verification Script

Verifies immutability and integrity of production freeze tags by:
1. Checking tag exists and resolves to a commit
2. Validating FINAL_FREEZE.json commit matches tag SHA
3. Ensuring no diffs exist after the freeze tag (immutable policy)
4. Comparing byte-for-byte hashes of critical artifacts

Usage:
    python3 scripts/ci/verify_freeze_state.py --tag v0.02-final --mode strict
    python3 scripts/ci/verify_freeze_state.py --tag v0.02-final --mode allow-dashboards

Exit codes:
    0 - All checks passed, freeze verified
    1 - Verification failed (drift or mismatch detected)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(".").resolve()

CRITICAL_ARTIFACTS = [
    "docs/_generated/FINAL_FREEZE.json",
    "docs/_generated/PRODUCTION_FREEZE.json",
    "docs/_generated/BASELINE_FREEZE.json",
    "docs/_generated/META_REGISTRY.json",
    "docs/_generated/MODULE_REGISTRY.json",
    "docs/_generated/DOCUMENTATION_MAP.md",
    "manifests/.ledger/freeze.ndjson",
    "manifests/.ledger/coverage.ndjson",
    "manifests/.ledger/scaffold.ndjson",
    "manifests/.ledger/test_scaffold.ndjson",
]

ALLOW_DASHBOARD_FILES = [
    # If using allow-dashboards mode, these may diverge:
    # (Keep empty to enforce full immutability by default)
    # "trends/coverage_trend.csv",
    # "trends/bench_trend.csv",
]


def sh(cmd: list[str]) -> str:
    """Execute shell command and return stripped output."""
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def file_hash(path: Path) -> str:
    """Calculate SHA256 hash of file at current HEAD."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_hash_at(tag: str, relpath: str) -> str | None:
    """Calculate SHA256 hash of file content at specified tag.

    Returns None if file doesn't exist at that tag.
    """
    try:
        data = subprocess.check_output(
            ["git", "show", f"{tag}:{relpath}"],
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return None

    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify final freeze immutability and integrity"
    )
    parser.add_argument(
        "--tag",
        default="v0.02-final",
        help="Final freeze tag name (default: v0.02-final)"
    )
    parser.add_argument(
        "--mode",
        choices=["strict", "allow-dashboards"],
        default="strict",
        help="Verification mode: strict (no divergence) or allow-dashboards (permit allowlist changes)"
    )
    args = parser.parse_args()

    print(f"🔍 Verifying freeze state for tag: {args.tag}")
    print(f"   Mode: {args.mode}\n")

    # 1) Verify tag exists
    print("📌 Step 1: Verifying tag exists...")
    try:
        tag_sha = sh(["git", "rev-parse", "--verify", args.tag])
        print(f"   ✅ Tag {args.tag} resolves to: {tag_sha}\n")
    except subprocess.CalledProcessError:
        print(f"   ❌ Tag not found: {args.tag}\n")
        return 1

    # 2) Verify FINAL_FREEZE.json commit matches tag
    print("📄 Step 2: Verifying FINAL_FREEZE.json...")
    ff_path = ROOT / "docs/_generated/FINAL_FREEZE.json"

    if not ff_path.exists():
        print(f"   ❌ Missing {ff_path}\n")
        return 1

    try:
        final_freeze = json.loads(ff_path.read_text())
    except Exception as e:
        print(f"   ❌ Unreadable FINAL_FREEZE.json: {e}\n")
        return 1

    freeze_commit = final_freeze.get("commit")
    if not freeze_commit:
        print("   ❌ FINAL_FREEZE.json missing 'commit' field\n")
        return 1

    if freeze_commit != tag_sha:
        print("   ❌ Commit mismatch:")
        print(f"      Tag {args.tag} -> {tag_sha}")
        print(f"      FINAL_FREEZE.commit -> {freeze_commit}\n")
        return 1

    print("   ✅ FINAL_FREEZE.json commit matches tag SHA\n")

    # 3) Verify no diffs since tag (immutability check)
    print("🔒 Step 3: Verifying immutability (no changes after freeze)...")
    diff_output = sh(["git", "diff", "--name-only", f"{args.tag}..HEAD"])
    diffs = [p for p in diff_output.splitlines() if p.strip()]

    if diffs:
        if args.mode == "allow-dashboards":
            violations = [p for p in diffs if p not in ALLOW_DASHBOARD_FILES]
            if violations:
                print("   ❌ Changes detected after freeze (not allowlisted):")
                for p in violations:
                    print(f"      - {p}")
                print()
                return 1
            else:
                print(f"   ⚠️  {len(diffs)} allowlisted dashboard file(s) changed")
        else:
            print("   ❌ Repository has changes after freeze tag:")
            for p in diffs:
                print(f"      - {p}")
            print()
            return 1
    else:
        print("   ✅ No changes detected after freeze\n")

    # 4) Verify artifact byte-for-byte integrity
    print("🔐 Step 4: Verifying critical artifact integrity...")
    bad_artifacts = []

    for rel in CRITICAL_ARTIFACTS:
        cur_path = ROOT / rel
        tag_hash = blob_hash_at(args.tag, rel)

        if tag_hash is None:
            print(f"   ❌ File missing at tag {args.tag}: {rel}")
            bad_artifacts.append(rel)
            continue

        if not cur_path.exists():
            print(f"   ❌ File missing at HEAD: {rel}")
            bad_artifacts.append(rel)
            continue

        cur_hash = file_hash(cur_path)

        if cur_hash != tag_hash:
            print(f"   ❌ Artifact drift detected: {rel}")
            print(f"      Tag SHA256: {tag_hash}")
            print(f"      HEAD SHA256: {cur_hash}")
            bad_artifacts.append(rel)
        else:
            print(f"   ✅ {rel}")

    print()

    if bad_artifacts:
        print("❌ FREEZE VERIFICATION FAILED")
        print(f"   {len(bad_artifacts)} artifact(s) failed integrity check\n")
        return 1

    # Success!
    print("=" * 80)
    print("✅ FREEZE VERIFICATION PASSED")
    print(f"   Tag: {args.tag}")
    print(f"   Commit: {tag_sha}")
    print(f"   Artifacts verified: {len(CRITICAL_ARTIFACTS)}")
    print(f"   Mode: {args.mode}")
    print("   Status: IMMUTABLE AND VERIFIED")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
