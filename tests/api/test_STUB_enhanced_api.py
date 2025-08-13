"""
Test suite for enhanced LUKHAS API system
"""

# Use service stubs for testing
import sys
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from core.api.api_client import APIError, LUKHASClient
from core.api.enhanced_api_system import EnhancedAPISystem
from core.api.service_stubs import (
    CoordinationManager,
    DreamEngine,
    EmotionEngine,
    GuardianSystem,
    MemoryManager,
    SymbolicEngine,
    UnifiedConsciousness,
)

sys.path.insert(0, "/Users/agi_dev/Lukhas")

# Import enhanced API


class TestEnhancedAPI:
    """Test enhanced API functionality"""

    @pytest.fixture
    async def api_system(self):
        """Create API system with stub services"""
        system = EnhancedAPISystem()

        # Replace with stubs
        system.symbolic_engine = SymbolicEngine()
        system.consciousness = UnifiedConsciousness()
        system.memory = MemoryManager()
        system.guardian = GuardianSystem()
        system.emotion = EmotionEngine()
        system.dream = DreamEngine()
        system.coordination = CoordinationManager()

        # Initialize stubs
        for service in [
            system.symbolic_engine,
            system.consciousness,
            system.memory,
            system.guardian,
            system.emotion,
            system.dream,
            system.coordination,
        ]:
            await service.initialize()

        # Mock security
        system.security = AsyncMock()
        system.security.validate_request = AsyncMock(return_value=(True, None))
        system.security.create_secure_session = AsyncMock(
            return_value={
                "session_id": "test_session",
                "jwt_token": "test_token",
                "mfa_verified": True,
            }
        )

        system.auth = Mock()

        return system

    @pytest.fixture
    def test_client(self, api_system):
        """Create test client"""
        return TestClient(api_system.app)

    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/api/v2/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "services" in data

    def test_auth_required(self, test_client):
        """Test that endpoints require authentication"""
        # Try without auth
        response = test_client.post(
            "/api/v2/consciousness/query", json={"query": "test"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_consciousness_query(self, api_system):
        """Test consciousness query endpoint"""
        # Use test client with auth
        client = TestClient(api_system.app)

        response = client.post(
            "/api/v2/consciousness/query",
            json={
                "query": "What is consciousness?",
                "awareness_level": 0.8,
                "include_emotional_context": True,
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["operation"] == "consciousness.query"
        assert "result" in data
        assert "processing_time_ms" in data

        result = data["result"]
        assert "interpretation" in result
        assert "consciousness_state" in result
        assert "emotional_context" in result

    @pytest.mark.asyncio
    async def test_memory_operations(self, api_system):
        """Test memory CRUD operations"""
        client = TestClient(api_system.app)
        headers = {"Authorization": "Bearer test_token"}

        # Store memory
        store_response = client.post(
            "/api/v2/memory/store",
            json={
                "action": "store",
                "content": {"event": "Test event", "importance": "high"},
                "memory_type": "episodic",
            },
            headers=headers,
        )

        assert store_response.status_code == 200
        store_data = store_response.json()
        assert store_data["status"] == "success"
        assert "memory_id" in store_data["result"]

        # Retrieve memory
        retrieve_response = client.post(
            "/api/v2/memory/retrieve",
            json={
                "action": "retrieve",
                "query": "Test event",
                "memory_type": "episodic",
            },
            headers=headers,
        )

        assert retrieve_response.status_code == 200
        retrieve_data = retrieve_response.json()
        assert retrieve_data["status"] == "success"
        assert "results" in retrieve_data["result"]

        # Search memories
        search_response = client.post(
            "/api/v2/memory/search",
            json={"action": "search", "query": "event"},
            headers=headers,
        )

        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["status"] == "success"

        # Update memory
        update_response = client.post(
            "/api/v2/memory/update",
            json={
                "action": "update",
                "query": "Test event",
                "content": {"importance": "critical"},
                "memory_type": "episodic",
            },
            headers=headers,
        )

        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["status"] == "success"

    @pytest.mark.asyncio
    async def test_governance_check(self, api_system):
        """Test governance/ethics checking"""
        client = TestClient(api_system.app)

        response = client.post(
            "/api/v2/governance/check",
            json={
                "action_proposal": {
                    "action": "generate_response",
                    "content": "User asking about sensitive topic",
                },
                "context": {"user_history": "trusted"},
                "urgency": "normal",
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        result = data["result"]
        assert "approved" in result
        assert "risk_score" in result
        assert "ethical_score" in result

    @pytest.mark.asyncio
    async def test_dream_generation(self, api_system):
        """Test creative content generation"""
        client = TestClient(api_system.app)

        response = client.post(
            "/api/v2/dream/generate",
            json={
                "prompt": "A world of infinite possibilities",
                "creativity_level": 0.9,
                "dream_type": "creative",
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        result = data["result"]
        assert "dream_content" in result
        assert "symbolic_elements" in result
        assert result["creativity_level"] == 0.9

    @pytest.mark.asyncio
    async def test_generic_process_endpoint(self, api_system):
        """Test generic process endpoint"""
        client = TestClient(api_system.app)

        # Test symbolic operation
        response = client.post(
            "/api/v2/process",
            json={
                "operation": "symbolic.encode",
                "data": {"text": "Love and think"},
                "context": None,
                "options": None,
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "glyphs" in data["result"]

        # Test emotion operation
        response = client.post(
            "/api/v2/process",
            json={
                "operation": "emotion.analyze",
                "data": {"text": "I am very happy today!"},
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "primary_emotion" in data["result"]

    @pytest.mark.asyncio
    async def test_capabilities_endpoint(self, api_system):
        """Test system capabilities endpoint"""
        client = TestClient(api_system.app)

        response = client.get(
            "/api/v2/capabilities",
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check all modules report capabilities
        expected_modules = [
            "consciousness",
            "memory",
            "guardian",
            "emotion",
            "dream",
            "symbolic",
        ]
        for module in expected_modules:
            assert module in data
            assert isinstance(data[module], dict)

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, api_system):
        """Test system metrics endpoint"""
        client = TestClient(api_system.app)

        response = client.get(
            "/api/v2/metrics", headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "timestamp" in data
        assert "active_requests" in data
        assert "total_requests" in data
        assert "services" in data

    @pytest.mark.asyncio
    async def test_error_handling(self, api_system):
        """Test API error handling"""
        client = TestClient(api_system.app)

        # Test with invalid memory action
        response = client.post(
            "/api/v2/memory/invalid_action",
            json={"action": "invalid"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with missing required fields
        response = client.post(
            "/api/v2/consciousness/query",
            json={},  # Missing 'query' field
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_request_tracking(self, api_system):
        """Test request tracking middleware"""
        client = TestClient(api_system.app)

        # Make a request
        response = client.get("/api/v2/health")
        assert response.status_code == 200

        # Check request was tracked
        assert api_system.request_counter > 0


class TestLUKHASClient:
    """Test LUKHAS API client SDK"""

    @pytest.fixture
    def mock_session(self):
        """Mock aiohttp session"""
        from unittest.mock import MagicMock

        # Create response mock
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(
            return_value={"status": "success", "result": {"test": "data"}}
        )

        # Create session mock with proper async context manager
        session = MagicMock()

        # Make request return an object with async context manager methods
        request_cm = MagicMock()
        request_cm.__aenter__ = AsyncMock(return_value=response)
        request_cm.__aexit__ = AsyncMock(return_value=None)

        session.request = MagicMock(return_value=request_cm)
        return session

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization"""
        async with LUKHASClient("http://localhost:8000", api_key="test_key") as client:
            assert client.base_url == "http://localhost:8000"
            assert client.api_key == "test_key"
            assert client.session is not None

    @pytest.mark.asyncio
    async def test_consciousness_client(self, mock_session):
        """Test consciousness client methods"""
        client = LUKHASClient("http://localhost:8000")
        client.session = mock_session

        result = await client.consciousness.query("Test query")

        assert result == {"test": "data"}
        mock_session.request.assert_called_once()

        # Check request parameters
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/consciousness/query" in call_args[1]["url"]

    @pytest.mark.asyncio
    async def test_memory_client(self, mock_session):
        """Test memory client methods"""
        client = LUKHASClient("http://localhost:8000")
        client.session = mock_session

        # Mock response for store
        mock_session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                "status": "success",
                "result": {"memory_id": "mem_123"},
            }
        )

        # Test store
        memory_id = await client.memory.store({"content": "test"})
        assert memory_id == "mem_123"

        # Test retrieve
        mock_session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                "status": "success",
                "result": {"results": [{"id": "mem_123"}]},
            }
        )

        results = await client.memory.retrieve("test")
        assert len(results) == 1
        assert results[0]["id"] == "mem_123"

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_session):
        """Test client error handling"""
        client = LUKHASClient("http://localhost:8000")
        client.session = mock_session

        # Mock error response
        mock_session.request.return_value.__aenter__.return_value.status = 401
        mock_session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"error": {"message": "Unauthorized"}}
        )

        with pytest.raises(APIError) as exc_info:
            await client.consciousness.query("Test")

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_client(self, mock_session):
        """Test authentication client"""
        client = LUKHASClient("http://localhost:8000")
        client.session = mock_session

        # Mock login response
        mock_session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                "session_id": "test_session",
                "jwt_token": "new_jwt_token",
                "mfa_required": False,
            }
        )

        result = await client.auth.login("test_user", "password")

        assert result["session_id"] == "test_session"
        assert client.jwt_token == "new_jwt_token"  # Token should be updated

    @pytest.mark.asyncio
    async def test_system_client(self, mock_session):
        """Test system information client"""
        client = LUKHASClient("http://localhost:8000")
        client.session = mock_session

        # Test health
        mock_session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"status": "healthy", "version": "2.0.0"}
        )

        health = await client.system.health()
        assert health["status"] == "healthy"

        # Test capabilities
        mock_session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                "consciousness": {"states": ["aware", "dreaming"]},
                "memory": {"types": ["episodic", "semantic"]},
            }
        )

        capabilities = await client.system.capabilities()
        assert "consciousness" in capabilities
        assert "memory" in capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
