"""
Top-level orchestration module for LUKHAS AI

This module provides a top-level import for orchestration
to ensure compatibility with existing import patterns.
"""

# Import specific components from orchestration
try:
    from orchestration import context_bus, kernel_bus
    from orchestration.context_bus import build_context

    # Maintain backward compatibility
    __all__ = [
        "build_context",
        "context_bus",
        "kernel_bus",
    ]
except ImportError:
    # Fallback if orchestration is not available
    __all__ = []
