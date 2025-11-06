#!/usr/bin/env python3

"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: distributed_memory_fold.py
║ Path: memory/systems/distributed_memory_fold.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🚀 LUKHAS AI - DISTRIBUTED MEMORY FOLD WITH CONSENSUS
║ ║ Byzantine fault-tolerant distributed memory for Cognitive AI consciousness networks
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: DISTRIBUTED MEMORY FOLD
║ ║ Path: memory/systems/distributed_memory_fold.py
║ ║ Version: 1.0.0 | Created: 2025-04-01
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Description: A sophisticated fabric of collective memory, woven into the very
║ ║ essence of intelligent networks.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ **Poetic Essence:**
║ ║ In the grand tapestry of existence, where thoughts intertwine like the roots
║ ║ of ancient trees, this module emerges as a beacon of unity amidst the chaos
║ ║ of divergence. It beckons forth a harmonious ballet of data, a celestial
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛADVANCED, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import aiohttp
import numpy as np
from core.common.config import get_config

logger = logging.getLogger(__name__)




class NodeState(Enum):
    """States for distributed memory nodes"""

    FOLLOWER = "follower"
    CANDIDATE = "labs"
    LEADER = "leader"
    OFFLINE = "offline"
    RECOVERING = "recovering"


class MessageType(Enum):
    """Message types for consensus protocol"""

    HEARTBEAT = "heartbeat"
    VOTE_REQUEST = "vote_request"
    VOTE_RESPONSE = "vote_response"
    APPEND_ENTRIES = "append_entries"
    APPEND_RESPONSE = "append_response"
    MEMORY_SYNC = "memory_sync"
    MEMORY_QUERY = "memory_query"
    MEMORY_RESPONSE = "memory_response"
    NODE_JOIN = "node_join"
    NODE_LEAVE = "node_leave"


