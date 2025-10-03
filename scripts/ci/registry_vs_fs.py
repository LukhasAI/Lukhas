#!/usr/bin/env python3
"""
T4/0.01% Registry vs Filesystem Validation Gate
================================================

Cross-check gate: fails if MODULE_REGISTRY.json disagrees with filesystem.

Checks:
- Registry says module has docs/ but FS disagrees → FAIL
- Registry says module has tests/ but FS disagrees → FAIL
- FS has docs/ but registry doesn't list them → FAIL
- FS has tests/ but registry doesn't list them → FAIL

Guarantees:
- Hard fail on discrepancies
- Actionable error messages
- Fast execution (filesystem checks only)

Usage:
  python scripts/ci/registry_vs_fs.py
  python scripts/ci/registry_vs_fs.py --verbose
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "_generated" / "MODULE_REGISTRY.json"


def check_module(module: dict, root: Path, verbose: bool = False) -> List[str]:
    """
    Validate single module against filesystem.

    Returns:
        List of error messages (empty = valid)
    """
    errors = []
    module_name = module["name"]
    module_path = root / module["path"]

    if not module_path.exists():
        errors.append(f"{module_name}: module path does not exist: {module['path']}")
        return errors

    # Check docs
    registry_docs = set(module.get("docs", []))
    docs_dir = module_path / "docs"

    if docs_dir.exists() and docs_dir.is_dir():
        # FS has docs/ - check registry lists them
        fs_docs = set([
            str(p.relative_to(root))
            for p in docs_dir.rglob("*.md")
        ])

        missing_from_registry = fs_docs - registry_docs
        if missing_from_registry:
            errors.append(
                f"{module_name}: docs/ exists but {len(missing_from_registry)} files not in registry"
            )
            if verbose:
                for doc in sorted(missing_from_registry)[:5]:
                    errors.append(f"  Missing: {doc}")
    else:
        # FS has no docs/ - registry should be empty
        if registry_docs:
            errors.append(
                f"{module_name}: registry lists {len(registry_docs)} docs but docs/ does not exist"
            )

    # Check tests
    registry_tests = set(module.get("tests", []))
    tests_dir = module_path / "tests"

    if tests_dir.exists() and tests_dir.is_dir():
        # FS has tests/ - check registry lists them
        fs_tests = set([
            str(p.relative_to(root))
            for p in tests_dir.rglob("*.py")
        ])

        missing_from_registry = fs_tests - registry_tests
        if missing_from_registry:
            errors.append(
                f"{module_name}: tests/ exists but {len(missing_from_registry)} files not in registry"
            )
            if verbose:
                for test in sorted(missing_from_registry)[:5]:
                    errors.append(f"  Missing: {test}")
    else:
        # FS has no tests/ - registry should be empty
        if registry_tests:
            errors.append(
                f"{module_name}: registry lists {len(registry_tests)} tests but tests/ does not exist"
            )

    return errors


def main():
    ap = argparse.ArgumentParser(
        description="Validate MODULE_REGISTRY.json against filesystem"
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed error messages"
    )
    args = ap.parse_args()

    # Load registry
    if not REGISTRY.exists():
        print(f"❌ Registry not found: {REGISTRY.relative_to(ROOT)}", file=sys.stderr)
        print("   Run: python scripts/generate_module_registry.py", file=sys.stderr)
        sys.exit(1)

    try:
        registry = json.loads(REGISTRY.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in registry: {e}", file=sys.stderr)
        sys.exit(1)

    modules = registry.get("modules", [])
    print(f"🔍 Validating {len(modules)} modules against filesystem...")

    all_errors = []

    for module in modules:
        errors = check_module(module, ROOT, args.verbose)
        all_errors.extend(errors)

    if all_errors:
        print(f"\n❌ Registry validation failed ({len(all_errors)} errors):\n", file=sys.stderr)
        for error in all_errors:
            print(f"  {error}", file=sys.stderr)
        print("\n💡 Run: python scripts/generate_module_registry.py", file=sys.stderr)
        sys.exit(1)

    print("✅ Registry matches filesystem")
    sys.exit(0)


if __name__ == "__main__":
    main()
