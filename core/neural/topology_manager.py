# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: topology_manager.py
# MODULE: core.adaptive_systems.crista_optimizer.topology_manager
# DESCRIPTION: Provides capabilities for managing and analyzing the topology of
#              a symbolic network, including metrics calculation, optimization
#              recommendations, and health monitoring for LUKHAS Cognitive AI.
# DEPENDENCIES: logging, numpy, typing, dataclasses, enum, .crista_optimizer, .symbolic_network
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import time  # For timestamping in record_optimization
from dataclasses import dataclass, field
from enum import Enum
from typing import Any  # Set, Optional not directly used by this file but good for consistency

import numpy as np
import structlog

# Assuming SymbolicNetwork is in symbolic_network.py and OptimizationMode in crista_optimizer.py
# Need to handle potential circular dependencies if they also import TopologyManager.
# For now, direct imports are assumed.
# ΛNOTE: Attempting to import OptimizationMode and SymbolicNetwork from
# local package. Includes fallback placeholders for these classes to
# handle potential ImportErrors, which might occur during isolated testing
# or if the module structure changes. This allows the module to load with
# default definitions for basic type hinting or functionality, though full
# operation would be impaired.

# TAG:core
# TAG:neural
# TAG:neuroplastic
# TAG:colony

try:
    from .crista_optimizer import OptimizationMode  # TODO: convert to absolute import
    from .symbolic_network import (
        SymbolicNetwork,  # This class uses SymbolicNode internally  # TODO: convert to absolute import
    )
except ImportError:
    logger_temp = structlog.get_logger(
        "ΛTRACE.core.adaptive_systems.crista_optimizer.topology_manager_import_fallback"
    )
    logger_temp.warning(
        "ΛTRACE: Could not import OptimizationMode or SymbolicNetwork. Using placeholders."
    )

    # Define placeholders if necessary

    class OptimizationMode(Enum):
        FISSION = "fission"
        FUSION = "fusion"
        STABILIZATION = "stabilization"
        ADAPTIVE = "adaptive"

    class SymbolicNetwork:
        pass  # Basic placeholder

# Initialize logger for ΛTRACE using structlog
# Assumes structlog is configured in a higher-level __init__.py (e.g., core/__init__.py)
logger = structlog.get_logger(
    "ΛTRACE.core.adaptive_systems.crista_optimizer.topology_manager"
)
logger.info("ΛTRACE: Initializing topology_manager module.")

# Enum for Network Health Status
# Enumerates the possible health statuses of the symbolic network.


class NetworkHealth(Enum):
    """Enumerates the possible health statuses of the symbolic network."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


logger.info(
    f"ΛTRACE: NetworkHealth Enum defined with values: {[health.value for health in NetworkHealth]}"
)

# Dataclass for Comprehensive Topology Metrics
# Stores a comprehensive set of metrics describing the network's topology and state.


@dataclass
class TopologyMetrics:
    """Stores a comprehensive set of metrics describing the network's topology and state."""

    node_count: int = 0
    connection_density: float = 0.0
    avg_error: float = 0.0
    avg_activity: float = 0.0
    total_entropy: float = 0.0
    clustering_coefficient: float = 0.0  # Measures local connectedness
    average_path_length: float = 0.0  # Average shortest path between node pairs
    network_efficiency: float = 0.0  # Composite measure of network performance
    timestamp: float = field(default_factory=time.time)
    logger.info("ΛTRACE: TopologyMetrics Dataclass defined.")

# Manages Network Topology and Optimization Strategies
# Manages the overall topology of a SymbolicNetwork. It analyzes network structure,
# calculates various metrics, recommends optimization strategies, assesses network health,
# identifies bottlenecks, and tracks optimization history.


