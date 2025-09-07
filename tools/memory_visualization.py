"""
Memory Visualization Framework for LUKHAS AI
============================================
Provides visualization tools for memory folds, consciousness states, and data flows.
Works with or without external visualization libraries (matplotlib, plotly, etc.).
"""
import streamlit as st

import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Import dashboard alternatives if available
try:
    from .dashboard_alternatives import SimpleDashboard

    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MemoryNode:
    """Represents a single memory node for visualization"""

    node_id: str
    x: float
    y: float
    z: float = 0.0
    size: float = 1.0
    color: str = "#4a90e2"
    label: str = ""
    connections: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class MemoryFold:
    """Represents a memory fold structure"""

    fold_id: str
    nodes: list[MemoryNode]
    fold_type: str = "standard"
    emotional_valence: float = 0.0
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryVisualizer:
    """
    Core memory visualization system.
    Provides multiple output formats depending on available libraries.
    """

    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.folds: dict[str, MemoryFold] = {}
        self.visualization_history: list[dict[str, Any]] = []

        # Visualization settings
        self.default_colors = {
            "positive": "#4CAF50",
            "negative": "#F44336",
            "neutral": "#9E9E9E",
            "important": "#FF9800",
            "connection": "#2196F3",
        }

        # Dashboard integration
        self.dashboard: Optional[SimpleDashboard] = None
        if DASHBOARD_AVAILABLE:
            self.dashboard = SimpleDashboard("Memory Visualization")

        self.logger = logging.getLogger("memory.visualizer")
        self.logger.info(
            f"Memory visualizer initialized (matplotlib: {MATPLOTLIB_AVAILABLE}, plotly: {PLOTLY_AVAILABLE})"
        )

    def add_memory_fold(self, fold: MemoryFold) -> None:
        """Add a memory fold to the visualization system"""
        self.folds[fold.fold_id] = fold
        self.logger.debug(f"Added memory fold: {fold.fold_id} with {len(fold.nodes)} nodes")

        # Update dashboard if available
        if self.dashboard:
            self.dashboard.add_metric("Total Folds", len(self.folds), "folds")
            self.dashboard.add_log(f"Added memory fold: {fold.fold_id}")

    def create_sample_fold(self, fold_id: str, num_nodes: int = 10) -> MemoryFold:
        """Create a sample memory fold for demonstration"""
        nodes = []

        for i in range(num_nodes):
            # Create nodes in a rough cluster
            angle = (2 * math.pi * i) / num_nodes
            radius = random.uniform(0.5, 2.0)

            node = MemoryNode(
                node_id=f"node_{i}",
                x=radius * math.cos(angle) + random.uniform(-0.2, 0.2),
                y=radius * math.sin(angle) + random.uniform(-0.2, 0.2),
                z=random.uniform(-0.5, 0.5),
                size=random.uniform(0.5, 2.0),
                color=random.choice(list(self.default_colors.values())),
                label=f"Memory {i}",
                metadata={"importance": random.uniform(0.1, 1.0)},
            )

            # Add some random connections
            if i > 0:
                num_connections = random.randint(0, min(3, i))
                connections = random.sample([f"node_{j}" for j in range(i)], num_connections)
                node.connections = connections

            nodes.append(node)

        fold = MemoryFold(
            fold_id=fold_id,
            nodes=nodes,
            fold_type="demonstration",
            emotional_valence=random.uniform(-1.0, 1.0),
            importance=random.uniform(0.3, 1.0),
        )

        return fold

    def visualize_fold_2d(self, fold_id: str, save_path: Optional[str] = None) -> Optional[str]:
        """Create 2D visualization of a memory fold"""
        if fold_id not in self.folds:
            self.logger.error(f"Fold {fold_id} not found")
            return None

        fold = self.folds[fold_id]

        # Try matplotlib first
        if MATPLOTLIB_AVAILABLE:
            return self._visualize_fold_matplotlib(fold, save_path)

        # Try plotly
        if PLOTLY_AVAILABLE:
            return self._visualize_fold_plotly(fold, save_path)

        # Fallback to ASCII art
        return self._visualize_fold_ascii(fold, save_path)

    def visualize_fold_3d(self, fold_id: str, save_path: Optional[str] = None) -> Optional[str]:
        """Create 3D visualization of a memory fold"""
        if fold_id not in self.folds:
            self.logger.error(f"Fold {fold_id} not found")
            return None

        fold = self.folds[fold_id]

        # Try plotly for 3D (best option)
        if PLOTLY_AVAILABLE:
            return self._visualize_fold_plotly_3d(fold, save_path)

        # Try matplotlib 3D
        if MATPLOTLIB_AVAILABLE:
            return self._visualize_fold_matplotlib_3d(fold, save_path)

        # Fallback to 2D projection
        self.logger.warning("3D visualization not available, using 2D projection")
        return self.visualize_fold_2d(fold_id, save_path)

    def create_memory_dashboard(self) -> Optional[str]:
        """Create a live memory dashboard"""
        if not self.dashboard:
            self.logger.error("Dashboard not available")
            return None

        # Update dashboard with current memory statistics
        total_nodes = sum(len(fold.nodes) for fold in self.folds.values())
        self.dashboard.add_metric("Total Nodes", total_nodes, "nodes")
        self.dashboard.add_metric("Total Folds", len(self.folds), "folds")

        # Add fold distribution chart
        fold_sizes = [len(fold.nodes) for fold in self.folds.values()]
        if fold_sizes:
            chart_data = [{"fold": f"Fold {i + 1}", "nodes": size} for i, size in enumerate(fold_sizes)]
            self.dashboard.add_chart(
                "fold_distribution",
                "bar",
                chart_data,
                "Memory Fold Distribution",
                "fold",
                "nodes",
            )

        # Start dashboard server
        self.dashboard.start_server()
        return self.dashboard.get_url()

    def export_fold_data(self, fold_id: str, format: str = "json") -> Optional[str]:
        """Export fold data in various formats"""
        if fold_id not in self.folds:
            self.logger.error(f"Fold {fold_id} not found")
            return None

        fold = self.folds[fold_id]

        if format.lower() == "json":
            return self._export_fold_json(fold)
        elif format.lower() == "csv":
            return self._export_fold_csv(fold)
        else:
            self.logger.error(f"Unsupported export format: {format}")
            return None

    def _visualize_fold_matplotlib(self, fold: MemoryFold, save_path: Optional[str] = None) -> str:
        """Create matplotlib visualization"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot nodes
        for node in fold.nodes:
            ax.scatter(node.x, node.y, s=node.size * 100, c=node.color, alpha=0.7)
            if node.label:
                ax.annotate(
                    node.label,
                    (node.x, node.y),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                )

        # Plot connections
        for node in fold.nodes:
            for conn_id in node.connections:
                conn_node = next((n for n in fold.nodes if n.node_id == conn_id), None)
                if conn_node:
                    ax.plot(
                        [node.x, conn_node.x],
                        [node.y, conn_node.y],
                        "b-",
                        alpha=0.3,
                        linewidth=1,
                    )

        ax.set_title(f"Memory Fold: {fold.fold_id}")
        ax.set_xlabel("X Position")
        ax.set_ylabel("Y Position")
        ax.grid(True, alpha=0.3)

        # Save or show
        output_path = self.output_dir / save_path if save_path else self.output_dir / f"fold_{fold.fold_id}_2d.png"

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        self.logger.info(f"Saved matplotlib visualization: {output_path}")
        return str(output_path)

    def _visualize_fold_plotly(self, fold: MemoryFold, save_path: Optional[str] = None) -> str:
        """Create plotly visualization"""
        fig = go.Figure()

        # Add nodes
        node_x = [node.x for node in fold.nodes]
        node_y = [node.y for node in fold.nodes]
        node_colors = [node.color for node in fold.nodes]
        node_sizes = [node.size * 20 for node in fold.nodes]
        node_labels = [node.label or node.node_id for node in fold.nodes]

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                marker=dict(size=node_sizes, color=node_colors, opacity=0.7),
                text=node_labels,
                textposition="top center",
                name="Memory Nodes",
            )
        )

        # Add connections
        for node in fold.nodes:
            for conn_id in node.connections:
                conn_node = next((n for n in fold.nodes if n.node_id == conn_id), None)
                if conn_node:
                    fig.add_trace(
                        go.Scatter(
                            x=[node.x, conn_node.x],
                            y=[node.y, conn_node.y],
                            mode="lines",
                            line=dict(color="blue", width=1, dash="dash"),
                            opacity=0.3,
                            showlegend=False,
                        )
                    )

        fig.update_layout(
            title=f"Memory Fold: {fold.fold_id}",
            xaxis_title="X Position",
            yaxis_title="Y Position",
            showlegend=True,
        )

        # Save
        output_path = self.output_dir / save_path if save_path else self.output_dir / f"fold_{fold.fold_id}_2d.html"

        fig.write_html(output_path)

        self.logger.info(f"Saved plotly visualization: {output_path}")
        return str(output_path)

    def _visualize_fold_plotly_3d(self, fold: MemoryFold, save_path: Optional[str] = None) -> str:
        """Create 3D plotly visualization"""
        fig = go.Figure()

        # Add 3D nodes
        node_x = [node.x for node in fold.nodes]
        node_y = [node.y for node in fold.nodes]
        node_z = [node.z for node in fold.nodes]
        node_colors = [node.color for node in fold.nodes]
        node_sizes = [node.size * 10 for node in fold.nodes]
        node_labels = [node.label or node.node_id for node in fold.nodes]

        fig.add_trace(
            go.Scatter3d(
                x=node_x,
                y=node_y,
                z=node_z,
                mode="markers+text",
                marker=dict(size=node_sizes, color=node_colors, opacity=0.8),
                text=node_labels,
                name="Memory Nodes",
            )
        )

        # Add 3D connections
        for node in fold.nodes:
            for conn_id in node.connections:
                conn_node = next((n for n in fold.nodes if n.node_id == conn_id), None)
                if conn_node:
                    fig.add_trace(
                        go.Scatter3d(
                            x=[node.x, conn_node.x],
                            y=[node.y, conn_node.y],
                            z=[node.z, conn_node.z],
                            mode="lines",
                            line=dict(color="blue", width=2),
                            opacity=0.4,
                            showlegend=False,
                        )
                    )

        fig.update_layout(
            title=f"3D Memory Fold: {fold.fold_id}",
            scene=dict(
                xaxis_title="X Position",
                yaxis_title="Y Position",
                zaxis_title="Z Position",
            ),
        )

        # Save
        output_path = self.output_dir / save_path if save_path else self.output_dir / f"fold_{fold.fold_id}_3d.html"

        fig.write_html(output_path)

        self.logger.info(f"Saved 3D plotly visualization: {output_path}")
        return str(output_path)

    def _visualize_fold_matplotlib_3d(self, fold: MemoryFold, save_path: Optional[str] = None) -> str:
        """Create 3D matplotlib visualization"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Plot 3D nodes
        for node in fold.nodes:
            ax.scatter(node.x, node.y, node.z, s=node.size * 100, c=node.color, alpha=0.7)

        # Plot 3D connections
        for node in fold.nodes:
            for conn_id in node.connections:
                conn_node = next((n for n in fold.nodes if n.node_id == conn_id), None)
                if conn_node:
                    ax.plot(
                        [node.x, conn_node.x],
                        [node.y, conn_node.y],
                        [node.z, conn_node.z],
                        "b-",
                        alpha=0.3,
                        linewidth=1,
                    )

        ax.set_title(f"3D Memory Fold: {fold.fold_id}")
        ax.set_xlabel("X Position")
        ax.set_ylabel("Y Position")
        ax.set_zlabel("Z Position")

        # Save
        output_path = self.output_dir / save_path if save_path else self.output_dir / f"fold_{fold.fold_id}_3d.png"

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        self.logger.info(f"Saved 3D matplotlib visualization: {output_path}")
        return str(output_path)

    def _visualize_fold_ascii(self, fold: MemoryFold, save_path: Optional[str] = None) -> str:
        """Create ASCII art visualization"""
        # Create simple ASCII representation
        width, height = 60, 20
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # Normalize coordinates
        if not fold.nodes:
            ascii_art = "Empty fold"
        else:
            min_x = min(node.x for node in fold.nodes)
            max_x = max(node.x for node in fold.nodes)
            min_y = min(node.y for node in fold.nodes)
            max_y = max(node.y for node in fold.nodes)

            x_range = max_x - min_x if max_x != min_x else 1
            y_range = max_y - min_y if max_y != min_y else 1

            # Place nodes
            for i, node in enumerate(fold.nodes):
                x_pos = int(((node.x - min_x) / x_range) * (width - 1))
                y_pos = int(((node.y - min_y) / y_range) * (height - 1))

                if 0 <= x_pos < width and 0 <= y_pos < height:
                    canvas[y_pos][x_pos] = str(i % 10)

            # Convert to string
            ascii_art = f"Memory Fold: {fold.fold_id}\n"
            ascii_art += "=" * width + "\n"
            for row in canvas:
                ascii_art += "".join(row) + "\n"
            ascii_art += "=" * width

        # Save
        output_path = self.output_dir / save_path if save_path else self.output_dir / f"fold_{fold.fold_id}_ascii.txt"

        with open(output_path, "w") as f:
            f.write(ascii_art)

        self.logger.info(f"Saved ASCII visualization: {output_path}")
        return str(output_path)

    def _export_fold_json(self, fold: MemoryFold) -> str:
        """Export fold as JSON"""
        output_path = self.output_dir / f"fold_{fold.fold_id}_data.json"

        # Convert to serializable format
        fold_data = {
            "fold_id": fold.fold_id,
            "fold_type": fold.fold_type,
            "emotional_valence": fold.emotional_valence,
            "importance": fold.importance,
            "created_at": fold.created_at,
            "metadata": fold.metadata,
            "nodes": [],
        }

        for node in fold.nodes:
            node_data = {
                "node_id": node.node_id,
                "x": node.x,
                "y": node.y,
                "z": node.z,
                "size": node.size,
                "color": node.color,
                "label": node.label,
                "connections": node.connections,
                "metadata": node.metadata,
                "timestamp": node.timestamp,
            }
            fold_data["nodes"].append(node_data)

        with open(output_path, "w") as f:
            json.dump(fold_data, f, indent=2)

        self.logger.info(f"Exported JSON data: {output_path}")
        return str(output_path)

    def _export_fold_csv(self, fold: MemoryFold) -> str:
        """Export fold as CSV"""
        output_path = self.output_dir / f"fold_{fold.fold_id}_nodes.csv"

        with open(output_path, "w") as f:
            # Header
            f.write("node_id,x,y,z,size,color,label,num_connections,timestamp\n")

            # Data rows
            for node in fold.nodes:
                f.write(
                    f"{node.node_id},{node.x},{node.y},{node.z},"
                    f"{node.size},{node.color},{node.label},"
                    f"{len(node.connections)},{node.timestamp}\n"
                )

        self.logger.info(f"Exported CSV data: {output_path}")
        return str(output_path)


