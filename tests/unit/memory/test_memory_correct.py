"""Unit tests for the LUKHAS memory module."""

import numpy as np
import pytest

from lukhas.memory.index import EmbeddingIndex, IndexManager


@pytest.fixture
def populated_index():
    """Returns a populated EmbeddingIndex for testing."""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 0.0, 0.0], {"type": "a"})
    index.add("vec2", [0.0, 1.0, 0.0], {"type": "b"})
    index.add("vec3", [-1.0, 0.0, 0.0], {"type": "c"})
    index.add("vec4", [0.5, 0.5, 0.5], {"type": "d"})
    return index


def test_embedding_index_add():
    """Tests adding a vector to the EmbeddingIndex."""
    index = EmbeddingIndex()
    vector = [0.1, 0.2, 0.3]
    metadata = {"key": "value"}
    index.add("test_vector", vector, metadata)
    assert "test_vector" in index._vectors
    assert np.array_equal(index._vectors["test_vector"], np.array(vector))
    assert "test_vector" in index._metadata
    assert index._metadata["test_vector"] == metadata


def test_embedding_index_add_no_metadata():
    """Tests adding a vector without metadata."""
    index = EmbeddingIndex()
    vector = [0.4, 0.5, 0.6]
    index.add("test_vector_no_meta", vector)
    assert "test_vector_no_meta" in index._vectors
    assert "test_vector_no_meta" not in index._metadata


def test_embedding_index_search(populated_index):
    """Tests searching for a vector in the EmbeddingIndex."""
    query_vector = [0.8, 0.1, 0.1]
    results = populated_index.search(query_vector, top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "vec1"


def test_embedding_index_search_no_results():
    """Tests a search with no results."""
    index = EmbeddingIndex()
    results = index.search([1.0, 2.0, 3.0])
    assert len(results) == 0


def test_embedding_index_search_top_k(populated_index):
    """Tests the top_k parameter of the search."""
    results = populated_index.search([0.9, 0.1, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]["id"] == "vec1"
    assert results[1]["id"] == "vec4"


def test_embedding_index_search_zero_vector(populated_index):
    """Tests searching with a zero vector."""
    results = populated_index.search([0.0, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    # The result is arbitrary, but it should not error
    assert "id" in results[0]


def test_embedding_index_search_with_zero_vector_in_index(populated_index):
    """Tests searching when the index contains a zero vector."""
    populated_index.add("zero_vec", [0.0, 0.0, 0.0])
    results = populated_index.search([0.1, 0.2, 0.3], top_k=1)
    assert len(results) == 1


def test_index_manager():
    """Tests the IndexManager."""
    manager = IndexManager()
    index1 = manager.get_index("tenant1")
    index2 = manager.get_index("tenant2")
    assert isinstance(index1, EmbeddingIndex)
    assert isinstance(index2, EmbeddingIndex)
    assert index1 is not index2

    index1_again = manager.get_index("tenant1")
    assert index1 is index1_again


def test_index_manager_isolation():
    """Tests that tenant indexes are isolated."""
    manager = IndexManager()
    index1 = manager.get_index("tenant1")
    index2 = manager.get_index("tenant2")
    index1.add("vec1", [1.0, 0.0, 0.0])
    assert len(index2.search([1.0, 0.0, 0.0])) == 0


def test_singleton_index_manager():
    """Tests the singleton instance of the IndexManager."""
    from lukhas.memory.index import index_manager as singleton_manager
    assert isinstance(singleton_manager, IndexManager)
    index1 = singleton_manager.get_index("tenant1")
    index2 = singleton_manager.get_index("tenant1")
    assert index1 is index2


def test_similarity_search_with_threshold(populated_index):
    """
    Tests similarity search with a threshold.
    TODO: The search method does not currently support a threshold.
    """
    results = populated_index.search([0.9, 0.1, 0.0], top_k=2)
    assert len(results) == 2


def test_memory_capacity_limits():
    """
    Tests memory capacity limits and eviction.
    TODO: The EmbeddingIndex does not currently support a max_size.
    """
    index = EmbeddingIndex()
    for i in range(100):
        index.add(f"vec{i}", [float(i), 0.0, 0.0])
    assert len(index._vectors) == 100


def test_memory_persistence():
    """
    Tests memory persistence and loading.
    TODO: The EmbeddingIndex does not currently support persistence.
    """
    pass


def test_concurrent_access():
    """
    Tests concurrent access to the EmbeddingIndex.
    TODO: The EmbeddingIndex is not thread-safe.
    """
    import threading
    index = EmbeddingIndex()
    errors = []
    def worker():
        try:
            for i in range(100):
                index.add(f"vec{threading.current_thread().name}-{i}", [float(i), 0.0, 0.0])
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, name=f"worker{i}") for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(index._vectors) == 1000
