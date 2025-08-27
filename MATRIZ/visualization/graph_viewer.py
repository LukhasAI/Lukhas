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
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

# Suppress Plotly warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="plotly")

try:
    import networkx as nx
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as e:
    raise ImportError(
        f"Missing required dependencies: {e}. "
        "Please install with: pip install networkx plotly pandas numpy"
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NodeTypeConfig:
    """Configuration for MATRIZ node type visualization."""

    # Color scheme for different node types
    COLORS = {
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
    SHAPES = {
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
    SIZE_MULTIPLIER = {
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
    COLORS = {
        "temporal": "#74B9FF",  # Blue - time-based connections
        "causal": "#E17055",  # Orange-red - cause-effect
        "semantic": "#00B894",  # Green - meaning-based
        "emotional": "#FFEAA7",  # Yellow - emotion-based
        "spatial": "#A29BFE",  # Purple - space-based
        "evidence": "#FD79A8",  # Pink - evidence relationships
        "unknown": "#636E72",  # Gray - unknown relationships
    }

    # Line styles for different link types
    STYLES = {
        "temporal": "solid",
        "causal": "dash",
        "semantic": "dot",
        "emotional": "dashdot",
        "spatial": "solid",
        "evidence": "dash",
        "unknown": "solid",
    }

    # Width scaling based on link importance
    WIDTH_MULTIPLIER = {
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


class MATRIZGraphViewer:
    """
    Production-ready interactive visualization system for MATRIZ cognitive graphs.

    This class provides comprehensive graph visualization capabilities including:
    - Interactive node and edge exploration
    - Temporal evolution tracking and animation
    - Multiple layout algorithms
    - Statistical analysis and metrics
    - Export capabilities
    - Real-time filtering and search
    """

    def __init__(
        self,
        width: int = 1200,
        height: int = 800,
        show_labels: bool = True,
        enable_physics: bool = True,
    ):
        """
        Initialize the MATRIZ graph viewer.

        Args:
            width: Plot width in pixels
            height: Plot height in pixels
            show_labels: Whether to show node labels by default
            enable_physics: Whether to enable physics simulation for layouts
        """
        self.width = width
        self.height = height
        self.show_labels = show_labels
        self.enable_physics = enable_physics

        # Core graph structure
        self.graph = nx.DiGraph()
        self.node_data = {}  # Store full MATRIZ node data
        self.temporal_snapshots = {}  # Time-based graph snapshots
        self.layout_cache = {}  # Cache computed layouts

        # Visualization state
        self.selected_nodes = set()
        self.filtered_node_types = set()
        self.filtered_link_types = set()
        self.time_range = None

        # Analysis results cache
        self._analysis_cache = {}
        self._cache_timestamp = 0

        logger.info(f"Initialized MATRIZ Graph Viewer ({width}x{height})")

    def add_node(self, matriz_node: dict[str, Any]) -> None:
        """
        Add a MATRIZ node to the graph.

        Args:
            matriz_node: Complete MATRIZ format node dictionary

        Raises:
            ValueError: If node format is invalid
        """
        try:
            # Validate node structure
            if not self._validate_matriz_node(matriz_node):
                raise ValueError("Invalid MATRIZ node format")

            node_id = matriz_node["id"]
            node_type = matriz_node["type"]
            state = matriz_node["state"]
            timestamps = matriz_node["timestamps"]

            # Store full node data
            self.node_data[node_id] = matriz_node

            # Add node to graph with computed attributes
            self.graph.add_node(
                node_id,
                type=node_type,
                confidence=state.get("confidence", 0.5),
                salience=state.get("salience", 0.5),
                valence=state.get("valence"),
                arousal=state.get("arousal"),
                created_ts=timestamps.get("created_ts", int(time.time() * 1000)),
                label=self._generate_node_label(matriz_node),
                size=self._calculate_node_size(matriz_node),
                color=NodeTypeConfig.get_color(node_type),
                shape=NodeTypeConfig.get_shape(node_type),
            )

            # Add links from this node
            for link in matriz_node.get("links", []):
                self._add_link(node_id, link)

            # Update temporal snapshots
            self._update_temporal_snapshots(node_id, timestamps.get("created_ts"))

            # Clear analysis cache
            self._invalidate_cache()

            logger.debug(f"Added node {node_id[:8]}... (type: {node_type})")

        except Exception as e:
            logger.error(f"Failed to add node: {e}")
            raise

    def add_nodes_batch(self, matriz_nodes: list[dict[str, Any]]) -> tuple[int, int]:
        """
        Add multiple MATRIZ nodes efficiently.

        Args:
            matriz_nodes: List of MATRIZ node dictionaries

        Returns:
            Tuple of (successful_adds, failed_adds)
        """
        successful = 0
        failed = 0

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
        """
        Remove a node from the graph.

        Args:
            node_id: ID of node to remove

        Returns:
            True if node was removed, False if not found
        """
        try:
            if node_id in self.graph:
                self.graph.remove_node(node_id)
                if node_id in self.node_data:
                    del self.node_data[node_id]
                self.selected_nodes.discard(node_id)
                self._invalidate_cache()
                logger.debug(f"Removed node {node_id[:8]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove node {node_id}: {e}")
            return False

    def get_node_details(self, node_id: str) -> Optional[dict[str, Any]]:
        """
        Get complete details for a specific node.

        Args:
            node_id: ID of node to inspect

        Returns:
            Complete node data or None if not found
        """
        return self.node_data.get(node_id)

    def search_nodes(
        self,
        node_type: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        min_salience: Optional[float] = None,
        max_salience: Optional[float] = None,
        time_range: Optional[tuple[int, int]] = None,
        has_links: Optional[bool] = None,
    ) -> list[str]:
        """
        Search for nodes matching specified criteria.

        Args:
            node_type: Filter by node type
            min_confidence: Minimum confidence threshold
            max_confidence: Maximum confidence threshold
            min_salience: Minimum salience threshold
            max_salience: Maximum salience threshold
            time_range: (start_ts, end_ts) in epoch milliseconds
            has_links: Filter nodes with/without links

        Returns:
            List of matching node IDs
        """
        matching_nodes = []

        for node_id, data in self.graph.nodes(data=True):
            # Type filter
            if node_type and data.get("type") != node_type:
                continue

            # Confidence filters
            confidence = data.get("confidence", 0)
            if min_confidence is not None and confidence < min_confidence:
                continue
            if max_confidence is not None and confidence > max_confidence:
                continue

            # Salience filters
            salience = data.get("salience", 0)
            if min_salience is not None and salience < min_salience:
                continue
            if max_salience is not None and salience > max_salience:
                continue

            # Time range filter
            if time_range:
                created_ts = data.get("created_ts", 0)
                if not (time_range[0] <= created_ts <= time_range[1]):
                    continue

            # Links filter
            if has_links is not None:
                has_any_links = (
                    self.graph.in_degree(node_id) > 0
                    or self.graph.out_degree(node_id) > 0
                )
                if has_links != has_any_links:
                    continue

            matching_nodes.append(node_id)

        logger.info(f"Search found {len(matching_nodes)} matching nodes")
        return matching_nodes

    def create_interactive_plot(
        self,
        layout: str = "force_directed",
        show_node_info: bool = True,
        show_link_weights: bool = False,
        highlight_critical_path: bool = False,
        title: str = "MATRIZ Cognitive Graph",
    ) -> go.Figure:
        """
        Create an interactive Plotly visualization of the graph.

        Args:
            layout: Layout algorithm ('force_directed', 'hierarchical', 'circular', 'spiral')
            show_node_info: Whether to show detailed node information on hover
            show_link_weights: Whether to display link weights
            highlight_critical_path: Whether to highlight high-importance paths
            title: Plot title

        Returns:
            Plotly Figure object
        """
        try:
            if self.graph.number_of_nodes() == 0:
                return self._create_empty_plot(title)

            # Compute layout positions
            pos = self._compute_layout(layout)

            # Create figure
            fig = go.Figure()

            # Add edges first (so they appear behind nodes)
            self._add_edges_to_plot(
                fig, pos, show_link_weights, highlight_critical_path
            )

            # Add nodes
            self._add_nodes_to_plot(fig, pos, show_node_info)

            # Configure layout
            fig.update_layout(
                title={
                    "text": title,
                    "x": 0.5,
                    "font": {"size": 20, "color": "#2C3E50"},
                },
                width=self.width,
                height=self.height,
                showlegend=True,
                hovermode="closest",
                margin={"b": 20, "l": 5, "r": 5, "t": 40},
                annotations=[
                    {
                        "text": f"Nodes: {self.graph.number_of_nodes()}, "
                        f"Edges: {self.graph.number_of_edges()}",
                        "showarrow": False,
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.005,
                        "y": -0.002,
                        "xanchor": "left",
                        "yanchor": "bottom",
                        "font": {"size": 12, "color": "#7F8C8D"},
                    }
                ],
                xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                plot_bgcolor="white",
                paper_bgcolor="white",
            )

            # Add legend for node types
            self._add_node_type_legend(fig)

            logger.info(
                f"Created interactive plot with {self.graph.number_of_nodes()} nodes"
            )
            return fig

        except Exception as e:
            logger.error(f"Failed to create interactive plot: {e}")
            return self._create_error_plot(str(e))

    def create_temporal_animation(
        self,
        time_step_ms: int = 1000,
        layout: str = "force_directed",
        title: str = "MATRIZ Temporal Evolution",
    ) -> go.Figure:
        """
        Create an animated visualization showing temporal evolution of the graph.

        Args:
            time_step_ms: Time step in milliseconds for animation frames
            layout: Layout algorithm to use
            title: Animation title

        Returns:
            Plotly Figure with animation frames
        """
        try:
            if not self.temporal_snapshots:
                return self._create_empty_plot(title)

            # Create time-ordered snapshots
            timestamps = sorted(self.temporal_snapshots.keys())
            frames = []

            # Compute stable layout using full graph
            base_pos = self._compute_layout(layout)

            for i, timestamp in enumerate(timestamps):
                # Get nodes active up to this timestamp
                active_nodes = set()
                for ts in timestamps[: i + 1]:
                    active_nodes.update(self.temporal_snapshots[ts])

                # Create subgraph
                subgraph = self.graph.subgraph(active_nodes)

                # Filter positions for active nodes
                frame_pos = {
                    node: base_pos[node] for node in active_nodes if node in base_pos
                }

                # Create frame
                frame_data = []

                # Add edges for this frame
                edge_trace = self._create_edge_trace(subgraph, frame_pos)
                if edge_trace:
                    frame_data.append(edge_trace)

                # Add nodes for this frame
                node_trace = self._create_node_trace(
                    subgraph, frame_pos, show_info=True
                )
                if node_trace:
                    frame_data.append(node_trace)

                frames.append(
                    go.Frame(
                        data=frame_data,
                        name=str(timestamp),
                        layout={
                            "title": f"{title} - {datetime.fromtimestamp(timestamp/1000).strftime('%H:%M:%S')}"
                        },
                    )
                )

            # Create initial figure with first frame
            fig = go.Figure(data=frames[0].data if frames else [], frames=frames)

            # Add animation controls
            fig.update_layout(
                title=title,
                width=self.width,
                height=self.height,
                updatemenus=[
                    {
                        "type": "buttons",
                        "buttons": [
                            {
                                "label": "Play",
                                "method": "animate",
                                "args": [
                                    None,
                                    {
                                        "frame": {
                                            "duration": time_step_ms,
                                            "redraw": True,
                                        },
                                        "fromcurrent": True,
                                        "transition": {"duration": 300},
                                    },
                                ],
                            },
                            {
                                "label": "Pause",
                                "method": "animate",
                                "args": [
                                    [None],
                                    {
                                        "frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0},
                                    },
                                ],
                            },
                        ],
                        "x": 0.1,
                        "y": 0,
                        "xanchor": "right",
                        "yanchor": "top",
                    }
                ],
                sliders=[
                    {
                        "steps": [
                            {
                                "args": [
                                    [frame.name],
                                    {
                                        "frame": {"duration": 300, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": 300},
                                    },
                                ],
                                "label": datetime.fromtimestamp(
                                    int(frame.name) / 1000
                                ).strftime("%H:%M:%S"),
                                "method": "animate",
                            }
                            for frame in frames
                        ],
                        "x": 0.1,
                        "len": 0.9,
                        "xanchor": "left",
                        "y": 0,
                        "yanchor": "top",
                    }
                ],
                xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                plot_bgcolor="white",
                paper_bgcolor="white",
            )

            logger.info(f"Created temporal animation with {len(frames)} frames")
            return fig

        except Exception as e:
            logger.error(f"Failed to create temporal animation: {e}")
            return self._create_error_plot(str(e))

    def create_statistics_dashboard(self) -> go.Figure:
        """
        Create a comprehensive statistics dashboard for the graph.

        Returns:
            Plotly Figure with multiple subplots showing graph statistics
        """
        try:
            if self.graph.number_of_nodes() == 0:
                return self._create_empty_plot("Graph Statistics Dashboard")

            # Create subplots
            fig = make_subplots(
                rows=2,
                cols=3,
                subplot_titles=[
                    "Node Type Distribution",
                    "Confidence Distribution",
                    "Salience Distribution",
                    "Link Type Distribution",
                    "Temporal Activity",
                    "Network Metrics",
                ],
                specs=[
                    [{"type": "pie"}, {"type": "histogram"}, {"type": "histogram"}],
                    [{"type": "pie"}, {"type": "scatter"}, {"type": "table"}],
                ],
            )

            # Node type distribution (pie chart)
            node_types = [data["type"] for _, data in self.graph.nodes(data=True)]
            type_counts = Counter(node_types)

            fig.add_trace(
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    marker_colors=[NodeTypeConfig.get_color(t) for t in type_counts],
                    name="Node Types",
                ),
                row=1,
                col=1,
            )

            # Confidence distribution (histogram)
            confidences = [
                data.get("confidence", 0) for _, data in self.graph.nodes(data=True)
            ]
            fig.add_trace(
                go.Histogram(
                    x=confidences, nbinsx=20, name="Confidence", marker_color="#3498DB"
                ),
                row=1,
                col=2,
            )

            # Salience distribution (histogram)
            saliences = [
                data.get("salience", 0) for _, data in self.graph.nodes(data=True)
            ]
            fig.add_trace(
                go.Histogram(
                    x=saliences, nbinsx=20, name="Salience", marker_color="#E74C3C"
                ),
                row=1,
                col=3,
            )

            # Link type distribution (pie chart)
            link_types = []
            for _, _, data in self.graph.edges(data=True):
                link_types.append(data.get("link_type", "unknown"))

            if link_types:
                link_counts = Counter(link_types)
                fig.add_trace(
                    go.Pie(
                        labels=list(link_counts.keys()),
                        values=list(link_counts.values()),
                        marker_colors=[
                            LinkTypeConfig.get_color(t) for t in link_counts
                        ],
                        name="Link Types",
                    ),
                    row=2,
                    col=1,
                )

            # Temporal activity (scatter plot)
            if self.temporal_snapshots:
                timestamps = list(self.temporal_snapshots.keys())
                activity_counts = [
                    len(nodes) for nodes in self.temporal_snapshots.values()
                ]

                fig.add_trace(
                    go.Scatter(
                        x=[datetime.fromtimestamp(ts / 1000) for ts in timestamps],
                        y=activity_counts,
                        mode="lines+markers",
                        name="Activity",
                        line={"color": "#2ECC71", "width": 2},
                        marker={"size": 6},
                    ),
                    row=2,
                    col=2,
                )

            # Network metrics (table)
            metrics = self.calculate_graph_metrics()
            fig.add_trace(
                go.Table(
                    header={
                        "values": ["Metric", "Value"],
                        "fill_color": "#F8F9FA",
                        "align": "left",
                        "font": {"size": 12},
                    },
                    cells={
                        "values": [
                            list(metrics.keys()),
                            [
                                f"{v:.3f}" if isinstance(v, float) else str(v)
                                for v in metrics.values()
                            ],
                        ],
                        "fill_color": "white",
                        "align": "left",
                        "font": {"size": 11},
                    },
                ),
                row=2,
                col=3,
            )

            # Update layout
            fig.update_layout(
                title={
                    "text": "MATRIZ Graph Statistics Dashboard",
                    "x": 0.5,
                    "font": {"size": 20, "color": "#2C3E50"},
                },
                width=self.width,
                height=self.height,
                showlegend=False,
            )

            logger.info("Created statistics dashboard")
            return fig

        except Exception as e:
            logger.error(f"Failed to create statistics dashboard: {e}")
            return self._create_error_plot(str(e))

    def calculate_graph_metrics(self) -> dict[str, Union[int, float]]:
        """
        Calculate comprehensive graph analysis metrics.

        Returns:
            Dictionary of calculated metrics
        """
        if not self.graph.nodes():
            return {}

        cache_key = "graph_metrics"
        current_time = time.time()

        # Check cache
        if (
            cache_key in self._analysis_cache
            and current_time - self._cache_timestamp < 300
        ):  # 5 minute cache
            return self._analysis_cache[cache_key]

        try:
            metrics = {}

            # Basic graph properties
            metrics["Nodes"] = self.graph.number_of_nodes()
            metrics["Edges"] = self.graph.number_of_edges()
            metrics["Density"] = nx.density(self.graph)

            # Convert to undirected for some metrics
            undirected_graph = self.graph.to_undirected()

            # Connectivity
            if nx.is_connected(undirected_graph):
                metrics["Connected Components"] = 1
                metrics["Average Path Length"] = nx.average_shortest_path_length(
                    undirected_graph
                )
                metrics["Diameter"] = nx.diameter(undirected_graph)
            else:
                components = list(nx.connected_components(undirected_graph))
                metrics["Connected Components"] = len(components)
                metrics["Largest Component Size"] = len(max(components, key=len))

            # Centrality measures (sample for performance)
            sample_size = min(100, self.graph.number_of_nodes())
            sample_nodes = list(self.graph.nodes())[:sample_size]

            if sample_nodes:
                # Degree centrality
                degree_centrality = nx.degree_centrality(self.graph)
                metrics["Avg Degree Centrality"] = np.mean(
                    [degree_centrality[n] for n in sample_nodes]
                )

                # Betweenness centrality (expensive, so sample)
                if len(sample_nodes) <= 50:
                    between_centrality = nx.betweenness_centrality(
                        self.graph, k=min(20, len(sample_nodes))
                    )
                    metrics["Avg Betweenness Centrality"] = np.mean(
                        list(between_centrality.values())
                    )

                # Clustering coefficient
                clustering = nx.clustering(undirected_graph)
                metrics["Avg Clustering Coefficient"] = np.mean(
                    [clustering[n] for n in sample_nodes]
                )

            # Confidence and salience statistics
            confidences = [
                data.get("confidence", 0) for _, data in self.graph.nodes(data=True)
            ]
            saliences = [
                data.get("salience", 0) for _, data in self.graph.nodes(data=True)
            ]

            if confidences:
                metrics["Avg Confidence"] = np.mean(confidences)
                metrics["Confidence Std"] = np.std(confidences)

            if saliences:
                metrics["Avg Salience"] = np.mean(saliences)
                metrics["Salience Std"] = np.std(saliences)

            # Node type diversity
            node_types = [data["type"] for _, data in self.graph.nodes(data=True)]
            metrics["Node Type Diversity"] = len(set(node_types))

            # Cache results
            self._analysis_cache[cache_key] = metrics
            self._cache_timestamp = current_time

            logger.info(f"Calculated {len(metrics)} graph metrics")
            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate graph metrics: {e}")
            return {"Error": str(e)}

    def export_graph(
        self,
        filepath: Union[str, Path],
        format: str = "json",
        include_layout: bool = True,
        layout_type: str = "force_directed",
    ) -> bool:
        """
        Export the graph to various formats.

        Args:
            filepath: Output file path
            format: Export format ('json', 'gexf', 'graphml', 'edgelist')
            include_layout: Whether to include layout positions
            layout_type: Layout algorithm to use for positions

        Returns:
            True if export successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Prepare graph for export
            export_graph = self.graph.copy()

            # Add layout positions if requested
            if include_layout:
                pos = self._compute_layout(layout_type)
                for node, (x, y) in pos.items():
                    if node in export_graph:
                        export_graph.nodes[node]["x"] = float(x)
                        export_graph.nodes[node]["y"] = float(y)

            # Export based on format
            if format.lower() == "json":
                # Custom JSON format with full MATRIZ data
                export_data = {
                    "graph": nx.node_link_data(export_graph),
                    "matriz_nodes": self.node_data,
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "node_count": export_graph.number_of_nodes(),
                        "edge_count": export_graph.number_of_edges(),
                        "layout_type": layout_type if include_layout else None,
                    },
                }

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            elif format.lower() == "gexf":
                nx.write_gexf(export_graph, filepath)

            elif format.lower() == "graphml":
                nx.write_graphml(export_graph, filepath)

            elif format.lower() == "edgelist":
                nx.write_edgelist(export_graph, filepath, data=True)

            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported graph to {filepath} ({format} format)")
            return True

        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return False

    def import_graph(self, filepath: Union[str, Path], format: str = "json") -> bool:
        """
        Import graph from file.

        Args:
            filepath: Input file path
            format: Import format ('json', 'gexf', 'graphml', 'edgelist')

        Returns:
            True if import successful, False otherwise
        """
        try:
            filepath = Path(filepath)

            if format.lower() == "json":
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                # Import graph structure
                self.graph = nx.node_link_graph(data["graph"], directed=True)

                # Import MATRIZ node data if available
                if "matriz_nodes" in data:
                    self.node_data = data["matriz_nodes"]

                # Rebuild temporal snapshots
                self._rebuild_temporal_snapshots()

            elif format.lower() == "gexf":
                self.graph = nx.read_gexf(filepath, node_type=str)

            elif format.lower() == "graphml":
                self.graph = nx.read_graphml(filepath)

            elif format.lower() == "edgelist":
                self.graph = nx.read_edgelist(
                    filepath, create_using=nx.DiGraph(), data=True
                )

            else:
                raise ValueError(f"Unsupported format: {format}")

            self._invalidate_cache()
            logger.info(f"Imported graph from {filepath} ({format} format)")
            return True

        except Exception as e:
            logger.error(f"Failed to import graph: {e}")
            return False

    def export_visualization(
        self,
        filepath: Union[str, Path],
        format: str = "html",
        layout: str = "force_directed",
        **kwargs,
    ) -> bool:
        """
        Export visualization to file.

        Args:
            filepath: Output file path
            format: Export format ('html', 'png', 'jpg', 'pdf', 'svg')
            layout: Layout algorithm to use
            **kwargs: Additional arguments for plot creation

        Returns:
            True if export successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Create the plot
            fig = self.create_interactive_plot(layout=layout, **kwargs)

            # Export based on format
            if format.lower() == "html":
                fig.write_html(str(filepath))
            elif format.lower() in ["png", "jpg", "jpeg", "pdf", "svg"]:
                fig.write_image(str(filepath), format=format.lower())
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported visualization to {filepath} ({format} format)")
            return True

        except Exception as e:
            logger.error(f"Failed to export visualization: {e}")
            return False

    def clear_graph(self) -> None:
        """Clear all graph data."""
        self.graph.clear()
        self.node_data.clear()
        self.temporal_snapshots.clear()
        self.layout_cache.clear()
        self.selected_nodes.clear()
        self._invalidate_cache()
        logger.info("Cleared all graph data")

    def get_summary(self) -> dict[str, Any]:
        """
        Get a comprehensive summary of the graph.

        Returns:
            Dictionary containing graph summary information
        """
        summary = {
            "basic_stats": {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "density": nx.density(self.graph) if self.graph.nodes() else 0,
            },
            "node_types": {},
            "link_types": {},
            "temporal_range": None,
            "metrics": self.calculate_graph_metrics(),
        }

        # Node type distribution
        if self.graph.nodes():
            node_types = [data["type"] for _, data in self.graph.nodes(data=True)]
            summary["node_types"] = dict(Counter(node_types))

        # Link type distribution
        if self.graph.edges():
            link_types = [
                data.get("link_type", "unknown")
                for _, _, data in self.graph.edges(data=True)
            ]
            summary["link_types"] = dict(Counter(link_types))

        # Temporal range
        if self.temporal_snapshots:
            timestamps = list(self.temporal_snapshots.keys())
            summary["temporal_range"] = {
                "start": min(timestamps),
                "end": max(timestamps),
                "duration_ms": max(timestamps) - min(timestamps),
            }

        return summary

    # Private helper methods

    def _validate_matriz_node(self, node: dict[str, Any]) -> bool:
        """Validate MATRIZ node format."""
        required_fields = ["id", "type", "state", "timestamps", "provenance"]
        for field in required_fields:
            if field not in node:
                return False

        state = node.get("state", {})
        if "confidence" not in state or "salience" not in state:
            return False

        return True

    def _add_link(self, source_id: str, link: dict[str, Any]) -> None:
        """Add a link to the graph."""
        target_id = link.get("target_node_id")
        link_type = link.get("link_type", "unknown")
        weight = link.get("weight", 1.0)

        if target_id and target_id in self.node_data:
            self.graph.add_edge(
                source_id,
                target_id,
                link_type=link_type,
                weight=weight,
                explanation=link.get("explanation", ""),
                direction=link.get("direction", "unidirectional"),
                color=LinkTypeConfig.get_color(link_type),
                style=LinkTypeConfig.get_style(link_type),
            )

    def _generate_node_label(self, matriz_node: dict[str, Any]) -> str:
        """Generate a display label for a node."""
        node_type = matriz_node["type"]
        node_id = matriz_node["id"][:8]
        confidence = matriz_node["state"].get("confidence", 0)

        return f"{node_type}\n{node_id}...\nConf: {confidence:.2f}"

    def _calculate_node_size(self, matriz_node: dict[str, Any]) -> float:
        """Calculate node size based on importance."""
        base_size = 20

        # Size based on confidence and salience
        confidence = matriz_node["state"].get("confidence", 0.5)
        salience = matriz_node["state"].get("salience", 0.5)
        importance = (confidence + salience) / 2

        # Type-based multiplier
        node_type = matriz_node["type"]
        type_multiplier = NodeTypeConfig.get_size_multiplier(node_type)

        return base_size * (0.5 + importance) * type_multiplier

    def _update_temporal_snapshots(
        self, node_id: str, timestamp: Optional[int]
    ) -> None:
        """Update temporal snapshots with new node."""
        if timestamp:
            if timestamp not in self.temporal_snapshots:
                self.temporal_snapshots[timestamp] = set()
            self.temporal_snapshots[timestamp].add(node_id)

    def _rebuild_temporal_snapshots(self) -> None:
        """Rebuild temporal snapshots from existing nodes."""
        self.temporal_snapshots.clear()
        for node_id, data in self.graph.nodes(data=True):
            timestamp = data.get("created_ts")
            if timestamp:
                self._update_temporal_snapshots(node_id, timestamp)

    def _compute_layout(self, layout_type: str) -> dict[str, tuple[float, float]]:
        """Compute node positions using specified layout algorithm."""
        cache_key = f"{layout_type}_{self.graph.number_of_nodes()}_{self.graph.number_of_edges()}"

        if cache_key in self.layout_cache:
            return self.layout_cache[cache_key]

        try:
            if layout_type == "force_directed":
                pos = nx.spring_layout(self.graph, k=1, iterations=50)
            elif layout_type == "hierarchical":
                pos = (
                    nx.nx_agraph.graphviz_layout(self.graph, prog="dot")
                    if "nx_agraph" in dir(nx)
                    else nx.spring_layout(self.graph)
                )
            elif layout_type == "circular":
                pos = nx.circular_layout(self.graph)
            elif layout_type == "spiral":
                pos = nx.spiral_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)

            self.layout_cache[cache_key] = pos
            return pos

        except Exception as e:
            logger.warning(f"Layout computation failed, using fallback: {e}")
            pos = nx.spring_layout(self.graph)
            self.layout_cache[cache_key] = pos
            return pos

    def _add_edges_to_plot(
        self, fig: go.Figure, pos: dict, show_weights: bool, highlight_critical: bool
    ) -> None:
        """Add edges to the plot."""
        edge_traces = defaultdict(list)

        for source, target, data in self.graph.edges(data=True):
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
        for (link_type, width, color), coords in edge_traces.items():
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

    def _add_nodes_to_plot(self, fig: go.Figure, pos: dict, show_info: bool) -> None:
        """Add nodes to the plot grouped by type."""
        node_traces = defaultdict(
            lambda: {"x": [], "y": [], "text": [], "hovertext": [], "size": []}
        )

        for node_id, data in self.graph.nodes(data=True):
            if node_id not in pos:
                continue

            x, y = pos[node_id]
            node_type = data.get("type", "UNKNOWN")

            node_traces[node_type]["x"].append(x)
            node_traces[node_type]["y"].append(y)
            node_traces[node_type]["text"].append(data.get("label", node_id[:8]))
            node_traces[node_type]["size"].append(data.get("size", 20))

            if show_info:
                hover_text = self._create_hover_text(node_id, data)
                node_traces[node_type]["hovertext"].append(hover_text)

        # Add node traces
        for node_type, trace_data in node_traces.items():
            if trace_data["x"]:  # Only add if there are nodes
                fig.add_trace(
                    go.Scatter(
                        x=trace_data["x"],
                        y=trace_data["y"],
                        mode="markers+text" if self.show_labels else "markers",
                        marker={
                            "size": trace_data["size"],
                            "color": NodeTypeConfig.get_color(node_type),
                            "symbol": NodeTypeConfig.get_shape(node_type),
                            "line": {"width": 1, "color": "white"},
                        },
                        text=trace_data["text"] if self.show_labels else None,
                        textposition="middle center",
                        textfont={"size": 8, "color": "white"},
                        hovertext=trace_data["hovertext"] if show_info else None,
                        hoverinfo="text" if show_info else "none",
                        name=node_type,
                        showlegend=True,
                    )
                )

    def _create_hover_text(self, node_id: str, data: dict) -> str:
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
        in_degree = self.graph.in_degree(node_id)
        out_degree = self.graph.out_degree(node_id)
        lines.append(f"Connections: {in_degree} in, {out_degree} out")

        return "<br>".join(lines)

    def _create_node_trace(
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
                hover_texts.append(self._create_hover_text(node_id, data))

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

    def _create_edge_trace(self, graph: nx.DiGraph, pos: dict) -> Optional[go.Scatter]:
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

    def _add_node_type_legend(self, fig: go.Figure) -> None:
        """Add a legend showing node type colors."""
        # This is handled automatically by the node traces
        pass

    def _create_empty_plot(self, title: str) -> go.Figure:
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
            width=self.width,
            height=self.height,
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        return fig

    def _create_error_plot(self, error_message: str) -> go.Figure:
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
            width=self.width,
            height=self.height,
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        return fig

    def _invalidate_cache(self) -> None:
        """Invalidate analysis cache."""
        self._analysis_cache.clear()
        self._cache_timestamp = 0


# Example usage and testing
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

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
        if viewer.export_graph(export_path, format="json"):
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
