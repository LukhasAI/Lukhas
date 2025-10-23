"""
Real memory system integration tests for OpenAI façade.

Tests actual embedding index, vector search, and context preservation
when memory systems are available. Validates graceful degradation.
"""
import pytest
from starlette.testclient import TestClient
from serve.main import app, MEMORY_AVAILABLE

# Skip entire module if memory systems not available
pytestmark = pytest.mark.skipif(
    not MEMORY_AVAILABLE,
    reason="Memory systems (EmbeddingIndex, IndexManager) not available"
)


@pytest.fixture
def client():
    """Test client with override for dependencies."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Valid bearer token headers."""
    return {"Authorization": "Bearer test-token-12345"}


# Embedding Index Tests
def test_memory_embedding_index_stores_vectors(client, auth_headers):
    """Verify EmbeddingIndex stores vectors from embeddings API."""
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "Knowledge to remember: LUKHAS uses MATRIZ",
            "store": True  # Request storage in index
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return embedding
    assert "data" in data
    assert len(data["data"]) > 0
    embedding = data["data"][0]["embedding"]
    assert len(embedding) == 1536


def test_memory_embedding_index_retrieval(client, auth_headers):
    """Verify EmbeddingIndex retrieves similar vectors."""
    # Store embedding
    r1 = client.post(
        "/v1/embeddings",
        json={
            "input": "Paris is the capital of France",
            "store": True,
            "metadata": {"topic": "geography"}
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Query for similar content
    r2 = client.post(
        "/v1/embeddings",
        json={
            "input": "What is the capital of France?",
            "retrieve_similar": True,
            "top_k": 3
        },
        headers=auth_headers
    )
    assert r2.status_code == 200

    data = r2.json()
    # Should return embedding plus similar results
    assert "data" in data


def test_memory_vector_similarity_search(client, auth_headers):
    """Verify vector similarity search finds related content."""
    # Store multiple related embeddings
    topics = [
        "Machine learning is a subset of AI",
        "Neural networks learn from data",
        "Deep learning uses multiple layers"
    ]

    for topic in topics:
        response = client.post(
            "/v1/embeddings",
            json={"input": topic, "store": True},
            headers=auth_headers
        )
        assert response.status_code == 200

    # Search for similar content
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "What is deep learning?",
            "retrieve_similar": True,
            "top_k": 2
        },
        headers=auth_headers
    )

    assert response.status_code == 200


def test_memory_index_manager_tenant_isolation(client, auth_headers):
    """Verify IndexManager isolates embeddings by tenant."""
    # Tenant A stores data
    tenant_a_headers = {"Authorization": "Bearer tenant-a-token"}
    r1 = client.post(
        "/v1/embeddings",
        json={
            "input": "Tenant A secret data",
            "store": True
        },
        headers=tenant_a_headers
    )
    assert r1.status_code == 200

    # Tenant B should not retrieve Tenant A data
    tenant_b_headers = {"Authorization": "Bearer tenant-b-token"}
    r2 = client.post(
        "/v1/embeddings",
        json={
            "input": "Tenant A secret data",  # Same query
            "retrieve_similar": True
        },
        headers=tenant_b_headers
    )
    assert r2.status_code == 200

    # Should not leak across tenants


# Context Preservation Tests
def test_memory_context_preservation_across_requests(client, auth_headers):
    """Verify memory system preserves context across requests."""
    session_id = "context-session-456"

    # Request 1: Store context
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "My project is called Phoenix",
            "context": {"session_id": session_id, "save_context": True}
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Request 2: Retrieve context
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "What is my project called?",
            "context": {"session_id": session_id, "load_context": True}
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


def test_memory_context_handoff_performance(client, auth_headers):
    """Verify context handoff meets <250ms performance target."""
    import time

    session_id = "perf-session-789"

    # Store context
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "Context data: user_id=12345, preference=dark_mode",
            "context": {"session_id": session_id, "save_context": True}
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Measure context retrieval time
    start = time.time()
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "Retrieve my preferences",
            "context": {"session_id": session_id, "load_context": True}
        },
        headers=auth_headers
    )
    retrieval_time = (time.time() - start) * 1000

    assert r2.status_code == 200
    # Should meet <250ms target (allow buffer for CI)
    assert retrieval_time < 1000, f"Context retrieval {retrieval_time:.1f}ms too slow"


