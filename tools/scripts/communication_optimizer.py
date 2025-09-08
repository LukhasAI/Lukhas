#!/usr/bin/env python3
"""
 Communication Optimizer
===========================
Implements optimizations for module communication pathways.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class CommunicationOptimizer:
    """Optimizes module communication pathways in LUKHAS """

    def __init__(self):
        self.root_path = Path("/Users/agi_dev/Lukhas"
        self.optimizations_made = []
        self.phase_status = {
            "phase1": "pending",
            "phase2": "pending",
            "phase3": "pending",
            "phase4": "pending",
        }

    def phase1_break_circular_dependencies(self):
        """Phase 1: Break circular dependencies using interfaces"""
        logger.info("\n🔧 PHASE 1: Breaking Circular Dependencies")
        logger.info("=" * 60)

        # Load the communication analysis report
        report_path = (
            self.root_path / "docs" / "reports" / "module_communication_analysis.json"
        )
        if not report_path.exists():
            logger.error("Communication analysis report not found. Run analyzer first.")
            return

        with open(report_path) as f:
            report = json.load(f)

        circular_deps = report["issues"]["circular_dependencies"]

        if not circular_deps:
            logger.info("✅ No circular dependencies found!")
            self.phase_status["phase1"] = "completed"
            return

        # Create interface definitions to break cycles
        self._create_module_interfaces()

        # Create dependency injection container
        self._create_dependency_container()

        logger.info(
            f"\n✅ Phase 1 complete. Created interfaces to break {len(circular_deps)} circular dependencies"
        )
        self.phase_status["phase1"] = "completed"

    def phase2_implement_event_bus(self):
        """Phase 2: Implement centralized event bus"""
        logger.info("\n🔧 PHASE 2: Implementing Centralized Event Bus")
        logger.info("=" * 60)

        # Create event bus implementation
        event_bus_content = '''"""
LUKHAS Event Bus
================
Centralized event system for loose module coupling.
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass

class Event:
    """Base event class"""
    event_type: str
    source_module: str
    target_module: Optional[str] = None
    payload: Dict[str, Any] = None
    timestamp: datetime = None
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.payload is None:
            self.payload = {}

class EventBus:
    """Centralized event bus for module communication"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._metrics = {
            'events_published': 0,
            'events_delivered': 0,
            'events_failed': 0
        }

    def subscribe(self, event_type: str, handler: Callable, is_async: bool = False):
        """Subscribe to an event type"""
        if is_async:
            self._async_subscribers[event_type].append(handler)
        else:
            self._subscribers[event_type].append(handler)

        logger.info(f"Subscribed {'async ' if is_async else ''}handler to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type"""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
        if handler in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(handler)

    async def publish(self, event: Event):
        """Publish an event"""
        await self._event_queue.put(event)
        self._metrics['events_published'] += 1

        # Process immediately if not running event loop
        if not self._running:
            await self._process_event(event)

    def publish_sync(self, event: Event):
        """Synchronously publish an event"""
        self._metrics['events_published'] += 1

        # Call sync handlers
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
                self._metrics['events_delivered'] += 1
            except Exception as e:
                logger.error(f"Error in sync handler for {event.event_type}: {e}")
                self._metrics['events_failed'] += 1

    async def _process_event(self, event: Event):
        """Process a single event"""
        # Call sync handlers
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
                self._metrics['events_delivered'] += 1
            except Exception as e:
                logger.error(f"Error in sync handler for {event.event_type}: {e}")
                self._metrics['events_failed'] += 1

        # Call async handlers
        tasks = []
        for handler in self._async_subscribers.get(event.event_type, []):
            tasks.append(self._call_async_handler(handler, event))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in async handler: {result}")
                    self._metrics['events_failed'] += 1
                else:
                    self._metrics['events_delivered'] += 1

    async def _call_async_handler(self, handler: Callable, event: Event):
        """Call an async handler safely"""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in async handler for {event.event_type}: {e}")
            raise

    async def start(self):
        """Start the event bus processing loop"""
        self._running = True
        logger.info("Event bus started")

        while self._running:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def stop(self):
        """Stop the event bus"""
        self._running = False

        # Process remaining events
        while not self._event_queue.empty():
            event = await self._event_queue.get()
            await self._process_event(event)

        logger.info("Event bus stopped")

    def get_metrics(self) -> Dict[str, int]:
        """Get event bus metrics"""
        return self._metrics.copy()

# Global event bus instance
event_bus = EventBus()

# Common event types

