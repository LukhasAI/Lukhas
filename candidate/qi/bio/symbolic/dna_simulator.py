"""DNA Simulator for symbolic tag generation."""

from typing import Optional

from lukhas.core.colonies.base_colony import BaseColony
from lukhas.core.symbolism.tags import TagPermission, TagScope


class DNASimulator:
    """Parse symbolic DNA sequences into inheritable tags."""

    SYMBOL_MAP = {
        "A": "alpha",
        "C": "cognition",
        "G": "growth",
        "T": "transcendence",
    }

    def parse_sequence(self, sequence: str) -> dict[str, tuple[str, TagScope, TagPermission, Optional[float]]]:
        tags: dict[str, tuple[str, TagScope, TagPermission, Optional[float]]] = {}
        for idx, char in enumerate(sequence):
            symbol = self.SYMBOL_MAP.get(char.upper())
            if symbol:
                tags[f"dna_{idx}"] = (
                    symbol,
                    TagScope.GLOBAL,
                    TagPermission.PUBLIC,
                    None,
                )
        return tags

    def entangle_with_colony(self, colony: BaseColony, sequence: str) -> None:
        """Parse sequence and entangle resulting tags with the provided colony."""
        tag_map = self.parse_sequence(sequence)
        colony.entangle_tags(tag_map)
