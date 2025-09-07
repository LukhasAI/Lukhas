from dataclasses import dataclass
from typing import Any, Optional

import streamlit as st


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
meta: dict,
) -> DNAWriteReceipt:
        raise NotImplementedError

    def read(self, key: str) -> Optional[dict]:
        raise NotImplementedError
