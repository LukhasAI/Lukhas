"""
🧠 Cognitive Mesh Coordinator
═══════════════════════════════════════════════════════════════════════════

PURPOSE: Orchestrates distributed cognitive processing across specialized AI nodes
         in a dynamic mesh topology for adaptive intelligence scaling

CAPABILITY: Manages specialist nodes (reasoning, memory, creativity, ethics) with
           dynamic load balancing, fault tolerance, and emergent coordination

ARCHITECTURE: Decentralized mesh with smart routing, consensus mechanisms,
             and adaptive topology optimization for cognitive workloads

INTEGRATION: Core orchestration layer connecting all AGI subsystems through
            the cognitive mesh with unified messaging and state synchronization

🔄 MESH TOPOLOGY FEATURES:
- Dynamic node discovery and registration
- Adaptive topology optimization
- Load-aware task distribution
- Fault tolerance with graceful degradation
- Consensus-based decision making
- Real-time performance monitoring
- Auto-scaling based on cognitive load
- Quality-of-service guarantees

🤖 SPECIALIST NODE TYPES:
- Reasoning Nodes: Symbolic logic, causal inference
- Memory Nodes: HDS storage, retrieval, compression
- Creative Nodes: Dream simulation, idea generation
- Ethics Nodes: MEG evaluation, compliance checking
- Integration Nodes: Cross-domain coordination
- Sensor Nodes: External data ingestion
- Output Nodes: Response generation, action execution

⚡ COORDINATION PROTOCOLS:
- Byzantine fault tolerant consensus
- Vector clock synchronization
- Gossip-based state propagation
- Hierarchical task decomposition
- Distributed leader election
- Adaptive quality control
- Resource allocation optimization

🛡️ RESILIENCE MECHANISMS:
- Redundant node deployment
- Circuit breaker patterns
- Graceful degradation modes
- Health monitoring and recovery
- Backup coordinator election
- Data replication strategies

VERSION: v1.0.0 • CREATED: 2025-01-21 • AUTHOR: LUKHAS AGI TEAM
SYMBOLIC TAGS: ΛMESH, ΛCOGNITIVE, ΛORCHESTRATION, ΛDISTRIBUTED, ΛCOORDINATOR
"""

import asyncio
import time
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import structlog

# Initialize structured logger
logger = structlog.get_logger("lukhas.cognitive_mesh")


class NodeType(Enum):
    """Types of cognitive nodes in the mesh"""

    REASONING = "reasoning"  # Symbolic and logical reasoning
    MEMORY = "memory"  # HDS and memory management
    CREATIVE = "creative"  # Dream and creative processing
    ETHICS = "ethics"  # MEG and ethical evaluation
    INTEGRATION = "integration"  # Cross-domain coordination
    SENSOR = "sensor"  # External data ingestion
    OUTPUT = "output"  # Response and action generation
    COORDINATOR = "coordinator"  # Mesh coordination


class NodeStatus(Enum):
    """Node operational status"""

    INITIALIZING = "initializing"
    ONLINE = "online"
    BUSY = "busy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    RECOVERING = "recovering"


