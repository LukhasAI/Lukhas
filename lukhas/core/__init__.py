"""
LUKHAS AI Core Module
Foundational systems for symbolic processing, GLYPH engine, and Trinity Framework
Trinity Framework: Identity, Consciousness, Guardian
"""

# Actor system imports
from .actor_system import Actor
from .actor_system import ActorRef
from .actor_system import ActorSystem
from .actor_system import AIAgentActor
from .actor_system import default_actor_system
from .actor_system import get_global_actor_system
from .core_wrapper import CoreStatus
from .core_wrapper import CoreWrapper
from .core_wrapper import GlyphResult
from .core_wrapper import SymbolicResult
from .core_wrapper import create_trinity_glyph
from .core_wrapper import encode_concept
from .core_wrapper import get_core
from .core_wrapper import get_core_status
from .distributed_tracing import AIAgentTracer
from .distributed_tracing import DistributedTracer
from .distributed_tracing import TraceCollector
from .distributed_tracing import TraceContext
from .distributed_tracing import TraceSpan
from .distributed_tracing import create_ai_tracer
from .distributed_tracing import get_global_collector
from .distributed_tracing import get_global_tracer

# Communication and coordination imports
from .efficient_communication import EfficientCommunicationFabric
from .efficient_communication import EnergyMonitor
from .efficient_communication import EventBus
from .efficient_communication import MessagePriority
from .efficient_communication import MessageRouter
from .efficient_communication import P2PChannel
from .efficient_communication import get_global_communication_fabric

# Event sourcing and tracing
from .event_sourcing import AIAgentAggregate
from .event_sourcing import Event
from .event_sourcing import EventReplayService
from .event_sourcing import EventSourcedAggregate
from .event_sourcing import EventStore
from .event_sourcing import get_global_event_store

# Supervision and oversight
from .supervisor_agent import SupervisorAgent
from .supervisor_agent import get_supervisor_agent

# Symbolic system imports
from .symbolism import MethylationModel
from .symbolism import SymbolicTag
from .symbolism import TagManager
from .symbolism import TagPermission
from .symbolism import TagScope
from .symbolism import get_methylation_model
from .symbolism import get_tag_manager

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
