"""
M.2 Distributed Memory - Federated storage and synchronization
Advanced distributed memory system with consensus protocols and federated architecture.
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set

from memory.consciousness_memory_integration import ConsciousnessMemoryIntegrator
from memory.fold_system import MemoryFold

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """Distributed memory node states"""

    INITIALIZING = "initializing"
    JOINING = "joining"
    ACTIVE = "active"
    SYNCING = "syncing"
    OFFLINE = "offline"
    FAILED = "failed"


class ConsensusProtocol(Enum):
    """Consensus protocols for distributed memory"""

    SIMPLE_MAJORITY = "simple_majority"
    BYZANTINE_FAULT_TOLERANT = "byzantine_fault_tolerant"
    EVENTUAL_CONSISTENCY = "eventual_consistency"
    STRONG_CONSISTENCY = "strong_consistency"


class ReplicationStrategy(Enum):
    """Memory replication strategies"""

    NONE = "none"
    MIRROR = "mirror"  # 1:1 replication
    QUORUM = "quorum"  # N/2+1 replicas
    FULL_MESH = "full_mesh"  # All nodes
    RING = "ring"  # Ring topology


@dataclass
class DistributedNode:
    """Distributed memory node information"""

    node_id: str
    address: str
    port: int
    state: NodeState
    capabilities: Set[str]
    last_heartbeat: datetime
    memory_capacity: int = 1000  # Max memory folds
    current_load: int = 0
    sync_latency_ms: float = 0.0
    reputation_score: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationRecord:
    """Memory fold replication record"""

    fold_id: str
    primary_node: str
    replica_nodes: Set[str]
    replication_factor: int
    created_at: datetime
    last_verified: datetime
    checksum: str
    version: int = 1


@dataclass
class SyncOperation:
    """Memory synchronization operation"""

    operation_id: str
    operation_type: str  # "create", "update", "delete", "sync"
    fold_id: str
    source_node: str
    target_nodes: Set[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    consensus_required: bool = True


@dataclass
class ConsensusResult:
    """Result of consensus operation"""

    operation_id: str
    consensus_reached: bool
    participating_nodes: Set[str]
    confirming_nodes: Set[str]
    rejecting_nodes: Set[str]
    consensus_time_ms: float
    error_message: Optional[str] = None


class DistributedMemoryOrchestrator:
    """
    M.2 Distributed Memory System
    Federated memory storage with consensus protocols and advanced synchronization
    """

    def __init__(
        self,
        node_id: Optional[str] = None,
        listen_port: int = 8790,
        consensus_protocol: ConsensusProtocol = ConsensusProtocol.SIMPLE_MAJORITY,
        replication_strategy: ReplicationStrategy = ReplicationStrategy.QUORUM,
        memory_integrator: Optional[ConsciousnessMemoryIntegrator] = None,
    ):
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        self.listen_port = listen_port
        self.consensus_protocol = consensus_protocol
        self.replication_strategy = replication_strategy
        self.memory_integrator = memory_integrator

        # Node state
        self.state = NodeState.INITIALIZING
        self.local_node = DistributedNode(
            node_id=self.node_id,
            address="localhost",
            port=listen_port,
            state=self.state,
            capabilities={"fold_storage", "consensus", "replication"},
            last_heartbeat=datetime.utcnow(),
        )

        # Distributed topology
        self.known_nodes: Dict[str, DistributedNode] = {}
        self.active_nodes: Set[str] = set()
        self.trusted_nodes: Set[str] = set()

        # Memory storage
        self.local_memory_folds: Dict[str, MemoryFold] = {}
        self.replication_records: Dict[str, ReplicationRecord] = {}
        self.pending_operations: Dict[str, SyncOperation] = {}

        # Consensus tracking
        self.consensus_operations: Dict[str, ConsensusResult] = {}
        self.vote_history: deque = deque(maxlen=1000)

        # Synchronization state
        self.sync_queue: deque = deque()
        self.sync_in_progress: Set[str] = set()
        self.last_global_sync: Optional[datetime] = None

        # Network and protocol handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.consensus_handlers: Dict[ConsensusProtocol, Callable] = {}

        # Performance tracking
        self.sync_metrics: Dict[str, Any] = {
            "total_operations": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "average_latency_ms": 0.0,
            "consensus_success_rate": 0.0,
        }

        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.sync_task: Optional[asyncio.Task] = None
        self.consensus_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Initialize handlers
        self._setup_message_handlers()
        self._setup_consensus_handlers()

    async def start(self):
        """Start the distributed memory orchestrator"""
        logger.info(f"🚀 Starting Distributed Memory Orchestrator: {self.node_id}")

        try:
            # Initialize local memory integrator if provided
            if self.memory_integrator:
                await self.memory_integrator.initialize_memory_consciousness_coupling()

            # Start background tasks
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.sync_task = asyncio.create_task(self._sync_loop())
            self.consensus_task = asyncio.create_task(self._consensus_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

            # Set state to joining
            self.state = NodeState.JOINING
            self.local_node.state = NodeState.JOINING

            # Discover and join existing network
            await self._discover_network()

            # Set state to active
            self.state = NodeState.ACTIVE
            self.local_node.state = NodeState.ACTIVE

            logger.info(f"✅ Distributed Memory Orchestrator started: {self.node_id}")

        except Exception as e:
            self.state = NodeState.FAILED
            logger.error(f"❌ Failed to start Distributed Memory Orchestrator: {e}")
            raise

    async def stop(self):
        """Stop the distributed memory orchestrator"""
        logger.info(f"🛑 Stopping Distributed Memory Orchestrator: {self.node_id}")

        self.state = NodeState.OFFLINE
        self._shutdown_event.set()

        # Cancel background tasks
        for task in [self.heartbeat_task, self.sync_task, self.consensus_task, self.cleanup_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Notify other nodes of shutdown
        await self._broadcast_node_shutdown()

        logger.info(f"✅ Distributed Memory Orchestrator stopped: {self.node_id}")

    async def store_memory_fold(
        self, memory_fold: MemoryFold, replicate: bool = True, consensus_required: bool = True
    ) -> bool:
        """Store memory fold in distributed system"""

        operation_id = f"store_{uuid.uuid4().hex[:8]}"
        fold_id = memory_fold.id if hasattr(memory_fold, "id") else memory_fold.fold_id

        # Store locally first
        self.local_memory_folds[fold_id] = memory_fold

        if not replicate:
            return True

        # Create sync operation
        sync_op = SyncOperation(
            operation_id=operation_id,
            operation_type="create",
            fold_id=fold_id,
            source_node=self.node_id,
            target_nodes=self._select_replica_nodes(fold_id),
            payload={
                "memory_fold": self._serialize_memory_fold(memory_fold),
                "checksum": self._calculate_fold_checksum(memory_fold),
            },
            timestamp=datetime.utcnow(),
            priority=2,
            consensus_required=consensus_required,
        )

        # Queue for processing
        self.pending_operations[operation_id] = sync_op
        self.sync_queue.append(operation_id)

        # Wait for consensus if required
        if consensus_required:
            consensus_result = await self._wait_for_consensus(operation_id, timeout=5.0)
            if consensus_result and consensus_result.consensus_reached:
                # Create replication record
                await self._create_replication_record(fold_id, sync_op.target_nodes)
                logger.info(f"📦 Memory fold stored with consensus: {fold_id}")
                return True
            else:
                logger.warning(f"⚠️ Consensus failed for memory fold: {fold_id}")
                return False

        logger.info(f"📦 Memory fold queued for replication: {fold_id}")
        return True

    async def retrieve_memory_fold(self, fold_id: str, prefer_local: bool = True) -> Optional[MemoryFold]:
        """Retrieve memory fold from distributed system"""

        # Try local storage first
        if prefer_local and fold_id in self.local_memory_folds:
            return self.local_memory_folds[fold_id]

        # Try to find in replication records
        if fold_id in self.replication_records:
            replication_record = self.replication_records[fold_id]

            # Try replicas
            for replica_node in replication_record.replica_nodes:
                if replica_node in self.active_nodes:
                    memory_fold = await self._request_memory_fold_from_node(replica_node, fold_id)
                    if memory_fold:
                        # Store locally for caching
                        self.local_memory_folds[fold_id] = memory_fold
                        return memory_fold

        # Try all active nodes as last resort
        for node_id in self.active_nodes:
            memory_fold = await self._request_memory_fold_from_node(node_id, fold_id)
            if memory_fold:
                # Store locally for caching
                self.local_memory_folds[fold_id] = memory_fold
                return memory_fold

        logger.warning(f"⚠️ Memory fold not found: {fold_id}")
        return None

    async def delete_memory_fold(self, fold_id: str, consensus_required: bool = True) -> bool:
        """Delete memory fold from distributed system"""

        operation_id = f"delete_{uuid.uuid4().hex[:8]}"

        # Remove from local storage
        if fold_id in self.local_memory_folds:
            del self.local_memory_folds[fold_id]

        # Get replication targets
        target_nodes = set()
        if fold_id in self.replication_records:
            target_nodes = self.replication_records[fold_id].replica_nodes

        # Create sync operation
        sync_op = SyncOperation(
            operation_id=operation_id,
            operation_type="delete",
            fold_id=fold_id,
            source_node=self.node_id,
            target_nodes=target_nodes,
            payload={"fold_id": fold_id},
            timestamp=datetime.utcnow(),
            priority=1,
            consensus_required=consensus_required,
        )

        # Queue for processing
        self.pending_operations[operation_id] = sync_op
        self.sync_queue.append(operation_id)

        # Wait for consensus if required
        if consensus_required:
            consensus_result = await self._wait_for_consensus(operation_id, timeout=5.0)
            if consensus_result and consensus_result.consensus_reached:
                # Remove replication record
                if fold_id in self.replication_records:
                    del self.replication_records[fold_id]
                logger.info(f"🗑️ Memory fold deleted with consensus: {fold_id}")
                return True
            else:
                logger.warning(f"⚠️ Consensus failed for delete operation: {fold_id}")
                return False

        logger.info(f"🗑️ Memory fold queued for deletion: {fold_id}")
        return True

    async def synchronize_with_network(self) -> Dict[str, Any]:
        """Perform full synchronization with network"""

        sync_start = time.time()
        sync_results = {"nodes_contacted": 0, "folds_synchronized": 0, "conflicts_resolved": 0, "errors": []}

        try:
            self.state = NodeState.SYNCING

            # Get list of all memory folds from all nodes
            network_folds = await self._collect_network_memory_state()

            # Resolve conflicts and synchronize
            for fold_id, fold_data in network_folds.items():
                try:
                    await self._synchronize_memory_fold(fold_id, fold_data)
                    sync_results["folds_synchronized"] += 1
                except Exception as e:
                    sync_results["errors"].append(f"Failed to sync {fold_id}: {e}")

            # Update last sync time
            self.last_global_sync = datetime.utcnow()
            self.state = NodeState.ACTIVE

            sync_duration = (time.time() - sync_start) * 1000
            logger.info(f"🔄 Network synchronization completed in {sync_duration:.1f}ms")

        except Exception as e:
            sync_results["errors"].append(f"Synchronization failed: {e}")
            logger.error(f"❌ Network synchronization failed: {e}")

        return sync_results

    async def add_trusted_node(self, node_id: str, address: str, port: int) -> bool:
        """Add a trusted node to the network"""

        if node_id == self.node_id:
            return False

        # Create node info
        node = DistributedNode(
            node_id=node_id,
            address=address,
            port=port,
            state=NodeState.ACTIVE,
            capabilities={"fold_storage", "consensus", "replication"},
            last_heartbeat=datetime.utcnow(),
        )

        # Add to known nodes
        self.known_nodes[node_id] = node
        self.active_nodes.add(node_id)
        self.trusted_nodes.add(node_id)

        # Send introduction message
        await self._send_node_introduction(node_id)

        logger.info(f"🤝 Added trusted node: {node_id} at {address}:{port}")
        return True

    async def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""

        return {
            "local_node": {
                "node_id": self.node_id,
                "state": self.state.value,
                "memory_folds": len(self.local_memory_folds),
                "replications": len(self.replication_records),
            },
            "network": {
                "known_nodes": len(self.known_nodes),
                "active_nodes": len(self.active_nodes),
                "trusted_nodes": len(self.trusted_nodes),
            },
            "synchronization": {
                "pending_operations": len(self.pending_operations),
                "sync_queue_size": len(self.sync_queue),
                "last_global_sync": self.last_global_sync.isoformat() if self.last_global_sync else None,
            },
            "consensus": {
                "protocol": self.consensus_protocol.value,
                "active_operations": len(self.consensus_operations),
                "success_rate": self.sync_metrics["consensus_success_rate"],
            },
            "performance": self.sync_metrics,
        }

    def _select_replica_nodes(self, fold_id: str) -> Set[str]:
        """Select nodes for memory fold replication"""

        available_nodes = self.active_nodes - {self.node_id}

        if self.replication_strategy == ReplicationStrategy.NONE:
            return set()
        elif self.replication_strategy == ReplicationStrategy.MIRROR:
            # Select one random node
            return set(list(available_nodes)[:1]) if available_nodes else set()
        elif self.replication_strategy == ReplicationStrategy.QUORUM:
            # Select N/2+1 nodes for quorum
            quorum_size = len(available_nodes) // 2 + 1
            return set(list(available_nodes)[:quorum_size])
        elif self.replication_strategy == ReplicationStrategy.FULL_MESH:
            # All available nodes
            return available_nodes
        elif self.replication_strategy == ReplicationStrategy.RING:
            # Ring topology - next 2 nodes in sorted order
            sorted_nodes = sorted(available_nodes)
            fold_hash = int(hashlib.sha256(fold_id.encode()).hexdigest()[:8], 16)
            start_idx = fold_hash % len(sorted_nodes) if sorted_nodes else 0
            ring_nodes = []
            for i in range(min(2, len(sorted_nodes))):
                idx = (start_idx + i) % len(sorted_nodes)
                ring_nodes.append(sorted_nodes[idx])
            return set(ring_nodes)

        return set()

    def _serialize_memory_fold(self, memory_fold: MemoryFold) -> Dict[str, Any]:
        """Serialize memory fold for network transmission"""
        try:
            # Convert dataclass to dict
            if hasattr(memory_fold, "__dict__"):
                fold_dict = asdict(memory_fold)
            else:
                fold_dict = {
                    "fold_id": getattr(memory_fold, "fold_id", getattr(memory_fold, "id", str(uuid.uuid4()))),
                    "content": getattr(memory_fold, "content", {}),
                    "fold_type": getattr(memory_fold, "fold_type", "EPISODIC"),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Ensure datetime objects are serialized
            for key, value in fold_dict.items():
                if isinstance(value, datetime):
                    fold_dict[key] = value.isoformat()

            return fold_dict
        except Exception as e:
            logger.error(f"Failed to serialize memory fold: {e}")
            return {}

    def _calculate_fold_checksum(self, memory_fold: MemoryFold) -> str:
        """Calculate checksum for memory fold integrity"""
        fold_data = self._serialize_memory_fold(memory_fold)
        content_str = json.dumps(fold_data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def _create_replication_record(self, fold_id: str, replica_nodes: Set[str]):
        """Create replication record for memory fold"""

        memory_fold = self.local_memory_folds.get(fold_id)
        if not memory_fold:
            return

        checksum = self._calculate_fold_checksum(memory_fold)

        replication_record = ReplicationRecord(
            fold_id=fold_id,
            primary_node=self.node_id,
            replica_nodes=replica_nodes,
            replication_factor=len(replica_nodes) + 1,  # +1 for primary
            created_at=datetime.utcnow(),
            last_verified=datetime.utcnow(),
            checksum=checksum,
        )

        self.replication_records[fold_id] = replication_record

    async def _wait_for_consensus(self, operation_id: str, timeout: float = 5.0) -> Optional[ConsensusResult]:
        """Wait for consensus operation to complete"""

        start_time = time.time()
        while time.time() - start_time < timeout:
            if operation_id in self.consensus_operations:
                return self.consensus_operations[operation_id]
            await asyncio.sleep(0.1)

        return None

    async def _request_memory_fold_from_node(self, node_id: str, fold_id: str) -> Optional[MemoryFold]:
        """Request memory fold from specific node"""
        # Placeholder for actual network communication
        # In production, this would use HTTP/gRPC/WebSocket

        if node_id not in self.known_nodes:
            return None

        # Simulate network request
        await asyncio.sleep(0.001)  # Simulated network latency

        # For now, return None (would implement actual network protocol)
        return None

    async def _collect_network_memory_state(self) -> Dict[str, Any]:
        """Collect memory state from all network nodes"""

        network_state = {}

        # Add local folds
        for fold_id, memory_fold in self.local_memory_folds.items():
            network_state[fold_id] = {
                "source_node": self.node_id,
                "fold_data": self._serialize_memory_fold(memory_fold),
                "checksum": self._calculate_fold_checksum(memory_fold),
            }

        # Request from other nodes (placeholder)
        for node_id in self.active_nodes:
            if node_id != self.node_id:
                # Simulate network request for node state
                pass

        return network_state

    async def _synchronize_memory_fold(self, fold_id: str, fold_data: Dict[str, Any]):
        """Synchronize individual memory fold"""

        fold_data.get("source_node")
        checksum = fold_data.get("checksum")

        # Check if we have this fold
        if fold_id in self.local_memory_folds:
            local_checksum = self._calculate_fold_checksum(self.local_memory_folds[fold_id])
            if local_checksum == checksum:
                return  # Already synchronized
            else:
                # Conflict resolution needed
                await self._resolve_memory_conflict(fold_id, fold_data)
        else:
            # New fold - add to local storage
            # Would deserialize and store the fold
            pass

    async def _resolve_memory_conflict(self, fold_id: str, remote_fold_data: Dict[str, Any]):
        """Resolve conflict between local and remote memory fold"""

        # Simple conflict resolution: newest wins
        local_fold = self.local_memory_folds.get(fold_id)
        if not local_fold:
            return

        # Compare timestamps (simplified)
        local_timestamp = getattr(local_fold, "timestamp", datetime.min)
        remote_timestamp_str = remote_fold_data.get("fold_data", {}).get("timestamp")

        if remote_timestamp_str:
            try:
                remote_timestamp = datetime.fromisoformat(remote_timestamp_str.replace("Z", "+00:00"))
                if remote_timestamp > local_timestamp:
                    # Remote fold is newer - would update local
                    logger.info(f"🔄 Resolved conflict for {fold_id}: remote newer")
                else:
                    logger.info(f"🔄 Resolved conflict for {fold_id}: local newer")
            except ValueError:
                logger.warning(f"⚠️ Invalid timestamp in remote fold: {fold_id}")

    async def _discover_network(self):
        """Discover existing network nodes"""

        # For now, just start as standalone node
        # In production, would implement service discovery
        logger.info(f"🔍 Network discovery completed - standalone node: {self.node_id}")

    async def _broadcast_node_shutdown(self):
        """Notify other nodes of shutdown"""

        # Placeholder for network broadcast
        logger.info(f"📢 Broadcasting shutdown for node: {self.node_id}")

    async def _send_node_introduction(self, target_node_id: str):
        """Send introduction message to node"""

        # Placeholder for network message
        logger.info(f"👋 Sending introduction to node: {target_node_id}")

    def _setup_message_handlers(self):
        """Setup network message handlers"""

        self.message_handlers = {
            "heartbeat": self._handle_heartbeat,
            "sync_request": self._handle_sync_request,
            "consensus_vote": self._handle_consensus_vote,
            "memory_fold_request": self._handle_memory_fold_request,
            "memory_fold_response": self._handle_memory_fold_response,
            "node_introduction": self._handle_node_introduction,
            "node_shutdown": self._handle_node_shutdown,
        }

    def _setup_consensus_handlers(self):
        """Setup consensus protocol handlers"""

        self.consensus_handlers = {
            ConsensusProtocol.SIMPLE_MAJORITY: self._handle_simple_majority_consensus,
            ConsensusProtocol.BYZANTINE_FAULT_TOLERANT: self._handle_bft_consensus,
            ConsensusProtocol.EVENTUAL_CONSISTENCY: self._handle_eventual_consistency,
            ConsensusProtocol.STRONG_CONSISTENCY: self._handle_strong_consistency,
        }

    async def _handle_heartbeat(self, node_id: str, message: Dict[str, Any]):
        """Handle heartbeat message from node"""

        if node_id in self.known_nodes:
            self.known_nodes[node_id].last_heartbeat = datetime.utcnow()
            self.active_nodes.add(node_id)

    async def _handle_sync_request(self, node_id: str, message: Dict[str, Any]):
        """Handle synchronization request"""

        # Placeholder for sync request handling
        pass

    async def _handle_consensus_vote(self, node_id: str, message: Dict[str, Any]):
        """Handle consensus vote message"""

        operation_id = message.get("operation_id")
        vote = message.get("vote")  # "approve" or "reject"

        if operation_id in self.pending_operations:
            # Process vote using appropriate consensus protocol
            consensus_handler = self.consensus_handlers.get(self.consensus_protocol)
            if consensus_handler:
                await consensus_handler(operation_id, node_id, vote)

    async def _handle_memory_fold_request(self, node_id: str, message: Dict[str, Any]):
        """Handle memory fold request"""

        fold_id = message.get("fold_id")
        if fold_id in self.local_memory_folds:
            # Send memory fold response
            memory_fold = self.local_memory_folds[fold_id]
            {
                "type": "memory_fold_response",
                "fold_id": fold_id,
                "fold_data": self._serialize_memory_fold(memory_fold),
                "checksum": self._calculate_fold_checksum(memory_fold),
            }
            # Would send response via network
            logger.debug(f"📤 Sending memory fold {fold_id} to {node_id}")

    async def _handle_memory_fold_response(self, node_id: str, message: Dict[str, Any]):
        """Handle memory fold response"""

        fold_id = message.get("fold_id")
        message.get("fold_data")
        message.get("checksum")

        # Would deserialize and store the fold
        logger.debug(f"📥 Received memory fold {fold_id} from {node_id}")

    async def _handle_node_introduction(self, node_id: str, message: Dict[str, Any]):
        """Handle node introduction message"""

        node_info = message.get("node_info", {})

        if node_id not in self.known_nodes:
            node = DistributedNode(
                node_id=node_id,
                address=node_info.get("address", "unknown"),
                port=node_info.get("port", 0),
                state=NodeState.ACTIVE,
                capabilities=set(node_info.get("capabilities", [])),
                last_heartbeat=datetime.utcnow(),
            )

            self.known_nodes[node_id] = node
            self.active_nodes.add(node_id)

            logger.info(f"👋 New node introduced: {node_id}")

    async def _handle_node_shutdown(self, node_id: str, message: Dict[str, Any]):
        """Handle node shutdown message"""

        if node_id in self.known_nodes:
            self.known_nodes[node_id].state = NodeState.OFFLINE
            self.active_nodes.discard(node_id)

            logger.info(f"👋 Node shutdown: {node_id}")

    async def _handle_simple_majority_consensus(self, operation_id: str, node_id: str, vote: str):
        """Handle simple majority consensus"""

        if operation_id not in self.consensus_operations:
            self.consensus_operations[operation_id] = ConsensusResult(
                operation_id=operation_id,
                consensus_reached=False,
                participating_nodes=set(),
                confirming_nodes=set(),
                rejecting_nodes=set(),
                consensus_time_ms=0.0,
            )

        result = self.consensus_operations[operation_id]
        result.participating_nodes.add(node_id)

        if vote == "approve":
            result.confirming_nodes.add(node_id)
        else:
            result.rejecting_nodes.add(node_id)

        # Check if majority reached
        total_nodes = len(self.active_nodes) + 1  # +1 for self
        required_votes = total_nodes // 2 + 1

        if len(result.confirming_nodes) >= required_votes:
            result.consensus_reached = True
            logger.debug(f"✅ Consensus reached for operation: {operation_id}")
        elif len(result.rejecting_nodes) >= required_votes:
            result.consensus_reached = False
            result.error_message = "Majority rejected"
            logger.debug(f"❌ Consensus rejected for operation: {operation_id}")

    async def _handle_bft_consensus(self, operation_id: str, node_id: str, vote: str):
        """Handle Byzantine Fault Tolerant consensus"""
        # Placeholder for BFT implementation
        await self._handle_simple_majority_consensus(operation_id, node_id, vote)

    async def _handle_eventual_consistency(self, operation_id: str, node_id: str, vote: str):
        """Handle eventual consistency"""
        # Always approve for eventual consistency
        if operation_id not in self.consensus_operations:
            self.consensus_operations[operation_id] = ConsensusResult(
                operation_id=operation_id,
                consensus_reached=True,
                participating_nodes={node_id},
                confirming_nodes={node_id},
                rejecting_nodes=set(),
                consensus_time_ms=0.0,
            )

    async def _handle_strong_consistency(self, operation_id: str, node_id: str, vote: str):
        """Handle strong consistency (requires unanimous approval)"""

        if operation_id not in self.consensus_operations:
            self.consensus_operations[operation_id] = ConsensusResult(
                operation_id=operation_id,
                consensus_reached=False,
                participating_nodes=set(),
                confirming_nodes=set(),
                rejecting_nodes=set(),
                consensus_time_ms=0.0,
            )

        result = self.consensus_operations[operation_id]
        result.participating_nodes.add(node_id)

        if vote == "approve":
            result.confirming_nodes.add(node_id)
        else:
            result.rejecting_nodes.add(node_id)
            result.consensus_reached = False
            result.error_message = "Unanimous approval required"

        # Check if unanimous approval
        total_nodes = len(self.active_nodes) + 1  # +1 for self
        if len(result.confirming_nodes) == total_nodes:
            result.consensus_reached = True

    async def _heartbeat_loop(self):
        """Background heartbeat loop"""

        while not self._shutdown_event.is_set():
            try:
                # Update local heartbeat
                self.local_node.last_heartbeat = datetime.utcnow()

                # Send heartbeat to all known nodes
                for node_id in self.known_nodes:
                    # Would send heartbeat message via network
                    pass

                # Check for offline nodes
                cutoff_time = datetime.utcnow() - timedelta(seconds=30)
                offline_nodes = []

                for node_id, node in self.known_nodes.items():
                    if node.last_heartbeat < cutoff_time:
                        offline_nodes.append(node_id)

                # Mark offline nodes
                for node_id in offline_nodes:
                    self.known_nodes[node_id].state = NodeState.OFFLINE
                    self.active_nodes.discard(node_id)

                await asyncio.sleep(10.0)  # Heartbeat every 10 seconds

            except Exception as e:
                logger.error(f"❌ Heartbeat loop error: {e}")
                await asyncio.sleep(5.0)

    async def _sync_loop(self):
        """Background synchronization loop"""

        while not self._shutdown_event.is_set():
            try:
                if self.sync_queue:
                    operation_id = self.sync_queue.popleft()
                    if operation_id in self.pending_operations:
                        await self._process_sync_operation(operation_id)

                await asyncio.sleep(0.1)  # Process sync queue

            except Exception as e:
                logger.error(f"❌ Sync loop error: {e}")
                await asyncio.sleep(1.0)

    async def _consensus_loop(self):
        """Background consensus processing loop"""

        while not self._shutdown_event.is_set():
            try:
                # Clean up old consensus operations
                cutoff_time = datetime.utcnow() - timedelta(seconds=60)
                expired_operations = []

                for operation_id, result in self.consensus_operations.items():
                    if operation_id in self.pending_operations:
                        op = self.pending_operations[operation_id]
                        if op.timestamp < cutoff_time:
                            expired_operations.append(operation_id)

                for operation_id in expired_operations:
                    if operation_id in self.consensus_operations:
                        del self.consensus_operations[operation_id]
                    if operation_id in self.pending_operations:
                        del self.pending_operations[operation_id]

                await asyncio.sleep(10.0)  # Consensus cleanup every 10 seconds

            except Exception as e:
                logger.error(f"❌ Consensus loop error: {e}")
                await asyncio.sleep(5.0)

    async def _cleanup_loop(self):
        """Background cleanup loop"""

        while not self._shutdown_event.is_set():
            try:
                # Clean up old operations
                cutoff_time = datetime.utcnow() - timedelta(hours=1)

                # Clean up vote history
                while self.vote_history and self.vote_history[0].get("timestamp", datetime.min) < cutoff_time:
                    self.vote_history.popleft()

                # Update metrics
                total_ops = len(self.pending_operations)
                if total_ops > 0:
                    self.sync_metrics["total_operations"] = total_ops

                await asyncio.sleep(300.0)  # Cleanup every 5 minutes

            except Exception as e:
                logger.error(f"❌ Cleanup loop error: {e}")
                await asyncio.sleep(60.0)

    async def _process_sync_operation(self, operation_id: str):
        """Process synchronization operation"""

        if operation_id not in self.pending_operations:
            return

        operation = self.pending_operations[operation_id]

        try:
            # Process based on operation type
            if operation.operation_type == "create":
                await self._process_create_operation(operation)
            elif operation.operation_type == "update":
                await self._process_update_operation(operation)
            elif operation.operation_type == "delete":
                await self._process_delete_operation(operation)

            self.sync_metrics["successful_syncs"] += 1

        except Exception as e:
            operation.retry_count += 1
            if operation.retry_count < operation.max_retries:
                # Re-queue for retry
                self.sync_queue.append(operation_id)
            else:
                # Max retries reached
                del self.pending_operations[operation_id]
                self.sync_metrics["failed_syncs"] += 1

            logger.error(f"❌ Sync operation failed: {operation_id} - {e}")

    async def _process_create_operation(self, operation: SyncOperation):
        """Process create operation"""

        # Send create request to target nodes
        for target_node in operation.target_nodes:
            if target_node in self.active_nodes:
                # Would send network message
                logger.debug(f"📤 Sending create request to {target_node} for {operation.fold_id}")

        # Complete operation
        del self.pending_operations[operation.operation_id]

    async def _process_update_operation(self, operation: SyncOperation):
        """Process update operation"""

        # Send update request to target nodes
        for target_node in operation.target_nodes:
            if target_node in self.active_nodes:
                # Would send network message
                logger.debug(f"📤 Sending update request to {target_node} for {operation.fold_id}")

        # Complete operation
        del self.pending_operations[operation.operation_id]

    async def _process_delete_operation(self, operation: SyncOperation):
        """Process delete operation"""

        # Send delete request to target nodes
        for target_node in operation.target_nodes:
            if target_node in self.active_nodes:
                # Would send network message
                logger.debug(f"📤 Sending delete request to {target_node} for {operation.fold_id}")

        # Complete operation
        del self.pending_operations[operation.operation_id]
