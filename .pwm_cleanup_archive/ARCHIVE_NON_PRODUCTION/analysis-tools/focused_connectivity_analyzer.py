#!/usr/bin/env python3
"""
Focused Connectivity Analyzer for LUKHAS Advanced Modules

Analyzes connectivity specifically for key advanced modules in the LUKHAS system:
1. Ethics modules (MEG, HITLO, SEEDRA, DAO, etc.)
2. Golden Trio (DAST, ABAS, NIAS)
3. Core systems (CoreHub, QuantumHub, ConsciousnessHub)
4. Advanced features (creativity, reasoning, learning)

Filters out .venv and test files, identifies isolated modules, shows connections,
and generates a clear report of what needs reconnecting.
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional


class FocusedConnectivityAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.key_modules = {
            "ethics": {
                "MEG": [
                    "meg_bridge.py",
                    "meg_guard.py",
                    "meg_openai_guard.py",
                    "meta_ethics_governor.py",
                ],
                "HITLO": ["hitlo_bridge.py", "hitlo_bridge_simple.py"],
                "SEEDRA": [
                    "seedra_core.py",
                    "seedra_ethics_engine.py",
                    "seedra_vault_manager.py",
                    "seedra_registry.py",
                ],
                "DAO": [
                    "dao_community.py",
                    "dao_core.py",
                    "dao_governance_node.py",
                    "dao_controller.py",
                ],
                "core": [
                    "ethics.py",
                    "ethical_guardian.py",
                    "ethical_evaluator.py",
                    "ethical_reasoning_system.py",
                ],
            },
            "golden_trio": {
                "DAST": ["dast_core.py", "dast_engine.py", "dast_integration_hub.py"],
                "ABAS": [
                    "abas_engine.py",
                    "abas_integration_hub.py",
                    "abas_quantum_specialist.py",
                ],
                "NIAS": [
                    "nias_core.py",
                    "nias_engine.py",
                    "nias_integration_hub.py",
                    "nias_hub.py",
                ],
            },
            "core_hubs": {
                "CoreHub": ["core_hub.py", "integration_hub.py"],
                "QuantumHub": ["quantum_hub.py", "quantum_integration_hub.py"],
                "ConsciousnessHub": [
                    "consciousness_hub.py",
                    "quantum_consciousness_hub.py",
                ],
            },
            "advanced_features": {
                "creativity": [
                    "creative_engine.py",
                    "creative_core.py",
                    "creative_expression_core.py",
                ],
                "reasoning": [
                    "reasoning_engine.py",
                    "reasoning_hub.py",
                    "symbolic_reasoning.py",
                ],
                "learning": [
                    "learning_hub.py",
                    "meta_learning.py",
                    "federated_learning.py",
                ],
                "memory": [
                    "memory_hub.py",
                    "memory_manager.py",
                    "quantum_memory_manager.py",
                ],
            },
        }

        self.module_connections = defaultdict(set)
        self.isolated_modules = set()
        self.found_modules = {}
        self.import_graph = defaultdict(set)

    def scan_for_modules(self):
        """Scan the repository for key modules, excluding .venv and test files"""
        print("🔍 Scanning for key advanced modules...")

        for category, systems in self.key_modules.items():
            for system, module_files in systems.items():
                self.found_modules[system] = {}

                for module_file in module_files:
                    # Find all instances of this module file
                    matches = list(self.root_path.rglob(module_file))

                    # Filter out .venv, test files, and backup files
                    filtered_matches = []
                    for match in matches:
                        path_str = str(match)
                        if self._should_exclude_path(path_str):
                            continue
                        filtered_matches.append(match)

                    if filtered_matches:
                        self.found_modules[system][module_file] = filtered_matches
                        print(
                            f"  ✓ Found {system}/{module_file}: {len(filtered_matches)} instances"
                        )
                    else:
                        print(f"  ⚠️  Missing {system}/{module_file}")

    def _should_exclude_path(self, path_str: str) -> bool:
        """Check if a path should be excluded from analysis"""
        exclude_patterns = [
            ".venv/",
            "venv/",
            "__pycache__/",
            ".git/",
            "node_modules/",
            "/test_",
            "/tests/",
            "_test.py",
            "_tests.py",
            "test.py",
            ".backup",
            "_backup",
            "/archive/",
            "/archived/",
            ".branding_backup_",
        ]

        path_lower = path_str.lower()
        return any(pattern in path_lower for pattern in exclude_patterns)

    def analyze_imports(self):
        """Analyze import statements to build connectivity graph"""
        print("\n🔗 Analyzing import connections...")

        for system, modules in self.found_modules.items():
            for module_file, paths in modules.items():
                for path in paths:
                    try:
                        imports = self._extract_imports(path)
                        module_key = f"{system}/{module_file}"

                        for imp in imports:
                            # Check if this import connects to another key module
                            connected_system = self._find_connected_system(imp)
                            if connected_system:
                                self.module_connections[module_key].add(
                                    connected_system
                                )
                                self.import_graph[module_key].add(imp)

                    except Exception as e:
                        print(f"  ⚠️  Error analyzing {path}: {e}")

    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from a Python file"""
        imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception:
            # Fallback to regex parsing if AST fails
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                import_patterns = [r"from\s+([^\s]+)\s+import", r"import\s+([^\s,]+)"]

                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    imports.extend(matches)

            except Exception:
                pass

        return imports

    def _find_connected_system(self, import_name: str) -> Optional[str]:
        """Check if an import connects to one of our key systems"""
        import_lower = import_name.lower()

        # Map imports to our key systems
        system_keywords = {
            "ethics": ["ethics", "meg", "hitlo", "seedra", "dao"],
            "dast": ["dast"],
            "abas": ["abas"],
            "nias": ["nias"],
            "core": ["core_hub", "corehub"],
            "quantum": ["quantum_hub", "quantumhub", "quantum"],
            "consciousness": ["consciousness_hub", "consciousnesshub", "consciousness"],
            "creativity": ["creative", "creativity"],
            "reasoning": ["reasoning", "symbolic_reasoning"],
            "learning": ["learning", "meta_learning"],
            "memory": ["memory"],
        }

        for system, keywords in system_keywords.items():
            if any(keyword in import_lower for keyword in keywords):
                return system

        return None

    def identify_isolated_modules(self):
        """Identify modules that have no connections to other key systems"""
        print("\n🏝️  Identifying isolated modules...")

        for system, modules in self.found_modules.items():
            for module_file, paths in modules.items():
                module_key = f"{system}/{module_file}"

                if not self.module_connections.get(module_key):
                    self.isolated_modules.add(module_key)
                    print(f"  🔴 ISOLATED: {module_key}")
                else:
                    connections = self.module_connections[module_key]
                    print(f"  🟢 CONNECTED: {module_key} -> {', '.join(connections)}")

    def analyze_system_connectivity(self) -> Dict:
        """Analyze connectivity between major systems"""
        system_connections = defaultdict(set)

        for module_key, connections in self.module_connections.items():
            system = module_key.split("/")[0]
            for connected_system in connections:
                system_connections[system].add(connected_system)

        return dict(system_connections)

    def generate_reconnection_plan(self) -> List[Dict]:
        """Generate specific tasks for reconnecting isolated modules"""
        tasks = []

        # Group isolated modules by system
        isolated_by_system = defaultdict(list)
        for module_key in self.isolated_modules:
            system = module_key.split("/")[0]
            isolated_by_system[system].append(module_key)

        # Generate reconnection tasks based on system type
        for system, modules in isolated_by_system.items():
            if system in ["MEG", "HITLO", "SEEDRA", "DAO"]:
                tasks.extend(self._generate_ethics_reconnection_tasks(system, modules))
            elif system in ["DAST", "ABAS", "NIAS"]:
                tasks.extend(
                    self._generate_golden_trio_reconnection_tasks(system, modules)
                )
            elif system in ["CoreHub", "QuantumHub", "ConsciousnessHub"]:
                tasks.extend(
                    self._generate_core_hub_reconnection_tasks(system, modules)
                )
            else:
                tasks.extend(self._generate_feature_reconnection_tasks(system, modules))

        return tasks

    def _generate_ethics_reconnection_tasks(
        self, system: str, modules: List[str]
    ) -> List[Dict]:
        """Generate reconnection tasks for ethics modules"""
        tasks = []

        for module in modules:
            tasks.append(
                {
                    "type": "ethics_reconnection",
                    "priority": "high",
                    "system": system,
                    "module": module,
                    "action": f"Connect {system} module to ethics framework",
                    "implementation": [
                        f"Import ethics framework in {module}",
                        f"Register {system} with ethics hub",
                        "Add ethics validation hooks",
                        "Connect to MEG (Meta Ethics Governor) if not MEG itself",
                    ],
                    "target_connections": ["ethics", "core", "governance"],
                }
            )

        return tasks

    def _generate_golden_trio_reconnection_tasks(
        self, system: str, modules: List[str]
    ) -> List[Dict]:
        """Generate reconnection tasks for Golden Trio modules"""
        tasks = []

        for module in modules:
            tasks.append(
                {
                    "type": "golden_trio_reconnection",
                    "priority": "critical",
                    "system": system,
                    "module": module,
                    "action": f"Integrate {system} with Golden Trio orchestrator",
                    "implementation": [
                        f"Connect {system} to TrioOrchestrator",
                        "Register with quantum integration hub",
                        "Connect to consciousness and reasoning systems",
                        f"Ensure {system} participates in decision-making processes",
                    ],
                    "target_connections": [
                        "quantum",
                        "consciousness",
                        "reasoning",
                        "ethics",
                    ],
                }
            )

        return tasks

    def _generate_core_hub_reconnection_tasks(
        self, system: str, modules: List[str]
    ) -> List[Dict]:
        """Generate reconnection tasks for core hub modules"""
        tasks = []

        for module in modules:
            tasks.append(
                {
                    "type": "core_hub_reconnection",
                    "priority": "critical",
                    "system": system,
                    "module": module,
                    "action": f"Connect {system} to system orchestration",
                    "implementation": [
                        f"Register {system} with MasterOrchestrator",
                        "Connect to event bus and message hub",
                        "Establish service discovery registration",
                        "Connect to monitoring and health check systems",
                    ],
                    "target_connections": ["orchestration", "core", "monitoring"],
                }
            )

        return tasks

    def _generate_feature_reconnection_tasks(
        self, system: str, modules: List[str]
    ) -> List[Dict]:
        """Generate reconnection tasks for advanced feature modules"""
        tasks = []

        for module in modules:
            tasks.append(
                {
                    "type": "feature_reconnection",
                    "priority": "medium",
                    "system": system,
                    "module": module,
                    "action": f"Connect {system} feature to system integration",
                    "implementation": [
                        f"Connect {system} to appropriate hub",
                        "Register services with service discovery",
                        "Connect to memory and learning systems",
                        "Add monitoring and metrics collection",
                    ],
                    "target_connections": ["memory", "learning", "core"],
                }
            )

        return tasks

    def generate_report(self):
        """Generate comprehensive connectivity report"""
        print("\n" + "=" * 80)
        print("🎯 FOCUSED CONNECTIVITY ANALYSIS REPORT")
        print("=" * 80)

        # Summary statistics
        total_found = sum(len(modules) for modules in self.found_modules.values())
        total_connected = len(self.module_connections)
        total_isolated = len(self.isolated_modules)

        print("\n📊 SUMMARY:")
        print(f"  • Total key modules found: {total_found}")
        print(f"  • Connected modules: {total_connected}")
        print(f"  • Isolated modules: {total_isolated}")
        print(
            f"  • Connection coverage: {(total_connected/max(total_found,1)*100):.1f}%"
        )

        # System-level connectivity
        system_connections = self.analyze_system_connectivity()

        print("\n🔗 SYSTEM-LEVEL CONNECTIVITY:")
        for system, connections in system_connections.items():
            if connections:
                print(f"  ✓ {system} -> {', '.join(sorted(connections))}")
            else:
                print(f"  ❌ {system} -> ISOLATED")

        # Isolated modules details
        print("\n🏝️  ISOLATED MODULES REQUIRING RECONNECTION:")
        isolated_by_category = defaultdict(list)
        for module in self.isolated_modules:
            system = module.split("/")[0]
            # Categorize by original category
            for category, systems in self.key_modules.items():
                if system in systems:
                    isolated_by_category[category].append(module)
                    break

        for category, modules in isolated_by_category.items():
            print(f"\n  {category.upper()}:")
            for module in sorted(modules):
                paths = []
                system, filename = module.split("/", 1)
                if (
                    system in self.found_modules
                    and filename in self.found_modules[system]
                ):
                    paths = [str(p) for p in self.found_modules[system][filename]]
                print(f"    ❌ {module}")
                for path in paths[:2]:  # Show first 2 paths
                    print(f"       📁 {path}")
                if len(paths) > 2:
                    print(f"       📁 ... and {len(paths)-2} more locations")

        # Generate reconnection plan
        reconnection_tasks = self.generate_reconnection_plan()

        # Create comprehensive report
        report_data = {
            "summary": {
                "total_modules_found": total_found,
                "connected_modules": total_connected,
                "isolated_modules": total_isolated,
                "connection_coverage_percent": round(
                    total_connected / max(total_found, 1) * 100, 1
                ),
            },
            "system_connectivity": {k: list(v) for k, v in system_connections.items()},
            "isolated_modules": list(self.isolated_modules),
            "module_locations": {
                system: {
                    filename: [str(p) for p in paths]
                    for filename, paths in modules.items()
                }
                for system, modules in self.found_modules.items()
            },
            "reconnection_tasks": reconnection_tasks,
            "import_graph": {k: list(v) for k, v in self.import_graph.items()},
        }

        # Save detailed report
        report_path = self.root_path / "focused_connectivity_report.json"
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_path}")

        # Show high-priority reconnection tasks
        print("\n🎯 PRIORITY RECONNECTION TASKS:")
        high_priority_tasks = [
            t for t in reconnection_tasks if t["priority"] in ["critical", "high"]
        ]

        for i, task in enumerate(high_priority_tasks[:10], 1):
            print(f"\n{i}. {task['action']}")
            print(f"   Priority: {task['priority'].upper()}")
            print(f"   System: {task['system']}")
            print("   Implementation steps:")
            for step in task["implementation"]:
                print(f"     • {step}")

        if len(high_priority_tasks) > 10:
            print(f"\n... and {len(high_priority_tasks) - 10} more high-priority tasks")

        print("\n📋 NEXT STEPS:")
        print("  1. Review isolated modules and understand why they're disconnected")
        print("  2. Implement high-priority reconnection tasks first")
        print("  3. Focus on Golden Trio and Core Hub connections")
        print("  4. Ensure ethics modules are properly integrated")
        print("  5. Re-run analysis after each batch of connections")


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent

    print("🚀 Starting Focused Connectivity Analysis for LUKHAS Advanced Modules")
    print(f"📁 Repository root: {repo_root}")

    analyzer = FocusedConnectivityAnalyzer(repo_root)

    # Run analysis
    analyzer.scan_for_modules()
    analyzer.analyze_imports()
    analyzer.identify_isolated_modules()
    analyzer.generate_report()

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
