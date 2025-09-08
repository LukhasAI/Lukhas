import logging
from datetime import timezone
from typing import Dict, List

import streamlit as st

logger = logging.getLogger(__name__)
"""
LUKHAS AI Debug Interface - Comprehensive System Debugging and Diagnostics

This module provides advanced debugging capabilities for LUKHAS AI system including:
- Real-time system state inspection
- Component debugging interfaces
- Trinity Framework diagnostics (⚛️🧠🛡️)
- Performance profiling and analysis
- Log aggregation and analysis
- Interactive debugging sessions
- Memory and resource tracking
- Guardian System debugging

#TAG:governance
#TAG:guardian
#TAG:debug
#TAG:diagnostics
#TAG:constellation
#TAG:observability
"""

import asyncio
import logging
import threading
import traceback
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class DebugLevel(Enum):
    """Debug information levels."""

    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComponentState(Enum):
    """Component operational states."""

    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class DebugCategory(Enum):
    """Debug information categories."""

    SYSTEM = "system"
    CONSCIOUSNESS = "consciousness"
    IDENTITY = "identity"
    GUARDIAN = "guardian"
    MEMORY = "memory"
    API = "api"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class DebugEvent:
    """Debug event record."""

    event_id: str
    timestamp: datetime
    level: DebugLevel
    category: DebugCategory
    component: str

    # Event details
    message: str
    details: dict[str, Any]
    stack_trace: Optional[str] = None

    # Context information
    user_context: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # Trinity Framework context
    identity_context: dict[str, Any] = field(default_factory=dict)  # ⚛️
    consciousness_context: dict[str, Any] = field(default_factory=dict)  # 🧠
    guardian_context: dict[str, Any] = field(default_factory=dict)  # 🛡️

    # Performance metrics
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


@dataclass
class ComponentSnapshot:
    """Component state snapshot for debugging."""

    component_id: str
    component_name: str
    timestamp: datetime
    state: ComponentState

    # Component details
    version: str
    configuration: dict[str, Any]
    runtime_stats: dict[str, Any]

    # Health information
    health_score: float
    error_count: int
    warning_count: int

    # Memory and resources
    memory_usage_mb: float
    cpu_usage_percent: float
    thread_count: int

    # Dependencies
    dependencies: list[str]
    dependents: list[str]

    # Recent events
    recent_events: list[DebugEvent]


@dataclass
class DebugSession:
    """Interactive debugging session."""

    session_id: str
    created_at: datetime
    user_id: Optional[str]

    # Session configuration
    debug_level: DebugLevel
    categories: set[DebugCategory]
    components: set[str]

    # Session state
    active: bool = True
    events_captured: int = 0
    breakpoints: dict[str, Any] = field(default_factory=dict)

    # Analysis tools
    filters: list[Callable] = field(default_factory=list)
    aggregators: list[Callable] = field(default_factory=list)


