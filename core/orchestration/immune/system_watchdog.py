import json
import os
import structlog
from typing import List

log = structlog.get_logger(__name__)

class SystemWatchdog:
    """Simple internal immune system scanning for corrupted memory entries."""

    def __init__(self, store_path: str = "helix_memory_store.jsonl"):
        self.store_path = store_path
        self.quarantine_path = f"{store_path}.quarantine"

    def scan(self) -> List[str]:
        if not os.path.exists(self.store_path):
            return []
        corrupted: List[str] = []
        with open(self.store_path, "r") as f:
            for line in f:
                try:
                    json.loads(line)
                except Exception:
                    corrupted.append(line.strip())
        for entry in corrupted:
            self._quarantine_entry(entry)
        if corrupted:
            log.warning("corrupted_entries_quarantined", count=len(corrupted))
        return corrupted

    def _quarantine_entry(self, line: str) -> None:
        with open(self.quarantine_path, "a") as qf:
            qf.write(line + "\n")