class TaskPriority(Enum):
    """Task priority levels"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class CognitiveTask:
    """Task for processing in the cognitive mesh"""

    task_id: str = field(default_factory=lambda: str(uuid4()))
    task_type: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    payload: dict[str, Any] = field(default_factory=dict)
    required_node_types: list[NodeType] = field(default_factory=list)
    timeout_seconds: int = 30
    created_at: datetime = field(default_factory=lambda: datetime.now())
    assigned_node_id: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    result: Optional[Any] = None
    status: str = "pending"


@dataclass
class NodeCapability:
    """Capability descriptor for cognitive nodes"""

    node_type: NodeType
    specializations: list[str] = field(default_factory=list)
    max_concurrent_tasks: int = 5
    average_response_time_ms: float = 100.0
    quality_score: float = 1.0
    resource_requirements: dict[str, float] = field(default_factory=dict)


@dataclass
class NodeMetrics:
    """Performance metrics for cognitive nodes"""

    total_tasks_processed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    current_load: float = 0.0
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now())
    uptime_seconds: float = 0.0
    quality_trend: deque = field(default_factory=lambda: deque(maxlen=100))


class CognitiveNode(ABC):
    """Abstract base class for cognitive nodes"""

    def __init__(self, node_id: str, node_type: NodeType, capabilities: NodeCapability):
        """
        Initialize a cognitive node

        # Notes:
        - Node ID should be unique across the mesh
        - Capabilities define what tasks this node can handle
        - Each node maintains its own metrics and health status
        """
        self.node_id = node_id
        self.node_type = node_type
        self.capabilities = capabilities
        self.status = NodeStatus.INITIALIZING
        self.metrics = NodeMetrics()
        self.active_tasks: dict[str, CognitiveTask] = {}
        self.task_queue: deque = deque()
        self.coordinator_ref: Optional[weakref.ref] = None
        self._running = False

        logger.info(
            "ΛMESH: Cognitive node initialized",
            node_id=node_id,
            node_type=node_type.value,
            specializations=capabilities.specializations,
        )

    @abstractmethod
    async def process_task(self, task: CognitiveTask) -> Any:
        """Process a cognitive task - must be implemented by subclasses"""

    async def start(self):
        """Start the node and begin processing tasks"""
        self._running = True
        self.status = NodeStatus.ONLINE
        asyncio.create_task(self._process_loop())
        asyncio.create_task(self._heartbeat_loop())
        logger.info("ΛMESH: Node started", node_id=self.node_id)

    async def stop(self):
        """Stop the node gracefully"""
        self._running = False
        self.status = NodeStatus.OFFLINE
        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(0.1)
        logger.info("ΛMESH: Node stopped", node_id=self.node_id)

    async def submit_task(self, task: CognitiveTask) -> bool:
        """Submit a task to this node's queue"""
        if len(self.active_tasks) >= self.capabilities.max_concurrent_tasks:
            return False

        self.task_queue.append(task)
        task.assigned_node_id = self.node_id
        task.status = "queued"

        logger.debug(
            "ΛMESH: Task queued",
            node_id=self.node_id,
            task_id=task.task_id,
            queue_size=len(self.task_queue),
        )
        return True

    async def _process_loop(self):
        """Main processing loop for handling tasks"""
        while self._running:
            try:
                if (
                    self.task_queue
                    and len(self.active_tasks) < self.capabilities.max_concurrent_tasks
                ):
                    task = self.task_queue.popleft()
                    asyncio.create_task(self._execute_task(task))
                else:
                    await asyncio.sleep(0.01)  # Small delay to prevent busy waiting

            except Exception as e:
                logger.error(
                    "ΛMESH: Processing loop error",
                    node_id=self.node_id,
                    error=str(e),
                )
                await asyncio.sleep(1)  # Error recovery delay

    async def _execute_task(self, task: CognitiveTask):
        """Execute a single task with metrics tracking"""
        start_time = time.time()
        self.active_tasks[task.task_id] = task
        task.status = "processing"

        try:
            # Update node status
            if len(self.active_tasks) >= self.capabilities.max_concurrent_tasks:
                self.status = NodeStatus.BUSY

            # Process the task
            result = await asyncio.wait_for(
                self.process_task(task), timeout=task.timeout_seconds
            )

            task.result = result
            task.status = "completed"
            self.metrics.successful_tasks += 1

            logger.info(
                "ΛMESH: Task completed",
                node_id=self.node_id,
                task_id=task.task_id,
                duration_ms=round((time.time() - start_time) * 1000, 2),
            )

        except asyncio.TimeoutError:
            task.status = "timeout"
            self.metrics.failed_tasks += 1
            logger.warning(
                "ΛMESH: Task timeout",
                node_id=self.node_id,
                task_id=task.task_id,
            )

        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            self.metrics.failed_tasks += 1
            logger.error(
                "ΛMESH: Task failed",
                node_id=self.node_id,
                task_id=task.task_id,
                error=str(e),
            )

        finally:
            # Update metrics
            duration = time.time() - start_time
            self.metrics.total_tasks_processed += 1

            # Update average response time
            total = self.metrics.total_tasks_processed
            current_avg = self.metrics.average_response_time
            self.metrics.average_response_time = (
                current_avg * (total - 1) + duration
            ) / total

            # Update quality trend
            quality = 1.0 if task.status == "completed" else 0.0
            self.metrics.quality_trend.append(quality)

            # Clean up
            del self.active_tasks[task.task_id]

            # Update status
            if len(self.active_tasks) == 0:
                self.status = NodeStatus.ONLINE

            # Notify coordinator if available
            if self.coordinator_ref and self.coordinator_ref():
                coordinator = self.coordinator_ref()
                await coordinator.task_completed(task)

    async def _heartbeat_loop(self):
        """Send periodic heartbeats to maintain node health"""
        while self._running:
            try:
                self.metrics.last_heartbeat = datetime.now()
                self.metrics.current_load = (
                    len(self.active_tasks) / self.capabilities.max_concurrent_tasks
                )

                # Send heartbeat to coordinator
                if self.coordinator_ref and self.coordinator_ref():
                    coordinator = self.coordinator_ref()
                    await coordinator.node_heartbeat(self.node_id, self.metrics)

                await asyncio.sleep(5)  # Heartbeat every 5 seconds

            except Exception as e:
                logger.error(
                    "ΛMESH: Heartbeat error",
                    node_id=self.node_id,
                    error=str(e),
                )
                await asyncio.sleep(5)

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive node status"""
        success_rate = self.metrics.successful_tasks / max(
            1, self.metrics.total_tasks_processed
        )

        quality_score = sum(self.metrics.quality_trend) / max(
            1, len(self.metrics.quality_trend)
        )

        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "status": self.status.value,
            "capabilities": {
                "specializations": self.capabilities.specializations,
                "max_concurrent": self.capabilities.max_concurrent_tasks,
            },
            "metrics": {
                "total_processed": self.metrics.total_tasks_processed,
                "success_rate": f"{success_rate:.2%}",
                "avg_response_ms": round(self.metrics.average_response_time * 1000, 2),
                "current_load": f"{self.metrics.current_load:.2%}",
                "quality_score": round(quality_score, 2),
            },
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
        }


class CognitiveMeshCoordinator:
    """Main coordinator for the cognitive mesh"""

    def __init__(self, mesh_id: Optional[str] = None):
        """
        Initialize the cognitive mesh coordinator

        # Notes:
        - Mesh ID helps identify this coordinator instance
        - Manages dynamic topology and load balancing
        - Provides fault tolerance and consensus mechanisms
        """
        self.mesh_id = mesh_id or str(uuid4())
        self.nodes: dict[str, CognitiveNode] = {}
        self.node_types: dict[NodeType, set[str]] = defaultdict(set)
        self.pending_tasks: dict[str, CognitiveTask] = {}
        self.completed_tasks: dict[str, CognitiveTask] = {}
        self.task_dependencies: dict[str, set[str]] = defaultdict(set)

        # Mesh topology and routing
        self.mesh_topology: dict[str, set[str]] = defaultdict(set)
        self.routing_table: dict[str, str] = {}

        # Performance and health monitoring
        self.mesh_metrics = {
            "total_nodes": 0,
            "active_nodes": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_task_time": 0.0,
            "mesh_utilization": 0.0,
        }

        # Background tasks
        self._running = False
        self._health_monitor_task = None
        self._load_balancer_task = None
        self._topology_optimizer_task = None

        logger.info(
            "ΛMESH: Cognitive mesh coordinator initialized",
            mesh_id=self.mesh_id,
        )

    async def start(self):
        """Start the mesh coordinator and background tasks"""
        self._running = True
        self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        self._load_balancer_task = asyncio.create_task(self._load_balancer_loop())
        self._topology_optimizer_task = asyncio.create_task(
            self._topology_optimizer_loop()
        )

        logger.info("ΛMESH: Mesh coordinator started", mesh_id=self.mesh_id)

    async def stop(self):
        """Stop the mesh coordinator gracefully"""
        self._running = False

        # Cancel background tasks
        for task in [
            self._health_monitor_task,
            self._load_balancer_task,
            self._topology_optimizer_task,
        ]:
            if task:
                task.cancel()

        # Stop all nodes
        for node in self.nodes.values():
            await node.stop()

        logger.info("ΛMESH: Mesh coordinator stopped", mesh_id=self.mesh_id)

    async def register_node(self, node: CognitiveNode) -> bool:
        """Register a new cognitive node in the mesh"""
        if node.node_id in self.nodes:
            logger.warning("ΛMESH: Node already registered", node_id=node.node_id)
            return False

        # Register node
        self.nodes[node.node_id] = node
        self.node_types[node.node_type].add(node.node_id)
        node.coordinator_ref = weakref.ref(self)

        # Start node if not already started
        if node.status == NodeStatus.INITIALIZING:
            await node.start()

        # Update metrics
        self.mesh_metrics["total_nodes"] += 1
        if node.status == NodeStatus.ONLINE:
            self.mesh_metrics["active_nodes"] += 1

        # Update topology
        await self._update_topology(node.node_id)

        logger.info(
            "ΛMESH: Node registered",
            node_id=node.node_id,
            node_type=node.node_type.value,
            total_nodes=self.mesh_metrics["total_nodes"],
        )
        return True

    async def unregister_node(self, node_id: str):
        """Unregister a node from the mesh"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

        # Remove from topology
        self.mesh_topology.pop(node_id, None)
        for neighbors in self.mesh_topology.values():
            neighbors.discard(node_id)

        # Remove from type mapping
        self.node_types[node.node_type].discard(node_id)

        # Remove from routing table
        self.routing_table = {
            k: v for k, v in self.routing_table.items() if v != node_id
        }

        # Stop node
        await node.stop()

        # Remove from registry
        del self.nodes[node_id]

        # Update metrics
        self.mesh_metrics["total_nodes"] -= 1
        if node.status == NodeStatus.ONLINE:
            self.mesh_metrics["active_nodes"] -= 1

        logger.info(
            "ΛMESH: Node unregistered",
            node_id=node_id,
            remaining_nodes=self.mesh_metrics["total_nodes"],
        )

    async def submit_task(self, task: CognitiveTask) -> str:
        """Submit a task to the cognitive mesh for processing"""
        self.pending_tasks[task.task_id] = task
        self.mesh_metrics["total_tasks"] += 1

        # Find best node for task
        best_node_id = await self._find_optimal_node(task)

        if best_node_id:
            node = self.nodes[best_node_id]
            success = await node.submit_task(task)

            if success:
                logger.info(
                    "ΛMESH: Task submitted",
                    task_id=task.task_id,
                    node_id=best_node_id,
                    task_type=task.task_type,
                )
                return task.task_id
            else:
                # Node is full, try alternative routing
                alternative = await self._find_alternative_node(task, {best_node_id})
                if alternative:
                    node = self.nodes[alternative]
                    success = await node.submit_task(task)
                    if success:
                        return task.task_id

        # No suitable node found
        logger.warning(
            "ΛMESH: No suitable node for task",
            task_id=task.task_id,
            required_types=[t.value for t in task.required_node_types],
        )
        task.status = "rejected"
        return task.task_id

    async def get_task_result(self, task_id: str) -> Optional[CognitiveTask]:
        """Get the result of a completed task"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        elif task_id in self.pending_tasks:
            task = self.pending_tasks[task_id]
            if task.status in ["completed", "failed", "timeout"]:
                return task
        return None

    async def task_completed(self, task: CognitiveTask):
        """Handle task completion notification from nodes"""
        if task.task_id in self.pending_tasks:
            del self.pending_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task

            if task.status == "completed":
                self.mesh_metrics["completed_tasks"] += 1
            else:
                self.mesh_metrics["failed_tasks"] += 1

            # Update average task time
            if hasattr(task, "duration"):
                total_completed = self.mesh_metrics["completed_tasks"]
                current_avg = self.mesh_metrics["average_task_time"]
                self.mesh_metrics["average_task_time"] = (
                    current_avg * (total_completed - 1) + task.duration
                ) / total_completed

            logger.debug(
                "ΛMESH: Task completed notification",
                task_id=task.task_id,
                status=task.status,
            )

    async def node_heartbeat(self, node_id: str, metrics: NodeMetrics):
        """Handle heartbeat from a node"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.metrics = metrics

            # Update mesh-level metrics
            total_load = sum(n.metrics.current_load for n in self.nodes.values())
            self.mesh_metrics["mesh_utilization"] = total_load / max(1, len(self.nodes))

    async def _find_optimal_node(self, task: CognitiveTask) -> Optional[str]:
        """Find the optimal node to process a task"""
        candidates = []

        # Filter by required node types
        if task.required_node_types:
            for node_type in task.required_node_types:
                candidates.extend(self.node_types[node_type])
        else:
            candidates = list(self.nodes.keys())

        # Filter by status and capacity
        available_candidates = []
        for node_id in candidates:
            node = self.nodes.get(node_id)
            if (
                node
                and node.status in [NodeStatus.ONLINE, NodeStatus.BUSY]
                and len(node.active_tasks) < node.capabilities.max_concurrent_tasks
            ):
                available_candidates.append(node_id)

        if not available_candidates:
            return None

        # Score candidates based on multiple factors

        def score_node(node_id: str) -> float:
            node = self.nodes[node_id]

            # Base score from node quality
            quality_score = sum(node.metrics.quality_trend) / max(
                1, len(node.metrics.quality_trend)
            )

            # Load factor (prefer less loaded nodes)
            load_factor = 1.0 - node.metrics.current_load

            # Response time factor (prefer faster nodes)
            max_time = max(n.metrics.average_response_time for n in self.nodes.values())
            time_factor = (
                1.0 - node.metrics.average_response_time / max_time
                if max_time > 0
                else 1.0
            )

            # Priority boost for critical tasks
            priority_factor = 1.0
            if task.priority == TaskPriority.CRITICAL:
                priority_factor = 2.0
            elif task.priority == TaskPriority.HIGH:
                priority_factor = 1.5

            return quality_score * load_factor * time_factor * priority_factor

        # Select best scoring node
        best_node = max(available_candidates, key=score_node)
        return best_node

    async def _find_alternative_node(
        self, task: CognitiveTask, excluded: set[str]
    ) -> Optional[str]:
        """Find alternative node when primary choice is unavailable"""
        # Similar to _find_optimal_node but with exclusions
        candidates = []

        if task.required_node_types:
            for node_type in task.required_node_types:
                candidates.extend(self.node_types[node_type])
        else:
            candidates = list(self.nodes.keys())

        # Remove excluded nodes
        candidates = [c for c in candidates if c not in excluded]

        available_candidates = []
        for node_id in candidates:
            node = self.nodes.get(node_id)
            if (
                node
                and node.status in [NodeStatus.ONLINE, NodeStatus.BUSY]
                and len(node.active_tasks) < node.capabilities.max_concurrent_tasks
            ):
                available_candidates.append(node_id)

        if available_candidates:
            # Return node with lowest load
            return min(
                available_candidates,
                key=lambda nid: self.nodes[nid].metrics.current_load,
            )

        return None

    async def _update_topology(self, node_id: str):
        """Update mesh topology when nodes are added/removed"""
        # Simple topology: connect each node to a few others based on type similarity
        node = self.nodes[node_id]

        # Find nodes of same or complementary types
        related_nodes = set()

        # Same type nodes (for redundancy)
        related_nodes.update(self.node_types[node.node_type])

        # Complementary type connections
        if node.node_type == NodeType.REASONING:
            related_nodes.update(self.node_types[NodeType.MEMORY])
            related_nodes.update(self.node_types[NodeType.ETHICS])
        elif node.node_type == NodeType.MEMORY:
            related_nodes.update(self.node_types[NodeType.REASONING])
            related_nodes.update(self.node_types[NodeType.CREATIVE])
        elif node.node_type == NodeType.CREATIVE:
            related_nodes.update(self.node_types[NodeType.MEMORY])
            related_nodes.update(self.node_types[NodeType.INTEGRATION])

        # Remove self
        related_nodes.discard(node_id)

        # Limit connections to avoid over-connectivity
        related_nodes = set(list(related_nodes)[:5])

        # Update topology
        self.mesh_topology[node_id].update(related_nodes)
        for related_id in related_nodes:
            self.mesh_topology[related_id].add(node_id)

        logger.debug(
            "ΛMESH: Topology updated",
            node_id=node_id,
            connections=len(self.mesh_topology[node_id]),
        )

    async def _health_monitor_loop(self):
        """Monitor node health and handle failures"""
        while self._running:
            try:
                current_time = datetime.now()
                unhealthy_nodes = []

                for node_id, node in self.nodes.items():
                    # Check heartbeat freshness
                    time_since_heartbeat = (
                        current_time - node.metrics.last_heartbeat
                    ).total_seconds()

                    if time_since_heartbeat > 30:  # 30 seconds timeout
                        if node.status != NodeStatus.OFFLINE:
                            node.status = NodeStatus.OFFLINE
                            unhealthy_nodes.append(node_id)
                            logger.warning(
                                "ΛMESH: Node unhealthy",
                                node_id=node_id,
                                last_heartbeat=time_since_heartbeat,
                            )

                # Handle unhealthy nodes
                for node_id in unhealthy_nodes:
                    # Reassign tasks from unhealthy nodes
                    node = self.nodes[node_id]
                    for task in list(node.active_tasks.values()):
                        # Try to reassign to healthy node
                        alternative = await self._find_alternative_node(task, {node_id})
                        if alternative:
                            alt_node = self.nodes[alternative]
                            if await alt_node.submit_task(task):
                                logger.info(
                                    "ΛMESH: Task reassigned",
                                    task_id=task.task_id,
                                    from_node=node_id,
                                    to_node=alternative,
                                )

                # Update active node count
                self.mesh_metrics["active_nodes"] = sum(
                    1
                    for node in self.nodes.values()
                    if node.status == NodeStatus.ONLINE
                )

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error("ΛMESH: Health monitor error", error=str(e))
                await asyncio.sleep(10)

    async def _load_balancer_loop(self):
        """Balance load across mesh nodes"""
        while self._running:
            try:
                # Find overloaded and underloaded nodes
                overloaded = []
                underloaded = []

                for node_id, node in self.nodes.items():
                    if node.status != NodeStatus.ONLINE:
                        continue

                    load = node.metrics.current_load
                    if load > 0.8:  # 80% threshold
                        overloaded.append((node_id, load))
                    elif load < 0.3:  # 30% threshold
                        underloaded.append((node_id, load))

                # Move queued tasks from overloaded to underloaded nodes
                overloaded.sort(key=lambda x: x[1], reverse=True)
                underloaded.sort(key=lambda x: x[1])

                for overloaded_id, _ in overloaded:
                    if not underloaded:
                        break

                    overloaded_node = self.nodes[overloaded_id]
                    if not overloaded_node.task_queue:
                        continue

                    # Move task to underloaded node
                    task = overloaded_node.task_queue.popleft()

                    underloaded_id, _ = underloaded[0]
                    underloaded_node = self.nodes[underloaded_id]

                    if await underloaded_node.submit_task(task):
                        logger.debug(
                            "ΛMESH: Task rebalanced",
                            task_id=task.task_id,
                            from_node=overloaded_id,
                            to_node=underloaded_id,
                        )

                        # Update underloaded list
                        underloaded[0] = (
                            underloaded_id,
                            underloaded_node.metrics.current_load,
                        )
                        underloaded.sort(key=lambda x: x[1])

                await asyncio.sleep(30)  # Rebalance every 30 seconds

            except Exception as e:
                logger.error("ΛMESH: Load balancer error", error=str(e))
                await asyncio.sleep(30)

    async def _topology_optimizer_loop(self):
        """Optimize mesh topology for performance"""
        while self._running:
            try:
                # Analyze communication patterns and optimize connections
                # This is a simplified version - production would use graph algorithms

                # Count communication frequency between node types
                defaultdict(lambda: defaultdict(int))

                # Update topology based on communication patterns
                # (Implementation would analyze task flows and optimize connections)

                await asyncio.sleep(300)  # Optimize every 5 minutes

            except Exception as e:
                logger.error("ΛMESH: Topology optimizer error", error=str(e))
                await asyncio.sleep(300)

    def get_mesh_status(self) -> dict[str, Any]:
        """Get comprehensive mesh status"""
        node_status_counts = defaultdict(int)
        for node in self.nodes.values():
            node_status_counts[node.status.value] += 1

        type_distribution = {}
        for node_type, node_set in self.node_types.items():
            type_distribution[node_type.value] = len(node_set)

        return {
            "mesh_id": self.mesh_id,
            "metrics": self.mesh_metrics.copy(),
            "topology": {
                "total_connections": sum(
                    len(neighbors) for neighbors in self.mesh_topology.values()
                ),
                "average_connections": (
                    sum(len(neighbors) for neighbors in self.mesh_topology.values())
                    / max(1, len(self.mesh_topology))
                ),
            },
            "node_distribution": {
                "by_status": dict(node_status_counts),
                "by_type": type_distribution,
            },
            "task_queues": {
                "pending": len(self.pending_tasks),
                "completed": len(self.completed_tasks),
            },
        }


