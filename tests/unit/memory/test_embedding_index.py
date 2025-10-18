from __future__ import annotations

from memory.embedding_index import EmbeddingIndex

# ΛTAG: memory_embedding_index_test


def test_embedding_index_add_and_query() -> None:
    index = EmbeddingIndex()
    index.add("a", [1.0, 0.0, 0.0])
    index.add("b", [0.0, 1.0, 0.0])

    results = index.query([1.0, 0.0, 0.0], k=1)
    assert results[0] == "a"


def test_embedding_index_ignores_dimension_mismatch(caplog) -> None:
    index = EmbeddingIndex()
    index.add("a", [1.0, 0.0])
    with caplog.at_level("WARNING"):
        index.add("b", [1.0])
    assert index.size() == 1
