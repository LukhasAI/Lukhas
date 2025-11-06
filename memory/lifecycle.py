"""Memory lifecycle helpers + retention wiring for tests."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from memory.retention import RetentionAction, RetentionRule, RetentionSeverity
except Exception:
    from enum import Enum

    class RetentionSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class RetentionAction(Enum):
        KEEP = "keep"
        ARCHIVE = "archive"
        PURGE = "purge"
        TOMBSTONE = "tombstone"

    class RetentionRule:
        def __init__(self, name: str, severity: RetentionSeverity, action: RetentionAction):
            self.name = name
            self.severity = severity
            self.action = action

        def matches(self, doc) -> bool:
            return bool(getattr(doc, "score", 0) > 0)


@dataclass
class RetentionPolicy:
    days: int = 30


class Lifecycle:
    """Minimal lifecycle stub retained for import compatibility."""

    def __init__(self, policy: RetentionPolicy | None = None):
        self.policy = policy or RetentionPolicy()

    def enforce_retention(self) -> int:
        return 0


__all__ = [
    "Lifecycle",
    "RetentionAction",
    "RetentionPolicy",
    "RetentionRule",
    "RetentionSeverity",
]

try:
# T4: code=F401 | ticket=GH-1031 | owner=core-team | status=accepted
# reason: Optional dependency import or module side-effect registration
# estimate: 0h | priority: low | dependencies: none
# T4: code=F401 | ticket=GH-1031 | owner=core-team | status=accepted
# reason: Optional dependency import or module side-effect registration
# estimate: 0h | priority: low | dependencies: none
    from memory.retention import AbstractArchivalBackend, ArchivalTier
    __all__.extend(
        name
        for name in ("ArchivalTier", "AbstractArchivalBackend")
        if name not in __all__
    )
except Exception:
    pass


try:
    from memory.tombstones import FileTombstoneStore, GDPRTombstone
except Exception:
    class FileTombstoneStore:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def add(self, key):
            return None

        def has(self, key):
            return False

    class GDPRTombstone(FileTombstoneStore):
        pass

for _name in ("FileTombstoneStore", "GDPRTombstone"):
    if _name not in globals():
        globals()[_name] = locals()[_name]
    if _name not in __all__:
        __all__.append(_name)


if "FileArchivalBackend" not in globals():

    class FileArchivalBackend:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def archive(self, doc):
            return None

        def retrieve(self, doc_id):
            return None

        def tombstone(self, doc_id):
            return None

    globals()["FileArchivalBackend"] = FileArchivalBackend
    __all__.append("FileArchivalBackend")


if "AbstractTombstoneStore" not in globals():

    class AbstractTombstoneStore:
        def add(self, key):
            raise NotImplementedError

        def has(self, key):
            raise NotImplementedError

    globals()["AbstractTombstoneStore"] = AbstractTombstoneStore
    __all__.append("AbstractTombstoneStore")


if "LifecycleStats" not in globals():

    class LifecycleStats(dict):
        """Fallback lifecycle stats container."""

    globals()["LifecycleStats"] = LifecycleStats
    __all__.append("LifecycleStats")


if "MemoryLifecycleManager" not in globals():

    class MemoryLifecycleManager:
        """Fallback lifecycle manager coordinating retention."""

        def __init__(self, policy: RetentionPolicy | None = None):
            self.policy = policy or RetentionPolicy()

        def summarize(self) -> LifecycleStats:
            return LifecycleStats()

    globals()["MemoryLifecycleManager"] = MemoryLifecycleManager
    __all__.append("MemoryLifecycleManager")
