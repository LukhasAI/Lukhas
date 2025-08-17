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
    from .bridges.quantum import QuantumConsciousnessBridge
except ImportError:
    pass

# Import engines
try:
    from .engines.expansion import ExpansionEngine
except ImportError:
    pass

__all__ = [
    "ConsciousnessCore",
    "ConsciousnessAPI",
    "MemoryConsciousnessBridge",
    "CoreConsciousnessBridge",
    "QuantumConsciousnessBridge",
    "ExpansionEngine",
]
