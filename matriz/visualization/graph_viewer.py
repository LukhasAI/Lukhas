#!/usr/bin/env python3
"""
MATRIZ Graph Visualization System

A production-ready interactive visualization system for MATRIZ cognitive nodes
and their relationships. Provides comprehensive graph analysis, temporal evolution
tracking, and interactive exploration capabilities.

Features:
- NetworkX graph structure management
- Plotly interactive visualizations
- Color-coded node types and relationships
- Temporal evolution tracking and animation
- Interactive node inspection with detailed metadata
- Multiple layout algorithms (force-directed, hierarchical, circular)
- Export capabilities (HTML, PNG, JSON)
- Real-time graph updates and filtering
- Statistical analysis and metrics
- Production-ready error handling and logging

Author: Claude Code
License: MIT
"""

import json
import logging
import time
import warnings
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, Optional, Union

# Suppress Plotly warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="plotly")

try:
    import networkx as nx
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as e:
    raise ImportError(
        f"Missing required dependencies: {e}. Please install with: pip install networkx plotly pandas numpy"
    ) from e

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NodeTypeConfig:
    """Configuration for MATRIZ node type visualization."""

    # Color scheme for different node types
    COLORS: ClassVar[dict[str, str]] = {
        "SENSORY_IMG": "#FF6B6B",  # Red - visual input
        "SENSORY_AUD": "#4ECDC4",  # Teal - audio input
        "SENSORY_VID": "#45B7D1",  # Blue - video input
        "SENSORY_TOUCH": "#96CEB4",  # Green - touch input
        "EMOTION": "#FFEAA7",  # Yellow - emotional processing
        "INTENT": "#DDA0DD",  # Plum - intentions
        "DECISION": "#FF7675",  # Coral - decision points
        "CONTEXT": "#A29BFE",  # Purple - contextual info
        "MEMORY": "#FD79A8",  # Pink - memory nodes
        "REFLECTION": "#FDCB6E",  # Orange - introspection
        "CAUSAL": "#E17055",  # Brown - causal relationships
        "TEMPORAL": "#00B894",  # Sea green - temporal links
        "AWARENESS": "#00CEC9",  # Cyan - awareness states
        "HYPOTHESIS": "#6C5CE7",  # Violet - hypotheses
        "REPLAY": "#A0A0A0",  # Gray - replay/simulation
        "DRM": "#2D3436",  # Dark gray - memory reconstruction
        "COMPUTATION": "#74B9FF",  # Light blue - mathematical/logical
        "VALIDATION": "#00B4D8",  # Ocean blue - validation results
        "UNKNOWN": "#636E72",  # Steel gray - unknown types
    }

    # Shapes for different node types
    SHAPES: ClassVar[dict[str, str]] = {
        "SENSORY_IMG": "square",
        "SENSORY_AUD": "circle",
        "SENSORY_VID": "diamond",
        "SENSORY_TOUCH": "triangle-up",
        "EMOTION": "star",
        "INTENT": "hexagon",
        "DECISION": "octagon",
        "CONTEXT": "circle",
        "MEMORY": "circle",
        "REFLECTION": "triangle-up",
        "CAUSAL": "circle",
        "TEMPORAL": "circle",
        "AWARENESS": "star",
        "HYPOTHESIS": "diamond",
        "REPLAY": "square",
        "DRM": "triangle-down",
        "COMPUTATION": "circle",
        "VALIDATION": "hexagon",
        "UNKNOWN": "circle",
    }

    # Size scaling based on node importance
    SIZE_MULTIPLIER: ClassVar[dict[str, float]] = {
        "DECISION": 1.5,
        "EMOTION": 1.3,
        "AWARENESS": 1.4,
        "MEMORY": 1.2,
        "COMPUTATION": 1.1,
        "VALIDATION": 1.1,
    }

    @classmethod
    def get_color(cls, node_type: str) -> str:
        """Get color for node type."""
        return cls.COLORS.get(node_type, cls.COLORS["UNKNOWN"])

    @classmethod
    def get_shape(cls, node_type: str) -> str:
        """Get shape for node type."""
        return cls.SHAPES.get(node_type, cls.SHAPES["UNKNOWN"])

    @classmethod
    def get_size_multiplier(cls, node_type: str) -> float:
        """Get size multiplier for node type."""
        return cls.SIZE_MULTIPLIER.get(node_type, 1.0)


