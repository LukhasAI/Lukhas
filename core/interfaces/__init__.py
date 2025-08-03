"""
LUKHAS AGI Interface Systems
===========================

This package contains all interface definitions, protocols, and registry
systems for the LUKHAS AGI ecosystem.

Components:
- gRPC API definitions (lukhas_pb2, lukhas_pb2_grpc)
- Awareness protocol interfaces
- Intelligence engine registry
- Additional protocol interfaces
"""

# Import protocol interfaces
from .protocols import (
    AwarenessAssessor,
    AwarenessInput,
    AwarenessOutput,
    AwarenessProtocolInterface,
    AwarenessType,
    DefaultAwarenessProtocol,
    ProtocolStatus,
    SessionContext,
    TierLevel,
    create_awareness_protocol,
    get_default_protocol,
)

# Import registry systems
from .registries import (
    EngineCapability,
    EngineInfo,
    EngineStatus,
    EngineType,
    HealthChecker,
    IntelligenceEngineRegistry,
    QueryFilter,
    RegistryConfig,
    RegistryEvent,
    create_capability,
    create_engine_info,
    get_global_registry,
)

# Interface Nodes - commented out due to missing module
# from .nodes import IntentNode, VoiceNode, NodeManager

__all__ = [
    # Awareness Protocol
    "AwarenessType",
    "TierLevel",
    "ProtocolStatus",
    "AwarenessInput",
    "AwarenessOutput",
    "SessionContext",
    "AwarenessAssessor",
    "AwarenessProtocolInterface",
    "DefaultAwarenessProtocol",
    "create_awareness_protocol",
    "get_default_protocol",
    # Intelligence Engine Registry
    "EngineType",
    "EngineStatus",
    "RegistryEvent",
    "EngineCapability",
    "EngineInfo",
    "RegistryConfig",
    "QueryFilter",
    "HealthChecker",
    "IntelligenceEngineRegistry",
    "get_global_registry",
    "create_engine_info",
    "create_capability",
    # Interface Nodes
    # "IntentNode",
    # "VoiceNode",
    # "NodeManager",
]
