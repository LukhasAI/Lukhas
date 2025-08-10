import time
from typing import Any, Dict, Optional

from lukhas_pwm.dna.interfaces import DNAWriteReceipt, HelixMemory


class InMemoryHelix(HelixMemory):
    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def write(
        self,
        key: str,
        value: Any,
        *,
        version: int,
        strength: float,
        meta: Dict,
    ) -> DNAWriteReceipt:
        cur = self._store.get(key)
        upserted = False
        if cur is None or version >= cur["version"]:
            self._store[key] = {
                "value": value,
                "version": int(version),
                "strength": max(0.0, min(1.0, float(strength))),
                "meta": meta,
                "ts": int(time.time() * 1000),
            }
            upserted = True
        row = self._store[key]
        return DNAWriteReceipt(
            key=key,
            version=row["version"],
            strength=row["strength"],
            upserted=upserted,
        )

    def read(self, key: str) -> Optional[Dict]:
        return self._store.get(key)
