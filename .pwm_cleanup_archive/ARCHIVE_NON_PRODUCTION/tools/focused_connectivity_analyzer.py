#!/usr/bin/env python3
"""
Focused Module Connectivity Analyzer
Analyzes connectivity of key advanced modules in LUKHAS system
"""

import ast
import json
import os
from collections import defaultdict


class FocusedConnectivityAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.connections = defaultdict(set)
        self.isolated_modules = set()

        # Define key modules to analyze
        self.key_modules = {
            # Ethics modules
            "ethics/meta_ethics_governor.py": "MEG (Meta-Ethics Governor)",
            "ethics/self_reflective_debugger.py": "SRD (Self-Reflective Debugger)",
            "ethics/hitlo_bridge.py": "HITLO (Human-in-the-Loop)",
            "ethics/seedra/seedra_core.py": "SEEDRA Core",
            "ethics/governor/dao_controller.py": "DAO Controller",
            "ethics/governor/lambda_governor.py": "Lambda Governor",
            "ethics/meg_guard.py": "MEG Guard",
            "ethics/compliance/engine.py": "Compliance Engine",
            "ethics/sentinel/ethical_drift_sentinel.py": "Ethical Drift Sentinel",
            "ethics/security/main_node_security_engine.py": "Main Security Engine",
            "ethics/stabilization/tuner.py": "Stabilization Tuner",
            # Golden Trio
            "dast/integration/dast_integration_hub.py": "DAST Integration Hub",
            "abas/integration/abas_integration_hub.py": "ABAS Integration Hub",
            "nias/integration/nias_integration_hub.py": "NIAS Integration Hub",
            # Core Hubs
            "core/core_hub.py": "Core Hub",
            "quantum/quantum_hub.py": "Quantum Hub",
            "consciousness/consciousness_hub.py": "Consciousness Hub",
            "identity/identity_hub.py": "Identity Hub",
            "memory/memory_hub.py": "Memory Hub",
            # Advanced Features
            "creativity/creative_engine.py": "Creative Engine",
            "reasoning/reasoning_engine.py": "Reasoning Engine",
            "engines/learning_engine.py": "Learning Engine",
            "features/integration/dynamic_modality_broker.py": "DMB (Dynamic Modality Broker)",
            # Orchestration
            "quantum/system_orchestrator.py": "System Orchestrator",
            "orchestration/core_modules/orchestration_service.py": "Orchestration Service",
            "bridge/message_bus.py": "Message Bus",
            # Bio Integration
            "bio/bio_engine.py": "Bio Engine",
            "bio/endocrine/hormonal_system.py": "Hormonal System",
            # Colony/Swarm Systems
            "core/colonies/base_colony.py": "Base Colony",
            "core/swarm.py": "Swarm System",
        }

        self.module_imports = {}
        self.module_exports = {}

    def analyze(self):
        """Analyze connectivity of key modules"""
        print("Analyzing focused module connectivity...")

        # First, analyze all Python files to build connection map
        self._scan_all_modules()

        # Then analyze key modules specifically
        results = {
            "connected_modules": {},
            "isolated_modules": {},
            "connection_summary": {},
            "recommendations": [],
        }

        for module_path, module_name in self.key_modules.items():
            full_path = os.path.join(self.root_path, module_path)
            if os.path.exists(full_path):
                connections = self._get_module_connections(module_path)
                if connections:
                    results["connected_modules"][module_name] = {
                        "path": module_path,
                        "connections": list(connections),
                        "connection_count": len(connections),
                    }
                else:
                    results["isolated_modules"][module_name] = {
                        "path": module_path,
                        "imports": self.module_imports.get(module_path, []),
                        "exports": self.module_exports.get(module_path, []),
                    }
            else:
                results["isolated_modules"][module_name] = {
                    "path": module_path,
                    "status": "FILE_NOT_FOUND",
                }

        # Analyze connection patterns
        results["connection_summary"] = self._analyze_connection_patterns(results)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _scan_all_modules(self):
        """Scan all Python modules to build connection map"""
        for root, dirs, files in os.walk(self.root_path):
            # Skip non-source directories
            dirs[:] = [
                d
                for d in dirs
                if d not in [".venv", "__pycache__", ".git", "venv", "env"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_path)

                    # Skip test files
                    if "test" in relative_path:
                        continue

                    self._analyze_module_imports(file_path, relative_path)

    def _analyze_module_imports(self, file_path: str, relative_path: str):
        """Analyze imports in a module"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []
            exports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        self._add_connection(relative_path, alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        self._add_connection(relative_path, node.module)

                elif isinstance(node, ast.ClassDef) or isinstance(
                    node, ast.FunctionDef
                ):
                    exports.append(node.name)

            self.module_imports[relative_path] = imports
            self.module_exports[relative_path] = exports

        except Exception:
            # Skip files with syntax errors
            pass

    def _add_connection(self, from_module: str, to_module: str):
        """Add a connection between modules"""
        # Convert import path to file path
        to_file = to_module.replace(".", "/") + ".py"

        # Check if imported module exists in our codebase
        for key_path in self.key_modules.keys():
            if key_path.endswith(to_file) or to_module in key_path:
                self.connections[from_module].add(key_path)
                self.connections[key_path].add(from_module)

    def _get_module_connections(self, module_path: str):
        """Get all connections for a specific module"""
        connections = set()

        # Direct connections
        if module_path in self.connections:
            connections.update(self.connections[module_path])

        # Check if other modules import this one
        module_name = module_path.replace("/", ".").replace(".py", "")
        for other_path, imports in self.module_imports.items():
            if any(module_name in imp for imp in imports):
                connections.add(other_path)

        return connections

    def _analyze_connection_patterns(self, results):
        """Analyze patterns in module connections"""
        summary = {
            "total_key_modules": len(self.key_modules),
            "connected_count": len(results["connected_modules"]),
            "isolated_count": len(results["isolated_modules"]),
            "connection_rate": f"{len(results['connected_modules']) / len(self.key_modules) * 100:.1f}%",
        }

        # Find most connected modules
        connected_sorted = sorted(
            results["connected_modules"].items(),
            key=lambda x: x[1]["connection_count"],
            reverse=True,
        )
        summary["most_connected"] = connected_sorted[:5] if connected_sorted else []

        # Group isolated modules by type
        isolated_by_type = defaultdict(list)
        for name, info in results["isolated_modules"].items():
            if "ethics" in info.get("path", ""):
                isolated_by_type["Ethics"].append(name)
            elif (
                "dast" in info.get("path", "")
                or "abas" in info.get("path", "")
                or "nias" in info.get("path", "")
            ):
                isolated_by_type["Golden Trio"].append(name)
            elif "hub" in name.lower():
                isolated_by_type["Core Hubs"].append(name)
            else:
                isolated_by_type["Other"].append(name)

        summary["isolated_by_type"] = dict(isolated_by_type)

        return summary

    def _generate_recommendations(self, results):
        """Generate recommendations for reconnecting modules"""
        recommendations = []

        # Check if core hubs are isolated
        for hub in ["Core Hub", "Quantum Hub", "Consciousness Hub"]:
            if hub in results["isolated_modules"]:
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "module": hub,
                        "issue": f"{hub} is isolated and not connected to other systems",
                        "action": f"Connect {hub} to orchestration system and related modules",
                    }
                )

        # Check Golden Trio connectivity
        trio_isolated = [
            m
            for m in [
                "DAST Integration Hub",
                "ABAS Integration Hub",
                "NIAS Integration Hub",
            ]
            if m in results["isolated_modules"]
        ]
        if trio_isolated:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "module": "Golden Trio",
                    "issue": f"{len(trio_isolated)} of 3 Golden Trio hubs are isolated",
                    "action": "Integrate Golden Trio hubs with ethics system and core orchestrator",
                }
            )

        # Check ethics modules
        ethics_isolated = [
            m
            for m, info in results["isolated_modules"].items()
            if "ethics" in info.get("path", "")
        ]
        if len(ethics_isolated) > 5:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "module": "Ethics System",
                    "issue": f"{len(ethics_isolated)} ethics modules are isolated",
                    "action": "Create ethics integration module to connect all ethics components",
                }
            )

        # Check for missing files
        missing = [
            m
            for m, info in results["isolated_modules"].items()
            if info.get("status") == "FILE_NOT_FOUND"
        ]
        if missing:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "module": "Missing Files",
                    "issue": f'{len(missing)} key modules are missing: {", ".join(missing[:3])}...',
                    "action": "Verify file paths or implement missing modules",
                }
            )

        return recommendations

    def generate_report(self, results):
        """Generate a formatted report"""
        report = []
        report.append("=" * 80)
        report.append("FOCUSED MODULE CONNECTIVITY ANALYSIS")
        report.append("=" * 80)

        summary = results["connection_summary"]
        report.append("\nSummary:")
        report.append(f"  Total Key Modules: {summary['total_key_modules']}")
        report.append(f"  Connected: {summary['connected_count']}")
        report.append(f"  Isolated: {summary['isolated_count']}")
        report.append(f"  Connectivity Rate: {summary['connection_rate']}")

        if summary.get("most_connected"):
            report.append("\nMost Connected Modules:")
            for module, info in summary["most_connected"]:
                report.append(f"  - {module}: {info['connection_count']} connections")

        report.append("\nIsolated Modules by Category:")
        for category, modules in summary.get("isolated_by_type", {}).items():
            if modules:
                report.append(f"\n  {category} ({len(modules)} modules):")
                for module in modules[:5]:  # Show first 5
                    report.append(f"    - {module}")
                if len(modules) > 5:
                    report.append(f"    ... and {len(modules) - 5} more")

        report.append("\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            report.append(f"\n  {i}. [{rec['priority']}] {rec['module']}")
            report.append(f"     Issue: {rec['issue']}")
            report.append(f"     Action: {rec['action']}")

        return "\n".join(report)


def main():
    analyzer = FocusedConnectivityAnalyzer(".")
    results = analyzer.analyze()

    # Print report
    report = analyzer.generate_report(results)
    print(report)

    # Save detailed results
    with open("focused_connectivity_report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\nDetailed results saved to focused_connectivity_report.json")


if __name__ == "__main__":
    main()
