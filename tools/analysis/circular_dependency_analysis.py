#!/usr/bin/env python3
"""
🔄  Circular Dependency Analysis
==================================
Identifies and analyzes circular dependencies in LUKHAS .
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import networkx as nx

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DependencyAnalyzer:
    """Analyzes module dependencies and finds circular imports"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.import_graph = nx.DiGraph()
        self.module_imports: dict[str, set[str]] = defaultdict(set)
        self.circular_dependencies: list[list[str]] = []
        self.analyzed_files = 0

    def analyze_file(self, file_path: Path) -> None:
        """Analyze imports in a single Python file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            module_name = self._path_to_module(file_path)

            # Add module to graph
            self.import_graph.add_node(module_name)

            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_module = alias.name
                        if self._is_local_module(imported_module):
                            self.module_imports[module_name].add(imported_module)
                            self.import_graph.add_edge(module_name, imported_module)

                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:  # Absolute import
                        imported_module = node.module
                        if self._is_local_module(imported_module):
                            self.module_imports[module_name].add(imported_module)
                            self.import_graph.add_edge(module_name, imported_module)
                    elif node.level > 0:  # Relative import
                        imported_module = self._resolve_relative_import(file_path, node.module, node.level)
                        if imported_module and self._is_local_module(imported_module):
                            self.module_imports[module_name].add(imported_module)
                            self.import_graph.add_edge(module_name, imported_module)

            self.analyzed_files += 1

        except Exception:
            # Skip files with syntax errors
            pass

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        try:
            rel_path = file_path.relative_to(self.root_path)
            parts = [*list(rel_path.parts[:-1]), rel_path.stem]
            # Remove __init__ from module name
            if parts[-1] == "__init__":
                parts = parts[:-1]
            return ".".join(parts)
        except ValueError:
            return str(file_path)

    def _is_local_module(self, module_name: str) -> bool:
        """Check if module is part of LUKHAS"""
        if not module_name:
            return False

        top_level = module_name.split(".")[0]
        local_modules = {
            "api",
            "architectures",
            "bio",
            "bridge",
            "consciousness",
            "core",
            "creativity",
            "emotion",
            "ethics",
            "governance",
            "identity",
            "memory",
            "orchestration",
            "quantum",
            "reasoning",
            "recovery",
            "security",
            "tests",
            "tools",
            "unified",
            "vivox",
        }

        return top_level in local_modules

    def _resolve_relative_import(self, file_path: Path, module: Optional[str], level: int) -> Optional[str]:
        """Resolve relative import to absolute module name"""
        current_module = self._path_to_module(file_path)
        parts = current_module.split(".")

        if level > len(parts):
            return None

        base_parts = parts[:-level]

        if module:
            return ".".join(base_parts + module.split("."))
        else:
            return ".".join(base_parts)

    def find_circular_dependencies(self) -> None:
        """Find all circular dependencies using networkx"""
        try:
            # Find all simple cycles
            cycles = list(nx.simple_cycles(self.import_graph))

            # Filter and deduplicate cycles
            seen_cycles = set()
            for cycle in cycles:
                # Sort cycle to create canonical form
                min_idx = cycle.index(min(cycle))
                canonical = tuple(cycle[min_idx:] + cycle[:min_idx])

                if canonical not in seen_cycles:
                    seen_cycles.add(canonical)
                    self.circular_dependencies.append(list(canonical))

        except Exception as e:
            print(f"Error finding cycles: {e}")

    def analyze_impact(self) -> dict[str, Any]:
        """Analyze the impact of circular dependencies"""
        impact = {
            "total_modules": len(self.import_graph.nodes),
            "total_imports": len(self.import_graph.edges),
            "circular_dependencies": len(self.circular_dependencies),
            "affected_modules": set(),
            "high_risk_cycles": [],
            "module_coupling": {},
        }

        # Find affected modules
        for cycle in self.circular_dependencies:
            impact["affected_modules"].update(cycle)

            # High risk if cycle involves core modules
            core_modules = {"core", "orchestration", "governance", "memory"}
            if any(any(core in module for core in core_modules) for module in cycle):
                impact["high_risk_cycles"].append(cycle)

        # Calculate coupling metrics
        for node in self.import_graph.nodes:
            in_degree = self.import_graph.in_degree(node)
            out_degree = self.import_graph.out_degree(node)
            impact["module_coupling"][node] = {
                "imports": out_degree,
                "imported_by": in_degree,
                "coupling_score": in_degree + out_degree,
            }

        return impact

    def suggest_fixes(self) -> list[dict[str, Any]]:
        """Suggest fixes for circular dependencies"""
        suggestions = []

        for cycle in self.circular_dependencies:
            # Analyze the cycle
            suggestion = {
                "cycle": cycle,
                "type": self._classify_cycle(cycle),
                "severity": self._calculate_severity(cycle),
                "fixes": [],
            }

            # Suggest specific fixes based on cycle type
            if suggestion["type"] == "initialization":
                suggestion["fixes"].append(
                    {
                        "action": "lazy_import",
                        "description": "Move imports inside functions to break initialization cycle",
                        "example": "def get_module():\n    from other_module import Component\n    return Component()",
                    }
                )

            elif suggestion["type"] == "bidirectional":
                suggestion["fixes"].append(
                    {
                        "action": "extract_interface",
                        "description": "Extract shared interface to separate module",
                        "modules_to_create": [f"interfaces.{self._suggest_interface_name(cycle)}"],
                    }
                )

            elif suggestion["type"] == "chain":
                # Find the weakest link
                weakest_edge = self._find_weakest_edge(cycle)
                suggestion["fixes"].append(
                    {
                        "action": "break_dependency",
                        "description": f"Remove or refactor import from {weakest_edge[0]} to {weakest_edge[1]}",
                        "alternative": "Use dependency injection or event system",
                    }
                )

            suggestions.append(suggestion)

        return suggestions

    def _classify_cycle(self, cycle: list[str]) -> str:
        """Classify the type of circular dependency"""
        if len(cycle) == 2:
            return "bidirectional"
        elif any("__init__" in module for module in cycle):
            return "initialization"
        else:
            return "chain"

    def _calculate_severity(self, cycle: list[str]) -> str:
        """Calculate severity of circular dependency"""
        # High severity for core modules
        core_modules = {"core", "orchestration", "governance", "memory"}
        if any(any(core in module for core in core_modules) for module in cycle):
            return "high"

        # Medium severity for service modules
        service_modules = {"api", "bridge", "security"}
        if any(any(service in module for service in service_modules) for module in cycle):
            return "medium"

        return "low"

    def _find_weakest_edge(self, cycle: list[str]) -> tuple[str, str]:
        """Find the edge that's easiest to break"""
        if len(cycle) < 2:
            return (cycle[0], cycle[0]) if cycle else ("unknown", "unknown")

        min_coupling = float("inf")
        weakest_edge = (cycle[0], cycle[1])

        for i in range(len(cycle)):
            from_module = cycle[i]
            to_module = cycle[(i + 1) % len(cycle)]

            # Calculate coupling strength
            from_imports = len(self.module_imports[from_module])
            to_imported_by = self.import_graph.in_degree(to_module)
            coupling = from_imports + to_imported_by

            if coupling < min_coupling:
                min_coupling = coupling
                weakest_edge = (from_module, to_module)

        return weakest_edge

    def _suggest_interface_name(self, cycle: list[str]) -> str:
        """Suggest interface module name based on cycle"""
        # Find common prefix
        parts = [module.split(".") for module in cycle]
        common_prefix = []

        for i in range(min(len(p) for p in parts)):
            if all(p[i] == parts[0][i] for p in parts):
                common_prefix.append(parts[0][i])
            else:
                break

        if common_prefix:
            return f"{'.'.join(common_prefix)}_interface"
        else:
            return "common_interface"


