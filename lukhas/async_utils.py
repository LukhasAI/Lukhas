"""Async utilities bridge."""
from __future__ import annotations
import asyncio
from typing import TypeVar, Awaitable

T = TypeVar("T")

async def await_with_timeout(coro: Awaitable[T], timeout: float) -> T:
    """Wait for coroutine with timeout."""
    return await asyncio.wait_for(coro, timeout=timeout)

__all__ = ["await_with_timeout"]
