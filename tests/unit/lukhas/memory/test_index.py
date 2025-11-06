
import pytest
import numpy as np
from lukhas.memory.index import EmbeddingIndex, IndexManager

def test_embedding_index_creation():
    """Test EmbeddingIndex initializes correctly"""
    index = EmbeddingIndex()
    assert index._vectors == {}
    assert index._metadata == {}

def test_embedding_index_add_vectors():
    """Test adding vectors to index"""
    index = EmbeddingIndex()
    index.add("vec1", [0.1, 0.2, 0.3], {"meta": "data1"})
    index.add("vec2", [0.4, 0.5, 0.6], {"meta": "data2"})

    assert "vec1" in index._vectors
    assert "vec2" in index._vectors
    assert "vec1" in index._metadata
    assert "vec2" in index._metadata

def test_embedding_index_search():
    """Test vector search functionality"""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 0.0, 0.0])
    index.add("vec2", [0.0, 1.0, 0.0])

    query = [0.8, 0.1, 0.1]
    results = index.search(query, top_k=1)
    assert len(results) == 1
    assert results[0]['id'] == 'vec1'

def test_index_manager_creation():
    """Test IndexManager initializes correctly"""
    manager = IndexManager()
    assert manager._indexes is not None

def test_index_manager_get_index():
    """Test getting an index from the manager"""
    manager = IndexManager()
    index1 = manager.get_index("tenant1")
    index2 = manager.get_index("tenant2")
    assert index1 is not None
    assert index2 is not None
    assert index1 != index2

def test_index_manager_singleton():
    """Test that the singleton instance works"""
    from lukhas.memory.index import index_manager
    assert index_manager is not None
    index1 = index_manager.get_index("tenant1")
    index2 = index_manager.get_index("tenant1")
    assert index1 is index2

def test_search_empty_index():
    """Test searching an empty index returns an empty list"""
    index = EmbeddingIndex()
    results = index.search([1, 2, 3])
    assert results == []

def test_search_with_zero_vector():
    """Test searching with a zero vector"""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 0.0, 0.0])
    results = index.search([0.0, 0.0, 0.0])
    assert len(results) == 1
    assert results[0]['similarity'] == 0.0

def test_add_vector_with_mismatched_dimensions():
    """Test that searching with a vector of a different dimension raises a ValueError"""
    index = EmbeddingIndex()
    index.add("vec1", [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        index.search([1.0, 2.0])

def test_performance_with_many_vectors():
    """Test performance with a large number of vectors"""
    index = EmbeddingIndex()
    num_vectors = 1000
    vector_dim = 128
    for i in range(num_vectors):
        vector = list(np.random.rand(vector_dim))
        index.add(f"vec{i}", vector)

    query_vector = list(np.random.rand(vector_dim))
    results = index.search(query_vector, top_k=10)
    assert len(results) == 10
