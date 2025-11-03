from __future__ import annotations

#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🌐 LUKHAS DASHBOARD WEBSOCKET SERVER
║ Real-time data streaming server with Oracle and Ethics intelligence integration
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: websocket_server.py
║ Path: dashboard/api/websocket_server.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ High-performance WebSocket server providing real-time data streams for the
║ Universal Adaptive Dashboard system:
║
║ 🧠 INTELLIGENT DATA STREAMING:
║ • Oracle Nervous System metrics and predictions in real-time
║ • Ethics Swarm Colony decision tracking and drift monitoring
║ • Cross-colony coordination events and health status
║ • Adaptive threshold updates and system morphing events
║
║ 🔄 SELF-HEALING INTEGRATION:
║ • Component health monitoring and healing event streams
║ • Fallback system activations and recovery notifications
║ • Performance metrics and optimization recommendations
║ • Predictive healing alerts and proactive interventions
║
║ ⚖️ ETHICS-AWARE STREAMING:
║ • Ethical decision complexity monitoring
║ • Stakeholder impact assessments in real-time
║ • Decision audit trail updates
║ • Swarm consensus tracking and drift correction events
║
║ 🏛️ COLONY-COORDINATED STREAMING:
║ • Multi-colony data aggregation and fusion
║ • Distributed system status coordination
║ • Cross-colony event propagation
║ • Swarm intelligence insights broadcasting
║
║ ΛTAG: ΛWEBSOCKET, ΛSTREAMING, ΛREALTIME, ΛDASHBOARD, ΛINTELLIGENCE
╚══════════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import builtins
import contextlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable

import uvicorn
from core.colonies.ethics_swarm_colony import get_ethics_swarm_colony

# LUKHAS system imports
from core.oracle_nervous_system import get_oracle_nervous_system
from dashboard.core.dashboard_colony_agent import create_dashboard_colony_swarm
from dashboard.core.dynamic_tab_system import DynamicTabSystem
from dashboard.core.morphing_engine import MorphingEngine
from dashboard.core.self_healing_manager import SelfHealingManager

# Dashboard system imports
from dashboard.core.universal_adaptive_dashboard import UniversalAdaptiveDashboard
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("ΛTRACE.websocket_server")


class StreamType(Enum):
    """Types of data streams available."""

    ORACLE_METRICS = "oracle_metrics"
    ETHICS_SWARM = "ethics_swarm"
    SYSTEM_HEALTH = "system_health"
    MORPHING_EVENTS = "morphing_events"
    HEALING_EVENTS = "healing_events"
    COLONY_COORDINATION = "colony_coordination"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_INTERACTIONS = "user_interactions"
    PREDICTIONS = "predictions"
    ALL_STREAMS = "all_streams"


@dataclass
class StreamClient:
    """Represents a connected WebSocket client."""

    client_id: str
    websocket: WebSocket
    subscribed_streams: set[StreamType]
    connected_at: datetime
    last_activity: datetime
    user_id: str | None = None
    permissions: set[str] = field(default_factory=set)
    client_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamMessage:
    """Represents a message to be streamed to clients."""

    message_id: str
    stream_type: StreamType
    data: dict[str, Any]
    timestamp: datetime
    priority: int = 3  # 1=critical, 2=high, 3=normal, 4=low, 5=debug
    target_clients: set[str] | None = None


