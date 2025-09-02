"""
New Paradigm for Observability and Steering
Addresses TODO 167: Complex Adaptive System Monitoring

This module implements advanced observability and steering capabilities for the
Symbiotic Swarm, treating it as a living system rather than static code.
"""

import asyncio
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ObservabilityLevel(Enum):
    """Different levels of system observability"""

    BASIC = "basic"  # Basic metrics only
    DETAILED = "detailed"  # Detailed metrics and traces
    FULL = "full"  # Complete system state capture
    INTERACTIVE = "interactive"  # Allow system steering


class SystemHealth(Enum):
    """Overall system health states"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ActorSnapshot:
    """Point-in-time snapshot of an actor's state"""

    actor_id: str
    timestamp: float
    state: str
    mailbox_size: int
    message_rate: float
    error_rate: float
    memory_usage: int
    custom_metrics: dict[str, Any]
    relationships: list[str]  # Connected actors


@dataclass
class MessageFlow:
    """Represents message flow between actors"""

    source: str
    destination: str
    message_type: str
    timestamp: float
    correlation_id: str
    latency: Optional[float] = None
    payload_size: int = 0


@dataclass
class EmergentPattern:
    """Detected emergent behavior pattern"""

    pattern_id: str
    pattern_type: str
    involved_actors: list[str]
    confidence: float
    description: str
    first_detected: float
    last_observed: float
    occurrence_count: int