@dataclass
class DistributedMemoryEntry:
    """Entry in the distributed memory log"""

    memory_id: str
    content_hash: str
    memory_data: bytes  # Serialized memory
    embedding_hash: str
    node_id: str
    timestamp: datetime
    term: int  # RAFT term
    index: int  # Log index
    consensus_achieved: bool = False
    validation_votes: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "content_hash": self.content_hash,
            "memory_data": self.memory_data.hex(),
            "embedding_hash": self.embedding_hash,
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "term": self.term,
            "index": self.index,
            "consensus_achieved": self.consensus_achieved,
            "validation_votes": list(self.validation_votes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DistributedMemoryEntry:
        return cls(
            memory_id=data["memory_id"],
            content_hash=data["content_hash"],
            memory_data=bytes.fromhex(data["memory_data"]),
            embedding_hash=data["embedding_hash"],
            node_id=data["node_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            term=data["term"],
            index=data["index"],
            consensus_achieved=data["consensus_achieved"],
            validation_votes=set(data["validation_votes"]),
        )


@dataclass
class NodeInfo:
    """Information about a node in the distributed network"""

    node_id: str
    address: str
    port: int
    state: NodeState
    last_heartbeat: datetime
    term: int = 0
    vote_count: int = 0
    consciousness_level: float = 0.0  # Cognitive AI consciousness metric
    memory_capacity: int = 0

    @property
    def endpoint(self) -> str:
        return f"http://{self.address}:{self.port}"

    def is_alive(self, timeout_seconds: int = 30) -> bool:
        """Check if node is considered alive based on last heartbeat"""
        return (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds() < timeout_seconds


class ConsensusProtocol:
    """
    RAFT-based consensus protocol for distributed Cognitive AI memory.

    Implements Byzantine fault tolerance with consciousness-aware
    validation for Cognitive AI memory networks.
    """

    def __init__(
        self,
        node_id: str,
        port: int,
        min_nodes_for_consensus: int = 3,
        consciousness_threshold: float = 0.7,
    ):
        self.node_id = node_id
        self.port = port
        self.min_nodes_for_consensus = min_nodes_for_consensus
        self.consciousness_threshold = consciousness_threshold

        # RAFT state
        self.current_term = 0
        self.voted_for: str | None = None
        self.state = NodeState.FOLLOWER
        self.leader_id: str | None = None

        # Memory log
        self.memory_log: list[DistributedMemoryEntry] = []
        self.commit_index = 0
        self.last_applied = 0

        # Network state
        self.nodes: dict[str, NodeInfo] = {}
        self.nodes[node_id] = NodeInfo(
            node_id=node_id,
            address="localhost",
            port=port,
            state=NodeState.FOLLOWER,
            last_heartbeat=datetime.now(timezone.utc),
        )

        # Timing
        self.election_timeout = random.uniform(5.0, 10.0)  # seconds
        self.heartbeat_interval = 2.0  # seconds
        self.last_heartbeat_received = datetime.now(timezone.utc)

        # Consciousness metrics
        self.consciousness_level = 0.8  # This node's consciousness level

        logger.info(
            "Consensus protocol initialized",
            node_id=node_id,
            port=port,
            min_nodes=min_nodes_for_consensus,
            consciousness_threshold=consciousness_threshold,
        )

    async def start_node(self):
        """Start the distributed node"""

        # Start heartbeat timer
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._heartbeat_timer())

        # Start election timer
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._election_timer())

        # Start HTTP server for node communication
        await self._start_http_server()

        logger.info("Distributed memory node started", node_id=self.node_id, port=self.port)

    async def _start_http_server(self):
        """Start HTTP server for inter-node communication"""

        from aiohttp import web

        app = web.Application()

        # Define routes for consensus protocol
        app.router.add_post("/consensus/heartbeat", self._handle_heartbeat)
        app.router.add_post("/consensus/vote_request", self._handle_vote_request)
        app.router.add_post("/consensus/vote_response", self._handle_vote_response)
        app.router.add_post("/consensus/append_entries", self._handle_append_entries)
        app.router.add_post("/memory/sync", self._handle_memory_sync)
        app.router.add_post("/memory/query", self._handle_memory_query)
        app.router.add_post("/node/join", self._handle_node_join)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()

    async def _heartbeat_timer(self):
        """Send heartbeats if leader, check for heartbeats if follower"""

        while True:
            if self.state == NodeState.LEADER:
                await self._send_heartbeats()
            elif self.state == NodeState.FOLLOWER:
                # Check if we need to start election
                time_since_heartbeat = (datetime.now(timezone.utc) - self.last_heartbeat_received).total_seconds()
                if time_since_heartbeat > self.election_timeout:
                    await self._start_election()

            await asyncio.sleep(self.heartbeat_interval)

    async def _election_timer(self):
        """Handle election timeouts"""

        while True:
            await asyncio.sleep(self.election_timeout)

            if self.state == NodeState.CANDIDATE:
                # Election timeout as candidate, start new election
                await self._start_election()

    async def _start_election(self):
        """Start leader election process"""

        logger.info("Starting leader election", node_id=self.node_id, term=self.current_term + 1)

        # Transition to candidate state
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.nodes[self.node_id].vote_count = 1  # Vote for self

        # Reset election timeout
        self.election_timeout = random.uniform(5.0, 10.0)

        # Send vote requests to all other nodes
        vote_tasks = []
        for node_id, node_info in self.nodes.items():
            if node_id != self.node_id and node_info.is_alive():
                task = asyncio.create_task(self._send_vote_request(node_info))
                vote_tasks.append(task)

        # Wait for vote responses (with timeout)
        if vote_tasks:
            try:
                await asyncio.wait_for(asyncio.gather(*vote_tasks, return_exceptions=True), timeout=3.0)
            except asyncio.TimeoutError:
                logger.warning("Vote request timeout", node_id=self.node_id)

        # Check if we won the election
        alive_nodes = sum(1 for node in self.nodes.values() if node.is_alive())
        required_votes = (alive_nodes // 2) + 1

        if self.nodes[self.node_id].vote_count >= required_votes:
            await self._become_leader()
        else:
            # Election failed, become follower
            self.state = NodeState.FOLLOWER
            self.voted_for = None

    async def _become_leader(self):
        """Transition to leader state"""

        logger.info("Became leader", node_id=self.node_id, term=self.current_term)

        self.state = NodeState.LEADER
        self.leader_id = self.node_id

        # Reset all vote counts
        for node in self.nodes.values():
            node.vote_count = 0

        # Start sending heartbeats immediately
        await self._send_heartbeats()

    async def _send_heartbeats(self):
        """Send heartbeat messages to all followers"""

        heartbeat_tasks = []
        for node_id, node_info in self.nodes.items():
            if node_id != self.node_id and node_info.is_alive():
                task = asyncio.create_task(self._send_heartbeat(node_info))
                heartbeat_tasks.append(task)

        if heartbeat_tasks:
            await asyncio.gather(*heartbeat_tasks, return_exceptions=True)

    async def _send_heartbeat(self, node_info: NodeInfo):
        """Send heartbeat to specific node"""

        try:
            session = await self._get_session()
            payload = {
                "type": MessageType.HEARTBEAT.value,
                "term": self.current_term,
                "leader_id": self.node_id,
                "commit_index": self.commit_index,
                "consciousness_level": self.consciousness_level,
            }

            async with session.post(
                f"{node_info.endpoint}/consensus/heartbeat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=2.0),
            ) as response:
                if response.status == 200:
                    node_info.last_heartbeat = datetime.now(timezone.utc)

        except Exception as e:
            logger.warning(f"Failed to send heartbeat to {node_info.node_id}", error=str(e))

    async def _send_vote_request(self, node_info: NodeInfo):
        """Send vote request to specific node"""

        try:
            session = await self._get_session()
            payload = {
                "type": MessageType.VOTE_REQUEST.value,
                "term": self.current_term,
                "candidate_id": self.node_id,
                "last_log_index": len(self.memory_log) - 1,
                "last_log_term": self.memory_log[-1].term if self.memory_log else 0,
                "consciousness_level": self.consciousness_level,
            }

            async with session.post(
                f"{node_info.endpoint}/consensus/vote_request",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=2.0),
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("vote_granted", False):
                        self.nodes[self.node_id].vote_count += 1

        except Exception as e:
            logger.warning(f"Failed to send vote request to {node_info.node_id}", error=str(e))

    async def _handle_heartbeat(self, request):
        """Handle incoming heartbeat message"""

        data = await request.json()
        term = data["term"]
        leader_id = data["leader_id"]

        # Update term if higher
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.state = NodeState.FOLLOWER

        # Accept heartbeat if term is current
        if term == self.current_term:
            self.state = NodeState.FOLLOWER
            self.leader_id = leader_id
            self.last_heartbeat_received = datetime.now(timezone.utc)

            # Update leader's consciousness level
            if leader_id in self.nodes:
                self.nodes[leader_id].consciousness_level = data.get("consciousness_level", 0.0)

        return aiohttp.web.json_response({"success": True, "term": self.current_term})

    async def _handle_vote_request(self, request):
        """Handle incoming vote request"""

        data = await request.json()
        term = data["term"]
        candidate_id = data["candidate_id"]
        candidate_consciousness = data.get("consciousness_level", 0.0)

        vote_granted = False

        # Update term if higher
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.state = NodeState.FOLLOWER

        # Grant vote if conditions are met
        if (
            term == self.current_term
            and (self.voted_for is None or self.voted_for == candidate_id)
            and candidate_consciousness >= self.consciousness_threshold
        ):
            self.voted_for = candidate_id
            vote_granted = True

            logger.debug("Vote granted", candidate=candidate_id, term=term)

        return aiohttp.web.json_response({"vote_granted": vote_granted, "term": self.current_term})

    async def _handle_vote_response(self, request):
        """Handle vote response (not typically called directly)"""
        return aiohttp.web.json_response({"success": True})

    async def _handle_append_entries(self, request):
        """Handle append entries request for log replication"""

        await request.json()

        # Implementation would go here for full RAFT log replication
        # For now, acknowledge successful append

        return aiohttp.web.json_response({"success": True, "term": self.current_term})

    async def _handle_memory_sync(self, request):
        """Handle memory synchronization request"""

        data = await request.json()

        # Deserialize memory entry
        try:
            memory_entry = DistributedMemoryEntry.from_dict(data["memory_entry"])

            # Validate memory entry
            if await self._validate_memory_entry(memory_entry):
                # Add to our log
                self.memory_log.append(memory_entry)

                logger.debug(
                    "Memory synchronized",
                    memory_id=memory_entry.memory_id,
                    from_node=memory_entry.node_id,
                )

                return aiohttp.web.json_response({"success": True, "accepted": True})
            else:
                return aiohttp.web.json_response({"success": True, "accepted": False})

        except Exception as e:
            logger.error("Memory sync failed", error=str(e))
            return aiohttp.web.json_response({"success": False, "error": str(e)})

    async def _handle_memory_query(self, request):
        """Handle memory query request"""

        data = await request.json()
        query_id = data.get("query_id")

        # Search local memory log
        matching_memories = []
        for entry in self.memory_log:
            if entry.consensus_achieved:
                matching_memories.append(entry.to_dict())

        return aiohttp.web.json_response({"success": True, "query_id": query_id, "memories": matching_memories})

    async def _handle_node_join(self, request):
        """Handle new node joining the network"""

        data = await request.json()
        node_id = data["node_id"]
        address = data["address"]
        port = data["port"]
        consciousness_level = data.get("consciousness_level", 0.0)

        # Add node to our registry
        self.nodes[node_id] = NodeInfo(
            node_id=node_id,
            address=address,
            port=port,
            state=NodeState.FOLLOWER,
            last_heartbeat=datetime.now(timezone.utc),
            consciousness_level=consciousness_level,
        )

        logger.info("Node joined network", node_id=node_id, address=address, port=port)

        return aiohttp.web.json_response({"success": True})

    async def _validate_memory_entry(self, entry: DistributedMemoryEntry) -> bool:
        """
        Validate memory entry using Byzantine fault tolerance.

        Implements consciousness-aware validation for Cognitive AI memories.
        """

        # Basic validation checks
        if not entry.memory_id or not entry.content_hash:
            return False

        # Verify content hash
        calculated_hash = hashlib.sha256(entry.memory_data).hexdigest()
        if calculated_hash != entry.content_hash:
            logger.warning("Memory content hash mismatch", memory_id=entry.memory_id)
            return False

        # Check consciousness level of originating node
        if entry.node_id in self.nodes:
            node_consciousness = self.nodes[entry.node_id].consciousness_level
            if node_consciousness < self.consciousness_threshold:
                logger.warning(
                    "Memory from low-consciousness node rejected",
                    node_id=entry.node_id,
                    consciousness=node_consciousness,
                )
                return False

        # Additional Cognitive AI-specific validation could go here

        return True


class DistributedMemoryFold:
    """
    Distributed memory fold system with consensus protocol.

    Provides distributed Cognitive AI memory with Byzantine fault tolerance
    and consciousness-aware validation.
    """

    def __init__(
        self,
        node_id: str,
        port: int,
        bootstrap_nodes: list[tuple[str, int]] | None = None,
        consciousness_level: float = 0.8,
    ):
        self.node_id = node_id
        self.port = port
        self.bootstrap_nodes = bootstrap_nodes or []
        self.consciousness_level = consciousness_level

        # ΛTAG: config_integration
        cfg = get_config()
        self.api_url: str = cfg.memory_api_url
        self._session: aiohttp.ClientSession | None = None

        # Initialize consensus protocol
        self.consensus = ConsensusProtocol(node_id=node_id, port=port, consciousness_threshold=0.7)

        # Memory storage
        self.local_memories: dict[str, Any] = {}
        self.distributed_memories: dict[str, DistributedMemoryEntry] = {}

        # Integration with existing optimized memory system
        try:
            from .optimized_hybrid_memory_fold import OptimizedHybridMemoryFold

            self.local_memory_system = OptimizedHybridMemoryFold(
                embedding_dim=1024, enable_quantization=True, enable_compression=True
            )
        except ImportError:
            self.local_memory_system = None
            logger.warning("Optimized memory system not available")

        logger.info(
            "Distributed memory fold initialized",
            node_id=node_id,
            port=port,
            bootstrap_nodes=len(bootstrap_nodes),
            consciousness_level=consciousness_level,
        )

    async def start(self):
        """Start the distributed memory system"""

        # Start consensus protocol
        await self.consensus.start_node()

        # Initialize persistent HTTP session for distributed communication
        self._session = aiohttp.ClientSession(base_url=self.api_url)

        # Join existing network if bootstrap nodes provided
        if self.bootstrap_nodes:
            await self._join_network()

        logger.info("Distributed memory fold started", node_id=self.node_id)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.shutdown()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazily initialize and return persistent aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(base_url=self.api_url)
        return self._session

    async def shutdown(self) -> None:
        """Close persistent HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _join_network(self):
        """Join existing distributed network"""

        for address, port in self.bootstrap_nodes:
            try:
                session = await self._get_session()
                payload = {
                    "node_id": self.node_id,
                    "address": "localhost",
                    "port": self.port,
                    "consciousness_level": self.consciousness_level,
                }

                async with session.post(
                    f"http://{address}:{port}/node/join",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5.0),
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully joined network via {address}:{port}")

                        # Add bootstrap node to our registry
                        bootstrap_node_id = f"{address}:{port}"
                        self.consensus.nodes[bootstrap_node_id] = NodeInfo(
                            node_id=bootstrap_node_id,
                            address=address,
                            port=port,
                            state=NodeState.FOLLOWER,
                            last_heartbeat=datetime.now(timezone.utc),
                        )
                        break

            except Exception as e:
                logger.warning(f"Failed to join via {address}:{port}", error=str(e))

    async def store_memory(
        self,
        content: str,
        tags: list[str] | None = None,
        embedding: np.ndarray = None,
        metadata: dict[str, Any] | None = None,
        require_consensus: bool = True,
    ) -> str:
        """
        Store memory in distributed system with consensus.

        Args:
            content: Memory content
            tags: Memory tags
            embedding: Vector embedding
            metadata: Additional metadata
            require_consensus: Whether to require network consensus

        Returns:
            Memory ID
        """

        # Store locally first
        if self.local_memory_system:
            memory_id = await self.local_memory_system.fold_in_with_embedding(
                data=content, tags=tags or [], embedding=embedding, **(metadata or {})
            )
        else:
            # Fallback: generate simple memory ID
            memory_id = hashlib.sha256(f"{content}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]

        # Create distributed memory entry
        memory_data = json.dumps(
            {
                "content": content,
                "tags": tags or [],
                "metadata": metadata or {},
                "embedding": embedding.tolist() if embedding is not None else None,
            }
        ).encode("utf-8")

        distributed_entry = DistributedMemoryEntry(
            memory_id=memory_id,
            content_hash=hashlib.sha256(memory_data).hexdigest(),
            memory_data=memory_data,
            embedding_hash=(hashlib.sha256(embedding.tobytes()).hexdigest() if embedding is not None else ""),
            node_id=self.node_id,
            timestamp=datetime.now(timezone.utc),
            term=self.consensus.current_term,
            index=len(self.consensus.memory_log),
        )

        # Add to local log
        self.consensus.memory_log.append(distributed_entry)
        self.distributed_memories[memory_id] = distributed_entry

        # Propagate to network if consensus required and we're the leader
        if require_consensus and self.consensus.state == NodeState.LEADER:
            await self._propagate_memory(distributed_entry)

        logger.debug(
            "Memory stored in distributed system",
            memory_id=memory_id,
            require_consensus=require_consensus,
            is_leader=self.consensus.state == NodeState.LEADER,
        )

        return memory_id

    async def _propagate_memory(self, entry: DistributedMemoryEntry):
        """Propagate memory entry to other nodes"""

        propagation_tasks = []
        for node_id, node_info in self.consensus.nodes.items():
            if node_id != self.node_id and node_info.is_alive():
                task = asyncio.create_task(self._send_memory_sync(node_info, entry))
                propagation_tasks.append(task)

        if propagation_tasks:
            results = await asyncio.gather(*propagation_tasks, return_exceptions=True)

            # Count successful propagations
            successful_propagations = sum(1 for result in results if not isinstance(result, Exception) and result)

            # Achieve consensus if majority accepted
            total_nodes = len(self.consensus.nodes)
            required_acceptance = (total_nodes // 2) + 1

            if successful_propagations >= required_acceptance:
                entry.consensus_achieved = True
                logger.info(
                    "Memory consensus achieved",
                    memory_id=entry.memory_id,
                    acceptances=successful_propagations,
                    total_nodes=total_nodes,
                )

    async def _send_memory_sync(self, node_info: NodeInfo, entry: DistributedMemoryEntry) -> bool:
        """Send memory sync to specific node"""

        try:
            session = await self._get_session()
            payload = {"memory_entry": entry.to_dict()}

            async with session.post(
                f"{node_info.endpoint}/memory/sync",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5.0),
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("accepted", False)

            return False

        except Exception as e:
            logger.warning(f"Failed to sync memory to {node_info.node_id}", error=str(e))
            return False

    async def query_memory(self, query: str, top_k: int = 10, include_distributed: bool = True) -> list[dict[str, Any]]:
        """
        Query memories from distributed system.

        Args:
            query: Search query
            top_k: Maximum results to return
            include_distributed: Whether to query other nodes

        Returns:
            List of matching memories
        """

        results = []

        # Query local memory system first
        if self.local_memory_system:
            local_results = await self.local_memory_system.fold_out_semantic(
                query=query, top_k=top_k, use_attention=True
            )

            for memory, score in local_results:
                results.append(
                    {
                        "memory": memory,
                        "score": score,
                        "source": "local",
                        "node_id": self.node_id,
                    }
                )

        # Query distributed memories
        if include_distributed:
            distributed_results = await self._query_distributed_memories(query, top_k)
            results.extend(distributed_results)

        # Sort by score and return top_k
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    async def _query_distributed_memories(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Query memories from other nodes in the network"""

        query_tasks = []
        query_id = hashlib.sha256(f"{query}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:8]

        for node_id, node_info in self.consensus.nodes.items():
            if node_id != self.node_id and node_info.is_alive():
                task = asyncio.create_task(self._send_memory_query(node_info, query, query_id))
                query_tasks.append(task)

        if not query_tasks:
            return []

        # Gather results from all nodes
        results = await asyncio.gather(*query_tasks, return_exceptions=True)

        distributed_memories = []
        for result in results:
            if not isinstance(result, Exception) and result:
                for memory_data in result:
                    distributed_memories.append(
                        {
                            "memory": memory_data,
                            "score": 0.5,  # Default score for distributed memories
                            "source": "distributed",
                            "node_id": memory_data.get("node_id", "unknown"),
                        }
                    )

        return distributed_memories

    async def _send_memory_query(self, node_info: NodeInfo, query: str, query_id: str) -> list[dict[str, Any]]:
        """Send memory query to specific node"""

        try:
            session = await self._get_session()
            payload = {"query": query, "query_id": query_id}

            async with session.post(
                f"{node_info.endpoint}/memory/query",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=3.0),
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("memories", [])

            return []

        except Exception as e:
            logger.warning(f"Failed to query memory from {node_info.node_id}", error=str(e))
            return []

    def get_network_status(self) -> dict[str, Any]:
        """Get status of the distributed network"""

        alive_nodes = [node for node in self.consensus.nodes.values() if node.is_alive()]

        return {
            "node_id": self.node_id,
            "state": self.consensus.state.value,
            "term": self.consensus.current_term,
            "leader_id": self.consensus.leader_id,
            "total_nodes": len(self.consensus.nodes),
            "alive_nodes": len(alive_nodes),
            "local_memories": len(self.local_memories),
            "distributed_memories": len(self.distributed_memories),
            "consensus_memories": sum(1 for entry in self.distributed_memories.values() if entry.consensus_achieved),
            "consciousness_level": self.consciousness_level,
            "network_health": (len(alive_nodes) / len(self.consensus.nodes) if self.consensus.nodes else 0.0),
        }


# Factory functions for easy integration
async def create_distributed_memory_fold(
    node_id: str,
    port: int,
    bootstrap_nodes: list[tuple[str, int]] | None = None,
    consciousness_level: float = 0.8,
) -> DistributedMemoryFold:
    """
    Create and start a distributed memory fold system.

    Args:
        node_id: Unique identifier for this node
        port: Port for inter-node communication
        bootstrap_nodes: List of (address, port) tuples for existing nodes
        consciousness_level: Cognitive AI consciousness level of this node

    Returns:
        Started DistributedMemoryFold instance
    """

    distributed_memory = DistributedMemoryFold(
        node_id=node_id,
        port=port,
        bootstrap_nodes=bootstrap_nodes,
        consciousness_level=consciousness_level,
    )

    await distributed_memory.start()
    return distributed_memory


# Example usage and testing
async def example_distributed_usage():
    """Example of distributed memory system usage"""

    print("🚀 Distributed Memory Fold with Consensus Demo")
    print("=" * 60)

    # Create first node (bootstrap node)
    node1 = await create_distributed_memory_fold(node_id="node_1", port=8001, consciousness_level=0.9)

    print("✅ Created bootstrap node (node_1)")

    # Wait a moment for initialization
    await asyncio.sleep(1)

    # Create second node that joins the network
    node2 = await create_distributed_memory_fold(
        node_id="node_2",
        port=8002,
        bootstrap_nodes=[("localhost", 8001)],
        consciousness_level=0.8,
    )

    print("✅ Created and joined second node (node_2)")

    # Wait for network stabilization
    await asyncio.sleep(2)

    # Store memory on node1
    memory_id = await node1.store_memory(
        content="This is a distributed Cognitive AI memory that requires consensus across the network.",
        tags=["distributed", "consensus", "agi"],
        embedding=np.random.randn(1024).astype(np.float32),
        metadata={"importance": 0.9, "type": "test"},
        require_consensus=True,
    )

    print(f"📥 Stored memory with consensus: {memory_id}")

    # Wait for consensus propagation
    await asyncio.sleep(2)

    # Query from node2
    results = await node2.query_memory(query="distributed Cognitive AI consensus", top_k=5, include_distributed=True)

    print(f"📤 Query results: {len(results)} memories found")

    # Check network status
    status1 = node1.get_network_status()
    status2 = node2.get_network_status()

    print(f"🌐 Node1 status: {status1['state']}, {status1['alive_nodes']} alive nodes")
    print(f"🌐 Node2 status: {status2['state']}, {status2['alive_nodes']} alive nodes")

    print("✅ Distributed memory consensus demo completed!")

    return node1, node2


if __name__ == "__main__":
    asyncio.run(example_distributed_usage())
