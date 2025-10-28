"""
Top-level orchestration module for LUKHAS AI

This module provides a top-level import for orchestration
to ensure compatibility with existing import patterns.
"""

# Import specific components from orchestration
try:
    from orchestration.context_bus import build_context

    from orchestration import context_bus, kernel_bus

    # Maintain backward compatibility
    __all__ = [
        "build_context",
        "kernel_bus",
        "context_bus",
    ]
except ImportError:
    # Fallback if orchestration is not available
    __all__ = []