class ObservabilityCollector:
    """Collects and aggregates observability data from all actors"""

    def __init__(
        self,
        retention_period: float = 3600.0,  # 1 hour
        aggregation_interval: float = 5.0,
    ):
        self.retention_period = retention_period
        self.aggregation_interval = aggregation_interval

        # Time-series data storage
        self.actor_snapshots: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.message_flows: deque = deque(maxlen=10000)
        self.system_events: deque = deque(maxlen=5000)

        # Real-time metrics
        self.current_metrics: dict[str, dict[str, Any]] = {}
        self.message_rates: dict[tuple[str, str], deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

        # Pattern detection
        self.detected_patterns: dict[str, EmergentPattern] = {}
        self.pattern_detectors: list[Callable] = []

        # Aggregation thread
        self._running = False
        self._aggregation_thread = None
        self._lock = threading.Lock()

    def start(self):
        """Start the collector"""
        self._running = True
        self._aggregation_thread = threading.Thread(
            target=self._aggregation_loop, daemon=True
        )
        self._aggregation_thread.start()
        logger.info("Observability collector started")

    def stop(self):
        """Stop the collector"""
        self._running = False
        if self._aggregation_thread:
            self._aggregation_thread.join(timeout=5.0)
        logger.info("Observability collector stopped")

    def record_actor_snapshot(self, snapshot: ActorSnapshot):
        """Record an actor state snapshot"""
        with self._lock:
            self.actor_snapshots[snapshot.actor_id].append(snapshot)
            self.current_metrics[snapshot.actor_id] = {
                "state": snapshot.state,
                "mailbox_size": snapshot.mailbox_size,
                "message_rate": snapshot.message_rate,
                "error_rate": snapshot.error_rate,
                "memory_usage": snapshot.memory_usage,
                "last_update": snapshot.timestamp,
            }

    def record_message_flow(self, flow: MessageFlow):
        """Record a message flow between actors"""
        with self._lock:
            self.message_flows.append(flow)

            # Update message rate tracking
            route = (flow.source, flow.destination)
            self.message_rates[route].append(flow.timestamp)

    def record_system_event(self, event_type: str, event_data: dict[str, Any]):
        """Record a system-wide event"""
        with self._lock:
            self.system_events.append(
                {
                    "timestamp": time.time(),
                    "event_type": event_type,
                    "data": event_data,
                }
            )

    def register_pattern_detector(self, detector: Callable):
        """Register a custom pattern detector"""
        self.pattern_detectors.append(detector)

    def _aggregation_loop(self):
        """Background aggregation and pattern detection"""
        while self._running:
            try:
                self._clean_old_data()
                self._detect_patterns()
                self._calculate_system_health()

                time.sleep(self.aggregation_interval)
            except Exception as e:
                logger.error(f"Aggregation error: {e}")

    def _clean_old_data(self):
        """Remove data older than retention period"""
        current_time = time.time()
        cutoff_time = current_time - self.retention_period

        with self._lock:
            # Clean message flows
            while self.message_flows and self.message_flows[0].timestamp < cutoff_time:
                self.message_flows.popleft()

            # Clean system events
            while (
                self.system_events and self.system_events[0]["timestamp"] < cutoff_time
            ):
                self.system_events.popleft()

    def _detect_patterns(self):
        """Run pattern detection algorithms"""
        with self._lock:
            # Detect communication hotspots
            self._detect_hotspots()

            # Detect cascading failures
            self._detect_cascades()

            # Run custom detectors
            for detector in self.pattern_detectors:
                try:
                    patterns = detector(self)
                    for pattern in patterns:
                        self.detected_patterns[pattern.pattern_id] = pattern
                except Exception as e:
                    logger.error(f"Pattern detector error: {e}")

    def _detect_hotspots(self):
        """Detect communication hotspots"""
        current_time = time.time()
        window = 60.0  # 1 minute window

        # Count messages per route
        route_counts = defaultdict(int)
        for flow in self.message_flows:
            if current_time - flow.timestamp <= window:
                route = (flow.source, flow.destination)
                route_counts[route] += 1

        # Find hotspots (routes with high traffic)
        avg_count = np.mean(list(route_counts.values())) if route_counts else 0
        std_count = np.std(list(route_counts.values())) if route_counts else 0

        for route, count in route_counts.items():
            if count > avg_count + 2 * std_count:  # 2 sigma threshold
                pattern = EmergentPattern(
                    pattern_id=f"hotspot_{route[0]}_{route[1]}",
                    pattern_type="communication_hotspot",
                    involved_actors=list(route),
                    confidence=min(1.0, (count - avg_count) / (3 * std_count)),
                    description=f"High message traffic: {count} msgs/min",
                    first_detected=current_time,
                    last_observed=current_time,
                    occurrence_count=count,
                )

                if pattern.pattern_id in self.detected_patterns:
                    # Update existing pattern
                    existing = self.detected_patterns[pattern.pattern_id]
                    existing.last_observed = current_time
                    existing.occurrence_count = count
                else:
                    self.detected_patterns[pattern.pattern_id] = pattern

    def _detect_cascades(self):
        """Detect cascading failure patterns"""
        current_time = time.time()
        window = 30.0  # 30 second window

        # Look for rapid succession of error events
        error_timeline = []
        for event in self.system_events:
            if (
                event["event_type"] == "actor_failure"
                and current_time - event["timestamp"] <= window
            ):
                error_timeline.append(event)

        if len(error_timeline) > 3:  # Multiple failures
            actors_involved = [e["data"].get("actor_id") for e in error_timeline]

            pattern = EmergentPattern(
                pattern_id=f"cascade_{int(current_time)}",
                pattern_type="cascading_failure",
                involved_actors=actors_involved,
                confidence=min(1.0, len(error_timeline) / 10.0),
                description=f"Potential cascade: {len(error_timeline)} failures",
                first_detected=error_timeline[0]["timestamp"],
                last_observed=current_time,
                occurrence_count=len(error_timeline),
            )

            self.detected_patterns[pattern.pattern_id] = pattern

    def _calculate_system_health(self):
        """Calculate overall system health"""
        with self._lock:
            total_actors = len(self.current_metrics)
            if total_actors == 0:
                return SystemHealth.UNKNOWN

            # Count healthy actors
            healthy_count = sum(
                1
                for metrics in self.current_metrics.values()
                if metrics.get("error_rate", 0) < 0.1
            )

            health_ratio = healthy_count / total_actors

            if health_ratio >= 0.9:
                self._system_health = SystemHealth.HEALTHY
            elif health_ratio >= 0.7:
                self._system_health = SystemHealth.DEGRADED
            else:
                self._system_health = SystemHealth.CRITICAL

    def get_system_overview(self) -> dict[str, Any]:
        """Get comprehensive system overview"""
        with self._lock:
            return {
                "timestamp": time.time(),
                "health": getattr(self, "_system_health", SystemHealth.UNKNOWN).value,
                "actor_count": len(self.current_metrics),
                "message_flow_rate": len(self.message_flows) / 60.0,  # per minute
                "active_patterns": len(self.detected_patterns),
                "top_patterns": list(self.detected_patterns.values())[:5],
            }


class SteeringController:
    """Allows interactive steering of the actor system"""

    def __init__(self, actor_system: ActorSystem):
        self.actor_system = actor_system
        self.steering_policies: dict[str, Callable] = {}
        self.intervention_log: deque = deque(maxlen=1000)

    async def pause_actor(self, actor_id: str) -> bool:
        """Pause an actor's message processing"""
        actor = self.actor_system.get_actor(actor_id)
        if actor:
            actor._running = False
            self._log_intervention("pause_actor", {"actor_id": actor_id})
            return True
        return False

    async def resume_actor(self, actor_id: str) -> bool:
        """Resume an actor's message processing"""
        actor = self.actor_system.get_actor(actor_id)
        if actor:
            actor._running = True
            asyncio.create_task(actor._message_loop())
            self._log_intervention("resume_actor", {"actor_id": actor_id})
            return True
        return False

    async def inject_message(
        self,
        source: str,
        destination: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> bool:
        """Inject a message into the system"""
        dest_ref = self.actor_system.get_actor_ref(destination)
        if dest_ref:
            await dest_ref.tell(message_type, payload)
            self._log_intervention(
                "inject_message",
                {
                    "source": source,
                    "destination": destination,
                    "message_type": message_type,
                },
            )
            return True
        return False

    async def modify_actor_state(
        self, actor_id: str, state_updates: dict[str, Any]
    ) -> bool:
        """Modify an actor's internal state"""
        actor = self.actor_system.get_actor(actor_id)
        if actor:
            for key, value in state_updates.items():
                if hasattr(actor, key):
                    setattr(actor, key, value)

            self._log_intervention(
                "modify_state",
                {"actor_id": actor_id, "updates": list(state_updates.keys())},
            )
            return True
        return False

    async def apply_steering_policy(self, policy_name: str, *args, **kwargs):
        """Apply a pre-defined steering policy"""
        if policy_name in self.steering_policies:
            policy = self.steering_policies[policy_name]
            result = await policy(self, *args, **kwargs)

            self._log_intervention(
                "apply_policy", {"policy": policy_name, "result": result}
            )
            return result

        raise ValueError(f"Unknown steering policy: {policy_name}")

    def register_steering_policy(self, name: str, policy: Callable):
        """Register a custom steering policy"""
        self.steering_policies[name] = policy

    def _log_intervention(self, intervention_type: str, details: dict[str, Any]):
        """Log a steering intervention"""
        self.intervention_log.append(
            {
                "timestamp": time.time(),
                "type": intervention_type,
                "details": details,
            }
        )


class ObservableActor(Actor):
    """Enhanced actor with built-in observability"""

    def __init__(
        self, actor_id: str, collector: Optional[ObservabilityCollector] = None
    ):
        super().__init__(actor_id)
        self.collector = collector
        self._last_snapshot_time = 0.0
        self._snapshot_interval = 5.0  # seconds

        # Message timing for latency tracking
        self._message_start_times: dict[str, float] = {}

    async def _process_message(self, message: ActorMessage):
        """Process message with observability"""
        start_time = time.time()
        self._message_start_times[message.message_id] = start_time

        try:
            # Process normally
            await super()._process_message(message)

            # Record successful flow
            if self.collector:
                latency = time.time() - start_time
                flow = MessageFlow(
                    source=message.sender,
                    destination=self.actor_id,
                    message_type=message.message_type,
                    timestamp=start_time,
                    correlation_id=message.correlation_id or message.message_id,
                    latency=latency,
                    payload_size=len(json.dumps(message.payload)),
                )
                self.collector.record_message_flow(flow)

        except Exception as e:
            # Record failure
            if self.collector:
                self.collector.record_system_event(
                    "actor_failure",
                    {
                        "actor_id": self.actor_id,
                        "error": str(e),
                        "message_type": message.message_type,
                    },
                )
            raise
        finally:
            # Clean up timing
            self._message_start_times.pop(message.message_id, None)

    async def _message_loop(self):
        """Enhanced message loop with periodic snapshots"""
        while self._running:
            try:
                # Take periodic snapshots
                current_time = time.time()
                if current_time - self._last_snapshot_time > self._snapshot_interval:
                    await self._take_snapshot()
                    self._last_snapshot_time = current_time

                # Process messages normally
                try:
                    message = await asyncio.wait_for(self.mailbox.get(), timeout=1.0)
                    await self._process_message(message)
                    self._stats["messages_processed"] += 1
                    self._stats["last_activity"] = time.time()

                except asyncio.TimeoutError:
                    continue

            except Exception as e:
                self._stats["messages_failed"] += 1
                logger.error(f"Actor {self.actor_id} message processing error: {e}")

                if self.supervisor:
                    await self.supervisor.tell(
                        "child_failed",
                        {"child_id": self.actor_id, "error": str(e)},
                    )

    async def _take_snapshot(self):
        """Take a snapshot of actor state"""
        if not self.collector:
            return

        # Calculate rates
        current_time = time.time()

        message_rate = self._stats["messages_processed"] / max(
            1.0, current_time - self._stats["created_at"]
        )

        error_rate = self._stats["messages_failed"] / max(
            1, self._stats["messages_processed"]
        )

        # Get memory usage (simplified)
        import sys

        memory_usage = sys.getsizeof(self.__dict__)

        # Create snapshot
        snapshot = ActorSnapshot(
            actor_id=self.actor_id,
            timestamp=current_time,
            state=self.state.value,
            mailbox_size=self.mailbox.qsize(),
            message_rate=message_rate,
            error_rate=error_rate,
            memory_usage=memory_usage,
            custom_metrics=self.get_custom_metrics(),
            relationships=list(self.children.keys()),
        )

        self.collector.record_actor_snapshot(snapshot)

    def get_custom_metrics(self) -> dict[str, Any]:
        """Override to provide custom metrics"""
        return {}


class ObservabilityDashboard:
    """Interactive dashboard for system observation and steering"""

    def __init__(self, collector: ObservabilityCollector, steering: SteeringController):
        self.collector = collector
        self.steering = steering
        self.visualizations: dict[str, Callable] = {}

    def register_visualization(self, name: str, viz_func: Callable):
        """Register a custom visualization"""
        self.visualizations[name] = viz_func

    async def get_actor_graph(self) -> dict[str, Any]:
        """Get actor relationship graph data"""
        nodes = []
        edges = []

        # Create nodes from current actors
        for actor_id, metrics in self.collector.current_metrics.items():
            nodes.append(
                {
                    "id": actor_id,
                    "state": metrics.get("state", "unknown"),
                    "health": (
                        "healthy" if metrics.get("error_rate", 0) < 0.1 else "unhealthy"
                    ),
                    "mailbox_size": metrics.get("mailbox_size", 0),
                }
            )

        # Create edges from message flows
        edge_weights = defaultdict(int)
        for flow in self.collector.message_flows:
            if time.time() - flow.timestamp < 60:  # Last minute
                edge_key = (flow.source, flow.destination)
                edge_weights[edge_key] += 1

        for (source, dest), weight in edge_weights.items():
            edges.append({"source": source, "target": dest, "weight": weight})

        return {"nodes": nodes, "edges": edges}

    async def get_time_series_data(
        self, actor_id: str, metric: str, duration: float = 300.0
    ) -> list[tuple[float, float]]:
        """Get time series data for a specific metric"""
        data = []
        current_time = time.time()

        for snapshot in self.collector.actor_snapshots.get(actor_id, []):
            if current_time - snapshot.timestamp <= duration:
                value = getattr(snapshot, metric, None)
                if value is not None:
                    data.append((snapshot.timestamp, value))

        return data

    def get_pattern_summary(self) -> dict[str, Any]:
        """Get summary of detected patterns"""
        patterns_by_type = defaultdict(list)

        for pattern in self.collector.detected_patterns.values():
            patterns_by_type[pattern.pattern_type].append(
                {
                    "id": pattern.pattern_id,
                    "actors": pattern.involved_actors,
                    "confidence": pattern.confidence,
                    "description": pattern.description,
                }
            )

        return dict(patterns_by_type)


# Example usage and demo


async def demo_observability():
    """Demonstrate observability and steering capabilities"""
    from .actor_system import AIAgentActor, get_global_actor_system

    # Setup
    system = await get_global_actor_system()
    collector = ObservabilityCollector()
    collector.start()

    steering = SteeringController(system)
    dashboard = ObservabilityDashboard(collector, steering)

    # Create observable actors

    class ObservableAgent(ObservableActor, AIAgentActor):
        def __init__(self, actor_id: str, capabilities: Optional[list[str]] = None):
            AIAgentActor.__init__(self, actor_id, capabilities)
            ObservableActor.__init__(self, actor_id, collector)

        def get_custom_metrics(self) -> dict[str, Any]:
            return {
                "energy_level": getattr(self, "energy_level", 0),
                "active_tasks": len(getattr(self, "current_tasks", {})),
            }

    # Create agents
    agent1 = await system.create_actor(
        ObservableAgent,
        "analytics-agent-001",
        capabilities=["analysis", "reporting"],
    )

    await system.create_actor(
        ObservableAgent,
        "processing-agent-001",
        capabilities=["data_processing", "transformation"],
    )

    # Simulate some activity
    for i in range(5):
        await agent1.tell(
            "assign_task", {"task_id": f"task_{i}", "task_type": "analysis"}
        )
        await asyncio.sleep(0.1)

    # Wait for data collection
    await asyncio.sleep(10)

    # Get system overview
    overview = collector.get_system_overview()
    print("System Overview:", json.dumps(overview, indent=2))

    # Get actor graph
    graph = await dashboard.get_actor_graph()
    print("Actor Graph:", json.dumps(graph, indent=2))

    # Demonstrate steering
    await steering.pause_actor("analytics-agent-001")
    print("Paused analytics agent")

    await asyncio.sleep(2)

    await steering.resume_actor("analytics-agent-001")
    print("Resumed analytics agent")

    # Cleanup
    collector.stop()


if __name__ == "__main__":
    asyncio.run(demo_observability())
