"""Symbolic methylation model affecting tag permanence."""

from typing import Optional

from .tags import TagScope


class MethylationModel:
    """Simple model controlling decay of symbolic tags."""

    def __init__(self, genetic_decay_factor: float = 0.5):
        self.genetic_decay_factor = genetic_decay_factor

    def adjust_lifespan(self, scope: TagScope, lifespan: Optional[float]) -> Optional[float]:
        if lifespan is None:
            return None
if scope == TagScope.GENETIC:
            return lifespan * self.genetic_decay_factor
return lifespan