# Convenience functions
def create_demo_visualization(output_dir: str = "demo_visualizations") -> str:
    """Create a demonstration memory visualization"""
    visualizer = MemoryVisualizer(output_dir)

    # Create sample folds
    fold1 = visualizer.create_sample_fold("consciousness_fold_1", 15)
    fold2 = visualizer.create_sample_fold("memory_cascade", 20)

    visualizer.add_memory_fold(fold1)
    visualizer.add_memory_fold(fold2)

    # Create visualizations
    viz_paths = []
    viz_paths.append(visualizer.visualize_fold_2d("consciousness_fold_1"))
    viz_paths.append(visualizer.visualize_fold_3d("memory_cascade"))

    # Export data
    viz_paths.append(visualizer.export_fold_data("consciousness_fold_1", "json"))
    viz_paths.append(visualizer.export_fold_data("memory_cascade", "csv"))

    # Create dashboard
    dashboard_url = visualizer.create_memory_dashboard()
    if dashboard_url:
        print(f"Memory dashboard available at: {dashboard_url}")

    return f"Created {len([p for p in viz_paths if p])} visualizations in {output_dir}/"


# Export key components
__all__ = [
    "MATPLOTLIB_AVAILABLE",
    "PLOTLY_AVAILABLE",
    "MemoryFold",
    "MemoryNode",
    "MemoryVisualizer",
    "create_demo_visualization",
]


# Demo usage
if __name__ == "__main__":
    print("Creating demonstration memory visualization...")
    result = create_demo_visualization()
    print(result)

    print("\nVisualization capabilities:")
    print(f"  - Matplotlib: {'✅' if MATPLOTLIB_AVAILABLE else '❌'}")
    print(f"  - Plotly: {'✅' if PLOTLY_AVAILABLE else '❌'}")
    print(f"  - Dashboard: {'✅' if DASHBOARD_AVAILABLE else '❌'}")

    if not MATPLOTLIB_AVAILABLE and not PLOTLY_AVAILABLE:
        print("\nTo enable advanced visualizations, install:")
        print("  pip install matplotlib plotly")
