"""
LUKHAS AI Orchestration Module
Trinity Framework: ⚛️🧠🛡️

Orchestration system with integrated branding compliance for
multi-agent coordination and Trinity Framework decision making.
"""

# Import LUKHAS AI branding system for orchestration compliance
try:
    from lukhas.branding_bridge import (
        get_brand_voice, get_trinity_context, validate_output,
        BrandContext, normalize_output_text
    )
    ORCHESTRATION_BRANDING_AVAILABLE = True
except ImportError:
    ORCHESTRATION_BRANDING_AVAILABLE = False

# Import context bus components
from .context_bus import build_context
from .kernel_bus import (
    KernelBus,
    EventPriority,
    get_kernel_bus,
    emit,
    subscribe,
    CONTEXT_BUS_ACTIVE
)

__all__ = [
    # Context bus
    "build_context",
    "KernelBus",
    "EventPriority",
    "get_kernel_bus",
    "emit",
    "subscribe",
    "CONTEXT_BUS_ACTIVE",
    # Branding integration
    "get_brand_voice",
    "get_trinity_context", 
    "validate_output",
    "BrandContext",
    "normalize_output_text",
    "ORCHESTRATION_BRANDING_AVAILABLE",
]
