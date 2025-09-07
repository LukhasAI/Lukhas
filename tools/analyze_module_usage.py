#!/usr/bin/env python3
"""
Module Usage Analyzer for LUKHAS AI
Detects unused modules, orphaned files, and import paths
Trinity Framework: ⚛️🧠🛡️
"""
from consciousness.qi import qi
import streamlit as st

import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


class ModuleUsageAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.all_python_files = set()
        self.imported_modules = defaultdict(set)  # module -> files that import it
        self.file_imports = defaultdict(set)  # file -> modules it imports
        self.orphaned_files = set()
        self.entry_points = {
            "main.py",
            "api/main.py",
            "serve/app.py",
            "orchestration/brain/primary_hub.py",
            "consciousness/unified/auto_consciousness.py",
        }

    def find_all_python_files(self):
        """Find all Python files in the repository"""
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
            ".venv",
            "venv",
            "env",
            ".tox",
            "build",
            "dist",
            "egg-info",
            ".eggs",
            "node_modules",
            ".mypy_cache",
            ".backups",
            ".venv_test",
            "site-packages",
            ".github",
            "reports",
            "data",
            "logs",
            "tmp",
            "temp",
            "archive",
            "deprecated",
            "old",
            "backup",
            "test_results",
        }

        for root, dirs, files in os.walk(self.root_path):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    relative_path = full_path.relative_to(self.root_path)
                    self.all_python_files.add(str(relative_path))

    def extract_imports(self, file_path: str) -> set[str]:
        """Extract all imports from a Python file"""
        imports = set()
        full_path = self.root_path / file_path

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)
                    # Also track specific imports
                    for alias in node.names:
                        if alias.name != "*":
                            imports.add(f"{node.module}.{alias.name}")

        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            # Skip files with syntax errors or encoding issues
            pass

        return imports

    def resolve_import_to_file(self, import_name: str) -> list[str]:
        """Resolve an import name to actual file paths"""
        possible_files = []

        # Convert import to potential file paths
        parts = import_name.split(".")

        # Try as a module (directory with __init__.py)
        module_path = Path(*parts)
        init_file = module_path / "__init__.py"
        if (self.root_path / init_file).exists():
            possible_files.append(str(init_file))

        # Try as a direct file
        py_file = Path(*parts[:-1]) / f"{parts[-1]}.py" if len(parts) > 1 else Path(f"{parts[0]}.py")
        if (self.root_path / py_file).exists():
            possible_files.append(str(py_file))

        # Try with common prefixes
        for prefix in ["lukhas", "lukhas", "core", "bridge", "governance"]:
            prefixed_import = f"{prefix}.{import_name}"
            parts = prefixed_import.split(".")

            module_path = Path(*parts)
            init_file = module_path / "__init__.py"
            if (self.root_path / init_file).exists():
                possible_files.append(str(init_file))

            py_file = Path(*parts[:-1]) / f"{parts[-1]}.py" if len(parts) > 1 else Path(f"{parts[0]}.py")
            if (self.root_path / py_file).exists():
                possible_files.append(str(py_file))

        return possible_files

    def analyze_imports(self):
        """Analyze all imports and build dependency graph"""
        for py_file in self.all_python_files:
            imports = self.extract_imports(py_file)
            self.file_imports[py_file] = imports

            for import_name in imports:
                # Resolve import to actual files
                resolved_files = self.resolve_import_to_file(import_name)
                for resolved_file in resolved_files:
                    if resolved_file in self.all_python_files:
                        self.imported_modules[resolved_file].add(py_file)

    def find_reachable_files(self) -> set[str]:
        """Find all files reachable from entry points"""
        reachable = set()
        to_visit = list(self.entry_points)

        while to_visit:
            current = to_visit.pop()
            if current in reachable or current not in self.all_python_files:
                continue

            reachable.add(current)

            # Add all files imported by this file
            for import_name in self.file_imports.get(current, set()):
                resolved_files = self.resolve_import_to_file(import_name)
                for resolved_file in resolved_files:
                    if resolved_file not in reachable and resolved_file in self.all_python_files:
                        to_visit.append(resolved_file)

            # Also check test files that test this module
            if not current.startswith("tests/"):
                # Find corresponding test files
                current.replace(".py", "").replace("/", ".")
                test_patterns = [
                    f"tests/test_{Path(current}.stem}.py",
                    f"tests/{Path(current).parent}/test_{Path(current}.stem}.py",
                    f"tests/unit/test_{Path(current}.stem}.py",
                    f"tests/integration/test_{Path(current}.stem}.py",
                ]
                for test_pattern in test_patterns:
                    if test_pattern in self.all_python_files:
                        to_visit.append(test_pattern)

        return reachable

    def find_orphaned_files(self):
        """Find files that are never imported"""
        reachable = self.find_reachable_files()

        # Files that are never imported (excluding tests and scripts)
        never_imported = set()
        for py_file in self.all_python_files:
            # Skip test files, setup files, and special files
            if (
                py_file.startswith("tests/")
                or py_file.startswith("tools/")
                or py_file.startswith("scripts/")
                or py_file.endswith("setup.py")
                or py_file.endswith("conftest.py")
                or "__pycache__" in py_file
            ):
                continue

            # Check if file is imported by anyone
            if py_file not in self.imported_modules and py_file not in self.entry_points:
                never_imported.add(py_file)

        # Files not reachable from entry points
        unreachable = self.all_python_files - reachable

        # Combine both criteria
        self.orphaned_files = never_imported | unreachable

        # Remove false positives
        false_positives = {
            "CLAUDE.md",  # Documentation
            "README.md",  # Documentation
            "__init__.py",  # May be empty but needed
        }

        self.orphaned_files = {f for f in self.orphaned_files if not any(fp in f for fp in false_positives)}

    def analyze_module_directories(self) -> dict[str, dict]:
        """Analyze each module directory for usage statistics"""
        module_stats = {}

        # Main module directories
        modules = [
            "core",
            "bridge",
            "governance",
            "consciousness",
            "memory",
            "orchestration",
            "identity",
            "emotion",
            "quantum",
            "bio",
            "symbolic",
            "universal_language",
            "vivox",
            "qim",
            "lukhas",
            "api",
            "serve",
            "agents",
            "adapters",
            "architectures",
        ]

        for module in modules:
            module_path = self.root_path / module
            if not module_path.exists():
                continue

            module_files = [f for f in self.all_python_files if f.startswith(f"{module}/")]

            imported_files = [f for f in module_files if f in self.imported_modules]

            orphaned = [f for f in module_files if f in self.orphaned_files]

            module_stats[module] = {
                "total_files": len(module_files),
                "imported_files": len(imported_files),
                "orphaned_files": len(orphaned),
                "usage_percentage": ((len(imported_files) / len(module_files) * 100) if module_files else 0),
                "orphaned_list": sorted(orphaned)[:10],  # Top 10 orphaned files
            }

        return module_stats

    def generate_report(self):
        """Generate comprehensive usage report"""
        self.find_all_python_files()
        self.analyze_imports()
        self.find_orphaned_files()
        module_stats = self.analyze_module_directories()

        # Calculate overall statistics
        total_files = len(self.all_python_files)
        imported_files = len(self.imported_modules)
        orphaned_count = len(self.orphaned_files)

        report = {
            "summary": {
                "total_python_files": total_files,
                "imported_files": imported_files,
                "orphaned_files": orphaned_count,
                "usage_percentage": ((imported_files / total_files * 100) if total_files else 0),
                "entry_points": list(self.entry_points),
            },
            "module_statistics": module_stats,
            "top_orphaned_files": sorted(self.orphaned_files)[:50],
            "most_imported": sorted(
                [(f, len(importers)) for f, importers in self.imported_modules.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:20],
            "never_imported": sorted(
                [
                    f
                    for f in self.all_python_files
                    if f not in self.imported_modules
                    and not f.startswith("tests/")
                    and not f.startswith("tools/")
                    and f not in self.entry_points
                ]
            )[:30],
        }

        return report


def main():
    # Get repository root
    repo_root = Path(__file__).parent.parent

    print("🔍 Analyzing module usage in LUKHAS AI...")
    analyzer = ModuleUsageAnalyzer(repo_root)
    report = analyzer.generate_report()

    # Print summary
    print("\n📊 USAGE SUMMARY")
    print("=" * 60)
    print(f"Total Python files: {report['summary']['total_python_files']}")
    print(f"Imported files: {report['summary']['imported_files']}")
    print(f"Orphaned files: {report['summary']['orphaned_files']}")
    print(f"Overall usage: {report['summary']['usage_percentage']:.1f}%")

    # Print module statistics
    print("\n📦 MODULE STATISTICS")
    print("=" * 60)
    print(f"{'Module':<20} {'Total':<8} {'Used':<8} {'Orphaned':<10} {'Usage %':<10}")
    print("-" * 60)

    for module, stats in sorted(report["module_statistics"].items()):
        if stats["total_files"] > 0:
            print(
                f"{module:<20} {stats['total_files']:<8} {stats['imported_files']:<8} "
                f"{stats['orphaned_files']:<10} {stats['usage_percentage']:<10.1f}"
            )

    # Print top orphaned files
    print("\n🚫 TOP ORPHANED FILES (Never imported or unreachable)")
    print("=" * 60)
    for i, file in enumerate(report["top_orphaned_files"][:20], 1):
        print(f"{i:3}. {file}")

    # Print most imported files
    print("\n⭐ MOST IMPORTED FILES")
    print("=" * 60)
    for i, (file, count) in enumerate(report["most_imported"][:10], 1):
        print(f"{i:3}. {file:<50} ({count} imports)")

    # Save full report to JSON
    report_path = repo_root / "module_usage_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Full report saved to: {report_path}")

    # Return exit code based on orphaned files
    if report["summary"]["orphaned_files"] > 100:
        print(f"\n⚠️  Warning: {report['summary']['orphaned_files']} orphaned files found!")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