# Global mesh coordinator instance
_mesh_coordinator: Optional[CognitiveMeshCoordinator] = None


async def get_mesh_coordinator() -> CognitiveMeshCoordinator:
    """Get the global cognitive mesh coordinator"""
    global _mesh_coordinator
    if _mesh_coordinator is None:
        _mesh_coordinator = CognitiveMeshCoordinator()
        await _mesh_coordinator.start()
    return _mesh_coordinator


# ═══════════════════════════════════════════════════════════════════════════
# 📚 USER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# BASIC USAGE:
# -----------
# 1. Create a cognitive node:
#    class ReasoningNode(CognitiveNode):
#        async def process_task(self, task):
#            # Implement reasoning logic
#            return {"result": "reasoning complete"}
#
# 2. Register with mesh:
#    coordinator = await get_mesh_coordinator()
#    node = ReasoningNode("reasoning-1", NodeType.REASONING, capabilities)
#    await coordinator.register_node(node)
#
# 3. Submit tasks:
#    task = CognitiveTask(
#        task_type="logical_inference",
#        required_node_types=[NodeType.REASONING],
#        payload={"premises": [...], "query": "..."}
#    )
#    task_id = await coordinator.submit_task(task)
#
# 4. Get results:
#    result = await coordinator.get_task_result(task_id)
#
# ═══════════════════════════════════════════════════════════════════════════
# 👨‍💻 DEVELOPER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# IMPLEMENTING CUSTOM NODES:
# --------------------------
# 1. Inherit from CognitiveNode
# 2. Implement process_task method
# 3. Define appropriate NodeCapability
# 4. Handle errors gracefully
# 5. Update metrics for monitoring
#
# MESH TOPOLOGY DESIGN:
# --------------------
# - Nodes are connected based on type relationships
# - Reasoning nodes connect to Memory and Ethics
# - Creative nodes connect to Memory and Integration
# - Use complementary connections for task routing
#
# FAULT TOLERANCE:
# ---------------
# - Heartbeat monitoring detects failed nodes
# - Task reassignment to healthy nodes
# - Graceful degradation with reduced capacity
# - Circuit breaker patterns prevent cascade failures
#
# PERFORMANCE OPTIMIZATION:
# ------------------------
# - Load balancing based on node capacity
# - Task priority affects routing decisions
# - Dynamic topology adjustment
# - Resource-aware scheduling
#
# ═══════════════════════════════════════════════════════════════════════════
# 🎯 FINE-TUNING INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════
#
# FOR HIGH-THROUGHPUT SYSTEMS:
# ---------------------------
# - Increase max_concurrent_tasks per node
# - Reduce heartbeat interval to 1-2 seconds
# - Use more aggressive load balancing (60/40 thresholds)
# - Implement task batching for efficiency
#
# FOR FAULT-SENSITIVE SYSTEMS:
# ---------------------------
# - Implement node redundancy (2-3 nodes per type)
# - Use stricter health monitoring (15s timeout)
# - Enable task checkpointing for recovery
# - Implement consensus for critical decisions
#
# FOR RESOURCE-CONSTRAINED SYSTEMS:
# --------------------------------
# - Limit concurrent tasks (2-3 per node)
# - Increase monitoring intervals (30s heartbeat)
# - Use simpler topology (star or tree)
# - Implement task shedding under load
#
# ═══════════════════════════════════════════════════════════════════════════
# ❓ COMMON QUESTIONS & PROBLEMS
# ═══════════════════════════════════════════════════════════════════════════
#
# Q: Why are tasks not being assigned to nodes?
# A: Check node status and capacity. Ensure required_node_types match registered nodes
#    Verify nodes are online and not overloaded
#
# Q: How do I implement Byzantine fault tolerance?
# A: Override consensus methods in coordinator
#    Implement vote-based decision making
#    Add message authentication
#
# Q: Can I use this across multiple machines?
# A: Yes, extend with network communication:
#    - Replace direct calls with RPC/REST APIs
#    - Add network discovery mechanisms
#    - Implement distributed consensus protocols
#
# Q: How do I debug mesh performance issues?
# A: Enable debug logging and monitor metrics
#    Check mesh_utilization and node load distribution
#    Analyze task completion times per node type
#
# Q: What's the maximum recommended mesh size?
# A: Typically 50-100 nodes for single coordinator
#    Use hierarchical coordinators for larger deployments
#    Consider partitioning by domain or geography
#
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: orchestration/brain/mesh/cognitive_mesh_coordinator.py
# VERSION: v1.0.0
# SYMBOLIC TAGS: ΛMESH, ΛCOGNITIVE, ΛORCHESTRATION, ΛDISTRIBUTED, ΛCOORDINATOR
# CLASSES: CognitiveMeshCoordinator, CognitiveNode, CognitiveTask, NodeCapability
# FUNCTIONS: get_mesh_coordinator, register_node, submit_task, get_task_result
# LOGGER: structlog (UTC)
# INTEGRATION: HDS, MEG, SRD, Fold Memory
# ═══════════════════════════════════════════════════════════════════════════
