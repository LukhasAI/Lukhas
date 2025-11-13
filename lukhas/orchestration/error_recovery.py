"""
Orchestrator Error Recovery

This module provides a suite of tools for handling errors in the LUKHAS orchestration
layer. It includes mechanisms for retrying failed operations, preventing cascading
failures with circuit breakers, and providing fallback handlers for graceful
degradation.
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Type, Union
from collections.abc import Coroutine


class CircuitBreaker:
    """
    An asynchronous circuit breaker to prevent repeated calls to a failing service.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        name: str = "CircuitBreaker",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    async def __aenter__(self):
        if self.state == "open":
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise RuntimeError(f"{self.name} is open")
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        if exc_type:
            if isinstance(exc_val, asyncio.CancelledError):
                raise
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.last_failure_time = time.monotonic()
        else:
            self.state = "closed"
            self.failure_count = 0


def retry(
    retries: int = 3,
    backoff: float = 0.5,
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
):
    """
    An asynchronous retry decorator with exponential backoff.
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if isinstance(e, asyncio.CancelledError):
                        raise
                    attempt += 1
                    if attempt >= retries:
                        raise
                    sleep_time = backoff * (2 ** (attempt - 1))
                    await asyncio.sleep(sleep_time)

        return wrapper

    return decorator


def fallback(
    fallback_handler: Callable[..., Coroutine[Any, Any, Any]],
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
):
    """
    A decorator to provide a fallback handler for a failing function.
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                if isinstance(e, asyncio.CancelledError):
                    raise
                return await fallback_handler(*args, **kwargs)

        return wrapper

    return decorator
