#!/usr/bin/env python3
"""
Migrate test files to module-local tests/ directories.

Uses git mv for history preservation.
Adds conftest.py if missing.
Updates pytest collection paths.
"""
import subprocess
import sys
from pathlib import Path
ART = Path("artifacts")


def find_test_files() -> dict[str, str]:
    """Find all test files and infer their module from path."""
    test_mapping = {}

    # Scan tests/ directory
    tests_root = Path("tests")
    if not tests_root.exists():
        return test_mapping

    for test_file in tests_root.rglob("test_*.py"):
        # Infer module from path
        # tests/unit/<module>/... → <module>
        # tests/integration/<module>/... → <module>
        parts = test_file.parts

        module = None
        if "unit" in parts:
            unit_idx = parts.index("unit")
            if unit_idx + 1 < len(parts):
                module = parts[unit_idx + 1]
        elif "integration" in parts:
            int_idx = parts.index("integration")
            if int_idx + 1 < len(parts):
                module = parts[int_idx + 1]
        elif len(parts) > 2:
            # tests/<module>/test_*.py
            module = parts[1]

        if module:
            test_mapping[str(test_file)] = module

    return test_mapping


def create_conftest(module_tests_dir: Path):
    """Create conftest.py if missing."""
    conftest_path = module_tests_dir / "conftest.py"

    if conftest_path.exists():
        return

    content = f'''"""Test configuration for {module_tests_dir.parent.name} module."""
import pytest
import sys
from pathlib import Path

# Add module root to Python path
module_root = Path(__file__).parent.parent
if str(module_root) not in sys.path:
    sys.path.insert(0, str(module_root))


@pytest.fixture
def module_root_path():
    """Provide module root directory."""
    return Path(__file__).parent.parent
'''

    conftest_path.write_text(content)
    print(f"  ✅ Created conftest.py: {conftest_path}")


def git_mv(old_path: Path, new_path: Path) -> bool:
    """Move file using git mv (preserves history)."""
    try:
        # Ensure target directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Use git mv for history preservation
        subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            capture_output=True,
            text=True,
            check=True
        )

        return True

    except subprocess.CalledProcessError as e:
        print(f"  ❌ git mv failed: {e.stderr}")
        return False


def migrate_tests(test_mapping: dict[str, str], dry_run: bool = False):
    """Migrate test files to module-local directories."""
    moved_count = 0
    skipped_count = 0
    modules_with_tests: set[str] = set()

    for test_file_str, module in test_mapping.items():
        test_file = Path(test_file_str)

        # Determine target path
        # tests/unit/<module>/test_*.py → <module>/tests/unit/test_*.py
        # tests/integration/<module>/test_*.py → <module>/tests/integration/test_*.py
        parts = test_file.parts
        if "unit" in parts or "integration" in parts:
            test_type = "unit" if "unit" in parts else "integration"
            # Get relative path after module
            type_idx = parts.index(test_type)
            relative_parts = parts[type_idx + 2:]  # Skip test_type/<module>/
            new_path = Path(module) / "tests" / test_type / Path(*relative_parts) if relative_parts else Path(module) / "tests" / test_type / test_file.name
        else:
            # tests/<module>/test_*.py → <module>/tests/test_*.py
            new_path = Path(module) / "tests" / test_file.name

        if dry_run:
            print(f"📋 Would move: {test_file} → {new_path}")
            continue

        # Skip if already in module directory
        if str(new_path) == str(test_file):
            continue

        print(f"🔄 Migrating: {test_file} → {new_path}")

        # Perform git mv
        if git_mv(test_file, new_path):
            modules_with_tests.add(module)
            moved_count += 1
        else:
            print(f"  ⚠️  Failed to move: {test_file}")
            skipped_count += 1

    # Create conftest.py for modules with tests
    if not dry_run:
        for module in modules_with_tests:
            module_tests_dir = Path(module) / "tests"
            create_conftest(module_tests_dir)

    return moved_count, skipped_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migrate tests to module-local directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    args = parser.parse_args()

    print("🔍 Finding test files...")
    test_mapping = find_test_files()

    total = len(test_mapping)
    print(f"📊 Found {total} test files")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")

    moved, skipped = migrate_tests(test_mapping, dry_run=args.dry_run)

    print("\n✅ Migration complete!")
    print(f"   Moved: {moved} files")
    print(f"   Skipped: {skipped} files")

    if args.dry_run:
        print("\n💡 Run without --dry-run to execute migration")

    return 0


if __name__ == "__main__":
    sys.exit(main())
