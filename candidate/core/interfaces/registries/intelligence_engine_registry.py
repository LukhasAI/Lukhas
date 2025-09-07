"""
═══════════════════════════════════════════════════════════════════════════
LUKHAS AGI Intelligence Engine Registry
═══════════════════════════════════════════════════════════════════════════

Central registry for managing intelligence engines across the LUKHAS AGI
ecosystem. Provides discovery, registration, health monitoring, and
load balancing capabilities.

Features:
- Engine registration and discovery
- Health monitoring and heartbeat
- Capability-based routing
- Load balancing and failover
- Security and access control
- Performance metrics
"""
import streamlit as st
from datetime import timezone

import asyncio
import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class EngineType(Enum):
    """Types of intelligence engines"""

    CONSCIOUSNESS = "consciousness"
    MEMORY = "memory"
    REASONING = "reasoning"
    LEARNING = "learning"
    CREATIVITY = "creativity"
    EMOTION = "emotion"
    ETHICS = "ethics"
    QUANTUM = "quantum"
    ORCHESTRATION = "orchestration"
    INTERFACE = "interface"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class EngineStatus(Enum):
    """Engine status states"""

    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class RegistryEvent(Enum):
    """Registry event types"""

    ENGINE_REGISTERED = "engine_registered"
    ENGINE_UNREGISTERED = "engine_unregistered"
    ENGINE_STATUS_CHANGED = "engine_status_changed"
    HEALTH_CHECK_FAILED = "health_check_failed"
    CAPABILITY_UPDATED = "capability_updated"


@dataclass
class EngineCapability:
    """Represents an engine capability"""

    name: str
    version: str
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineInfo:
    """Information about a registered engine"""

    engine_id: str
    engine_type: EngineType
    name: str
    version: str
    description: str = ""
    capabilities: list[EngineCapability] = field(default_factory=list)
    endpoint: str = ""
    health_endpoint: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)

    # Runtime information
    status: EngineStatus = EngineStatus.INITIALIZING
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_score: float = 0.0
    load_score: float = 0.0
    request_count: int = 0
    error_count: int = 0


@dataclass
class RegistryConfig:
    """Configuration for the intelligence registry"""

    heartbeat_interval: int = 30  # seconds
    health_check_interval: int = 60  # seconds
    engine_timeout: int = 300  # seconds
    max_failed_health_checks: int = 3
    enable_load_balancing: bool = True
    enable_auto_discovery: bool = False
    registry_persistence_path: Optional[str] = None
    security_enabled: bool = True
    max_engines_per_type: int = 10


@dataclass
class QueryFilter:
    """Filter criteria for engine queries"""

    engine_types: Optional[list[EngineType]] = None
    capabilities: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    status_filter: Optional[list[EngineStatus]] = None
    min_health_score: float = 0.0
    exclude_overloaded: bool = True


class HealthChecker(ABC):
    """Abstract base class for engine health checkers"""

    @abstractmethod
    async def check_health(self, engine_info: EngineInfo) -> dict[str, Any]:
        """Check the health of an engine"""


