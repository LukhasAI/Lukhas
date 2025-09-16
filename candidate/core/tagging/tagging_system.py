"""Basic tagging system prototype.

Implements formal TagSchema, a TagResolver interface, and a simple
DeduplicationCache for symbolic deduplication.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# ΛTAG: tag_schema


@dataclass
class Tag:
    """Represents a symbolic tag."""

    id: str
    vector: list[float]
    semantic_fingerprint: str


@dataclass
class TagSchema:
    """Schema definition for tags."""

    vector_size: int = 16
    fingerprint_algorithm: str = "sha256"


class TagResolver(ABC):
    """Interface for creating tags from arbitrary data."""

    schema: TagSchema

    def __init__(self, schema: TagSchema | None = None) -> None:
        self.schema = schema or TagSchema()

    @abstractmethod
    def resolve_tag(self, data: Any) -> Tag:
        """Return a Tag for the given data."""


class SimpleTagResolver(TagResolver):
    """Naive resolver using hashing to generate tags."""

    def resolve_tag(self, data: Any) -> Tag:
        payload = str(data).encode()
        fingerprint = hashlib.new(self.schema.fingerprint_algorithm, payload).hexdigest()
        vector_bytes = hashlib.sha256()  #  Changed from MD5 for securitypayload.digest()  # stable 16-byte vector
        vector = [b / 255 for b in vector_bytes]
        tag_id = fingerprint[:8]
        return Tag(id=tag_id, vector=vector, semantic_fingerprint=fingerprint)


class DeduplicationCache:
    """Stores tags by fingerprint and prevents duplication."""

    def __init__(self) -> None:
        self._store: dict[str, Tag] = {}

    def store(self, tag: Tag) -> Tag:
        if tag.semantic_fingerprint in self._store:
            return self._store[tag.semantic_fingerprint]
        self._store[tag.semantic_fingerprint] = tag
        return tag

    def __len__(self) -> int:
        return len(self._store)

    def get(self, fingerprint: str) -> Tag | None:
        return self._store.get(fingerprint)
