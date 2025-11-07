"""Bridge for `core.reliability.circuit_breaker`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.core.reliability.circuit_breaker
  2) candidate.core.reliability.circuit_breaker
  3) core.reliability.circuit_breaker

Graceful fallback to stubs if no backend available.
"""

from __future__ import annotations

import asyncio
from importlib import import_module
from typing import List

__all__: list[str] = [
    "CircuitBreaker",
    "circuit_breaker",
    "get_circuit_health",
]


def _try(n: str):
    try:
        mod = import_module(n)
    except Exception:
        return None
    if mod.__name__ == __name__:
        return None
    return mod


_CANDIDATES = (
    "lukhas_website.core.reliability.circuit_breaker",
    "labs.core.reliability.circuit_breaker",
    "core.reliability.circuit_breaker",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if not _m:
        continue
    _SRC = _m
    for _k in dir(_m):
        if _k.startswith("_"):
            continue
        globals()[_k] = getattr(_m, _k)
        if _k not in __all__:
            __all__.append(_k)
    break


class _CircuitBreakerStub:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.state = "closed"

    def __call__(self, func):
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            return async_wrapper

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def record_success(self):
        self.state = "closed"

    def record_failure(self):
        self.state = "open"


def circuit_breaker(name: str, **kwargs):  # type: ignore[misc]
    if _SRC and hasattr(_SRC, "circuit_breaker"):
        return _SRC.circuit_breaker(name, **kwargs)
    return _CircuitBreakerStub(name, **kwargs)


def get_circuit_health():
    if _SRC and hasattr(_SRC, "get_circuit_health"):
        return _SRC.get_circuit_health()
    return {"state": "unknown"}


if "CircuitBreaker" not in globals():
    CircuitBreaker = _CircuitBreakerStub  # type: ignore