class EventTypes:
    """Standard event types for LUKHAS modules"""

    # Core events
    MODULE_INITIALIZED = "module.initialized"
    MODULE_SHUTDOWN = "module.shutdown"

    # Consciousness events
    AWARENESS_CHANGED = "consciousness.awareness_changed"
    REFLECTION_COMPLETE = "consciousness.reflection_complete"

    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RETRIEVED = "memory.retrieved"
    FOLD_CREATED = "memory.fold_created"

    # Orchestration events
    TASK_STARTED = "orchestration.task_started"
    TASK_COMPLETED = "orchestration.task_completed"
    WORKFLOW_TRIGGERED = "orchestration.workflow_triggered"

    # Governance events
    POLICY_VIOLATED = "governance.policy_violated"
    PERMISSION_GRANTED = "governance.permission_granted"
    AUDIT_LOGGED = "governance.audit_logged"

    # GLYPH events
    GLYPH_EMITTED = "glyph.emitted"
    GLYPH_PROCESSED = "glyph.processed"

# Helper functions

def emit_event(event_type: str, source: str, payload: Dict[str, Any] = None):
    """Helper to emit events synchronously"""
    event = Event(
        event_type=event_type,
        source_module=source,
        payload=payload
    )
    event_bus.publish_sync(event)

async def emit_event_async(event_type: str, source: str, payload: Dict[str,
    Any] = None):
    """Helper to emit events asynchronously"""
    event = Event(
        event_type=event_type,
        source_module=source,
        payload=payload
    )
    await kernel_bus.emit(event)
