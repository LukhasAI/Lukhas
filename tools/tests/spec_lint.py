#!/usr/bin/env python3
"""
T4 Spec Lint - Test Ownership Enforcement
=========================================

Enforces that all tests have proper markers and ownership.
Rejects unmarked tests (ownership required).
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List


class TestMarkerVisitor(ast.NodeVisitor):
    """AST visitor to find test functions and their markers."""

    def __init__(self):
        self.test_functions = []
        self.current_markers = set()

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            # Check for pytest.mark decorators
            markers = set()
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Attribute):
                    # pytest.mark.tier1, etc.
                    if isinstance(decorator.value, ast.Attribute) and decorator.value.attr == "mark":
                        markers.add(decorator.attr)
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                    # pytest.mark.tier1(), etc.
                    if isinstance(decorator.func.value, ast.Attribute) and decorator.func.value.attr == "mark":
                        markers.add(decorator.func.attr)

            self.test_functions.append({"name": node.name, "line": node.lineno, "markers": markers})

        self.generic_visit(node)


def lint_test_file(file_path: Path) -> List[str]:
    """Lint a single test file for marker compliance."""
    errors = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        visitor = TestMarkerVisitor()
        visitor.visit(tree)

        required_markers = {"tier1", "tier2", "tier3", "tier4", "smoke", "matriz", "golden", "quarantine"}

        for test_func in visitor.test_functions:
            if not test_func["markers"]:
                errors.append(
                    f"{file_path}:{test_func['line']} - Test '{test_func['name']}' has no markers (ownership required)"
                )
            elif not test_func["markers"] & required_markers:
                errors.append(
                    f"{file_path}:{test_func['line']} - Test '{test_func['name']}' has no tier/category marker"
                )

    except Exception as e:
        errors.append(f"{file_path} - Failed to parse: {e}")

    return errors


def main():
    """Main spec lint entry point."""
    parser = argparse.ArgumentParser(description="T4 Test Spec Linter")
    parser.add_argument("paths", nargs="*", default=["tests/"], help="Paths to lint")
    parser.add_argument("--strict", action="store_true", help="Fail on any violations")
    args = parser.parse_args()

    all_errors = []

    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file() and path.name.startswith("test_") and path.suffix == ".py":
            all_errors.extend(lint_test_file(path))
        elif path.is_dir():
            for test_file in path.rglob("test_*.py"):
                all_errors.extend(lint_test_file(test_file))

    if all_errors:
        print("T4 Spec Lint Violations:")
        for error in all_errors:
            print(f"  ❌ {error}")
        print(f"\nTotal violations: {len(all_errors)}")

        if args.strict:
            sys.exit(1)
    else:
        print("✅ All tests properly marked and owned")


if __name__ == "__main__":
    main()
