"""
LUKHAS AI Orchestration Module
Trinity Framework: ⚛️🧠🛡️

Orchestration system with integrated branding compliance for
multi-agent coordination and Trinity Framework decision making.
"""

# Import LUKHAS AI branding system for orchestration compliance
try:
    from lukhas.branding_bridge import (
        BrandContext,
        get_brand_voice,
        get_constellation_context,
        normalize_output_text,
        validate_output,
    )

    ORCHESTRATION_BRANDING_AVAILABLE = True
except ImportError:
    ORCHESTRATION_BRANDING_AVAILABLE = False

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

# Alias for backward compatibility
OrchestrationHub = KernelBus

__all__ = [
    "CONTEXT_BUS_ACTIVE",
    "ORCHESTRATION_BRANDING_AVAILABLE",
    "BrandContext",
    "EventPriority",
    "KernelBus",
    "OrchestrationHub",  # Alias
    # Context bus
    "build_context",
    "emit",
    # Branding integration
    "get_brand_voice",
    "get_kernel_bus",
    "get_constellation_context",
    "normalize_output_text",
    "subscribe",
    "validate_output",
]