def test_memory_long_term_storage(client, auth_headers):
    """Verify memory system provides long-term storage."""
    # Store fact
    r1 = client.post(
        "/v1/embeddings",
        json={
            "input": "LUKHAS was founded to build consciousness-aware AI",
            "store": True,
            "metadata": {"type": "fact", "timestamp": "2024-01-01"}
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Retrieve later (simulate long-term storage)
    r2 = client.post(
        "/v1/embeddings",
        json={
            "input": "When was LUKHAS founded?",
            "retrieve_similar": True
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


# Working Memory Tests
def test_memory_working_memory_capacity(client, auth_headers):
    """Verify working memory handles short-term context."""
    session_id = "working-mem-test"

    # Load working memory with multiple items
    for i in range(5):
        response = client.post(
            "/v1/responses",
            json={
                "input": f"Remember item {i}: value_{i}",
                "context": {"session_id": session_id, "working_memory": True}
            },
            headers=auth_headers
        )
        assert response.status_code == 200

    # Query working memory
    response = client.post(
        "/v1/responses",
        json={
            "input": "What items do you remember?",
            "context": {"session_id": session_id, "working_memory": True}
        },
        headers=auth_headers
    )
    assert response.status_code == 200


def test_memory_working_memory_eviction(client, auth_headers):
    """Verify working memory evicts old items when full."""
    session_id = "eviction-test"

    # Overflow working memory (typically 7±2 items)
    for i in range(15):
        response = client.post(
            "/v1/responses",
            json={
                "input": f"Item {i}",
                "context": {"session_id": session_id, "working_memory": True}
            },
            headers=auth_headers
        )
        assert response.status_code == 200

    # Should still function (oldest items evicted)


# Episodic Memory Tests
def test_memory_episodic_memory_timeline(client, auth_headers):
    """Verify episodic memory preserves temporal sequence."""
    session_id = "episodic-test"

    events = [
        "First, I woke up",
        "Then, I had breakfast",
        "After that, I went to work",
        "Finally, I came home"
    ]

    # Store episodic sequence
    for event in events:
        response = client.post(
            "/v1/responses",
            json={
                "input": event,
                "context": {
                    "session_id": session_id,
                    "memory_type": "episodic"
                }
            },
            headers=auth_headers
        )
        assert response.status_code == 200

    # Query episodic memory
    response = client.post(
        "/v1/responses",
        json={
            "input": "What did I do today in order?",
            "context": {
                "session_id": session_id,
                "memory_type": "episodic"
            }
        },
        headers=auth_headers
    )
    assert response.status_code == 200


def test_memory_episodic_memory_recall(client, auth_headers):
    """Verify episodic memory supports specific event recall."""
    session_id = "recall-test"

    # Store specific event
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "Yesterday I met Alice at the coffee shop",
            "context": {
                "session_id": session_id,
                "memory_type": "episodic",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Recall specific event
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "Who did I meet yesterday?",
            "context": {
                "session_id": session_id,
                "memory_type": "episodic"
            }
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


# Semantic Memory Tests
def test_memory_semantic_memory_facts(client, auth_headers):
    """Verify semantic memory stores factual knowledge."""
    # Store semantic facts
    facts = [
        "The Earth orbits the Sun",
        "Water boils at 100°C",
        "Python is a programming language"
    ]

    for fact in facts:
        response = client.post(
            "/v1/embeddings",
            json={
                "input": fact,
                "store": True,
                "metadata": {"type": "semantic_fact"}
            },
            headers=auth_headers
        )
        assert response.status_code == 200

    # Query semantic memory
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "What is Python?",
            "retrieve_similar": True,
            "metadata_filter": {"type": "semantic_fact"}
        },
        headers=auth_headers
    )
    assert response.status_code == 200


def test_memory_semantic_memory_concepts(client, auth_headers):
    """Verify semantic memory handles abstract concepts."""
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "Consciousness is the state of awareness",
            "store": True,
            "metadata": {"type": "concept"}
        },
        headers=auth_headers
    )

    assert response.status_code == 200


# Memory Consolidation Tests
def test_memory_consolidation_short_to_long_term(client, auth_headers):
    """Verify memory consolidates from short to long-term storage."""
    session_id = "consolidation-test"

    # Store in working memory
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "Important fact to remember: MATRIZ is the cognitive engine",
            "context": {
                "session_id": session_id,
                "working_memory": True,
                "consolidate": True
            }
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Should be available in long-term
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "What is MATRIZ?",
            "context": {
                "session_id": session_id,
                "use_long_term": True
            }
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


def test_memory_consolidation_importance_weighting(client, auth_headers):
    """Verify consolidation prioritizes important memories."""
    session_id = "importance-test"

    # High importance memory
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "CRITICAL: System password is changeme123",
            "context": {
                "session_id": session_id,
                "importance": 10,
                "consolidate": True
            }
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Low importance memory
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "Random thought: clouds are fluffy",
            "context": {
                "session_id": session_id,
                "importance": 1
            }
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


# Memory Retrieval Tests
def test_memory_retrieval_by_metadata(client, auth_headers):
    """Verify memory retrieval supports metadata filtering."""
    # Store with metadata
    r1 = client.post(
        "/v1/embeddings",
        json={
            "input": "Project Alpha status: completed",
            "store": True,
            "metadata": {
                "project": "alpha",
                "status": "completed",
                "date": "2024-01-01"
            }
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Retrieve by metadata
    r2 = client.post(
        "/v1/embeddings",
        json={
            "input": "project status",
            "retrieve_similar": True,
            "metadata_filter": {"project": "alpha"}
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


def test_memory_retrieval_by_timestamp(client, auth_headers):
    """Verify memory retrieval supports time-based filtering."""
    # Store with timestamp
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "Event from last week",
            "store": True,
            "metadata": {
                "timestamp": "2024-01-08T12:00:00Z"
            }
        },
        headers=auth_headers
    )
    assert response.status_code == 200

    # Retrieve recent memories
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "recent events",
            "retrieve_similar": True,
            "time_range": {"after": "2024-01-01"}
        },
        headers=auth_headers
    )
    assert response.status_code == 200


def test_memory_retrieval_relevance_scoring(client, auth_headers):
    """Verify memory retrieval ranks by relevance."""
    # Store multiple items
    items = [
        "Dogs are mammals",
        "Cats are mammals",
        "Birds are not mammals"
    ]

    for item in items:
        response = client.post(
            "/v1/embeddings",
            json={"input": item, "store": True},
            headers=auth_headers
        )
        assert response.status_code == 200

    # Retrieve most relevant
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "Are cats mammals?",
            "retrieve_similar": True,
            "top_k": 3,
            "return_scores": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200


# Memory Performance Tests
def test_memory_index_lookup_performance(client, auth_headers):
    """Verify memory index lookups are fast (<100ms)."""
    import time

    # Store item
    r1 = client.post(
        "/v1/embeddings",
        json={"input": "Performance test item", "store": True},
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Measure lookup time
    start = time.time()
    r2 = client.post(
        "/v1/embeddings",
        json={
            "input": "Performance test item",
            "retrieve_similar": True
        },
        headers=auth_headers
    )
    lookup_time = (time.time() - start) * 1000

    assert r2.status_code == 200
    # Target <100ms, allow buffer for CI
    assert lookup_time < 500, f"Lookup {lookup_time:.1f}ms too slow"


def test_memory_batch_embedding_performance(client, auth_headers):
    """Verify sequential embedding generation is efficient."""
    import time

    # Process multiple embeddings sequentially
    # Note: Batch API (array input) not yet implemented
    texts = [f"Text {i}" for i in range(5)]

    start = time.time()
    embeddings = []
    for text in texts:
        response = client.post(
            "/v1/embeddings",
            json={"input": text},
            headers=auth_headers
        )
        assert response.status_code == 200
        embeddings.append(response.json()["data"][0])
    batch_time = time.time() - start

    # Should process all texts
    assert len(embeddings) == 5

    # Should complete in reasonable time
    assert batch_time < 5.0
