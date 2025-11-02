# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
# do_not_edit: true
# human_editable: false
#
#!/usr/bin/env python3
"""
T4 Contract Check - Contract-First Validation
=============================================

Refuses new tests where package lacks CONTRACT.md and matching spec.
Contract-first approach enforcement.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Set


def get_changed_test_files(base_ref: str) -> Set[Path]:
    """Get test files that have been changed since base_ref."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, "HEAD"], capture_output=True, text=True, check=True
        )

        changed_files = set()
        for line in result.stdout.strip().split("\n"):
            if line and ("test_" in line or line.startswith("tests/")):
                path = Path(line)
                if path.exists() and path.suffix == ".py":
                    changed_files.add(path)

        return changed_files
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not get git diff: {e}")
        return set()


def find_package_for_test(test_path: Path) -> Path:
    """Find the package directory that this test is testing."""
    # tests/unit/candidate/aka_qualia/test_memory.py -> candidate/aka_qualia/
    # tests/integration/orchestration/test_basic.py -> orchestration/

    parts = test_path.parts

    # Remove 'tests' and test category (unit/integration/e2e)
    if "tests" in parts:
        idx = parts.index("tests")
        remaining_parts = parts[idx + 1 :]

        # Skip category (unit/integration/e2e) if present
        if remaining_parts and remaining_parts[0] in ["unit", "integration", "e2e", "contract", "smoke"]:
            remaining_parts = remaining_parts[1:]

        # Remove test file name
        if remaining_parts:
            package_parts = remaining_parts[:-1]  # Remove test file
            if package_parts:
                package_path = Path(*package_parts)
                if package_path.exists():
                    return package_path

    return None


def has_contract_md(package_path: Path) -> bool:
    """Check if package has CONTRACT.md file."""
    contract_file = package_path / "CONTRACT.md"
    return contract_file.exists()


def has_matching_spec(test_path: Path) -> bool:
    """Check if test has matching spec in tests/specs/."""
    # Convert test path to spec path
    # tests/unit/candidate/aka_qualia/test_memory.py -> tests/specs/candidate_aka_qualia_memory_spec.yaml

    parts = test_path.parts
    if "tests" in parts:
        idx = parts.index("tests")
        remaining_parts = parts[idx + 1 :]

        # Skip category
        if remaining_parts and remaining_parts[0] in ["unit", "integration", "e2e", "contract", "smoke"]:
            remaining_parts = remaining_parts[1:]

        # Build spec name
        if remaining_parts:
            # Remove .py extension and test_ prefix from filename
            filename = remaining_parts[-1]
            if filename.startswith("test_"):
                filename = filename[5:]  # Remove 'test_'
            if filename.endswith(".py"):
                filename = filename[:-3]  # Remove '.py'

            # Join with underscores
            spec_parts = [*list(remaining_parts[:-1]), filename]
            spec_name = "_".join(spec_parts) + "_spec.yaml"

            spec_path = Path("tests/specs") / spec_name
            return spec_path.exists()

    return False


def main():
    """Main contract check entry point."""
    parser = argparse.ArgumentParser(description="T4 Contract-First Check")
    parser.add_argument("base_ref", nargs="?", default="origin/main", help="Base git ref to compare against")
    parser.add_argument("--strict", action="store_true", help="Fail on contract violations")
    args = parser.parse_args()

    changed_tests = get_changed_test_files(args.base_ref)

    if not changed_tests:
        print("✅ No test changes detected")
        return

    violations = []

    for test_path in changed_tests:
        package_path = find_package_for_test(test_path)

        if package_path:
            if not has_contract_md(package_path):
                violations.append(f"{test_path} -> Missing CONTRACT.md in {package_path}")

            if not has_matching_spec(test_path):
                violations.append(f"{test_path} -> Missing matching spec in tests/specs/")
        else:
            print(f"Warning: Could not determine package for {test_path}")

    if violations:
        print("T4 Contract Violations:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print(f"\nTotal violations: {len(violations)}")
        print("\nNote: Add CONTRACT.md to packages and create matching specs in tests/specs/")

        if args.strict:
            sys.exit(1)
    else:
        print(f"✅ All {len(changed_tests)} changed tests have proper contracts")


if __name__ == "__main__":
    main()
