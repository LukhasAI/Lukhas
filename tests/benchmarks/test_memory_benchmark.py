"""Benchmarks for memory operations."""

import pytest
import numpy as np
from memory.index_manager import IndexManager

@pytest.fixture
def index_manager_with_index():
    """Provides an IndexManager with a single index."""
    manager = IndexManager()
    index_id = manager.create_index(name="benchmark_tenant", dimension=1536)
    return manager, index_id

def test_add_vector_benchmark(benchmark, index_manager_with_index):
    """Benchmark adding a vector to an index."""
    manager, index_id = index_manager_with_index
    vector = np.random.rand(1536).tolist()
    benchmark(manager.add_vector, index_id, "test_vector", vector)

def test_search_vector_benchmark(benchmark, index_manager_with_index):
    """Benchmark searching for a vector in an index."""
    manager, index_id = index_manager_with_index
    vector = np.random.rand(1536).tolist()
    manager.add_vector(index_id, "test_vector", vector)
    query_vector = np.random.rand(1536).tolist()
    benchmark(manager.search, index_id, query_vector)
