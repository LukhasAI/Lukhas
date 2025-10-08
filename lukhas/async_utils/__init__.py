"""lukhas.async_utils module."""
import asyncio
from contextlib import contextmanager

__all__ = []

# Add consciousness_context for test compatibility
try:
    from candidate.async_utils import consciousness_context
    __all__.append("consciousness_context")
except ImportError:
    # Stub context manager
    @contextmanager
    def consciousness_context(*args, **kwargs):
        """Stub consciousness context."""
        yield {}
    __all__.append("consciousness_context")

# Add await_with_timeout for test compatibility
try:
    from candidate.async_utils import await_with_timeout
    __all__.append("await_with_timeout")
except ImportError:
    # Stub async timeout wrapper
    async def await_with_timeout(coro, timeout: float):
        """Stub timeout wrapper."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            return None
    __all__.append("await_with_timeout")
