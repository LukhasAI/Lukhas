"""
LUKHAS AI Orchestration Module
Trinity Framework: ⚛️🧠🛡️

Orchestration system with integrated branding compliance for
multi-agent coordination and Trinity Framework decision making.
"""

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
]
