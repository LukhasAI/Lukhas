"""
LUKHAS AI Consolidated Consciousness Module

This module consolidates all consciousness-related components:
- Core consciousness logic
- API interfaces
- Bridge modules
- Processing engines
- Consciousness layers
- Stream processors
- Colony systems
"""

from typing import Optional

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

# Import core components
try:
    from .core import ConsciousnessCore
except ImportError:
    ConsciousnessCore = None

# Import API components
try:
    from .api.core import ConsciousnessAPI
except ImportError:
    ConsciousnessAPI = None

# Import bridges
try:
    from .bridges.memory import MemoryConsciousnessBridge
    from .bridges.core import CoreConsciousnessBridge
    from .bridges.quantum import QIConsciousnessBridge
except ImportError:
    pass

# Import engines
try:
    from .engines.expansion import ExpansionEngine
except ImportError:
    pass

# Import LUKHAS AI branding system for consciousness outputs
try:
    from lukhas.branding_bridge import (
        get_brand_voice, get_trinity_context, BrandContext
    )
    CONSCIOUSNESS_BRANDING_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_BRANDING_AVAILABLE = False

__all__ = [
    "ConsciousnessCore",
    "ConsciousnessAPI",
    "MemoryConsciousnessBridge",
    "CoreConsciousnessBridge",
    "QIConsciousnessBridge",
    "ExpansionEngine",
    # Branding integration
    "get_brand_voice",
    "get_trinity_context",
    "BrandContext",
    "CONSCIOUSNESS_BRANDING_AVAILABLE",
]
