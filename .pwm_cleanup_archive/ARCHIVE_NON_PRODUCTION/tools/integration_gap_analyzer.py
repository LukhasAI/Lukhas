#!/usr/bin/env python3
"""
Integration Gap Analyzer
Identifies missing connections and generates integration recommendations
"""

import json
from collections import defaultdict
from typing import Dict


class IntegrationGapAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.modules_by_system = defaultdict(list)
        self.isolated_modules = {}
        self.connection_map = defaultdict(set)
        self.integration_recommendations = []

        # Core systems that should be interconnected
        self.core_systems = {
            "core": "Core infrastructure and coordination",
            "consciousness": "Awareness and cognitive processing",
            "quantum": "Quantum computing and superposition",
            "memory": "Memory and state management",
            "identity": "Identity and authentication",
            "ethics": "Ethical decision making",
            "learning": "Machine learning and adaptation",
            "reasoning": "Logic and reasoning",
            "creativity": "Creative generation",
            "voice": "Voice processing",
            "orchestration": "System orchestration",
        }

        # Expected connections between systems
        self.expected_connections = {
            "core": ["consciousness", "memory", "orchestration", "quantum", "ethics"],
            "consciousness": ["core", "memory", "quantum", "reasoning", "creativity"],
            "quantum": ["core", "consciousness", "memory", "orchestration"],
            "memory": ["core", "consciousness", "learning", "identity"],
            "identity": ["core", "memory", "ethics", "orchestration"],
            "ethics": ["core", "reasoning", "learning", "identity"],
            "learning": ["memory", "reasoning", "ethics", "consciousness"],
            "reasoning": ["consciousness", "learning", "ethics", "creativity"],
            "creativity": ["consciousness", "reasoning", "voice", "memory"],
            "voice": ["creativity", "consciousness", "orchestration"],
            "orchestration": ["core", "identity", "quantum", "voice"],
        }

    def analyze(self):
        """Run complete integration gap analysis"""
        print("Loading connectivity data...")
        self.load_connectivity_data()

        print("Analyzing system boundaries...")
        self.categorize_modules()

        print("Identifying integration gaps...")
        self.identify_gaps()

        print("Generating recommendations...")
        self.generate_recommendations()

        return self.create_reports()

    def load_connectivity_data(self):
        """Load existing connectivity report"""
        try:
            with open("module_connectivity_report.json") as f:
                data = json.load(f)

            # Extract isolated modules
            for directory, modules in data["isolated_modules"]["by_directory"].items():
                if not directory.startswith(".venv"):
                    for module in modules:
                        self.isolated_modules[module] = directory

            # Extract connections
            for edge in data["visualization"]["edges"]:
                self.connection_map[edge["source"]].add(edge["target"])
                self.connection_map[edge["target"]].add(edge["source"])

        except FileNotFoundError:
            print("Warning: module_connectivity_report.json not found")

    def categorize_modules(self):
        """Categorize modules by system"""
        for module_name in self.isolated_modules:
            for system in self.core_systems:
                if module_name.startswith(system):
                    self.modules_by_system[system].append(module_name)
                    break
            else:
                # Module doesn't belong to core systems
                self.modules_by_system["other"].append(module_name)

    def identify_gaps(self):
        """Identify missing connections"""
        self.gaps = {
            "inter_system": [],  # Between different systems
            "intra_system": [],  # Within same system
            "critical": [],  # Critical missing connections
        }

        # Check inter-system connections
        for system1, expected in self.expected_connections.items():
            for system2 in expected:
                if not self.has_connection(system1, system2):
                    self.gaps["inter_system"].append(
                        {
                            "from": system1,
                            "to": system2,
                            "severity": "high",
                            "reason": f"{system1} should connect to {system2}",
                        }
                    )

        # Check intra-system connections
        for system, modules in self.modules_by_system.items():
            if system == "other":
                continue

            # Identify potential hub modules
            hub_candidates = [
                m
                for m in modules
                if "hub" in m or "coordinator" in m or "manager" in m or "__init__" in m
            ]

            if not hub_candidates and modules:
                self.gaps["intra_system"].append(
                    {
                        "system": system,
                        "issue": "No central hub/coordinator",
                        "modules": len(modules),
                        "severity": "critical",
                    }
                )

            # Check for orphaned subsystems
            subsystems = defaultdict(list)
            for module in modules:
                parts = module.split(".")
                if len(parts) > 2:
                    subsystem = ".".join(parts[:3])
                    subsystems[subsystem].append(module)

            for subsystem, submods in subsystems.items():
                if len(submods) > 3 and all(
                    m in self.isolated_modules for m in submods
                ):
                    self.gaps["intra_system"].append(
                        {
                            "system": system,
                            "subsystem": subsystem,
                            "issue": "Entire subsystem isolated",
                            "modules": len(submods),
                            "severity": "high",
                        }
                    )

        # Identify critical gaps
        critical_modules = [
            "core.ai_interface",
            "consciousness.quantum_consciousness_hub",
            "core.safety.ai_safety_orchestrator",
            "memory.systems.memoria_system",
            "orchestration.brain.core.core_integrator",
        ]

        for module in critical_modules:
            if module in self.isolated_modules:
                self.gaps["critical"].append(
                    {
                        "module": module,
                        "issue": "Critical module is isolated",
                        "severity": "critical",
                    }
                )

    def has_connection(self, system1: str, system2: str) -> bool:
        """Check if two systems have any connection"""
        modules1 = self.modules_by_system.get(system1, [])
        modules2 = self.modules_by_system.get(system2, [])

        for m1 in modules1:
            if m1 in self.connection_map:
                for m2 in self.connection_map[m1]:
                    if m2.startswith(system2):
                        return True
        return False

    def generate_recommendations(self):
        """Generate specific integration recommendations"""
        recommendations = []

        # Inter-system recommendations
        for gap in self.gaps["inter_system"]:
            rec = {
                "type": "inter_system",
                "priority": "high" if gap["severity"] == "high" else "medium",
                "task": f"Connect {gap['from']} to {gap['to']}",
                "specific_actions": [],
            }

            # Suggest specific connections
            if gap["from"] == "core" and gap["to"] == "consciousness":
                rec["specific_actions"].extend(
                    [
                        "Import consciousness.quantum_consciousness_hub in core.__init__",
                        "Add consciousness adapter in core.integration_hub",
                        "Create core/consciousness_bridge.py for bidirectional communication",
                    ]
                )
            elif gap["from"] == "memory" and gap["to"] == "learning":
                rec["specific_actions"].extend(
                    [
                        "Import learning.meta_learning in memory.systems.memoria_system",
                        "Add memory provider interface in learning/__init__.py",
                        "Create shared memory-learning protocol in memory/learning_interface.py",
                    ]
                )
            # Add more specific recommendations based on system pairs

            recommendations.append(rec)

        # Intra-system recommendations
        for gap in self.gaps["intra_system"]:
            if gap["issue"] == "No central hub/coordinator":
                rec = {
                    "type": "intra_system",
                    "priority": "critical",
                    "task": f"Create central hub for {gap['system']} system",
                    "specific_actions": [
                        f"Create {gap['system']}/{gap['system']}_hub.py",
                        f"Import all {gap['system']} modules in the hub",
                        f"Add hub to {gap['system']}/__init__.py",
                        "Create service registry in hub for module discovery",
                    ],
                }
                recommendations.append(rec)
            elif gap["issue"] == "Entire subsystem isolated":
                rec = {
                    "type": "intra_system",
                    "priority": "high",
                    "task": f"Integrate {gap['subsystem']} subsystem",
                    "specific_actions": [
                        f"Create {gap['subsystem']}/__init__.py with exports",
                        "Import subsystem in parent module",
                        "Add subsystem to service registry",
                    ],
                }
                recommendations.append(rec)

        # Critical module recommendations
        for gap in self.gaps["critical"]:
            rec = {
                "type": "critical",
                "priority": "critical",
                "task": f"Connect critical module {gap['module']}",
                "specific_actions": [
                    f"Import {gap['module']} in relevant system hubs",
                    "Add to service registry for discovery",
                    "Create integration tests",
                ],
            }
            recommendations.append(rec)

        self.integration_recommendations = recommendations

    def create_reports(self) -> Dict[str, any]:
        """Create comprehensive reports"""
        # Summary report
        summary = {
            "total_isolated": len(self.isolated_modules),
            "systems_analyzed": len(self.core_systems),
            "inter_system_gaps": len(self.gaps["inter_system"]),
            "intra_system_gaps": len(self.gaps["intra_system"]),
            "critical_gaps": len(self.gaps["critical"]),
            "total_recommendations": len(self.integration_recommendations),
        }

        # Detailed system report
        system_report = {}
        for system, description in self.core_systems.items():
            modules = self.modules_by_system.get(system, [])
            connected = [m for m in modules if m not in self.isolated_modules]

            system_report[system] = {
                "description": description,
                "total_modules": len(modules),
                "isolated_modules": len(
                    [m for m in modules if m in self.isolated_modules]
                ),
                "connected_modules": len(connected),
                "isolation_rate": (
                    (
                        len([m for m in modules if m in self.isolated_modules])
                        / len(modules)
                        * 100
                    )
                    if modules
                    else 0
                ),
                "missing_connections": [
                    g for g in self.gaps["inter_system"] if g["from"] == system
                ],
                "internal_issues": [
                    g for g in self.gaps["intra_system"] if g["system"] == system
                ],
            }

        # Integration roadmap
        roadmap = {
            "critical": [
                r
                for r in self.integration_recommendations
                if r["priority"] == "critical"
            ],
            "high": [
                r for r in self.integration_recommendations if r["priority"] == "high"
            ],
            "medium": [
                r for r in self.integration_recommendations if r["priority"] == "medium"
            ],
        }

        return {
            "summary": summary,
            "system_report": system_report,
            "gaps": self.gaps,
            "recommendations": self.integration_recommendations,
            "roadmap": roadmap,
        }


