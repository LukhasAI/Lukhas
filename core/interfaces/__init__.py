"""
Core Interfaces - Base classes and protocols for cognitive nodes.

Provides CognitiveNodeBase and ICognitiveNode interfaces.
"""
from __future__ import annotations

try:
    from labs.core.identity.interfaces import CognitiveNodeBase, ICognitiveNode
except Exception:
    # Fallback minimal definitions
    class CognitiveNodeBase:
        """Base class for cognitive nodes."""
        pass

    class ICognitiveNode:
        """Interface for cognitive nodes."""
        pass

__all__ = ["CognitiveNodeBase", "ICognitiveNode"]