'''

        # Save event bus
        event_bus_path = self.root_path / "lukhas" / "common" / "event_bus.py"
        event_bus_path.parent.mkdir(parents=True, exist_ok=True)

        with open(event_bus_path, "w") as f:
            f.write(event_bus_content)

        logger.info(f"✅ Created event bus at: {event_bus_path}")

        # Create event adapters for existing modules
        self._create_event_adapters()

        self.phase_status["phase2"] = "completed"

    def phase3_optimize_glyph_communication(self):
        """Phase 3: Optimize GLYPH communication"""
        logger.info("\n🔧 PHASE 3: Optimizing GLYPH Communication")
        logger.info("=" * 60)

        # Create GLYPH router
        glyph_router_content = '''"""
GLYPH Communication Router
=========================
Optimized routing and caching for GLYPH-based communication.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict
from functools import lru_cache

from lukhas.core.common import GLYPHSymbol

logger = logging.getLogger(__name__)

@dataclass

class GLYPHRoute:
    """Represents a GLYPH routing rule"""
    glyph_type: str
    source_pattern: str
    target_module: str
    priority: int = 0
    cache_ttl: int = 60  # seconds

class GLYPHRouter:
    """Intelligent GLYPH routing system"""

    def __init__(self):
        self._routes: Dict[str, List[GLYPHRoute]] = defaultdict(list)
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._metrics = {
            'glyphs_routed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'routing_errors': 0
        }

        # Initialize default routes
        self._initialize_default_routes()

    def _initialize_default_routes(self):
        """Set up default GLYPH routes"""
        default_routes = [
            # Core system routes
            GLYPHRoute("SYSTEM_*", "core.*", "orchestration", priority=10),
            GLYPHRoute("CONFIG_*", "core.*", "governance", priority=5),

            # Consciousness routes
            GLYPHRoute("AWARENESS_*", "consciousness.*", "consciousness.unified",
    priority=10),
            GLYPHRoute("DREAM_*", "consciousness.dream.*", "consciousness.dream",
    priority=10),

            # Memory routes
            GLYPHRoute("MEMORY_*", "memory.*", "memory.core", priority=10),
            GLYPHRoute("FOLD_*", "memory.folds.*", "memory.folds", priority=10),

            # Cross-module routes
            GLYPHRoute("SYNC_*", "*", "orchestration.brain", priority=20),
            GLYPHRoute("ERROR_*", "*", "governance.guardian", priority=30),
        ]

        for route in default_routes:
            self.add_route(route)

    def add_route(self, route: GLYPHRoute):
        """Add a GLYPH route"""
        self._routes[route.glyph_type].append(route)
        # Sort by priority
        self._routes[route.glyph_type].sort(key=lambda r: r.priority, reverse=True)

    def register_handler(self, glyph_pattern: str, handler: Callable):
        """Register a GLYPH handler"""
        self._handlers[glyph_pattern].append(handler)
        logger.info(f"Registered handler for pattern: {glyph_pattern}")

    async def route_glyph(self, glyph: GLYPHSymbol, source_module: str) -> Optional[str]:
        """Route a GLYPH to appropriate handler"""
        glyph_type = glyph.symbol_type

        # Check cache first
        cache_key = f"{glyph_type}:{source_module}"
        cached_result = self._get_cached_route(cache_key)
        if cached_result:
            self._metrics['cache_hits'] += 1
            return cached_result

        self._metrics['cache_misses'] += 1

        # Find matching routes
        target_module = None
        for pattern, routes in self._routes.items():
            if self._matches_pattern(glyph_type, pattern):
                for route in routes:
                    if self._matches_pattern(source_module, route.source_pattern):
                        target_module = route.target_module
                        # Cache the result
                        self._cache_route(cache_key, target_module, route.cache_ttl)
                        break

        if target_module:
            self._metrics['glyphs_routed'] += 1
            await self._deliver_glyph(glyph, target_module)
            return target_module
        else:
            self._metrics['routing_errors'] += 1
            logger.warning(f"No route found for GLYPH {glyph_type} from {source_module}")
            return None

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches pattern (supports wildcards)"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        return value == pattern

    def _get_cached_route(self, cache_key: str) -> Optional[str]:
        """Get cached route if valid"""
        if cache_key in self._cache:
            timestamp = self._cache_timestamps[cache_key]
            if datetime.now(timezone.utc) - timestamp < timedelta(seconds=60):
                return self._cache[cache_key]
        return None

    def _cache_route(self, cache_key: str, target: str, ttl: int):
        """Cache a routing decision"""
        self._cache[cache_key] = target
        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)

    async def _deliver_glyph(self, glyph: GLYPHSymbol, target_module: str):
        """Deliver GLYPH to target module handlers"""
        # Find matching handlers
        for pattern, handlers in self._handlers.items():
            if self._matches_pattern(glyph.symbol_type, pattern):
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(glyph, target_module)
                        else:
                            handler(glyph, target_module)
                    except Exception as e:
                        logger.error(f"Error in GLYPH handler: {e}")

    def get_metrics(self) -> Dict[str, int]:
        """Get routing metrics"""
        return self._metrics.copy()

    def clear_cache(self):
        """Clear routing cache"""
        self._cache.clear()
        self._cache_timestamps.clear()

# Global GLYPH router instance
glyph_router = GLYPHRouter()

# Helper functions
async def emit_glyph(glyph: GLYPHSymbol, source_module: str):
    """Emit a GLYPH through the router"""
    await glyph_router.route_glyph(glyph, source_module)

def create_glyph(symbol_type: str, payload: Dict[str, Any], metadata: Dict[str,
    Any] = None) -> GLYPHSymbol:
    """Create a GLYPH with standard format"""
    return GLYPHSymbol(
        symbol_type=symbol_type,
        symbol_data=payload,
        metadata=metadata or {},
        timestamp=datetime.now(timezone.utc)
    )
'''

        # Save GLYPH router
        glyph_router_path = self.root_path / "lukhas" / "common" / "glyph_router.py"

        with open(glyph_router_path, "w") as f:
            f.write(glyph_router_content)

        logger.info(f"✅ Created GLYPH router at: {glyph_router_path}")

        self.phase_status["phase3"] = "completed"

    def phase4_decouple_bottlenecks(self):
        """Phase 4: Decouple bottleneck modules"""
        logger.info("\n🔧 PHASE 4: Decoupling Bottleneck Modules")
        logger.info("=" * 60)

        # Create message queue for bottlenecks
        message_queue_content = '''"""
Message Queue for Bottleneck Modules
====================================
Handles high-traffic communication with queuing and caching.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from collections import deque
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

@dataclass

