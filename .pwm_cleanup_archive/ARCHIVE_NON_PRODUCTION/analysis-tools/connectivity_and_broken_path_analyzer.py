#!/usr/bin/env python3
"""
Connectivity and Broken Path Analyzer
Analyzes the codebase for connectivity between modules and identifies broken import paths.
"""

import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


class ConnectivityAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.module_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.broken_imports: List[Dict[str, str]] = []
        self.file_to_module: Dict[str, str] = {}
        self.module_to_file: Dict[str, str] = {}
        self.total_files = 0
        self.python_files = 0
        self.connected_files = set()
        self.isolated_files = set()

    def analyze(self):
        """Run complete connectivity analysis"""
        print("🔍 Starting Connectivity and Broken Path Analysis...")

        # 1. Discover all Python files
        self._discover_python_files()

        # 2. Analyze imports and build graph
        self._analyze_imports()

        # 3. Find connected components
        self._find_connected_components()

        # 4. Identify broken imports
        self._identify_broken_imports()

        # 5. Generate report
        return self._generate_report()

    def _discover_python_files(self):
        """Discover all Python files in the codebase"""
        print("\n📁 Discovering Python files...")

        for path in self.root_path.rglob("*.py"):
            if any(part.startswith(".") for part in path.parts):
                continue  # Skip hidden directories
            if "venv" in path.parts or "__pycache__" in path.parts:
                continue  # Skip virtual environments and cache

            self.total_files += 1
            self.python_files += 1

            # Convert file path to module name
            relative_path = path.relative_to(self.root_path)
            module_name = str(relative_path).replace("/", ".").replace("\\", ".")[:-3]

            self.file_to_module[str(path)] = module_name
            self.module_to_file[module_name] = str(path)

        print(f"  Found {self.python_files} Python files")

    def _analyze_imports(self):
        """Analyze imports in all Python files"""
        print("\n🔗 Analyzing imports...")

        for filepath, module_name in self.file_to_module.items():
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST
                try:
                    tree = ast.parse(content)
                    imports = self._extract_imports(tree, module_name)

                    for imported_module in imports:
                        self.module_graph[module_name].add(imported_module)
                        self.reverse_graph[imported_module].add(module_name)

                except SyntaxError as e:
                    # Track files with syntax errors
                    self.broken_imports.append(
                        {
                            "file": filepath,
                            "module": module_name,
                            "error": f"Syntax error: {str(e)}",
                            "type": "syntax_error",
                        }
                    )

            except Exception as e:
                self.broken_imports.append(
                    {
                        "file": filepath,
                        "module": module_name,
                        "error": f"Read error: {str(e)}",
                        "type": "read_error",
                    }
                )

    def _extract_imports(self, tree: ast.AST, current_module: str) -> Set[str]:
        """Extract all imports from an AST"""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Handle relative imports
                    if node.level > 0:
                        # Relative import
                        base_parts = current_module.split(".")
                        if node.level <= len(base_parts):
                            base = ".".join(base_parts[: -node.level])
                            if base and node.module:
                                full_module = f"{base}.{node.module}"
                            elif base:
                                full_module = base
                            else:
                                full_module = node.module
                        else:
                            full_module = node.module
                    else:
                        full_module = node.module

                    imports.add(full_module)

                    # Also track specific imports
                    for alias in node.names:
                        if alias.name != "*":
                            imports.add(f"{full_module}.{alias.name}")

        return imports

    def _find_connected_components(self):
        """Find connected components in the module graph"""
        print("\n🌐 Finding connected components...")

        visited = set()
        components = []

        for module in self.file_to_module.values():
            if module not in visited:
                component = set()
                self._dfs(module, visited, component)
                components.append(component)

        # Find the largest component (main connected codebase)
        if components:
            main_component = max(components, key=len)
            self.connected_files = {
                self.module_to_file[m]
                for m in main_component
                if m in self.module_to_file
            }

            # All other files are isolated
            all_files = set(self.file_to_module.keys())
            self.isolated_files = all_files - self.connected_files

        print(f"  Found {len(components)} connected components")
        if components:
            print(f"  Main component has {len(max(components, key=len))} modules")

    def _dfs(self, module: str, visited: Set[str], component: Set[str]):
        """Depth-first search to find connected component"""
        visited.add(module)
        component.add(module)

        # Check both directions (imports and imported by)
        for neighbor in self.module_graph.get(module, set()):
            if neighbor not in visited and neighbor in self.file_to_module.values():
                self._dfs(neighbor, visited, component)

        for neighbor in self.reverse_graph.get(module, set()):
            if neighbor not in visited:
                self._dfs(neighbor, visited, component)

    def _identify_broken_imports(self):
        """Identify broken import paths"""
        print("\n❌ Identifying broken imports...")

        for module, imports in self.module_graph.items():
            for imported in imports:
                # Check if it's an internal import
                if not any(
                    imported.startswith(prefix)
                    for prefix in [
                        "sys",
                        "os",
                        "typing",
                        "collections",
                        "json",
                        "asyncio",
                        "logging",
                        "datetime",
                        "enum",
                        "pathlib",
                        "math",
                        "time",
                        "re",
                        "unittest",
                        "numpy",
                        "torch",
                        "transformers",
                    ]
                ):
                    # Check if the imported module exists
                    base_module = imported.split(".")[0]

                    # Check if it's a file in our codebase
                    possible_file = self.root_path / imported.replace(".", "/").replace(
                        ".py", ""
                    )
                    possible_file_py = possible_file.with_suffix(".py")
                    possible_init = possible_file / "__init__.py"

                    if not (possible_file_py.exists() or possible_init.exists()):
                        # Check if it's a module that should exist
                        if base_module in [
                            "bio",
                            "consciousness",
                            "core",
                            "ethics",
                            "identity",
                            "memory",
                            "quantum",
                            "orchestration",
                            "learning",
                            "engines",
                        ]:
                            self.broken_imports.append(
                                {
                                    "file": self.module_to_file.get(module, "unknown"),
                                    "module": module,
                                    "broken_import": imported,
                                    "error": f"Module not found: {imported}",
                                    "type": "missing_module",
                                }
                            )

    def _generate_report(self) -> Dict:
        """Generate comprehensive connectivity report"""
        print("\n📊 Generating report...")

        connectivity_percentage = (
            (len(self.connected_files) / self.python_files * 100)
            if self.python_files > 0
            else 0
        )

        # Categorize isolated files
        isolated_by_type = defaultdict(list)
        for file in self.isolated_files:
            if "__init__.py" in file:
                isolated_by_type["init_files"].append(file)
            elif "test" in file.lower():
                isolated_by_type["test_files"].append(file)
            elif any(
                file.endswith(f"/{d}") or f"/{d}/" in file
                for d in ["docs", "examples", "scripts"]
            ):
                isolated_by_type["utility_files"].append(file)
            else:
                isolated_by_type["implementation_files"].append(file)

        # Find highly connected modules (hubs)
        connection_counts = {
            module: len(
                self.module_graph.get(module, set())
                | self.reverse_graph.get(module, set())
            )
            for module in self.file_to_module.values()
        }
        top_hubs = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        report = {
            "summary": {
                "total_files": self.total_files,
                "python_files": self.python_files,
                "connected_files": len(self.connected_files),
                "isolated_files": len(self.isolated_files),
                "connectivity_percentage": round(connectivity_percentage, 2),
                "broken_imports_count": len(self.broken_imports),
            },
            "isolated_files_breakdown": {
                "init_files": len(isolated_by_type["init_files"]),
                "test_files": len(isolated_by_type["test_files"]),
                "utility_files": len(isolated_by_type["utility_files"]),
                "implementation_files": len(isolated_by_type["implementation_files"]),
            },
            "critical_isolated_files": isolated_by_type["implementation_files"][
                :20
            ],  # Top 20
            "broken_imports": self.broken_imports[:50],  # Top 50 broken imports
            "top_connected_modules": [
                {"module": m, "connections": c} for m, c in top_hubs
            ],
            "integration_points": self._find_integration_points(),
        }

        return report

    def _find_integration_points(self) -> List[Dict]:
        """Find key integration points in the codebase"""
        integration_points = []

        # Check key integration files
        key_files = [
            "orchestration/integration_hub.py",
            "core/core_hub.py",
            "quantum/quantum_hub.py",
            "consciousness/consciousness_hub.py",
            "memory/memory_hub.py",
            "identity/identity_hub.py",
        ]

        for file in key_files:
            full_path = self.root_path / file
            if full_path.exists():
                module = self.file_to_module.get(str(full_path), "")
                connections = len(
                    self.module_graph.get(module, set())
                    | self.reverse_graph.get(module, set())
                )
                integration_points.append(
                    {
                        "file": file,
                        "exists": True,
                        "connections": connections,
                        "imports_from": list(self.module_graph.get(module, set()))[:10],
                        "imported_by": list(self.reverse_graph.get(module, set()))[:10],
                    }
                )
            else:
                integration_points.append(
                    {"file": file, "exists": False, "connections": 0}
                )

        return integration_points


