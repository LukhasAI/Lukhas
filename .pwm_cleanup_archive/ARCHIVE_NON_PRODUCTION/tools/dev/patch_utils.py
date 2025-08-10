"""Utility decorators for development patches."""

import sys
from functools import wraps

import structlog

log = structlog.get_logger(__name__)


def temporary_patch(func):
    """Decorator for temporary compatibility patches."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        module = sys.modules.get(func.__module__)
        compat = getattr(module, "compat_mode", True)
        if not compat:
            log.debug("Temporary patch disabled", function=func.__name__)
            raise NotImplementedError(
                f"{func.__name__} disabled with compat_mode=False"
            )
        return func(*args, **kwargs)

    wrapper._temporary_patch = True
    return wrapper
