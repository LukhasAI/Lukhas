#!/usr/bin/env python3
'''
Batch autofix for code quality improvements

Runs: autoflake → isort → black → ruff --fix
Small batches with test verification between changes.
'''

import subprocess
from pathlib import Path


def run_autofix_batch(module_path: str) -> bool:
    """Run autofix tools on module and verify tests pass"""

    print(f"\n{'='*60}")
    print(f"Autofix batch: {module_path}")
    print('='*60)

    # Step 1: autoflake (remove unused imports and variables)
    print("\n1. Running autoflake...")
    subprocess.run([
        "autoflake",
        "--in-place",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--remove-duplicate-keys",
        "--recursive",
        module_path
    ], check=True)

    # Step 2: isort (organize imports)
    print("\n2. Running isort...")
    subprocess.run([
        "isort",
        module_path
    ], check=True)

    # Step 3: black (format code)
    print("\n3. Running black...")
    subprocess.run([
        "black",
        module_path
    ], check=True)

    # Step 4: ruff --fix
    print("\n4. Running ruff --fix...")
    subprocess.run([
        "ruff",
        "check",
        "--fix",
        module_path
    ], check=True)

    # Step 5: Run tests to verify no breakage
    print("\n5. Running tests...")
    test_result = subprocess.run([
        "pytest",
        f"tests/unit/test_{Path(module_path).stem}.py",
        "-v"
    ])

    if test_result.returncode != 0:
        print(f"\n⚠️  Tests failed for {module_path}")
        return False

    print(f"\n✅ Autofix batch complete for {module_path}")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run batch autofix")
    parser.add_argument("module", help="Module path to autofix")
    args = parser.parse_args()

    success = run_autofix_batch(args.module)
    exit(0 if success else 1)
