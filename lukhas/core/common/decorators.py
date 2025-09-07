"""
🎭 Common Decorators
===================
Reusable decorators for LUKHAS modules.
"""
import logging

log = logging.getLogger(__name__)
import streamlit as st

import asyncio
import functools
import secrets
import time
from datetime import datetime, timezone
from typing import Callable, Optional, Union

from .exceptions import ModuleTimeoutError
from .logger import get_logger

logger = get_logger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for each retry
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry

    Example:
        @retry(max_attempts=3, delay=1.0, exceptions=(ConnectionError,))
        async def fetch_data():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            attempt = 0
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:  # noqa: PERF203 # Intentional: retry pattern requires try-except in loop
                    last_exception = e

                    if attempt < max_attempts - 1:
                        if on_retry:
                            on_retry(e, attempt + 1)

                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__} after {type(e).__name__}: {e!s}"
                        )

                        # Add secure jitter to prevent thundering herd
                        jitter = secrets.randbelow(1000) / 2000.0  # 0.0 to 0.5
                        jittered_delay = current_delay * (0.5 + jitter)
                        await asyncio.sleep(jittered_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"Max retries ({max_attempts}) exceeded for {func.__name__}")

                    attempt += 1

            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:  # noqa: PERF203 # Intentional: retry pattern requires try-except in loop
                    last_exception = e

                    if attempt < max_attempts - 1:
                        if on_retry:
                            on_retry(e, attempt + 1)

                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__} after {type(e).__name__}: {e!s}"
                        )

                        # Add secure jitter
                        jitter = secrets.randbelow(1000) / 2000.0  # 0.0 to 0.5
                        jittered_delay = current_delay * (0.5 + jitter)
                        time.sleep(jittered_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"Max retries ({max_attempts}) exceeded for {func.__name__}")

                    attempt += 1

            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def with_timeout(timeout: float, error_message: Optional[str] = None) -> Callable:
    """
    Add timeout to async functions.

    Args:
        timeout: Timeout in seconds
        error_message: Optional custom error message

    Example:
        @with_timeout(30.0)
        async def process_data():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError as err:
                msg = error_message or f"{func.__name__} timed out after {timeout}s"
                logger.error(msg)
                raise ModuleTimeoutError(msg) from err

        # Only works with async functions
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"@with_timeout can only be used with async functions, but {func.__name__} is synchronous")

        return wrapper

    return decorator


def lukhas_tier_required(tier: Union[int, str], fallback: Optional[Callable] = None) -> Callable:
    """
    Require specific LUKHAS tier for function access.

    Args:
        tier: Required tier (1-5 or 'alpha', 'beta', 'gamma', 'delta', 'epsilon')
        fallback: Optional fallback function if tier not met

    Example:
        @lukhas_tier_required(3)

        def advanced_function():
            ...
    """
    # Convert tier names to numbers
    tier_map = {"alpha": 1, "beta": 2, "gamma": 3, "delta": 4, "epsilon": 5}

    required_tier = tier_map.get(tier.lower(), 5) if isinstance(tier, str) else tier

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get current tier from context or config
            current_tier = await _get_current_tier(args, kwargs)

            if current_tier >= required_tier:
                return await func(*args, **kwargs)
            else:
                logger.warning(
                    f"Access denied to {func.__name__}: requires tier {required_tier}, current tier {current_tier}"
                )
                if fallback:
                    return await fallback(*args, **kwargs)
                else:
                    raise PermissionError(f"Function {func.__name__} requires LUKHAS tier {required_tier}")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get current tier from context or config
            current_tier = _get_current_tier_sync(args, kwargs)

            if current_tier >= required_tier:
                return func(*args, **kwargs)
            else:
                logger.warning(
                    f"Access denied to {func.__name__}: requires tier {required_tier}, current tier {current_tier}"
                )
                if fallback:
                    return fallback(*args, **kwargs)
                else:
                    raise PermissionError(f"Function {func.__name__} requires LUKHAS tier {required_tier}")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def _get_current_tier(args, kwargs) -> int:
    """Get current LUKHAS tier from context"""
    # Check if first argument has tier attribute (self.tier)
    if args and hasattr(args[0], "tier"):
        return args[0].tier

    # Check kwargs for tier
    if "tier" in kwargs:
        return kwargs["tier"]

    # Check for context in kwargs
    if "context" in kwargs and isinstance(kwargs["context"], dict):
        return kwargs["context"].get("tier", 1)

    # Default to tier 1
    return 1


def _get_current_tier_sync(args, kwargs) -> int:
    """Synchronous version of tier check"""
    # Same logic as async version
    if args and hasattr(args[0], "tier"):
        return args[0].tier
    if "tier" in kwargs:
        return kwargs["tier"]
    if "context" in kwargs and isinstance(kwargs["context"], dict):
        return kwargs["context"].get("tier", 1)
    return 1


def cached(ttl: Optional[float] = None, key_func: Optional[Callable] = None) -> Callable:
    """
    Simple caching decorator with TTL support.

    Args:
        ttl: Time to live in seconds (None for no expiration)
        key_func: Function to generate cache key from arguments

    Example:
        @cached(ttl=60.0)
        async def expensive_calculation(x, y):
            ...
    """

    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}

        def default_key_func(*args, **kwargs):
            # Simple key generation
            return str(args) + str(sorted(kwargs.items()))

        cache_key_func = key_func or default_key_func

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = cache_key_func(*args, **kwargs)

            # Check cache
            if key in cache and (ttl is None or (datetime.now(timezone.utc) - cache_times[key]).total_seconds() < ttl):
                return cache[key]

            # Cache miss or expired
            result = await func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = datetime.now(timezone.utc)

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = cache_key_func(*args, **kwargs)

            # Check cache
            if key in cache and (ttl is None or (datetime.now(timezone.utc) - cache_times[key]).total_seconds() < ttl):
                return cache[key]

            # Cache miss or expired
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = datetime.now(timezone.utc)

            return result

        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.clear_cache = lambda: (cache.clear(), cache_times.clear())

        return wrapper

    return decorator


def log_execution(
    level: str = "INFO",
    include_args: bool = False,
    include_result: bool = False,
) -> Callable:
    """
    Log function execution details.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        include_args: Include function arguments in log
        include_result: Include function result in log
    """

    def decorator(func: Callable) -> Callable:
        log_func = getattr(logger, level.lower(), logger.info)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            # Build log message
            msg_parts = [f"Executing {func.__name__}"]
            if include_args:
                msg_parts.append(f"args={args}, kwargs={kwargs}")

            log_func(" - ".join(msg_parts))

            try:
                result = await func(*args, **kwargs)

                # Log completion
                duration = time.time() - start_time
                completion_parts = [
                    f"Completed {func.__name__}",
                    f"duration={duration:.3f}s",
                ]
                if include_result:
                    completion_parts.append(f"result={result}")

                log_func(" - ".join(completion_parts))

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {duration:.3f}s: {type(e}.__name__}: {e!s}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            # Build log message
            msg_parts = [f"Executing {func.__name__}"]
            if include_args:
                msg_parts.append(f"args={args}, kwargs={kwargs}")

            log_func(" - ".join(msg_parts))

            try:
                result = func(*args, **kwargs)

                # Log completion
                duration = time.time() - start_time
                completion_parts = [
                    f"Completed {func.__name__}",
                    f"duration={duration:.3f}s",
                ]
                if include_result:
                    completion_parts.append(f"result={result}")

                log_func(" - ".join(completion_parts))

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {duration:.3f}s: {type(e}.__name__}: {e!s}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
