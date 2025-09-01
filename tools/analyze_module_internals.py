#!/usr/bin/env python3
"""
Analyze internal connections within each module
Find internal orphans - files not connected within their own module
Trinity Framework: ⚛️🧠🛡️
"""

import ast
import json
import os
from pathlib import Path


class ModuleInternalAnalyzer:
    def __init__(self):
        self.modules_to_check = [
            "memory",
            "consciousness",
            "dream",
            "qim",
            "governance",
            "identity",
            "bio",
            "quantum",
            "emotion",
            "vivox",
        ]
        self.results = {}

    def analyze_module(self, module_name: str) -> dict:
        """Analyze internal connections for a single module"""
        print(f"\n🔍 Analyzing {module_name} module...")

        module_path = Path(module_name)
        if not module_path.exists():
            return {"error": f"Module {module_name} not found"}

        # Find all Python files in module
        all_files = set()
        for root, dirs, files in os.walk(module_path):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), module_path)
                    all_files.add(rel_path)

        # Find entry points
        entry_points = self.find_entry_points(module_path)

        # Trace connections from entry points
        connected_files = self.trace_connections(module_path, entry_points)

        # Find orphans
        orphaned_files = all_files - connected_files

        # Analyze orphan value
        high_value_orphans = []
        for orphan in orphaned_files:
            file_path = module_path / orphan
            if self.is_high_value(file_path):
                size = os.path.getsize(file_path)
                high_value_orphans.append({"file": orphan, "size": size, "lines": self.count_lines(file_path)})

        # Sort by size
        high_value_orphans.sort(key=lambda x: x["size"], reverse=True)

        return {
            "total_files": len(all_files),
            "connected_files": len(connected_files),
            "orphaned_files": len(orphaned_files),
            "connection_rate": f"{len(connected_files) / len(all_files) * 100:.1f}%",
            "entry_points": list(entry_points),
            "high_value_orphans": high_value_orphans[:10],  # Top 10
            "sample_orphans": list(orphaned_files)[:20],
        }

    def find_entry_points(self, module_path: Path) -> set[str]:
        """Find module entry points"""
        entry_points = set()

        # Standard entry points
        standard_entries = [
            "__init__.py",
            "main.py",
            "core.py",
            f"{module_path.name}.py",  # e.g., memory/memory.py
            "api.py",
            "service.py",
        ]

        for entry in standard_entries:
            if (module_path / entry).exists():
                entry_points.add(entry)

        # For consciousness, add dream.py
        if module_path.name == "consciousness":
            if (module_path / "dream" / "dream.py").exists():
                entry_points.add("dream/dream.py")

        return entry_points if entry_points else {"__init__.py"}

    def trace_connections(self, module_path: Path, entry_points: set[str]) -> set[str]:
        """Trace which files are connected from entry points"""
        connected = set(entry_points)
        to_check = list(entry_points)
        checked = set()

        while to_check:
            current = to_check.pop(0)
            if current in checked:
                continue
            checked.add(current)

            file_path = module_path / current
            if not file_path.exists():
                continue

            # Find imports in this file
            imports = self.find_imports(file_path, module_path.name)

            for imp in imports:
                # Convert import to file path
                if imp.startswith("."):
                    # Relative import
                    imp = imp[1:]  # Remove leading dot

                # Convert module path to file path
                possible_files = [
                    imp.replace(".", "/") + ".py",
                    imp.replace(".", "/") + "/__init__.py",
                ]

                for pf in possible_files:
                    if pf not in connected and (module_path / pf).exists():
                        connected.add(pf)
                        to_check.append(pf)

        return connected

    def find_imports(self, file_path: Path, module_name: str) -> list[str]:
        """Find all internal imports in a file"""
        imports = []
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(module_name):
                            imports.append(alias.name[len(module_name) + 1 :])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith(module_name):
                        imports.append(node.module[len(module_name) + 1 :])
                    elif node.level > 0:  # Relative import
                        imports.append("." + (node.module or ""))
        except:
            pass
        return imports

    def is_high_value(self, file_path: Path) -> bool:
        """Check if a file is likely high value"""
        name = file_path.name.lower()

        # High value indicators
        high_value_words = [
            "core",
            "engine",
            "manager",
            "system",
            "processor",
            "orchestrator",
            "controller",
            "service",
            "api",
            "model",
            "algorithm",
            "network",
            "quantum",
            "consciousness",
        ]

        # Check file size
        try:
            size = os.path.getsize(file_path)
            if size > 5000:  # Over 5KB
                return True
        except:
            pass

        # Check name
        return any(word in name for word in high_value_words)

    def count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path) as f:
                return len(f.readlines())
        except:
            return 0

    def analyze_all(self):
        """Analyze all modules"""
        print("=" * 60)
        print("   MODULE INTERNAL CONNECTION ANALYSIS")
        print("   Trinity Framework: ⚛️🧠🛡️")
        print("=" * 60)

        for module in self.modules_to_check:
            self.results[module] = self.analyze_module(module)

        self.print_summary()
        self.save_report()

    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        for module, data in self.results.items():
            if "error" in data:
                print(f"\n❌ {module}: {data['error']}")
                continue

            print(f"\n📦 {module.upper()}")
            print(f"  Total files: {data['total_files']}")
            print(f"  Connected: {data['connected_files']} ({data['connection_rate']})")
            print(f"  Orphaned: {data['orphaned_files']}")

            if data["high_value_orphans"]:
                print("  High-value orphans:")
                for orphan in data["high_value_orphans"][:3]:
                    print(f"    - {orphan['file']} ({orphan['lines']} lines)")

    def save_report(self):
        """Save detailed report"""
        with open("module_internal_analysis.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\n💾 Detailed report saved to: module_internal_analysis.json")


if __name__ == "__main__":
    analyzer = ModuleInternalAnalyzer()
    analyzer.analyze_all()
