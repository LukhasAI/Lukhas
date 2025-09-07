#!/usr/bin/env python3
"""
Aggressive Linting Fix - Fixes all auto-fixable issues
USE WITH CAUTION - Review changes before committing
"""
import subprocess
import sys
import time
from pathlib import Path


def aggressive_fix_directory(directory: str):
    """Aggressively fix all issues in a directory"""
    print(f"\n🔥 Aggressively fixing {directory}...")

    if not Path(directory).exists():
        print(f"  Directory {directory} not found")
        return

    # Count initial issues
    initial_count = (
        subprocess.run(
            ["flake8", directory, "--count", "--exit-zero", "--max-line-length=88"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        .stdout.strip()
        .split("\n")[-1]
    )

    print(f"  Initial issues: {initial_count}")

    # Step 1: Remove ALL unused imports and variables
    print("  1. Removing unused imports and variables...")
    subprocess.run(
        [
            "autoflake",
            "--in-place",
            "--recursive",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--remove-duplicate-keys",
            "--ignore-init-module-imports",
            directory,
        ],
        capture_output=True,
        timeout=60,
    )

    # Step 2: Fix import sorting
    print("  2. Sorting imports...")
    subprocess.run(
        [
            "isort",
            "--profile",
            "black",
            "--line-length",
            "88",
            "--force-single-line",
            "--force-alphabetical-sort-within-sections",
            "--quiet",
            "--recursive",
            directory,
        ],
        capture_output=True,
        timeout=60,
    )

    # Step 3: Apply Black formatting
    print("  3. Applying Black formatting...")
    subprocess.run(
        [
            "black",
            "--line-length",
            "88",
            "--target-version",
            "py39",
            "--quiet",
            "--exclude",
            "migrations",
            directory,
        ],
        capture_output=True,
        timeout=60,
    )

    # Step 4: Apply Ruff fixes
    print("  4. Applying Ruff fixes...")
    subprocess.run(
        [
            "ruff",
            "check",
            "--fix",
            "--unsafe-fixes",  # Apply even unsafe fixes
            "--exit-zero",
            directory,
        ],
        capture_output=True,
        timeout=60,
    )

    # Step 5: Apply autopep8 for remaining PEP8 issues
    print("  5. Applying autopep8...")
    subprocess.run(
        [
            "autopep8",
            "--in-place",
            "--recursive",
            "--aggressive",
            "--aggressive",  # Double aggressive mode
            "--max-line-length",
            "88",
            directory,
        ],
        capture_output=True,
        timeout=60,
    )

    # Count final issues
    final_count = (
        subprocess.run(
            ["flake8", directory, "--count", "--exit-zero", "--max-line-length=88"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        .stdout.strip()
        .split("\n")[-1]
    )

    print(f"  Final issues: {final_count}")

    try:
        initial = int(initial_count)
        final = int(final_count)
        reduction = initial - final
        percent = (reduction / initial * 100) if initial > 0 else 0
        print(f"  ✅ Fixed {reduction} issues ({percent:.1f}% reduction)")
    except BaseException:
        print("  ✅ Completed aggressive fix")


def main():
    """Main function"""
    print("🚨 AGGRESSIVE FIX MODE 🚨")
    print("=" * 60)
    print("⚠️  WARNING: This will make extensive changes!")
    print("⚠️  Review all changes with 'git diff' before committing")
    print("=" * 60)

    # Install missing tools
    print("\n📦 Ensuring all tools are installed...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "autoflake",
            "isort",
            "black",
            "ruff",
            "autopep8",
            "flake8",
            "--quiet",
        ]
    )

    # Target the worst offenders
    directories = [
        "core",  # 1866 issues
        "tools",  # 1065 issues
        "bridge",  # 349 issues
        "tests",  # 251 issues
        "lukhas",  # 11 issues
    ]

    total_start = time.time()

    for directory in directories:
        aggressive_fix_directory(directory)

    total_time = time.time() - total_start

    print("\n" + "=" * 60)
    print("🏁 AGGRESSIVE FIX COMPLETE")
    print("=" * 60)
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print("\n📝 Next steps:")
    print("1. Review changes: git diff --stat")
    print("2. Check specific changes: git diff <file>")
    print("3. Run tests: make test")
    print("4. If satisfied: git add -A && git commit -m 'fix: aggressive linting cleanup'")
    print("5. If not satisfied: git checkout -- .")
    print("\n⚠️  IMPORTANT: Test critical functionality before committing!")


if __name__ == "__main__":
    response = input("\n⚠️  This will make EXTENSIVE changes. Continue? (yes/no): ")
    if response.lower() == "yes":
        main()
    else:
        print("Aborted.")
        sys.exit(0)
