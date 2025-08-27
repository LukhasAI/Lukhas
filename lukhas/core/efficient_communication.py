"""
LUKHAS AI Efficient Communication System
Energy-optimized communication fabric for colony and agent coordination
Trinity Framework: ⚛️🧠🛡️

This module provides efficient communication patterns for the LUKHAS ecosystem,
supporting event-driven messaging, P2P transfers, and energy optimization.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Callable
from typing import Optional

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels for efficient routing"""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class CommunicationMode(Enum):
    """Communication modes for different traffic types"""

    EVENT_BUS = "event_bus"  # Lightweight coordination
    P2P_DIRECT = "p2p_direct"  # High-volume data transfer
    MULTICAST = "multicast"  # Efficient broadcast
    GOSSIP = "gossip"  # Epidemic protocols


@dataclass
class Message:
    """Optimized message structure for minimal overhead"""

    message_id: str
    source: str
    destination: str
    message_type: str
    payload: dict[str, Any]
    priority: MessagePriority
    mode: CommunicationMode
    timestamp: float
    ttl: int = 30  # Time to live in seconds
    compression: bool = False
    size_bytes: int = 0
    energy_cost: float = 0.0

    def __post_init__(self):
        """Calculate message size and energy cost"""
        self.size_bytes = len(json.dumps(self.payload))
        self.energy_cost = self._calculate_energy_cost()

    def _calculate_energy_cost(self) -> float:
        """Calculate energy cost based on message characteristics"""
        base_cost = 0.1  # Base energy unit
        size_factor = self.size_bytes / 1024.0  # KB

        priority_factor = {
            MessagePriority.CRITICAL: 1.5,
            MessagePriority.HIGH: 1.2,
            MessagePriority.NORMAL: 1.0,
            MessagePriority.LOW: 0.8,
            MessagePriority.BACKGROUND: 0.5,
        }[self.priority]

        mode_factor = {
            CommunicationMode.P2P_DIRECT: 0.7,  # Most efficient for large data
            CommunicationMode.EVENT_BUS: 1.0,  # Standard efficiency
            CommunicationMode.MULTICAST: 0.6,  # Efficient for many recipients
            CommunicationMode.GOSSIP: 1.3,  # Higher overhead
        }[self.mode]

        return base_cost * size_factor * priority_factor * mode_factor

    def is_expired(self) -> bool:
        """Check if message has expired"""
        return (time.time() - self.timestamp) > self.ttl

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary"""
        return {
            **asdict(self),
            "priority": self.priority.value,
            "mode": self.mode.value,
        }


class MessageRouter:
    """
    Intelligent message router that selects optimal communication paths
    based on message characteristics and network conditions
    """

    def __init__(self):
        self.routing_table: dict[str, dict[str, Any]] = {}
        self.network_conditions: dict[str, float] = {}
        self.energy_budget = 1000.0  # Available energy units
        self.energy_used = 0.0
        self._lock = threading.Lock()

    def register_node(
        self,
        node_id: str,
        capabilities: Optional[list[str]] = None,
        location: Optional[dict[str, Any]] = None,
    ):
        """Register a node in the routing table"""
        with self._lock:
            self.routing_table[node_id] = {
                "capabilities": capabilities or [],
                "location": location or {},
                "last_seen": time.time(),
                "energy_efficiency": 1.0,
                "message_count": 0,
                "total_latency": 0.0,
            }

    def select_communication_mode(self, message: Message) -> CommunicationMode:
        """Select the most energy-efficient communication mode"""
        payload_size = message.size_bytes
        priority = message.priority

        # Large data transfers use P2P for efficiency
        if payload_size > 10240:  # 10KB threshold
            return CommunicationMode.P2P_DIRECT

        # Critical messages use event bus for reliability
        if priority in [MessagePriority.CRITICAL, MessagePriority.HIGH]:
            return CommunicationMode.EVENT_BUS

        # Multiple recipients use multicast
        if isinstance(message.destination, list) and len(message.destination) > 3:
            return CommunicationMode.MULTICAST

        # Default to event bus
        return CommunicationMode.EVENT_BUS

    def find_optimal_path(self, source: str, destination: str) -> list[str]:
        """Find the most energy-efficient path between nodes"""
        # Simple implementation - direct path for now
        # In a real system, this would consider network topology
        return [source, destination]

    def can_afford_message(self, message: Message) -> bool:
        """Check if we have enough energy budget for the message"""
        return (self.energy_used + message.energy_cost) <= self.energy_budget

    def record_message_sent(self, message: Message, latency: float):
        """Record message statistics for learning"""
        with self._lock:
            self.energy_used += message.energy_cost

            if message.destination in self.routing_table:
                node_info = self.routing_table[message.destination]
                node_info["message_count"] += 1
                node_info["total_latency"] += latency
                node_info["last_seen"] = time.time()


class EventBus:
    """
    Lightweight event bus for coordination and discovery
    Optimized for minimal broker load
    """

    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.stats = {
            "messages_published": 0,
            "messages_delivered": 0,
            "energy_consumed": 0.0,
            "average_latency": 0.0,
        }
        self._running = False

    async def start(self):
        """Start the event bus"""
        self._running = True
        asyncio.create_task(self._process_messages())
        logger.info("Event bus started")

    async def stop(self):
        """Stop the event bus"""
        self._running = False

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events of a specific type"""
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from events"""
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)

    async def publish(self, message: Message) -> bool:
        """Publish a message to the event bus"""
        try:
            await self.message_queue.put(message)
            self.stats["messages_published"] += 1
            return True
        except asyncio.QueueFull:
            logger.warning("Event bus queue full, dropping message")
            return False

    async def _process_messages(self):
        """Process messages from the queue"""
        while self._running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)

                start_time = time.time()
                await self._deliver_message(message)

                # Update statistics
                latency = time.time() - start_time
                self.stats["messages_delivered"] += 1
                self.stats["energy_consumed"] += message.energy_cost
                self.stats["average_latency"] = (
                    self.stats["average_latency"]
                    * (self.stats["messages_delivered"] - 1)
                    + latency
                ) / self.stats["messages_delivered"]

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def _deliver_message(self, message: Message):
        """Deliver message to subscribers"""
        handlers = self.subscribers.get(message.message_type, [])

        if not handlers:
            logger.debug(f"No handlers for message type: {message.message_type}")
            return

        # Deliver to all handlers
        delivery_tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._safe_handle(handler, message))
            delivery_tasks.append(task)

        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)

    async def _safe_handle(self, handler: Callable, message: Message):
        """Safely execute a message handler"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
        except Exception as e:
            logger.error(f"Handler error: {e}")


