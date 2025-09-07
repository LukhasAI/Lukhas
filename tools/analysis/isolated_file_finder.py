#!/usr/bin/env python3
"""
Isolated File Finder - Identifies disconnected components in LUKHAS
"""
import time
import streamlit as st

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path


class IsolatedFileFinder:
    def __init__(self):
        self.import_graph = defaultdict(set)  # file -> imported files
        self.reverse_graph = defaultdict(set)  # file -> files that import it
        self.all_python_files = set()
        self.isolated_files = []
        self.weakly_connected = []

    def scan_directory(self, root_path="."):
        """Scan all Python files and build import graph"""
        print("🔍 Scanning for Python files...")

        for root, _dirs, files in os.walk(root_path):
            # Skip certain directories
            if any(skip in root for skip in [".git", "__pycache__", ".venv", "node_modules"]):
                continue

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    self.all_python_files.add(filepath)
                    self._analyze_imports(filepath)

        print(f"Found {len(self.all_python_files} Python files")

    def _analyze_imports(self, filepath):
        """Analyze imports in a Python file"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content)
            except BaseException:
                return  # Skip files with syntax errors

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.import_graph[filepath].add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.import_graph[filepath].add(node.module)

            # Also check for dynamic imports
            dynamic_imports = re.findall(r'__import__\([\'"]([^\'"]*)[\'"]\)', content)
            for imp in dynamic_imports:
                self.import_graph[filepath].add(imp)

        except Exception:
            pass  # Skip problematic files

    def build_reverse_graph(self):
        """Build reverse import graph"""
        for file, imports in self.import_graph.items():
            for imp in imports:
                # Convert module to potential file paths
                potential_files = [
                    f"./{imp.replace('.', '/'}.py",
                    f"./{imp.replace('.', '/'}/__init__.py",
                ]

                for pf in potential_files:
                    if pf in self.all_python_files:
                        self.reverse_graph[pf].add(file)

    def find_isolated_files(self):
        """Find files that are not imported by anyone and don't import anything"""
        self.build_reverse_graph()

        for file in self.all_python_files:
            # Skip test files and scripts
            if "test" in file or "script" in file or "__pycache__" in file:
                continue

            imports_nothing = file not in self.import_graph or len(self.import_graph[file]) == 0
            imported_by_none = file not in self.reverse_graph or len(self.reverse_graph[file]) == 0

            if imports_nothing and imported_by_none:
                self.isolated_files.append(file)
            elif imported_by_none and not imports_nothing:
                # Files that import others but aren't imported
                self.weakly_connected.append(file)

    def categorize_isolated_files(self):
        """Categorize isolated files by type and location"""
        categories = defaultdict(list)

        for file in self.isolated_files:
            # Determine category
            if "/tools/" in file:
                categories["tools"].append(file)
            elif "/docs/" in file:
                categories["documentation"].append(file)
            elif "/examples/" in file or "/demo/" in file:
                categories["examples"].append(file)
            elif file.startswith("./") and "/" not in file[2:]:
                categories["root_level"].append(file)
            else:
                # Determine by module
                parts = file.split("/")
                if len(parts) > 1:
                    module = parts[1]
                    categories[f"module_{module}"].append(file)
                else:
                    categories["uncategorized"].append(file)

        return categories

    def generate_consolidation_plan(self):
        """Generate a plan for consolidating isolated files"""
        categories = self.categorize_isolated_files()
        plan = {
            "total_isolated": len(self.isolated_files),
            "total_weakly_connected": len(self.weakly_connected),
            "categories": categories,
            "recommendations": [],
        }

        # Generate recommendations
        if categories["root_level"]:
            plan["recommendations"].append(
                {
                    "action": "move_root_files",
                    "description": f"Move {len(categories['root_level']} root-level files to appropriate modules",
                    "files": categories["root_level"],
                }
            )

        if categories["tools"]:
            plan["recommendations"].append(
                {
                    "action": "consolidate_tools",
                    "description": f"Consolidate {len(categories['tools']} tool files into organized scripts",
                    "files": categories["tools"],
                }
            )

        # Check for duplicate functionality
        plan["recommendations"].append(
            {
                "action": "check_duplicates",
                "description": "Review isolated files for duplicate functionality",
                "files": self.isolated_files[:10],  # First 10 as examples
            }
        )

        return plan

    def save_report(self):
        """Save analysis report"""
        report = {
            "scan_timestamp": str(Path().absolute()),
            "total_files": len(self.all_python_files),
            "isolated_files": self.isolated_files,
            "weakly_connected": self.weakly_connected,
            "consolidation_plan": self.generate_consolidation_plan(),
        }

        with open("isolated_files_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report


def main():
    print("🔍 LUKHAS Isolated File Finder")
    print("=" * 50)

    finder = IsolatedFileFinder()
    finder.scan_directory()
    finder.find_isolated_files()

    print("\n📊 Analysis Results:")
    print(f"  - Isolated files: {len(finder.isolated_files}")
    print(f"  - Weakly connected: {len(finder.weakly_connected}")

    categories = finder.categorize_isolated_files()
    print("\n📁 Isolated Files by Category:")
    for cat, files in categories.items():
        print(f"  - {cat}: {len(files} files")

    # Show some examples
    if finder.isolated_files:
        print("\n🔗 Example Isolated Files (first 10):")
        for file in finder.isolated_files[:10]:
            print(f"  - {file}")

    # Save report
    finder.save_report()
    print("\n💾 Report saved to: isolated_files_report.json")

    # Generate consolidation recommendations
    plan = finder.generate_consolidation_plan()
    print("\n🎯 Consolidation Recommendations:")
    for rec in plan["recommendations"]:
        print(f"  - {rec['description']}")


if __name__ == "__main__":
    main()
