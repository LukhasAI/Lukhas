#!/usr/bin/env python3
"""
System Connectivity Visualizer

Creates a visual representation of system connectivity and identifies integration status.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List


class ConnectivityVisualizer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.systems = {
            "core": {"color": "#FF6B6B", "hubs": [], "bridges": []},
            "consciousness": {"color": "#4ECDC4", "hubs": [], "bridges": []},
            "memory": {"color": "#45B7D1", "hubs": [], "bridges": []},
            "quantum": {"color": "#96CEB4", "hubs": [], "bridges": []},
            "bio": {"color": "#DDA0DD", "hubs": [], "bridges": []},
            "symbolic": {"color": "#FFD93D", "hubs": [], "bridges": []},
            "nias": {"color": "#FF8C42", "hubs": [], "bridges": []},
            "learning": {"color": "#6C5CE7", "hubs": [], "bridges": []},
            "dream": {"color": "#A8E6CF", "hubs": [], "bridges": []},
            "orchestration": {"color": "#FF6B9D", "hubs": [], "bridges": []},
            "safety": {"color": "#C7CEEA", "hubs": [], "bridges": []},
            "ethics": {"color": "#FFA07A", "hubs": [], "bridges": []},
            "dast": {"color": "#98D8C8", "hubs": [], "bridges": []},
            "abas": {"color": "#F7DC6F", "hubs": [], "bridges": []},
            "identity": {"color": "#85C1E2", "hubs": [], "bridges": []},
            "voice": {"color": "#F8B195", "hubs": [], "bridges": []},
            "api": {"color": "#C5E99B", "hubs": [], "bridges": []},
            "tools": {"color": "#D4A5A5", "hubs": [], "bridges": []},
            "features": {"color": "#9A8C98", "hubs": [], "bridges": []},
        }
        self.connections = []
        self.golden_trio_status = {
            "seedra": None,
            "symbolic_language": None,
            "shared_ethics": None,
            "trio_orchestrator": None,
            "dast_core": None,
            "abas_core": None,
            "nias_core": None,
        }

    def analyze(self) -> Dict[str, any]:
        """Main analysis method"""
        print("🔍 Discovering system components...")
        self._discover_components()

        print("🔗 Analyzing connections...")
        self._analyze_connections()

        print("🏆 Checking Golden Trio implementation...")
        self._check_golden_trio_status()

        print("📊 Generating connectivity report...")
        report = self._generate_report()

        print("🎨 Creating visualization...")
        self._create_visualization(report)

        return report

    def _discover_components(self):
        """Discover hubs and bridges in the system"""
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)

            for file in files:
                if file.endswith(".py"):
                    file_path = root_path / file
                    rel_path = file_path.relative_to(self.root_path)

                    # Identify system
                    system = self._identify_system(rel_path)
                    if not system:
                        continue

                    # Check if it's a hub
                    if "hub" in file.lower() and system in self.systems:
                        self.systems[system]["hubs"].append(
                            {
                                "name": file[:-3],
                                "path": str(rel_path),
                                "status": (
                                    "active"
                                    if self._check_file_active(file_path)
                                    else "inactive"
                                ),
                            }
                        )

                    # Check if it's a bridge
                    elif "bridge" in file.lower():
                        # Identify connected systems
                        connected_systems = self._identify_bridge_connections(
                            file, str(rel_path)
                        )
                        if len(connected_systems) >= 2:
                            self.connections.append(
                                {
                                    "type": "bridge",
                                    "name": file[:-3],
                                    "path": str(rel_path),
                                    "systems": connected_systems,
                                    "status": (
                                        "active"
                                        if self._check_file_active(file_path)
                                        else "inactive"
                                    ),
                                }
                            )

    def _identify_system(self, path: Path) -> str:
        """Identify which system a file belongs to"""
        parts = path.parts

        # Direct mapping
        for part in parts:
            if part in self.systems:
                return part

        # Check for core subdirectories
        if "core" in parts:
            # Check for specific core subsystems
            if "nias" in str(path).lower():
                return "nias"
            elif "dast" in str(path).lower():
                return "dast"
            elif "abas" in str(path).lower():
                return "abas"
            elif "safety" in str(path).lower():
                return "safety"
            elif "interfaces" in parts:
                # Check subdirectories
                for part in parts:
                    if part in ["nias", "dast", "abas"]:
                        return part
            return "core"

        # Check path string
        path_str = str(path).lower()
        for system in self.systems:
            if system in path_str:
                return system

        return None

    def _identify_bridge_connections(self, filename: str, filepath: str) -> List[str]:
        """Identify which systems a bridge connects"""
        connected = []

        # Check filename
        name_lower = filename.lower()
        for system in self.systems:
            if system in name_lower:
                connected.append(system)

        # Special cases
        if "consciousness_quantum" in name_lower:
            connected = ["consciousness", "quantum"]
        elif "memory_learning" in name_lower:
            connected = ["memory", "learning"]
        elif "nias_dream" in name_lower:
            connected = ["nias", "dream"]
        elif "bio_symbolic" in name_lower:
            connected = ["bio", "symbolic"]
        elif "core_consciousness" in name_lower:
            connected = ["core", "consciousness"]
        elif "core_safety" in name_lower:
            connected = ["core", "safety"]
        elif "safety_quantum" in name_lower:
            connected = ["safety", "quantum"]
        elif "safety_memory" in name_lower:
            connected = ["safety", "memory"]
        elif "safety_core" in name_lower:
            connected = ["safety", "core"]

        return list(set(connected))

    def _check_file_active(self, file_path: Path) -> bool:
        """Check if a file is actively used (has imports)"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for imports to/from this file
            has_imports = bool(re.search(r"^\s*(import|from)", content, re.MULTILINE))

            # Check file size (very small files might be stubs)
            if file_path.stat().st_size < 100:
                return False

            return has_imports
        except:
            return False

    def _analyze_connections(self):
        """Analyze inter-system connections"""
        # Look for import statements that cross system boundaries
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    source_system = self._identify_system(
                        file_path.relative_to(self.root_path)
                    )

                    if source_system:
                        try:
                            with open(file_path, encoding="utf-8") as f:
                                content = f.read()

                            # Find imports
                            import_pattern = (
                                r"^\s*(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)"
                            )
                            for match in re.finditer(
                                import_pattern, content, re.MULTILINE
                            ):
                                imported = match.group(1)
                                target_system = None

                                # Check if import crosses system boundary
                                for system in self.systems:
                                    if system != source_system and system in imported:
                                        target_system = system
                                        break

                                if target_system:
                                    self.connections.append(
                                        {
                                            "type": "import",
                                            "source": source_system,
                                            "target": target_system,
                                            "file": str(
                                                file_path.relative_to(self.root_path)
                                            ),
                                        }
                                    )
                        except:
                            pass

    def _check_golden_trio_status(self):
        """Check implementation status of Golden Trio components"""
        # Check for Phase 1 components
        phase1_files = {
            "seedra": "ethics/seedra/seedra_core.py",
            "symbolic_language": "symbolic/core/symbolic_language.py",
            "shared_ethics": "ethics/core/shared_ethics_engine.py",
            "trio_orchestrator": "orchestration/golden_trio/trio_orchestrator.py",
        }

        for component, path in phase1_files.items():
            full_path = self.root_path / path
            if full_path.exists():
                size = full_path.stat().st_size
                self.golden_trio_status[component] = {
                    "status": "implemented" if size > 1000 else "stub",
                    "path": path,
                    "size": size,
                }
            else:
                self.golden_trio_status[component] = {
                    "status": "missing",
                    "path": path,
                    "size": 0,
                }

        # Check for Phase 2 core engines
        phase2_patterns = {
            "dast_core": [
                "dast/core/dast_engine.py",
                "dast/core/engine.py",
                "orchestration/security/dast/engine.py",
            ],
            "abas_core": [
                "abas/core/abas_engine.py",
                "abas/core/engine.py",
                "core/interfaces/as_agent/sys/abas/abas.py",
            ],
            "nias_core": [
                "nias/core/nias_engine.py",
                "nias/core/engine.py",
                "core/interfaces/as_agent/sys/nias/nias_core.py",
            ],
        }

        for component, paths in phase2_patterns.items():
            found = False
            for path in paths:
                full_path = self.root_path / path
                if full_path.exists():
                    size = full_path.stat().st_size
                    self.golden_trio_status[component] = {
                        "status": "partial" if size > 500 else "stub",
                        "path": path,
                        "size": size,
                    }
                    found = True
                    break

            if not found:
                self.golden_trio_status[component] = {
                    "status": "missing",
                    "path": paths[0],
                    "size": 0,
                }

    def _generate_report(self) -> Dict[str, any]:
        """Generate connectivity report"""
        # Count connections by type
        bridge_connections = [c for c in self.connections if c.get("type") == "bridge"]
        import_connections = [c for c in self.connections if c.get("type") == "import"]

        # System statistics
        system_stats = {}
        for system, info in self.systems.items():
            active_hubs = [h for h in info["hubs"] if h["status"] == "active"]

            # Count incoming/outgoing connections
            incoming = sum(1 for c in import_connections if c.get("target") == system)
            outgoing = sum(1 for c in import_connections if c.get("source") == system)

            system_stats[system] = {
                "total_hubs": len(info["hubs"]),
                "active_hubs": len(active_hubs),
                "incoming_connections": incoming,
                "outgoing_connections": outgoing,
                "hub_names": [h["name"] for h in active_hubs],
            }

        # Find isolated systems
        isolated_systems = []
        for system, stats in system_stats.items():
            if (
                stats["incoming_connections"] == 0
                and stats["outgoing_connections"] == 0
            ):
                isolated_systems.append(system)

        # Golden Trio implementation progress
        phase1_complete = all(
            status["status"] == "implemented"
            for key, status in self.golden_trio_status.items()
            if key
            in ["seedra", "symbolic_language", "shared_ethics", "trio_orchestrator"]
        )

        phase2_progress = sum(
            1
            for key, status in self.golden_trio_status.items()
            if key.endswith("_core") and status["status"] in ["partial", "implemented"]
        )

        return {
            "summary": {
                "total_systems": len(self.systems),
                "total_hubs": sum(len(info["hubs"]) for info in self.systems.values()),
                "active_hubs": sum(
                    len([h for h in info["hubs"] if h["status"] == "active"])
                    for info in self.systems.values()
                ),
                "total_bridges": len(bridge_connections),
                "active_bridges": len(
                    [b for b in bridge_connections if b["status"] == "active"]
                ),
                "total_connections": len(self.connections),
                "isolated_systems": isolated_systems,
            },
            "golden_trio": {
                "phase1_complete": phase1_complete,
                "phase2_progress": f"{phase2_progress}/3",
                "status": self.golden_trio_status,
            },
            "systems": system_stats,
            "bridges": bridge_connections,
            "top_connected_systems": sorted(
                system_stats.items(),
                key=lambda x: x[1]["incoming_connections"]
                + x[1]["outgoing_connections"],
                reverse=True,
            )[:10],
        }

    def _create_visualization(self, report: Dict[str, any]):
        """Create HTML visualization of system connectivity"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LUKHAS System Connectivity</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        #network {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            background-color: white;
        }}
        .info-panel {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .golden-trio {{
            background: #f0f8ff;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .status-implemented {{ color: #28a745; font-weight: bold; }}
        .status-partial {{ color: #ffc107; font-weight: bold; }}
        .status-missing {{ color: #dc3545; font-weight: bold; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
    </style>
</head>
<body>
    <h1>🏗️ LUKHAS System Connectivity Report</h1>

    <div class="info-panel">
        <h2>📊 System Overview</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{report['summary']['total_systems']}</div>
                <div>Total Systems</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['summary']['active_hubs']}/{report['summary']['total_hubs']}</div>
                <div>Active/Total Hubs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['summary']['active_bridges']}/{report['summary']['total_bridges']}</div>
                <div>Active/Total Bridges</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(report['summary']['isolated_systems'])}</div>
                <div>Isolated Systems</div>
            </div>
        </div>
    </div>

    <div class="info-panel golden-trio">
        <h2>🏆 Golden Trio Implementation Status</h2>
        <p><strong>Phase 1 (Foundation):</strong> {'✅ Complete' if report['golden_trio']['phase1_complete'] else '⏳ In Progress'}</p>
        <ul>
"""

        # Add Golden Trio status
        for component, status in report["golden_trio"]["status"].items():
            status_class = f"status-{status['status']}"
            icon = (
                "✅"
                if status["status"] == "implemented"
                else "🔄" if status["status"] == "partial" else "❌"
            )
            html += f"            <li>{component}: <span class='{status_class}'>{icon} {status['status'].upper()}</span> - {status['path']}</li>\n"

        html += f"""
        </ul>
        <p><strong>Phase 2 (Core Engines):</strong> {report['golden_trio']['phase2_progress']} Complete</p>
    </div>

    <div class="info-panel">
        <h2>🔗 System Connectivity Graph</h2>
        <div id="network"></div>
    </div>

    <div class="info-panel">
        <h2>📈 Top Connected Systems</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f8f9fa;">
                <th style="padding: 10px; text-align: left;">System</th>
                <th style="padding: 10px; text-align: center;">Active Hubs</th>
                <th style="padding: 10px; text-align: center;">Incoming</th>
                <th style="padding: 10px; text-align: center;">Outgoing</th>
                <th style="padding: 10px; text-align: center;">Total Connections</th>
            </tr>
"""

        # Add top connected systems
        for system, stats in report["top_connected_systems"]:
            total = stats["incoming_connections"] + stats["outgoing_connections"]
            html += f"""
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 10px;"><strong>{system}</strong></td>
                <td style="padding: 10px; text-align: center;">{stats['active_hubs']}</td>
                <td style="padding: 10px; text-align: center;">{stats['incoming_connections']}</td>
                <td style="padding: 10px; text-align: center;">{stats['outgoing_connections']}</td>
                <td style="padding: 10px; text-align: center;"><strong>{total}</strong></td>
            </tr>
"""

        html += """
        </table>
    </div>

    <script>
        // Create nodes
        var nodes = new vis.DataSet([
"""

        # Add nodes for each system
        node_id = 1
        node_map = {}
        for system, info in self.systems.items():
            stats = report["systems"].get(system, {})
            size = 20 + (stats.get("active_hubs", 0) * 5)

            # Special styling for Golden Trio
            if system in ["dast", "abas", "nias"]:
                size += 20
                info["color"] = "#FFD700"  # Gold color

            node_map[system] = node_id
            html += f"""            {{id: {node_id}, label: '{system}\\n({stats.get("active_hubs", 0)} hubs)', color: '{info["color"]}', size: {size}}},\n"""
            node_id += 1

        html += """        ]);

        // Create edges
        var edges = new vis.DataSet([
"""

        # Add edges for bridges
        edge_id = 1
        for bridge in report["bridges"]:
            if len(bridge["systems"]) >= 2 and bridge["status"] == "active":
                system1 = bridge["systems"][0]
                system2 = bridge["systems"][1]
                if system1 in node_map and system2 in node_map:
                    html += f"""            {{id: {edge_id}, from: {node_map[system1]}, to: {node_map[system2]}, width: 3, color: '#666'}},\n"""
                    edge_id += 1

        html += """        ]);

        // Create network
        var container = document.getElementById('network');
        var data = {
            nodes: nodes,
            edges: edges
        };
        var options = {
            nodes: {
                shape: 'dot',
                font: {
                    size: 14,
                    color: '#000'
                },
                borderWidth: 2
            },
            edges: {
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                barnesHut: {
                    gravitationalConstant: -8000,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        };
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

        # Save visualization
        output_file = (
            self.root_path / "analysis-tools" / "connectivity_visualization.html"
        )
        with open(output_file, "w") as f:
            f.write(html)

        print(f"📊 Visualization saved to: {output_file}")


def main():
    repo_root = Path(__file__).parent.parent

    visualizer = ConnectivityVisualizer(repo_root)
    report = visualizer.analyze()

    # Save report
    output_file = repo_root / "analysis-tools" / "connectivity_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("🔗 CONNECTIVITY ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Systems: {report['summary']['total_systems']}")
    print(
        f"Active Hubs: {report['summary']['active_hubs']} / {report['summary']['total_hubs']}"
    )
    print(
        f"Active Bridges: {report['summary']['active_bridges']} / {report['summary']['total_bridges']}"
    )
    print(f"Isolated Systems: {report['summary']['isolated_systems']}")

    print("\n🏆 GOLDEN TRIO STATUS:")
    print(
        f"Phase 1 (Foundation): {'✅ COMPLETE' if report['golden_trio']['phase1_complete'] else '⏳ In Progress'}"
    )
    print(
        f"Phase 2 (Core Engines): {report['golden_trio']['phase2_progress']} Complete"
    )

    print("\n📈 TOP CONNECTED SYSTEMS:")
    for system, stats in report["top_connected_systems"][:5]:
        total = stats["incoming_connections"] + stats["outgoing_connections"]
        print(f"  - {system}: {total} connections ({stats['active_hubs']} active hubs)")

    print(f"\n✅ Full report saved to: {output_file}")


if __name__ == "__main__":
    main()