class DebugInterface:
    """
    Comprehensive debugging interface for LUKHAS AI.

    Provides real-time system diagnostics, component inspection,
    performance analysis, and interactive debugging capabilities.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize debug interface.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Debug configuration
        self.max_events = 10000
        self.max_sessions = 50
        self.event_retention_hours = 24

        # Event storage
        self.debug_events: deque = deque(maxlen=self.max_events)
        self.component_snapshots: dict[str, ComponentSnapshot] = {}
        self.active_sessions: dict[str, DebugSession] = {}

        # Component tracking
        self.registered_components: dict[str, dict[str, Any]] = {}
        self.component_states: dict[str, ComponentState] = {}

        # Performance tracking
        self.performance_metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.profiling_sessions: dict[str, dict[str, Any]] = {}

        # Trinity Framework debugging
        self.trinity_debug_state = {
            "identity": {"active_contexts": [], "debug_level": DebugLevel.INFO},  # ⚛️
            "consciousness": {
                "awareness_state": {},
                "debug_level": DebugLevel.INFO,
            },  # 🧠
            "guardian": {"protection_status": {}, "debug_level": DebugLevel.INFO},  # 🛡️
        }

        # Debugging state
        self.debug_enabled = True
        self.profiling_enabled = False

        logger.info("🔍 LUKHAS Debug Interface initialized")

    async def start_debug_interface(self):
        """Start the debug interface."""

        # Start background tasks
        asyncio.create_task(self._event_collection_loop())
        asyncio.create_task(self._component_monitoring_loop())
        asyncio.create_task(self._performance_analysis_loop())
        asyncio.create_task(self._session_management_loop())
        asyncio.create_task(self._trinity_debug_loop())

        logger.info("🔍 Debug interface started")

    async def log_debug_event(
        self,
        level: DebugLevel,
        category: DebugCategory,
        component: str,
        message: str,
        details: Optional[dict[str, Any]] = None,
        **context,
    ) -> str:
        """
        Log a debug event.

        Args:
            level: Debug level
            category: Debug category
            component: Component name
            message: Debug message
            details: Additional details
            **context: Additional context information

        Returns:
            str: Event ID
        """

        if not self.debug_enabled:
            return ""

        event_id = f"debug_{uuid.uuid4().hex[:8]}"

        # Create debug event
        event = DebugEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            level=level,
            category=category,
            component=component,
            message=message,
            details=details or {},
            user_context=context.get("user_id"),
            session_id=context.get("session_id"),
            request_id=context.get("request_id"),
            execution_time=context.get("execution_time"),
            memory_usage=context.get("memory_usage"),
            cpu_usage=context.get("cpu_usage"),
        )

        # Add stack trace for errors
        if level in [DebugLevel.ERROR, DebugLevel.CRITICAL]:
            event.stack_trace = traceback.format_stack()

        # Add Trinity Framework context
        if category == DebugCategory.IDENTITY:
            event.identity_context = context.get("identity_context", {})
        elif category == DebugCategory.CONSCIOUSNESS:
            event.consciousness_context = context.get("consciousness_context", {})
        elif category == DebugCategory.GUARDIAN:
            event.guardian_context = context.get("guardian_context", {})

        # Store event
        self.debug_events.append(event)

        # Notify active debug sessions
        await self._notify_debug_sessions(event)

        # Log to system logger
        log_level = {
            DebugLevel.TRACE: logging.DEBUG,
            DebugLevel.DEBUG: logging.DEBUG,
            DebugLevel.INFO: logging.INFO,
            DebugLevel.WARNING: logging.WARNING,
            DebugLevel.ERROR: logging.ERROR,
            DebugLevel.CRITICAL: logging.CRITICAL,
        }.get(level, logging.INFO)

        logger.log(log_level, f"🔍 [{category.value}] {component}: {message}")

        return event_id

    async def register_component(
        self,
        component_name: str,
        component_instance: Any,
        version: str = "unknown",
        dependencies: Optional[list[str]] = None,
    ):
        """
        Register a component for debugging.

        Args:
            component_name: Name of the component
            component_instance: Component instance
            version: Component version
            dependencies: List of component dependencies
        """

        self.registered_components[component_name] = {
            "instance": component_instance,
            "version": version,
            "dependencies": dependencies or [],
            "registered_at": datetime.now(timezone.utc),
            "debug_enabled": True,
        }

        self.component_states[component_name] = ComponentState.RUNNING

        await self.log_debug_event(
            DebugLevel.INFO,
            DebugCategory.SYSTEM,
            "debug_interface",
            f"Component registered: {component_name}",
            {"version": version, "dependencies": dependencies},
        )

    async def create_debug_session(
        self,
        user_id: Optional[str] = None,
        debug_level: DebugLevel = DebugLevel.DEBUG,
        categories: Optional[set[DebugCategory]] = None,
        components: Optional[set[str]] = None,
    ) -> str:
        """
        Create a new debug session.

        Args:
            user_id: User ID for the session
            debug_level: Minimum debug level to capture
            categories: Debug categories to include
            components: Components to monitor

        Returns:
            str: Session ID
        """

        session_id = f"debug_session_{uuid.uuid4().hex[:8]}"

        session = DebugSession(
            session_id=session_id,
            created_at=datetime.now(timezone.utc),
            user_id=user_id,
            debug_level=debug_level,
            categories=categories or set(DebugCategory),
            components=components or set(self.registered_components.keys()),
        )

        self.active_sessions[session_id] = session

        await self.log_debug_event(
            DebugLevel.INFO,
            DebugCategory.SYSTEM,
            "debug_interface",
            f"Debug session created: {session_id}",
            {"user_id": user_id, "debug_level": debug_level.value},
        )

        return session_id

    async def get_component_snapshot(self, component_name: str) -> Optional[ComponentSnapshot]:
        """
        Get a debug snapshot of a component.

        Args:
            component_name: Name of the component

        Returns:
            ComponentSnapshot: Component debug information
        """

        if component_name not in self.registered_components:
            return None

        component_info = self.registered_components[component_name]
        component_instance = component_info["instance"]

        # Collect component information
        try:
            # Get component configuration
            config = getattr(component_instance, "config", {})

            # Get runtime statistics
            runtime_stats = {}
            if hasattr(component_instance, "get_status"):
                try:
                    status = component_instance.get_status()
                    if isinstance(status, dict):
                        runtime_stats.update(status)
                except Exception as e:
                    runtime_stats["status_error"] = str(e)

            # Get health information
            health_score = 1.0
            if hasattr(component_instance, "get_monitoring_status"):
                try:
                    monitoring_status = component_instance.get_monitoring_status()
                    health_score = monitoring_status.get("health_score", 1.0)
                except Exception as e:
                    runtime_stats["health_error"] = str(e)

            # Count recent events for this component
            recent_events = [e for e in list(self.debug_events)[-100:] if e.component == component_name]

            error_count = len([e for e in recent_events if e.level == DebugLevel.ERROR])
            warning_count = len([e for e in recent_events if e.level == DebugLevel.WARNING])

            # Create snapshot
            snapshot = ComponentSnapshot(
                component_id=component_name,
                component_name=component_name,
                timestamp=datetime.now(timezone.utc),
                state=self.component_states.get(component_name, ComponentState.UNKNOWN),
                version=component_info["version"],
                configuration=self._serialize_config(config),
                runtime_stats=runtime_stats,
                health_score=health_score,
                error_count=error_count,
                warning_count=warning_count,
                memory_usage_mb=self._get_component_memory_usage(component_instance),
                cpu_usage_percent=0.0,  # Would need more sophisticated tracking
                thread_count=threading.active_count(),
                dependencies=component_info["dependencies"],
                dependents=self._find_component_dependents(component_name),
                recent_events=recent_events[-20:],  # Last 20 events
            )

            self.component_snapshots[component_name] = snapshot
            return snapshot

        except Exception as e:
            await self.log_debug_event(
                DebugLevel.ERROR,
                DebugCategory.SYSTEM,
                "debug_interface",
                f"Failed to create snapshot for {component_name}: {e}",
                {"error": str(e), "component": component_name},
            )
            return None

    async def get_debug_dashboard_data(
        self, session_id: Optional[str] = None, time_range_hours: int = 1
    ) -> dict[str, Any]:
        """
        Get comprehensive debug dashboard data.

        Args:
            session_id: Optional session ID to filter for
            time_range_hours: Time range in hours for events

        Returns:
            Dict: Debug dashboard data
        """

        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=time_range_hours)

        # Filter events by time range
        filtered_events = [e for e in self.debug_events if start_time <= e.timestamp <= end_time]

        # Filter by session if specified
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            filtered_events = [
                e
                for e in filtered_events
                if (
                    e.level.value >= session.debug_level.value
                    and e.category in session.categories
                    and e.component in session.components
                )
            ]

        # Event statistics
        events_by_level = defaultdict(int)
        events_by_category = defaultdict(int)
        events_by_component = defaultdict(int)

        for event in filtered_events:
            events_by_level[event.level.value] += 1
            events_by_category[event.category.value] += 1
            events_by_component[event.component] += 1

        # Component health summary
        component_health = {}
        for component_name in self.registered_components:
            snapshot = await self.get_component_snapshot(component_name)
            if snapshot:
                component_health[component_name] = {
                    "health_score": snapshot.health_score,
                    "state": snapshot.state.value,
                    "error_count": snapshot.error_count,
                    "warning_count": snapshot.warning_count,
                    "memory_usage_mb": snapshot.memory_usage_mb,
                }

        # Trinity Framework status
        trinity_status = {
            "identity": {
                "health": self._get_trinity_component_health("identity"),
                "active_contexts": len(self.trinity_debug_state["identity"]["active_contexts"]),
                "debug_level": self.trinity_debug_state["identity"]["debug_level"].value,
            },
            "consciousness": {
                "health": self._get_trinity_component_health("consciousness"),
                "awareness_state": len(self.trinity_debug_state["consciousness"]["awareness_state"]),
                "debug_level": self.trinity_debug_state["consciousness"]["debug_level"].value,
            },
            "guardian": {
                "health": self._get_trinity_component_health("guardian"),
                "protection_active": bool(self.trinity_debug_state["guardian"]["protection_status"]),
                "debug_level": self.trinity_debug_state["guardian"]["debug_level"].value,
            },
        }

        # Performance metrics summary
        performance_summary = {}
        for metric_name, metric_values in self.performance_metrics.items():
            if metric_values:
                recent_values = list(metric_values)[-100:]  # Last 100 values
                performance_summary[metric_name] = {
                    "current": recent_values[-1] if recent_values else 0.0,
                    "average": sum(recent_values) / len(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "trend": self._calculate_trend(recent_values),
                }

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "time_range_hours": time_range_hours,
            "session_id": session_id,
            "debug_enabled": self.debug_enabled,
            "profiling_enabled": self.profiling_enabled,
            # Event statistics
            "events": {
                "total_count": len(filtered_events),
                "by_level": dict(events_by_level),
                "by_category": dict(events_by_category),
                "by_component": dict(events_by_component),
                "recent_events": [self._serialize_event(e) for e in filtered_events[-50:]],
            },
            # Component information
            "components": {
                "registered_count": len(self.registered_components),
                "health_summary": component_health,
                "snapshots_available": list(self.component_snapshots.keys()),
            },
            # Debug sessions
            "sessions": {
                "active_count": len(self.active_sessions),
                "active_sessions": [
                    {
                        "session_id": s.session_id,
                        "user_id": s.user_id,
                        "debug_level": s.debug_level.value,
                        "events_captured": s.events_captured,
                        "created_at": s.created_at.isoformat(),
                    }
                    for s in self.active_sessions.values()
                ],
            },
            # Trinity Framework status
            "constellation_framework": trinity_status,
            # Performance metrics
            "performance": performance_summary,
            # System information
            "system": {
                "debug_events_stored": len(self.debug_events),
                "max_events": self.max_events,
                "profiling_sessions": len(self.profiling_sessions),
                "uptime": self._get_system_uptime(),
            },
        }

    async def start_profiling_session(self, component_name: str, session_name: Optional[str] = None) -> str:
        """
        Start a performance profiling session for a component.

        Args:
            component_name: Component to profile
            session_name: Optional session name

        Returns:
            str: Profiling session ID
        """

        session_id = f"profile_{uuid.uuid4().hex[:8]}"
        session_name = session_name or f"Profile {component_name}"

        profiling_session = {
            "session_id": session_id,
            "session_name": session_name,
            "component_name": component_name,
            "started_at": datetime.now(timezone.utc),
            "samples": [],
            "active": True,
        }

        self.profiling_sessions[session_id] = profiling_session

        await self.log_debug_event(
            DebugLevel.INFO,
            DebugCategory.PERFORMANCE,
            "debug_interface",
            f"Started profiling session for {component_name}",
            {"session_id": session_id, "session_name": session_name},
        )

        return session_id

    # Background monitoring loops

    async def _event_collection_loop(self):
        """Background loop for event collection and processing."""

        while True:
            try:
                # Clean up old events
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.event_retention_hours)
                while self.debug_events and self.debug_events[0].timestamp < cutoff_time:
                    self.debug_events.popleft()

                await asyncio.sleep(60)  # Clean up every minute

            except Exception as e:
                logger.error(f"Event collection loop error: {e}")
                await asyncio.sleep(60)

    async def _component_monitoring_loop(self):
        """Background loop for component state monitoring."""

        while True:
            try:
                # Update component snapshots
                for component_name in self.registered_components:
                    await self.get_component_snapshot(component_name)

                await asyncio.sleep(30)  # Update every 30 seconds

            except Exception as e:
                logger.error(f"Component monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def _performance_analysis_loop(self):
        """Background loop for performance analysis."""

        while True:
            try:
                # Collect performance metrics
                await self._collect_performance_metrics()

                await asyncio.sleep(5)  # Collect every 5 seconds

            except Exception as e:
                logger.error(f"Performance analysis loop error: {e}")
                await asyncio.sleep(30)

    async def _session_management_loop(self):
        """Background loop for debug session management."""

        while True:
            try:
                # Clean up inactive sessions
                current_time = datetime.now(timezone.utc)
                inactive_sessions = []

                for session_id, session in self.active_sessions.items():
                    if current_time - session.created_at > timedelta(hours=24):
                        inactive_sessions.append(session_id)

                for session_id in inactive_sessions:
                    del self.active_sessions[session_id]
                    await self.log_debug_event(
                        DebugLevel.INFO,
                        DebugCategory.SYSTEM,
                        "debug_interface",
                        f"Debug session expired: {session_id}",
                    )

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Session management loop error: {e}")
                await asyncio.sleep(300)

    async def _trinity_debug_loop(self):
        """Background loop for Trinity Framework debugging."""

        while True:
            try:
                # Update Trinity Framework debug state
                await self._update_trinity_debug_state()

                await asyncio.sleep(15)  # Update every 15 seconds

            except Exception as e:
                logger.error(f"Trinity debug loop error: {e}")
                await asyncio.sleep(60)

    # Helper methods

    async def _notify_debug_sessions(self, event: DebugEvent):
        """Notify active debug sessions about new events."""

        for session in self.active_sessions.values():
            if (
                event.level.value >= session.debug_level.value
                and event.category in session.categories
                and event.component in session.components
            ):
                session.events_captured += 1

    def _serialize_config(self, config: Any) -> dict[str, Any]:
        """Serialize configuration for debug output."""

        try:
            if isinstance(config, dict):
                return {k: str(v) for k, v in config.items()}
            else:
                return {"value": str(config)}
        except:
            return {"error": "Failed to serialize configuration"}

    def _serialize_event(self, event: DebugEvent) -> dict[str, Any]:
        """Serialize debug event for output."""

        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "level": event.level.value,
            "category": event.category.value,
            "component": event.component,
            "message": event.message,
            "details": event.details,
            "execution_time": event.execution_time,
            "memory_usage": event.memory_usage,
            "cpu_usage": event.cpu_usage,
        }

    def _get_component_memory_usage(self, component_instance: Any) -> float:
        """Estimate component memory usage."""

        try:
            import sys

            return sys.getsizeof(component_instance) / (1024 * 1024)  # MB
        except:
            return 0.0

    def _find_component_dependents(self, component_name: str) -> list[str]:
        """Find components that depend on the given component."""

        dependents = []
        for name, info in self.registered_components.items():
            if component_name in info.get("dependencies", []):
                dependents.append(name)

        return dependents

    def _get_trinity_component_health(self, framework_component: str) -> float:
        """Get Trinity Framework component health score."""

        # Simulate health calculation based on registered components
        related_components = [name for name in self.registered_components if framework_component in name.lower()]

        if not related_components:
            return 1.0

        total_health = 0.0
        for component in related_components:
            if component in self.component_snapshots:
                total_health += self.component_snapshots[component].health_score
            else:
                total_health += 0.8  # Default health

        return total_health / len(related_components)

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction for a series of values."""

        if len(values) < 2:
            return "stable"

        recent = values[-5:]  # Last 5 values
        older = values[-10:-5] if len(values) >= 10 else values[:-5]

        if not older:
            return "stable"

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)

        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

    def _get_system_uptime(self) -> str:
        """Get system uptime information."""

        try:
            import uptime

            uptime_seconds = uptime.uptime()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except:
            return "unknown"

    async def _collect_performance_metrics(self):
        """Collect system performance metrics."""

        try:
            import psutil

            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            self.performance_metrics["cpu_usage"].append(cpu_percent)
            self.performance_metrics["memory_usage"].append(memory_percent)

            # Network metrics
            try:
                net_io = psutil.net_io_counters()
                self.performance_metrics["network_bytes_sent"].append(net_io.bytes_sent)
                self.performance_metrics["network_bytes_recv"].append(net_io.bytes_recv)
            except:
                pass

        except ImportError:
            # psutil not available, skip performance collection
            pass

    async def _update_trinity_debug_state(self):
        """Update Trinity Framework debug state."""

        # Update identity debug state (⚛️)
        identity_components = [name for name in self.registered_components if "identity" in name.lower()]
        self.trinity_debug_state["identity"]["active_contexts"] = identity_components

        # Update consciousness debug state (🧠)
        consciousness_components = [
            name
            for name in self.registered_components
            if "consciousness" in name.lower() or "awareness" in name.lower()
        ]
        self.trinity_debug_state["consciousness"]["awareness_state"] = {
            comp: "active" for comp in consciousness_components
        }

        # Update guardian debug state (🛡️)
        guardian_components = [name for name in self.registered_components if "guardian" in name.lower()]
        self.trinity_debug_state["guardian"]["protection_status"] = {comp: "protected" for comp in guardian_components}


# Export main classes
__all__ = [
    "ComponentSnapshot",
    "ComponentState",
    "DebugCategory",
    "DebugEvent",
    "DebugInterface",
    "DebugLevel",
    "DebugSession",
]
