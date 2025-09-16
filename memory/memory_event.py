"""Memory event structures and factory utilities."""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ΛTAG: memory_event
@dataclass
class MemoryEvent:
    """Simple container for memory event data."""

    data: Dict[str, Any]
    metadata: Dict[str, Any]


class MemoryEventFactory:
    """Factory for creating :class:`MemoryEvent` objects."""

    def create(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> MemoryEvent:
        """Create a new :class:`MemoryEvent` instance.

        Args:
            data: Core event payload.
            metadata: Additional contextual information.

        Returns:
            A populated :class:`MemoryEvent`.
        """
        logger.debug("Creating MemoryEvent with metadata: %s", metadata)
        # TODO: implement validation and driftScore tracking
        return MemoryEvent(data=data, metadata=metadata)


__all__ = ["MemoryEvent", "MemoryEventFactory", "logger"]
