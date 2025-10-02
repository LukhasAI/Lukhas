#!/usr/bin/env python3
"""
LUKHAS Registry Diff Tool
Compares current registry with baseline to detect:
- Modules removed without deprecation/alias entries
- Modules added
- Modules modified

Fails (exit 1) if modules removed without proper deprecation workflow.
Can bypass with --allow-removals flag or LUKHAS_ALLOW_MODULE_REMOVALS env var.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "artifacts"
REGISTRY_PATH = ARTIFACTS_DIR / "module.registry.json"
BASELINE_PATH = ARTIFACTS_DIR / "module.registry.json.baseline"


def load_registry(path: Path) -> dict:
    """Load registry file."""
    if not path.exists():
        return {"modules": []}

    with path.open() as f:
        return json.load(f)


def get_module_map(registry: dict) -> dict[str, dict]:
    """Create a map of module name -> module data."""
    return {m["module"]: m for m in registry.get("modules", [])}


def check_deprecation_or_alias(module_name: str, current_map: dict[str, dict]) -> tuple[bool, str]:
    """
    Check if a removed module has deprecation or alias entry in current registry.
    Returns (has_entry, reason).
    """
    # Check if any module has this as an alias
    for module_data in current_map.values():
        aliases = module_data.get("aliases", [])
        if module_name in aliases:
            return True, f"aliased in {module_data['module']}"

    # Check if any module has this in deprecations
    for module_data in current_map.values():
        deprecations = module_data.get("deprecations", [])
        for dep in deprecations:
            if dep.get("old_name") == module_name:
                return True, f"deprecated in {module_data['module']} (until {dep.get('until', 'unknown')})"

    return False, ""


def main():
    ap = argparse.ArgumentParser(description="Compare LUKHAS module registries")
    ap.add_argument(
        "--baseline",
        help=f"Path to baseline registry (default: {BASELINE_PATH})",
        default=str(BASELINE_PATH),
    )
    ap.add_argument(
        "--current",
        help=f"Path to current registry (default: {REGISTRY_PATH})",
        default=str(REGISTRY_PATH),
    )
    ap.add_argument(
        "--allow-removals",
        action="store_true",
        help="Allow module removals without deprecation/alias",
    )
    ap.add_argument(
        "--create-baseline",
        action="store_true",
        help="Copy current registry to baseline path",
    )
    args = ap.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)

    # Create baseline mode
    if args.create_baseline:
        if not current_path.exists():
            print(f"❌ Current registry not found: {current_path}", file=sys.stderr)
            sys.exit(1)

        ARTIFACTS_DIR.mkdir(exist_ok=True)
        with current_path.open() as f_in, baseline_path.open("w") as f_out:
            f_out.write(f_in.read())

        print(f"✅ Baseline created: {baseline_path}")
        sys.exit(0)

    # Check if registries exist
    if not current_path.exists():
        print(f"❌ Current registry not found: {current_path}", file=sys.stderr)
        print("   Run manifest_indexer.py to generate it.", file=sys.stderr)
        sys.exit(1)

    if not baseline_path.exists():
        print(f"⚠️  Baseline registry not found: {baseline_path}")
        print(f"   Creating baseline from current registry...")
        ARTIFACTS_DIR.mkdir(exist_ok=True)
        with current_path.open() as f_in, baseline_path.open("w") as f_out:
            f_out.write(f_in.read())
        print(f"✅ Baseline created: {baseline_path}")
        print("   Run this command again to perform diff.")
        sys.exit(0)

    # Load registries
    baseline = load_registry(baseline_path)
    current = load_registry(current_path)

    baseline_map = get_module_map(baseline)
    current_map = get_module_map(current)

    baseline_names = set(baseline_map.keys())
    current_names = set(current_map.keys())

    # Calculate differences
    added = current_names - baseline_names
    removed = baseline_names - current_names
    common = baseline_names & current_names

    # Check for modifications in common modules
    modified = []
    for name in common:
        baseline_hash = baseline_map[name].get("hashes", {})
        current_hash = current_map[name].get("hashes", {})
        if baseline_hash != current_hash:
            modified.append(name)

    print("📊 LUKHAS Registry Diff")
    print(f"Baseline: {baseline_path}")
    print(f"Current:  {current_path}")
    print("-" * 60)

    print(f"\nModules in baseline: {len(baseline_names)}")
    print(f"Modules in current:  {len(current_names)}")

    # Report additions
    if added:
        print(f"\n✨ Added ({len(added)}):")
        for name in sorted(added):
            module_path = current_map[name].get("module_path", "unknown")
            print(f"   + {name} ({module_path})")
    else:
        print(f"\n✨ Added: 0")

    # Report modifications
    if modified:
        print(f"\n🔄 Modified ({len(modified)}):")
        for name in sorted(modified):
            print(f"   ~ {name}")
    else:
        print(f"\n🔄 Modified: 0")

    # Report removals and check for violations
    violations = []
    if removed:
        print(f"\n🗑️  Removed ({len(removed)}):")
        for name in sorted(removed):
            has_entry, reason = check_deprecation_or_alias(name, current_map)
            if has_entry:
                print(f"   - {name} ✅ ({reason})")
            else:
                print(f"   - {name} ❌ (no deprecation/alias entry)")
                violations.append(name)
    else:
        print(f"\n🗑️  Removed: 0")

    # Check for bypass
    allow_removals = args.allow_removals or os.getenv("LUKHAS_ALLOW_MODULE_REMOVALS") == "1"

    # Final verdict
    print("\n" + "=" * 60)

    if violations:
        print(f"\n❌ VIOLATIONS: {len(violations)} module(s) removed without deprecation/alias:")
        for name in violations:
            print(f"   - {name}")

        print("\nTo fix:")
        print("   1. Add deprecation entry to the module that replaces this functionality")
        print("   2. Add alias entry if the module was renamed")
        print("   3. Use --allow-removals flag to bypass (not recommended)")
        print("   4. Set LUKHAS_ALLOW_MODULE_REMOVALS=1 environment variable")

        if allow_removals:
            print("\n⚠️  Removals allowed by flag/environment variable")
            print("✅ Diff complete (violations bypassed)")
            sys.exit(0)
        else:
            print("\n❌ Diff failed: unplanned module removals detected")
            sys.exit(1)

    print("\n✅ Diff complete: no violations detected")

    if added or modified:
        print(f"   Changes: {len(added)} added, {len(modified)} modified, {len(removed)} removed")
    else:
        print("   No changes detected")

    sys.exit(0)


if __name__ == "__main__":
    main()
