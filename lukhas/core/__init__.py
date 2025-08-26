"""
LUKHAS AI Core Module
Foundational systems for symbolic processing, GLYPH engine, and Trinity Framework
Trinity Framework: Identity, Consciousness, Guardian
"""

# Actor system imports
from .actor_system import (
    Actor,
    ActorRef,
    ActorSystem,
    AIAgentActor,
    default_actor_system,
    get_global_actor_system,
)
from .core_wrapper import (
    CoreStatus,
    CoreWrapper,
    GlyphResult,
    SymbolicResult,
    create_trinity_glyph,
    encode_concept,
    get_core,
    get_core_status,
)
from .distributed_tracing import (
    AIAgentTracer,
    DistributedTracer,
    TraceCollector,
    TraceContext,
    TraceSpan,
    create_ai_tracer,
    get_global_collector,
    get_global_tracer,
)

# Communication and coordination imports
from .efficient_communication import (
    EfficientCommunicationFabric,
    EnergyMonitor,
    EventBus,
    MessagePriority,
    MessageRouter,
    P2PChannel,
    get_global_communication_fabric,
)

# Event sourcing and tracing
from .event_sourcing import (
    AIAgentAggregate,
    Event,
    EventReplayService,
    EventSourcedAggregate,
    EventStore,
    get_global_event_store,
)

# Supervision and oversight
from .supervisor_agent import (
    SupervisorAgent,
    get_supervisor_agent,
)

# Symbolic system imports
from .symbolism import (
    MethylationModel,
    SymbolicTag,
    TagManager,
    TagPermission,
    TagScope,
    get_methylation_model,
    get_tag_manager,
)

# Version and module info
__version__ = "2.0.0"
__module_name__ = "core"
__description__ = "LUKHAS AI foundational systems - GLYPH engine, symbolic processing, Trinity Framework"

# Trinity Framework symbols
TRINITY_SYMBOLS = {
    "identity": "⚛️",
    "consciousness": "🧠",
    "guardian": "🛡️",
    "framework": "⚛️🧠🛡️"
}

# Export public interface
__all__ = [
    # Core wrapper exports
    "CoreWrapper",
    "GlyphResult",
    "SymbolicResult",
    "CoreStatus",
    "get_core",
    "encode_concept",
    "create_trinity_glyph",
    "get_core_status",
    "TRINITY_SYMBOLS",
    # Actor system exports
    "ActorRef",
    "ActorSystem",
    "Actor",
    "AIAgentActor",
    "get_global_actor_system",
    "default_actor_system",
    # Communication system exports
    "EfficientCommunicationFabric",
    "MessageRouter",
    "EventBus",
    "P2PChannel",
    "EnergyMonitor",
    "MessagePriority",
    "get_global_communication_fabric",
    # Supervision exports
    "SupervisorAgent",
    "get_supervisor_agent",
    # Symbolic system exports
    "TagScope",
    "TagPermission",
    "MethylationModel",
    "SymbolicTag",
    "TagManager",
    "get_tag_manager",
    "get_methylation_model",
    # Event sourcing exports
    "Event",
    "EventStore",
    "EventSourcedAggregate",
    "AIAgentAggregate",
    "EventReplayService",
    "get_global_event_store",
    # Distributed tracing exports
    "TraceSpan",
    "TraceContext",
    "TraceCollector",
    "DistributedTracer",
    "AIAgentTracer",
    "get_global_collector",
    "get_global_tracer",
    "create_ai_tracer",
]