class LinkTypeConfig:
    """Configuration for MATRIZ link type visualization."""

    # Colors for different link types
    COLORS: ClassVar[dict[str, str]] = {
        "temporal": "#74B9FF",  # Blue - time-based connections
        "causal": "#E17055",  # Orange-red - cause-effect
        "semantic": "#00B894",  # Green - meaning-based
        "emotional": "#FFEAA7",  # Yellow - emotion-based
        "spatial": "#A29BFE",  # Purple - space-based
        "evidence": "#FD79A8",  # Pink - evidence relationships
        "unknown": "#636E72",  # Gray - unknown relationships
    }

    # Line styles for different link types
    STYLES: ClassVar[dict[str, str]] = {
        "temporal": "solid",
        "causal": "dash",
        "semantic": "dot",
        "emotional": "dashdot",
        "spatial": "solid",
        "evidence": "dash",
        "unknown": "solid",
    }

    # Width scaling based on link importance
    WIDTH_MULTIPLIER: ClassVar[dict[str, float]] = {
        "causal": 1.5,
        "temporal": 1.3,
        "evidence": 1.2,
        "emotional": 1.1,
    }

    @classmethod
    def get_color(cls, link_type: str) -> str:
        """Get color for link type."""
        return cls.COLORS.get(link_type, cls.COLORS["unknown"])

    @classmethod
    def get_style(cls, link_type: str) -> str:
        """Get line style for link type."""
        return cls.STYLES.get(link_type, cls.STYLES["unknown"])

    @classmethod
    def get_width_multiplier(cls, link_type: str) -> float:
        """Get width multiplier for link type."""
        return cls.WIDTH_MULTIPLIER.get(link_type, 1.0)


