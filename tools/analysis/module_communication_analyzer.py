#!/usr/bin/env python3
"""
 Module Communication Analyzer
=================================
Analyzes current module communication patterns to identify optimization opportunities.
"""

import ast
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class ModuleCommunicationAnalyzer:
    """Analyzes communication patterns between LUKHAS modules"""

    def __init__(self):
        # Analyze from repository root
        self.root_path = Path.cwd()
        self.communication_graph = nx.DiGraph()
        self.glyph_usage = defaultdict(list)
        self.direct_imports = defaultdict(set)
        self.event_patterns = defaultdict(list)
        self.circular_dependencies = []

    def analyze(self) -> dict[str, Any]:
        """Run comprehensive communication analysis"""
        logger.info("🔍 Analyzing LUKHAS  Module Communication Patterns...\n")

        # Analyze different communication methods
        self._analyze_import_patterns()
        self._analyze_glyph_communication()
        self._analyze_event_patterns()
        self._detect_circular_dependencies()
        self._analyze_communication_bottlenecks()

        # Generate optimization recommendations
        recommendations = self._generate_recommendations()

        # Create report
        report = {
            "summary": self._generate_summary(),
            "communication_patterns": {
                "import_based": self._summarize_imports(),
                "glyph_based": self._summarize_glyphs(),
                "event_based": self._summarize_events(),
            },
            "issues": {
                "circular_dependencies": self.circular_dependencies,
                "bottlenecks": self._identify_bottlenecks(),
                "inefficiencies": self._identify_inefficiencies(),
            },
            "recommendations": recommendations,
            "optimization_plan": self._create_optimization_plan(),
        }

        # Save report
        report_path = self.root_path / "docs" / "reports" / "module_communication_analysis.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate visualization
        self._create_communication_graph()

        # Print summary
        self._print_summary(report)

        return report

    def _analyze_import_patterns(self):
        """Analyze direct import-based communication"""
        logger.info("📦 Analyzing import-based communication...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                module_name = self._get_module_name(py_file)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        imported_module = node.module.split(".")[0]
                        if imported_module in [
                            "core",
                            "consciousness",
                            "memory",
                            "orchestration",
                            "governance",
                        ]:
                            self.direct_imports[module_name].add(imported_module)
                            self.communication_graph.add_edge(
                                module_name,
                                imported_module,
                                method="import",
                                weight=1,
                            )

            except Exception:
                pass

        logger.info(f"   Found {len(self.direct_imports)} modules with cross-module imports")

    def _analyze_glyph_communication(self):
        """Analyze GLYPH-based communication patterns"""
        logger.info("\n🔮 Analyzing GLYPH-based communication...")

        glyph_patterns = [
            "GLYPHSymbol",
            "create_glyph",
            "emit_glyph",
            "process_glyph",
            "glyph_exchange",
            "symbolic_token",
        ]

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                module_name = self._get_module_name(py_file)

                for pattern in glyph_patterns:
                    if pattern in content:
                        self.glyph_usage[module_name].append(
                            {
                                "pattern": pattern,
                                "file": str(py_file.relative_to(self.root_path)),
                                "count": content.count(pattern),
                            }
                        )

            except Exception:
                pass

        logger.info(f"   Found {len(self.glyph_usage)} modules using GLYPH communication")

    def _analyze_event_patterns(self):
        """Analyze event-based communication patterns"""
        logger.info("\n📡 Analyzing event-based communication...")

        event_patterns = [
            "EventBus",
            "emit_event",
            "subscribe",
            "publish",
            "on_event",
            "event_handler",
            "message_queue",
        ]

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                module_name = self._get_module_name(py_file)

                for pattern in event_patterns:
                    if pattern in content:
                        self.event_patterns[module_name].append(
                            {
                                "pattern": pattern,
                                "file": str(py_file.relative_to(self.root_path)),
                                "count": content.count(pattern),
                            }
                        )

            except Exception:
                pass

        logger.info(f"   Found {len(self.event_patterns)} modules using event-based communication")

    def _detect_circular_dependencies(self):
        """Detect circular dependencies in module communication"""
        logger.info("\n🔄 Detecting circular dependencies...")

        try:
            cycles = list(nx.simple_cycles(self.communication_graph))
            self.circular_dependencies = [list(cycle) for cycle in cycles if len(cycle) > 1]
            logger.info(f"   Found {len(self.circular_dependencies)} circular dependencies")
        except Exception:
            logger.warning("   Could not detect cycles in communication graph")

    def _analyze_communication_bottlenecks(self):
        """Identify communication bottlenecks"""
        logger.info("\n🚧 Analyzing communication bottlenecks...")

        # Calculate node centrality
        if self.communication_graph.nodes():
            try:
                self.centrality = nx.betweenness_centrality(self.communication_graph)
                self.in_degree = dict(self.communication_graph.in_degree())
                self.out_degree = dict(self.communication_graph.out_degree())

                # Find highly connected nodes
                avg_degree = sum(self.in_degree.values()) / len(self.in_degree) if self.in_degree else 0
                bottlenecks = [node for node, degree in self.in_degree.items() if degree > avg_degree * 2]

                logger.info(f"   Identified {len(bottlenecks)} potential bottleneck modules")
            except Exception:
                pass

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path"""
        relative_path = file_path.relative_to(self.root_path)
        parts = relative_path.parts
        if parts[0] in [
            "core",
            "consciousness",
            "memory",
            "orchestration",
            "governance",
            "api",
            "vivox",
        ]:
            return parts[0]
        return "other"

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ["__pycache__", ".git", "archive", "test_", "docs/"]
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _summarize_imports(self) -> dict[str, Any]:
        """Summarize import-based communication"""
        return {
            "total_modules": len(self.direct_imports),
            "total_connections": sum(len(imports) for imports in self.direct_imports.values()),
            "most_imported": self._get_most_imported_modules(),
            "most_importing": self._get_most_importing_modules(),
        }

    def _summarize_glyphs(self) -> dict[str, Any]:
        """Summarize GLYPH-based communication"""
        total_glyph_usage = sum(sum(g["count"] for g in glyphs) for glyphs in self.glyph_usage.values())

        return {
            "modules_using_glyphs": len(self.glyph_usage),
            "total_glyph_operations": total_glyph_usage,
            "most_active_modules": self._get_most_active_glyph_modules(),
        }

    def _summarize_events(self) -> dict[str, Any]:
        """Summarize event-based communication"""
        total_event_usage = sum(sum(e["count"] for e in events) for events in self.event_patterns.values())

        return {
            "modules_using_events": len(self.event_patterns),
            "total_event_operations": total_event_usage,
            "most_active_modules": self._get_most_active_event_modules(),
        }

    def _get_most_imported_modules(self) -> list[tuple[str, int]]:
        """Get most imported modules"""
        import_counts = defaultdict(int)
        for imports in self.direct_imports.values():
            for module in imports:
                import_counts[module] += 1

        return sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    def _get_most_importing_modules(self) -> list[tuple[str, int]]:
        """Get modules that import the most"""
        return sorted(
            [(module, len(imports)) for module, imports in self.direct_imports.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

    def _get_most_active_glyph_modules(self) -> list[tuple[str, int]]:
        """Get modules with most GLYPH usage"""
        glyph_counts = {module: sum(g["count"] for g in glyphs) for module, glyphs in self.glyph_usage.items()}
        return sorted(glyph_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    def _get_most_active_event_modules(self) -> list[tuple[str, int]]:
        """Get modules with most event usage"""
        event_counts = {module: sum(e["count"] for e in events) for module, events in self.event_patterns.items()}
        return sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    def _identify_bottlenecks(self) -> list[dict[str, Any]]:
        """Identify communication bottlenecks"""
        bottlenecks = []

        if hasattr(self, "in_degree"):
            avg_in_degree = sum(self.in_degree.values()) / len(self.in_degree) if self.in_degree else 0

            for node, degree in self.in_degree.items():
                if degree > avg_in_degree * 2:
                    bottlenecks.append(
                        {
                            "module": node,
                            "incoming_connections": degree,
                            "outgoing_connections": self.out_degree.get(node, 0),
                            "centrality": self.centrality.get(node, 0),
                        }
                    )

        return sorted(bottlenecks, key=lambda x: x["incoming_connections"], reverse=True)

    def _identify_inefficiencies(self) -> list[dict[str, str]]:
        """Identify communication inefficiencies"""
        inefficiencies = []

        # Check for modules using multiple communication methods
        multi_method_modules = []
        for module in set(
            list(self.direct_imports.keys()) + list(self.glyph_usage.keys()) + list(self.event_patterns.keys())
        ):
            methods = []
            if module in self.direct_imports:
                methods.append("imports")
            if module in self.glyph_usage:
                methods.append("glyphs")
            if module in self.event_patterns:
                methods.append("events")

            if len(methods) > 2:
                multi_method_modules.append(module)

        if multi_method_modules:
            inefficiencies.append(
                {
                    "type": "multiple_communication_methods",
                    "description": f"{len(multi_method_modules)} modules use 3+ communication methods",
                    "modules": multi_method_modules[:5],
                }
            )

        # Check for tight coupling
        tightly_coupled = []
        for module, imports in self.direct_imports.items():
            if len(imports) > 3:
                tightly_coupled.append(module)

        if tightly_coupled:
            inefficiencies.append(
                {
                    "type": "tight_coupling",
                    "description": f"{len(tightly_coupled)} modules import from 4+ other modules",
                    "modules": tightly_coupled[:5],
                }
            )

        return inefficiencies

    def _generate_recommendations(self) -> list[dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []

        # Recommendation for circular dependencies
        if self.circular_dependencies:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "Circular dependencies detected",
                    "recommendation": "Break circular dependencies using interfaces or event-based communication",
                    "affected_modules": self.circular_dependencies[:3],
                    "impact": "Improved maintainability and reduced coupling",
                }
            )

        # Recommendation for bottlenecks
        bottlenecks = self._identify_bottlenecks()
        if bottlenecks:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "Communication bottlenecks identified",
                    "recommendation": "Implement caching or message queuing for high-traffic modules",
                    "affected_modules": [b["module"] for b in bottlenecks[:3]],
                    "impact": "Better performance and scalability",
                }
            )

        # Recommendation for GLYPH optimization
        if len(self.glyph_usage) < 5:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "issue": "Underutilized GLYPH communication",
                    "recommendation": "Increase GLYPH usage for loose coupling between modules",
                    "current_usage": f"{len(self.glyph_usage)} modules",
                    "target": "All major modules should support GLYPH communication",
                }
            )

        # Recommendation for event-based communication
        if len(self.event_patterns) < 10:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "issue": "Limited event-based communication",
                    "recommendation": "Implement centralized event bus for async communication",
                    "benefit": "Reduced coupling and better scalability",
                }
            )

        return recommendations

    def _create_optimization_plan(self) -> dict[str, Any]:
        """Create detailed optimization plan"""
        return {
            "phase1": {
                "name": "Break Circular Dependencies",
                "duration": "2-3 days",
                "tasks": [
                    "Identify all circular dependency chains",
                    "Create interface abstractions",
                    "Refactor direct imports to use interfaces",
                    "Test module isolation",
                ],
            },
            "phase2": {
                "name": "Implement Event Bus",
                "duration": "3-4 days",
                "tasks": [
                    "Design centralized event bus architecture",
                    "Create event types and schemas",
                    "Implement publish/subscribe mechanism",
                    "Migrate high-traffic communications to events",
                ],
            },
            "phase3": {
                "name": "Optimize GLYPH Communication",
                "duration": "1 week",
                "tasks": [
                    "Standardize GLYPH token formats",
                    "Create GLYPH routing system",
                    "Implement GLYPH caching layer",
                    "Add GLYPH monitoring and metrics",
                ],
            },
            "phase4": {
                "name": "Decouple Bottleneck Modules",
                "duration": "1 week",
                "tasks": [
                    "Implement message queuing for bottlenecks",
                    "Add caching layers",
                    "Create module proxies",
                    "Implement load balancing",
                ],
            },
        }

    def _generate_summary(self) -> dict[str, Any]:
        """Generate analysis summary"""
        return {
            "total_modules_analyzed": len(
                set(list(self.direct_imports.keys()) + list(self.glyph_usage.keys()) + list(self.event_patterns.keys()))
            ),
            "communication_methods": {
                "import_based": len(self.direct_imports),
                "glyph_based": len(self.glyph_usage),
                "event_based": len(self.event_patterns),
            },
            "issues_found": {
                "circular_dependencies": len(self.circular_dependencies),
                "bottlenecks": len(self._identify_bottlenecks()),
                "inefficiencies": len(self._identify_inefficiencies()),
            },
        }

    def _create_communication_graph(self):
        """Create visual representation of module communication"""
        if not self.communication_graph.nodes():
            return

        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.communication_graph)

            # Draw nodes
            node_sizes = [self.in_degree.get(node, 1) * 100 for node in self.communication_graph.nodes()]
            nx.draw_networkx_nodes(
                self.communication_graph,
                pos,
                node_size=node_sizes,
                node_color="lightblue",
                alpha=0.7,
            )

            # Draw edges
            nx.draw_networkx_edges(self.communication_graph, pos, alpha=0.5, edge_color="gray", arrows=True)

            # Draw labels
            nx.draw_networkx_labels(self.communication_graph, pos)

            plt.title("LUKHAS Module Communication Graph")
            plt.axis("off")

            # Save graph
            graph_path = self.root_path / "docs" / "reports" / "module_communication_graph.png"
            plt.savefig(graph_path, dpi=300, bbox_inches="tight")
            plt.close()

            logger.info(f"\n📊 Communication graph saved to: {graph_path}")
        except Exception as e:
            logger.warning(f"   Could not create graph visualization: {e}")

    def _print_summary(self, report: dict[str, Any]):
        """Print analysis summary"""
        print("\n" + "=" * 80)
        print("📊 MODULE COMMUNICATION ANALYSIS SUMMARY")
        print("=" * 80)

        summary = report["summary"]
        print("\n📈 Overview:")
        print(f"   Modules analyzed: {summary['total_modules_analyzed']}")
        print(f"   Using imports: {summary['communication_methods']['import_based']}")
        print(f"   Using GLYPHs: {summary['communication_methods']['glyph_based']}")
        print(f"   Using events: {summary['communication_methods']['event_based']}")

        print("\n⚠️  Issues Found:")
        print(f"   Circular dependencies: {summary['issues_found']['circular_dependencies']}")
        print(f"   Bottlenecks: {summary['issues_found']['bottlenecks']}")
        print(f"   Inefficiencies: {summary['issues_found']['inefficiencies']}")

        if report["recommendations"]:
            print("\n💡 Top Recommendations:")
            for rec in report["recommendations"][:3]:
                print(f"\n   [{rec['priority']}] {rec['issue']}")
                print(f"   → {rec['recommendation']}")

        print("\n📁 Full report: docs/reports/module_communication_analysis.json")
        print("=" * 80)


def main():
    """Run module communication analysis"""
    analyzer = ModuleCommunicationAnalyzer()
    analyzer.analyze()


if __name__ == "__main__":
    main()
