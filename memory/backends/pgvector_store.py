# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

# Assuming a psycopg2-like connection object is used.
# The actual client is injected, so this is for type hinting.
from psycopg2.extensions import connection as PgConnection


@dataclass(frozen=True)
class VectorDoc:
    id: str
    text: str
    embedding: list[float]
    meta: dict[str, Any]


class PgVectorStore:
    """Minimal pgvector-backed store."""

    def __init__(self, conn: PgConnection, table: str = "mem_store", dim: int = 1536):
        self.conn = conn
        self.table = table
        self.dim = dim

    def add(self, doc: VectorDoc) -> str:
        """Upsert document with conflict resolution."""
        query = f"""
        INSERT INTO {self.table} (id, embedding, metadata, text)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            text = EXCLUDED.text,
            updated_at = NOW()
        RETURNING id
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (
                doc.id,
                doc.embedding,
                json.dumps(doc.meta),
                doc.text
            ))
            result = cur.fetchone()
            if result:
                return result[0]
            raise ValueError("Upsert failed to return ID")

    def bulk_add(self, docs: Iterable[VectorDoc]) -> list[str]:
        """Bulk insert using INSERT with multiple VALUES."""
        # Note: For very large volumes, COPY is faster, but this is simpler.
        if not docs:
            return []

        values_placeholder = ", ".join(["(%s, %s, %s, %s)"] * len(docs))
        query = f"""
        INSERT INTO {self.table} (id, embedding, metadata, text)
        VALUES {values_placeholder}
        ON CONFLICT (id) DO UPDATE SET
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            text = EXCLUDED.text,
            updated_at = NOW()
        RETURNING id
        """

        params = []
        for doc in docs:
            params.extend([
                doc.id,
                doc.embedding,
                json.dumps(doc.meta),
                doc.text
            ])

        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return [row[0] for row in cur.fetchall()]

    def search(
        self,
        embedding: list[float],
        k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[str, float]]:
        """Return [(id, score)] by cosine distance with optional filters."""
        params = [embedding, k]

        if filters:
            filter_clauses = []
            for key, value in filters.items():
                filter_clauses.append(f"metadata->>'{key}' = %s")
                params.append(value)

            where_clause = "WHERE " + " AND ".join(filter_clauses)
            query = f"SELECT id, 1 - (embedding <=> %s) AS score FROM {self.table} {where_clause} ORDER BY score DESC LIMIT %s"
        else:
            query = f"SELECT id, 1 - (embedding <=> %s) AS score FROM {self.table} ORDER BY score DESC LIMIT %s"

        with self.conn.cursor() as cur:
            cur.execute(query, tuple(params))
            return [(row[0], row[1]) for row in cur.fetchall()]

    def delete(
        self, *, id: str | None = None, where: dict[str, Any] | None = None
    ) -> int:
        """Delete by id or filter. Return rows affected."""
        if not id and not where:
            raise ValueError("Either id or where filter must be provided")

        if id:
            query = f"DELETE FROM {self.table} WHERE id = %s"
            params = (id,)
        else:
            # Simple WHERE implementation, e.g., where={"source": "doc.pdf"}
            # This is not safe for complex queries, but works for this scope.
            conditions = " AND ".join([f"metadata->>'{key}' = %s" for key in where.keys()])
            query = f"DELETE FROM {self.table} WHERE {conditions}"
            params = tuple(where.values())

        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount

    def stats(self) -> dict[str, Any]:
        """Return {count, table, dim}."""
        query = f"SELECT COUNT(*) FROM {self.table}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            count = cur.fetchone()[0]
        return {"table": self.table, "dim": self.dim, "count": count}
