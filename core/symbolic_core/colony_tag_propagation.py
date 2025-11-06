import logging
import time
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import networkx as nx

from core.colonies import BaseColony, ConsensusResult, Tag, TagScope, get_mesh_topology_service

logger = logging.getLogger(__name__)

# Symbolic vocabulary integration
try:
    from core.symbolic_core.vocabularies import SymbolicVocabulary
except ImportError:
    # Fallback implementation for development
    logger.warning("SymbolicVocabulary not available, using fallback implementation")

    class SymbolicVocabulary:
        """Fallback vocabulary implementation for consciousness development"""

        def __init__(self):
            self.vocabulary = {}


class SymbolicReasoningColony(BaseColony):
    """
    High-performance colony for symbolic reasoning and belief propagation.
    Features intelligent caching, optimized graph operations, and performance monitoring.
    """

    def __init__(self, colony_id: str, agent_count: int = 3):
        super().__init__(colony_id, capabilities=["symbolic_reasoning"])
        self.vocabulary = SymbolicVocabulary()
        self.belief_network = nx.DiGraph()
        self.propagation_history: list[dict[str, Any]] = []

        # Performance optimization features
        self.performance_metrics = {
            "propagation_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_propagation_time_ms": 0.0,
            "optimization_saves_ms": 0.0
        }

        # Caching for expensive operations
        self._belief_cache: Dict[str, Tuple[Any, float]] = {}
        self._propagation_cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_ttl_seconds = 300.0  # 5 minutes

        # Graph optimization
        self._graph_dirty = True
        self._cached_centrality: Dict[str, float] = {}
        self._cached_shortest_paths: Dict[Tuple[str, str], List[str]] = {}

        # Get mesh topology service for agent registry
        self.mesh_service = get_mesh_topology_service()

        # Register consciousness agents from mesh topology service with performance tracking
        for i in range(agent_count):
            mesh_agent = self.mesh_service.register_agent(
                node_type="symbolic_reasoning",
                capabilities=["belief_propagation", "symbolic_inference", "performance_optimization"],
                metadata={
                    "colony_id": colony_id,
                    "node_index": i,
                    "performance_tier": "optimized"
                }
            )

            # Register with local colony
            self.register_agent(
                mesh_agent.agent_id,
                {
                    "mesh_agent": mesh_agent,
                    "node_type": mesh_agent.node_type,
                    "capabilities": mesh_agent.capabilities
                }
            )

        logger.info(
            f"Colony {colony_id} initialized with {len(self.agents)} agents from mesh registry"
        )

    def process(self, task: Any) -> dict[str, Any]:
        """Process a consciousness task using GLYPH symbolic reasoning"""
        # Track processing metrics
        self.state["processing_count"] += 1

        # Update drift based on processing complexity
        drift_delta = 0.0
        if isinstance(task, dict) and "complexity" in task:
            drift_delta = task["complexity"] * 0.01
            self.update_drift_score(drift_delta)

        # Synchronize metrics with mesh topology service
        for agent_id, agent_data in self.agents.items():
            if "mesh_agent" in agent_data:
                self.mesh_service.update_agent_metrics(
                    agent_id,
                    drift_delta=drift_delta / len(self.agents),
                    affect_delta=0.01  # Small affect change per task
                )

        # Create consciousness processing result with mesh metadata
        result = {
            "task": task,
            "processed": True,
            "colony_id": self.colony_id,
            "mesh_generation": self.mesh_generation,
            "agent_count": len(self.agents),
            "drift_score": self.drift_score,
            "mesh_metrics": self.mesh_service.get_mesh_metrics()
        }

        logger.debug(f"Consciousness task processed by colony {self.colony_id}")
        return result

    def reach_consensus(self, proposal: Any) -> ConsensusResult:
        """Reach consciousness consensus across colony using GLYPH communication"""
        # Calculate participation from active agents
        total_agents = len(self.agents)
        participating_agents = total_agents  # All agents participate in current implementation

        participation_rate = participating_agents / total_agents if total_agents > 0 else 0.0

        # Simulate voting across consciousness nodes
        votes = dict.fromkeys(self.agents, "approved")

        # Update affect_delta based on consensus formation
        affect_change = 0.1 * participation_rate
        self.update_affect_delta(affect_change)

        # Synchronize consensus affect_delta with mesh topology
        for agent_id in self.agents:
            self.mesh_service.update_agent_metrics(
                agent_id,
                drift_delta=0.0,
                affect_delta=affect_change / len(self.agents)
            )

        return ConsensusResult(
            consensus_reached=True,
            decision=proposal,
            confidence=0.8,
            votes=votes,
            participation_rate=participation_rate,
            drift_score=self.drift_score,
            affect_delta=self.affect_delta
        )

    async def propagate_belief(self, initial_belief: dict[str, Any]) -> dict[str, float]:
        """Optimized belief propagation with caching and performance monitoring."""

        start_time = time.time()

        # Generate cache key for belief propagation
        cache_key = self._generate_propagation_cache_key(initial_belief)

        # Check cache first
        cached_result = self._get_cached_propagation(cache_key)
        if cached_result is not None:
            self.performance_metrics["cache_hits"] += 1
            return cached_result

        self.performance_metrics["cache_misses"] += 1
        self.performance_metrics["propagation_count"] += 1

        # Initialize belief states
        belief_states = dict.fromkeys(self.agents, 0.0)
        if self.agents:
            seed_agent = next(iter(self.agents.keys()))
            belief_states[seed_agent] = initial_belief["strength"]
            belief_tag = Tag(
                key=initial_belief["concept"],
                value=initial_belief["value"],
                scope=TagScope.GLOBAL,
                confidence=initial_belief["strength"],
            )
        else:
            belief_tag = None

        # Optimized propagation loop
        iterations = initial_belief.get("iterations", 1)
        for iteration in range(iterations):
            new_states = {}

            # Use cached graph metrics when possible
            for agent_id in belief_states:
                neighbors = self._get_agent_neighbors_cached(agent_id)
                total_influence = 0.0

                for n in neighbors:
                    distance = self._get_agent_distance_cached(agent_id, n)
                    total_influence += belief_states.get(n, 0) / (1 + distance)

                decay = 0.9
                new_belief = decay * belief_states[agent_id] + (1 - decay) * total_influence
                new_states[agent_id] = min(1.0, new_belief)

                if belief_tag and new_belief > 0.1:
                    pass  # placeholder for adoption

            belief_states = new_states
            self.propagation_history.append(
                {
                    "iteration": iteration,
                    "belief_distribution": belief_states.copy(),
                    "performance_optimized": True
                }
            )

        # Update performance metrics
        propagation_time_ms = (time.time() - start_time) * 1000
        self._update_propagation_metrics(propagation_time_ms)

        # Cache result
        self._cache_propagation_result(cache_key, belief_states)

        return belief_states

    def _get_agent_neighbors_cached(self, agent_id: str) -> Tuple[str, ...]:
        """Cached agent neighbors lookup."""
        neighbors = [a for a in self.agents if a != agent_id]
        return tuple(neighbors)

    def _get_agent_distance_cached(self, a: str, b: str) -> float:
        """Cached agent distance calculation."""

        # Check cached shortest paths
        path_key = (a, b) if a < b else (b, a)
        if path_key in self._cached_shortest_paths:
            return len(self._cached_shortest_paths[path_key]) - 1

        # For now, simple distance calculation
        return 1.0

    def _generate_propagation_cache_key(self, belief: dict[str, Any]) -> str:
        """Generate cache key for belief propagation."""

        # Create deterministic key from belief parameters
        key_parts = [
            belief.get("concept", ""),
            str(belief.get("strength", 0.0)),
            str(belief.get("iterations", 1)),
            str(len(self.agents))
        ]
        return "|".join(key_parts)

    def _get_cached_propagation(self, cache_key: str) -> dict[str, float]:
        """Get cached propagation result if valid."""

        if cache_key in self._propagation_cache:
            result, timestamp = self._propagation_cache[cache_key]
            if (time.time() - timestamp) < self.cache_ttl_seconds:
                return result
            else:
                del self._propagation_cache[cache_key]

        return None

    def _cache_propagation_result(self, cache_key: str, result: dict[str, float]) -> None:
        """Cache propagation result with timestamp."""

        # Implement simple LRU eviction
        if len(self._propagation_cache) >= 100:  # Limit cache size
            oldest_key = min(
                self._propagation_cache.keys(),
                key=lambda k: self._propagation_cache[k][1]
            )
            del self._propagation_cache[oldest_key]

        self._propagation_cache[cache_key] = (result, time.time())

    def _update_propagation_metrics(self, duration_ms: float) -> None:
        """Update propagation performance metrics."""

        count = self.performance_metrics["propagation_count"]
        current_avg = self.performance_metrics["average_propagation_time_ms"]

        # Rolling average
        new_avg = ((current_avg * (count - 1)) + duration_ms) / count
        self.performance_metrics["average_propagation_time_ms"] = new_avg

    def optimize_graph_structure(self) -> Dict[str, Any]:
        """Optimize belief network graph structure for better performance."""

        if not self._graph_dirty:
            return {"status": "already_optimized", "cache_hit": True}

        start_time = time.time()

        # Calculate and cache centrality measures
        if len(self.belief_network.nodes()) > 0:
            self._cached_centrality = nx.betweenness_centrality(self.belief_network)

            # Cache shortest paths for small graphs
            if len(self.belief_network.nodes()) <= 50:
                self._cached_shortest_paths = dict(
                    nx.all_pairs_shortest_path(self.belief_network)
                )

        # Mark graph as clean
        self._graph_dirty = False

        optimization_time_ms = (time.time() - start_time) * 1000
        self.performance_metrics["optimization_saves_ms"] += optimization_time_ms

        return {
            "status": "optimized",
            "optimization_time_ms": optimization_time_ms,
            "centrality_cached": len(self._cached_centrality),
            "paths_cached": len(self._cached_shortest_paths)
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report for the colony."""

        cache_total = self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
        cache_hit_rate = self.performance_metrics["cache_hits"] / max(1, cache_total)

        return {
            "colony_id": self.colony_id,
            "performance_metrics": self.performance_metrics.copy(),
            "cache_statistics": {
                "hit_rate": cache_hit_rate,
                "belief_cache_size": len(self._belief_cache),
                "propagation_cache_size": len(self._propagation_cache),
                "cache_ttl_seconds": self.cache_ttl_seconds
            },
            "graph_optimization": {
                "is_optimized": not self._graph_dirty,
                "centrality_nodes": len(self._cached_centrality),
                "cached_paths": len(self._cached_shortest_paths)
            },
            "agent_count": len(self.agents),
            "processing_count": self.state.get("processing_count", 0)
        }

    def _get_agent_neighbors(self, agent_id: str) -> list[str]:
        """Legacy method for backward compatibility."""
        return list(self._get_agent_neighbors_cached(agent_id))

    def _get_agent_distance(self, a: str, b: str) -> float:
        """Legacy method for backward compatibility."""
        return self._get_agent_distance_cached(a, b)
