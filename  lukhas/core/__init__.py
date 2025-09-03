"""
LUKHAS AI Core Module
Foundational systems for symbolic processing, GLYPH engine, and Trinity Framework
Trinity Framework: Identity, Consciousness, Guardian
"""

# ΛTAG: glyph_export
from importlib import import_module as _import_module

glyph = _import_module(".common.glyph", __name__)

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
from .supervisor_agent import SupervisorAgent, get_supervisor_agent

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
    "framework": "⚛️🧠🛡️",
}

# Export public interface
__all__ = [
    "TRINITY_SYMBOLS",
    "AIAgentActor",
    "AIAgentAggregate",
    "AIAgentTracer",
    "Actor",
    # Actor system exports
    "ActorRef",
    "ActorSystem",
    "CoreStatus",
    # Core wrapper exports
    "CoreWrapper",
    "DistributedTracer",
    # Communication system exports
    "EfficientCommunicationFabric",
    "EnergyMonitor",
    # Event sourcing exports
    "Event",
    "EventBus",
    "EventReplayService",
    "EventSourcedAggregate",
    "EventStore",
    "GlyphResult",
    "MessagePriority",
    "MessageRouter",
    "MethylationModel",
    "P2PChannel",
    # Supervision exports
    "SupervisorAgent",
    "SymbolicResult",
    "SymbolicTag",
    "TagManager",
    "TagPermission",
    # Symbolic system exports
    "TagScope",
    "TraceCollector",
    "TraceContext",
    # Distributed tracing exports
    "TraceSpan",
    "create_ai_tracer",
    "create_trinity_glyph",
    "default_actor_system",
    "encode_concept",
    "get_core",
    "get_core_status",
    "get_global_actor_system",
    "get_global_collector",
    "get_global_communication_fabric",
    "get_global_event_store",
    "get_global_tracer",
    "get_methylation_model",
    "get_supervisor_agent",
    "get_tag_manager",
    "glyph",
]
