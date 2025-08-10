#!/usr/bin/env python3
"""
Generate Updated Connectivity Visualization for LUKHAS AGI System
Reflects current state after AGENT 1-4 implementation
"""

from datetime import datetime
from pathlib import Path
from typing import List

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx


class LUKHASConnectivityVisualizer:
    """Generate comprehensive connectivity visualization for LUKHAS AGI"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = (
            root_path / "visualizations" / f"connectivity_{self.timestamp}"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # System colors matching LUKHAS branding
        self.system_colors = {
            "core": "#e74c3c",  # Red - Core infrastructure
            "consciousness": "#9b59b6",  # Purple - Consciousness
            "memory": "#3498db",  # Blue - Memory systems
            "quantum": "#f39c12",  # Orange - Quantum
            "bio": "#2ecc71",  # Green - Bio systems
            "safety": "#34495e",  # Dark gray - Safety
            "learning": "#f1c40f",  # Yellow - Learning
            "orchestration": "#e91e63",  # Pink - Orchestration
            "nias": "#1abc9c",  # Turquoise - NIAS
            "dream": "#8e44ad",  # Dark purple - Dream
            "symbolic": "#16a085",  # Dark turquoise - Symbolic
            "bridge": "#795548",  # Brown - Bridges
            "identity": "#607d8b",  # Blue gray - Identity
        }

        # Current system state after AGENT 1-4 implementation
        self.current_hubs = [
            "core",
            "consciousness",
            "memory",
            "quantum",
            "bio",
            "safety",
            "learning",
            "orchestration",
            "nias",
            "dream",
            "symbolic",
        ]

        self.implemented_bridges = [
            ("core", "consciousness"),
            ("core", "safety"),
            ("consciousness", "quantum"),
            ("memory", "learning"),
            ("bio", "symbolic"),
            ("nias", "dream"),
            ("core", "orchestration"),
            ("identity", "core"),
        ]

        # Service discovery and critical connections
        self.service_discovery_enabled = True
        self.hub_registry_enabled = True
        self.critical_connections_count = 167

    def generate_system_architecture_graph(self):
        """Generate the main system architecture visualization"""
        G = nx.Graph()

        # Add hub nodes
        for hub in self.current_hubs:
            G.add_node(
                hub, node_type="hub", color=self.system_colors.get(hub, "#95a5a6")
            )

        # Add bridge connections
        for source, target in self.implemented_bridges:
            G.add_edge(source, target, edge_type="bridge", weight=2)

        # Add service discovery connections (all hubs connected through service discovery)
        if self.service_discovery_enabled:
            # Service discovery creates a hub-and-spoke pattern with core at center
            for hub in self.current_hubs:
                if hub != "core":
                    G.add_edge("core", hub, edge_type="service_discovery", weight=1)

        return G

    def create_main_visualization(self):
        """Create the main connectivity visualization"""
        G = self.generate_system_architecture_graph()

        # Set up the plot
        plt.figure(figsize=(16, 12))
        plt.style.use("dark_background")

        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

        # Draw edges first (behind nodes)
        # Bridge connections (thick, colored)
        bridge_edges = [
            (u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "bridge"
        ]
        nx.draw_networkx_edges(
            G, pos, edgelist=bridge_edges, edge_color="#f39c12", width=3, alpha=0.8
        )

        # Service discovery connections (thin, gray)
        service_edges = [
            (u, v)
            for u, v, d in G.edges(data=True)
            if d.get("edge_type") == "service_discovery"
        ]
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=service_edges,
            edge_color="#7f8c8d",
            width=1,
            alpha=0.5,
            style="dashed",
        )

        # Draw nodes
        for node in G.nodes():
            color = self.system_colors.get(node, "#95a5a6")
            nx.draw_networkx_nodes(
                G, pos, nodelist=[node], node_color=color, node_size=2000, alpha=0.9
            )

        # Add labels
        nx.draw_networkx_labels(
            G, pos, font_size=10, font_weight="bold", font_color="white"
        )

        # Create title and subtitle
        plt.title(
            "LUKHAS AGI System Connectivity Architecture\nCurrent State After AGENT 1-4 Implementation",
            fontsize=18,
            fontweight="bold",
            color="white",
            pad=20,
        )

        # Create legend
        legend_elements = [
            mpatches.Patch(color="#f39c12", label="Bridge Connections"),
            mpatches.Patch(color="#7f8c8d", label="Service Discovery"),
            mpatches.Patch(color="#e74c3c", label="Core Hub"),
            mpatches.Patch(color="#9b59b6", label="Consciousness Hub"),
            mpatches.Patch(color="#3498db", label="Memory Hub"),
            mpatches.Patch(color="#2ecc71", label="Bio Hub"),
            mpatches.Patch(color="#34495e", label="Safety Hub"),
        ]

        plt.legend(
            handles=legend_elements,
            loc="upper left",
            bbox_to_anchor=(0.02, 0.98),
            framealpha=0.9,
        )

        plt.axis("off")
        plt.tight_layout()

        # Save the visualization
        output_file = self.output_dir / "system_architecture.png"
        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight",
            facecolor="#0a0a0a",
            edgecolor="none",
        )
        plt.close()

        return output_file

    def create_implementation_status_chart(self):
        """Create a chart showing implementation status of each agent"""
        agents = [
            "AGENT 1\nSystem Hubs",
            "AGENT 2\nBridges",
            "AGENT 3\nInit Files",
            "AGENT 4\nConnections",
            "AGENT 5\nEntity Activation",
            "AGENT 6\nTesting",
        ]
        completion = [100, 100, 100, 100, 75, 25]  # Current completion percentages
        colors = ["#2ecc71", "#2ecc71", "#2ecc71", "#2ecc71", "#f39c12", "#e74c3c"]

        plt.figure(figsize=(12, 8))
        plt.style.use("dark_background")

        bars = plt.bar(
            agents, completion, color=colors, alpha=0.8, edgecolor="white", linewidth=2
        )

        # Add percentage labels on bars
        for bar, pct in zip(bars, completion):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{pct}%",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=12,
            )

        plt.title(
            "LUKHAS AGI Implementation Progress\nAgent Completion Status",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
        plt.ylabel("Completion Percentage", fontsize=12, fontweight="bold")
        plt.ylim(0, 110)

        # Add completion status legend
        status_colors = {
            "Complete": "#2ecc71",
            "In Progress": "#f39c12",
            "Planned": "#e74c3c",
        }
        legend_elements = [
            mpatches.Patch(color=color, label=status)
            for status, color in status_colors.items()
        ]
        plt.legend(handles=legend_elements, loc="upper right")

        plt.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

        # Save the chart
        output_file = self.output_dir / "implementation_status.png"
        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight",
            facecolor="#0a0a0a",
            edgecolor="none",
        )
        plt.close()

        return output_file

    def create_connection_metrics_chart(self):
        """Create a chart showing connection metrics"""
        metrics = [
            "Hub\nConnections",
            "Bridge\nConnections",
            "Service\nRegistrations",
            "Critical\nConnections",
            "Entity\nActivations",
        ]
        current_values = [11, 8, 50, 167, 1950]  # Current implementation numbers
        target_values = [11, 8, 50, 167, 2636]  # Target numbers

        x = range(len(metrics))
        width = 0.35

        plt.figure(figsize=(14, 8))
        plt.style.use("dark_background")

        bars1 = plt.bar(
            [i - width / 2 for i in x],
            current_values,
            width,
            label="Current",
            color="#2ecc71",
            alpha=0.8,
        )
        bars2 = plt.bar(
            [i + width / 2 for i in x],
            target_values,
            width,
            label="Target",
            color="#3498db",
            alpha=0.8,
        )

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 20,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

        plt.title(
            "LUKHAS AGI Connection Metrics\nCurrent vs Target Implementation",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
        plt.ylabel("Count", fontsize=12, fontweight="bold")
        plt.xlabel("Connection Type", fontsize=12, fontweight="bold")
        plt.xticks(x, metrics)
        plt.legend()
        plt.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

        # Save the chart
        output_file = self.output_dir / "connection_metrics.png"
        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight",
            facecolor="#0a0a0a",
            edgecolor="none",
        )
        plt.close()

        return output_file

    def generate_html_dashboard(self, image_files: List[Path]):
        """Generate an HTML dashboard with all visualizations"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LUKHAS AGI Connectivity Dashboard - {self.timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #ffffff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            background: linear-gradient(45deg, #e74c3c, #9b59b6, #3498db);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }}

        .subtitle {{
            font-size: 1.2em;
            margin-top: 10px;
            color: #bdc3c7;
        }}

        .timestamp {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 30px;
        }}

        .visualization-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease;
        }}

        .visualization-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        .visualization-card h2 {{
            margin: 0 0 20px 0;
            font-size: 1.5em;
            color: #ecf0f1;
        }}

        .visualization-card img {{
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: rgba(46, 204, 113, 0.1);
            border: 1px solid #2ecc71;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2ecc71;
            margin-bottom: 5px;
        }}

        .stat-label {{
            color: #bdc3c7;
            font-size: 0.9em;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-complete {{ background-color: #2ecc71; }}
        .status-progress {{ background-color: #f39c12; }}
        .status-planned {{ background-color: #e74c3c; }}

        .agent-status {{
            margin: 20px 0;
        }}

        .agent-item {{
            padding: 10px 15px;
            margin: 5px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            display: flex;
            align-items: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>LUKHAS AGI Connectivity Dashboard</h1>
        <div class="subtitle">Real-time System Architecture & Implementation Status</div>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">11</div>
            <div class="stat-label">System Hubs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">8</div>
            <div class="stat-label">Bridge Connections</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">167</div>
            <div class="stat-label">Critical Connections</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">74%</div>
            <div class="stat-label">Entity Activation</div>
        </div>
    </div>

    <div class="agent-status">
        <h2>Implementation Status</h2>
        <div class="agent-item">
            <span class="status-indicator status-complete"></span>
            <strong>AGENT 1: System Hubs</strong> - Complete (11/11 hubs implemented)
        </div>
        <div class="agent-item">
            <span class="status-indicator status-complete"></span>
            <strong>AGENT 2: Bridges</strong> - Complete (8/8 bridges functional)
        </div>
        <div class="agent-item">
            <span class="status-indicator status-complete"></span>
            <strong>AGENT 3: Init Files</strong> - Complete (Service discovery enabled)
        </div>
        <div class="agent-item">
            <span class="status-indicator status-complete"></span>
            <strong>AGENT 4: Critical Connections</strong> - Complete (167/167 connections)
        </div>
        <div class="agent-item">
            <span class="status-indicator status-progress"></span>
            <strong>AGENT 5: Entity Activation</strong> - In Progress (1950/2636 entities)
        </div>
        <div class="agent-item">
            <span class="status-indicator status-planned"></span>
            <strong>AGENT 6: Testing & Validation</strong> - Planned
        </div>
    </div>

    <div class="dashboard">
        <div class="visualization-card">
            <h2>🏗️ System Architecture Overview</h2>
            <img src="system_architecture.png" alt="System Architecture">
        </div>

        <div class="visualization-card">
            <h2>📊 Implementation Progress</h2>
            <img src="implementation_status.png" alt="Implementation Status">
        </div>

        <div class="visualization-card">
            <h2>🔗 Connection Metrics</h2>
            <img src="connection_metrics.png" alt="Connection Metrics">
        </div>
    </div>

    <div style="text-align: center; margin-top: 40px; padding: 20px; color: #7f8c8d;">
        <p>LUKHAS AGI System - Advanced General Intelligence Architecture</p>
        <p>Hub-and-Spoke Integration with Service Discovery</p>
    </div>
</body>
</html>
"""

        html_file = self.output_dir / "index.html"
        with open(html_file, "w") as f:
            f.write(html_content)

        return html_file

    def generate_all_visualizations(self):
        """Generate all connectivity visualizations"""
        print("🎨 Generating LUKHAS AGI Connectivity Visualizations...")
        print(f"📁 Output directory: {self.output_dir}")

        # Generate individual visualizations
        arch_file = self.create_main_visualization()
        print(f"✅ System architecture: {arch_file.name}")

        status_file = self.create_implementation_status_chart()
        print(f"✅ Implementation status: {status_file.name}")

        metrics_file = self.create_connection_metrics_chart()
        print(f"✅ Connection metrics: {metrics_file.name}")

        # Generate HTML dashboard
        image_files = [arch_file, status_file, metrics_file]
        html_file = self.generate_html_dashboard(image_files)
        print(f"✅ HTML dashboard: {html_file.name}")

        print("\n🎉 Connectivity visualizations complete!")
        print(f"🌐 Open: {html_file}")

        return html_file


def main():
    """Main function to generate connectivity visualizations"""
    root_path = Path(__file__).parent.parent
    visualizer = LUKHASConnectivityVisualizer(root_path)
    html_file = visualizer.generate_all_visualizations()

    # Also update the main connectivity visualization in archive
    import shutil

    archive_file = root_path / "archive" / "connectivity_visualization.html"
    if archive_file.exists():
        shutil.copy2(html_file, archive_file)
        print(f"📋 Updated archive: {archive_file}")


if __name__ == "__main__":
    main()
    main()
