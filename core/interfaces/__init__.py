"""
Core Interfaces - Base classes and protocols for cognitive nodes.

Provides CognitiveNodeBase and ICognitiveNode interfaces.
"""
from __future__ import annotations

# Fallback minimal definitions (used if labs not available)
class CognitiveNodeBase:
    """Base class for cognitive nodes."""
    pass

class ICognitiveNode:
    """Interface for cognitive nodes."""
    pass

# Attempt to load labs interfaces dynamically (avoids lane violation)
try:
    import importlib
    labs_interfaces = importlib.import_module("labs.core.identity.interfaces")
    CognitiveNodeBase = labs_interfaces.CognitiveNodeBase
    ICognitiveNode = labs_interfaces.ICognitiveNode
except Exception:
    # Keep fallback definitions
    pass

__all__ = ["CognitiveNodeBase", "ICognitiveNode"]
