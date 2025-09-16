"""Memory identity structures and factory utilities."""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ΛTAG: memory_identity
@dataclass
class MemoryIdentity:
    """Representation of an entity capable of holding memories."""

    identifier: str
    attributes: Dict[str, Any]


class MemoryIdentityFactory:
    """Factory for creating :class:`MemoryIdentity` objects."""

    def create(self, identifier: str, attributes: Dict[str, Any]) -> MemoryIdentity:
        """Create a new :class:`MemoryIdentity` instance.

        Args:
            identifier: Unique identity key.
            attributes: Supplementary attribute mapping.

        Returns:
            A populated :class:`MemoryIdentity`.
        """
        logger.debug("Creating MemoryIdentity '%s' with attributes: %s", identifier, attributes)
        # TODO: integrate with identity registry and affect_delta metrics
        return MemoryIdentity(identifier=identifier, attributes=attributes)


__all__ = ["MemoryIdentity", "MemoryIdentityFactory", "logger"]
