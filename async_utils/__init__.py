"""async_utils module.

We lazily proxy symbols from `labs.async_utils` to avoid static import-time
edges into `labs`. When a symbol is unavailable, a small stub fallback is
provided so callers (including tests) continue to function.
"""
import asyncio
import importlib
import types
from contextlib import contextmanager
from typing import Any, Awaitable, Callable, Dict, Generator, Optional

__all__ = []


def _load_labs_async_utils() -> Optional[types.ModuleType]:
    try:
        return importlib.import_module("labs.async_utils")
    except Exception:
        return None


# consciousness_context
_mod = _load_labs_async_utils()
if _mod is not None and hasattr(_mod, "consciousness_context"):
    consciousness_context = getattr(_mod, "consciousness_context")
else:
    @contextmanager
    def consciousness_context(*args: Any, **kwargs: Any) -> Generator[Dict[str, Any], None, None]:
        """Stub consciousness context."""
        yield {}
__all__.append("consciousness_context")


# await_with_timeout
_mod = _load_labs_async_utils()
if _mod is not None and hasattr(_mod, "await_with_timeout"):
    await_with_timeout = getattr(_mod, "await_with_timeout")
else:
    async def await_with_timeout(coro: Awaitable[Any], timeout: float) -> Any | None:
        """Stub timeout wrapper."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            return None
__all__.append("await_with_timeout")


# gather_with_error_handling
_mod = _load_labs_async_utils()
if _mod is not None and hasattr(_mod, "gather_with_error_handling"):
    gather_with_error_handling = getattr(_mod, "gather_with_error_handling")
else:
    async def gather_with_error_handling(*coros: Awaitable[Any], return_exceptions: bool = True) -> list[Any]:
        """Stub gather with error handling."""
        return await asyncio.gather(*coros, return_exceptions=return_exceptions)
__all__.append("gather_with_error_handling")


# consciousness_task
_mod = _load_labs_async_utils()
if _mod is not None and hasattr(_mod, "consciousness_task"):
    consciousness_task = getattr(_mod, "consciousness_task")
else:
    def consciousness_task(func: Callable[..., Any]) -> Callable[..., Any]:
        """Stub consciousness task decorator."""
        return func
__all__.append("consciousness_task")


# run_guardian_task
_mod = _load_labs_async_utils()
if _mod is not None and hasattr(_mod, "run_guardian_task"):
    run_guardian_task = getattr(_mod, "run_guardian_task")
else:
    async def run_guardian_task(task: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Stub guardian task runner."""
        return await task(*args, **kwargs)
__all__.append("run_guardian_task")


# run_with_retry
_mod = _load_labs_async_utils()
if _mod is not None and hasattr(_mod, "run_with_retry"):
    run_with_retry = getattr(_mod, "run_with_retry")
else:
    async def run_with_retry(coro: Callable[..., Awaitable[Any]], max_retries: int = 3, *args: Any, **kwargs: Any) -> Any | None:
        """Stub retry wrapper."""
        for attempt in range(max_retries):
            try:
                return await coro(*args, **kwargs)
            except Exception:
                if attempt == max_retries - 1:
                    raise
        return None
__all__.append("run_with_retry")