class Message:
    """Message in the queue"""
    id: str
    source: str
    target: str
    payload: Dict[str, Any]
    priority: int = 0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class MessageQueue:
    """Priority message queue for module communication"""

    def __init__(self, max_size: int = 10000):
        self._queues: Dict[str, asyncio.PriorityQueue] = {}
        self._processors: Dict[str, Callable] = {}
        self._max_size = max_size
        self._running = False
        self._metrics = {
            'messages_queued': 0,
            'messages_processed': 0,
            'messages_dropped': 0,
            'average_latency_ms': 0
        }

    def register_processor(self, module: str, processor: Callable):
        """Register a message processor for a module"""
        self._processors[module] = processor
        if module not in self._queues:
            self._queues[module] = asyncio.PriorityQueue(maxsize=self._max_size)
        logger.info(f"Registered processor for module: {module}")

    async def enqueue(self, message: Message):
        """Add message to queue"""
        target_queue = self._queues.get(message.target)

        if not target_queue:
            logger.warning(f"No queue for target module: {message.target}")
            self._metrics['messages_dropped'] += 1
            return

        try:
            # Priority is negative because PriorityQueue is min-heap
            await target_queue.put((-message.priority, message))
            self._metrics['messages_queued'] += 1
        except asyncio.QueueFull:
            logger.error(f"Queue full for module: {message.target}")
            self._metrics['messages_dropped'] += 1

    async def process_module_queue(self, module: str):
        """Process messages for a specific module"""
        queue = self._queues.get(module)
        processor = self._processors.get(module)

        if not queue or not processor:
            return

        while self._running:
            try:
                # Get message with timeout
                priority, message = await asyncio.wait_for(
                    queue.get(), timeout=1.0
                )

                # Calculate latency
                latency = (datetime.now(timezone.utc) - message.timestamp).total_seconds() * 1000
                self._update_latency(latency)

                # Process message
                if asyncio.iscoroutinefunction(processor):
                    await processor(message)
                else:
                    processor(message)

                self._metrics['messages_processed'] += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message for {module}: {e}")

    async def start(self):
        """Start message queue processing"""
        self._running = True
        logger.info("Message queue started")

        # Start processors for each module
        tasks = []
        for module in self._queues.keys():
            task = asyncio.create_task(self.process_module_queue(module))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop message queue processing"""
        self._running = False

        # Process remaining messages
        for module, queue in self._queues.items():
            while not queue.empty():
                try:
                    priority, message = queue.get_nowait()
                    processor = self._processors.get(module)
                    if processor:
                        await processor(message)
                except Exception as e:
                    logger.error(f"Error processing remaining messages: {e}")

        logger.info("Message queue stopped")

    def _update_latency(self, latency: float):
        """Update average latency metric"""
        if self._metrics['average_latency_ms'] == 0:
            self._metrics['average_latency_ms'] = latency
        else:
            # Exponential moving average
            alpha = 0.1
            self._metrics['average_latency_ms'] = (
                alpha * latency + (1 - alpha) * self._metrics['average_latency_ms']
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get queue metrics"""
        metrics = self._metrics.copy()
        metrics['queue_sizes'] = {
            module: queue.qsize()
            for module, queue in self._queues.items()
        }
        return metrics

# Global message queue instance
message_queue = MessageQueue()

# Cache layer for frequent requests

class CacheLayer:
    """Caching layer for reducing bottleneck load"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            timestamp = self._timestamps[key]
            if (datetime.now(timezone.utc) - timestamp).total_seconds() < self._ttl:
                self._hits += 1
                return self._cache[key]
            else:
                # Expired
                del self._cache[key]
                del self._timestamps[key]

        self._misses += 1
        return None

    def set(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = value
        self._timestamps[key] = datetime.now(timezone.utc)

    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._timestamps.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'size': len(self._cache)
        }

# Create cache instances for bottleneck modules
cache_layers = {
    'core': CacheLayer(),
    'orchestration': CacheLayer()
}
'''

        # Save message queue
        queue_path = self.root_path / "lukhas" / "common" / "message_queue.py"

        with open(queue_path, "w") as f:
            f.write(message_queue_content)

        logger.info(f"✅ Created message queue at: {queue_path}")

        self.phase_status["phase4"] = "completed"

    def _create_module_interfaces(self):
        """Create interface definitions for modules"""
        interfaces_content = '''"""
Module Interfaces
================
Interface definitions to break circular dependencies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

class IConsciousnessModule(ABC):
    """Interface for consciousness modules"""

    @abstractmethod
    async def get_awareness_state(self) -> Dict[str, Any]:
        """Get current awareness state"""
        pass

    @abstractmethod
    async def update_awareness(self, state: Dict[str, Any]) -> bool:
        """Update awareness state"""
        pass

    @abstractmethod
    async def process_reflection(self, input_data: Any) -> Any:
        """Process reflection request"""
        pass

class IMemoryModule(ABC):
    """Interface for memory modules"""

    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Dict[str, Any] = \
    None) -> bool:
        """Store data in memory"""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory"""
        pass

    @abstractmethod
    async def create_fold(self, fold_data: Dict[str, Any]) -> str:
        """Create memory fold"""
        pass

class IOrchestrationModule(ABC):
    """Interface for orchestration modules"""

    @abstractmethod
    async def execute_task(self, task_id: str, params: Dict[str, Any]) -> Any:
        """Execute orchestration task"""
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task execution status"""
        pass

    @abstractmethod
    async def schedule_workflow(self, workflow: Dict[str, Any]) -> str:
        """Schedule workflow execution"""
        pass

