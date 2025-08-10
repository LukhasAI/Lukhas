#!/usr/bin/env python3
"""
Check Python syntax across the codebase.
"""

import ast
from pathlib import Path
from typing import Dict, List, Tuple


def check_python_syntax(filepath: Path) -> Tuple[bool, List[str]]:
    """Check if a Python file has valid syntax."""
    errors = []

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            return False, [f"Could not read file: {e}"]

    try:
        ast.parse(content, filename=str(filepath))
        return True, []
    except SyntaxError as e:
        errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")
        if e.text:
            errors.append(f"  {e.text.strip()}")
            if e.offset:
                errors.append(f"  {' ' * (e.offset - 1)}^")
    except Exception as e:
        errors.append(f"Unexpected error: {type(e).__name__}: {e}")

    return False, errors


def check_imports(filepath: Path) -> List[str]:
    """Check for common import issues."""
    issues = []

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except:
        return []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check for old lukhas imports
        if "from lukhas." in stripped or "import lukhas." in stripped:
            issues.append(f"Line {i}: Old lukhas import found: {stripped}")

        # Check for broken relative imports
        if stripped.startswith("from ..") and "import" in stripped:
            # Count the dots to determine the level
            parts = stripped.split()
            if len(parts) > 1:
                dots = parts[1]
                level = dots.count(".")
                if level > 3:
                    issues.append(
                        f"Line {i}: Deeply nested relative import (level {level}): {stripped}"
                    )

    return issues


def scan_directory(directory: Path) -> Dict[str, Dict[str, List[str]]]:
    """Scan directory for Python files and check syntax."""
    results = {}

    python_files = list(directory.rglob("*.py"))
    total_files = len(python_files)

    print(f"Found {total_files} Python files to check...\n")

    syntax_errors = 0
    import_issues = 0

    for i, py_file in enumerate(python_files):
        # Skip certain directories
        if any(
            skip in str(py_file)
            for skip in [".venv", "__pycache__", "node_modules", ".git", ".mypy_cache"]
        ):
            continue

        # Show progress
        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{total_files} files checked...")

        file_results = {}

        # Check syntax
        valid, errors = check_python_syntax(py_file)
        if not valid:
            file_results["syntax_errors"] = errors
            syntax_errors += 1

        # Check imports
        import_issues_found = check_imports(py_file)
        if import_issues_found:
            file_results["import_issues"] = import_issues_found
            import_issues += 1

        if file_results:
            results[str(py_file.relative_to(directory))] = file_results

    print("\nChecking complete!")
    print(f"Total files with syntax errors: {syntax_errors}")
    print(f"Total files with import issues: {import_issues}")

    return results


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Check Python syntax across codebase")
    parser.add_argument("--path", type=str, default=".", help="Path to scan")
    parser.add_argument("--verbose", action="store_true", help="Show all errors")
    parser.add_argument(
        "--fix-imports", action="store_true", help="Suggest import fixes"
    )
    args = parser.parse_args()

    base_path = Path(args.path).resolve()
    print(f"Checking Python syntax in: {base_path}")
    print("-" * 80)

    results = scan_directory(base_path)

    if results:
        print(f"\n\nFound issues in {len(results)} files:\n")

        # Group by error type
        syntax_error_files = []
        import_issue_files = []

        for filepath, issues in results.items():
            if "syntax_errors" in issues:
                syntax_error_files.append((filepath, issues["syntax_errors"]))
            if "import_issues" in issues:
                import_issue_files.append((filepath, issues["import_issues"]))

        # Show syntax errors first (more critical)
        if syntax_error_files:
            print(f"\n{'='*80}")
            print(f"SYNTAX ERRORS ({len(syntax_error_files)} files):")
            print(f"{'='*80}\n")

            for filepath, errors in sorted(syntax_error_files):
                print(f"\n{filepath}:")
                for error in errors:
                    print(f"  {error}")

        # Then show import issues
        if import_issue_files:
            print(f"\n{'='*80}")
            print(f"IMPORT ISSUES ({len(import_issue_files)} files):")
            print(f"{'='*80}\n")

            if args.verbose:
                for filepath, issues in sorted(import_issue_files):
                    print(f"\n{filepath}:")
                    for issue in issues:
                        print(f"  {issue}")
            else:
                print("Run with --verbose to see detailed import issues")
                print("\nFiles with import issues:")
                for filepath, _ in sorted(import_issue_files):
                    print(f"  - {filepath}")
    else:
        print("\n✅ No syntax or import issues found!")


if __name__ == "__main__":
    main()
