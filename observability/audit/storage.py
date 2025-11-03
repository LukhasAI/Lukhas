"""
Storage adapters for audit trails.
Default: Append-only JSONL files with optional Postgres backend.
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any, Dict, List

# Storage configuration
AUDIT_STORAGE = Path("audit_logs")
AUDIT_STORAGE.mkdir(parents=True, exist_ok=True)


class JSONLStorage:
    """Append-only JSONL storage for audit events."""

    def __init__(self, base_path: Path = AUDIT_STORAGE):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _table_path(self, table: str) -> Path:
        """Get path for JSONL table file."""
        return self.base_path / f"{table}.jsonl"

    async def write_json(self, table: str, payload: Dict[str, Any]):
        """
        Write JSON object to append-only JSONL file.

        Args:
            table: Table name (decision_trace, trace_span, etc.)
            payload: JSON-serializable dict
        """
        path = self._table_path(table)
        line = json.dumps(payload, sort_keys=True) + "\n"

        # Append-only write
        with path.open("a") as f:
            f.write(line)

    async def fetch_decision_trace(self, trace_id: str) -> Dict[str, Any] | None:
        """
        Fetch decision trace by ID.

        Args:
            trace_id: Trace identifier

        Returns:
            Trace dict or None if not found
        """
        path = self._table_path("decision_trace")
        if not path.exists():
            return None

        with path.open("r") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("id") == trace_id or obj.get("trace_id") == trace_id:
                        return obj
                except json.JSONDecodeError:
                    continue

        return None

    async def fetch_jsons_by_trace(
        self,
        table: str,
        trace_id: str,
        order_by: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all JSON objects matching trace_id.

        Args:
            table: Table name
            trace_id: Trace identifier
            order_by: Optional field to sort by

        Returns:
            List of matching objects
        """
        path = self._table_path(table)
        if not path.exists():
            return []

        results = []
        with path.open("r") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("trace_id") == trace_id:
                        results.append(obj)
                except json.JSONDecodeError:
                    continue

        # Sort if requested
        if order_by and results:
            with contextlib.suppress(TypeError, KeyError):
                results.sort(key=lambda x: x.get(order_by, 0))

        return results


# Singleton storage instance
_storage: JSONLStorage | None = None


def get_storage() -> JSONLStorage:
    """Get singleton storage instance."""
    global _storage
    if _storage is None:
        _storage = JSONLStorage()
    return _storage


# Convenience wrappers
async def write_json(table: str, payload: Dict[str, Any]):
    """Write JSON to storage."""
    storage = get_storage()
    await storage.write_json(table, payload)


async def fetch_decision_trace(trace_id: str) -> Dict[str, Any] | None:
    """Fetch decision trace by ID."""
    storage = get_storage()
    return await storage.fetch_decision_trace(trace_id)


async def fetch_jsons_by_trace(
    table: str,
    trace_id: str,
    order_by: str | None = None
) -> List[Dict[str, Any]]:
    """Fetch JSONs by trace ID."""
    storage = get_storage()
    return await storage.fetch_jsons_by_trace(table, trace_id, order_by)
