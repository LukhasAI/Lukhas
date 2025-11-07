#!/usr/bin/env python3
"""
Matrix Schema v3 Upgrade Script

Idempotently extends existing Matrix contracts with v3 placeholders
while preserving 100% v2 compatibility and existing values.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# v3 Default values for new fields (safe defaults, disabled by default)
V3_DEFAULTS = {
    "tokenization": {
        "enabled": False,
        "network": "solana",
        "standard": "solana:spl-token",
        "mint_address": None,
        "token_id": None,
        "anchor_txid": None,
        "anchor_block": None,
        "anchor_digest": None,
        "anchor_merkle_root": None,
        "issuer": None,
        "policy_version": None,
        "proof_uri": None,
        "note": None
    },
    "glyph_provenance": {
        "glyph_signature": None,
        "entropy_phase": "null",
        "drift_index": None,
        "attractor_state": "null"
    },
    "dream_provenance": {
        "last_dream_cid": None,
        "drift_delta": None,
        "recurrence_score": None,
        "dream_depth": None,
        "coherence_index": None
    },
    "guardian_check": {
        "enabled": True,
        "policy_ref": "guardian/ethics.v1",
        "dissonance_threshold": 0.05,
        "last_check_timestamp": None,
        "drift_detection": True
    },
    "biosymbolic_map": {
        "compound": "NAD+",
        "role": "homeostasis",
        "state": "baseline",
        "pathway_coupling": None,
        "symbolic_ph": None
    },
    "quantum_proof": {
        "zkp_circuit": None,
        "merkle_dag_root": None,
        "post_quantum_sig": None,
        "lattice_commitment": None,
        "entanglement_witness": None,
        "superposition_state": "null"
    }
}


def upgrade_contract(contract_data: dict[str, Any], dry_run: bool = False) -> bool:
    """
    Upgrade a single contract with v3 placeholders.

    Args:
        contract_data: The contract data to upgrade
        dry_run: If True, don't modify the data, just return if changes would be made

    Returns:
        True if changes were made (or would be made in dry run), False otherwise
    """
    changed = False

    # Add missing top-level v3 sections
    for section_name, default_values in V3_DEFAULTS.items():
        if section_name not in contract_data:
            if not dry_run:
                contract_data[section_name] = default_values.copy()
            changed = True
        else:
            # Fill in any missing fields within existing sections
            if isinstance(default_values, dict) and isinstance(contract_data[section_name], dict):
                for field_name, default_value in default_values.items():
                    if field_name not in contract_data[section_name]:
                        if not dry_run:
                            contract_data[section_name][field_name] = default_value
                        changed = True

    return changed


def upgrade_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Upgrade a single contract file with v3 placeholders.

    Args:
        file_path: Path to the contract file
        dry_run: If True, don't write changes, just return if changes would be made

    Returns:
        True if changes were made (or would be made in dry run), False otherwise
    """
    try:
        # Read existing contract
        contract_text = file_path.read_text(encoding="utf-8")
        contract_data = json.loads(contract_text)

        # Upgrade with v3 fields
        changed = upgrade_contract(contract_data, dry_run=dry_run)

        # Write back if changes were made and not dry run
        if changed and not dry_run:
            updated_text = json.dumps(contract_data, indent=2) + "\n"
            file_path.write_text(updated_text, encoding="utf-8")

        return changed

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}", file=sys.stderr)
        return False


def find_contract_files(pattern: str) -> list[Path]:
    """Find all contract files matching the pattern."""
    return sorted(Path(".").rglob(pattern))


def main():
    """Main entry point for the upgrade script."""
    parser = argparse.ArgumentParser(
        description="Upgrade Matrix contracts with v3 placeholders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/matrix_upgrade_v3.py                    # Upgrade all contracts
  python3 tools/matrix_upgrade_v3.py --dry-run          # Preview changes
  python3 tools/matrix_upgrade_v3.py --pattern "contracts/matrix_*.json"  # Custom pattern
        """
    )

    parser.add_argument(
        "--pattern",
        default="**/matrix_*.json",
        help="Glob pattern for finding contract files (default: **/matrix_*.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )

    args = parser.parse_args()

    # Find all contract files
    contract_files = find_contract_files(args.pattern)

    if not contract_files:
        print(f"No contract files found matching pattern: {args.pattern}")
        return 1

    if args.verbose:
        print(f"Found {len(contract_files)} contract files:")
        for f in contract_files:
            print(f"  {f}")
        print()

    # Process each file
    updated_count = 0
    for contract_file in contract_files:
        if args.verbose:
            action = "WOULD UPDATE" if args.dry_run else "UPDATING"
            print(f"Processing {contract_file}...", end=" ")

        changed = upgrade_file(contract_file, dry_run=args.dry_run)

        if changed:
            updated_count += 1
            if args.verbose:
                status = "WOULD UPDATE" if args.dry_run else "UPDATED"
                print(f"{status}")
            elif not args.dry_run:
                print(f"UPDATED {contract_file}")
        elif args.verbose:
            print("NO CHANGES")

    # Summary
    action = "would be updated" if args.dry_run else "updated"
    print(f"\nDone. Files {action}: {updated_count}/{len(contract_files)}")

    if args.dry_run and updated_count > 0:
        print("\nRe-run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