class RenderingHelper:
    """Helper class for rendering MATRIZ graphs."""

    def __init__(self, viewer: "MATRIZGraphViewer"):
        """
        Initialize the rendering helper.

        Args:
            viewer: The MATRIZGraphViewer instance.
        """
        self.viewer = viewer

    def add_edges_to_plot(
        self, fig: go.Figure, pos: dict, show_weights: bool, highlight_critical: bool
    ) -> None:
        """Add edges to the plot."""
        edge_traces = defaultdict(list)

        for source, target, data in self.viewer.graph.edges(data=True):
            if source not in pos or target not in pos:
                continue

            link_type = data.get("link_type", "unknown")
            weight = data.get("weight", 1.0)

            x0, y0 = pos[source]
            x1, y1 = pos[target]

            # Determine line properties
            color = LinkTypeConfig.get_color(link_type)
            width = 1 + (weight - 0.5) * 2 if show_weights else 1
            width *= LinkTypeConfig.get_width_multiplier(link_type)

            if highlight_critical and weight > 0.8:
                width *= 1.5
                color = "#E74C3C"

            trace_key = (link_type, width, color)
            edge_traces[trace_key].extend([x0, x1, None])
            edge_traces[trace_key].extend([y0, y1, None])

        # Add edge traces
        for (_link_type, width, color), coords in edge_traces.items():
            if len(coords) >= 6:  # At least one edge
                x_coords = coords[::3]  # Every 3rd element starting from 0
                y_coords = coords[1::3]  # Every 3rd element starting from 1

                fig.add_trace(
                    go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode="lines",
                        line={"width": width, "color": color},
                        hoverinfo="none",
                        showlegend=False,
                    )
                )

    def add_nodes_to_plot(self, fig: go.Figure, pos: dict, show_info: bool) -> None:
        """Add nodes to the plot grouped by type."""
        node_traces = defaultdict(
            lambda: {"x": [], "y": [], "text": [], "hovertext": [], "size": []}
        )

        for node_id, data in self.viewer.graph.nodes(data=True):
            if node_id not in pos:
                continue

            x, y = pos[node_id]
            node_type = data.get("type", "UNKNOWN")

            node_traces[node_type]["x"].append(x)
            node_traces[node_type]["y"].append(y)
            node_traces[node_type]["text"].append(data.get("label", node_id[:8]))
            node_traces[node_type]["size"].append(data.get("size", 20))

            if show_info:
                hover_text = self.create_hover_text(node_id, data)
                node_traces[node_type]["hovertext"].append(hover_text)

        # Add node traces
        for node_type, trace_data in node_traces.items():
            if trace_data["x"]:  # Only add if there are nodes
                fig.add_trace(
                    go.Scatter(
                        x=trace_data["x"],
                        y=trace_data["y"],
                        mode="markers+text" if self.viewer.show_labels else "markers",
                        marker={
                            "size": trace_data["size"],
                            "color": NodeTypeConfig.get_color(node_type),
                            "symbol": NodeTypeConfig.get_shape(node_type),
                            "line": {"width": 1, "color": "white"},
                        },
                        text=trace_data["text"] if self.viewer.show_labels else None,
                        textposition="middle center",
                        textfont={"size": 8, "color": "white"},
                        hovertext=trace_data["hovertext"] if show_info else None,
                        hoverinfo="text" if show_info else "none",
                        name=node_type,
                        showlegend=True,
                    )
                )

    def create_hover_text(self, node_id: str, data: dict) -> str:
        """Create detailed hover text for a node."""
        lines = [
            f"<b>{data.get('type', 'Unknown')}</b>",
            f"ID: {node_id[:12]}...",
            f"Confidence: {data.get('confidence', 0):.3f}",
            f"Salience: {data.get('salience', 0):.3f}",
        ]

        if "valence" in data and data["valence"] is not None:
            lines.append(f"Valence: {data['valence']:.3f}")

        if "arousal" in data and data["arousal"] is not None:
            lines.append(f"Arousal: {data['arousal']:.3f}")

        # Add connection info
        in_degree = self.viewer.graph.in_degree(node_id)
        out_degree = self.viewer.graph.out_degree(node_id)
        lines.append(f"Connections: {in_degree} in, {out_degree} out")

        return "<br>".join(lines)

    def create_node_trace(
        self, graph: nx.DiGraph, pos: dict, show_info: bool
    ) -> Optional[go.Scatter]:
        """Create a single node trace for animation frames."""
        if not graph.nodes():
            return None

        x_coords = []
        y_coords = []
        colors = []
        sizes = []
        hover_texts = []

        for node_id, data in graph.nodes(data=True):
            if node_id not in pos:
                continue

            x, y = pos[node_id]
            x_coords.append(x)
            y_coords.append(y)
            colors.append(NodeTypeConfig.get_color(data.get("type", "UNKNOWN")))
            sizes.append(data.get("size", 20))

            if show_info:
                hover_texts.append(self.create_hover_text(node_id, data))

        if not x_coords:
            return None

        return go.Scatter(
            x=x_coords,
            y=y_coords,
            mode="markers",
            marker={
                "size": sizes,
                "color": colors,
                "line": {"width": 1, "color": "white"},
            },
            hovertext=hover_texts if show_info else None,
            hoverinfo="text" if show_info else "none",
            showlegend=False,
        )

    def create_edge_trace(self, graph: nx.DiGraph, pos: dict) -> Optional[go.Scatter]:
        """Create a single edge trace for animation frames."""
        if not graph.edges():
            return None

        x_coords = []
        y_coords = []

        for source, target in graph.edges():
            if source not in pos or target not in pos:
                continue

            x0, y0 = pos[source]
            x1, y1 = pos[target]

            x_coords.extend([x0, x1, None])
            y_coords.extend([y0, y1, None])

        if not x_coords:
            return None

        return go.Scatter(
            x=x_coords,
            y=y_coords,
            mode="lines",
            line={"width": 1, "color": "#7F8C8D"},
            hoverinfo="none",
            showlegend=False,
        )

    def add_node_type_legend(self, fig: go.Figure) -> None:
        """Add a legend showing node type colors."""
        # This is handled automatically by the node traces

    def create_empty_plot(self, title: str) -> go.Figure:
        """Create an empty plot with instructions."""
        fig = go.Figure()

        fig.add_annotation(
            text="No data to display<br>Add MATRIZ nodes to visualize the graph",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            xanchor="center",
            yanchor="middle",
            font={"size": 16, "color": "#7F8C8D"},
            showarrow=False,
        )

        fig.update_layout(
            title=title,
            width=self.viewer.width,
            height=self.viewer.height,
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        return fig

    def create_error_plot(self, error_message: str) -> go.Figure:
        """Create an error plot."""
        fig = go.Figure()

        fig.add_annotation(
            text=f"Error: {error_message}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            xanchor="center",
            yanchor="middle",
            font={"size": 16, "color": "#E74C3C"},
            showarrow=False,
        )

        fig.update_layout(
            title="Visualization Error",
            width=self.viewer.width,
            height=self.viewer.height,
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        return fig


class MATRIZGraphViewer:
    """
    Production-ready interactive visualization system for MATRIZ cognitive graphs.
    """

    def __init__(
        self,
        width: int = 1200,
        height: int = 800,
        show_labels: bool = True,
        enable_physics: bool = True,
    ):
        self.width = width
        self.height = height
        self.show_labels = show_labels
        self.enable_physics = enable_physics
        self.graph = nx.DiGraph()
        self.node_data = {}
        self.temporal_snapshots = {}
        self.layout_cache = {}
        self.selected_nodes = set()
        self.filtered_node_types = set()
        self.filtered_link_types = set()
        self.time_range = None
        self._analysis_cache = {}
        self._cache_timestamp = 0
        self.renderer = RenderingHelper(self)
        logger.info(f"Initialized MATRIZ Graph Viewer ({width}x{height})")

    def add_node(self, matriz_node: dict[str, Any]) -> None:
        if not self._validate_matriz_node(matriz_node):
            raise ValueError("Invalid MATRIZ node format")
        node_id = matriz_node["id"]
        self.node_data[node_id] = matriz_node
        self._add_node_to_graph(matriz_node)
        for link in matriz_node.get("links", []):
            self._add_link(node_id, link)
        self._update_temporal_snapshots(node_id, matriz_node["timestamps"].get("created_ts"))
        self._invalidate_cache()
        logger.debug(f"Added node {node_id[:8]}... (type: {matriz_node['type']})")

    def add_nodes_batch(self, matriz_nodes: list[dict[str, Any]]) -> tuple[int, int]:
        successful, failed = 0, 0
        for node in matriz_nodes:
            try:
                self.add_node(node)
                successful += 1
            except Exception as e:
                logger.warning(f"Failed to add node {node.get('id', 'unknown')}: {e}")
                failed += 1
        logger.info(f"Batch add complete: {successful} success, {failed} failed")
        return successful, failed

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self.graph:
            return False
        self.graph.remove_node(node_id)
        if node_id in self.node_data:
            del self.node_data[node_id]
        self.selected_nodes.discard(node_id)
        self._invalidate_cache()
        logger.debug(f"Removed node {node_id[:8]}...")
        return True

    def get_node_details(self, node_id: str) -> Optional[dict[str, Any]]:
        return self.node_data.get(node_id)

    def search_nodes(self, **criteria) -> list[str]:
        return [
            node_id
            for node_id, data in self.graph.nodes(data=True)
            if self._node_matches_criteria(node_id, data, criteria)
        ]

    def create_interactive_plot(self, **kwargs) -> go.Figure:
        if not self.graph.nodes():
            return self.renderer.create_empty_plot(kwargs.get("title", "MATRIZ Cognitive Graph"))
        pos = self._compute_layout(kwargs.get("layout", "force_directed"))
        fig = go.Figure()
        self.renderer.add_edges_to_plot(fig, pos, kwargs.get("show_link_weights", False), kwargs.get("highlight_critical_path", False))
        self.renderer.add_nodes_to_plot(fig, pos, kwargs.get("show_node_info", True))
        self._configure_plot_layout(fig, kwargs.get("title", "MATRIZ Cognitive Graph"))
        return fig

    def create_temporal_animation(self, **kwargs) -> go.Figure:
        if not self.temporal_snapshots:
            return self.renderer.create_empty_plot(kwargs.get("title", "MATRIZ Temporal Evolution"))
        timestamps = sorted(self.temporal_snapshots.keys())
        base_pos = self._compute_layout(kwargs.get("layout", "force_directed"))
        frames = [self._create_animation_frame(ts, base_pos, timestamps) for ts in timestamps]
        fig = go.Figure(data=frames[0].data if frames else [], frames=frames)
        self._configure_animation_layout(fig, frames, kwargs.get("time_step_ms", 1000), kwargs.get("title", "MATRIZ Temporal Evolution"))
        return fig

    def create_statistics_dashboard(self) -> go.Figure:
        if not self.graph.nodes():
            return self.renderer.create_empty_plot("Graph Statistics Dashboard")
        fig = make_subplots(
            rows=2,
            cols=3,
            subplot_titles=("Node Type Distribution", "Confidence Distribution", "Salience Distribution", "Link Type Distribution", "Temporal Activity", "Network Metrics"),
            specs=[[{"type": "pie"}, {"type": "histogram"}, {"type": "histogram"}], [{"type": "pie"}, {"type": "scatter"}, {"type": "table"}]]
        )
        self._add_dashboard_traces(fig)
        fig.update_layout(title_text="MATRIZ Graph Statistics Dashboard", showlegend=False)
        return fig

    def calculate_graph_metrics(self) -> dict[str, Union[int, float]]:
        if not self.graph.nodes():
            return {}
        cache_key = "graph_metrics"
        if self._is_cache_valid(cache_key):
            return self._analysis_cache[cache_key]
        metrics = self._compute_graph_metrics()
        self._analysis_cache[cache_key] = metrics
        self._cache_timestamp = time.time()
        return metrics

    def export_graph(self, filepath: Union[str, Path], **kwargs) -> bool:
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            export_graph = self.graph.copy()
            if kwargs.get("include_layout", True):
                self._add_layout_to_graph(export_graph, kwargs.get("layout_type", "force_directed"))
            self._write_graph_to_file(export_graph, filepath, kwargs.get("format", "json"))
            logger.info(f"Exported graph to {filepath} ({kwargs.get('format', 'json')} format)")
            return True
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return False

    def import_graph(self, filepath: Union[str, Path], format: str = "json") -> bool:
        try:
            self.graph = self._read_graph_from_file(Path(filepath), format)
            self._invalidate_cache()
            logger.info(f"Imported graph from {filepath} ({format} format)")
            return True
        except Exception as e:
            logger.error(f"Failed to import graph: {e}")
            return False

    def export_visualization(self, filepath: Union[str, Path], **kwargs) -> bool:
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            fig = self.create_interactive_plot(**kwargs)
            self._write_visualization_to_file(fig, filepath, kwargs.get("format", "html"))
            logger.info(f"Exported visualization to {filepath} ({kwargs.get('format', 'html')} format)")
            return True
        except Exception as e:
            logger.error(f"Failed to export visualization: {e}")
            return False

    def clear_graph(self) -> None:
        self.graph.clear()
        self.node_data.clear()
        self.temporal_snapshots.clear()
        self.layout_cache.clear()
        self.selected_nodes.clear()
        self._invalidate_cache()
        logger.info("Cleared all graph data")

    def get_summary(self) -> dict[str, Any]:
        return {
            "basic_stats": self._get_basic_stats(),
            "node_types": dict(Counter(nx.get_node_attributes(self.graph, "type").values())),
            "link_types": dict(Counter(nx.get_edge_attributes(self.graph, "link_type").values())),
            "temporal_range": self._get_temporal_range(),
            "metrics": self.calculate_graph_metrics(),
        }

    def _validate_matriz_node(self, node: dict[str, Any]) -> bool:
        required = ["id", "type", "state", "timestamps", "provenance"]
        return all(k in node for k in required) and all(k in node["state"] for k in ("confidence", "salience"))

    def _add_node_to_graph(self, node: dict[str, Any]):
        self.graph.add_node(
            node["id"],
            type=node["type"],
            confidence=node["state"].get("confidence", 0.5),
            salience=node["state"].get("salience", 0.5),
            valence=node["state"].get("valence"),
            arousal=node["state"].get("arousal"),
            created_ts=node["timestamps"].get("created_ts", int(time.time() * 1000)),
            label=self._generate_node_label(node),
            size=self._calculate_node_size(node),
            color=NodeTypeConfig.get_color(node["type"]),
            shape=NodeTypeConfig.get_shape(node["type"]),
        )

    def _add_link(self, source_id: str, link: dict[str, Any]) -> None:
        target_id = link.get("target_node_id")
        if target_id and target_id in self.node_data:
            self.graph.add_edge(source_id, target_id, **self._extract_link_attributes(link))

    def _extract_link_attributes(self, link: dict[str, Any]) -> dict:
        link_type = link.get("link_type", "unknown")
        return {
            "link_type": link_type,
            "weight": link.get("weight", 1.0),
            "explanation": link.get("explanation", ""),
            "direction": link.get("direction", "unidirectional"),
            "color": LinkTypeConfig.get_color(link_type),
            "style": LinkTypeConfig.get_style(link_type),
        }

    def _generate_node_label(self, node: dict[str, Any]) -> str:
        return f"{node['type']}\n{node['id'][:8]}...\nConf: {node['state'].get('confidence', 0):.2f}"

    def _calculate_node_size(self, node: dict[str, Any]) -> float:
        base_size = 20
        importance = (node["state"].get("confidence", 0.5) + node["state"].get("salience", 0.5)) / 2
        multiplier = NodeTypeConfig.get_size_multiplier(node["type"])
        return base_size * (0.5 + importance) * multiplier

    def _update_temporal_snapshots(self, node_id: str, timestamp: Optional[int]) -> None:
        if timestamp:
            self.temporal_snapshots.setdefault(timestamp, set()).add(node_id)

    def _rebuild_temporal_snapshots(self) -> None:
        self.temporal_snapshots.clear()
        for node_id, data in self.graph.nodes(data=True):
            if ts := data.get("created_ts"):
                self._update_temporal_snapshots(node_id, ts)

    def _compute_layout(self, layout_type: str) -> dict:
        cache_key = f"{layout_type}_{self.graph.number_of_nodes()}_{self.graph.number_of_edges()}"
        if cache_key in self.layout_cache:
            return self.layout_cache[cache_key]
        try:
            layout_func = getattr(nx, f"{layout_type}_layout", nx.spring_layout)
            pos = layout_func(self.graph)
        except Exception as e:
            logger.warning(f"Layout '{layout_type}' failed, fallback to spring: {e}")
            pos = nx.spring_layout(self.graph)
        self.layout_cache[cache_key] = pos
        return pos

    def _invalidate_cache(self) -> None:
        self._analysis_cache.clear()
        self._cache_timestamp = 0

    def _node_matches_criteria(self, node_id, data, criteria) -> bool:
        for key, value in criteria.items():
            if key == "node_type" and data.get("type") != value:
                return False
            if key == "min_confidence" and data.get("confidence", 0) < value:
                return False
            if key == "max_confidence" and data.get("confidence", 0) > value:
                return False
            if key == "min_salience" and data.get("salience", 0) < value:
                return False
            if key == "max_salience" and data.get("salience", 0) > value:
                return False
            if key == "time_range" and not (value[0] <= data.get("created_ts", 0) <= value[1]):
                return False
            if key == "has_links":
                has = self.graph.in_degree(node_id) > 0 or self.graph.out_degree(node_id) > 0
                if value != has:
                    return False
        return True

    def _configure_plot_layout(self, fig, title):
        fig.update_layout(
            title=title,
            width=self.width,
            height=self.height,
            showlegend=True,
            hovermode="closest",
            margin={"b": 20, "l": 5, "r": 5, "t": 40},
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        )

    def _create_animation_frame(self, timestamp, base_pos, all_timestamps):
        active_nodes = {n for ts in all_timestamps if ts <= timestamp for n in self.temporal_snapshots[ts]}
        subgraph = self.graph.subgraph(active_nodes)
        frame_pos = {n: base_pos[n] for n in active_nodes if n in base_pos}
        edge_trace = self.renderer.create_edge_trace(subgraph, frame_pos)
        node_trace = self.renderer.create_node_trace(subgraph, frame_pos, show_info=True)
        return go.Frame(data=[edge_trace, node_trace] if edge_trace and node_trace else [], name=str(timestamp))

    def _configure_animation_layout(self, fig, frames, time_step, title):
        fig.update_layout(
            title=title,
            updatemenus=[{"type": "buttons", "buttons": [{"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": time_step, "redraw": True}, "fromcurrent": True}]}, {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}]}],
            sliders=[{"steps": [{"args": [[f.name], {"frame": {"duration": 300, "redraw": True}, "mode": "immediate"}], "label": datetime.fromtimestamp(int(f.name) / 1000).strftime('%H:%M:%S'), "method": "animate"} for f in frames]}],
        )

    def _add_dashboard_traces(self, fig):
        node_types = list(nx.get_node_attributes(self.graph, "type").values())
        confidences = list(nx.get_node_attributes(self.graph, "confidence").values())
        saliences = list(nx.get_node_attributes(self.graph, "salience").values())
        link_types = list(nx.get_edge_attributes(self.graph, "link_type").values())

        if node_types:
            fig.add_trace(go.Pie(labels=list(Counter(node_types).keys()), values=list(Counter(node_types).values()), name="Node Types"), row=1, col=1)
        if confidences:
            fig.add_trace(go.Histogram(x=confidences, name="Confidence"), row=1, col=2)
        if saliences:
            fig.add_trace(go.Histogram(x=saliences, name="Salience"), row=1, col=3)
        if link_types:
            fig.add_trace(go.Pie(labels=list(Counter(link_types).keys()), values=list(Counter(link_types).values()), name="Link Types"), row=2, col=1)
        if self.temporal_snapshots:
            timestamps = sorted(self.temporal_snapshots.keys())
            fig.add_trace(go.Scatter(x=[datetime.fromtimestamp(ts/1000) for ts in timestamps], y=[len(self.temporal_snapshots[ts]) for ts in timestamps], mode='lines+markers', name='Activity'), row=2, col=2)
        metrics = self.calculate_graph_metrics()
        if metrics:
            fig.add_trace(go.Table(header={"values":['Metric', 'Value']}, cells={"values":[list(metrics.keys()), [f"{v:.3f}" if isinstance(v, float) else v for v in metrics.values()]]}), row=2, col=3)

    def _is_cache_valid(self, key):
        return key in self._analysis_cache and (time.time() - self._cache_timestamp) < 300

    def _compute_graph_metrics(self):
        metrics = self._get_basic_stats()
        metrics.update(self._get_connectivity_metrics())
        metrics.update(self._get_centrality_metrics())
        metrics.update(self._get_node_attribute_metrics())
        return metrics

    def _get_basic_stats(self):
        return {"Nodes": self.graph.number_of_nodes(), "Edges": self.graph.number_of_edges(), "Density": nx.density(self.graph)}

    def _get_connectivity_metrics(self):
        if not self.graph.nodes():
            return {}
        undirected = self.graph.to_undirected()
        if nx.is_connected(undirected):
            return {"Connected Components": 1, "Average Path Length": nx.average_shortest_path_length(undirected), "Diameter": nx.diameter(undirected)}
        components = list(nx.connected_components(undirected))
        return {"Connected Components": len(components), "Largest Component Size": len(max(components, key=len))}

    def _get_centrality_metrics(self):
        if not self.graph.nodes():
            return {}
        sample = self.graph.nodes()
        if len(sample) > 100:
            sample = list(sample)[:100]
        return {
            "Avg Degree Centrality": np.mean(list(nx.degree_centrality(self.graph).values())),
            "Avg Betweenness Centrality": np.mean(list(nx.betweenness_centrality(self.graph, k=min(20, len(sample))).values())),
            "Avg Clustering Coefficient": np.mean(list(nx.clustering(self.graph.to_undirected()).values())),
        }

    def _get_node_attribute_metrics(self):
        metrics = {}
        confidences = list(nx.get_node_attributes(self.graph, 'confidence').values())
        saliences = list(nx.get_node_attributes(self.graph, 'salience').values())
        if confidences:
            metrics.update({"Avg Confidence": np.mean(confidences), "Confidence Std": np.std(confidences)})
        if saliences:
            metrics.update({"Avg Salience": np.mean(saliences), "Salience Std": np.std(saliences)})
        metrics["Node Type Diversity"] = len(set(nx.get_node_attributes(self.graph, 'type').values()))
        return metrics

    def _add_layout_to_graph(self, graph, layout_type):
        pos = self._compute_layout(layout_type)
        for node, (x, y) in pos.items():
            graph.nodes[node]['x'], graph.nodes[node]['y'] = x, y

    def _write_graph_to_file(self, graph, filepath, format):
        if format == "json":
            data = {"graph": nx.node_link_data(graph), "matriz_nodes": self.node_data, "metadata": {"created_at": datetime.now(timezone.utc).isoformat()}}
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        else:
            getattr(nx, f"write_{format}")(graph, str(filepath))

    def _read_graph_from_file(self, filepath, format):
        if format == "json":
            with open(filepath) as f:
                data = json.load(f)
            self.node_data = data.get("matriz_nodes", {})
            self._rebuild_temporal_snapshots()
            return nx.node_link_graph(data["graph"])
        return getattr(nx, f"read_{format}")(str(filepath))

    def _write_visualization_to_file(self, fig, filepath, format):
        if format == "html":
            fig.write_html(str(filepath))
        else:
            fig.write_image(str(filepath))

    def _get_temporal_range(self):
        if not self.temporal_snapshots:
            return None
        start, end = min(self.temporal_snapshots), max(self.temporal_snapshots)
        return {"start": start, "end": end, "duration_ms": end - start}


