"""
M.2 Federation Coordinator - Advanced distributed memory federation
Coordinates multiple distributed memory clusters with advanced governance and optimization.
"""

import asyncio
import contextlib
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from memory.distributed_memory import DistributedMemoryOrchestrator

logger = logging.getLogger(__name__)


class FederationState(Enum):
    """Federation states"""
    INITIALIZING = "initializing"
    FORMING = "forming"
    ACTIVE = "active"
    OPTIMIZING = "optimizing"
    DEGRADED = "degraded"
    EMERGENCY = "emergency"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for federation"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    GEOGRAPHIC = "geographic"
    SMART_ROUTING = "smart_routing"
    ADAPTIVE = "adaptive"


class FederationRole(Enum):
    """Node roles in federation"""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    OBSERVER = "observer"
    BACKUP_COORDINATOR = "backup_coordinator"


@dataclass
class FederationCluster:
    """Represents a cluster in the federation"""
    cluster_id: str
    coordinator_node: str
    member_nodes: Set[str]
    region: str
    capabilities: Set[str]
    load_factor: float = 0.0
    health_score: float = 1.0
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederationMetrics:
    """Federation-wide metrics"""
    total_clusters: int = 0
    total_nodes: int = 0
    total_memory_folds: int = 0
    average_latency_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    success_rate: float = 1.0
    federation_health: float = 1.0
    load_distribution_variance: float = 0.0


@dataclass
class CrossClusterOperation:
    """Cross-cluster operation tracking"""
    operation_id: str
    operation_type: str
    source_cluster: str
    target_clusters: Set[str]
    payload: Dict[str, Any]
    priority: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "executing", "completed", "failed"
    retry_count: int = 0