def main():
    """Run the connectivity analysis"""
    analyzer = ConnectivityAnalyzer()
    report = analyzer.analyze()

    # Save detailed report
    with open("connectivity_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("CONNECTIVITY AND BROKEN PATH REPORT")
    print("=" * 60)

    summary = report["summary"]
    print("\n📊 Summary:")
    print(f"  Total Python files: {summary['python_files']}")
    print(
        f"  Connected files: {summary['connected_files']} ({summary['connectivity_percentage']}%)"
    )
    print(f"  Isolated files: {summary['isolated_files']}")
    print(f"  Broken imports: {summary['broken_imports_count']}")

    breakdown = report["isolated_files_breakdown"]
    print("\n📁 Isolated Files Breakdown:")
    print(f"  __init__.py files: {breakdown['init_files']}")
    print(f"  Test files: {breakdown['test_files']}")
    print(f"  Utility files: {breakdown['utility_files']}")
    print(f"  Implementation files: {breakdown['implementation_files']} ⚠️")

    if report["critical_isolated_files"]:
        print("\n⚠️  Critical Isolated Implementation Files (top 10):")
        for file in report["critical_isolated_files"][:10]:
            print(f"    - {file}")

    if report["broken_imports"]:
        print("\n❌ Broken Imports (top 10):")
        for imp in report["broken_imports"][:10]:
            if "broken_import" in imp:
                print(f"    - {imp['module']} → {imp['broken_import']}")
            else:
                print(f"    - {imp['module']} ({imp.get('type', 'unknown')})")
            print(f"      Error: {imp['error']}")

    print("\n🔗 Top Connected Modules (Hubs):")
    for hub in report["top_connected_modules"][:5]:
        print(f"    - {hub['module']}: {hub['connections']} connections")

    print("\n🎯 Integration Points Status:")
    for point in report["integration_points"]:
        status = "✅" if point["exists"] else "❌"
        print(f"    {status} {point['file']} - {point['connections']} connections")

    print("\n💾 Full report saved to: connectivity_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
