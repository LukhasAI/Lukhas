"""Unit tests for the LUKHAS memory system."""
import numpy as np
import pytest

from lukhas.memory.index import EmbeddingIndex, IndexManager


def test_embedding_index_initialization():
    """Test that EmbeddingIndex initializes correctly."""
    index = EmbeddingIndex()
    assert index._vectors == {}
    assert index._metadata == {}


def test_add_vector_without_metadata():
    """Test adding a vector to the index without metadata."""
    index = EmbeddingIndex()
    index.add("vec1", [0.1, 0.2, 0.3])
    assert "vec1" in index._vectors
    assert np.array_equal(index._vectors["vec1"], np.array([0.1, 0.2, 0.3]))
    assert "vec1" not in index._metadata


def test_add_vector_with_metadata():
    """Test adding a vector to the index with metadata."""
    index = EmbeddingIndex()
    index.add("vec1", [0.1, 0.2, 0.3], {"source": "test"})
    assert "vec1" in index._vectors
    assert "vec1" in index._metadata
    assert index._metadata["vec1"] == {"source": "test"}


def test_search_empty_index():
    """Test that searching an empty index returns an empty list."""
    index = EmbeddingIndex()
    results = index.search([0.1, 0.2, 0.3])
    assert results == []


def test_search_basic():
    """Test a basic search with a few vectors."""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 0.0, 0.0], {"id": "a"})
    index.add("vec2", [0.0, 1.0, 0.0], {"id": "b"})
    index.add("vec3", [0.8, 0.2, 0.0], {"id": "c"})

    query_vector = [0.9, 0.1, 0.0]
    results = index.search(query_vector, top_k=2)

    assert len(results) == 2
    assert results[0]["id"] == "vec1"
    assert results[1]["id"] == "vec3"
    assert results[0]["metadata"]["id"] == "a"


def test_search_with_top_k():
    """Test that the top_k parameter works correctly."""
    index = EmbeddingIndex()
    for i in range(10):
        index.add(f"vec{i}", list(np.random.rand(3)))

    results_top_3 = index.search([0.5, 0.5, 0.5], top_k=3)
    assert len(results_top_3) == 3

    results_top_5 = index.search([0.5, 0.5, 0.5], top_k=5)
    assert len(results_top_5) == 5


def test_search_with_zero_query_vector():
    """Test searching with a zero vector as the query."""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 0.0, 0.0])
    results = index.search([0.0, 0.0, 0.0])
    for result in results:
        assert result["similarity"] == 0.0


def test_search_with_zero_vector_in_index():
    """Test searching when a zero vector is in the index."""
    index = EmbeddingIndex()
    index.add("zero_vec", [0.0, 0.0, 0.0])
    index.add("vec1", [1.0, 0.0, 0.0])

    results = index.search([0.5, 0.5, 0.5])
    assert len(results) > 0
    for result in results:
        if result["id"] == "zero_vec":
            assert result["similarity"] == 0.0


def test_index_manager_get_index():
    """Test that the IndexManager returns an index for a tenant."""
    manager = IndexManager()
    index = manager.get_index("tenant1")
    assert isinstance(index, EmbeddingIndex)


def test_index_manager_separate_tenants():
    """Test that the IndexManager keeps tenant indexes separate."""
    manager = IndexManager()

    index1 = manager.get_index("tenant1")
    index1.add("vec1", [0.1, 0.2, 0.3])

    index2 = manager.get_index("tenant2")
    index2.add("vec2", [0.4, 0.5, 0.6])

    assert "vec1" in index1._vectors
    assert "vec2" not in index1._vectors
    assert "vec2" in index2._vectors
    assert "vec1" not in index2._vectors


def test_search_with_mismatched_dimensions_raises_error():
    """Test that searching with a query of a different dimension raises a ValueError."""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 0.0, 0.0])  # Dimension 3
    with pytest.raises(ValueError):
        index.search([0.5, 0.5])  # Query with dimension 2
