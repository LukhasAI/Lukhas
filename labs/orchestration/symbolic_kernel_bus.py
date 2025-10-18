"""
LUKHΛS Symbolic Kernel Bus
==========================

Production-ready event coordination system for swarm actions, plugin triggers,
and memory signals. Implements symbolic routing with automatic handler connections.

Constellation Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, Callable, Optional

# Import LUKHAS AI branding system for orchestration compliance
try:
    from branding_bridge import (
        BrandContext,
        get_brand_voice,
        get_constellation_context,
        normalize_output_text,
        validate_output,
    )

    BRANDING_AVAILABLE = True
except ImportError:
    BRANDING_AVAILABLE = False

logger = logging.getLogger(__name__)


class SymbolicEffect(Enum):
    """
    Symbolic effects that events can trigger in the system.
    Each effect maps to specific kernel subsystems.
    """

    # Memory Effects
    MEMORY_FOLD = "memory_fold"  # → Triggers memory fold creation
    MEMORY_CASCADE = "memory_cascade"  # → Cascades through memory chains
    MEMORY_PERSIST = "memory_persist"  # → Persists to long-term storage

    # Consciousness Effects
    AWARENESS_UPDATE = "awareness_update"  # → Updates consciousness state
    DREAM_TRIGGER = "dream_trigger"  # → Initiates dream sequence
    REFLECTION_INIT = "reflection_init"  # → Triggers self-reflection

    # Guardian Effects
    ETHICS_CHECK = "ethics_check"  # → Validates ethical compliance
    DRIFT_DETECT = "drift_detect"  # → Monitors behavioral drift
    SAFETY_GATE = "safety_gate"  # → Safety validation checkpoint

    # Swarm Effects
    AGENT_SPAWN = "agent_spawn"  # → Creates new agent instance
    AGENT_SYNC = "agent_sync"  # → Synchronizes agent states
    SWARM_CONSENSUS = "swarm_consensus"  # → Triggers consensus protocol

    # Plugin Effects
    PLUGIN_LOAD = "plugin_load"  # → Loads plugin module
    PLUGIN_UPDATE = "plugin_update"  # → Updates plugin state
    PLUGIN_UNLOAD = "plugin_unload"  # → Unloads plugin module

    # System Effects
    LOG_TRACE = "log_trace"  # → System logging and tracing
    METRIC_UPDATE = "metric_update"  # → Updates performance metrics
    STATE_CHECKPOINT = "state_checkpoint"  # → Creates state checkpoint


class EventPriority(Enum):
    """Event priority levels for queue management"""

    CRITICAL = 5  # System-critical events (safety, ethics)
    HIGH = 4  # Important operations (memory, consciousness)
    NORMAL = 3  # Standard operations
    LOW = 2  # Background tasks
    TRACE = 1  # Logging and metrics


@dataclass
class SymbolicEvent:
    """
    Core event structure with symbolic metadata.
    All events in the kernel bus use this format.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    target: Optional[str] = None  # Specific target module/agent
    timestamp: float = field(default_factory=time.time)

    # Symbolic metadata
    effects: list[SymbolicEffect] = field(default_factory=list)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None  # Links related events
    causality_chain: list[str] = field(default_factory=list)  # Event causality

    # Routing metadata
    ttl: int = 10  # Time-to-live (hop count)
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp,
            "effects": [e.value for e in self.effects],
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "causality_chain": self.causality_chain,
            "ttl": self.ttl,
            "retries": self.retries,
        }