class IntelligenceEngineRegistry:
    """Central registry for intelligence engines"""

    def __init__(self, config: Optional[RegistryConfig] = None):
        self.config = config or RegistryConfig()
        self.engines: dict[str, EngineInfo] = {}
        self.engine_types_index: dict[EngineType, set[str]] = {}
        self.capabilities_index: dict[str, set[str]] = {}
        self.tags_index: dict[str, set[str]] = {}

        # Health monitoring
        self.health_checker: Optional[HealthChecker] = None
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Event handling
        self.event_handlers: dict[RegistryEvent, list[Callable]] = {}

        # Security
        self.access_tokens: dict[str, str] = {}

        self.logger = logger.getChild("IntelligenceEngineRegistry")
        self.logger.info("Intelligence Engine Registry initialized")

        # Start monitoring if enabled
        if self.config.heartbeat_interval > 0:
            self.start_monitoring()

    def register_engine(self, engine_info: EngineInfo, access_token: Optional[str] = None) -> bool:
        """Register a new intelligence engine"""
        try:
            # Validate access if security is enabled
            if self.config.security_enabled and not self._validate_access(access_token):
                self.logger.warning(f"Access denied for engine registration: {engine_info.engine_id}")
                return False

            # Check if engine already exists
            if engine_info.engine_id in self.engines:
                self.logger.warning(f"Engine already registered: {engine_info.engine_id}")
                return False

            # Check engine type limits
            type_index = self.engine_types_index.get(engine_info.engine_type, set())
            type_count = len(type_index)
            if type_count >= self.config.max_engines_per_type:
                self.logger.warning(f"Maximum engines reached for type {engine_info.engine_type}: {type_count}")
                return False

            # Register the engine
            engine_info.registered_at = datetime.now(timezone.utc)
            engine_info.status = EngineStatus.HEALTHY
            self.engines[engine_info.engine_id] = engine_info

            # Update indices
            self._update_indices(engine_info, add=True)

            # Generate access token
            if self.config.security_enabled:
                token = self._generate_access_token(engine_info.engine_id)
                self.access_tokens[engine_info.engine_id] = token

            self.logger.info(f"Registered engine: {engine_info.engine_id} ({engine_info.engine_type.value})")

            # Fire event
            self._fire_event(RegistryEvent.ENGINE_REGISTERED, {"engine_info": engine_info})

            return True

        except Exception as e:
            self.logger.error(f"Failed to register engine {engine_info.engine_id}: {e}")
            return False

    def unregister_engine(self, engine_id: str, access_token: Optional[str] = None) -> bool:
        """Unregister an intelligence engine"""
        try:
            # Validate access
            security_check = self.config.security_enabled and not self._validate_engine_access(engine_id, access_token)
            if security_check:
                return False

            if engine_id not in self.engines:
                return False

            engine_info = self.engines[engine_id]

            # Update indices
            self._update_indices(engine_info, add=False)

            # Remove from registry
            del self.engines[engine_id]

            # Remove access token
            if engine_id in self.access_tokens:
                del self.access_tokens[engine_id]

            self.logger.info(f"Unregistered engine: {engine_id}")

            # Fire event
            self._fire_event(RegistryEvent.ENGINE_UNREGISTERED, {"engine_id": engine_id})

            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister engine {engine_id}: {e}")
            return False

    def query_engines(self, filter_criteria: Optional[QueryFilter] = None) -> list[EngineInfo]:
        """Query engines based on filter criteria"""
        if filter_criteria is None:
            filter_criteria = QueryFilter()

        matching_engines = []

        for engine_info in self.engines.values():
            if self._matches_filter(engine_info, filter_criteria):
                matching_engines.append(engine_info)

        # Sort by health score and load
        matching_engines.sort(key=lambda e: (e.health_score, -e.load_score), reverse=True)

        return matching_engines

    def get_engine(self, engine_id: str) -> Optional[EngineInfo]:
        """Get information about a specific engine"""
        return self.engines.get(engine_id)

    def update_engine_status(
        self,
        engine_id: str,
        status: EngineStatus,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Update the status of an engine"""
        if engine_id not in self.engines:
            return False

        engine_info = self.engines[engine_id]
        old_status = engine_info.status
        engine_info.status = status

        if metadata:
            engine_info.metadata.update(metadata)

        self.logger.info(f"Engine {engine_id} status changed: {old_status.value} -> {status.value}")

        # Fire event
        self._fire_event(
            RegistryEvent.ENGINE_STATUS_CHANGED,
            {
                "engine_id": engine_id,
                "old_status": old_status,
                "new_status": status,
            },
        )

        return True

    def record_heartbeat(self, engine_id: str) -> bool:
        """Record a heartbeat from an engine"""
        if engine_id not in self.engines:
            return False

        self.engines[engine_id].last_heartbeat = datetime.now(timezone.utc)
        return True

    def update_engine_metrics(self, engine_id: str, metrics: dict[str, Any]) -> bool:
        """Update engine performance metrics"""
        if engine_id not in self.engines:
            return False

        engine_info = self.engines[engine_id]

        # Update metrics
        if "request_count" in metrics:
            engine_info.request_count = metrics["request_count"]
        if "error_count" in metrics:
            engine_info.error_count = metrics["error_count"]
        if "load_score" in metrics:
            engine_info.load_score = metrics["load_score"]
        if "health_score" in metrics:
            engine_info.health_score = metrics["health_score"]

        return True

    def get_engines_by_capability(self, capability: str) -> list[EngineInfo]:
        """Get engines that support a specific capability"""
        engine_ids = self.capabilities_index.get(capability, set())
        return [self.engines[eid] for eid in engine_ids if eid in self.engines]

    def get_engines_by_type(self, engine_type: EngineType) -> list[EngineInfo]:
        """Get engines of a specific type"""
        engine_ids = self.engine_types_index.get(engine_type, set())
        return [self.engines[eid] for eid in engine_ids if eid in self.engines]

    def set_health_checker(self, health_checker: HealthChecker):
        """Set the health checker for engines"""
        self.health_checker = health_checker

    def add_event_handler(self, event: RegistryEvent, handler: Callable):
        """Add an event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def start_monitoring(self):
        """Start engine monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_engines, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Engine monitoring started")

    def stop_monitoring(self):
        """Stop engine monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Engine monitoring stopped")

    def get_registry_metrics(self) -> dict[str, Any]:
        """Get registry performance metrics"""
        now = datetime.now(timezone.utc)
        healthy_engines = sum(1 for e in self.engines.values() if e.status == EngineStatus.HEALTHY)

        uptime = (now - datetime.now(timezone.utc)).total_seconds() if hasattr(self, "start_time") else 0

        return {
            "total_engines": len(self.engines),
            "healthy_engines": healthy_engines,
            "engine_types": {et.value: len(engines) for et, engines in self.engine_types_index.items()},
            "capabilities": len(self.capabilities_index),
            "monitoring_active": self.monitoring_active,
            "uptime_seconds": uptime,
        }

    def save_registry_state(self, file_path: str):
        """Save registry state to file"""
        try:
            state = {
                "engines": {
                    eid: {
                        "engine_id": info.engine_id,
                        "engine_type": info.engine_type.value,
                        "name": info.name,
                        "version": info.version,
                        "description": info.description,
                        "capabilities": [
                            {
                                "name": cap.name,
                                "version": cap.version,
                                "description": cap.description,
                                "parameters": cap.parameters,
                                "metadata": cap.metadata,
                            }
                            for cap in info.capabilities
                        ],
                        "endpoint": info.endpoint,
                        "health_endpoint": info.health_endpoint,
                        "metadata": info.metadata,
                        "tags": list(info.tags),
                        "status": info.status.value,
                        "registered_at": info.registered_at.isoformat(),
                        "health_score": info.health_score,
                        "load_score": info.load_score,
                        "request_count": info.request_count,
                        "error_count": info.error_count,
                    }
                    for eid, info in self.engines.items()
                },
                "config": {
                    "heartbeat_interval": self.config.heartbeat_interval,
                    "health_check_interval": self.config.health_check_interval,
                    "engine_timeout": self.config.engine_timeout,
                    "max_failed_health_checks": self.config.max_failed_health_checks,
                    "enable_load_balancing": self.config.enable_load_balancing,
                    "max_engines_per_type": self.config.max_engines_per_type,
                },
            }

            with open(file_path, "w") as f:
                json.dump(state, f, indent=2)

            self.logger.info(f"Registry state saved to {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to save registry state: {e}")

    def _update_indices(self, engine_info: EngineInfo, add: bool = True):
        """Update internal indices"""
        engine_id = engine_info.engine_id

        # Update type index
        if add:
            if engine_info.engine_type not in self.engine_types_index:
                self.engine_types_index[engine_info.engine_type] = set()
            self.engine_types_index[engine_info.engine_type].add(engine_id)
        else:
            if engine_info.engine_type in self.engine_types_index:
                self.engine_types_index[engine_info.engine_type].discard(engine_id)

        # Update capabilities index
        for capability in engine_info.capabilities:
            if add:
                if capability.name not in self.capabilities_index:
                    self.capabilities_index[capability.name] = set()
                self.capabilities_index[capability.name].add(engine_id)
            else:
                if capability.name in self.capabilities_index:
                    self.capabilities_index[capability.name].discard(engine_id)

        # Update tags index
        for tag in engine_info.tags:
            if add:
                if tag not in self.tags_index:
                    self.tags_index[tag] = set()
                self.tags_index[tag].add(engine_id)
            else:
                if tag in self.tags_index:
                    self.tags_index[tag].discard(engine_id)

    def _matches_filter(self, engine_info: EngineInfo, filter_criteria: QueryFilter) -> bool:
        """Check if engine matches filter criteria"""
        # Type filter
        if filter_criteria.engine_types and engine_info.engine_type not in filter_criteria.engine_types:
            return False

        # Capabilities filter
        if filter_criteria.capabilities:
            engine_capabilities = {cap.name for cap in engine_info.capabilities}
            if not any(cap in engine_capabilities for cap in filter_criteria.capabilities):
                return False

        # Tags filter
        if filter_criteria.tags and not any(tag in engine_info.tags for tag in filter_criteria.tags):
            return False

        # Status filter
        if filter_criteria.status_filter and engine_info.status not in filter_criteria.status_filter:
            return False

        # Health score filter
        if engine_info.health_score < filter_criteria.min_health_score:
            return False

        # Load filter
        return not (filter_criteria.exclude_overloaded and engine_info.load_score > 0.9)

    def _validate_access(self, access_token: Optional[str]) -> bool:
        """Validate access token"""
        if not self.config.security_enabled:
            return True

        # Simplified token validation - in production, use proper JWT or similar
        return access_token is not None and len(access_token) > 0

    def _validate_engine_access(self, engine_id: str, access_token: Optional[str]) -> bool:
        """Validate engine-specific access"""
        if not self.config.security_enabled:
            return True

        stored_token = self.access_tokens.get(engine_id)
        return stored_token == access_token

    def _generate_access_token(self, engine_id: str) -> str:
        """Generate access token for engine"""
        # Simplified token generation - use proper cryptographic methods in production
        return f"token_{engine_id}_{uuid.uuid4().hex[:16]}"

    def _fire_event(self, event: RegistryEvent, event_data: dict[str, Any]):
        """Fire an event to all registered handlers"""
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(event, event_data)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event}: {e}")

    def _monitor_engines(self):
        """Background monitoring of engines"""
        while self.monitoring_active:
            try:
                self._check_engine_heartbeats()

                if self.health_checker:
                    self._perform_health_checks()

                time.sleep(self.config.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Error in engine monitoring: {e}")
                time.sleep(5)  # Brief pause before retrying

    def _check_engine_heartbeats(self):
        """Check for missing heartbeats"""
        now = datetime.now(timezone.utc)
        timeout_threshold = timedelta(seconds=self.config.engine_timeout)

        for engine_id, engine_info in self.engines.items():
            if engine_info.last_heartbeat:
                time_since_heartbeat = now - engine_info.last_heartbeat
                if time_since_heartbeat > timeout_threshold:
                    if engine_info.status == EngineStatus.HEALTHY:
                        self.update_engine_status(engine_id, EngineStatus.UNHEALTHY)
                        self.logger.warning(f"Engine {engine_id} missed heartbeat")

    def _perform_health_checks(self):
        """Perform health checks on engines"""
        if not self.health_checker:
            return

        # Submit health checks to executor
        for engine_info in self.engines.values():
            if engine_info.status in [
                EngineStatus.HEALTHY,
                EngineStatus.DEGRADED,
            ]:
                self.executor.submit(self._check_engine_health, engine_info)

    def _check_engine_health(self, engine_info: EngineInfo):
        """Check health of a single engine"""
        try:
            # This would be async in a real implementation
            health_result = asyncio.run(self.health_checker.check_health(engine_info))

            # Update health metrics
            engine_info.last_health_check = datetime.now(timezone.utc)
            engine_info.health_score = health_result.get("health_score", 0.0)

            # Update status based on health
            if engine_info.health_score > 0.8:
                new_status = EngineStatus.HEALTHY
            elif engine_info.health_score > 0.5:
                new_status = EngineStatus.DEGRADED
            else:
                new_status = EngineStatus.UNHEALTHY

            if new_status != engine_info.status:
                self.update_engine_status(engine_info.engine_id, new_status)

        except Exception as e:
            self.logger.error(f"Health check failed for {engine_info.engine_id}: {e}")
            self._fire_event(
                RegistryEvent.HEALTH_CHECK_FAILED,
                {"engine_id": engine_info.engine_id, "error": str(e)},
            )


# Global registry instance
_global_registry: Optional[IntelligenceEngineRegistry] = None


def get_global_registry(
    config: Optional[RegistryConfig] = None,
) -> IntelligenceEngineRegistry:
    """Get the global intelligence engine registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = IntelligenceEngineRegistry(config)
    return _global_registry


# Factory functions


def create_engine_info(engine_id: str, engine_type: EngineType, name: str, version: str, **kwargs) -> EngineInfo:
    """Factory function to create EngineInfo"""
    return EngineInfo(
        engine_id=engine_id,
        engine_type=engine_type,
        name=name,
        version=version,
        **kwargs,
    )


def create_capability(name: str, version: str, **kwargs) -> EngineCapability:
    """Factory function to create EngineCapability"""
    return EngineCapability(name=name, version=version, **kwargs)
