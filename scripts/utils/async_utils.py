"""Async utilities bridge."""
from __future__ import annotations

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")

try:
    from labs.async_utils import await_with_timeout as _candidate_await_with_timeout
except ImportError:

    async def await_with_timeout(coro: Awaitable[T], timeout: float) -> T:
        """Wait for coroutine with timeout."""
        return await asyncio.wait_for(coro, timeout=timeout)
else:
    await_with_timeout = _candidate_await_with_timeout


try:
    from labs.async_utils import run_guardian_task
except ImportError:

    async def run_guardian_task(task, *args, **kwargs):
        """Stub guardian task runner."""
        return await task(*args, **kwargs)


try:
    from labs.async_utils import run_with_retry
except ImportError:

    async def run_with_retry(coro, max_retries: int = 3, *args, **kwargs):
        """Stub retry wrapper."""
        for attempt in range(max_retries):
            try:
                return await coro(*args, **kwargs)
            except Exception:
                if attempt == max_retries - 1:
                    raise
        return None


__all__ = ["await_with_timeout", "run_guardian_task", "run_with_retry"]
