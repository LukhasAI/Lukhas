"""Consensus surface used in orchestration tests."""

from __future__ import annotations

from importlib import import_module
from typing import Iterable

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.core.consensus",
    "candidate.core.consensus",
    "core.consensus",
)

_backend = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)
else:

    class ConsensusEngine:
        """Fallback consensus engine using simple majority."""

        def decide(self, votes: Iterable[bool]) -> bool:
            votes = list(votes)
            if not votes:
                return False
            return sum(bool(vote) for vote in votes) >= (len(votes) / 2.0)

    __all__ = ["ConsensusEngine"]
