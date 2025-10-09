"""Bridge for lukhas.ledger.events."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any

for _candidate in (
    "lukhas_website.lukhas.ledger.events",
    "ledger.events",
    "candidate.ledger.events",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


@dataclass
class LedgerEvent:  # type: ignore[misc]
    event_type: str
    payload: dict[str, Any]