class FederationCoordinator:
    """
    M.2 Federation Coordinator
    Advanced coordinator for distributed memory federation with intelligent load balancing
    """

    def __init__(self,
                 federation_id: str,
                 local_orchestrator: DistributedMemoryOrchestrator,
                 load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE,
                 max_clusters: int = 10,
                 health_check_interval: int = 30):
        self.federation_id = federation_id
        self.local_orchestrator = local_orchestrator
        self.load_balancing_strategy = load_balancing_strategy
        self.max_clusters = max_clusters
        self.health_check_interval = health_check_interval

        # Federation state
        self.state = FederationState.INITIALIZING
        self.role = FederationRole.COORDINATOR  # Assume coordinator initially
        self.metrics = FederationMetrics()

        # Cluster management
        self.clusters: Dict[str, FederationCluster] = {}
        self.cluster_assignments: Dict[str, str] = {}  # node_id -> cluster_id
        self.load_balancer_state: Dict[str, Any] = {}

        # Cross-cluster operations
        self.pending_operations: Dict[str, CrossClusterOperation] = {}
        self.operation_history: deque = deque(maxlen=1000)

        # Optimization and monitoring
        self.performance_history: deque = deque(maxlen=1000)
        self.health_checks: Dict[str, datetime] = {}
        self.optimization_strategies: List[str] = []

        # Event handlers
        self.federation_event_handlers: Dict[str, List] = defaultdict(list)

        # Background tasks
        self.coordination_task: Optional[asyncio.Task] = None
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        self.load_balancer_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """Start the federation coordinator"""
        logger.info(f"🚀 Starting Federation Coordinator: {self.federation_id}")

        try:
            # Initialize local cluster
            await self._initialize_local_cluster()

            # Start coordination tasks
            self.coordination_task = asyncio.create_task(self._coordination_loop())
            self.health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
            self.optimization_task = asyncio.create_task(self._optimization_loop())
            self.load_balancer_task = asyncio.create_task(self._load_balancing_loop())

            # Discover existing federation
            await self._discover_federation()

            # Set state to active
            self.state = FederationState.ACTIVE

            logger.info(f"✅ Federation Coordinator started: {self.federation_id}")

        except Exception as e:
            self.state = FederationState.EMERGENCY
            logger.error(f"❌ Failed to start Federation Coordinator: {e}")
            raise

    async def stop(self):
        """Stop the federation coordinator"""
        logger.info(f"🛑 Stopping Federation Coordinator: {self.federation_id}")

        self._shutdown_event.set()

        # Cancel background tasks
        for task in [self.coordination_task, self.health_monitor_task,
                    self.optimization_task, self.load_balancer_task]:
            if task and not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        logger.info(f"✅ Federation Coordinator stopped: {self.federation_id}")

    async def join_federation(self, coordinator_address: str, coordinator_port: int) -> bool:
        """Join existing federation"""

        try:
            self.state = FederationState.FORMING

            # Contact federation coordinator
            join_request = {
                "federation_id": self.federation_id,
                "local_cluster": self._get_local_cluster_info(),
                "capabilities": list(self.local_orchestrator.local_node.capabilities),
                "request_timestamp": datetime.utcnow().isoformat()
            }

            # Simulate join request (would use actual network in production)
            join_response = await self._send_federation_join_request(
                coordinator_address, coordinator_port, join_request
            )

            if join_response.get("accepted"):
                # Process federation topology
                federation_topology = join_response.get("topology", {})
                await self._process_federation_topology(federation_topology)

                self.state = FederationState.ACTIVE
                logger.info(f"✅ Successfully joined federation: {self.federation_id}")
                return True
            else:
                logger.warning(f"⚠️ Federation join rejected: {join_response.get('reason', 'unknown')}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to join federation: {e}")
            self.state = FederationState.EMERGENCY
            return False

    async def create_federation(self) -> bool:
        """Create new federation as coordinator"""

        try:
            self.state = FederationState.FORMING
            self.role = FederationRole.COORDINATOR

            # Initialize local cluster as founding cluster
            local_cluster = await self._initialize_local_cluster()

            # Setup federation metadata
            {
                "federation_id": self.federation_id,
                "created_at": datetime.utcnow().isoformat(),
                "coordinator_cluster": local_cluster.cluster_id,
                "founding_node": self.local_orchestrator.node_id
            }

            self.state = FederationState.ACTIVE
            logger.info(f"✅ Created new federation: {self.federation_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create federation: {e}")
            self.state = FederationState.EMERGENCY
            return False

    async def add_cluster_to_federation(self, cluster_info: Dict[str, Any]) -> bool:
        """Add new cluster to federation"""

        if len(self.clusters) >= self.max_clusters:
            logger.warning(f"⚠️ Maximum clusters reached: {self.max_clusters}")
            return False

        cluster_id = cluster_info.get("cluster_id")
        if not cluster_id or cluster_id in self.clusters:
            return False

        # Create cluster object
        cluster = FederationCluster(
            cluster_id=cluster_id,
            coordinator_node=cluster_info.get("coordinator_node", ""),
            member_nodes=set(cluster_info.get("member_nodes", [])),
            region=cluster_info.get("region", "unknown"),
            capabilities=set(cluster_info.get("capabilities", [])),
            metadata=cluster_info.get("metadata", {})
        )

        self.clusters[cluster_id] = cluster

        # Update cluster assignments
        for node_id in cluster.member_nodes:
            self.cluster_assignments[node_id] = cluster_id

        # Trigger federation optimization
        await self._trigger_federation_optimization()

        self.metrics.total_clusters = len(self.clusters)
        self.metrics.total_nodes = sum(len(c.member_nodes) for c in self.clusters.values())

        logger.info(f"🏗️ Added cluster to federation: {cluster_id}")
        return True

    async def remove_cluster_from_federation(self, cluster_id: str) -> bool:
        """Remove cluster from federation"""

        if cluster_id not in self.clusters:
            return False

        cluster = self.clusters[cluster_id]

        # Remove cluster assignments
        for node_id in cluster.member_nodes:
            self.cluster_assignments.pop(node_id, None)

        # Remove cluster
        del self.clusters[cluster_id]

        # Trigger rebalancing
        await self._trigger_federation_optimization()

        self.metrics.total_clusters = len(self.clusters)
        self.metrics.total_nodes = sum(len(c.member_nodes) for c in self.clusters.values())

        logger.info(f"🗑️ Removed cluster from federation: {cluster_id}")
        return True

    async def route_memory_operation(self,
                                   operation_type: str,
                                   memory_fold_id: str,
                                   payload: Dict[str, Any],
                                   priority: int = 1) -> Optional[str]:
        """Route memory operation to optimal cluster"""

        # Determine target cluster based on load balancing strategy
        target_cluster = await self._select_target_cluster(operation_type, memory_fold_id, payload)

        if not target_cluster:
            logger.warning(f"⚠️ No available cluster for operation: {operation_type}")
            return None

        # Create cross-cluster operation
        operation_id = f"fed_op_{uuid.uuid4().hex[:8]}"
        operation = CrossClusterOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            source_cluster=self._get_local_cluster_id(),
            target_clusters={target_cluster},
            payload=payload,
            priority=priority,
            created_at=datetime.utcnow()
        )

        self.pending_operations[operation_id] = operation

        # Execute operation
        await self._execute_cross_cluster_operation(operation)

        logger.debug(f"🔀 Routed {operation_type} operation to cluster: {target_cluster}")
        return operation_id

    async def balance_federation_load(self) -> Dict[str, Any]:
        """Perform federation-wide load balancing"""

        balance_start = time.time()
        balance_results = {
            "operations_moved": 0,
            "clusters_rebalanced": 0,
            "load_variance_improvement": 0.0,
            "errors": []
        }

        try:
            # Calculate current load distribution
            cluster_loads = {}
            for cluster_id, cluster in self.clusters.items():
                cluster_loads[cluster_id] = cluster.load_factor

            # Calculate load variance
            if cluster_loads:
                avg_load = sum(cluster_loads.values()) / len(cluster_loads)
                variance_before = sum((load - avg_load) ** 2 for load in cluster_loads.values()) / len(cluster_loads)

                # Identify overloaded and underloaded clusters
                overloaded = [cid for cid, load in cluster_loads.items() if load > avg_load + 0.2]
                underloaded = [cid for cid, load in cluster_loads.items() if load < avg_load - 0.2]

                # Move operations from overloaded to underloaded clusters
                for source_cluster in overloaded:
                    for target_cluster in underloaded:
                        moved = await self._move_operations_between_clusters(source_cluster, target_cluster)
                        balance_results["operations_moved"] += moved

                balance_results["clusters_rebalanced"] = len(overloaded) + len(underloaded)

                # Recalculate variance
                cluster_loads_after = {cid: c.load_factor for cid, c in self.clusters.items()}
                if cluster_loads_after:
                    avg_load_after = sum(cluster_loads_after.values()) / len(cluster_loads_after)
                    variance_after = sum((load - avg_load_after) ** 2 for load in cluster_loads_after.values()) / len(cluster_loads_after)
                    balance_results["load_variance_improvement"] = variance_before - variance_after
                    self.metrics.load_distribution_variance = variance_after

            balance_time = (time.time() - balance_start) * 1000
            logger.info(f"⚖️ Federation load balancing completed in {balance_time:.1f}ms")

        except Exception as e:
            balance_results["errors"].append(f"Load balancing failed: {e}")
            logger.error(f"❌ Federation load balancing failed: {e}")

        return balance_results

    async def optimize_federation_topology(self) -> Dict[str, Any]:
        """Optimize federation topology for performance"""

        optimization_start = time.time()
        optimization_results = {
            "topology_changes": 0,
            "latency_improvement_ms": 0.0,
            "efficiency_improvement": 0.0,
            "recommendations": []
        }

        try:
            # Analyze current topology
            topology_analysis = await self._analyze_federation_topology()

            # Generate optimization recommendations
            recommendations = await self._generate_topology_recommendations(topology_analysis)
            optimization_results["recommendations"] = recommendations

            # Apply safe optimizations
            for recommendation in recommendations:
                if recommendation.get("risk_level", "high") == "low":
                    applied = await self._apply_topology_optimization(recommendation)
                    if applied:
                        optimization_results["topology_changes"] += 1

            # Measure improvements
            post_analysis = await self._analyze_federation_topology()
            if topology_analysis.get("average_latency") and post_analysis.get("average_latency"):
                latency_improvement = topology_analysis["average_latency"] - post_analysis["average_latency"]
                optimization_results["latency_improvement_ms"] = latency_improvement

            optimization_time = (time.time() - optimization_start) * 1000
            logger.info(f"🎯 Federation topology optimization completed in {optimization_time:.1f}ms")

        except Exception as e:
            logger.error(f"❌ Federation topology optimization failed: {e}")

        return optimization_results

    async def get_federation_status(self) -> Dict[str, Any]:
        """Get comprehensive federation status"""

        return {
            "federation_id": self.federation_id,
            "state": self.state.value,
            "role": self.role.value,
            "metrics": asdict(self.metrics),
            "clusters": {
                cluster_id: {
                    "coordinator_node": cluster.coordinator_node,
                    "member_count": len(cluster.member_nodes),
                    "region": cluster.region,
                    "load_factor": cluster.load_factor,
                    "health_score": cluster.health_score,
                    "capabilities": list(cluster.capabilities)
                }
                for cluster_id, cluster in self.clusters.items()
            },
            "load_balancing": {
                "strategy": self.load_balancing_strategy.value,
                "pending_operations": len(self.pending_operations),
                "load_variance": self.metrics.load_distribution_variance
            },
            "performance": {
                "average_latency_ms": self.metrics.average_latency_ms,
                "throughput_ops_per_sec": self.metrics.throughput_ops_per_sec,
                "success_rate": self.metrics.success_rate,
                "federation_health": self.metrics.federation_health
            }
        }

    async def _initialize_local_cluster(self) -> FederationCluster:
        """Initialize local cluster information"""

        local_cluster_id = f"cluster_{self.local_orchestrator.node_id}"

        cluster = FederationCluster(
            cluster_id=local_cluster_id,
            coordinator_node=self.local_orchestrator.node_id,
            member_nodes={self.local_orchestrator.node_id},
            region="local",
            capabilities=self.local_orchestrator.local_node.capabilities
        )

        self.clusters[local_cluster_id] = cluster
        self.cluster_assignments[self.local_orchestrator.node_id] = local_cluster_id

        return cluster

    def _get_local_cluster_info(self) -> Dict[str, Any]:
        """Get local cluster information"""

        local_cluster_id = f"cluster_{self.local_orchestrator.node_id}"
        if local_cluster_id in self.clusters:
            cluster = self.clusters[local_cluster_id]
            return {
                "cluster_id": cluster.cluster_id,
                "coordinator_node": cluster.coordinator_node,
                "member_nodes": list(cluster.member_nodes),
                "region": cluster.region,
                "capabilities": list(cluster.capabilities),
                "load_factor": cluster.load_factor,
                "health_score": cluster.health_score
            }
        return {}

    def _get_local_cluster_id(self) -> str:
        """Get local cluster ID"""
        return f"cluster_{self.local_orchestrator.node_id}"

    async def _send_federation_join_request(self,
                                          coordinator_address: str,
                                          coordinator_port: int,
                                          join_request: Dict[str, Any]) -> Dict[str, Any]:
        """Send federation join request"""

        # Simulate network request
        await asyncio.sleep(0.1)  # Simulated network latency

        # Return simulated response
        return {
            "accepted": True,
            "federation_id": self.federation_id,
            "topology": {
                "clusters": {},
                "coordinator_cluster": self._get_local_cluster_id()
            }
        }

    async def _process_federation_topology(self, topology: Dict[str, Any]):
        """Process federation topology information"""

        clusters_info = topology.get("clusters", {})
        for cluster_id, cluster_info in clusters_info.items():
            if cluster_id not in self.clusters:
                await self.add_cluster_to_federation(cluster_info)

    async def _discover_federation(self):
        """Discover existing federation"""

        # For now, just initialize as standalone
        logger.info(f"🔍 Federation discovery completed - standalone: {self.federation_id}")

    async def _select_target_cluster(self,
                                   operation_type: str,
                                   memory_fold_id: str,
                                   payload: Dict[str, Any]) -> Optional[str]:
        """Select target cluster based on load balancing strategy"""

        if not self.clusters:
            return None

        if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return await self._round_robin_selection()
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_LOADED:
            return await self._least_loaded_selection()
        elif self.load_balancing_strategy == LoadBalancingStrategy.GEOGRAPHIC:
            return await self._geographic_selection(payload)
        elif self.load_balancing_strategy == LoadBalancingStrategy.SMART_ROUTING:
            return await self._smart_routing_selection(operation_type, memory_fold_id, payload)
        else:  # ADAPTIVE
            return await self._adaptive_selection(operation_type, memory_fold_id, payload)

    async def _round_robin_selection(self) -> str:
        """Round robin cluster selection"""

        cluster_ids = list(self.clusters.keys())
        if not cluster_ids:
            return None

        current_index = self.load_balancer_state.get("round_robin_index", 0)
        selected_cluster = cluster_ids[current_index % len(cluster_ids)]
        self.load_balancer_state["round_robin_index"] = (current_index + 1) % len(cluster_ids)

        return selected_cluster

    async def _least_loaded_selection(self) -> str:
        """Select cluster with least load"""

        if not self.clusters:
            return None

        min_load = float('inf')
        selected_cluster = None

        for cluster_id, cluster in self.clusters.items():
            if cluster.load_factor < min_load and cluster.health_score > 0.5:
                min_load = cluster.load_factor
                selected_cluster = cluster_id

        return selected_cluster

    async def _geographic_selection(self, payload: Dict[str, Any]) -> str:
        """Select cluster based on geographic location"""

        # Placeholder for geographic routing
        return await self._least_loaded_selection()

    async def _smart_routing_selection(self,
                                     operation_type: str,
                                     memory_fold_id: str,
                                     payload: Dict[str, Any]) -> str:
        """Smart routing based on operation characteristics"""

        # Consider operation type, memory fold characteristics, etc.
        if operation_type in ["read", "query"]:
            # Prefer clusters with cached data
            return await self._least_loaded_selection()
        else:
            # For writes, prefer clusters with available capacity
            return await self._least_loaded_selection()

    async def _adaptive_selection(self,
                                operation_type: str,
                                memory_fold_id: str,
                                payload: Dict[str, Any]) -> str:
        """Adaptive selection based on current conditions"""

        # Analyze current federation state and adapt strategy
        cluster_loads = [c.load_factor for c in self.clusters.values()]
        if cluster_loads:
            avg_load = sum(cluster_loads) / len(cluster_loads)
            load_variance = sum((load - avg_load) ** 2 for load in cluster_loads) / len(cluster_loads)

            if load_variance > 0.1:  # High variance - balance load
                return await self._least_loaded_selection()
            else:  # Balanced - use smart routing
                return await self._smart_routing_selection(operation_type, memory_fold_id, payload)

        return await self._round_robin_selection()

    async def _execute_cross_cluster_operation(self, operation: CrossClusterOperation):
        """Execute cross-cluster operation"""

        operation.status = "executing"

        try:
            # Simulate cross-cluster operation
            await asyncio.sleep(0.01)  # Simulated processing time

            operation.status = "completed"
            operation.completed_at = datetime.utcnow()

            # Move to history
            self.operation_history.append(asdict(operation))
            del self.pending_operations[operation.operation_id]

            # Update metrics
            self.metrics.throughput_ops_per_sec += 1

        except Exception as e:
            operation.status = "failed"
            operation.retry_count += 1

            if operation.retry_count < 3:
                # Retry
                operation.status = "pending"
            else:
                # Move to history as failed
                self.operation_history.append(asdict(operation))
                del self.pending_operations[operation.operation_id]

            logger.error(f"❌ Cross-cluster operation failed: {operation.operation_id} - {e}")

    async def _move_operations_between_clusters(self, source_cluster: str, target_cluster: str) -> int:
        """Move operations from source to target cluster"""

        # Placeholder for operation migration
        # In production, would identify movable operations and migrate them
        moved_count = 0

        if source_cluster in self.clusters and target_cluster in self.clusters:
            # Simulate moving operations
            source_load = self.clusters[source_cluster].load_factor
            target_load = self.clusters[target_cluster].load_factor

            if source_load > target_load:
                # Move some load
                transfer_amount = min(0.1, (source_load - target_load) / 2)
                self.clusters[source_cluster].load_factor -= transfer_amount
                self.clusters[target_cluster].load_factor += transfer_amount
                moved_count = int(transfer_amount * 10)  # Simulated operation count

        return moved_count

    async def _analyze_federation_topology(self) -> Dict[str, Any]:
        """Analyze current federation topology"""

        analysis = {
            "cluster_count": len(self.clusters),
            "total_nodes": sum(len(c.member_nodes) for c in self.clusters.values()),
            "average_latency": self.metrics.average_latency_ms,
            "load_distribution": [c.load_factor for c in self.clusters.values()],
            "health_scores": [c.health_score for c in self.clusters.values()],
            "topology_efficiency": 0.8  # Placeholder calculation
        }

        return analysis

    async def _generate_topology_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate topology optimization recommendations"""

        recommendations = []

        # Check for load imbalance
        load_distribution = analysis.get("load_distribution", [])
        if load_distribution:
            load_variance = sum((load - sum(load_distribution) / len(load_distribution)) ** 2
                              for load in load_distribution) / len(load_distribution)

            if load_variance > 0.1:
                recommendations.append({
                    "type": "load_rebalancing",
                    "description": "High load variance detected, recommend rebalancing",
                    "risk_level": "low",
                    "expected_improvement": "20% latency reduction"
                })

        # Check for unhealthy clusters
        health_scores = analysis.get("health_scores", [])
        if health_scores and min(health_scores) < 0.5:
            recommendations.append({
                "type": "cluster_isolation",
                "description": "Unhealthy cluster detected, recommend isolation",
                "risk_level": "medium",
                "expected_improvement": "Improved federation stability"
            })

        return recommendations

    async def _apply_topology_optimization(self, recommendation: Dict[str, Any]) -> bool:
        """Apply topology optimization recommendation"""

        optimization_type = recommendation.get("type")

        if optimization_type == "load_rebalancing":
            result = await self.balance_federation_load()
            return result.get("operations_moved", 0) > 0
        elif optimization_type == "cluster_isolation":
            # Placeholder for cluster isolation
            return True

        return False

    async def _trigger_federation_optimization(self):
        """Trigger federation optimization"""

        self.optimization_strategies.append(f"optimization_triggered_{int(time.time())}")

    async def _coordination_loop(self):
        """Main coordination loop"""

        while not self._shutdown_event.is_set():
            try:
                # Process pending cross-cluster operations
                for _operation_id, operation in list(self.pending_operations.items()):
                    if operation.status == "pending":
                        await self._execute_cross_cluster_operation(operation)

                await asyncio.sleep(0.1)  # Coordination loop interval

            except Exception as e:
                logger.error(f"❌ Coordination loop error: {e}")
                await asyncio.sleep(1.0)

    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""

        while not self._shutdown_event.is_set():
            try:
                # Check cluster health
                for cluster_id, cluster in self.clusters.items():
                    health_score = await self._calculate_cluster_health(cluster)
                    cluster.health_score = health_score

                    if health_score < 0.3:
                        logger.warning(f"⚠️ Cluster health degraded: {cluster_id} ({health_score:.2f})")

                # Update federation health
                if self.clusters:
                    avg_health = sum(c.health_score for c in self.clusters.values()) / len(self.clusters)
                    self.metrics.federation_health = avg_health

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(10.0)

    async def _optimization_loop(self):
        """Background optimization loop"""

        while not self._shutdown_event.is_set():
            try:
                if self.state == FederationState.ACTIVE:
                    # Trigger periodic optimization
                    optimization_results = await self.optimize_federation_topology()

                    if optimization_results.get("topology_changes", 0) > 0:
                        logger.info(f"🎯 Applied {optimization_results['topology_changes']} topology optimizations")

                await asyncio.sleep(300.0)  # Optimize every 5 minutes

            except Exception as e:
                logger.error(f"❌ Optimization loop error: {e}")
                await asyncio.sleep(60.0)

    async def _load_balancing_loop(self):
        """Background load balancing loop"""

        while not self._shutdown_event.is_set():
            try:
                if len(self.clusters) > 1:
                    # Trigger load balancing
                    balance_results = await self.balance_federation_load()

                    if balance_results.get("operations_moved", 0) > 0:
                        logger.info(f"⚖️ Balanced federation load: {balance_results['operations_moved']} operations moved")

                await asyncio.sleep(60.0)  # Balance every minute

            except Exception as e:
                logger.error(f"❌ Load balancing loop error: {e}")
                await asyncio.sleep(30.0)

    async def _calculate_cluster_health(self, cluster: FederationCluster) -> float:
        """Calculate cluster health score"""

        health_factors = []

        # Check heartbeat recency
        time_since_heartbeat = (datetime.utcnow() - cluster.last_heartbeat).total_seconds()
        heartbeat_health = max(0.0, 1.0 - (time_since_heartbeat / 60.0))  # Decay over 1 minute
        health_factors.append(heartbeat_health * 0.4)

        # Check load factor
        load_health = max(0.0, 1.0 - cluster.load_factor)  # Lower load = better health
        health_factors.append(load_health * 0.3)

        # Check member node count
        member_health = min(1.0, len(cluster.member_nodes) / 3.0)  # Optimal around 3+ nodes
        health_factors.append(member_health * 0.3)

        return sum(health_factors)
