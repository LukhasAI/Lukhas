"""Async utilities bridge."""
from __future__ import annotations

import asyncio
import importlib as _importlib
from typing import Awaitable, TypeVar

T = TypeVar("T")

try:
    _mod = _importlib.import_module("labs.async_utils")
    _candidate_await_with_timeout = _mod.await_with_timeout
except Exception:

    async def await_with_timeout(coro: Awaitable[T], timeout: float) -> T:
        """Wait for coroutine with timeout."""
        return await asyncio.wait_for(coro, timeout=timeout)
else:
    await_with_timeout = _candidate_await_with_timeout


try:
    _mod = _importlib.import_module("labs.async_utils")
    run_guardian_task = _mod.run_guardian_task
except Exception:

    async def run_guardian_task(task, *args, **kwargs):
        """Stub guardian task runner."""
        return await task(*args, **kwargs)


try:
    _mod = _importlib.import_module("labs.async_utils")
    run_with_retry = _mod.run_with_retry
except Exception:

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
