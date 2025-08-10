#!/usr/bin/env python3
"""
Comprehensive Isolation Analyzer
Finds all isolated Python files in the system, excluding test files, demos, scripts, and tools
"""

import ast
import json
import os
import re
from collections import defaultdict
from typing import Dict


class ComprehensiveIsolationAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.connections = defaultdict(set)
        self.all_modules = set()
        self.isolated_modules = set()

        # Directories to exclude
        self.exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "venv",
            "env",
            ".env",
            "tests",
            "test",
            "testing",
            "test_data",
            "examples",
            "demos",
            "demo",
            "scripts",
            "tools",
            "utils",
            "docs",
            "documentation",
            "benchmarks",
            "benchmark",
            ".branding_backup_20250731_073052",
            "archived",
            "archive",
            "backup",
            "tmp",
            "temp",
            "cache",
            "analysis-tools",  # One-time analysis scripts
        }

        # File patterns to exclude
        self.exclude_patterns = [
            r"test_.*\.py$",
            r".*_test\.py$",
            r".*_demo\.py$",
            r"demo_.*\.py$",
            r"example_.*\.py$",
            r".*_example\.py$",
            r"setup\.py$",
            r"__main__\.py$",
            r"conftest\.py$",
            r".*_backup\.py$",
            r".*_old\.py$",
            r".*_temp\.py$",
            r".*_migration\.py$",
            r".*_script\.py$",
            r".*_tool\.py$",
            r".*_analyzer\.py$",
            r".*_generator\.py$",
            r".*_fixer\.py$",
            r".*_updater\.py$",
        ]

    def should_analyze_file(self, file_path: str) -> bool:
        """Check if file should be analyzed"""
        # Check if in excluded directory
        path_parts = file_path.split(os.sep)
        for part in path_parts:
            if part.lower() in self.exclude_dirs:
                return False

        # Check file patterns
        filename = os.path.basename(file_path)
        for pattern in self.exclude_patterns:
            if re.match(pattern, filename, re.IGNORECASE):
                return False

        # Only analyze .py files
        return file_path.endswith(".py")

    def analyze(self):
        """Analyze all Python modules in the codebase"""
        print("Analyzing comprehensive module isolation...")

        # First pass: collect all modules
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.root_path)

                if self.should_analyze_file(relative_path):
                    self.all_modules.add(relative_path)
                    self.analyze_module(file_path, relative_path)

        # Second pass: find isolated modules
        self.find_isolated_modules()

        return self.generate_report()

    def analyze_module(self, file_path: str, relative_path: str):
        """Analyze a single Python module for imports"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                return

            tree = ast.parse(content)

            # Find imports
            has_imports = False
            has_exports = False

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    has_imports = True
                    for alias in node.names:
                        # Record connection
                        self.connections[relative_path].add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    has_imports = True
                    if node.module:
                        self.connections[relative_path].add(node.module)

                elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    has_exports = True

            # Check if module is imported by others
            module_name = relative_path.replace(".py", "").replace("/", ".")
            is_imported = False

            for other_path, imports in self.connections.items():
                if other_path != relative_path:
                    for imp in imports:
                        if (
                            module_name in imp
                            or relative_path.replace(".py", "") in imp
                        ):
                            is_imported = True
                            break

        except Exception:
            # Skip files with syntax errors
            pass

    def find_isolated_modules(self):
        """Find modules that are not connected to any other module"""
        for module in self.all_modules:
            module_name = module.replace(".py", "").replace("/", ".")

            # Check if module imports anything (has outgoing connections)
            has_imports = len(self.connections.get(module, set())) > 0

            # Check if module is imported by anything (has incoming connections)
            is_imported = False
            for other_module, imports in self.connections.items():
                if other_module != module:
                    for imp in imports:
                        if module_name in imp or module.replace(".py", "") in imp:
                            is_imported = True
                            break
                    if is_imported:
                        break

            # Module is isolated if it neither imports nor is imported
            if not has_imports and not is_imported:
                self.isolated_modules.add(module)

    def generate_report(self) -> Dict:
        """Generate isolation report"""
        # Group isolated modules by directory
        isolated_by_dir = defaultdict(list)
        for module in sorted(self.isolated_modules):
            dir_path = os.path.dirname(module)
            if not dir_path:
                dir_path = "root"
            isolated_by_dir[dir_path].append(module)

        # Sort directories by number of isolated files
        sorted_dirs = sorted(
            isolated_by_dir.items(), key=lambda x: len(x[1]), reverse=True
        )

        report = {
            "total_modules": len(self.all_modules),
            "isolated_modules": len(self.isolated_modules),
            "connected_modules": len(self.all_modules) - len(self.isolated_modules),
            "isolation_rate": (
                f"{len(self.isolated_modules) / len(self.all_modules) * 100:.1f}%"
                if self.all_modules
                else "0%"
            ),
            "isolated_by_directory": dict(sorted_dirs),
            "isolated_files": sorted(list(self.isolated_modules)),
        }

        # Print summary
        print(f"\n{'='*80}")
        print("COMPREHENSIVE MODULE ISOLATION ANALYSIS")
        print(f"{'='*80}")
        print(f"Total System Modules: {report['total_modules']}")
        print(f"Isolated Modules: {report['isolated_modules']}")
        print(f"Connected Modules: {report['connected_modules']}")
        print(f"Isolation Rate: {report['isolation_rate']}")

        if sorted_dirs:
            print("\nTop Directories with Isolated Modules:")
            for dir_path, modules in sorted_dirs[:10]:
                print(f"  {dir_path}: {len(modules)} isolated files")

        return report


def main():
    analyzer = ComprehensiveIsolationAnalyzer(".")
    report = analyzer.analyze()

    # Save detailed report
    with open("comprehensive_isolation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\nDetailed report saved to comprehensive_isolation_report.json")

    # Show some examples of isolated files
    if report["isolated_files"]:
        print("\nExample isolated files:")
        for file in report["isolated_files"][:10]:
            print(f"  - {file}")
        if len(report["isolated_files"]) > 10:
            print(f"  ... and {len(report['isolated_files']) - 10} more")


if __name__ == "__main__":
    main()