class SymbolicKernelBus:
    """
    Central event coordination system for LUKHΛS.
    Manages all inter-module communication with symbolic routing.
    """

    def __init__(self, max_queue_size: int = 10000):
        """
        Initialize the symbolic kernel bus.

        Args:
            max_queue_size: Maximum number of events in queue
        """
        # Event routing
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._effect_handlers: dict[SymbolicEffect, list[Callable]] = defaultdict(list)
        # (pattern_fn, handler)
        self._pattern_subscribers: list[tuple[Callable, Callable]] = []

        # Event queues (priority-based)
        self._priority_queues: dict[EventPriority, asyncio.Queue] = {}
        for priority in EventPriority:
            self._priority_queues[priority] = asyncio.Queue(maxsize=max_queue_size)

        # Event tracking
        self._event_history: deque = deque(maxlen=1000)  # Recent events
        self._correlation_map: dict[str, list[SymbolicEvent]] = defaultdict(list)
        self._causality_graph: dict[str, set[str]] = defaultdict(set)

        # Performance metrics
        self._metrics = {
            "events_emitted": 0,
            "events_dispatched": 0,
            "events_failed": 0,
            "handlers_triggered": 0,
            "effects_processed": 0,
        }
        self._metrics_lock = Lock()

        # System state
        self._running = False
        self._workers: list[asyncio.Task] = []

        # Auto-connect symbolic handlers on init
        self._auto_connect_handlers()

        # Initialize branding context for orchestration
        if BRANDING_AVAILABLE:
            self._brand_context = BrandContext(
                voice_profile="identity",  # Orchestration uses identity profile
                triad_emphasis="balanced",  # All Constellation components
                compliance_level="standard",
                creative_mode=False,
                terminology_enforcement=True,
            )
            logger.info("🎨 Branding integrated with Symbolic Kernel Bus")
        else:
            self._brand_context = None
            logger.warning("⚠️ Branding not available for Kernel Bus")

        logger.info("🌀 Symbolic Kernel Bus initialized")

    def emit(
        self,
        event: str,
        payload: dict[str, Any],
        source: str = "unknown",
        effects: Optional[list[SymbolicEffect]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Emit an event to the kernel bus.

        Args:
            event: Event type/name
            payload: Event data payload
            source: Source module/component
            effects: Symbolic effects to trigger
            priority: Event priority level
            correlation_id: ID to correlate related events

        Returns:
            Event ID for tracking

        Example:
            bus.emit("memory.fold.created", {"fold_id": "123"},
                    effects=[SymbolicEffect.MEMORY_PERSIST])
        """
        # Create symbolic event
        symbolic_event = SymbolicEvent(
            event_type=event,
            payload=payload,
            source=source,
            effects=effects or [],
            priority=priority,
            correlation_id=correlation_id,
        )

        # Update metrics
        with self._metrics_lock:
            self._metrics["events_emitted"] += 1

        # Track event
        self._event_history.append(symbolic_event)
        if correlation_id:
            self._correlation_map[correlation_id].append(symbolic_event)

        # Queue for async processing
        try:
            queue = self._priority_queues[priority]
            queue.put_nowait(symbolic_event)
        except asyncio.QueueFull:
            logger.error(f"Queue full for priority {priority}, dropping event {event}")
            with self._metrics_lock:
                self._metrics["events_failed"] += 1

        logger.debug(f"📤 Emitted: {event} from {source} with effects {effects}")

        # Apply branding to event content if available
        if BRANDING_AVAILABLE and self._brand_context:
            self._apply_event_branding(symbolic_event)

        return symbolic_event.event_id

    def subscribe(self, event: str, callback: Callable):
        """
        Subscribe to an event type.

        Args:
            event: Event type to subscribe to (supports wildcards: "memory.*")
            callback: Function to call when event occurs

        Example:
            bus.subscribe("memory.fold.*", handle_memory_fold)
        """
        if "*" in event:
            # Pattern subscription
            import re

            pattern = event.replace(".", r"\.").replace("*", ".*")

            def pattern_fn(e):
                return re.match(pattern, e)

            self._pattern_subscribers.append((pattern_fn, callback))
            logger.info(f"📥 Pattern subscription: {event} → {callback.__name__}")
        else:
            # Exact subscription
            self._subscribers[event].append(callback)
            logger.info(f"📥 Subscribed: {event} → {callback.__name__}")

    def subscribe_effect(self, effect: SymbolicEffect, callback: Callable):
        """
        Subscribe to a symbolic effect.

        Args:
            effect: Symbolic effect to monitor
            callback: Handler for the effect

        Example:
            bus.subscribe_effect(SymbolicEffect.MEMORY_FOLD, handle_memory_effect)
        """
        self._effect_handlers[effect].append(callback)
        logger.info(f"🎯 Effect subscription: {effect.value} → {callback.__name__}")

    async def dispatch(self, event: SymbolicEvent):
        """
        Dispatch an event to all subscribers.

        Args:
            event: Event to dispatch

        Annotated symbolic effects:
            - MEMORY_FOLD → Triggers memory subsystem fold creation
            - DREAM_TRIGGER → Logs to dream journal, initiates dream cycle
            - DRIFT_DETECT → Alerts Guardian system, logs drift metrics
            - AGENT_SYNC → Synchronizes swarm agent states
            - PLUGIN_UPDATE → Refreshes plugin registry
        """
        try:
            # Update causality chain for downstream events
            if event.causality_chain:
                self._causality_graph[event.event_id].update(event.causality_chain)

            # Dispatch to exact subscribers
            handlers = self._subscribers.get(event.event_type, [])

            # Add pattern-matched handlers
            for pattern_fn, handler in self._pattern_subscribers:
                if pattern_fn(event.event_type):
                    handlers.append(handler)

            # Execute handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)

                    with self._metrics_lock:
                        self._metrics["handlers_triggered"] += 1

                except Exception as e:
                    logger.error(f"Handler error for {event.event_type}: {e}")
                    with self._metrics_lock:
                        self._metrics["events_failed"] += 1

                    # Retry logic for critical events
                    if event.priority == EventPriority.CRITICAL and event.retries < event.max_retries:
                        event.retries += 1
                        await self._requeue_event(event)

            # Process symbolic effects
            await self._process_effects(event)

            # Update metrics
            with self._metrics_lock:
                self._metrics["events_dispatched"] += 1

            logger.debug(f"📨 Dispatched: {event.event_type} to {len(handlers)} handlers")

        except Exception as e:
            logger.error(f"Dispatch error: {e}")
            with self._metrics_lock:
                self._metrics["events_failed"] += 1

    async def _process_effects(self, event: SymbolicEvent):
        """
        Process symbolic effects attached to an event.

        Each effect triggers specific kernel subsystem behaviors:

        Memory Effects:
            MEMORY_FOLD → Create new memory fold with event context
            MEMORY_CASCADE → Propagate through memory chain
            MEMORY_PERSIST → Save to persistent storage

        Consciousness Effects:
            AWARENESS_UPDATE → Update global consciousness state
            DREAM_TRIGGER → Initialize dream sequence with context
            REFLECTION_INIT → Start self-reflection cycle

        Guardian Effects:
            ETHICS_CHECK → Validate action against ethical rules
            DRIFT_DETECT → Check for behavioral drift
            SAFETY_GATE → Enforce safety boundaries

        Swarm Effects:
            AGENT_SPAWN → Create new agent with configuration
            AGENT_SYNC → Synchronize agent knowledge base
            SWARM_CONSENSUS → Initiate voting protocol

        Plugin Effects:
            PLUGIN_LOAD → Load and initialize plugin
            PLUGIN_UPDATE → Refresh plugin state
            PLUGIN_UNLOAD → Gracefully shutdown plugin

        System Effects:
            LOG_TRACE → Write to system trace log
            METRIC_UPDATE → Update performance metrics
            STATE_CHECKPOINT → Create recoverable checkpoint
        """
        for effect in event.effects:
            handlers = self._effect_handlers.get(effect, [])

            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)

                    with self._metrics_lock:
                        self._metrics["effects_processed"] += 1

                except Exception as e:
                    logger.error(f"Effect handler error for {effect.value}: {e}")

            # Log effect processing
            logger.debug(f"🎯 Processed effect: {effect.value} for {event.event_type}")

    def _auto_connect_handlers(self):
        """
        Auto-connect symbolic handlers for core system events.
        This establishes the default event routing for LUKHΛS.
        """
        # Memory fold events
        self.subscribe("memory.fold.init", self._handle_memory_fold_init)
        self.subscribe("memory.fold.close", self._handle_memory_fold_close)
        self.subscribe("memory.cascade.detected", self._handle_memory_cascade)

        # Agent drift detection
        self.subscribe("agent.drift.detected", self._handle_agent_drift)
        self.subscribe("swarm.consensus.required", self._handle_swarm_consensus)

        # Plugin system updates
        self.subscribe("plugin.loaded", self._handle_plugin_loaded)
        self.subscribe("plugin.error", self._handle_plugin_error)

        # Consciousness events
        self.subscribe("consciousness.state.changed", self._handle_consciousness_change)
        self.subscribe("dream.cycle.started", self._handle_dream_start)

        # Guardian events
        self.subscribe("ethics.violation.detected", self._handle_ethics_violation)
        self.subscribe("safety.boundary.approached", self._handle_safety_boundary)

        logger.info("🔗 Auto-connected core symbolic handlers")

    def _apply_event_branding(self, event: SymbolicEvent):
        """Apply LUKHAS AI branding to event content"""
        try:
            # Apply branding to text content in payload
            for key, value in event.payload.items():
                if isinstance(value, str) and len(value) > 10:  # Only brand substantial text
                    # Normalize terminology
                    branded_value = normalize_output_text(value, self._brand_context)

                    # Validate compliance
                    validation = validate_output(branded_value, self._brand_context)
                    if not validation["valid"]:
                        logger.debug(f"Event payload branding issue in {key}: {validation['issues']}")

                    event.payload[key] = branded_value

            # Add Constellation Framework context for consciousness and guardian events
            if any(
                effect
                in [
                    SymbolicEffect.AWARENESS_UPDATE,
                    SymbolicEffect.DREAM_TRIGGER,
                    SymbolicEffect.ETHICS_CHECK,
                    SymbolicEffect.SAFETY_GATE,
                ]
                for effect in event.effects
            ):
                constellation_context = get_constellation_context("balanced")
                event.payload["constellation_framework"] = constellation_context["framework"]

            # Add system signature for external events
            if event.source.startswith("external.") or "api" in event.source:
                event.payload["system_signature"] = get_brand_voice(
                    f"Event from {event.source}", self._brand_context
                ).replace(
                    f"Event from {event.source}",
                    f"LUKHAS AI ⚛️🧠🛡️ event from {event.source}",
                )

        except Exception as e:
            logger.warning(f"Event branding failed for {event.event_type}: {e}")

    # Core event handlers with symbolic annotations

    def _handle_memory_fold_init(self, event: SymbolicEvent):
        """
        FOLD_INIT → memory
        Creates new memory fold and establishes causal links.
        """
        fold_id = event.payload.get("fold_id")
        logger.info(f"💾 Memory fold initiated: {fold_id}")

        # Emit cascade event to propagate
        self.emit(
            "memory.fold.ready",
            {"fold_id": fold_id, "parent_event": event.event_id},
            source="kernel.memory",
            effects=[SymbolicEffect.MEMORY_CASCADE],
            correlation_id=event.correlation_id,
        )

    def _handle_memory_fold_close(self, event: SymbolicEvent):
        """
        FOLD_CLOSE → memory.persist
        Persists closed fold to long-term storage.
        """
        fold_id = event.payload.get("fold_id")
        logger.info(f"💾 Memory fold closing: {fold_id}")

        # Trigger persistence
        self.emit(
            "memory.persist.request",
            {"fold_id": fold_id, "timestamp": time.time()},
            source="kernel.memory",
            effects=[SymbolicEffect.MEMORY_PERSIST, SymbolicEffect.LOG_TRACE],
            priority=EventPriority.HIGH,
        )

    def _handle_memory_cascade(self, event: SymbolicEvent):
        """
        CASCADE_DETECT → memory.chain
        Handles memory cascade through causal chains.
        """
        cascade_depth = event.payload.get("depth", 0)
        if cascade_depth > 10:  # Prevent infinite cascades
            logger.warning(f"⚠️ Memory cascade depth limit: {cascade_depth}")
            return

        logger.info(f"🌊 Memory cascade at depth {cascade_depth}")

    def _handle_agent_drift(self, event: SymbolicEvent):
        """
        DRIFT_DETECT → guardian.alert
        Detects agent behavioral drift and alerts Guardian.
        """
        agent_id = event.payload.get("agent_id")
        drift_score = event.payload.get("drift_score", 0.0)

        logger.warning(f"📊 Agent drift detected: {agent_id} (score: {drift_score})")

        # Alert Guardian if drift exceeds threshold
        if drift_score > 0.5:
            self.emit(
                "guardian.intervention.required",
                {"agent_id": agent_id, "drift_score": drift_score, "action": "review"},
                source="kernel.drift_detector",
                effects=[SymbolicEffect.ETHICS_CHECK, SymbolicEffect.SAFETY_GATE],
                priority=EventPriority.HIGH,
            )

    def _handle_swarm_consensus(self, event: SymbolicEvent):
        """
        CONSENSUS_REQ → swarm.vote
        Initiates swarm consensus protocol.
        """
        topic = event.payload.get("topic")
        agents = event.payload.get("agents", [])

        logger.info(f"🐝 Swarm consensus requested: {topic} ({len(agents)} agents)")

        # Broadcast to all agents
        for agent_id in agents:
            self.emit(
                "agent.vote.request",
                {"topic": topic, "agent_id": agent_id},
                source="kernel.swarm",
                target=agent_id,
                effects=[SymbolicEffect.AGENT_SYNC],
                correlation_id=event.correlation_id,
            )

    def _handle_plugin_loaded(self, event: SymbolicEvent):
        """
        PLUGIN_LOAD → registry.update
        Updates plugin registry on load.
        """
        plugin_name = event.payload.get("name")
        logger.info(f"🔌 Plugin loaded: {plugin_name}")

        # Update registry
        self.emit(
            "registry.plugin.add",
            {"plugin": plugin_name, "timestamp": time.time()},
            source="kernel.plugins",
            effects=[SymbolicEffect.PLUGIN_UPDATE, SymbolicEffect.LOG_TRACE],
        )

    def _handle_plugin_error(self, event: SymbolicEvent):
        """
        PLUGIN_ERROR → safety.check
        Handles plugin errors with safety checks.
        """
        plugin_name = event.payload.get("name")
        error = event.payload.get("error")

        logger.error(f"❌ Plugin error: {plugin_name} - {error}")

        # Safety check
        self.emit(
            "safety.plugin.check",
            {"plugin": plugin_name, "error": str(error)},
            source="kernel.plugins",
            effects=[SymbolicEffect.SAFETY_GATE],
            priority=EventPriority.HIGH,
        )

    def _handle_consciousness_change(self, event: SymbolicEvent):
        """
        CONSCIOUSNESS_CHANGE → awareness.update
        Updates global consciousness state.
        """
        new_state = event.payload.get("state")
        logger.info(f"🧠 Consciousness state changed: {new_state}")

        # Propagate awareness
        self.emit(
            "awareness.global.update",
            {"state": new_state, "timestamp": time.time()},
            source="kernel.consciousness",
            effects=[SymbolicEffect.AWARENESS_UPDATE, SymbolicEffect.LOG_TRACE],
        )

    def _handle_dream_start(self, event: SymbolicEvent):
        """
        DREAM_START → log, memory.fold
        Initiates dream cycle with logging and memory integration.
        """
        dream_id = event.payload.get("dream_id")
        logger.info(f"💭 Dream cycle started: {dream_id}")

        # Create dream memory fold
        self.emit(
            "memory.fold.create",
            {"fold_type": "dream", "dream_id": dream_id},
            source="kernel.dreams",
            effects=[SymbolicEffect.MEMORY_FOLD, SymbolicEffect.DREAM_TRIGGER],
            correlation_id=dream_id,
        )

    def _handle_ethics_violation(self, event: SymbolicEvent):
        """
        ETHICS_VIOLATION → guardian.enforce
        Handles ethical violations with Guardian enforcement.
        """
        violation = event.payload.get("violation")
        severity = event.payload.get("severity", "low")

        logger.critical(f"⚠️ Ethics violation: {violation} (severity: {severity})")

        # Guardian enforcement
        self.emit(
            "guardian.enforce.action",
            {"violation": violation, "severity": severity, "action": "block"},
            source="kernel.ethics",
            effects=[SymbolicEffect.ETHICS_CHECK, SymbolicEffect.SAFETY_GATE],
            priority=EventPriority.CRITICAL,
        )

    def _handle_safety_boundary(self, event: SymbolicEvent):
        """
        SAFETY_BOUNDARY → safety.enforce
        Enforces safety boundaries when approached.
        """
        boundary = event.payload.get("boundary")
        distance = event.payload.get("distance", 1.0)

        logger.warning(f"🛡️ Safety boundary approached: {boundary} (distance: {distance})")

        if distance < 0.1:  # Critical proximity
            self.emit(
                "safety.emergency.stop",
                {"boundary": boundary, "reason": "critical_proximity"},
                source="kernel.safety",
                effects=[SymbolicEffect.SAFETY_GATE],
                priority=EventPriority.CRITICAL,
            )

    async def _requeue_event(self, event: SymbolicEvent):
        """Requeue an event for retry"""
        await asyncio.sleep(0.1 * (2**event.retries))  # Exponential backoff
        queue = self._priority_queues[event.priority]
        await queue.put(event)

    async def _worker(self, priority: EventPriority):
        """Worker coroutine for processing events of specific priority"""
        queue = self._priority_queues[priority]

        while self._running:
            try:
                # Get event with timeout to allow checking _running flag
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                await self.dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error for priority {priority}: {e}")

    async def start(self):
        """Start the kernel bus workers"""
        if self._running:
            return

        self._running = True

        # Start workers for each priority level
        for priority in EventPriority:
            worker = asyncio.create_task(self._worker(priority))
            self._workers.append(worker)

        logger.info("🚀 Symbolic Kernel Bus started")

    async def stop(self):
        """Stop the kernel bus workers"""
        self._running = False

        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()

        logger.info("🛑 Symbolic Kernel Bus stopped")

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""
        with self._metrics_lock:
            return self._metrics.copy()

    def get_event_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent event history"""
        return [e.to_dict() for e in list(self._event_history)[-limit:]]

    def get_correlation_chain(self, correlation_id: str) -> list[dict[str, Any]]:
        """Get all events in a correlation chain"""
        events = self._correlation_map.get(correlation_id, [])
        return [e.to_dict() for e in events]


# Global kernel bus instance
kernel_bus = SymbolicKernelBus()

# Convenience functions for backward compatibility


def emit(event: str, payload: dict[str, Any], **kwargs) -> str:
    """Emit an event to the kernel bus"""
    return kernel_bus.emit(event, payload, **kwargs)


def subscribe(event: str, callback: Callable):
    """Subscribe to an event"""
    kernel_bus.subscribe(event, callback)


async def dispatch(event: SymbolicEvent):
    """Dispatch an event"""
    await kernel_bus.dispatch(event)


# Export key components
__all__ = [
    "EventPriority",
    "SymbolicEffect",
    "SymbolicEvent",
    "SymbolicKernelBus",
    "dispatch",
    "emit",
    "kernel_bus",
    "subscribe",
]
