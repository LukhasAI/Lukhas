"""
Top-level orchestration module for LUKHAS AI

This module provides a top-level import for lukhas.orchestration
to ensure compatibility with existing import patterns.
"""

# Import specific components from lukhas.orchestration
try:
    from lukhas.orchestration import context_bus, kernel_bus
    from lukhas.orchestration.context_bus import build_context

    # Maintain backward compatibility
    __all__ = [
        "build_context",
        "kernel_bus",
        "context_bus",
    ]
except ImportError:
    # Fallback if lukhas.orchestration is not available
    __all__ = []