class DashboardWebSocketServer:
    """
    High-performance WebSocket server for real-time dashboard data streaming
    with Oracle and Ethics intelligence integration.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.server_id = f"dashboard_ws_{int(datetime.now(timezone.utc).timestamp())}"
        self.logger = logger.bind(server_id=self.server_id)

        # FastAPI application
        self.app = FastAPI(title="LUKHAS Dashboard WebSocket Server", version="1.0.0")
        self._setup_fastapi()

        # Connected clients
        self.clients: dict[str, StreamClient] = {}
        self.client_lock = asyncio.Lock()

        # Dashboard system components
        self.dashboard: UniversalAdaptiveDashboard | None = None
        self.colony_agents: list = []
        self.tab_system: DynamicTabSystem | None = None
        self.morphing_engine: MorphingEngine | None = None
        self.healing_manager: SelfHealingManager | None = None

        # LUKHAS system integration
        self.oracle_nervous_system = None
        self.ethics_swarm = None

        # Streaming coordination
        self.message_queue = asyncio.Queue()
        self.stream_handlers: dict[StreamType, Callable] = {}
        self.performance_metrics = {
            "messages_sent": 0,
            "clients_connected": 0,
            "average_latency": 0.0,
            "error_rate": 0.0,
        }

        # Background tasks
        self.background_tasks: list[asyncio.Task] = []

        self.logger.info("Dashboard WebSocket Server initialized", host=host, port=port)

    def _setup_fastapi(self):
        """Setup FastAPI application with CORS and routes."""

        # CORS middleware for cross-origin requests
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # WebSocket endpoint
        @self.app.websocket("/ws/{stream_type}")
        async def websocket_endpoint(websocket: WebSocket, stream_type: str):
            await self.handle_websocket_connection(websocket, stream_type)

        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "server_id": self.server_id,
                "connected_clients": len(self.clients),
                "uptime": ((datetime.now(timezone.utc) - self.start_time).total_seconds() if hasattr(self, "start_time") else 0),
            }

        # Metrics endpoint
        @self.app.get("/metrics")
        async def get_metrics():
            return {
                "performance_metrics": self.performance_metrics,
                "clients": len(self.clients),
                "stream_types": list(StreamType),
                "system_health": await self._get_system_health_summary(),
            }

    async def initialize(self):
        """Initialize the WebSocket server and dashboard components."""
        self.start_time = datetime.now(timezone.utc)
        self.logger.info("Initializing Dashboard WebSocket Server")

        try:
            # Initialize dashboard system components
            await self._initialize_dashboard_components()

            # Initialize LUKHAS system integration
            await self._initialize_lukhas_integration()

            # Setup stream handlers
            await self._setup_stream_handlers()

            # Start background tasks
            await self._start_background_tasks()

            self.logger.info("Dashboard WebSocket Server fully initialized")

        except Exception as e:
            self.logger.error("WebSocket server initialization failed", error=str(e))
            raise

    async def _initialize_dashboard_components(self):
        """Initialize dashboard system components."""

        # Initialize universal adaptive dashboard
        self.dashboard = UniversalAdaptiveDashboard()
        await self.dashboard.initialize()

        # Initialize colony agents
        self.colony_agents = await create_dashboard_colony_swarm()

        # Initialize tab system
        self.tab_system = DynamicTabSystem(self.dashboard.current_context)
        await self.tab_system.initialize()

        # Initialize morphing engine
        self.morphing_engine = MorphingEngine(self.tab_system)
        await self.morphing_engine.initialize()

        # Initialize self-healing manager
        self.healing_manager = SelfHealingManager()
        await self.healing_manager.initialize()

        self.logger.info("Dashboard components initialized")

    async def _initialize_lukhas_integration(self):
        """Initialize integration with LUKHAS AI systems."""

        try:
            # Oracle Nervous System integration
            self.oracle_nervous_system = await get_oracle_nervous_system()
            self.logger.info("Oracle Nervous System integrated")

            # Ethics Swarm Colony integration
            self.ethics_swarm = await get_ethics_swarm_colony()
            self.logger.info("Ethics Swarm Colony integrated")

        except Exception as e:
            self.logger.warning("Some LUKHAS systems unavailable", error=str(e))
            # Server continues with reduced functionality

    async def _setup_stream_handlers(self):
        """Setup handlers for different stream types."""

        self.stream_handlers = {
            StreamType.ORACLE_METRICS: self._handle_oracle_metrics_stream,
            StreamType.ETHICS_SWARM: self._handle_ethics_swarm_stream,
            StreamType.SYSTEM_HEALTH: self._handle_system_health_stream,
            StreamType.MORPHING_EVENTS: self._handle_morphing_events_stream,
            StreamType.HEALING_EVENTS: self._handle_healing_events_stream,
            StreamType.COLONY_COORDINATION: self._handle_colony_coordination_stream,
            StreamType.PERFORMANCE_METRICS: self._handle_performance_metrics_stream,
            StreamType.PREDICTIONS: self._handle_predictions_stream,
        }

        self.logger.info("Stream handlers configured", handlers=len(self.stream_handlers))

    async def _start_background_tasks(self):
        """Start background tasks for data streaming."""

        # Message broadcasting task
        self.background_tasks.append(asyncio.create_task(self._message_broadcaster()))

        # Data collection tasks for each stream type
        for stream_type in StreamType:
            if stream_type != StreamType.ALL_STREAMS:
                self.background_tasks.append(asyncio.create_task(self._data_collector(stream_type)))

        # Client cleanup task
        self.background_tasks.append(asyncio.create_task(self._client_cleanup_task()))

        # Performance monitoring task
        self.background_tasks.append(asyncio.create_task(self._performance_monitor()))

        self.logger.info("Background tasks started", tasks=len(self.background_tasks))

    async def handle_websocket_connection(self, websocket: WebSocket, stream_type: str):
        """Handle new WebSocket connections."""

        try:
            # Parse stream type
            try:
                requested_stream = StreamType(stream_type)
            except ValueError:
                await websocket.close(code=4000, reason=f"Invalid stream type: {stream_type}")
                return

            # Accept connection
            await websocket.accept()

            # Create client
            client_id = str(uuid.uuid4())
            client = StreamClient(
                client_id=client_id,
                websocket=websocket,
                subscribed_streams=(
                    {requested_stream} if requested_stream != StreamType.ALL_STREAMS else set(StreamType)
                ),
                connected_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc),
            )

            # Add to clients
            async with self.client_lock:
                self.clients[client_id] = client
                self.performance_metrics["clients_connected"] = len(self.clients)

            self.logger.info(
                "Client connected",
                client_id=client_id,
                stream_type=stream_type,
                total_clients=len(self.clients),
            )

            # Send welcome message
            await self._send_welcome_message(client)

            # Handle client messages
            try:
                while True:
                    message = await websocket.receive_text()
                    await self._handle_client_message(client, message)
                    client.last_activity = datetime.now(timezone.utc)

            except WebSocketDisconnect:
                self.logger.info("Client disconnected", client_id=client_id)
            except Exception as e:
                self.logger.error(
                    "Client communication error",
                    client_id=client_id,
                    error=str(e),
                )

        except Exception as e:
            self.logger.error("WebSocket connection error", error=str(e))

        finally:
            # Remove client
            async with self.client_lock:
                if client_id in self.clients:
                    del self.clients[client_id]
                    self.performance_metrics["clients_connected"] = len(self.clients)

    async def _send_welcome_message(self, client: StreamClient):
        """Send welcome message to newly connected client."""

        welcome_data = {
            "type": "welcome",
            "client_id": client.client_id,
            "server_id": self.server_id,
            "subscribed_streams": [stream.value for stream in client.subscribed_streams],
            "server_capabilities": [stream.value for stream in StreamType],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await client.websocket.send_text(json.dumps(welcome_data))

    async def _handle_client_message(self, client: StreamClient, message: str):
        """Handle messages from clients."""

        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            if message_type == "subscribe":
                # Handle stream subscription
                stream_types = data.get("streams", [])
                for stream_type_str in stream_types:
                    try:
                        stream_type = StreamType(stream_type_str)
                        client.subscribed_streams.add(stream_type)
                    except ValueError:
                        pass

                response = {
                    "type": "subscription_updated",
                    "subscribed_streams": [s.value for s in client.subscribed_streams],
                }
                await client.websocket.send_text(json.dumps(response))

            elif message_type == "unsubscribe":
                # Handle stream unsubscription
                stream_types = data.get("streams", [])
                for stream_type_str in stream_types:
                    try:
                        stream_type = StreamType(stream_type_str)
                        client.subscribed_streams.discard(stream_type)
                    except ValueError:
                        pass

                response = {
                    "type": "subscription_updated",
                    "subscribed_streams": [s.value for s in client.subscribed_streams],
                }
                await client.websocket.send_text(json.dumps(response))

            elif message_type == "dashboard_interaction":
                # Handle dashboard interaction events
                await self._handle_dashboard_interaction(client, data)

        except json.JSONDecodeError:
            self.logger.warning("Invalid JSON from client", client_id=client.client_id)
        except Exception as e:
            self.logger.error(
                "Client message handling error",
                client_id=client.client_id,
                error=str(e),
            )

    async def _handle_dashboard_interaction(self, client: StreamClient, data: dict[str, Any]):
        """Handle dashboard interaction events from clients."""

        interaction_type = data.get("interaction_type", "")
        interaction_data = data.get("data", {})

        if self.tab_system and interaction_type in [
            "tab_access",
            "dwell_time",
            "satisfaction_feedback",
        ]:
            tab_id = interaction_data.get("tab_id", "")
            if tab_id:
                await self.tab_system.handle_user_interaction(tab_id, interaction_type, interaction_data)

    async def broadcast_message(
        self,
        stream_type: StreamType,
        data: dict[str, Any],
        priority: int = 3,
        target_clients: set[str] | None = None,
    ):
        """Broadcast a message to subscribed clients."""

        message = StreamMessage(
            message_id=str(uuid.uuid4()),
            stream_type=stream_type,
            data=data,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            target_clients=target_clients,
        )

        await self.message_queue.put(message)

    # Background task methods

    async def _message_broadcaster(self):
        """Background task to broadcast messages to clients."""
        while True:
            try:
                # Get message from queue
                message = await self.message_queue.get()

                # Find target clients
                target_clients = []
                async with self.client_lock:
                    for client in self.clients.values():
                        # Check if client is subscribed to this stream type
                        if (
                            message.stream_type in client.subscribed_streams
                            or StreamType.ALL_STREAMS in client.subscribed_streams
                        ):
                            # Check if message is targeted to specific clients
                            if message.target_clients is None or client.client_id in message.target_clients:
                                target_clients.append(client)

                # Broadcast to target clients
                broadcast_data = {
                    "message_id": message.message_id,
                    "stream_type": message.stream_type.value,
                    "data": message.data,
                    "timestamp": message.timestamp.isoformat(),
                    "priority": message.priority,
                }

                broadcast_json = json.dumps(broadcast_data)

                for client in target_clients:
                    try:
                        await client.websocket.send_text(broadcast_json)
                        self.performance_metrics["messages_sent"] += 1
                    except Exception as e:
                        self.logger.error(
                            "Failed to send message to client",
                            client_id=client.client_id,
                            error=str(e),
                        )
                        # Client will be cleaned up by cleanup task

            except Exception as e:
                self.logger.error("Message broadcaster error", error=str(e))
                await asyncio.sleep(1)

    async def _data_collector(self, stream_type: StreamType):
        """Background task to collect data for specific stream type."""

        # Different collection frequencies for different stream types
        collection_intervals = {
            StreamType.ORACLE_METRICS: 2,
            StreamType.ETHICS_SWARM: 3,
            StreamType.SYSTEM_HEALTH: 5,
            StreamType.MORPHING_EVENTS: 1,
            StreamType.HEALING_EVENTS: 1,
            StreamType.COLONY_COORDINATION: 4,
            StreamType.PERFORMANCE_METRICS: 10,
            StreamType.PREDICTIONS: 15,
        }

        interval = collection_intervals.get(stream_type, 5)

        while True:
            try:
                # Get stream handler
                handler = self.stream_handlers.get(stream_type)
                if handler:
                    # Collect data
                    data = await handler()

                    # Broadcast if data available
                    if data:
                        await self.broadcast_message(stream_type, data)

                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(
                    f"Data collector error for {stream_type.value}",
                    error=str(e),
                )
                await asyncio.sleep(interval * 2)

    async def _client_cleanup_task(self):
        """Background task to clean up disconnected clients."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                cleanup_threshold = timedelta(minutes=5)

                clients_to_remove = []
                async with self.client_lock:
                    for client_id, client in self.clients.items():
                        # Check if client has been inactive too long
                        if current_time - client.last_activity > cleanup_threshold:
                            clients_to_remove.append(client_id)

                    # Remove inactive clients
                    for client_id in clients_to_remove:
                        del self.clients[client_id]
                        self.logger.info("Cleaned up inactive client", client_id=client_id)

                    if clients_to_remove:
                        self.performance_metrics["clients_connected"] = len(self.clients)

                await asyncio.sleep(60)  # Run cleanup every minute

            except Exception as e:
                self.logger.error("Client cleanup error", error=str(e))
                await asyncio.sleep(60)

    async def _performance_monitor(self):
        """Background task to monitor server performance."""
        while True:
            try:
                # Update performance metrics
                # This would include latency calculations, error rates, etc.

                # Log performance periodically
                self.logger.info(
                    "Server performance metrics",
                    clients=len(self.clients),
                    messages_sent=self.performance_metrics["messages_sent"],
                )

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                self.logger.error("Performance monitoring error", error=str(e))
                await asyncio.sleep(300)

    # Stream handler methods

    async def _handle_oracle_metrics_stream(self) -> dict[str, Any] | None:
        """Handle Oracle metrics stream."""
        if not self.oracle_nervous_system:
            return None

        try:
            status = await self.oracle_nervous_system.get_system_status()
            return {
                "oracle_status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            self.logger.error("Oracle metrics stream error", error=str(e))
            return None

    async def _handle_ethics_swarm_stream(self) -> dict[str, Any] | None:
        """Handle Ethics Swarm stream."""
        if not self.ethics_swarm:
            return None

        try:
            status = await self.ethics_swarm.get_system_status()
            return {
                "ethics_status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            self.logger.error("Ethics swarm stream error", error=str(e))
            return None

    async def _handle_system_health_stream(self) -> dict[str, Any] | None:
        """Handle system health stream."""
        if not self.healing_manager:
            return None

        try:
            health_status = await self.healing_manager.get_system_health_status()
            return {
                "system_health": health_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            self.logger.error("System health stream error", error=str(e))
            return None

    async def _handle_morphing_events_stream(self) -> dict[str, Any] | None:
        """Handle morphing events stream."""
        # This would be event-driven rather than polling
        return None

    async def _handle_healing_events_stream(self) -> dict[str, Any] | None:
        """Handle healing events stream."""
        # This would be event-driven rather than polling
        return None

    async def _handle_colony_coordination_stream(
        self,
    ) -> dict[str, Any] | None:
        """Handle colony coordination stream."""
        if not self.colony_agents:
            return None

        try:
            coordination_data = {
                "active_agents": len(self.colony_agents),
                "agent_status": [
                    {
                        "agent_id": agent.colony_id,
                        "role": agent.agent_role.value,
                        "is_running": agent.is_running,
                    }
                    for agent in self.colony_agents
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            return coordination_data
        except Exception as e:
            self.logger.error("Colony coordination stream error", error=str(e))
            return None

    async def _handle_performance_metrics_stream(
        self,
    ) -> dict[str, Any] | None:
        """Handle performance metrics stream."""
        return {
            "server_metrics": self.performance_metrics.copy(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _handle_predictions_stream(self) -> dict[str, Any] | None:
        """Handle predictions stream."""
        if not (self.tab_system and self.morphing_engine):
            return None

        try:
            tab_predictions = await self.tab_system.predict_tab_needs()
            morph_predictions = await self.morphing_engine.predict_morph_needs()

            return {
                "tab_predictions": tab_predictions,
                "morph_predictions": morph_predictions,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            self.logger.error("Predictions stream error", error=str(e))
            return None

    async def _get_system_health_summary(self) -> dict[str, Any]:
        """Get system health summary for metrics endpoint."""
        summary = {
            "dashboard": "operational" if self.dashboard else "unavailable",
            "oracle_integration": ("operational" if self.oracle_nervous_system else "unavailable"),
            "ethics_integration": ("operational" if self.ethics_swarm else "unavailable"),
            "colony_agents": len(self.colony_agents),
            "active_streams": len(self.stream_handlers),
        }
        return summary

    async def start_server(self):
        """Start the WebSocket server."""
        self.logger.info(
            "Starting Dashboard WebSocket Server",
            host=self.host,
            port=self.port,
        )

        # Initialize server
        await self.initialize()

        # Start FastAPI server
        config = uvicorn.Config(app=self.app, host=self.host, port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def stop_server(self):
        """Stop the WebSocket server."""
        self.logger.info("Stopping Dashboard WebSocket Server")

        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Close all client connections
        async with self.client_lock:
            for client in self.clients.values():
                with contextlib.suppress(builtins.BaseException):
                    await client.websocket.close()
            self.clients.clear()

        self.logger.info("Dashboard WebSocket Server stopped")


# Convenience function to create and start server


async def create_dashboard_websocket_server(host: str = "localhost", port: int = 8765) -> DashboardWebSocketServer:
    """Create and initialize a dashboard WebSocket server."""
    server = DashboardWebSocketServer(host, port)
    await server.initialize()
    return server


logger.info("ΛWEBSOCKET: Dashboard WebSocket Server loaded. Real-time streaming ready.")
