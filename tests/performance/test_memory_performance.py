import numpy as np
import pytest

from lukhas.memory.index import EmbeddingIndex

DIMENSION = 128
NUM_VECTORS = 1000

@pytest.fixture(scope="module")
def populated_index():
    """Creates an EmbeddingIndex and populates it with random vectors."""
    index = EmbeddingIndex()
    for i in range(NUM_VECTORS):
        vector_id = f"vector_{i}"
        vector = np.random.rand(DIMENSION).tolist()
        index.add(vector_id, vector, metadata={"id": i})
    return index

def test_search_performance(benchmark, populated_index):
    """Benchmarks the performance of the search method."""
    query_vector = np.random.rand(DIMENSION).tolist()

    # The search function is benchmarked here
    result = benchmark.pedantic(populated_index.search, args=(query_vector,), iterations=10, rounds=5)

    assert result is not None
    assert len(result) == 5  # top_k defaults to 5

def test_cached_search_performance(benchmark, populated_index):
    """Benchmarks the performance of a cached search."""
    query_vector = np.random.rand(DIMENSION).tolist()

    # First call to cache the result
    populated_index.search(query_vector)

    # Benchmark the cached call
    result = benchmark.pedantic(populated_index.search, args=(query_vector,), iterations=100, rounds=10)

    assert result is not None
    assert len(result) == 5
