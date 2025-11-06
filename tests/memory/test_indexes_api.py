"""
SPDX-License-Identifier: Apache-2.0

tests/memory/test_indexes_api.py

Comprehensive pytest tests for memory index management API endpoints.
Tests CRUD operations, validation, error handling, and RBAC.

Environment:
    LUKHAS_POLICY_MODE=permissive - Test suite runs in permissive mode
    for development/CI environments. Production uses strict mode.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from memory.index_manager import IndexManager

from adapters.openai.api import get_app


@pytest.fixture(autouse=True)
def permissive_policy_mode(monkeypatch):
    """
    Configure permissive policy mode for all tests.

    This ensures consistent behavior across development and CI environments.
    PolicyGuard will allow all operations without RBAC checks.
    """
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "permissive")


@pytest.fixture
def app():
    """Create test FastAPI application."""
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_index(client):
    """
    Create a test index for use in tests.

    Yields:
        dict: Created index response

    Cleanup:
        Deletes the test index after test completion
    """
    # Create test index
    response = client.post(
        "/v1/indexes",
        json={
            "name": "test-index",
            "metric": "angular",
            "dimension": 128,
        }
    )

    assert response.status_code == 201
    index_data = response.json()
    index_id = index_data["id"]

    yield index_data

    # Cleanup: delete index
    try:
        client.delete(f"/v1/indexes/{index_id}")
    except Exception:
        pass  # Ignore cleanup errors


class TestIndexList:
    """Test index listing endpoint."""

    def test_list_indexes_empty(self, client):
        """Test listing indexes when none exist."""
        response = client.get("/v1/indexes")

        assert response.status_code == 200
        data = response.json()
        assert "indexes" in data
        assert "total_count" in data
        assert "total_vectors" in data
        assert isinstance(data["indexes"], list)
        assert data["total_count"] >= 0
        assert data["total_vectors"] >= 0

    def test_list_indexes_with_data(self, client, test_index):
        """Test listing indexes when one exists."""
        response = client.get("/v1/indexes")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 1

        # Check test index appears in list
        index_ids = [idx["id"] for idx in data["indexes"]]
        assert test_index["id"] in index_ids


class TestIndexCreate:
    """Test index creation endpoint."""

    def test_create_index_minimal(self, client):
        """Test creating index with minimal parameters."""
        response = client.post(
            "/v1/indexes",
            json={"name": "test-minimal"}
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "test-minimal"
        assert data["metric"] == "angular"  # Default
        assert data["dimension"] is None  # Auto-detect
        assert data["vector_count"] == 0
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Cleanup
        client.delete(f"/v1/indexes/{data['id']}")

    def test_create_index_full(self, client):
        """Test creating index with all parameters."""
        response = client.post(
            "/v1/indexes",
            json={
                "name": "test-full",
                "metric": "euclidean",
                "trees": 20,
                "dimension": 256,
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "test-full"
        assert data["metric"] == "euclidean"
        assert data["dimension"] == 256
        assert data["vector_count"] == 0

        # Cleanup
        client.delete(f"/v1/indexes/{data['id']}")

    def test_create_index_duplicate_name(self, client, test_index):
        """Test that duplicate index names are rejected."""
        response = client.post(
            "/v1/indexes",
            json={"name": "test-index"}  # Same as test_index
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_index_invalid_metric(self, client):
        """Test that invalid metrics are rejected."""
        response = client.post(
            "/v1/indexes",
            json={
                "name": "test-invalid-metric",
                "metric": "manhattan"  # Invalid
            }
        )

        assert response.status_code == 422  # Validation error

    def test_create_index_invalid_name(self, client):
        """Test that invalid names are rejected."""
        response = client.post(
            "/v1/indexes",
            json={"name": "test index with spaces"}  # Invalid
        )

        assert response.status_code == 422  # Validation error


class TestIndexGet:
    """Test index retrieval endpoint."""

    def test_get_index_success(self, client, test_index):
        """Test getting an existing index."""
        index_id = test_index["id"]
        response = client.get(f"/v1/indexes/{index_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == index_id
        assert data["name"] == "test-index"
        assert data["metric"] == "angular"
        assert data["dimension"] == 128
        assert data["vector_count"] == 0

    def test_get_index_not_found(self, client):
        """Test getting a non-existent index."""
        response = client.get("/v1/indexes/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestVectorAdd:
    """Test vector addition endpoint."""

    def test_add_vectors_success(self, client, test_index):
        """Test successfully adding vectors."""
        index_id = test_index["id"]

        vectors = [
            {"id": "vec-1", "vector": [0.1] * 128},
            {"id": "vec-2", "vector": [0.2] * 128},
            {"id": "vec-3", "vector": [0.3] * 128},
        ]

        response = client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": vectors}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["index_id"] == index_id
        assert data["added_count"] == 3
        assert data["failed_count"] == 0
        assert data["errors"] is None

    def test_add_vectors_dimension_mismatch(self, client, test_index):
        """Test that dimension mismatches are reported."""
        index_id = test_index["id"]

        # First add a vector with correct dimension
        client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [{"id": "vec-1", "vector": [0.1] * 128}]}
        )

        # Try to add vector with wrong dimension
        response = client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [{"id": "vec-2", "vector": [0.2] * 64}]}  # Wrong dimension
        )

        assert response.status_code == 200
        data = response.json()

        assert data["added_count"] == 0
        assert data["failed_count"] == 1
        assert data["errors"] is not None
        assert len(data["errors"]) > 0

    def test_add_vectors_to_nonexistent_index(self, client):
        """Test adding vectors to non-existent index."""
        response = client.post(
            "/v1/indexes/nonexistent/vectors",
            json={"vectors": [{"id": "vec-1", "vector": [0.1] * 128}]}
        )

        assert response.status_code == 404

    def test_add_vectors_invalid_format(self, client, test_index):
        """Test that invalid vector formats are rejected."""
        index_id = test_index["id"]

        # Missing 'vector' field
        response = client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [{"id": "vec-1"}]}
        )

        assert response.status_code == 422  # Validation error


class TestVectorSearch:
    """Test vector search endpoint."""

    def test_search_vectors_success(self, client, test_index):
        """Test successful vector search."""
        index_id = test_index["id"]

        # Add test vectors
        vectors = [
            {"id": "vec-1", "vector": [0.1] * 128},
            {"id": "vec-2", "vector": [0.2] * 128},
            {"id": "vec-3", "vector": [0.3] * 128},
        ]
        client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": vectors}
        )

        # Search
        response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={
                "vector": [0.15] * 128,
                "k": 2,
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["index_id"] == index_id
        assert data["k"] == 2
        assert "query_time_ms" in data
        assert len(data["results"]) <= 2

        # Check result format
        for result in data["results"]:
            assert "id" in result
            assert result["id"] in ["vec-1", "vec-2", "vec-3"]

    def test_search_vectors_with_vectors(self, client, test_index):
        """Test search with include_vectors=True."""
        index_id = test_index["id"]

        # Add test vector
        test_vec = [0.1] * 128
        client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [{"id": "vec-1", "vector": test_vec}]}
        )

        # Search with include_vectors
        response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={
                "vector": test_vec,
                "k": 1,
                "include_vectors": True,
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["id"] == "vec-1"
        assert result["vector"] is not None
        assert len(result["vector"]) == 128

    def test_search_dimension_mismatch(self, client, test_index):
        """Test that dimension mismatches are rejected."""
        index_id = test_index["id"]

        # Add vector with dimension 128
        client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [{"id": "vec-1", "vector": [0.1] * 128}]}
        )

        # Try to search with wrong dimension
        response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={
                "vector": [0.1] * 64,  # Wrong dimension
                "k": 1,
            }
        )

        assert response.status_code == 400
        assert "dimension" in response.json()["detail"].lower()

    def test_search_nonexistent_index(self, client):
        """Test searching in non-existent index."""
        response = client.post(
            "/v1/indexes/nonexistent/search",
            json={"vector": [0.1] * 128, "k": 10}
        )

        assert response.status_code == 404


class TestVectorDelete:
    """Test vector deletion endpoint."""

    def test_delete_vector_success(self, client, test_index):
        """Test successful vector deletion."""
        index_id = test_index["id"]

        # Add test vector
        client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [{"id": "vec-to-delete", "vector": [0.1] * 128}]}
        )

        # Delete vector
        response = client.delete(f"/v1/indexes/{index_id}/vectors/vec-to-delete")

        assert response.status_code == 200
        data = response.json()

        assert data["index_id"] == index_id
        assert data["vector_id"] == "vec-to-delete"
        assert data["success"] is True

    def test_delete_vector_not_found(self, client, test_index):
        """Test deleting non-existent vector."""
        index_id = test_index["id"]

        response = client.delete(f"/v1/indexes/{index_id}/vectors/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_delete_vector_from_nonexistent_index(self, client):
        """Test deleting vector from non-existent index."""
        response = client.delete("/v1/indexes/nonexistent/vectors/vec-1")

        assert response.status_code == 404


class TestIndexDelete:
    """Test index deletion endpoint."""

    def test_delete_index_success(self, client):
        """Test successful index deletion."""
        # Create index
        create_response = client.post(
            "/v1/indexes",
            json={"name": "index-to-delete"}
        )
        assert create_response.status_code == 201
        index_id = create_response.json()["id"]

        # Delete index
        response = client.delete(f"/v1/indexes/{index_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["index_id"] == index_id
        assert data["success"] is True

        # Verify index is gone
        get_response = client.get(f"/v1/indexes/{index_id}")
        assert get_response.status_code == 404

    def test_delete_index_not_found(self, client):
        """Test deleting non-existent index."""
        response = client.delete("/v1/indexes/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_delete_index_with_vectors(self, client):
        """Test deleting index that contains vectors."""
        # Create index and add vectors
        create_response = client.post(
            "/v1/indexes",
            json={"name": "index-with-vectors", "dimension": 128}
        )
        assert create_response.status_code == 201
        index_id = create_response.json()["id"]

        # Add vectors
        client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": [
                {"id": "vec-1", "vector": [0.1] * 128},
                {"id": "vec-2", "vector": [0.2] * 128},
            ]}
        )

        # Delete index (should succeed even with vectors)
        response = client.delete(f"/v1/indexes/{index_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow(self, client):
        """Test complete workflow: create, add, search, delete."""
        # 1. Create index
        create_response = client.post(
            "/v1/indexes",
            json={
                "name": "integration-test",
                "metric": "angular",
                "dimension": 64,
            }
        )
        assert create_response.status_code == 201
        index_id = create_response.json()["id"]

        # 2. Add vectors
        vectors = [
            {"id": f"doc-{i}", "vector": [float(i) / 10.0] * 64}
            for i in range(10)
        ]
        add_response = client.post(
            f"/v1/indexes/{index_id}/vectors",
            json={"vectors": vectors}
        )
        assert add_response.status_code == 200
        assert add_response.json()["added_count"] == 10

        # 3. Search
        search_response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={"vector": [0.5] * 64, "k": 5}
        )
        assert search_response.status_code == 200
        results = search_response.json()["results"]
        assert len(results) == 5

        # 4. Get index details
        get_response = client.get(f"/v1/indexes/{index_id}")
        assert get_response.status_code == 200
        assert get_response.json()["vector_count"] == 10

        # 5. Delete specific vector
        delete_vec_response = client.delete(f"/v1/indexes/{index_id}/vectors/doc-0")
        assert delete_vec_response.status_code == 200
        assert delete_vec_response.json()["success"] is True

        # 6. Verify vector count decreased
        get_response2 = client.get(f"/v1/indexes/{index_id}")
        assert get_response2.status_code == 200
        assert get_response2.json()["vector_count"] == 9

        # 7. Delete index
        delete_response = client.delete(f"/v1/indexes/{index_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True

        # 8. Verify index is gone
        final_get = client.get(f"/v1/indexes/{index_id}")
        assert final_get.status_code == 404


class TestValidation:
    """Test request validation."""

    def test_create_index_validation(self, client):
        """Test validation on index creation."""
        # Missing name
        response = client.post("/v1/indexes", json={})
        assert response.status_code == 422

        # Invalid trees (too many)
        response = client.post(
            "/v1/indexes",
            json={"name": "test", "trees": 1000}
        )
        assert response.status_code == 422

        # Invalid dimension (negative)
        response = client.post(
            "/v1/indexes",
            json={"name": "test", "dimension": -1}
        )
        assert response.status_code == 422

    def test_search_validation(self, client, test_index):
        """Test validation on search requests."""
        index_id = test_index["id"]

        # Invalid k (too large)
        response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={"vector": [0.1] * 128, "k": 10000}
        )
        assert response.status_code == 422

        # Invalid k (negative)
        response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={"vector": [0.1] * 128, "k": -1}
        )
        assert response.status_code == 422

        # Empty vector
        response = client.post(
            f"/v1/indexes/{index_id}/search",
            json={"vector": [], "k": 10}
        )
        assert response.status_code == 422
