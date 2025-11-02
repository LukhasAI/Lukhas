"""
🎭 Common Decorators
===================
Reusable decorators for LUKHAS modules.
"""

import logging
import asyncio
import functools
import secrets
import time
from datetime import datetime, timezone
from typing import Callable, Optional, Union
from .exceptions import ModuleTimeoutError
from .logger import get_logger
                try:
                try:
            try:
            try:
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
                logger.error(f"Failed {func.__name__} after {duration:.3f}s: {type(e).__name__}: {e!s}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