class P2PChannel:
    """
    Direct peer-to-peer channel for high-volume data transfers
    Bypasses the central broker for efficiency
    """

    def __init__(self, local_node_id: str):
        self.local_node_id = local_node_id
        self.connections: dict[str, dict[str, Any]] = {}
        self.transfer_stats = {
            "bytes_sent": 0,
            "bytes_received": 0,
            "connections_established": 0,
            "energy_saved": 0.0,
        }

    async def establish_connection(
        self, remote_node_id: str, connection_info: dict[str, Any]
    ) -> bool:
        """Establish a direct connection to another node"""
        try:
            self.connections[remote_node_id] = {
                "connection_info": connection_info,
                "established_at": time.time(),
                "bytes_transferred": 0,
                "last_activity": time.time(),
            }

            self.transfer_stats["connections_established"] += 1
            logger.info(f"P2P connection established with {remote_node_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to establish P2P connection: {e}")
            return False

    async def send_direct(self, remote_node_id: str, data: bytes) -> bool:
        """Send data directly to a peer"""
        if remote_node_id not in self.connections:
            logger.warning(f"No P2P connection to {remote_node_id}")
            return False

        try:
            connection = self.connections[remote_node_id]
            connection["bytes_transferred"] += len(data)
            connection["last_activity"] = time.time()

            self.transfer_stats["bytes_sent"] += len(data)

            # Calculate energy savings compared to broker routing
            broker_energy_cost = len(data) * 0.001  # Simulated broker overhead
            direct_energy_cost = len(data) * 0.0007  # Direct transfer efficiency
            energy_saved = broker_energy_cost - direct_energy_cost
            self.transfer_stats["energy_saved"] += energy_saved

            logger.debug(f"Sent {len(data)} bytes to {remote_node_id} via P2P")
            return True

        except Exception as e:
            logger.error(f"P2P send error: {e}")
            return False

    def get_connection_stats(self) -> dict[str, Any]:
        """Get P2P connection statistics"""
        return {
            "active_connections": len(self.connections),
            "transfer_stats": self.transfer_stats,
            "connections": {
                node_id: {
                    "bytes_transferred": conn["bytes_transferred"],
                    "uptime": time.time() - conn["established_at"],
                    "last_activity": conn["last_activity"],
                }
                for node_id, conn in self.connections.items()
            },
        }


