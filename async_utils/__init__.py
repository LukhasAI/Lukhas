"""async_utils module."""

import importlib as _importlib
import asyncio
from contextlib import contextmanager

__all__ = []

# Add consciousness_context for test compatibility
try:
    _mod = _importlib.import_module("labs.async_utils")
    consciousness_context = getattr(_mod, "consciousness_context")
    __all__.append("consciousness_context")
except Exception:
    # Stub context manager
    @contextmanager
    def consciousness_context(*args, **kwargs):
        """Stub consciousness context."""
        yield {}

    __all__.append("consciousness_context")

# Add await_with_timeout for test compatibility
try:
    _mod = _importlib.import_module("labs.async_utils")
    await_with_timeout = getattr(_mod, "await_with_timeout")
    __all__.append("await_with_timeout")
except Exception:
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
    _mod = _importlib.import_module("labs.async_utils")
    gather_with_error_handling = getattr(_mod, "gather_with_error_handling")
    __all__.append("gather_with_error_handling")
except Exception:

    async def gather_with_error_handling(*coros, return_exceptions=True):
        """Stub gather with error handling."""
        return await asyncio.gather(*coros, return_exceptions=return_exceptions)

    __all__.append("gather_with_error_handling")

# Add consciousness_task for test compatibility
try:
    _mod = _importlib.import_module("labs.async_utils")
    consciousness_task = getattr(_mod, "consciousness_task")
    __all__.append("consciousness_task")
except Exception:

    def consciousness_task(func):
        """Stub consciousness task decorator."""
        return func

    __all__.append("consciousness_task")

# Add run_guardian_task for test compatibility
try:
    _mod = _importlib.import_module("labs.async_utils")
    run_guardian_task = getattr(_mod, "run_guardian_task")
    __all__.append("run_guardian_task")
except Exception:

    async def run_guardian_task(task, *args, **kwargs):
        """Stub guardian task runner."""
        return await task(*args, **kwargs)

    __all__.append("run_guardian_task")

# Add run_with_retry for test compatibility
try:
    _mod = _importlib.import_module("labs.async_utils")
    run_with_retry = getattr(_mod, "run_with_retry")
    __all__.append("run_with_retry")
except Exception:

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
