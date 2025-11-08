#!/usr/bin/env python3
"""
Policy Bundle Checksum Checker

Validates that OPA policy bundles haven't drifted from canonical sources.
"""

import hashlib
import json
import logging
import sys
from pathlib import Path

# Module-level logger
logger = logging.getLogger(__name__)

# Repository structure
ROOT = Path(__file__).resolve().parents[1]
POLICIES_DIR = ROOT / "policies" / "matrix"
CHECKSUM_FILE = ROOT / "artifacts" / "policy_bundle.sha256"
TIER_PERMISSIONS = ROOT / "labs" / "governance" / "identity" / "config" / "tier_permissions.json"

def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return ""

def compute_bundle_hash() -> dict[str, str]:
    """Compute hashes for all policy files."""
    hashes = {}

    # Hash main policy file
    policy_file = POLICIES_DIR / "identity.rego"
    if policy_file.exists():
        hashes["identity.rego"] = compute_file_hash(policy_file)

    # Hash test file
    test_file = POLICIES_DIR / "identity_test.rego"
    if test_file.exists():
        hashes["identity_test.rego"] = compute_file_hash(test_file)

    # Hash tier permissions if exists
    if TIER_PERMISSIONS.exists():
        hashes["tier_permissions.json"] = compute_file_hash(TIER_PERMISSIONS)

    # Compute aggregate hash
    aggregate = hashlib.sha256()
    for file_name in sorted(hashes.keys()):
        aggregate.update(f"{file_name}:{hashes[file_name]}".encode())

    hashes["aggregate"] = aggregate.hexdigest()
    return hashes

def load_stored_checksum() -> dict[str, str]:
    """Load stored checksums."""
    if CHECKSUM_FILE.exists():
        try:
            return json.loads(CHECKSUM_FILE.read_text())
        except Exception as e:
            logger.debug(f"Expected optional failure: {e}")
            return {}
    return {}

def save_checksum(hashes: dict[str, str]):
    """Save checksums to file."""
    CHECKSUM_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKSUM_FILE.write_text(json.dumps(hashes, indent=2, sort_keys=True))

def main():
    """Check policy bundle checksums."""
    print("🔍 Policy Bundle Checksum Checker")
    print("=" * 60)

    # Compute current hashes
    current_hashes = compute_bundle_hash()

    if not current_hashes:
        print("❌ No policy files found")
        return 1

    print("📋 Current policy files:")
    for file_name, hash_val in current_hashes.items():
        if file_name != "aggregate":
            print(f"  {file_name}: {hash_val[:16]}...")

    # Load stored checksums
    stored_hashes = load_stored_checksum()

    if not stored_hashes:
        print("\n⚠️ No stored checksums found, creating initial baseline...")
        save_checksum(current_hashes)
        print(f"✅ Baseline saved to {CHECKSUM_FILE.relative_to(ROOT)}")
        return 0

    # Compare checksums
    print("\n🔐 Comparing checksums...")
    drifted = False

    for file_name, current_hash in current_hashes.items():
        if file_name == "aggregate":
            continue

        stored_hash = stored_hashes.get(file_name)
        if stored_hash != current_hash:
            print(f"  ❌ {file_name}: DRIFT DETECTED")
            print(f"     Expected: {stored_hash[:16] if stored_hash else 'none'}...")
            print(f"     Got:      {current_hash[:16]}...")
            drifted = True
        else:
            print(f"  ✅ {file_name}: OK")

    # Check aggregate
    if stored_hashes.get("aggregate") != current_hashes["aggregate"]:
        print("\n❌ Aggregate checksum mismatch - policy bundle has drifted!")
        drifted = True
    else:
        print("\n✅ Aggregate checksum matches - no drift detected")

    if drifted:
        print("\n⚠️ Policy drift detected!")
        print("To update baseline, run:")
        print(f"  python3 {__file__} --update")

        # Check if update flag is set
        if "--update" in sys.argv:
            print("\nUpdating checksums...")
            save_checksum(current_hashes)
            print(f"✅ Updated checksums saved to {CHECKSUM_FILE.relative_to(ROOT)}")
            return 0
        return 1

    print("\n✅ All policy checksums match - no drift detected")
    return 0

if __name__ == "__main__":
    sys.exit(main())
