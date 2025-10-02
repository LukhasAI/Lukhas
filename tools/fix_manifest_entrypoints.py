#!/usr/bin/env python3
"""
Manifest Entrypoint Fixer

Restores and corrects entrypoints in module.manifest.json files by:
1. Extracting entrypoints from git history (commit 1d6383f45)
2. Validating each entrypoint against actual code
3. Fixing case sensitivity issues
4. Removing non-existent entrypoints
5. Updating manifests with corrected entrypoints

Usage:
    python3 tools/fix_manifest_entrypoints.py [--dry-run]
"""

import json
import sys
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
import argparse


def get_historical_entrypoints(repo_root: Path) -> Dict[str, List[str]]:
    """Extract entrypoints from git commit 1d6383f45."""
    print("📚 Extracting entrypoints from git history (commit 1d6383f45)...")

    # Get list of all manifests in that commit
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "1d6383f45"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True
    )

    manifest_paths = [
        line for line in result.stdout.strip().split('\n')
        if line.endswith('module.manifest.json')
    ]

    entrypoints_by_module = {}

    for manifest_path in manifest_paths:
        # Get the manifest content from that commit
        try:
            result = subprocess.run(
                ["git", "show", f"1d6383f45:{manifest_path}"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True
            )

            data = json.loads(result.stdout)
            module_name = data.get("module", "")
            entrypoints = data.get("runtime", {}).get("entrypoints", [])

            if entrypoints:
                # Convert manifest path to actual filesystem path
                actual_path = repo_root / manifest_path
                if actual_path.exists():
                    entrypoints_by_module[str(actual_path)] = entrypoints
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
            continue

    total_eps = sum(len(eps) for eps in entrypoints_by_module.values())
    print(f"   Found {total_eps} entrypoints across {len(entrypoints_by_module)} modules")

    return entrypoints_by_module


def validate_entrypoint(entrypoint: str, module_dir: Path) -> Tuple[bool, str, str]:
    """
    Validate an entrypoint exists in the code.

    Returns:
        (is_valid, corrected_module_path, corrected_attr_name)
    """
    # Parse entrypoint format: "module.path.Attribute" or "module.path:function"
    if ":" in entrypoint:
        module_path, attr_name = entrypoint.split(":", 1)
    else:
        parts = entrypoint.rsplit(".", 1)
        if len(parts) == 2:
            module_path, attr_name = parts
        else:
            return False, entrypoint, ""

    # Fix common case sensitivity issues
    original_module_path = module_path

    # Case 1: All uppercase module name (e.g., "CLAUDE_ARMY" -> "claude_army")
    parts = module_path.split(".")
    fixed_parts = []
    for part in parts:
        if part.isupper() and len(part) > 1:
            # Check if lowercase version exists as directory
            lowercase_part = part.lower()
            potential_dir = module_dir.parent / lowercase_part
            if potential_dir.exists() and potential_dir.is_dir():
                fixed_parts.append(lowercase_part)
                continue
        fixed_parts.append(part)

    module_path = ".".join(fixed_parts)

    # Try to import and validate
    try:
        # Add parent directory to path if needed
        sys.path.insert(0, str(module_dir.parent))

        # Suppress warnings during import
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            module = importlib.import_module(module_path)

        if hasattr(module, attr_name):
            return True, module_path, attr_name
        else:
            # Attribute doesn't exist
            return False, module_path, attr_name

    except (ImportError, AttributeError, TypeError, ValueError, SyntaxError, Exception):
        # Module doesn't exist or can't be imported
        return False, module_path, attr_name
    finally:
        # Clean up sys.path
        if str(module_dir.parent) in sys.path:
            sys.path.remove(str(module_dir.parent))


def fix_manifest_entrypoints(
    manifest_path: Path,
    historical_entrypoints: List[str],
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Fix entrypoints in a manifest file.

    Returns:
        (fixed_count, removed_count, kept_count)
    """
    module_dir = manifest_path.parent
    module_name = module_dir.name

    print(f"\n🔧 Processing: {module_name}")

    # Load current manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    validated_entrypoints = []
    fixed_entrypoints = []
    removed_entrypoints = []

    for entrypoint in historical_entrypoints:
        is_valid, corrected_module, corrected_attr = validate_entrypoint(
            entrypoint, module_dir
        )

        if is_valid:
            corrected_ep = f"{corrected_module}.{corrected_attr}"
            validated_entrypoints.append(corrected_ep)

            if corrected_ep != entrypoint:
                fixed_entrypoints.append((entrypoint, corrected_ep))
                print(f"   ✓ Fixed: {entrypoint} → {corrected_ep}")
            else:
                print(f"   ✓ Valid: {entrypoint}")
        else:
            removed_entrypoints.append(entrypoint)
            print(f"   ✗ Removed: {entrypoint} (not found in code)")

    # Update manifest
    if not dry_run:
        manifest["runtime"]["entrypoints"] = validated_entrypoints

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline

    return len(fixed_entrypoints), len(removed_entrypoints), len(validated_entrypoints)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix manifest entrypoints")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    args = parser.parse_args()

    # Determine repository root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent

    print("🔍 Manifest Entrypoint Fixer")
    print("=" * 60)

    if args.dry_run:
        print("🧪 DRY RUN MODE - No changes will be made")
        print()

    # Step 1: Get historical entrypoints
    historical_data = get_historical_entrypoints(repo_root)

    if not historical_data:
        print("❌ No historical entrypoints found")
        return 1

    # Step 2: Process each manifest
    print(f"\n🔨 Processing {len(historical_data)} modules...")

    total_fixed = 0
    total_removed = 0
    total_kept = 0

    for manifest_path_str, entrypoints in sorted(historical_data.items()):
        manifest_path = Path(manifest_path_str)

        if not manifest_path.exists():
            print(f"\n⚠️  Skipping {manifest_path.name} (file no longer exists)")
            continue

        fixed, removed, kept = fix_manifest_entrypoints(
            manifest_path, entrypoints, args.dry_run
        )

        total_fixed += fixed
        total_removed += removed
        total_kept += kept

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"   Entrypoints validated: {total_kept}")
    print(f"   Entrypoints fixed: {total_fixed}")
    print(f"   Entrypoints removed: {total_removed}")
    print(f"   Total processed: {total_kept + total_removed}")

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    else:
        print("\n✅ Manifests updated successfully")
        print("\nNext steps:")
        print("  1. Run: make manifests-validate")
        print("  2. Run: make conformance-generate")
        print("  3. Run: pytest tests/conformance/ -v")

    return 0


if __name__ == "__main__":
    sys.exit(main())
