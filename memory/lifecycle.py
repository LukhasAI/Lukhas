from __future__ import annotations
from dataclasses import dataclass

@dataclass
class RetentionPolicy:
    days: int = 30

class Lifecycle:
    def __init__(self, retention: RetentionPolicy):
        self.retention = retention

    def enforce_retention(self) -> int:
        """Delete/Archive docs older than policy. Return count.
        TODO: implement archive -> ./archive/ + tombstones + audit log
        """
        raise NotImplementedError