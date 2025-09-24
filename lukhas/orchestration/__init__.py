"""
LUKHAS AI Orchestration Module - Phase 4 Complete
Constellation Framework: ⚛️🧠🛡️

Complete orchestration system with externalized routing, health monitoring,
context preservation, A/B testing, and hot-reload capabilities.

Phase 4 Implementation v2.0.0
- Externalized routing configuration with hot-reload
- Health-aware routing strategies
- Context preservation across hops
- Circuit breaker patterns
- A/B testing framework
- Admin preview API
- Comprehensive observability
"""

import streamlit as st

# Import context bus components
from .context_bus import build_context
from .kernel_bus import (
    CONTEXT_BUS_ACTIVE,
    EventPriority,
    KernelBus,
    emit,
    get_kernel_bus,
    subscribe,
)

# Import O.2 Orchestration Core components
from .multi_ai_router import (
    AIProvider,
    AIModel,
    AIResponse,
    ConsensusType,
    ConsensusResult,
    MultiAIRouter,
    RoutingRequest,
    get_multi_ai_router,
    route_multi_ai_request,
)

# Import Phase 4 Externalized Orchestration components
from .routing_config import (
    RoutingStrategy,
    RoutingConfiguration,
    RoutingRule,
    HealthStatus,
    get_routing_config_manager,
    get_routing_configuration,
)

from .routing_strategies import (
    RoutingContext,
    RoutingResult,
    get_routing_engine,
)

from .health_monitor import (
    HealthMonitor,
    ProviderHealth,
    get_health_monitor,
    get_provider_health_status,
)

from .context_preservation import (
    ContextType,
    CompressionLevel,
    get_context_preservation_engine,
)

from .externalized_orchestrator import (
    ExternalizedOrchestrator,
    OrchestrationRequest,
    OrchestrationResponse,
    RequestType,
    get_externalized_orchestrator,
    orchestrate_request,
)

from .api import router as orchestration_router

_orchestration_branding_available = False
try:
    from lukhas.branding_bridge import (
        BrandContext,
        get_brand_voice,
        get_constellation_context,
        normalize_output_text,
        validate_output,
    )

    _orchestration_branding_available = True
except ImportError:
    # Keep default False if branding bridge not available
    pass

# Public constant
ORCHESTRATION_BRANDING_AVAILABLE = _orchestration_branding_available

# Alias for backward compatibility
OrchestrationHub = KernelBus

__all__ = [
    # Legacy context bus
    "CONTEXT_BUS_ACTIVE",
    "ORCHESTRATION_BRANDING_AVAILABLE",
    "BrandContext",
    "EventPriority",
    "KernelBus",
    "OrchestrationHub",
    "build_context",
    "emit",
    "get_brand_voice",
    "get_constellation_context",
    "get_kernel_bus",
    "normalize_output_text",
    "subscribe",
    "validate_output",
    # O.2 Orchestration Core
    "AIProvider",
    "AIModel",
    "AIResponse",
    "ConsensusType",
    "ConsensusResult",
    "MultiAIRouter",
    "RoutingRequest",
    "get_multi_ai_router",
    "route_multi_ai_request",
    "orchestration_router",
    # Phase 4 Externalized Orchestration
    "RoutingStrategy",
    "RoutingConfiguration",
    "RoutingRule",
    "RoutingContext",
    "RoutingResult",
    "HealthStatus",
    "HealthMonitor",
    "ProviderHealth",
    "ContextType",
    "CompressionLevel",
    "ExternalizedOrchestrator",
    "OrchestrationRequest",
    "OrchestrationResponse",
    "RequestType",
    "get_routing_config_manager",
    "get_routing_configuration",
    "get_routing_engine",
    "get_health_monitor",
    "get_provider_health_status",
    "get_context_preservation_engine",
    "get_externalized_orchestrator",
    "orchestrate_request",
]
