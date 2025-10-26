"""Accent adapter bridge for Healix memory retrieval."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Iterable, List, Mapping

logger = logging.getLogger("accent_adapter")


@dataclass
class MemoryRecord:
    """Normalized structure for memory chain records."""

    timestamp: str
    type: str
    tone: str
    intensity: float
    hash: str
    recall_count: int = 0


class AccentAdapter:
    """Retrieve memory chains from accent-aware storage layers."""

    def __init__(
        self,
        *,
        tier: str = "resident",
        memory_source: Callable[[str], Iterable[Mapping[str, object]]] | None = None,
    ) -> None:
        self.tier = tier
        self._memory_source = memory_source or (lambda user_id: [])
        # ΛTAG: memory - monitor retrieval characteristics
        logger.debug(
            "AccentAdapter initialized",
            extra={"tier": tier},
        )

    def get_user_memory_chain(self, user_id: str) -> List[Mapping[str, object]]:
        """Fetch a normalized memory chain for a user."""

        raw_chain = list(self._memory_source(user_id))
        logger.info(
            "Memory chain retrieved",
            extra={"user_id": user_id, "count": len(raw_chain)},
        )
        return raw_chain

    # ✅ TODO: connect to the live accent storage once orchestration bridge is ready
