#!/usr/bin/env python3
'''
Batch autofix for code quality improvements

Runs: autoflake → isort → black → ruff --fix
Small batches with test verification between changes.
'''

import os
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

    # Step 4: ruff --fix (auto-fixable issues)
    print("\n4. Running ruff --fix...")
    subprocess.run([
        "python3", "-m", "ruff", "check",
        "--fix",
        module_path
    ], check=False)  # Don't fail on remaining issues

    # Step 5: Verify tests still pass
    print("\n5. Running tests...")
    test_dir = Path(f"tests/unit/{module_path}")

    if not test_dir.is_dir() or not any(test_dir.iterdir()):
        print("🟡 No tests found, skipping test run.")
        return True

    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    # Create a local pytest.ini to avoid conflicts
    pytest_ini_path = test_dir / "pytest.ini"
    pytest_ini_content = "[pytest]\ntestpaths = .\nasyncio_mode = auto\n"

    # Create the directory if it doesn't exist
    test_dir.mkdir(parents=True, exist_ok=True)

    with open(pytest_ini_path, "w") as f:
        f.write(pytest_ini_content)

    result = subprocess.run([
        "python3", "-m", "pytest",
        str(test_dir),
        "-q"
    ], capture_output=True, text=True, env=env)

    # Clean up the local pytest.ini
    os.remove(pytest_ini_path)

    if result.returncode == 0:
        print("✅ Tests passed")
        return True
    else:
        print("❌ Tests failed - changes need review")
        print("--- begin test output ---")
        print(result.stdout)
        print(result.stderr)
        print("--- end test output ---")
        return False

# Priority modules for autofix (small batches)
MODULES = [
    "matriz",
]

def main():
    results = {}

    for module in MODULES:
        success = run_autofix_batch(module)
        results[module] = "✅" if success else "❌"

    print("\n" + "="*60)
    print("Autofix Summary")
    print("="*60)
    for module, status in results.items():
        print(f"{status} {module}")

if __name__ == "__main__":
    main()
