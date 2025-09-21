"""
AsyncIO compatibility module for Python 3.9+
Provides asyncio.timeout equivalent for older Python versions.
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Optional, Any


if sys.version_info >= (3, 11):
    # Use native asyncio.timeout
    from asyncio import timeout
else:
    # Provide compatibility implementation
    @asynccontextmanager
    async def timeout(delay: Optional[float]):
        """Compatibility timeout context manager for Python 3.9+"""
        if delay is None:
            yield
            return

        try:
            async with asyncio.wait_for(asyncio.shield(asyncio.sleep(0)), timeout=delay):
                yield
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Operation timed out")


# Also provide a timeout function that works with asyncio.wait_for
async def wait_for_with_timeout(coro, timeout_seconds: Optional[float]):
    """Wait for coroutine with timeout, compatible across Python versions."""
    if timeout_seconds is None:
        return await coro

    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"Operation timed out after {timeout_seconds}s")