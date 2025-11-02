"""
T4/0.01% Review Queue
=====================

Accumulator for unmapped feature phrases discovered during enrichment.
Items are promoted to vocab/features.json via scripts/vocab_promote.py CLI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ReviewItem:
    """Single unmapped phrase awaiting vocabulary promotion"""

    raw: str
    module: str
    source: str  # e.g., "claude.me:bullets"
    count: int = 1
    first_seen: str = None
    last_seen: str = None

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if self.first_seen is None:
            self.first_seen = now
        if self.last_seen is None:
            self.last_seen = now


class ReviewQueue:
    """
    Review queue for unmapped feature phrases.

    Guarantees:
    - Idempotent: re-adding same phrase increments count + updates last_seen
    - Schema-compliant: always validates against schemas/review_queue.schema.json
    - Case-insensitive: "Temporal Stability" and "temporal stability" are same item
    """

    def __init__(self, repo_root: Path):
        self.root = repo_root
        self.path = self.root / "manifests" / "review_queue.json"
        self.data = {"updated_at": datetime.now(timezone.utc).isoformat(), "items": []}

        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except Exception:
                # Corrupt file - start fresh
                pass

        # Index by raw.lower() for fast lookup
        self.idx = {i["raw"].lower(): i for i in self.data.get("items", [])}

    def add(self, raw: str, module: str, source: str):
        """
        Add unmapped phrase to queue (or increment count if already present).

        Args:
            raw: Raw phrase as extracted (e.g., "Temporal Stability")
            module: Module name where discovered
            source: Extraction source (e.g., "claude.me:bullets")
        """
        key = raw.strip().lower()
        now = datetime.now(timezone.utc).isoformat()

        if key in self.idx:
            # Already in queue - increment count and update last_seen
            item = self.idx[key]
            item["count"] = int(item.get("count", 1)) + 1
            item["last_seen"] = now

            # Merge module hint if different
            if module and module not in item.get("notes", ""):
                item["notes"] = (item.get("notes", "") + f" module:{module}").strip()
        else:
            # New item
            item = ReviewItem(raw=raw.strip(), module=module, source=source).__dict__
            self.idx[key] = item
            self.data["items"].append(item)

        self.data["updated_at"] = now

    def save(self):
        """Write queue to disk atomically"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self.data, indent=2, sort_keys=True) + "\n"

        # Atomic write
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(content)
        tmp.replace(self.path)
