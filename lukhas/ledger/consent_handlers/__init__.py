"""Bridge for `lukhas.ledger.consent_handlers`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.lukhas.ledger.consent_handlers
  2) candidate.lukhas.ledger.consent_handlers
  3) ledger.consent_handlers

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = ["IdempotentConsentHandler", "IdempotentTraceHandler"]


def _try(name: str):
    try:
        mod = import_module(name)
    except Exception:
        return None
    if mod.__name__ == __name__:
        return None
    return mod


_CANDIDATES = (
    "lukhas_website.lukhas.ledger.consent_handlers",
    "labs.ledger.consent_handlers",
    "lukhas.ledger.consent_handlers",
)

_SRC = None
for _cand in _CANDIDATES:
    _mod = _try(_cand)
    if not _mod:
        continue
    _SRC = _mod
    for name in dir(_mod):
        if name.startswith("_"):
            continue
        globals()[name] = getattr(_mod, name)
        if name not in __all__:
            __all__.append(name)
    break


if "IdempotentConsentHandler" not in globals():

    class IdempotentConsentHandler:  # type: ignore[misc]
        def handle(self, event):
            return event


if "IdempotentTraceHandler" not in globals():

    class IdempotentTraceHandler:  # type: ignore[misc]
        def handle(self, event):
            return event
