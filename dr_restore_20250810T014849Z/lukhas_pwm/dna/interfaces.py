from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DNAWriteReceipt:
    key: str
    version: int
    strength: float
    upserted: bool


class HelixMemory:
    """DNA Helix memory interface (production impl lives elsewhere)."""

    def write(
        self,
        key: str,
        value: Any,
        *,
        version: int,
        strength: float,
        meta: Dict,
    ) -> DNAWriteReceipt:
        raise NotImplementedError

    def read(self, key: str) -> Optional[Dict]:
        raise NotImplementedError