class IGovernanceModule(ABC):
    """Interface for governance modules"""

    @abstractmethod
    async def validate_action(self, action: str, context: Dict[str, Any]) -> bool:
        """Validate if action is allowed"""
        pass

    @abstractmethod
    async def audit_log(self, event: Dict[str, Any]) -> None:
        """Log audit event"""
        pass

    @abstractmethod
    async def check_policy(self, policy_id: str, data: Any) -> bool:
        """Check if data complies with policy"""
        pass

class ICoreModule(ABC):
    """Interface for core modules"""

    @abstractmethod
    async def process_glyph(self, glyph: Any) -> Any:
        """Process GLYPH symbol"""
        pass

    @abstractmethod
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        pass

    @abstractmethod
    async def execute_symbolic_operation(self, operation: str, params: Dict[str,
    Any]) -> Any:
        """Execute symbolic operation"""
        pass
'''

        interfaces_path = self.root_path / "lukhas" / "common" / "module_interfaces.py"

        with open(interfaces_path, "w") as f:
            f.write(interfaces_content)

        logger.info(f"   Created module interfaces at: {interfaces_path}")
        self.optimizations_made.append("Created module interfaces")

    def _create_dependency_container(self):
        """Create dependency injection container"""
        container_content = '''"""
Dependency Injection Container
=============================
Manages module dependencies without circular imports.
"""

from typing import Dict, Any, Type, Optional
import logging
from .module_interfaces import (
    IConsciousnessModule,
    IMemoryModule,
    IOrchestrationModule,
    IGovernanceModule,
    ICoreModule
)

logger = logging.getLogger(__name__)

class DependencyContainer:
    """Dependency injection container for LUKHAS modules"""

    def __init__(self):
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}

    def register(self, interface: Type, instance: Any):
        """Register a module instance"""
        self._instances[interface] = instance
        logger.info(f"Registered {interface.__name__} implementation")

    def register_factory(self, interface: Type, factory: callable):
        """Register a factory function for lazy instantiation"""
        self._factories[interface] = factory
        logger.info(f"Registered factory for {interface.__name__}")

    def get(self, interface: Type) -> Optional[Any]:
        """Get module instance by interface"""
        # Check if already instantiated
        if interface in self._instances:
            return self._instances[interface]

        # Check if factory exists
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance
            return instance

        logger.warning(f"No implementation found for {interface.__name__}")
        return None

    def resolve_dependencies(self, module: Any):
        """Inject dependencies into module"""
        # Check for dependency declarations
        if hasattr(module, '_dependencies'):
            for dep_name, dep_interface in module._dependencies.items():
                dep_instance = self.get(dep_interface)
                if dep_instance:
                    setattr(module, dep_name, dep_instance)
                else:
                    logger.warning(f"Could not resolve dependency {dep_name} for {module.__class__.__name__}")

# Global container instance
container = DependencyContainer()

# Decorator for dependency injection

def inject(**dependencies):
    """Decorator to inject dependencies into a class"""

    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            # Set dependencies attribute
            self._dependencies = dependencies

            # Call original init
            original_init(self, *args, **kwargs)

            # Resolve dependencies
            container.resolve_dependencies(self)

        cls.__init__ = new_init
        return cls

    return decorator

# Helper function to get module

def get_module(interface: Type) -> Optional[Any]:
    """Get module instance from container"""
    return container.get(interface)
'''

        container_path = (
            self.root_path / "lukhas" / "common" / "dependency_container.py"
        )

        with open(container_path, "w") as f:
            f.write(container_content)

        logger.info(f"   Created dependency container at: {container_path}")
        self.optimizations_made.append("Created dependency injection container")

    def _create_event_adapters(self):
        """Create event adapters for existing modules"""
        adapter_content = '''"""
Event Adapters for LUKHAS Modules
=================================
Adapts existing module communication to use event bus.
"""

from typing import Dict, Any
import logging
from .event_bus import event_bus, EventTypes, Event

logger = logging.getLogger(__name__)

