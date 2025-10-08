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

# Add gather_with_error_handling for test compatibility
try:
    from candidate.async_utils import gather_with_error_handling
    __all__.append("gather_with_error_handling")
except ImportError:
    async def gather_with_error_handling(*coros, return_exceptions=True):
        """Stub gather with error handling."""
        return await asyncio.gather(*coros, return_exceptions=return_exceptions)
    __all__.append("gather_with_error_handling")

# Add consciousness_task for test compatibility
try:
    from candidate.async_utils import consciousness_task
    __all__.append("consciousness_task")
except ImportError:
    def consciousness_task(func):
        """Stub consciousness task decorator."""
        return func
    __all__.append("consciousness_task")

# Add run_guardian_task for test compatibility
try:
    from candidate.async_utils import run_guardian_task  # noqa: F401
    __all__.append("run_guardian_task")
except ImportError:
    async def run_guardian_task(task, *args, **kwargs):
        """Stub guardian task runner."""
        return await task(*args, **kwargs)
    __all__.append("run_guardian_task")

# Add run_with_retry for test compatibility
try:
    from candidate.async_utils import run_with_retry  # noqa: F401
    __all__.append("run_with_retry")
except ImportError:
    async def run_with_retry(coro, max_retries=3, *args, **kwargs):
        """Stub retry wrapper."""
        for attempt in range(max_retries):
            try:
                return await coro(*args, **kwargs)
            except Exception:
                if attempt == max_retries - 1:
                    raise
        return None
    __all__.append("run_with_retry")
