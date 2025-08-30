import json
from pathlib import Path
from typing import Any, Optional

from lukhas.migration.legacy_store import LegacyStore


class LegacyJSONL(LegacyStore):
    """Very simple JSONL adapter with lines: {"key","value","version", "strength", "meta"}"""

    def __init__(self, path: str = ".lukhas_legacy/memory.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._index = None

    def _load_index(self):
        self._index = {}
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    k = rec["key"]
                    prev = self._index.get(k)
                    if (prev is None) or (rec.get("version", 0) >= prev.get("version", 0)):
                        self._index[k] = rec
                except Exception:
                    continue

    def iter_all(self, start_after: Optional[str] = None):
        if self._index is None:
            self._load_index()
        keys = sorted(self._index.keys())
        for k in keys:
            if start_after and k <= start_after:
                continue
            yield self._index[k]

    def read(self, key: str) -> Optional[dict[str, Any]]:
        if self._index is None:
            self._load_index()
        return self._index.get(key)

    def write(self, key: str, value: Any, *, version: int, strength: float, meta: dict) -> bool:
        rec = {
            "key": key,
            "value": value,
            "version": int(version),
            "strength": float(strength),
            "meta": meta,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if self._index is None:
            self._load_index()
        cur = self._index.get(key)
        if (cur is None) or (rec["version"] >= cur.get("version", 0)):
            self._index[key] = rec
            return True
        return False

    def count(self) -> int:
        if self._index is None:
            self._load_index()
        return len(self._index)