class TopologyManager:
    """
    Manages the overall topology of a SymbolicNetwork. It analyzes network structure,
    calculates various metrics, recommends optimization strategies, assesses network health,
    identifies bottlenecks, and tracks optimization history.
    """

    # Initialization

    def __init__(self, network: SymbolicNetwork):
        """
        Initializes the TopologyManager with a reference to a SymbolicNetwork.
        Args:
            network (SymbolicNetwork): The symbolic network instance to manage.
        """
        self.network = network
        self.optimization_history: list[dict[str, Any]] = (
            []
        )  # Stores history of optimization operations
        self.logger = logger.getChild(
            "TopologyManager"
        )  # Instance-specific child logger

        # Thresholds for health assessment, could be made configurable
        self.health_thresholds: dict[NetworkHealth, dict[str, float]] = {
            NetworkHealth.EXCELLENT: {
                "error_max": 0.2,
                "activity_min": 0.8,
                "efficiency_min": 0.9,
            },
            NetworkHealth.GOOD: {
                "error_max": 0.4,
                "activity_min": 0.6,
                "efficiency_min": 0.7,
            },
            NetworkHealth.FAIR: {
                "error_max": 0.6,
                "activity_min": 0.4,
                "efficiency_min": 0.5,
            },
            NetworkHealth.POOR: {
                "error_max": 0.8,
                "activity_min": 0.2,
                "efficiency_min": 0.3,
            },
            # CRITICAL is typically defined as worse than POOR
        }
        self.logger.info(
            f"ΛTRACE: TopologyManager initialized for network. Health thresholds set. Current node count: {len(self.network.nodes)}"
        )

    # Method to analyze network topology

    def analyze_topology(self) -> TopologyMetrics:
        """
        Analyzes the current network topology and computes a comprehensive set of metrics.
        Returns:
            TopologyMetrics: An object containing various calculated metrics.
        """
        self.logger.info("ΛTRACE: Starting comprehensive topology analysis.")
        nodes_list = list(self.network.nodes.values())

        if not nodes_list:
            self.logger.warning(
                "ΛTRACE: Network is empty. Returning zeroed TopologyMetrics."
            )
            return TopologyMetrics(
                timestamp=time.time()
            )  # Return default (mostly zero) metrics

        # Basic metrics
        node_count = len(nodes_list)
        connection_count = len(self.network.connections)
        # Max possible connections in a directed graph (allowing self-loops, though typically not used for density)
        # Or for undirected: node_count * (node_count - 1) / 2
        # Assuming an undirected graph for density as per typical network science
        # measures.
        max_possible_connections = (
            node_count * (node_count - 1) / 2.0 if node_count > 1 else 0.0
        )
        connection_density = (
            connection_count / max_possible_connections
            if max_possible_connections > 0
            else 0.0
        )
        self.logger.debug(
            f"ΛTRACE: Basic metrics: Nodes={node_count}, Connections={connection_count}, "
            f"Density={connection_density:.4f}"
        )

        # Node-level aggregations
        avg_error = (
            np.mean([node.error_level for node in nodes_list]) if nodes_list else 0.0
        )
        avg_activity = (
            np.mean([node.activity_level for node in nodes_list]) if nodes_list else 0.0
        )
        total_entropy = sum(node.entropy for node in nodes_list)
        self.logger.debug(
            f"ΛTRACE: Aggregated metrics: AvgError={avg_error:.4f}, AvgActivity={avg_activity:.4f}, TotalEntropy={total_entropy:.4f}"
        )

        # Advanced topology metrics (can be computationally intensive for large
        # networks)
        clustering_coeff = self._calculate_clustering_coefficient()
        avg_path_len = self._calculate_average_path_length()
        # Network efficiency calculation might depend on the above metrics, so calculate it last or pass them.
        # The original _calculate_network_efficiency called
        # self.analyze_topology() recursively. This is fixed.
        temp_metrics_for_efficiency = TopologyMetrics(  # Create a temporary metrics object for efficiency calculation
            node_count=node_count,
            connection_density=connection_density,
            avg_error=avg_error,
            avg_activity=avg_activity,
            total_entropy=total_entropy,
            clustering_coefficient=clustering_coeff,
            average_path_length=avg_path_len,
        )
        network_eff = self._calculate_network_efficiency_from_metrics(
            temp_metrics_for_efficiency
        )

        self.logger.debug(
            f"ΛTRACE: Advanced metrics: ClusteringCoeff={clustering_coeff:.4f}, "
            f"AvgPathLength={avg_path_len:.4f}, NetworkEfficiency={network_eff:.4f}"
        )

        final_metrics = TopologyMetrics(
            node_count=node_count,
            connection_density=connection_density,
            avg_error=avg_error,
            avg_activity=avg_activity,
            total_entropy=total_entropy,
            clustering_coefficient=clustering_coeff,
            average_path_length=avg_path_len,  # Renamed from path_length for clarity
            network_efficiency=network_eff,
            timestamp=time.time(),
        )
        self.logger.info(
            f"ΛTRACE: Topology analysis complete. Metrics: {final_metrics}"
        )
        return final_metrics

    # Private method to calculate clustering coefficient

    def _calculate_clustering_coefficient(self) -> float:
        """Calculates the average clustering coefficient of the network."""
        self.logger.debug("ΛTRACE: Calculating clustering coefficient.")
        if (
            len(self.network.nodes) < 3
        ):  # Clustering requires at least 3 nodes for non-zero results typically
            self.logger.debug(
                "ΛTRACE: Network too small for meaningful clustering coefficient; returning 0.0."
            )
            return 0.0

        total_node_coefficient_sum = 0.0
        nodes_with_degree_ge_2 = 0  # Count of nodes with degree >= 2

        for node_id_str in self.network.nodes:
            neighbors_list = self._get_neighbors(node_id_str)  # Already logs
            k_i = len(neighbors_list)  # Degree of node i

            if k_i < 2:  # Node needs at least 2 neighbors to form a triangle:
                continue

            nodes_with_degree_ge_2 += 1
            triangles_count = 0  # Number of triangles involving this node
            # Iterate over pairs of neighbors
            for i, neighbor1_id in enumerate(neighbors_list):
                for j in range(
                    i + 1, k_i
                ):  # Avoid redundant pairs and self-loops with i+1
                    neighbor2_id = neighbors_list[j]
                    # Check if these two neighbors are connected
                    if self._are_connected(neighbor1_id, neighbor2_id):  # Already logs:
                        triangles_count += 1

            # Local clustering coefficient for this node
            # Max possible triangles for node i is k_i * (k_i - 1) / 2
            max_possible_triangles = k_i * (k_i - 1) / 2.0
            if max_possible_triangles > 0:
                local_coeff = triangles_count / max_possible_triangles
                total_node_coefficient_sum += local_coeff
                self.logger.debug(
                    f"ΛTRACE: Node '{node_id_str}' local clustering coeff: {local_coeff:.4f} (Triangles: {triangles_count}, MaxPossible: {max_possible_triangles})"
                )
            else:
                self.logger.debug(
                    f"ΛTRACE: Node '{node_id_str}' has < 2 possible triangles, "
                    "local coeff is 0."
                )

        # Average clustering coefficient
        avg_coeff = (
            total_node_coefficient_sum / nodes_with_degree_ge_2
            if nodes_with_degree_ge_2 > 0
            else 0.0
        )
        self.logger.debug(
            f"ΛTRACE: Average clustering coefficient calculated: {avg_coeff:.4f} over {nodes_with_degree_ge_2} nodes."
        )
        return avg_coeff

    # Private method to calculate average path length

    def _calculate_average_path_length(self) -> float:
        """Calculates the average shortest path length between all pairs of nodes in the network."""
        self.logger.debug("ΛTRACE: Calculating average shortest path length.")
        node_ids_list = list(self.network.nodes.keys())
        if (
            len(node_ids_list) < 2
        ):  # Path length is undefined or 0 for networks with < 2 nodes
            self.logger.debug(
                "ΛTRACE: Network too small for meaningful average path length; returning 0.0."
            )
            return 0.0

        total_shortest_path_sum = 0
        num_paths_calculated = 0

        # Using BFS from each node to find all shortest paths
        for i, source_node_id in enumerate(node_ids_list):
            # Optimization: Only calculate for pairs (i, j) where j > i for undirected assumption
            # If graph is directed, need to run BFS from all nodes to all other nodes.
            # Assuming undirected for average path length as typical in network science.
            # The _bfs_distances calculates distances from one source to all reachable
            # nodes.
            distances_from_source = self._bfs_distances(source_node_id)  # Already logs
            for j in range(i + 1, len(node_ids_list)):
                target_node_id = node_ids_list[j]
                if target_node_id in distances_from_source:  # If target is reachable:
                    path_len = distances_from_source[target_node_id]
                    total_shortest_path_sum += path_len
                    num_paths_calculated += 1
                    self.logger.debug(
                        f"ΛTRACE: Path from '{source_node_id}' to '{target_node_id}' length: {path_len}"
                    )
                # else: target is not reachable from source in this component. Path length could be considered infinite.
                # For simplicity, we only average over reachable pairs. Some definitions
                # might handle this differently.

        avg_len = (
            total_shortest_path_sum / num_paths_calculated
            if num_paths_calculated > 0
            else float("inf")
        )
        self.logger.debug(
            f"ΛTRACE: Average shortest path length calculated: {avg_len:.4f} over {num_paths_calculated} paths."
        )
        return avg_len

    # Private method to calculate network efficiency from pre-calculated metrics

    def _calculate_network_efficiency_from_metrics(
        self, current_metrics: TopologyMetrics
    ) -> float:
        """
        Calculates network efficiency based on pre-computed metrics.
        This avoids recursive calls to analyze_topology.
        """
        self.logger.debug(
            f"ΛTRACE: Calculating network efficiency from metrics: {current_metrics}"
        )

        # Weighted combination of factors
        # Ensure connection_density is not overly dominant if it's very high
        connectivity_factor = min(current_metrics.connection_density * 2.0, 1.0)
        # Performance factor: high activity and low error are good
        performance_factor = (
            1.0 - current_metrics.avg_error
        ) * current_metrics.avg_activity
        # Structural factor: higher clustering is generally good for local efficiency
        structure_factor = current_metrics.clustering_coefficient

        # Penalize very long path lengths (or disconnected components where path_length is inf)
        # If path_length is inf, this penalty becomes 0. If 0, penalty is 1.
        path_penalty = (
            1.0 / (1.0 + current_metrics.average_path_length)
            if (current_metrics.average_path_length != float("inf")
                and current_metrics.average_path_length >= 0)
            else 0.0
        )

        self.logger.debug(
            f"ΛTRACE: Efficiency factors: Connectivity={connectivity_factor:.2f}, "
            f"Performance={performance_factor:.2f}, Structure={structure_factor:.2f}, PathPenalty={path_penalty:.2f}"
        )

        # Weights for each factor, summing to 1.0
        # These weights can be tuned based on system priorities
        efficiency = (
            connectivity_factor * 0.3
            + performance_factor * 0.4
            + structure_factor * 0.2
            + path_penalty * 0.1
        )

        final_efficiency = max(
            0.0, min(efficiency, 1.0)
        )  # Ensure efficiency is between 0 and 1
        self.logger.debug(
            f"ΛTRACE: Calculated network efficiency: {final_efficiency:.4f}"
        )
        return final_efficiency

    # Private helper to get neighbors of a node

    def _get_neighbors(self, node_id_str: str) -> list[str]:
        """Gets all unique neighbors of a given node (nodes it's connected to or from)."""
        self.logger.debug(f"ΛTRACE: Getting neighbors for node '{node_id_str}'.")
        if node_id_str not in self.network.nodes:
            self.logger.warning(
                f"ΛTRACE: Node '{node_id_str}' not found in network when getting neighbors."
            )
            return []

        neighbors_set: set[str] = set()
        # Check connections where node_id_str is the source
        for src, dst in self.network.connections:
            if src == node_id_str:
                neighbors_set.add(dst)
            # Also consider connections where node_id_str is the destination (for
            # undirected sense)
            elif dst == node_id_str:
                neighbors_set.add(src)

        # Also check the node's own connection list, which should be authoritative for outgoing
        # This might be redundant if self.network.connections is perfectly synced, but good for robustness.
        # node_obj = self.network.nodes.get(node_id_str)
        # if node_obj:
        #     for conn_target in node_obj.connections:
        #         neighbors_set.add(conn_target)

        self.logger.debug(
            f"ΛTRACE: Node '{node_id_str}' has {len(neighbors_set)} unique neighbors: "
            f"{list(neighbors_set)[:5]}{'...' if len(neighbors_set) > 5 else ''}"
        )
        return list(neighbors_set)

    # Private helper to check if two nodes are connected

    def _are_connected(self, node1_id: str, node2_id: str) -> bool:
        """Checks if two nodes are directly connected (in either direction)."""
        self.logger.debug(
            f"ΛTRACE: Checking direct connection between '{node1_id}' and '{node2_id}'."
        )
        # This check assumes connections list stores directed edges.
        # For an undirected sense (common in clustering coeff), check both directions.
        is_conn = (node1_id, node2_id) in self.network.connections or (
            node2_id,
            node1_id,
        ) in self.network.connections
        self.logger.debug(
            f"ΛTRACE: Connection status between '{node1_id}' and '{node2_id}': {is_conn}."
        )
        return is_conn

    # Private helper for BFS distances

    def _bfs_distances(self, source_node_id: str) -> dict[str, int]:
        """Calculates shortest path distances from a source node using Breadth-First Search."""
        self.logger.debug(f"ΛTRACE: Starting BFS from source node '{source_node_id}'.")
        if source_node_id not in self.network.nodes:
            self.logger.warning(
                f"ΛTRACE: Source node '{source_node_id}' for BFS not found in network."
            )
            return {}

        distances: dict[str, int] = {source_node_id: 0}
        queue: list[str] = [source_node_id]
        visited_nodes: set[str] = {source_node_id}

        head = 0  # Use index for queue to avoid list.pop(0) inefficiency on large lists
        while head < len(queue):
            current_node_id = queue[head]
            head += 1
            current_node_dist = distances[current_node_id]

            for neighbor_id in self._get_neighbors(
                current_node_id
            ):  # _get_neighbors already logs
                if neighbor_id not in visited_nodes:
                    visited_nodes.add(neighbor_id)
                    distances[neighbor_id] = current_node_dist + 1
                    queue.append(neighbor_id)
                    self.logger.debug(
                        f"ΛTRACE: BFS: Reached '{neighbor_id}' from '{source_node_id}', distance {distances[neighbor_id]}."
                    )

        self.logger.debug(
            f"ΛTRACE: BFS from '{source_node_id}' complete. Found distances to {len(distances)-1} other nodes."
        )
        return distances

    # Method to recommend optimization strategy

    def recommend_optimization(
        self, current_metrics: TopologyMetrics
    ) -> OptimizationMode:
        """
        Recommends an optimization strategy based on comprehensive network metrics.
        Args:
            current_metrics (TopologyMetrics): The current calculated metrics of the network.
        Returns:
            OptimizationMode: The suggested optimization mode.
        """
        self.logger.info(
            f"ΛTRACE: Recommending optimization strategy based on metrics: {current_metrics}"
        )

        # Priority 1: High error often requires fission to reduce load/complexity
        # on nodes
        if current_metrics.avg_error > self.network.config.fission_threshold:
            self.logger.info(
                "ΛTRACE: Recommendation: FISSION (due to high average error)."
            )
            return OptimizationMode.FISSION

        # Priority 2: Low activity coupled with reasonable density might indicate fusion opportunity
        # Density check helps avoid fusing an already sparse network further.
        # Threshold for "reasonable density" can be tuned (e.g. > 0.1 or > 0.05)
        if (
            current_metrics.avg_activity < self.network.config.fusion_threshold
            and current_metrics.connection_density > 0.05
        ):
            self.logger.info(
                "ΛTRACE: Recommendation: FUSION (due to low activity and sufficient density)."
            )
            return OptimizationMode.FUSION

        # Priority 3: Poor overall efficiency or structural issues (low clustering) might need adaptive changes
        # "Adaptive" could imply a more complex strategy or a mix, perhaps decided by CristaOptimizer itself.
        # Thresholds for "poor efficiency" (e.g. < 0.5) and "low clustering" (e.g.
        # < 0.3) can be tuned.
        if (
            current_metrics.network_efficiency < 0.5
            or current_metrics.clustering_coefficient < 0.2
        ):
            self.logger.info(
                "ΛTRACE: Recommendation: ADAPTIVE (due to low efficiency or clustering)."
            )
            return OptimizationMode.ADAPTIVE

        # Default: If no pressing issues, stabilize and maintain.
        self.logger.info(
            "ΛTRACE: Recommendation: STABILIZATION (default maintenance mode)."
        )
        return OptimizationMode.STABILIZATION

    # Method to assess network health

    def assess_network_health(self, current_metrics: TopologyMetrics) -> NetworkHealth:
        """
        Assesses the overall health of the network based on comprehensive metrics and predefined thresholds.
        Args:
            current_metrics (TopologyMetrics): The current calculated metrics of the network.
        Returns:
            NetworkHealth: The assessed health status of the network.
        """
        self.logger.info(
            f"ΛTRACE: Assessing network health based on metrics: {current_metrics}"
        )

        # Calculate a composite health score (0-1 range, higher is better)
        # Weights can be adjusted based on what's most critical for system health.
        # Error is inverted (1 - error) so higher is better.
        error_score_component = (1.0 - current_metrics.avg_error) * 0.4
        activity_score_component = current_metrics.avg_activity * 0.3
        efficiency_score_component = current_metrics.network_efficiency * 0.3

        overall_health_score = (
            error_score_component
            + activity_score_component
            + efficiency_score_component
        )
        overall_health_score = max(
            0.0, min(1.0, overall_health_score)
        )  # Clamp to [0,1]
        self.logger.debug(
            f"ΛTRACE: Health components: ErrorScoreComp={error_score_component:.2f}, "
            f"ActivityScoreComp={activity_score_component:.2f}, EfficiencyScoreComp={efficiency_score_component:.2f}. "
            f"Overall Health Score: {overall_health_score:.2f}"
        )

        # Determine health level based on score and potentially critical
        # individual metrics
        if (
            current_metrics.avg_error
            > self.health_thresholds[NetworkHealth.POOR]["error_max"]
        ):  # If error is beyond "poor"
            health = NetworkHealth.CRITICAL
        elif (
            overall_health_score >= 0.8
            and current_metrics.avg_error
            < self.health_thresholds[NetworkHealth.EXCELLENT]["error_max"]
        ):  # Example: Excellent score AND low error
            health = NetworkHealth.EXCELLENT
        elif (
            overall_health_score >= 0.6
            and current_metrics.avg_error
            < self.health_thresholds[NetworkHealth.GOOD]["error_max"]
        ):
            health = NetworkHealth.GOOD
        elif (
            overall_health_score >= 0.4
            and current_metrics.avg_error
            < self.health_thresholds[NetworkHealth.FAIR]["error_max"]
        ):
            health = NetworkHealth.FAIR
        elif overall_health_score >= 0.2:
            health = NetworkHealth.POOR
        else:
            health = NetworkHealth.CRITICAL

        self.logger.info(
            f"ΛTRACE: Network health assessed as: {health.value} (Score: {overall_health_score:.2f})"
        )
        return health

    # Method to identify network bottlenecks

    def identify_bottlenecks(self) -> list[dict[str, Any]]:
        """
        Identifies potential bottlenecks or performance issues within the network,
        such as high-error nodes, isolated nodes, or overconnected nodes.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each describing a bottleneck.
        """
        self.logger.info("ΛTRACE: Identifying network bottlenecks.")
        identified_bottlenecks: list[dict[str, Any]] = []
        node_values = list(self.network.nodes.values())  # Avoid re-iterating .values()

        # Bottleneck Type 1: High error nodes
        high_error_threshold = 0.8  # Configurable
        for node in node_values:
            if node.error_level > high_error_threshold:
                bottleneck_info = {
                    "type": "high_error_node",
                    "node_id": node.node_id,
                    "error_level": node.error_level,
                    "severity_score": node.error_level,  # Use error level as severity
                    "recommendation": "Investigate cause of error; consider node splitting or error correction mechanisms.",
                }
                identified_bottlenecks.append(bottleneck_info)
                self.logger.debug(
                    f"ΛTRACE: Bottleneck(High Error): Node '{node.node_id}', Error: {node.error_level:.2f}"
                )

        # Bottleneck Type 2: Isolated nodes (very low degree/connectivity)
        # Degree is number of neighbors. Threshold for "isolated" can be tuned.
        isolated_degree_threshold = 1  # Nodes with degree < 2 (0 or 1 connection)
        node_degrees_map: dict[str, int] = {
            node_id: len(self._get_neighbors(node_id)) for node_id in self.network.nodes
        }

        for node_id_str, degree in node_degrees_map.items():
            if degree < isolated_degree_threshold:
                severity = (
                    1.0 - (degree / isolated_degree_threshold)
                    if isolated_degree_threshold > 0
                    else 1.0
                )
                bottleneck_info = {
                    "type": "isolated_node",
                    "node_id": node_id_str,
                    "degree": degree,
                    "severity_score": severity,
                    "recommendation": "Review node purpose; consider increasing connectivity or merging if redundant.",
                }
                identified_bottlenecks.append(bottleneck_info)
                self.logger.debug(
                    f"ΛTRACE: Bottleneck(Isolated): Node '{node_id_str}', Degree: {degree}"
                )

        # Bottleneck Type 3: Overconnected nodes (potential congestion points or "hubs")
        # "Overconnected" could be relative to average degree or an absolute threshold.
        avg_network_degree = (
            np.mean(list(node_degrees_map.values())) if node_degrees_map else 0.0
        )
        overconnected_factor = 3.0  # e.g., degree > 3 * average
        min_degree_for_overconnected_check = (
            5  # Don't flag nodes in very small/sparse nets as overconnected easily
        )

        if avg_network_degree > 0:  # Only if average degree is meaningful
            for node_id_str, degree in node_degrees_map.items():
                if degree > max(
                    min_degree_for_overconnected_check,
                    avg_network_degree * overconnected_factor,
                ):
                    severity = (
                        min(
                            degree / (avg_network_degree * overconnected_factor),
                            1.0,
                        )
                        if avg_network_degree > 0
                        else 0.5
                    )
                    bottleneck_info = {
                        "type": "overconnected_node",
                        "node_id": node_id_str,
                        "degree": degree,
                        "avg_degree_ref": avg_network_degree,
                        "severity_score": severity,
                        "recommendation": "Assess load on this node; consider load balancing strategies or targeted fission.",
                    }
                    identified_bottlenecks.append(bottleneck_info)
                    self.logger.debug(
                        f"ΛTRACE: Bottleneck(Overconnected): Node '{node_id_str}', "
                        f"Degree: {degree} (Avg: {avg_network_degree:.2f})"
                    )

        # Sort bottlenecks by severity for prioritization
        sorted_bottlenecks = sorted(
            identified_bottlenecks,
            key=lambda x: x["severity_score"],
            reverse=True,
        )
        self.logger.info(
            f"ΛTRACE: Identified {len(sorted_bottlenecks)} potential bottlenecks. Top severity: {sorted_bottlenecks[0]['severity_score'] if sorted_bottlenecks else 'N/A'}"
        )
        return sorted_bottlenecks

    # Method to suggest topology improvements

    def suggest_topology_improvements(
        self, current_metrics: TopologyMetrics
    ) -> list[str]:
        """
        Suggests specific, human-readable improvements to the network topology
        based on its current state and metrics.
        Args:
            current_metrics (TopologyMetrics): The current calculated metrics of the network.
        Returns:
            List[str]: A list of string suggestions for improvement.
        """
        self.logger.info(
            f"ΛTRACE: Suggesting topology improvements based on metrics: {current_metrics}"
        )
        improvement_suggestions: list[str] = []

        # Density suggestions
        if current_metrics.connection_density < 0.1:  # Threshold for "too sparse"
            improvement_suggestions.append(
                "Increase overall network connectivity; the network appears too sparse, potentially leading to fragmentation."
            )
        elif current_metrics.connection_density > 0.8:  # Threshold for "too dense":
            improvement_suggestions.append(
                "Consider reducing overall network connectivity if resource usage is high; the network is very dense."
            )

        # Clustering suggestions
        if current_metrics.clustering_coefficient < 0.2:  # Threshold for low local clustering
            improvement_suggestions.append(
                "Improve local clustering by forming more triangular connections between nodes; this can enhance local information processing efficiency."
            )

        # Path length suggestions
        if (
            current_metrics.average_path_length > 5.0
            and current_metrics.average_path_length != float("inf")
        ):  # Threshold for long paths
            improvement_suggestions.append(
                "Reduce average path length by introducing shortcut connections or hub-like nodes to improve global information flow."
            )
        elif current_metrics.average_path_length == float("inf"):
            improvement_suggestions.append(
                "Network may be fragmented (disconnected components); ensure critical paths exist or bridge components."
            )

        # Error and Activity suggestions (covered by recommend_optimization but
        # can be explicit here too)
        if current_metrics.avg_error > 0.6:  # High average error:
            improvement_suggestions.append(
                "Address high average error rates across the network; investigate sources of error and consider node fission or targeted error correction."
            )
        if current_metrics.avg_activity < 0.3:  # Low average activity:
            improvement_suggestions.append(
                "Increase average node activity; consider merging underutilized nodes or adjusting task routing to activate dormant areas."
            )

        # Efficiency suggestions
        if current_metrics.network_efficiency < 0.4:  # Low overall efficiency
            improvement_suggestions.append(
                "Optimize overall network efficiency by balancing connectivity, performance (error/activity), and structural properties like path length and clustering."
            )

        if not improvement_suggestions:
            improvement_suggestions.append(
                "Network topology appears relatively balanced based on current metrics. Continue monitoring."
            )

        self.logger.info(
            f"ΛTRACE: Generated {len(improvement_suggestions)} topology improvement suggestions."
        )
        return improvement_suggestions

    # Method to record optimization history

    def record_optimization(self, optimization_result_dict: dict[str, Any]) -> None:
        """
        Records the results of an optimization operation in the manager's history.
        Args:
            optimization_result_dict (Dict[str, Any]): A dictionary containing details of the optimization.
        """
        self.logger.debug(
            f"ΛTRACE: Recording optimization result: {optimization_result_dict.get('operation_type', 'N/A')}"
        )
        # Ensure metrics are TopologyMetrics objects or serializable dicts
        # The provided dict might contain TopologyMetrics objects directly, or dict representations.
        # For storage, it's often better to store the dict representation.

        metrics_before = optimization_result_dict.get("initial_metrics")
        metrics_after = optimization_result_dict.get("final_metrics")

        record = {
            "timestamp": time.time(),  # Use current time for record
            "operation_type": optimization_result_dict.get("operation_type"),
            # Convert TopologyMetrics to dict if they are objects for consistent storage
            "metrics_before": (
                metrics_before.__dict__
                if isinstance(metrics_before, TopologyMetrics)
                else metrics_before
            ),
            "metrics_after": (
                metrics_after.__dict__
                if isinstance(metrics_after, TopologyMetrics)
                else metrics_after
            ),
            "success": optimization_result_dict.get("success", False),
            "nodes_affected": optimization_result_dict.get("nodes_affected", 0),
            "error_reduction_cycle": optimization_result_dict.get(
                "error_reduction_cycle", 0.0
            ),
        }
        self.optimization_history.append(record)

        # Limit the size of the optimization history to save memory
        max_history_size = 100
        if len(self.optimization_history) > max_history_size:
            self.optimization_history = self.optimization_history[-max_history_size:]
        self.logger.info(
            f"ΛTRACE: Optimization result recorded. History size: {len(self.optimization_history)}."
        )

    # Method to get optimization trends

    def get_optimization_trends(self) -> dict[str, Any]:
        """
        Analyzes the recent optimization history to identify trends in operations,
        success rates, and error levels.
        Returns:
            Dict[str, Any]: A dictionary summarizing observed trends.
        """
        self.logger.debug("ΛTRACE: Analyzing optimization trends.")
        if not self.optimization_history:
            self.logger.info(
                "ΛTRACE: No optimization history available to analyze trends."
            )
            return {"trend_status": "no_data_available"}

        # Analyze the last N operations (e.g., last 10 or 20)
        num_recent_ops_to_analyze = min(len(self.optimization_history), 20)
        recent_ops = self.optimization_history[-num_recent_ops_to_analyze:]

        # Should not happen if self.optimization_history is not empty, but defensive.
        if not recent_ops:
            self.logger.info(
                "ΛTRACE: No recent operations found in history for trend analysis."
            )
            return {"trend_status": "no_recent_data"}

        operation_types_list = [
            op["operation_type"] for op in recent_ops if op.get("operation_type")
        ]
        successful_ops_count = sum(1 for op in recent_ops if op.get("success", False))
        success_rate_recent = (
            successful_ops_count / len(recent_ops) if recent_ops else 0.0
        )

        # Analyze error trend from 'metrics_after'
        avg_errors_after_ops = [
            op["metrics_after"]["avg_error"]
            for op in recent_ops
            if op.get("metrics_after") and "avg_error" in op["metrics_after"]
        ]

        error_trend_direction = "stable"
        if len(avg_errors_after_ops) >= 2:  # Need at least two points to determine a trend
            # Compare first half avg vs second half avg for robustness
            mid = len(avg_errors_after_ops) // 2
            first_half_avg_error = np.mean(avg_errors_after_ops[:mid])
            second_half_avg_error = np.mean(avg_errors_after_ops[mid:])

            if second_half_avg_error < first_half_avg_error * 0.95:  # Significant improvement (>5% reduction)
                error_trend_direction = "improving"
            elif second_half_avg_error > first_half_avg_error * 1.05:  # Significant degradation (>5% increase)
                error_trend_direction = "degrading"
        else:
            # Single point or none
            first_half_avg_error = avg_errors_after_ops[0] if avg_errors_after_ops else 0.0
            second_half_avg_error = first_half_avg_error

        dominant_op = None
        if operation_types_list:
            from collections import Counter

            dominant_op_counter = Counter(operation_types_list)
            dominant_op = (
                dominant_op_counter.most_common(1)[0][0]
                if dominant_op_counter
                else None
            )

        trends_summary = {
            "analysis_window_size": len(recent_ops),
            "error_trend_direction": error_trend_direction,
            "average_errors_in_window": avg_errors_after_ops,
            "recent_success_rate": success_rate_recent,
            "dominant_operation_type_recent": dominant_op,
            "operation_type_counts_recent": (
                dict(Counter(operation_types_list)) if operation_types_list else {}
            ),
        }
        self.logger.info(f"ΛTRACE: Optimization trends analyzed: {trends_summary}")
        return trends_summary

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: topology_manager.py
# VERSION: 1.1.0 # Assuming evolution from a prior version
# TIER SYSTEM: Tier 2-4 (Advanced analysis and management component)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Network topology analysis (density, clustering, path length, efficiency),
#               Optimization strategy recommendation, Network health assessment,
#               Bottleneck identification, Topology improvement suggestions,
#               Optimization history tracking and trend analysis.
# FUNCTIONS: None directly exposed at module level.
# CLASSES: NetworkHealth (Enum), TopologyMetrics (Dataclass), TopologyManager.
# DECORATORS: @dataclass.
# DEPENDENCIES: logging, numpy, typing, dataclasses, enum, time,
#               .crista_optimizer (for OptimizationMode),
#               .symbolic_network (for SymbolicNetwork).
# INTERFACES: TopologyManager class is the main interface.
# ERROR HANDLING: Handles empty networks gracefully in metric calculations.
#                 More specific error handling for complex graph algorithms could be added.
# LOGGING: ΛTRACE_ENABLED via Python's logging module for detailed tracing of analyses and recommendations.
# AUTHENTICATION: Not applicable at this component level.
# HOW TO USE:
#   from core.adaptive_systems.crista_optimizer.topology_manager import TopologyManager, TopologyMetrics
#   from core.adaptive_systems.crista_optimizer.symbolic_network import SymbolicNetwork # and NetworkConfig
#   # ... (assuming network is an initialized SymbolicNetwork instance) ...
#   topo_manager = TopologyManager(network)
#   metrics = topo_manager.analyze_topology()
#   health = topo_manager.assess_network_health(metrics)
#   recommendation = topo_manager.recommend_optimization(metrics)
# INTEGRATION NOTES: This manager relies heavily on a well-defined SymbolicNetwork.
#                    Its calculations (clustering, path length) can be intensive on large networks;
#                    consider sampling or approximations for real-time use if performance is an issue.
# MAINTENANCE: Regularly review and tune thresholds for health assessment and optimization recommendations.
#              Update graph algorithms if more performant or accurate methods are needed.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
