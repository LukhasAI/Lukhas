#!/usr/bin/env python3
"""
LUKHAS Manifest Indexer
Reads all module.manifest.lock.json files and generates:
- artifacts/module.registry.json with all modules
- artifacts/registry_errors.json if duplicates detected
Exits with code 1 if duplicates found.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".venv", "artifacts", "node_modules", ".git", "__pycache__"}
ARTIFACTS_DIR = ROOT / "artifacts"
REGISTRY_PATH = ARTIFACTS_DIR / "module.registry.json"
ERRORS_PATH = ARTIFACTS_DIR / "registry_errors.json"


def iter_lockfiles(start: Path) -> list[Path]:
    """Find all module.manifest.lock.json files, skipping excluded directories."""
    lockfiles = []
    for lockfile in start.rglob("module.manifest.lock.json"):
        # Skip if in excluded directories
        if any(part in SKIP_DIRS for part in lockfile.parts):
            continue
        lockfiles.append(lockfile)
    return sorted(lockfiles)


def load_lockfile(path: Path) -> dict:
    """Load and return lockfile data."""
    with path.open() as f:
        return json.load(f)


def detect_duplicates(modules: list[dict]) -> dict[str, list[dict]]:
    """Detect duplicate module names."""
    by_name = defaultdict(list)
    for module in modules:
        by_name[module["module"]].append(module)

    duplicates = {name: entries for name, entries in by_name.items() if len(entries) > 1}
    return duplicates


def main():
    ap = argparse.ArgumentParser(description="Generate LUKHAS module registry from lockfiles")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be generated without writing")
    ap.add_argument("--output", help="Custom output path for registry (default: artifacts/module.registry.json)")
    args = ap.parse_args()

    # Find all lockfiles
    lockfiles = iter_lockfiles(ROOT)

    if not lockfiles:
        print("⚠️  No lockfiles found. Run manifest_lock_hydrator.py first.", file=sys.stderr)
        sys.exit(1)

    print("📑 LUKHAS Manifest Indexer")
    print(f"Repository: {ROOT}")
    print(f"Found: {len(lockfiles)} lockfiles")
    print("-" * 60)

    # Load all lockfiles
    modules = []
    errors = []

    for lockfile_path in lockfiles:
        try:
            rel_path = lockfile_path.relative_to(ROOT)
        except ValueError:
            rel_path = lockfile_path

        try:
            lockfile_data = load_lockfile(lockfile_path)

            # Add source path to the module data
            lockfile_data["_source_lockfile"] = str(rel_path)

            modules.append(lockfile_data)
            print(f"✅ {rel_path} → {lockfile_data.get('module', 'unknown')}")

        except Exception as e:
            print(f"❌ {rel_path}")
            print(f"   Error: {e}")
            errors.append({"path": str(rel_path), "error": str(e)})

    # Detect duplicates
    duplicates = detect_duplicates(modules)

    # Prepare registry data
    registry_data = {
        "version": "1.0.0",
        "generated_at": modules[0]["generated_at"] if modules else "",
        "total_modules": len(modules),
        "modules": sorted(modules, key=lambda m: m.get("module", "")),
    }

    # Prepare output path
    output_path = Path(args.output) if args.output else REGISTRY_PATH

    # Ensure artifacts directory exists
    if not args.dry_run:
        ARTIFACTS_DIR.mkdir(exist_ok=True)

    print("\n📊 Summary:")
    print(f"   Total modules: {len(modules)}")
    print(f"   Duplicates: {len(duplicates)}")
    print(f"   Load errors: {len(errors)}")

    # Report duplicates
    has_duplicates = False
    if duplicates:
        has_duplicates = True
        print("\n⚠️  DUPLICATE MODULES DETECTED:")
        duplicate_details = []

        for module_name, entries in duplicates.items():
            print(f"\n   Module: {module_name}")
            paths = []
            for entry in entries:
                source = entry.get("_source_lockfile", "unknown")
                module_path = entry.get("module_path", "unknown")
                print(f"      - {source} (path: {module_path})")
                paths.append({
                    "lockfile": source,
                    "module_path": module_path,
                })

            duplicate_details.append({
                "module": module_name,
                "count": len(entries),
                "locations": paths,
            })

        # Write errors file
        if not args.dry_run:
            error_data = {
                "duplicates": duplicate_details,
                "load_errors": errors,
                "total_duplicates": len(duplicates),
            }
            with ERRORS_PATH.open("w") as f:
                json.dump(error_data, f, indent=2, sort_keys=True)
            print(f"\n   ❌ Duplicate details written to: {ERRORS_PATH.relative_to(ROOT)}")

    # Write registry
    if args.dry_run:
        print(f"\n🔍 Would write registry to: {output_path}")
        print(f"   Modules to include: {len(modules)}")
    else:
        with output_path.open("w") as f:
            json.dump(registry_data, f, indent=2, sort_keys=True)
        try:
            rel_output = output_path.relative_to(ROOT)
        except ValueError:
            rel_output = output_path
        print(f"\n✅ Registry written to: {rel_output}")

    # Exit with error if duplicates found
    if has_duplicates:
        print("\n❌ Cannot proceed with duplicate module names in registry")
        sys.exit(1)

    if errors:
        print("\n❌ Some lockfiles failed to load")
        sys.exit(1)

    print("\n✅ Registry generation complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
