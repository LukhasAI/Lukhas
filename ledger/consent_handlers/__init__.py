"""Bridge for `ledger.consent_handlers`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.ledger.consent_handlers
  2) candidate.ledger.consent_handlers
  3) ledger.consent_handlers

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.ledger.consent_handlers",
    "candidate.ledger.consent_handlers",
    "ledger.consent_handlers",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Add expected symbols as stubs if not found
# No pre-defined stubs

# Add expected symbols as stubs if not found
if "IdempotentConsentHandler" not in globals():

    class IdempotentConsentHandler:
        pass


if "IdempotentTraceHandler" not in globals():

    class IdempotentTraceHandler:
        pass
