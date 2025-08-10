#!/usr/bin/env python3
"""
PWM Workspace Status Analysis
============================
Comprehensive analysis of current workspace connectivity, working systems,
    and isolated files.
"""

import ast
import json
from collections import defaultdict
from pathlib import Path


class PWMWorkspaceAnalyzer:

    def __init__(self, root_path="."):
        self.root_path = Path(root_path)
        self.modules = {}
        self.imports = defaultdict(set)
        self.exports = defaultdict(set)
        self.isolated_files = []
        self.working_systems = []
        self.broken_systems = []
        self.connectivity_map = {}

    def analyze_file(self, file_path):
        """Analyze a single Python file for imports, exports, and functionality."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            file_info = {
                "path": str(file_path),
                "imports": [],
                "functions": [],
                "classes": [],
                "has_main": False,
                "is_executable": False,
                "dependencies": set(),
                "size": len(content),
                "lines": len(content.split("\n")),
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_info["imports"].append(alias.name)
                        file_info["dependencies"].add(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_info["imports"].append(f"from {node.module}")
                        file_info["dependencies"].add(node.module.split(".")[0])

                elif isinstance(node, ast.FunctionDef):
                    file_info["functions"].append(node.name)
                    if node.name == "main":
                        file_info["has_main"] = True

                elif isinstance(node, ast.ClassDef):
                    file_info["classes"].append(node.name)

            # Check if it's executable
            if '__name__ == "__main__"' in content or file_info["has_main"]:
                file_info["is_executable"] = True

            return file_info

        except Exception as e:
            return {"path": str(file_path), "error": str(e), "size": 0, "lines": 0}

    def scan_workspace(self):
        """Scan entire workspace for Python files."""
        print("🔍 Scanning PWM workspace...")

        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)

        print(f"📊 Found {total_files} Python files")

        for i, file_path in enumerate(python_files):
            if i % 50 == 0:
                print(f"   Processing: {i}/{total_files} files...")

            rel_path = file_path.relative_to(self.root_path)

            # Skip archive and hidden directories
            if ".pwm_cleanup_archive" in str(rel_path) or str(rel_path).startswith("."):
                continue

            file_info = self.analyze_file(file_path)
            self.modules[str(rel_path)] = file_info

        print(f"✅ Analyzed {len(self.modules)} active Python files")

    def analyze_connectivity(self):
        """Analyze how modules are connected to each other."""
        print("🔗 Analyzing module connectivity...")

        # Build dependency graph
        for file_path, info in self.modules.items():
            if "dependencies" in info:
                for dep in info["dependencies"]:
                    # Check if dependency exists in our workspace
                    matching_files = [f for f in self.modules if dep in f]
                    if matching_files:
                        self.imports[file_path].update(matching_files)
                        for match in matching_files:
                            self.exports[match].add(file_path)

        # Identify isolated files (no imports or exports within workspace)
        for file_path, info in self.modules.items():
            internal_imports = len(self.imports[file_path])
            internal_exports = len(self.exports[file_path])

            if internal_imports == 0 and internal_exports == 0:
                self.isolated_files.append(
                    {
                        "path": file_path,
                        "size": info.get("size", 0),
                        "lines": info.get("lines", 0),
                        "functions": len(info.get("functions", [])),
                        "classes": len(info.get("classes", [])),
                        "is_executable": info.get("is_executable", False),
                    }
                )

    def identify_working_systems(self):
        """Identify which root-level systems are working vs broken."""
        print("⚙️ Identifying working vs broken systems...")

        root_dirs = [
            d
            for d in self.root_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        for root_dir in root_dirs:
            system_info = {
                "name": root_dir.name,
                "path": str(root_dir),
                "file_count": 0,
                "connected_files": 0,
                "isolated_files": 0,
                "has_init": False,
                "has_main": False,
                "executable_files": 0,
                "status": "unknown",
            }

            # Count files in this system
            py_files = list(root_dir.rglob("*.py"))
            system_info["file_count"] = len(py_files)

            # Check for __init__.py
            if (root_dir / "__init__.py").exists():
                system_info["has_init"] = True

            # Analyze connectivity within this system
            for py_file in py_files:
                rel_path = str(py_file.relative_to(self.root_path))
                if rel_path in self.modules:
                    file_info = self.modules[rel_path]

                    if file_info.get("has_main") or file_info.get("is_executable"):
                        system_info["executable_files"] += 1
                        system_info["has_main"] = True

                    # Check if this file is connected to other files
                    if rel_path in self.imports or rel_path in self.exports:
                        system_info["connected_files"] += 1
                    else:
                        system_info["isolated_files"] += 1

            # Determine system status
            if system_info["file_count"] == 0:
                system_info["status"] = "empty"
            elif system_info["connected_files"] > system_info["isolated_files"]:
                system_info["status"] = "working"
                self.working_systems.append(system_info)
            elif system_info["has_init"] and system_info["file_count"] > 3:
                system_info["status"] = "structured"
                self.working_systems.append(system_info)
            else:
                system_info["status"] = "isolated"
                self.broken_systems.append(system_info)

    def generate_report(self):
        """Generate comprehensive status report."""
        report = {
            "timestamp": "2025-08-01T05:50:00Z",
            "workspace_overview": {
                "total_python_files": len(self.modules),
                "total_root_systems": len(
                    [
                        d
                        for d in self.root_path.iterdir()
                        if d.is_dir() and not d.name.startswith(".")
                    ]
                ),
                "working_systems": len(self.working_systems),
                "broken_systems": len(self.broken_systems),
                "isolated_files": len(self.isolated_files),
            },
            "working_systems": self.working_systems,
            "broken_systems": self.broken_systems,
            "isolated_files": sorted(
                self.isolated_files, key=lambda x: x["size"], reverse=True
            ),
            "connectivity_stats": {
                "files_with_imports": len([f for f in self.modules if self.imports[f]]),
                "files_with_exports": len([f for f in self.modules if self.exports[f]]),
                "highly_connected": len(
                    [
                        f
                        for f in self.modules
                        if len(self.imports[f]) + len(self.exports[f]) > 5
                    ]
                ),
            },
        }

        return report

    def save_report(self, filename="PWM_WORKSPACE_STATUS_REPORT.json"):
        """Save detailed report to file."""
        report = self.generate_report()

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📋 Report saved to {filename}")
        return report

    def print_summary(self):
        """Print executive summary of workspace status."""
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("🎯 PWM WORKSPACE STATUS ANALYSIS")
        print("=" * 60)

        overview = report["workspace_overview"]
        print("\n📊 OVERVIEW:")
        print(f"   • Total Python Files: {overview['total_python_files']}")
        print(f"   • Root Systems: {overview['total_root_systems']}")
        print(f"   • Working Systems: {overview['working_systems']} ✅")
        print(f"   • Broken/Isolated Systems: {overview['broken_systems']} ❌")
        print(f"   • Isolated Files: {overview['isolated_files']} 🔍")

        print(f"\n✅ WORKING SYSTEMS ({len(self.working_systems)}):")
        for system in self.working_systems[:10]:  # Top 10
            print(
                f"   • {system['name']}: {system['file_count']} files, {system['connected_files']} connected"
            )

        print(f"\n❌ BROKEN/ISOLATED SYSTEMS ({len(self.broken_systems)}):")
        for system in self.broken_systems[:10]:  # Top 10
            print(
                f"   • {system['name']}: {system['file_count']} files, {system['isolated_files']} isolated"
            )

        print("\n🔍 TOP ISOLATED FILES (Size-based):")
        for file_info in self.isolated_files[:15]:  # Top 15
            size_kb = file_info["size"] / 1024
            print(
                f"   • {file_info['path']} ({size_kb:.1f}KB, {file_info['lines']} lines)"
            )

        print("\n🎯 CRITICAL FILES TO KEEP (Based on size & functionality):")
        critical_files = [
            f
            for f in self.isolated_files
            if f["size"] > 1000
            or f["is_executable"]
            or f["functions"] > 3
            or f["classes"] > 1
        ]
        for file_info in critical_files[:20]:  # Top 20
            features = []
            if file_info["is_executable"]:
                features.append("executable")
            if file_info["functions"] > 5:
                features.append(f"{file_info['functions']} functions")
            if file_info["classes"] > 1:
                features.append(f"{file_info['classes']} classes")

            size_kb = file_info["size"] / 1024
            feature_str = ", ".join(features) if features else "basic"
            print(f"   • {file_info['path']} ({size_kb:.1f}KB, {feature_str})")


if __name__ == "__main__":
    analyzer = PWMWorkspaceAnalyzer()
    analyzer.scan_workspace()
    analyzer.analyze_connectivity()
    analyzer.identify_working_systems()
    analyzer.print_summary()
    analyzer.save_report()
