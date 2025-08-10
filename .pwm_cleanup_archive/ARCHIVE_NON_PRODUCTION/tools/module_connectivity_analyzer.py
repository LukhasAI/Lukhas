#!/usr/bin/env python3
"""
Module Connectivity Analyzer
Analyzes the codebase to find isolated modules and generate connectivity data
"""

import ast
import json
import os
from collections import defaultdict
from typing import Dict


class ModuleConnectivityAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.modules = {}  # module_path -> module_info
        self.connections = defaultdict(set)  # module -> set of connected modules
        self.isolated_modules = set()

    def analyze(self):
        """Analyze all Python modules in the codebase"""
        print("Analyzing module connectivity...")

        # Find all Python files
        for root, dirs, files in os.walk(self.root_path):
            # Skip common non-source directories
            dirs[:] = [
                d
                for d in dirs
                if d not in ["__pycache__", ".git", "venv", "env", ".env"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_path)

                    # Skip test files and setup files
                    if "test" in relative_path or "setup.py" in file:
                        continue

                    self.analyze_module(file_path, relative_path)

        # Find isolated modules
        self.find_isolated_modules()

        return self.generate_report()

    def analyze_module(self, file_path: str, relative_path: str):
        """Analyze a single Python module"""
        module_name = relative_path.replace(".py", "").replace("/", ".")

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            imports = []
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            # Store module info
            self.modules[module_name] = {
                "path": relative_path,
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "size": len(content),
                "lines": content.count("\n"),
            }

            # Build connections based on imports
            for imp in imports:
                # Check if import is internal (part of our codebase)
                if any(
                    imp.startswith(prefix)
                    for prefix in ["core", "consciousness", "colony", "quantum", "bio"]
                ):
                    self.connections[module_name].add(imp)
                    self.connections[imp].add(module_name)  # Bidirectional

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def find_isolated_modules(self):
        """Find modules with no connections"""
        for module in self.modules:
            if module not in self.connections or len(self.connections[module]) == 0:
                self.isolated_modules.add(module)

    def generate_report(self) -> Dict:
        """Generate connectivity report"""
        # Calculate statistics
        total_modules = len(self.modules)
        connected_modules = len(
            [
                m
                for m in self.modules
                if m in self.connections and len(self.connections[m]) > 0
            ]
        )
        isolated_count = len(self.isolated_modules)

        # Find most connected modules (hubs)
        module_connections = [(m, len(conns)) for m, conns in self.connections.items()]
        module_connections.sort(key=lambda x: x[1], reverse=True)
        top_hubs = module_connections[:10]

        # Group isolated modules by directory
        isolated_by_dir = defaultdict(list)
        for module in self.isolated_modules:
            if module in self.modules:
                path = self.modules[module]["path"]
                dir_path = os.path.dirname(path)
                isolated_by_dir[dir_path].append(module)

        # Build visualization data
        nodes = []
        edges = []

        # Add all modules as nodes
        for module, info in self.modules.items():
            node = {
                "id": module,
                "label": module.split(".")[-1],  # Just the last part for readability
                "group": module.split(".")[0] if "." in module else "root",
                "size": min(info["lines"] / 10, 50),  # Node size based on lines of code
                "isolated": module in self.isolated_modules,
            }
            nodes.append(node)

        # Add connections as edges
        seen_edges = set()
        for module, connections in self.connections.items():
            for connected in connections:
                edge_key = tuple(sorted([module, connected]))
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({"source": module, "target": connected, "value": 1})

        report = {
            "summary": {
                "total_modules": total_modules,
                "connected_modules": connected_modules,
                "isolated_modules": isolated_count,
                "connectivity_rate": (
                    (connected_modules / total_modules * 100)
                    if total_modules > 0
                    else 0
                ),
                "total_connections": len(seen_edges),
            },
            "isolated_modules": {
                "count": isolated_count,
                "by_directory": dict(isolated_by_dir),
                "list": sorted(list(self.isolated_modules)),
            },
            "top_hubs": [{"module": m, "connections": c} for m, c in top_hubs],
            "visualization": {"nodes": nodes, "edges": edges},
        }

        return report


def main():
    # Analyze the codebase
    analyzer = ModuleConnectivityAnalyzer("/Users/agi_dev/Downloads/Consolidation-Repo")
    report = analyzer.analyze()

    # Save report
    with open("module_connectivity_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("MODULE CONNECTIVITY ANALYSIS")
    print("=" * 60)
    print(f"Total Modules: {report['summary']['total_modules']}")
    print(f"Connected Modules: {report['summary']['connected_modules']}")
    print(f"Isolated Modules: {report['summary']['isolated_modules']}")
    print(f"Connectivity Rate: {report['summary']['connectivity_rate']:.1f}%")
    print(f"Total Connections: {report['summary']['total_connections']}")

    print("\nTop 10 Most Connected Modules (Hubs):")
    for hub in report["top_hubs"]:
        print(f"  - {hub['module']}: {hub['connections']} connections")

    print("\nIsolated Modules by Directory:")
    for dir_path, modules in report["isolated_modules"]["by_directory"].items():
        print(f"\n  {dir_path or 'root'}/ ({len(modules)} modules):")
        for module in modules[:5]:  # Show first 5
            print(f"    - {module}")
        if len(modules) > 5:
            print(f"    ... and {len(modules) - 5} more")

    print("\nReport saved to: module_connectivity_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
