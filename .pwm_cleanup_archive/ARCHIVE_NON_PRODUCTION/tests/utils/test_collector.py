#!/usr/bin/env python3
"""
Test Collector Utility for LUKHAS AGI System
============================================

This utility traverses all test files, validates their parsability with AST,
and reports uncollectable modules for diagnostic purposes.

ΛORIGIN_AGENT: Codex-Agent-C14
ΛTASK_ID: C-14
ΛCOMMIT_WINDOW: codex-phase2b-C14
ΛPROVED_BY: GitHub-Copilot/Codex-Integration
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List


class TestCollector:
    """Collects and validates test files for the LUKHAS AGI system."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.test_files = []
        self.errors = []

    def find_test_files(self) -> List[Path]:
        """Find all Python test files in the project."""
        test_files = []

        # Look for test files in common locations
        test_patterns = ["test_*.py", "*_test.py", "tests.py"]

        # Search in tests/ directory and subdirectories
        for pattern in test_patterns:
            test_files.extend(self.root_dir.rglob(pattern))

        return test_files

    def validate_syntax(self, file_path: Path) -> Dict[str, Any]:
        """Validate Python syntax using AST."""
        result = {
            "file": str(file_path),
            "valid": False,
            "error": None,
            "functions": [],
            "classes": [],
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse with AST
            tree = ast.parse(content, filename=str(file_path))

            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    result["classes"].append(node.name)

            result["valid"] = True

        except SyntaxError as e:
            result["error"] = f"SyntaxError: {e.msg} at line {e.lineno}"
        except Exception as e:
            result["error"] = f"Error: {str(e)}"

        return result

    def collect_and_validate(self) -> Dict[str, Any]:
        """Collect all test files and validate them."""
        self.test_files = self.find_test_files()

        results = {
            "total_files": len(self.test_files),
            "valid_files": 0,
            "invalid_files": 0,
            "files": [],
            "errors": [],
        }

        for test_file in self.test_files:
            validation_result = self.validate_syntax(test_file)
            results["files"].append(validation_result)

            if validation_result["valid"]:
                results["valid_files"] += 1
            else:
                results["invalid_files"] += 1
                results["errors"].append(
                    {"file": str(test_file), "error": validation_result["error"]}
                )

        return results

    def print_report(self, results: Dict[str, Any]):
        """Print a formatted report of test collection results."""
        print("🔍 LUKHAS AGI Test Collection Report")
        print("=" * 50)
        print(f"Total test files found: {results['total_files']}")
        print(f"Valid files: {results['valid_files']}")
        print(f"Invalid files: {results['invalid_files']}")
        print()

        if results["errors"]:
            print("❌ Files with errors:")
            for error in results["errors"]:
                print(f"  • {error['file']}: {error['error']}")
        else:
            print("✅ All test files are syntactically valid!")

        print()
        print("📋 Test Files Summary:")
        for file_result in results["files"]:
            status = "✅" if file_result["valid"] else "❌"
            print(f"  {status} {file_result['file']}")
            if file_result["functions"]:
                print(f"    Functions: {', '.join(file_result['functions'])}")
            if file_result["classes"]:
                print(f"    Classes: {', '.join(file_result['classes'])}")


def find_uncollectable_tests(root_dir: str = ".") -> List[str]:
    """ΛTRACE: detect syntax errors in test files."""
    collector = TestCollector(root_dir)
    results = collector.collect_and_validate()
    return [err["file"] for err in results["errors"]]


def main():
    """ΛTRACE: run test collector CLI."""
    collector = TestCollector()
    results = collector.collect_and_validate()
    collector.print_report(results)

    # Exit with error code if there are invalid files
    if results["invalid_files"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
