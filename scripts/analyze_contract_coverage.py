#!/usr/bin/env python3
"""
Analyze contract coverage across all modules, with focus on T1 modules.
Reports broken references and missing contracts.
"""
import json
import pathlib
import sys
from typing import Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS_DIR = ROOT / "manifests"
CONTRACTS_DIR = ROOT / "contracts"


def load_contract_index() -> Dict[str, pathlib.Path]:
    """Load all contract files and index them by path."""
    idx: Dict[str, pathlib.Path] = {}
    if not CONTRACTS_DIR.exists():
        return idx

    for p in CONTRACTS_DIR.rglob("*.json"):
        # Store both absolute and relative paths
        rel_path = p.relative_to(ROOT)
        idx[str(rel_path)] = p
        # Also index common variations
        idx[f"{rel_path}"] = p

    return idx


def analyze_manifests():
    """Analyze all manifests for contract coverage."""
    contract_index = load_contract_index()

    stats = {
        "total_modules": 0,
        "t1_modules": 0,
        "t1_with_contracts": 0,
        "t1_without_contracts": [],
        "broken_references": [],
        "modules_with_contracts": 0,
    }

    print("=" * 80)
    print("CONTRACT COVERAGE ANALYSIS")
    print("=" * 80)
    print()

    # Find all manifests
    manifests = list(MANIFESTS_DIR.rglob("module.manifest.json"))
    manifests = [m for m in manifests if ".archive" not in str(m)]

    stats["total_modules"] = len(manifests)

    for manifest_file in sorted(manifests):
        try:
            with open(manifest_file) as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not read {manifest_file}: {e}")
            continue

        module_name = data.get("module", {}).get("name", "unknown")
        quality_tier = data.get("module", {}).get("quality_tier", "unknown")
        contracts = data.get("contracts", [])

        # Track T1 modules
        if quality_tier == "T1":
            stats["t1_modules"] += 1

            if contracts:
                stats["t1_with_contracts"] += 1
                # Check if contracts exist
                for contract_path in contracts:
                    if contract_path not in contract_index:
                        stats["broken_references"].append(
                            {
                                "module": module_name,
                                "contract": contract_path,
                                "manifest": str(manifest_file.relative_to(ROOT)),
                            }
                        )
            else:
                stats["t1_without_contracts"].append(
                    {"module": module_name, "tier": quality_tier, "manifest": str(manifest_file.relative_to(ROOT))}
                )

        # Track modules with contracts
        if contracts:
            stats["modules_with_contracts"] += 1

    # Report findings
    print("📊 OVERALL STATISTICS")
    print(f"   Total Modules: {stats['total_modules']}")
    print(f"   Modules with Contracts: {stats['modules_with_contracts']}")
    print(f"   Available Contract Files: {len(contract_index)}")
    print()

    print("🎯 T1 MODULE COVERAGE")
    print(f"   T1 Modules: {stats['t1_modules']}")
    print(f"   T1 with Contracts: {stats['t1_with_contracts']}")
    print(f"   T1 without Contracts: {len(stats['t1_without_contracts'])}")

    if stats["t1_modules"] > 0:
        coverage = (stats["t1_with_contracts"] / stats["t1_modules"]) * 100
        print(f"   Coverage: {coverage:.1f}%")
    print()

    if stats["t1_without_contracts"]:
        print(f"❌ T1 MODULES WITHOUT CONTRACTS ({len(stats['t1_without_contracts'])})")
        for item in stats["t1_without_contracts"]:
            print(f"   - {item['module']} (manifest: {item['manifest']})")
        print()

    if stats["broken_references"]:
        print(f"⚠️  BROKEN CONTRACT REFERENCES ({len(stats['broken_references'])})")
        for item in stats["broken_references"]:
            print(f"   - Module: {item['module']}")
            print(f"     Missing: {item['contract']}")
            print(f"     Manifest: {item['manifest']}")
        print()
    else:
        print("✅ NO BROKEN CONTRACT REFERENCES")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    issues = []
    if stats["t1_without_contracts"]:
        issues.append(f"{len(stats['t1_without_contracts'])} T1 modules need contracts")
    if stats["broken_references"]:
        issues.append(f"{len(stats['broken_references'])} broken references")

    if issues:
        print("🔴 ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        return 1
    else:
        print("✅ ALL CHECKS PASSED")
        print(f"   - 100% T1 contract coverage ({stats['t1_with_contracts']}/{stats['t1_modules']})")
        print("   - 0 broken references")
        return 0


if __name__ == "__main__":
    sys.exit(analyze_manifests())