def main():
    analyzer = IntegrationGapAnalyzer("/Users/agi_dev/Downloads/Consolidation-Repo")
    reports = analyzer.analyze()

    # Save reports
    with open("integration_gap_report.json", "w") as f:
        json.dump(reports, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("INTEGRATION GAP ANALYSIS REPORT")
    print("=" * 70)

    summary = reports["summary"]
    print("\nSummary:")
    print(f"  Total Isolated Modules: {summary['total_isolated']}")
    print(f"  Inter-System Gaps: {summary['inter_system_gaps']}")
    print(f"  Intra-System Gaps: {summary['intra_system_gaps']}")
    print(f"  Critical Gaps: {summary['critical_gaps']}")
    print(f"  Total Recommendations: {summary['total_recommendations']}")

    print("\n\nSystem Isolation Rates:")
    print("-" * 50)
    for system, data in reports["system_report"].items():
        if data["total_modules"] > 0:
            print(
                f"{system:15} {data['isolation_rate']:5.1f}% isolated ({data['isolated_modules']}/{data['total_modules']} modules)"
            )

    print("\n\nCritical Integration Tasks:")
    print("-" * 50)
    for rec in reports["roadmap"]["critical"][:5]:
        print(f"\n[CRITICAL] {rec['task']}")
        for action in rec["specific_actions"][:3]:
            print(f"  - {action}")

    print("\n\nHigh Priority Integration Tasks:")
    print("-" * 50)
    for rec in reports["roadmap"]["high"][:5]:
        print(f"\n[HIGH] {rec['task']}")
        for action in rec["specific_actions"][:2]:
            print(f"  - {action}")

    # Generate TODO list
    print("\n\nGenerating integration TODO list...")
    generate_todo_list(reports)

    print("\nReports saved:")
    print("  - integration_gap_report.json")
    print("  - integration_todo_list.md")
    print("=" * 70)


def generate_todo_list(reports):
    """Generate markdown TODO list from recommendations"""
    with open("integration_todo_list.md", "w") as f:
        f.write("# Integration TODO List\n\n")
        f.write("Generated from integration gap analysis\n\n")

        # Critical tasks
        f.write("## 🔴 Critical Priority\n\n")
        for i, rec in enumerate(reports["roadmap"]["critical"], 1):
            f.write(f"### {i}. {rec['task']}\n")
            for action in rec["specific_actions"]:
                f.write(f"- [ ] {action}\n")
            f.write("\n")

        # High priority tasks
        f.write("## 🟡 High Priority\n\n")
        for i, rec in enumerate(reports["roadmap"]["high"], 1):
            f.write(f"### {i}. {rec['task']}\n")
            for action in rec["specific_actions"]:
                f.write(f"- [ ] {action}\n")
            f.write("\n")

        # Medium priority tasks
        f.write("## 🟢 Medium Priority\n\n")
        for i, rec in enumerate(
            reports["roadmap"]["medium"][:10], 1
        ):  # Limit to first 10
            f.write(f"### {i}. {rec['task']}\n")
            for action in rec["specific_actions"]:
                f.write(f"- [ ] {action}\n")
            f.write("\n")

        # System-specific integration needs
        f.write("## 📊 System-Specific Integration Needs\n\n")
        for system, data in reports["system_report"].items():
            if data["isolation_rate"] > 50:
                f.write(
                    f"### {system.title()} System ({data['isolation_rate']:.1f}% isolated)\n"
                )
                f.write(f"- Total modules: {data['total_modules']}\n")
                f.write(f"- Isolated: {data['isolated_modules']}\n")
                f.write("- Needs connection to: ")
                connections_needed = [g["to"] for g in data["missing_connections"]]
                f.write(
                    ", ".join(connections_needed)
                    if connections_needed
                    else "None identified"
                )
                f.write("\n\n")


if __name__ == "__main__":
    main()