def generate_interface_modules(suggestions: list[dict[str, Any]], root_path: Path) -> None:
    """Generate interface module files"""
    interfaces_dir = root_path / "core" / "interfaces"
    interfaces_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_file = interfaces_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Core module interfaces to break circular dependencies"""\n')

    created_interfaces = []

    for suggestion in suggestions:
        if suggestion["type"] == "bidirectional" and suggestion["severity"] in [
            "high",
            "medium",
        ]:
            for fix in suggestion["fixes"]:
                if fix["action"] == "extract_interface":
                    for interface_module in fix.get("modules_to_create", []):
                        interface_name = interface_module.split(".")[-1]
                        interface_file = interfaces_dir / f"{interface_name}.py"

                        if not interface_file.exists():
                            # Generate interface template
                            content = f'''"""
🔌 {interface_name.replace("_", " ").title()}
{"=" * (len(interface_name) + 4)}

Interface module to break circular dependencies between:
{" <-> ".join(suggestion["cycle"])}
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from lukhas.core.common import GLYPHToken

class {interface_name.replace("_interface", "").title()}Interface(ABC):
    """Abstract interface for {interface_name.replace("_interface", "")} modules"""

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the module"""
        pass

    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        pass

# Module registry for dependency injection
_module_registry: Dict[str, {interface_name.replace("_interface", "").title()}Interface] = {{}}

def register_module(name: str, module: {interface_name.replace("_interface", "").title()}Interface) -> None:
    """Register module implementation"""
    _module_registry[name] = module

def get_module(name: str) -> Optional[{interface_name.replace("_interface", "").title()}Interface]:
    """Get registered module"""
    return _module_registry.get(name)
'''
                            interface_file.write_text(content)
                            created_interfaces.append(str(interface_file.relative_to(root_path)))

    return created_interfaces


def main():
    """Main analysis function"""
    print("🔄  Circular Dependency Analysis")
    print("=" * 60)

    analyzer = DependencyAnalyzer(PROJECT_ROOT)

    # Analyze all Python files
    print("\n📂 Analyzing module dependencies...")
    for py_file in PROJECT_ROOT.rglob("*.py"):
        # Skip certain directories
        if any(
            skip in str(py_file)
            for skip in [
                "__pycache__",
                ".git",
                "archive",
                "._cleanup_archive",
                "venv",
                ".venv",
            ]
        ):
            continue

        analyzer.analyze_file(py_file)

    print(f"   Analyzed {analyzer.analyzed_files} files")
    print(f"   Found {len(analyzer.import_graph.nodes)} modules")
    print(f"   Found {len(analyzer.import_graph.edges)} imports")

    # Find circular dependencies
    print("\n🔍 Finding circular dependencies...")
    analyzer.find_circular_dependencies()

    if not analyzer.circular_dependencies:
        print("✅ No circular dependencies found!")
        return

    print(f"❌ Found {len(analyzer.circular_dependencies)} circular dependencies")

    # Analyze impact
    impact = analyzer.analyze_impact()
    print("\n📊 Impact Analysis:")
    print(f"   Affected modules: {len(impact['affected_modules'])}")
    print(f"   High-risk cycles: {len(impact['high_risk_cycles'])}")

    # Show top circular dependencies
    print("\n🔄 Top Circular Dependencies:")
    for i, cycle in enumerate(analyzer.circular_dependencies[:10], 1):
        print(f"\n   {i}. {' → '.join(cycle)} → {cycle[0]}")

    # Generate fix suggestions
    suggestions = analyzer.suggest_fixes()

    print("\n💡 Fix Suggestions:")
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"\n   Cycle {i}: {' → '.join(suggestion['cycle'][:3])}{'...' if len(suggestion['cycle']) > 3 else ''}")
        print(f"   Type: {suggestion['type']}, Severity: {suggestion['severity']}")
        for fix in suggestion["fixes"]:
            print(f"   Fix: {fix['action']} - {fix['description']}")

    # Generate interface modules
    print("\n🔨 Generating interface modules...")
    created_interfaces = generate_interface_modules(suggestions, PROJECT_ROOT)
    if created_interfaces:
        print(f"   Created {len(created_interfaces)} interface modules:")
        for interface in created_interfaces[:5]:
            print(f"   • {interface}")

    # Save detailed report
    report = {
        "summary": {
            "files_analyzed": analyzer.analyzed_files,
            "total_modules": len(analyzer.import_graph.nodes),
            "total_imports": len(analyzer.import_graph.edges),
            "circular_dependencies": len(analyzer.circular_dependencies),
            "affected_modules": list(impact["affected_modules"]),
        },
        "circular_dependencies": analyzer.circular_dependencies,
        "suggestions": suggestions,
        "high_risk_cycles": impact["high_risk_cycles"],
        "module_coupling": impact["module_coupling"],
    }

    report_path = PROJECT_ROOT / "docs" / "reports" / "analysis" / "_CIRCULAR_DEPENDENCY_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