# Example usage and testing
if __name__ == "__main__":
    # Example MATRIZ nodes for testing
    example_nodes = [
        {
            "version": 1,
            "id": "node_001",
            "type": "COMPUTATION",
            "state": {
                "confidence": 0.95,
                "salience": 0.8,
                "valence": 0.7,
                "expression": "2 + 3 * 4",
                "result": 14,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "MathNode",
                "capabilities": ["arithmetic_evaluation"],
                "tenant": "test",
                "trace_id": "trace_001",
                "consent_scopes": ["cognitive_processing"],
            },
            "links": [
                {
                    "target_node_id": "node_002",
                    "link_type": "causal",
                    "direction": "unidirectional",
                    "weight": 0.9,
                }
            ],
            "evolves_to": [],
            "triggers": [],
            "reflections": [],
        },
        {
            "version": 1,
            "id": "node_002",
            "type": "VALIDATION",
            "state": {
                "confidence": 0.88,
                "salience": 0.6,
                "valence": 0.5,
                "validation_result": True,
            },
            "timestamps": {"created_ts": int(time.time() * 1000) + 1000},
            "provenance": {
                "producer": "ValidatorNode",
                "capabilities": ["result_validation"],
                "tenant": "test",
                "trace_id": "trace_002",
                "consent_scopes": ["cognitive_processing"],
            },
            "links": [],
            "evolves_to": [],
            "triggers": [],
            "reflections": [],
        },
        {
            "version": 1,
            "id": "node_003",
            "type": "EMOTION",
            "state": {
                "confidence": 0.75,
                "salience": 0.9,
                "valence": 0.8,
                "arousal": 0.6,
                "emotion_type": "satisfaction",
            },
            "timestamps": {"created_ts": int(time.time() * 1000) + 2000},
            "provenance": {
                "producer": "EmotionNode",
                "capabilities": ["emotion_processing"],
                "tenant": "test",
                "trace_id": "trace_003",
                "consent_scopes": ["cognitive_processing"],
            },
            "links": [
                {
                    "target_node_id": "node_001",
                    "link_type": "emotional",
                    "direction": "unidirectional",
                    "weight": 0.7,
                }
            ],
            "evolves_to": [],
            "triggers": [],
            "reflections": [],
        },
    ]

    print("MATRIZ Graph Visualization System Demo")
    print("=" * 50)

    # Create viewer
    viewer = MATRIZGraphViewer(width=1000, height=700)

    # Add example nodes
    print("\nAdding example nodes...")
    success, failed = viewer.add_nodes_batch(example_nodes)
    print(f"Successfully added: {success}, Failed: {failed}")

    # Display summary
    print("\nGraph Summary:")
    summary = viewer.get_summary()
    for section, data in summary.items():
        print(f"  {section}: {data}")

    # Search functionality
    print("\nTesting search functionality...")
    computation_nodes = viewer.search_nodes(node_type="COMPUTATION")
    print(f"Found {len(computation_nodes)} COMPUTATION nodes")

    high_confidence_nodes = viewer.search_nodes(min_confidence=0.8)
    print(f"Found {len(high_confidence_nodes)} high-confidence nodes")

    # Create visualizations
    print("\nCreating visualizations...")

    try:
        # Interactive plot
        fig1 = viewer.create_interactive_plot(title="Demo Graph - Interactive View")
        print("✓ Created interactive plot")

        # Statistics dashboard
        fig2 = viewer.create_statistics_dashboard()
        print("✓ Created statistics dashboard")

        # Temporal animation
        fig3 = viewer.create_temporal_animation(title="Demo Graph - Temporal Evolution")
        print("✓ Created temporal animation")

        # Export graph
        export_path = Path("demo_export.json")
        if viewer.export_graph(filepath=export_path, format="json"):
            print(f"✓ Exported graph to {export_path}")

        # Save visualizations
        try:
            fig1.write_html("demo_interactive.html")
            print("✓ Saved interactive plot to demo_interactive.html")
        except Exception as e:
            print(f"⚠ Could not save HTML: {e}")

        print("\nDemo completed successfully!")
        print("Check the generated files for visualization outputs.")

    except Exception as e:
        print(f"✗ Visualization error: {e}")

    # Calculate and display metrics
    print("\nGraph Metrics:")
    metrics = viewer.calculate_graph_metrics()
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")