class EfficientCommunicationFabric:
    """
    Main communication fabric that orchestrates all communication modes
    for maximum energy efficiency
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.router = MessageRouter()
        self.event_bus = EventBus()
        self.p2p_channel = P2PChannel(node_id)
        self.message_cache: dict[str, Message] = {}
        self.energy_monitor = EnergyMonitor()
        self._total_messages = 0

        # Register self in routing table
        self.router.register_node(node_id, ["communication", "routing"])

    async def start(self):
        """Start the communication fabric"""
        await self.event_bus.start()
        logger.info(f"Communication fabric started for node {self.node_id}")

    async def stop(self):
        """Stop the communication fabric"""
        await self.event_bus.stop()

    async def send_message(
        self,
        destination: str,
        message_type: str,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> bool:
        """Send a message using the most efficient communication mode"""
        message = Message(
            message_id=str(uuid.uuid4()),
            source=self.node_id,
            destination=destination,
            message_type=message_type,
            payload=payload,
            priority=priority,
            mode=CommunicationMode.EVENT_BUS,  # Will be optimized
            timestamp=time.time(),
        )

        # Optimize communication mode
        optimal_mode = self.router.select_communication_mode(message)
        message.mode = optimal_mode

        # Check energy budget
        if not self.router.can_afford_message(message):
            logger.warning(
                f"Insufficient energy budget for message {message.message_id}"
            )
            return False

        # Route message based on selected mode
        success = False
        start_time = time.time()

        if optimal_mode == CommunicationMode.P2P_DIRECT:
            # Use P2P for large data transfers
            data = json.dumps(message.to_dict()).encode()
            success = await self.p2p_channel.send_direct(destination, data)

        else:  # EVENT_BUS, MULTICAST, GOSSIP
            # Use event bus for coordination
            success = await self.event_bus.publish(message)

        # Record statistics
        if success:
            self._total_messages += 1
            latency = time.time() - start_time
            self.router.record_message_sent(message, latency)
            self.energy_monitor.record_energy_usage(message.energy_cost)

            # Cache message for potential retransmission
            self.message_cache[message.message_id] = message

        return success

    def subscribe_to_events(self, event_type: str, handler: Callable):
        """Subscribe to specific event types"""
        self.event_bus.subscribe(event_type, handler)

    async def establish_p2p_connection(
        self, remote_node: str, connection_info: dict[str, Any]
    ) -> bool:
        """Establish P2P connection for efficient data transfer"""
        return await self.p2p_channel.establish_connection(remote_node, connection_info)

    def get_communication_stats(self) -> dict[str, Any]:
        """Get comprehensive communication statistics"""
        return {
            "node_id": self.node_id,
            "total_messages": self._total_messages,
            "event_bus_stats": self.event_bus.stats,
            "p2p_stats": self.p2p_channel.get_connection_stats(),
            "energy_stats": self.energy_monitor.get_stats(),
            "router_energy_used": self.router.energy_used,
            "router_energy_budget": self.router.energy_budget,
            "cached_messages": len(self.message_cache),
        }

    async def send_large_data(
        self, recipient: str, data: bytes, chunk_size: int = 1024 * 1024
    ) -> bool:
        """Send large data in chunks to prevent memory issues"""
        if len(data) <= chunk_size:
            # Small data, send normally
            return await self.send_message(recipient, "data_transfer", {"data": data})

        # Split into chunks
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
        chunk_id = str(uuid.uuid4())

        # Send metadata first
        metadata = {
            "type": "large_data_start",
            "chunk_id": chunk_id,
            "total_chunks": len(chunks),
            "total_size": len(data),
        }

        if not await self.send_message(
            recipient, "large_data_meta", metadata, MessagePriority.HIGH
        ):
            return False

        # Send chunks
        for i, chunk in enumerate(chunks):
            chunk_msg = {
                "type": "large_data_chunk",
                "chunk_id": chunk_id,
                "chunk_index": i,
                "data": chunk,
            }

            if not await self.send_message(
                recipient, "large_data_chunk", chunk_msg, MessagePriority.HIGH
            ):
                return False

        # Send completion message
        completion = {"type": "large_data_complete", "chunk_id": chunk_id}
        return await self.send_message(
            recipient, "large_data_complete", completion, MessagePriority.HIGH
        )


class EnergyMonitor:
    """Monitor and optimize energy consumption"""

    def __init__(self):
        self.total_energy_used = 0.0
        self.energy_history: list[dict[str, Any]] = []
        self.efficiency_targets = {
            "max_energy_per_message": 1.0,
            "max_hourly_consumption": 100.0,
        }

    def record_energy_usage(self, energy_cost: float):
        """Record energy usage for monitoring"""
        self.total_energy_used += energy_cost
        self.energy_history.append(
            {
                "timestamp": time.time(),
                "energy_cost": energy_cost,
                "cumulative": self.total_energy_used,
            }
        )

        # Keep only recent history (last 1000 entries)
        if len(self.energy_history) > 1000:
            self.energy_history.pop(0)

    def get_stats(self) -> dict[str, Any]:
        """Get energy consumption statistics"""
        if not self.energy_history:
            return {"total_energy": 0.0, "average_per_message": 0.0}

        recent_hour = time.time() - 3600
        recent_usage = [
            entry["energy_cost"]
            for entry in self.energy_history
            if entry["timestamp"] > recent_hour
        ]

        return {
            "total_energy": self.total_energy_used,
            "average_per_message": (
                sum(e["energy_cost"] for e in self.energy_history)
                / len(self.energy_history)
            ),
            "hourly_usage": sum(recent_usage),
            "efficiency_score": self._calculate_efficiency_score(),
            "message_count": len(self.energy_history),
        }

    def _calculate_efficiency_score(self) -> float:
        """Calculate efficiency score (0-100)"""
        if not self.energy_history:
            return 100.0

        avg_per_message = sum(e["energy_cost"] for e in self.energy_history) / len(
            self.energy_history
        )

        target = self.efficiency_targets["max_energy_per_message"]
        efficiency = max(0, (target - avg_per_message) / target * 100)

        return min(100.0, efficiency)


# Global instance management
_global_communication_fabric = None


def get_global_communication_fabric() -> EfficientCommunicationFabric:
    """Get or create the global communication fabric instance."""
    global _global_communication_fabric
    if _global_communication_fabric is None:
        _global_communication_fabric = EfficientCommunicationFabric("global-fabric")
    return _global_communication_fabric


# Export public interface
__all__ = [
    "EfficientCommunicationFabric",
    "MessagePriority",
    "CommunicationMode",
    "Message",
    "MessageRouter",
    "EventBus",
    "P2PChannel",
    "EnergyMonitor",
    "get_global_communication_fabric",
]
