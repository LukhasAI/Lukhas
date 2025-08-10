#!/usr/bin/env python3
"""
Comprehensive Connectivity Assessment
Analyzes system connectivity post-Agent 4 completion and generates consolidation plan
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class ConnectivityAssessment:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.unused_files = []
        self.isolated_files = []
        self.connection_opportunities = []
        self.consolidation_candidates = defaultdict(
            lambda: {"count": 0, "files": [], "total_size": 0}
        )

    def load_reports(self):
        """Load existing analysis reports"""
        # Load unused files report
        report_path = self.root_path / "analysis-tools" / "unused_files_report.json"
        if report_path.exists():
            with open(report_path) as f:
                data = json.load(f)
                self.unused_files = data.get("unused_files", [])
                self.isolated_files = data.get("isolated_files", [])

        # Load connectivity report
        conn_path = self.root_path / "analysis-tools" / "connectivity_report.json"
        if conn_path.exists():
            with open(conn_path) as f:
                self.connectivity_data = json.load(f)

    def analyze_connection_opportunities(self):
        """Identify opportunities to connect unused files"""

        # Categorize unused files
        categories = {
            "orchestrators": [],
            "bridges": [],
            "hubs": [],
            "engines": [],
            "managers": [],
            "apis": [],
            "tests": [],
            "demos": [],
            "utils": [],
            "golden_trio": [],
        }

        for file_info in self.unused_files:
            path = file_info["path"].lower()

            if "orchestrator" in path:
                categories["orchestrators"].append(file_info)
            elif "bridge" in path:
                categories["bridges"].append(file_info)
            elif "hub" in path:
                categories["hubs"].append(file_info)
            elif "engine" in path:
                categories["engines"].append(file_info)
            elif "manager" in path:
                categories["managers"].append(file_info)
            elif "api" in path:
                categories["apis"].append(file_info)
            elif "test" in path or "demo" in path:
                categories["tests"].append(file_info)
            elif "demo" in path:
                categories["demos"].append(file_info)
            elif any(trio in path for trio in ["dast", "abas", "nias"]):
                categories["golden_trio"].append(file_info)
            else:
                categories["utils"].append(file_info)

        return categories

    def analyze_consolidation_opportunities(self):
        """Identify duplicate files that can be consolidated"""

        # Extract core names from file paths
        for file_info in self.unused_files:
            path = Path(file_info["path"])
            name = path.stem

            # Normalize names to find duplicates
            core_name = self._extract_core_name(name)

            self.consolidation_candidates[core_name]["count"] += 1
            self.consolidation_candidates[core_name]["files"].append(file_info)
            self.consolidation_candidates[core_name]["total_size"] += file_info.get(
                "size", 0
            )

    def _extract_core_name(self, filename: str) -> str:
        """Extract core functionality name from filename"""
        # Remove common suffixes/prefixes
        patterns = [
            r"_v\d+",  # version numbers
            r"_old",
            r"_new",
            r"_backup",
            r"_copy",
            r"_test",
            r"_demo",
            r"_example",
            r"_integration",
            r"_impl",
            r"_implementation",
            r"_service",
            r"_client",
            r"_server",
            r"_api",
            r"_interface",
            r"_base",
            r"_core",
            r"_main",
            r"_manager",
            r"_controller",
            r"_handler",
            r"_processor",
            r"_analyzer",
            r"_validator",
            r"_generator",
            r"_builder",
            r"_factory",
            r"_singleton",
            r"_instance",
            r"_wrapper",
            r"_adapter",
            r"_proxy",
            r"_decorator",
            r"_observer",
            r"_listener",
            r"_emitter",
            r"_publisher",
            r"_subscriber",
            r"_queue",
            r"_stack",
            r"_list",
            r"_dict",
            r"_map",
            r"_set",
            r"_tree",
            r"_graph",
            r"_node",
            r"_edge",
            r"_vertex",
            r"_path",
            r"_route",
            r"_link",
            r"_connection",
            r"_bridge",
            r"_hub",
            r"_spoke",
            r"_cluster",
            r"_pool",
            r"_cache",
            r"_store",
            r"_repository",
            r"_dao",
            r"_dto",
            r"_model",
            r"_entity",
            r"_schema",
            r"_type",
            r"_enum",
            r"_constant",
            r"_config",
            r"_settings",
            r"_options",
            r"_params",
            r"_args",
            r"_kwargs",
            r"_input",
            r"_output",
            r"_request",
            r"_response",
            r"_result",
            r"_status",
            r"_error",
            r"_exception",
            r"_warning",
            r"_info",
            r"_debug",
            r"_trace",
            r"_log",
            r"_logger",
            r"_monitor",
            r"_metric",
            r"_stat",
            r"_counter",
            r"_gauge",
            r"_timer",
            r"_histogram",
            r"_summary",
        ]

        core_name = filename.lower()
        for pattern in patterns:
            core_name = re.sub(pattern, "", core_name)

        return core_name.strip("_")

    def generate_connection_plan(self) -> List[Dict]:
        """Generate actionable tasks to improve connectivity"""
        categories = self.analyze_connection_opportunities()
        tasks = []

        # Priority 1: Connect Golden Trio components
        if categories["golden_trio"]:
            tasks.extend(self._generate_golden_trio_connections())

        # Priority 2: Connect orchestrators
        if categories["orchestrators"]:
            tasks.extend(self._generate_orchestrator_connections())

        # Priority 3: Connect bridges
        if categories["bridges"]:
            tasks.extend(self._generate_bridge_connections())

        # Priority 4: Connect hubs
        if categories["hubs"]:
            tasks.extend(self._generate_hub_connections())

        # Priority 5: Connect engines
        if categories["engines"]:
            tasks.extend(self._generate_engine_connections())

        return tasks

    def _generate_bridge_connections(self) -> List[Dict]:
        """Generate tasks for connecting isolated bridges"""
        tasks = []
        categories = self.analyze_connection_opportunities()

        for bridge in categories["bridges"]:
            # Extract systems that this bridge should connect
            bridge_name = Path(bridge["path"]).stem
            systems = self._extract_systems_from_bridge_name(bridge_name)

            if len(systems) >= 2:
                tasks.append(
                    {
                        "type": "connect_bridge",
                        "priority": "high",
                        "file": bridge["path"],
                        "systems": systems,
                        "action": f"Connect bridge between {systems[0]} and {systems[1]}",
                        "implementation": "Register in bridge registry and connect to both systems",
                    }
                )

        return tasks

    def _generate_hub_connections(self) -> List[Dict]:
        """Generate tasks for connecting isolated hubs"""
        tasks = []
        categories = self.analyze_connection_opportunities()

        for hub in categories["hubs"]:
            # Determine the system this hub belongs to
            path_parts = Path(hub["path"]).parts
            system = path_parts[0] if path_parts else "unknown"

            tasks.append(
                {
                    "type": "connect_hub",
                    "priority": "high",
                    "file": hub["path"],
                    "system": system,
                    "action": f"Connect {Path(hub['path']).name} to hub registry",
                    "implementation": "Register hub and establish connections to related components",
                }
            )

        return tasks

    def _generate_engine_connections(self) -> List[Dict]:
        """Generate tasks for connecting isolated engines"""
        tasks = []
        categories = self.analyze_connection_opportunities()

        # Group engines by system
        system_engines = defaultdict(list)
        for engine in categories["engines"]:
            system = (
                Path(engine["path"]).parts[0]
                if Path(engine["path"]).parts
                else "unknown"
            )
            system_engines[system].append(engine)

        for system, engines in system_engines.items():
            if len(engines) > 1:
                # Multiple engines in same system - consolidation candidate
                tasks.append(
                    {
                        "type": "consolidate_engines",
                        "priority": "medium",
                        "system": system,
                        "files": [e["path"] for e in engines],
                        "action": f"Consolidate {len(engines)} engines in {system}",
                        "implementation": "Merge functionality and remove duplicates",
                    }
                )
            else:
                # Single engine - just needs connection
                for engine in engines:
                    tasks.append(
                        {
                            "type": "connect_engine",
                            "priority": "medium",
                            "file": engine["path"],
                            "system": system,
                            "action": f"Connect {Path(engine['path']).name} to system",
                            "implementation": "Register with appropriate hub or orchestrator",
                        }
                    )

        return tasks

    def _generate_orchestrator_connections(self) -> List[Dict]:
        """Generate tasks for connecting orchestrators"""
        tasks = []
        categories = self.analyze_connection_opportunities()

        isolated_orchestrators = categories["orchestrators"]

        # Group by system
        system_orchestrators = defaultdict(list)
        for orch in isolated_orchestrators:
            system = (
                Path(orch["path"]).parts[0] if Path(orch["path"]).parts else "unknown"
            )
            system_orchestrators[system].append(orch)

        for system, orchestrators in system_orchestrators.items():
            if len(orchestrators) > 1:
                # Consolidation needed
                tasks.append(
                    {
                        "type": "consolidate_orchestrators",
                        "priority": "high",
                        "system": system,
                        "files": [o["path"] for o in orchestrators],
                        "action": f"Consolidate {len(orchestrators)} orchestrators in {system}",
                        "implementation": "Merge functionality into single orchestrator",
                    }
                )
            else:
                # Just needs connection
                for orch in orchestrators:
                    tasks.append(
                        {
                            "type": "connect_orchestrator",
                            "priority": "medium",
                            "file": orch["path"],
                            "system": system,
                            "action": f"Connect {Path(orch['path']).name} to main orchestration layer",
                            "implementation": "Register with MasterOrchestrator or system coordinator",
                        }
                    )

        return tasks

    def _generate_golden_trio_connections(self) -> List[Dict]:
        """Generate tasks for Golden Trio integration"""
        tasks = []
        categories = self.analyze_connection_opportunities()

        # Find unused Golden Trio components
        trio_files = {"dast": [], "abas": [], "nias": []}

        for f in categories["golden_trio"]:
            path_lower = f["path"].lower()
            for system in trio_files:
                if system in path_lower:
                    trio_files[system].append(f)

        # Generate integration tasks
        for system, files in trio_files.items():
            if files:
                tasks.append(
                    {
                        "type": "integrate_golden_trio",
                        "priority": "high",
                        "system": system.upper(),
                        "files": [f["path"] for f in files],
                        "action": f"Integrate unused {system.upper()} components with TrioOrchestrator",
                        "implementation": "Connect to Phase 1 foundation (SEEDRA, Symbolic Language, Ethics Engine)",
                    }
                )

        return tasks

    def _extract_systems_from_bridge_name(self, bridge_name: str) -> List[str]:
        """Extract system names from bridge filename"""
        systems = []

        # Known system names
        known_systems = [
            "memory",
            "learning",
            "consciousness",
            "quantum",
            "bio",
            "symbolic",
            "ethics",
            "safety",
            "orchestration",
            "core",
            "dast",
            "abas",
            "nias",
        ]

        for system in known_systems:
            if system in bridge_name:
                systems.append(system)

        return systems

    def generate_consolidation_plan(self) -> List[Dict]:
        """Generate a plan for consolidating duplicate files"""
        consolidation_tasks = []

        # Sort by total size (prioritize larger consolidations)
        sorted_candidates = sorted(
            self.consolidation_candidates.items(),
            key=lambda x: x[1]["total_size"],
            reverse=True,
        )

        for core_name, info in sorted_candidates[:20]:  # Top 20
            if info["count"] > 2:  # Only if 3+ duplicates
                consolidation_tasks.append(
                    {
                        "type": "consolidate_duplicates",
                        "priority": "medium" if info["total_size"] > 50000 else "low",
                        "core_name": core_name,
                        "file_count": info["count"],
                        "total_size": info["total_size"],
                        "files": [f["path"] for f in info["files"]],
                        "action": f"Consolidate {info['count']} versions of {core_name}",
                        "implementation": "Review implementations, merge best features, remove duplicates",
                    }
                )

        return consolidation_tasks

    def generate_report(self):
        """Generate comprehensive report and todo list"""
        print("\n" + "=" * 80)
        print("CONNECTIVITY ASSESSMENT REPORT")
        print("=" * 80)

        # Summary
        print(f"\nTotal Unused Files: {len(self.unused_files)}")
        print(f"Isolated Files: {len(self.isolated_files)}")
        print(f"Connection Opportunities: {len(self.connection_opportunities)}")
        print(f"Consolidation Candidates: {len(self.consolidation_candidates)}")

        # Generate tasks
        connection_tasks = self.generate_connection_plan()
        consolidation_tasks = self.generate_consolidation_plan()

        # Create todo list
        todo_list = {
            "connection_tasks": connection_tasks,
            "consolidation_tasks": consolidation_tasks,
            "summary": {
                "total_connection_tasks": len(connection_tasks),
                "total_consolidation_tasks": len(consolidation_tasks),
                "high_priority_tasks": len(
                    [
                        t
                        for t in connection_tasks + consolidation_tasks
                        if t.get("priority") == "high"
                    ]
                ),
                "estimated_file_reduction": sum(
                    c["file_count"] - 1 for c in consolidation_tasks
                ),
            },
        }

        # Save report
        report_path = self.root_path / "analysis-tools" / "connectivity_todo_list.json"
        with open(report_path, "w") as f:
            json.dump(todo_list, f, indent=2)

        print(f"\n✅ Todo list saved to: {report_path}")

        # Display high priority tasks
        print("\n" + "=" * 60)
        print("HIGH PRIORITY TASKS:")
        print("=" * 60)

        high_priority = [
            t
            for t in connection_tasks + consolidation_tasks
            if t.get("priority") == "high"
        ]
        for i, task in enumerate(high_priority[:10], 1):
            print(f"\n{i}. {task['action']}")
            print(f"   Type: {task['type']}")
            print(f"   Implementation: {task['implementation']}")
            if "files" in task:
                print(f"   Files: {len(task['files'])} files involved")


def main():
    repo_root = Path(__file__).parent.parent

    assessment = ConnectivityAssessment(repo_root)
    assessment.load_reports()
    assessment.analyze_connection_opportunities()
    assessment.analyze_consolidation_opportunities()
    assessment.generate_report()


if __name__ == "__main__":
    main()
