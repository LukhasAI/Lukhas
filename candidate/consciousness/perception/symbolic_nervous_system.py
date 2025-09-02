"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - SYMBOLIC NERVOUS SYSTEM
║ Maps temperature and light input to memory tags and stores sensory echoes
║ alongside symbolic dreams
╚══════════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class SensoryEcho:
    """Representation of a sensory snapshot."""

    temperature: float
    light: float
    tags: list[str]
    timestamp: str


class SymbolicNervousSystem:
    """Map sensory input to memory tags and attach echoes to dreams."""

    def __init__(self, memory_manager: Optional[Any] = None):
        self.memory_manager = memory_manager

    # ΛTAG: sensory_mapping
    def map_inputs_to_tags(self, temperature: float, light: float) -> list[str]:
        """Convert raw sensor values to symbolic tags."""
        tags = []

        if temperature > 30:
            tags.append("hot")
        elif temperature > 20:
            tags.append("warm")
        else:
            tags.append("cold")

        if light > 0.7:
            tags.append("bright")
        elif light > 0.3:
            tags.append("dim")
        else:
            tags.append("dark")

        return tags

    # ΛTAG: memory_tagging
    async def store_sensory_echo(
        self, dream: dict[str, Any], temperature: float, light: float
    ) -> dict[str, Any]:
        """Attach sensory echo to dream and persist via memory manager."""
        tags = self.map_inputs_to_tags(temperature, light)
        echo = SensoryEcho(
            temperature=temperature,
            light=light,
            tags=tags,
            timestamp=datetime.utcnow().isoformat(),
        )

        dream.setdefault("sensory_echoes", []).append(asdict(echo))

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                {"echo": asdict(echo)}, metadata={"tags": tags}
            )

        return dream


__all__ = ["SensoryEcho", "SymbolicNervousSystem"]
