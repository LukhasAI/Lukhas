"""lukhas.async_utils module."""

__all__ = []

# Add consciousness_context for test compatibility
try:
    from candidate.async_utils import consciousness_context
    __all__.append("consciousness_context")
except ImportError:
    # Stub context manager
    from contextlib import contextmanager
    @contextmanager
    def consciousness_context(*args, **kwargs):
        """Stub consciousness context."""
        yield {}
    __all__.append("consciousness_context")
