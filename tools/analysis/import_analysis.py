#!/usr/bin/env python3
"""
🔍  Import Analysis Tool
==========================
Identifies and analyzes import errors across the LUKHAS  codebase.
"""
import logging
import time
import random
import streamlit as st

import ast
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ImportAnalyzer:
    """Analyzes Python imports and identifies errors"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.import_errors: list[dict] = []
        self.import_graph: dict[str, set[str]] = defaultdict(set)
        self.missing_modules: set[str] = set()
        self.circular_imports: list[list[str]] = []

    def analyze_file(self, file_path: Path) -> None:
        """Analyze imports in a single Python file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.import_errors.append(
                    {
                        "file": str(file_path.relative_to(self.root_path)),
                        "error": f"Syntax error: {e}",
                        "line": e.lineno,
                    }
                )
                return

            # Extract imports
            module_name = self._path_to_module(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import(file_path, alias.name, node.lineno)
                        self.import_graph[module_name].add(alias.name)

                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.level == 0:  # Absolute import
                        module = node.module
                    else:  # Relative import
                        module = self._resolve_relative_import(file_path, node.module, node.level)

                    self._check_import(file_path, module, node.lineno)
                    self.import_graph[module_name].add(module)

        except Exception as e:
            self.import_errors.append(
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "error": f"Failed to analyze: {e}",
                    "line": 0,
                }
            )

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        rel_path = file_path.relative_to(self.root_path)
        parts = [*list(rel_path.parts[:-1]), rel_path.stem]
        return ".".join(parts)

    def _resolve_relative_import(self, file_path: Path, module: Optional[str], level: int) -> str:
        """Resolve relative import to absolute module name"""
        current_parts = self._path_to_module(file_path).split(".")

        # Go up 'level' directories
        if level > len(current_parts):
            return module or ""

        base_parts = current_parts[:-level]

        if module:
            return ".".join(base_parts + module.split("."))
        else:
            return ".".join(base_parts)

    def _check_import(self, file_path: Path, module_name: str, line_no: int) -> None:
        """Check if an import is valid"""
        # Skip built-in modules
        if module_name in sys.builtin_module_names:
            return

        # Check if it's a standard library module
        if self._is_stdlib_module(module_name):
            return

        # Check if it's an installed package
        if self._is_installed_package(module_name):
            return

        # Check if it's a local module
        if self._is_local_module(module_name):
            return

        # Import not found
        self.import_errors.append(
            {
                "file": str(file_path.relative_to(self.root_path)),
                "error": f"Cannot import '{module_name}'",
                "line": line_no,
                "module": module_name,
            }
        )
        self.missing_modules.add(module_name)

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if module is in standard library"""
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "time",
            "datetime",
            "random",
            "math",
            "collections",
            "itertools",
            "functools",
            "typing",
            "enum",
            "pathlib",
            "asyncio",
            "logging",
            "unittest",
            "abc",
            "re",
            "hashlib",
            "pickle",
            "tempfile",
            "shutil",
            "subprocess",
        }

        # Check top-level module
        top_module = module_name.split(".")[0]
        return top_module in stdlib_modules

    def _is_installed_package(self, module_name: str) -> bool:
        """Check if module is an installed package"""
        try:
            spec = importlib.util.find_spec(module_name.split(".")[0])
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def _is_local_module(self, module_name: str) -> bool:
        """Check if module exists locally in the project"""
        # Convert module name to potential file paths
        parts = module_name.split(".")

        # Check as package (__init__.py)
        package_path = self.root_path / Path(*parts) / "__init__.py"
        if package_path.exists():
            return True

        # Check as module (.py file)
        if parts:
            module_path = self.root_path / Path(*parts[:-1]) / f"{parts[-1]}.py"
            if module_path.exists():
                return True

        return False

    def find_circular_imports(self) -> None:
        """Detect circular import dependencies"""
        visited = set()
        rec_stack = set()
        path = []

        def dfs(module: str) -> bool:
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for imported in self.import_graph.get(module, set()):
                if imported not in visited:
                    if dfs(imported):
                        return True
                elif imported in rec_stack:
                    # Found circular import
                    cycle_start = path.index(imported)
                    self.circular_imports.append(path[cycle_start:] + [imported])

            path.pop()
            rec_stack.remove(module)
            return False

        for module in self.import_graph:
            if module not in visited:
                dfs(module)

    def analyze_directory(self, directory: Path) -> None:
        """Analyze all Python files in directory"""
        for py_file in directory.rglob("*.py"):
            # Skip __pycache__ and other generated files
            if "__pycache__" in str(py_file):
                continue
            if ".pyc" in str(py_file):
                continue

            self.analyze_file(py_file)

    def generate_report(self) -> dict:
        """Generate analysis report"""
        # Group errors by type
        errors_by_type = defaultdict(list)
        for error in self.import_errors:
            if "Cannot import" in error["error"]:
                errors_by_type["missing_imports"].append(error)
            elif "Syntax error" in error["error"]:
                errors_by_type["syntax_errors"].append(error)
            else:
                errors_by_type["other_errors"].append(error)

        # Group missing imports by module
        missing_by_module = defaultdict(list)
        for error in errors_by_type["missing_imports"]:
            if "module" in error:
                missing_by_module[error["module"]].append(error["file"])

        return {
            "total_errors": len(self.import_errors),
            "errors_by_type": dict(errors_by_type),
            "missing_modules": sorted(self.missing_modules),
            "missing_by_module": dict(missing_by_module),
            "circular_imports": self.circular_imports,
            "total_files_analyzed": len(self.import_graph),
        }


def main():
    """Main analysis function"""
    print("🔍  Import Analysis")
    print("=" * 60)

    analyzer = ImportAnalyzer(PROJECT_ROOT)

    # Analyze all Python files
    print("\n📂 Analyzing Python files...")
    analyzer.analyze_directory(PROJECT_ROOT)

    # Find circular imports
    print("🔄 Checking for circular imports...")
    analyzer.find_circular_imports()

    # Generate report
    report = analyzer.generate_report()

    # Display results
    print("\n📊 Analysis Results:")
    print(f"   Total files analyzed: {report['total_files_analyzed']}")
    print(f"   Total import errors: {report['total_errors']}")

    if report["errors_by_type"]["syntax_errors"]:
        print(f"\n❌ Syntax Errors ({len(report['errors_by_type']['syntax_errors'])}):")
        for error in report["errors_by_type"]["syntax_errors"][:5]:
            print(f"   • {error['file']}:{error['line']} - {error['error']}")

    if report["missing_modules"]:
        print(f"\n❌ Missing Modules ({len(report['missing_modules'])}):")
        for module in sorted(report["missing_modules"])[:10]:
            files = report["missing_by_module"][module]
            print(f"   • {module} (used in {len(files)} files)")
            for file in files[:3]:
                print(f"      - {file}")
            if len(files) > 3:
                print(f"      ... and {len(files)} - 3} more")

    if report["circular_imports"]:
        print(f"\n🔄 Circular Imports ({len(report['circular_imports'])}):")
        for cycle in report["circular_imports"][:5]:
            print(f"   • {' → '.join(cycle)}")

    # Suggest fixes
    print("\n💡 Suggested Fixes:")

    # Group missing imports by probable fix
    local_missing = []
    external_missing = []

    for module in report["missing_modules"]:
        if module.startswith(("lukhas", "core", "memory", "orchestration", "consciousness")):
            local_missing.append(module)
        else:
            external_missing.append(module)

    if local_missing:
        print(f"\n   Local modules to fix ({len(local_missing)}):")
        for module in local_missing[:5]:
            print(f"   • {module} - Check module path and __init__.py files")

    if external_missing:
        print(f"\n   External packages to install ({len(external_missing)}):")
        for module in external_missing[:5]:
            print(f"   • {module} - Add to requirements.txt or install with pip")

    # Save detailed report
    import json

    report_path = PROJECT_ROOT / "docs" / "reports" / "analysis" / "_IMPORT_ANALYSIS_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {report_path.relative_to(PROJECT_ROOT)}")

    return report["total_errors"]


if __name__ == "__main__":
    sys.exit(main())
