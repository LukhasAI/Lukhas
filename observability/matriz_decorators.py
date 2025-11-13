"""
Bridge module for observability.matriz_decorators
=================================================

Provides access to MATRIZ instrumentation decorators from lukhas_website.lukhas.observability.matriz_decorators.

This bridge enables imports like:
    from observability.matriz_decorators import instrument

MATRIZ Decorators:
- instrument: Decorator for adding MATRIZ instrumentation to functions

  Usage:
      @instrument("DECISION", label="guardian:drift", capability="guardian:drift:detect")
      def detect_drift(...):
          pass
"""

from __future__ import annotations

try:
    # Primary: lukhas_website production lane
    from lukhas_website.lukhas.observability.matriz_decorators import instrument
except ImportError:
    # Fallback: Create no-op decorator if MATRIZ not available
    def instrument(node_type=None, **kwargs):
        """No-op fallback decorator when MATRIZ is not available"""
        def decorator(func):
            return func
        return decorator

__all__ = ["instrument"]
