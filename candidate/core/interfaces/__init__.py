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
import lukhas_pb2
import streamlit as st

from .core_interface import CoreInterface, get_module as get_core_module, register_module as register_core_module

# Import dependency injection system
from .dependency_injection import (
    LazyProxy,
    ServiceLocator,
    ServiceRegistry,
    clear_registry,
    consciousness_service,
    get_by_interface,
    get_service,
    guardian_service,
    inject,
    lazy_service,
    memory_service,
    orchestration_service,
    register_factory,
    register_interface,
    register_service,
)
from .encrypted_perception_interface import (
    Encrypted_PerceptionInterface,
    get_module as get_encrypted_perception_module,
    register_module as register_encrypted_perception_module,
)

# Import interface modules for circular dependency resolution
from .memory_interface import (
    MemoryInterface,
    get_module as get_memory_module,
    register_module as register_memory_module,
)
from .moral_alignment_interface import (
    Moral_AlignmentInterface,
    get_module as get_moral_alignment_module,
    register_module as register_moral_alignment_module,
)

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
    # Dependency Injection
    "ServiceRegistry",
    "ServiceLocator",
    "LazyProxy",
    "inject",
    "register_service",
    "register_factory",
    "register_interface",
    "get_service",
    "get_by_interface",
    "clear_registry",
    "lazy_service",
    "memory_service",
    "consciousness_service",
    "guardian_service",
    "orchestration_service",
    # Interface Modules
    "MemoryInterface",
    "CoreInterface",
    "Encrypted_PerceptionInterface",
    "Moral_AlignmentInterface",
    "register_memory_module",
    "get_memory_module",
    "register_core_module",
    "get_core_module",
    "register_encrypted_perception_module",
    "get_encrypted_perception_module",
    "register_moral_alignment_module",
    "get_moral_alignment_module",
    # Interface Nodes
    # "IntentNode",
    # "VoiceNode",
    # "NodeManager",
]
