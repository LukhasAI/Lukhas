# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


# TODO: replace with real DB client (psycopg or sqlalchemy)
class _PgClient: ...

@dataclass(frozen=True)
class VectorDoc:
    id: str
    text: str
    embedding: list[float]
    meta: dict[str, Any]

class PgVectorStore:
    """Minimal pgvector-backed store (scaffold).
    API is intentionally simple for mocking & tests.
    """
    def __init__(self, conn: _PgClient, table="mem_store", dim: int = 1536):
        self.conn = conn
        self.table = table
        self.dim = dim

    def add(self, doc: VectorDoc) -> str:
        """Insert one doc. TODO: upsert on id, return id."""
        # TODO: SQL: INSERT ... ON CONFLICT (id) DO UPDATE
        raise NotImplementedError("implement add()")

    def bulk_add(self, docs: Iterable[VectorDoc]) -> list[str]:
        """Bulk insert. TODO: chunked COPY for perf."""
        raise NotImplementedError("implement bulk_add()")

    def search(self, embedding: list[float], k: int = 10,
               filters: dict[str, Any] | None = None) -> list[tuple[str, float]]:
        """Return [(id, score)] by cosine distance. TODO: apply filters."""
        raise NotImplementedError("implement search()")

    def delete(self, *, id: str | None = None, where: dict[str, Any] | None = None) -> int:
        """Delete by id or filter. Return rows affected."""
        raise NotImplementedError("implement delete()")

    def stats(self) -> dict[str, Any]:
        """Return {count, table, dim}."""
        return {"table": self.table, "dim": self.dim, "count": None}  # TODO: SELECT COUNT(*)
