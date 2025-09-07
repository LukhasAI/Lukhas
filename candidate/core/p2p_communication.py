"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - P2P DECENTRALIZED COMMUNICATION MODULE
║ Peer-to-peer communication system for distributed AI agents
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: p2p_communication.py
║ Path: lukhas/core/p2p_communication.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Implements TODO 60: P2P decentralized communication model where peers connect
║ and exchange information directly without central servers. Provides robustness,
║ fault tolerance, and reduced latency for high-bandwidth agent communication.
╚══════════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import json
import logging
import random
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class PeerStatus(Enum):
    """Peer connection states"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


class MessageType(Enum):
    """P2P message types"""

    HANDSHAKE = "handshake"
    HEARTBEAT = "heartbeat"
    DATA = "data"
    DISCOVERY = "discovery"
    ROUTING = "routing"
    ACK = "ack"


@dataclass
class PeerInfo:
    """Information about a peer in the network"""

    peer_id: str
    address: str
    port: int
    status: PeerStatus
    last_seen: float
    capabilities: set[str]
    latency_ms: float = 0.0
    reliability_score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "peer_id": self.peer_id,
            "address": self.address,
            "port": self.port,
            "status": self.status.value,
            "last_seen": self.last_seen,
            "capabilities": list(self.capabilities),
            "latency_ms": self.latency_ms,
            "reliability_score": self.reliability_score,
        }


@dataclass
class P2PMessage:
    """P2P network message"""

    message_id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    message_type: MessageType
    payload: Any
    timestamp: float
    ttl: int = 5  # Time to live for routing

    def to_bytes(self) -> bytes:
        """Serialize message to bytes"""
        data = {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> "P2PMessage":
        """Deserialize message from bytes"""
        msg_dict = json.loads(data.decode("utf-8"))
        return cls(
            message_id=msg_dict["message_id"],
            sender_id=msg_dict["sender_id"],
            recipient_id=msg_dict["recipient_id"],
            message_type=MessageType(msg_dict["message_type"]),
            payload=msg_dict["payload"],
            timestamp=msg_dict["timestamp"],
            ttl=msg_dict.get("ttl", 5),
        )


class P2PNode:
    """
    Decentralized P2P node supporting direct peer communication.
    Each node can act as both client and server.
    """

    def __init__(
        self,
        node_id: str,
        host: str = "127.0.0.1",
        port: int = 0,  # 0 = auto-assign
        capabilities: Optional[set[str]] = None,
    ):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.capabilities = capabilities or set()

        # Peer management
        self.peers: dict[str, PeerInfo] = {}
        self.connections: dict[str, tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}

        # Message handling
        self.message_handlers: dict[MessageType, list[Callable]] = defaultdict(list)
        self.pending_acks: dict[str, asyncio.Future] = {}
        self.message_cache: set[str] = set()  # Prevent duplicate processing

        # Network state
        self._server: Optional[asyncio.Server] = None
        self._running = False
        self._tasks: list[asyncio.Task] = []

        # Routing table for multi-hop
        self.routing_table: dict[str, str] = {}  # destination -> next_hop

        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
        }

    async def start(self) -> None:
        """Start the P2P node"""
        if self._running:
            return

        # Start server
        self._server = await asyncio.start_server(self._handle_connection, self.host, self.port)

        # Get actual port if auto-assigned
        if self.port == 0:
            self.port = self._server.sockets[0].getsockname()[1]

        self._running = True

        # Start background tasks
        self._tasks.append(asyncio.create_task(self._heartbeat_loop()))
        self._tasks.append(asyncio.create_task(self._peer_maintenance_loop()))

        logger.info(f"P2P node {self.node_id} started on {self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the P2P node"""
        self._running = False

        # Close all connections
        for _peer_id, (_reader, writer) in list(self.connections.items()):
            writer.close()
            await writer.wait_closed()

        # Stop server
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()

        logger.info(f"P2P node {self.node_id} stopped")

    async def connect_to_peer(self, address: str, port: int) -> Optional[str]:
        """
        Connect to a peer node.
        Returns peer_id if successful, None otherwise.
        """
        try:
            reader, writer = await asyncio.open_connection(address, port)

            # Send handshake
            handshake_msg = P2PMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=None,
                message_type=MessageType.HANDSHAKE,
                payload={
                    "capabilities": list(self.capabilities),
                    "port": self.port,
                },
                timestamp=time.time(),
            )

            await self._send_message(writer, handshake_msg)

            # Wait for response
            response = await self._receive_message(reader)
            if response and response.message_type == MessageType.HANDSHAKE:
                peer_id = response.sender_id

                # Store connection
                self.connections[peer_id] = (reader, writer)

                # Store peer info
                self.peers[peer_id] = PeerInfo(
                    peer_id=peer_id,
                    address=address,
                    port=response.payload["port"],
                    status=PeerStatus.CONNECTED,
                    last_seen=time.time(),
                    capabilities=set(response.payload["capabilities"]),
                )

                # Start message handler for this connection
                asyncio.create_task(self._handle_peer_messages(peer_id, reader))

                logger.info(f"Connected to peer {peer_id}")
                return peer_id

        except Exception as e:
            logger.error(f"Failed to connect to {address}:{port}: {e}")

        return None

    async def send_to_peer(self, peer_id: str, payload: Any, require_ack: bool = False) -> bool:
        """
        Send data directly to a specific peer.
        Returns True if sent successfully.
        """
        if peer_id not in self.connections:
            # Try multi-hop routing
            if peer_id in self.routing_table:
                next_hop = self.routing_table[peer_id]
                if next_hop in self.connections:
                    return await self._route_message(peer_id, payload, next_hop)
            return False

        message = P2PMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.node_id,
            recipient_id=peer_id,
            message_type=MessageType.DATA,
            payload=payload,
            timestamp=time.time(),
        )

        # Setup ACK handling if required
        ack_future = None
        if require_ack:
            ack_future = asyncio.Future()
            self.pending_acks[message.message_id] = ack_future

        # Send message
        _, writer = self.connections[peer_id]
        success = await self._send_message(writer, message)

        if success:
            self.stats["messages_sent"] += 1

            # Wait for ACK if required
            if require_ack:
                try:
                    await asyncio.wait_for(ack_future, timeout=5.0)
                    return True
                except asyncio.TimeoutError:
                    del self.pending_acks[message.message_id]
                    return False

        return success

    async def broadcast(self, payload: Any) -> int:
        """
        Broadcast message to all connected peers.
        Returns number of peers reached.
        """
        message = P2PMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.node_id,
            recipient_id=None,
            message_type=MessageType.DATA,
            payload=payload,
            timestamp=time.time(),
        )

        sent_count = 0
        for _, writer in self.connections.values():
            if await self._send_message(writer, message):
                sent_count += 1

        self.stats["messages_sent"] += sent_count
        return sent_count

    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a message handler for a specific message type"""
        self.message_handlers[message_type].append(handler)

    async def discover_peers(self, bootstrap_peers: list[tuple[str, int]]) -> int:
        """
        Discover peers through bootstrap nodes.
        Returns number of new peers discovered.
        """
        discovered = 0

        # Connect to bootstrap peers
        for address, port in bootstrap_peers:
            peer_id = await self.connect_to_peer(address, port)
            if peer_id:
                discovered += 1

                # Request peer list
                await self.send_to_peer(peer_id, {"request": "peer_list"}, require_ack=False)

        return discovered

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming peer connection"""
        peer_address = writer.get_extra_info("peername")
        logger.debug(f"New connection from {peer_address}")

        try:
            # Wait for handshake
            message = await self._receive_message(reader)
            if message and message.message_type == MessageType.HANDSHAKE:
                peer_id = message.sender_id

                # Send handshake response
                response = P2PMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.node_id,
                    recipient_id=peer_id,
                    message_type=MessageType.HANDSHAKE,
                    payload={
                        "capabilities": list(self.capabilities),
                        "port": self.port,
                    },
                    timestamp=time.time(),
                )

                await self._send_message(writer, response)

                # Store connection
                self.connections[peer_id] = (reader, writer)

                # Store peer info
                self.peers[peer_id] = PeerInfo(
                    peer_id=peer_id,
                    address=peer_address[0],
                    port=message.payload["port"],
                    status=PeerStatus.CONNECTED,
                    last_seen=time.time(),
                    capabilities=set(message.payload["capabilities"]),
                )

                # Handle messages from this peer
                await self._handle_peer_messages(peer_id, reader)

        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _handle_peer_messages(self, peer_id: str, reader: asyncio.StreamReader) -> None:
        """Handle messages from a connected peer"""
        while self._running and peer_id in self.connections:
            try:
                message = await self._receive_message(reader)
                if not message:
                    break

                # Update last seen
                if peer_id in self.peers:
                    self.peers[peer_id].last_seen = time.time()

                # Check for duplicate
                if message.message_id in self.message_cache:
                    continue

                self.message_cache.add(message.message_id)
                self.stats["messages_received"] += 1

                # Handle message based on type
                if message.message_type == MessageType.HEARTBEAT:
                    # Update peer latency
                    latency = (time.time() - message.timestamp) * 1000
                    self.peers[peer_id].latency_ms = latency

                elif message.message_type == MessageType.DATA:
                    # Process or route message
                    if message.recipient_id == self.node_id:
                        # Message for us
                        await self._process_data_message(message)
                    elif message.recipient_id is None:
                        # Broadcast message - process locally AND forward
                        await self._process_data_message(message)
                        await self._forward_broadcast(message, exclude=peer_id)
                    else:
                        # Route to recipient
                        await self._route_message(
                            message.recipient_id,
                            message.payload,
                            exclude=peer_id,
                        )

                elif message.message_type == MessageType.ACK:
                    # Handle acknowledgment
                    orig_msg_id = message.payload.get("message_id")
                    if orig_msg_id in self.pending_acks:
                        self.pending_acks[orig_msg_id].set_result(True)

                elif message.message_type == MessageType.DISCOVERY:
                    # Share peer list
                    peer_list = [peer.to_dict() for peer in self.peers.values() if peer.status == PeerStatus.CONNECTED]
                    await self.send_to_peer(peer_id, {"peers": peer_list})

            except Exception as e:
                logger.error(f"Error handling message from {peer_id}: {e}")
                break

        # Clean up connection
        if peer_id in self.connections:
            del self.connections[peer_id]
        if peer_id in self.peers:
            self.peers[peer_id].status = PeerStatus.DISCONNECTED

    async def _send_message(self, writer: asyncio.StreamWriter, message: P2PMessage) -> bool:
        """Send a message to a peer"""
        try:
            data = message.to_bytes()
            writer.write(len(data).to_bytes(4, "big"))
            writer.write(data)
            await writer.drain()

            self.stats["bytes_sent"] += len(data) + 4
            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def _receive_message(self, reader: asyncio.StreamReader) -> Optional[P2PMessage]:
        """Receive a message from a peer"""
        try:
            # Read message length
            length_bytes = await reader.readexactly(4)
            length = int.from_bytes(length_bytes, "big")

            # Read message data
            data = await reader.readexactly(length)
            self.stats["bytes_received"] += length + 4

            return P2PMessage.from_bytes(data)

        except Exception as e:
            logger.debug(f"Failed to receive message: {e}")
            return None

    async def _process_data_message(self, message: P2PMessage) -> None:
        """Process a data message intended for this node"""
        # Send ACK if message has recipient
        if message.recipient_id:
            ack = P2PMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=message.sender_id,
                message_type=MessageType.ACK,
                payload={"message_id": message.message_id},
                timestamp=time.time(),
            )

            if message.sender_id in self.connections:
                _, writer = self.connections[message.sender_id]
                await self._send_message(writer, ack)

        # Call registered handlers
        for handler in self.message_handlers[MessageType.DATA]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(self, message)
                else:
                    handler(self, message)
            except Exception as e:
                logger.error(f"Handler error: {e}")

    async def _forward_broadcast(self, message: P2PMessage, exclude: str) -> None:
        """Forward a broadcast message to all peers except sender"""
        if message.ttl <= 0:
            return

        # Decrease TTL
        message.ttl -= 1

        for peer_id, (_, writer) in self.connections.items():
            if peer_id != exclude:
                await self._send_message(writer, message)

    async def _route_message(
        self,
        destination: str,
        payload: Any,
        next_hop: Optional[str] = None,
        exclude: Optional[str] = None,
    ) -> bool:
        """Route a message to destination via next hop"""
        if destination in self.connections and destination != exclude:
            # Direct connection available
            return await self.send_to_peer(destination, payload)

        # Use routing table
        if not next_hop and destination in self.routing_table:
            next_hop = self.routing_table[destination]

        if next_hop and next_hop in self.connections and next_hop != exclude:
            # Forward via next hop
            message = P2PMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=destination,
                message_type=MessageType.DATA,
                payload=payload,
                timestamp=time.time(),
                ttl=5,
            )

            _, writer = self.connections[next_hop]
            return await self._send_message(writer, message)

        return False

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to maintain connections"""
        while self._running:
            try:
                heartbeat = P2PMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.node_id,
                    recipient_id=None,
                    message_type=MessageType.HEARTBEAT,
                    payload={},
                    timestamp=time.time(),
                )

                for _peer_id, (_, writer) in list(self.connections.items()):
                    await self._send_message(writer, heartbeat)

                await asyncio.sleep(30)  # Heartbeat every 30 seconds

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    async def _peer_maintenance_loop(self) -> None:
        """Maintain peer connections and clean up stale ones"""
        while self._running:
            try:
                current_time = time.time()
                timeout = 120  # 2 minutes

                for peer_id, peer_info in list(self.peers.items()):
                    if peer_info.status == PeerStatus.CONNECTED:
                        if current_time - peer_info.last_seen > timeout:
                            # Peer timed out
                            logger.info(f"Peer {peer_id} timed out")
                            peer_info.status = PeerStatus.DISCONNECTED

                            # Close connection
                            if peer_id in self.connections:
                                _, writer = self.connections[peer_id]
                                writer.close()
                                await writer.wait_closed()
                                del self.connections[peer_id]

                # Clean up old message cache
                if len(self.message_cache) > 10000:
                    self.message_cache.clear()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Peer maintenance error: {e}")

    def get_network_stats(self) -> dict[str, Any]:
        """Get network statistics"""
        connected_peers = [p for p in self.peers.values() if p.status == PeerStatus.CONNECTED]

        avg_latency = sum(p.latency_ms for p in connected_peers) / len(connected_peers) if connected_peers else 0

        return {
            "node_id": self.node_id,
            "connected_peers": len(connected_peers),
            "total_peers": len(self.peers),
            "avg_latency_ms": avg_latency,
            "messages_sent": self.stats["messages_sent"],
            "messages_received": self.stats["messages_received"],
            "bytes_sent": self.stats["bytes_sent"],
            "bytes_received": self.stats["bytes_received"],
        }


# Example usage functions


async def create_p2p_network(num_nodes: int = 5) -> list[P2PNode]:
    """
    Create a test P2P network with multiple nodes.
    """
    nodes = []

    # Create nodes
    for i in range(num_nodes):
        node = P2PNode(
            node_id=f"node_{i}",
            capabilities={"compute", "storage"} if i % 2 == 0 else {"relay"},
        )
        await node.start()
        nodes.append(node)

    # Connect nodes in a mesh topology
    for i, node in enumerate(nodes):
        # Connect to previous nodes
        for j in range(i):
            if random.random() > 0.3:  # 70% connection probability
                await node.connect_to_peer("127.0.0.1", nodes[j].port)

    return nodes


async def data_handler(node: P2PNode, message: P2PMessage):
    """Example data message handler"""
    logger.info(f"Node {node.node_id} received: {message.payload}")

    # Example: aggregate data from multiple sources
    if "values" in message.payload:
        if not hasattr(node, "aggregated_values"):
            node.aggregated_values = []
        node.aggregated_values.extend(message.payload["values"])

        if len(node.aggregated_values) >= 10:
            result = sum(node.aggregated_values)
            logger.info(f"Node {node.node_id} aggregated result: {result}")
            node.aggregated_values = []
