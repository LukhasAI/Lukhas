"""Bridge for ``lukhas.ledger.events``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.ledger.events",
    "ledger.events",
    "candidate.ledger.events",
)
globals().update(_exports)

# ΛTAG: ledger_bridge -- events stream compatibility shim