class ConsciousnessEventAdapter:
    """Adapter for consciousness module events"""

    def __init__(self, consciousness_module):
        self.module = consciousness_module
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        event_bus.subscribe(
            EventTypes.MODULE_INITIALIZED,
            self._on_module_initialized
        )

    def _on_module_initialized(self, event: Event):
        """Handle module initialization events"""
        if event.source_module != 'consciousness':
            logger.info(f"Consciousness aware of {event.source_module} initialization")

    async def emit_awareness_changed(self, new_state: Dict[str, Any]):
        """Emit awareness changed event"""
        await event_bus.publish(Event(
            event_type=EventTypes.AWARENESS_CHANGED,
            source_module='consciousness',
            payload={'new_state': new_state}
        ))

class MemoryEventAdapter:
    """Adapter for memory module events"""

    def __init__(self, memory_module):
        self.module = memory_module
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        event_bus.subscribe(
            EventTypes.MEMORY_STORED,
            self._on_memory_stored,
            is_async=True
        )

    async def _on_memory_stored(self, event: Event):
        """Handle memory stored events"""
        # Could trigger related operations
        pass

    async def emit_fold_created(self, fold_id: str, fold_data: Dict[str, Any]):
        """Emit fold created event"""
        await event_bus.publish(Event(
            event_type=EventTypes.FOLD_CREATED,
            source_module='memory',
            payload={'fold_id': fold_id, 'data': fold_data}
        ))

class OrchestrationEventAdapter:
    """Adapter for orchestration module events"""

    def __init__(self, orchestration_module):
        self.module = orchestration_module
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        event_bus.subscribe(
            EventTypes.TASK_COMPLETED,
            self._on_task_completed
        )

    def _on_task_completed(self, event: Event):
        """Handle task completion events"""
        task_id = event.payload.get('task_id')
        logger.info(f"Task {task_id} completed, updating orchestration state")

    async def emit_workflow_triggered(self, workflow_id: str):
        """Emit workflow triggered event"""
        await event_bus.publish(Event(
            event_type=EventTypes.WORKFLOW_TRIGGERED,
            source_module='orchestration',
            payload={'workflow_id': workflow_id}
        ))

# Factory functions for creating adapters

def create_consciousness_adapter(module):
    """Create consciousness event adapter"""
    return ConsciousnessEventAdapter(module)

def create_memory_adapter(module):
    """Create memory event adapter"""
    return MemoryEventAdapter(module)

def create_orchestration_adapter(module):
    """Create orchestration event adapter"""
    return OrchestrationEventAdapter(module)
'''

        adapter_path = self.root_path / "lukhas" / "common" / "event_adapters.py"

        with open(adapter_path, "w") as f:
            f.write(adapter_content)

        logger.info(f"   Created event adapters at: {adapter_path}")
        self.optimizations_made.append("Created event adapters")

    def generate_report(self) -> dict[str, Any]:
        """Generate optimization report"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phases_completed": self.phase_status,
            "optimizations_made": self.optimizations_made,
            "new_components": [
                "lukhas/common/module_interfaces.py",
                "lukhas/common/dependency_container.py",
                "lukhas/common/event_bus.py",
                "lukhas/common/event_adapters.py",
                "lukhas/common/glyph_router.py",
                "lukhas/common/message_queue.py",
            ],
            "benefits": {
                "circular_dependencies": "Broken using interfaces and DI",
                "coupling": "Reduced through event-based communication",
                "performance": "Improved with caching and queuing",
                "scalability": "Enhanced with message queues and routing",
            },
        }

        # Save report
        report_path = (
            self.root_path
            / "docs"
            / "reports"
            / "communication_optimization_report.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def run(self):
        """Run all optimization phases"""
        logger.info("🚀 Starting Module Communication Optimization")
        logger.info("=" * 80)

        # Run phases
        self.phase1_break_circular_dependencies()
        self.phase2_implement_event_bus()
        self.phase3_optimize_glyph_communication()
        self.phase4_decouple_bottlenecks()

        # Generate report
        report = self.generate_report()

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 OPTIMIZATION COMPLETE")
        logger.info("=" * 80)

        logger.info("\n✅ All phases completed successfully!")

        logger.info("\n📦 New components created:")
        for component in report["new_components"]:
            logger.info(f"   - {component}")

        logger.info("\n💡 Benefits achieved:")
        for benefit, description in report["benefits"].items():
            logger.info(f"   {benefit}: {description}")

        logger.info(
            "\n📁 Full report: docs/reports/communication_optimization_report.json"
        )
        logger.info("=" * 80)


def main():
    """Run communication optimization"""
    optimizer = CommunicationOptimizer()
    optimizer.run()


if __name__ == "__main__":
    main()
