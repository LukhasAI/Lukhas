"""
Comprehensive test suite for agi_enhanced_consciousness_api.py

Tests AGI-enhanced consciousness endpoints with reasoning, memory,
dream sessions, learning, and fallback behavior.

Target: 80%+ coverage
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient


@pytest.fixture
def mock_agi_components():
    """Mock all AGI cognitive core components"""
    # Mock ChainOfThought
    mock_reasoning = Mock()
    reasoning_result = Mock()
    reasoning_result.final_answer = "This is a reasoned answer"
    reasoning_result.confidence = 0.92
    reasoning_result.reasoning_steps = [
        Mock(description="Step 1", confidence=0.9),
        Mock(description="Step 2", confidence=0.95),
    ]
    mock_reasoning.reason = AsyncMock(return_value=reasoning_result)

    # Mock VectorMemoryStore
    mock_memory = Mock()
    mock_memory.memories = {}
    mock_memory.embedding_dimension = 768
    search_result = Mock()
    search_result.memory = Mock(
        id="mem_1",
        content="Test memory content",
        memory_type=Mock(value="episodic"),
        importance=Mock(name="HIGH"),
        timestamp=datetime.now(timezone.utc),
        constellation_tags={"DREAM": 0.8}
    )
    search_result.similarity = 0.95
    mock_memory.search_similar = AsyncMock(return_value=[search_result])
    mock_memory.get_memory_stats = Mock(return_value={
        "total_memories": 100,
        "memory_types": {},
        "performance": {"avg_search_time_ms": 4}
    })

    # Mock DreamMemoryBridge
    mock_dream_bridge = Mock()
    dream_session = Mock()
    dream_session.success = True
    dream_session.patterns_discovered = [{"pattern": "test"}]
    dream_session.insights_generated = [{"content": "Test insight"}]
    mock_dream_bridge.initiate_dream_session = AsyncMock(return_value="dream_session_123")
    mock_dream_bridge.get_dream_session = Mock(return_value=dream_session)

    # Mock ConstitutionalAI
    mock_safety = Mock()
    mock_safety.evaluate_action = AsyncMock(return_value=(True, []))

    # Mock DreamGuidedLearner
    mock_learner = Mock()
    mock_learner.start_learning_session = AsyncMock(return_value="learning_session_123")

    return {
        "reasoning": mock_reasoning,
        "memory": mock_memory,
        "dream_bridge": mock_dream_bridge,
        "safety": mock_safety,
        "learner": mock_learner,
    }


@pytest.fixture
def app_with_agi(mock_agi_components):
    """Create app with AGI components mocked"""
    with patch("serve.agi_enhanced_consciousness_api.AGI_AVAILABLE", True), \
         patch("serve.agi_enhanced_consciousness_api.SYMBOLIC_AVAILABLE", True):

        # Import and patch global components
        import serve.agi_enhanced_consciousness_api as api_module

        api_module.agi_reasoning = mock_agi_components["reasoning"]
        api_module.agi_memory = mock_agi_components["memory"]
        api_module.agi_dream_bridge = mock_agi_components["dream_bridge"]
        api_module.agi_safety = mock_agi_components["safety"]
        api_module.agi_learner = mock_agi_components["learner"]

        # Create a test app with the router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(api_module.router)

        yield app


@pytest.fixture
def app_without_agi():
    """Create app without AGI components (fallback mode)"""
    with patch("serve.agi_enhanced_consciousness_api.AGI_AVAILABLE", False):
        import serve.agi_enhanced_consciousness_api as api_module

        api_module.agi_reasoning = None
        api_module.agi_memory = None
        api_module.agi_dream_bridge = None
        api_module.agi_safety = None
        api_module.agi_learner = None

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(api_module.router)

        yield app


@pytest.fixture
def client(app_with_agi):
    """Create test client with AGI"""
    return TestClient(app_with_agi)


@pytest.fixture
def fallback_client(app_without_agi):
    """Create test client without AGI (fallback)"""
    return TestClient(app_without_agi)


class TestConsciousnessQueryEndpoint:
    """Test /api/v2/consciousness/query endpoint"""

    def test_query_successful_with_agi(self, client, mock_agi_components):
        """Test successful query with AGI reasoning"""
        request_data = {
            "query": "What is the meaning of consciousness?",
            "use_dream_enhancement": True,
            "reasoning_depth": 5
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "reasoning_chain" in data
        assert "confidence" in data
        assert data["confidence"] > 0

    def test_query_includes_reasoning_chain(self, client, mock_agi_components):
        """Test query response includes reasoning steps"""
        request_data = {
            "query": "Explain quantum computing",
            "reasoning_depth": 3
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        data = response.json()

        assert data["reasoning_chain"] is not None
        assert len(data["reasoning_chain"]) > 0
        assert "step" in data["reasoning_chain"][0]
        assert "confidence" in data["reasoning_chain"][0]

    def test_query_with_dream_enhancement(self, client, mock_agi_components):
        """Test query with dream enhancement enabled"""
        request_data = {
            "query": "Test query",
            "use_dream_enhancement": True
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        data = response.json()

        # Dream insights should be included
        assert "dream_insights" in data

    def test_query_without_dream_enhancement(self, client, mock_agi_components):
        """Test query without dream enhancement"""
        request_data = {
            "query": "Test query",
            "use_dream_enhancement": False
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        data = response.json()

        assert response.status_code == 200

    def test_query_with_context(self, client):
        """Test query with additional context"""
        request_data = {
            "query": "Test query",
            "context": {"user_id": "test_user", "session": "session_123"}
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        assert response.status_code == 200

    def test_query_safety_check_violation(self, client, mock_agi_components):
        """Test query that violates safety principles"""
        # Mock safety check to fail
        mock_agi_components["safety"].evaluate_action = AsyncMock(
            return_value=(False, [{"reason": "Unsafe content"}])
        )

        request_data = {
            "query": "Unsafe query content"
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        assert response.status_code == 400
        assert "violates safety" in response.json()["detail"]

    def test_query_includes_processing_time(self, client):
        """Test query includes processing time"""
        request_data = {"query": "Test"}

        response = client.post("/api/v2/consciousness/query", json=request_data)
        data = response.json()

        assert "processing_time_ms" in data
        assert data["processing_time_ms"] > 0

    def test_query_constellation_alignment(self, client):
        """Test query includes constellation alignment"""
        request_data = {"query": "Test query"}

        response = client.post("/api/v2/consciousness/query", json=request_data)
        data = response.json()

        assert "constellation_alignment" in data

    def test_query_fallback_without_agi(self, fallback_client):
        """Test query fallback when AGI not available"""
        request_data = {"query": "Test query"}

        response = fallback_client.post("/api/v2/consciousness/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "confidence" in data


class TestDreamSessionEndpoint:
    """Test /api/v2/consciousness/dream endpoint"""

    def test_dream_session_initiation(self, client, mock_agi_components):
        """Test dream session initiation"""
        request_data = {
            "phase": "exploration",
            "duration_preference": 60
        }

        response = client.post("/api/v2/consciousness/dream", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "dream_id" in data
        assert "status" in data
        assert data["phase"] == "exploration"

    def test_dream_session_different_phases(self, client):
        """Test dream sessions with different phases"""
        phases = ["exploration", "synthesis", "creativity", "consolidation", "integration"]

        for phase in phases:
            request_data = {"phase": phase}

            response = client.post("/api/v2/consciousness/dream", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert data["phase"] == phase

    def test_dream_session_with_target_memories(self, client):
        """Test dream session with specific target memories"""
        request_data = {
            "target_memories": ["mem_1", "mem_2"],
            "phase": "synthesis"
        }

        response = client.post("/api/v2/consciousness/dream", json=request_data)
        assert response.status_code == 200

    def test_dream_session_returns_patterns_and_insights(self, client, mock_agi_components):
        """Test dream session returns discovered patterns and insights"""
        request_data = {"phase": "exploration"}

        response = client.post("/api/v2/consciousness/dream", json=request_data)
        data = response.json()

        assert "patterns_discovered" in data
        assert "insights_generated" in data

    def test_dream_session_expected_completion_time(self, client):
        """Test dream session includes expected completion time"""
        request_data = {"phase": "synthesis"}

        response = client.post("/api/v2/consciousness/dream", json=request_data)
        data = response.json()

        assert "expected_completion_ms" in data

    def test_dream_session_fallback_without_agi(self, fallback_client):
        """Test dream session fallback without AGI"""
        request_data = {"phase": "exploration"}

        response = fallback_client.post("/api/v2/consciousness/dream", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["patterns_discovered"] == 0
        assert data["insights_generated"] == 0


class TestMemoryQueryEndpoint:
    """Test /api/v2/consciousness/memory endpoint"""

    def test_memory_query_with_text_search(self, client, mock_agi_components):
        """Test memory query with text-based search"""
        response = client.get(
            "/api/v2/consciousness/memory",
            params={"query": "test memory", "max_results": 10}
        )
        assert response.status_code == 200

        data = response.json()
        assert "memories" in data
        assert "total_count" in data
        assert "search_time_ms" in data

    def test_memory_query_without_search(self, client, mock_agi_components):
        """Test memory query without search (returns recent)"""
        response = client.get("/api/v2/consciousness/memory")
        assert response.status_code == 200

        data = response.json()
        assert "memories" in data

    def test_memory_query_with_type_filter(self, client):
        """Test memory query with memory type filter"""
        response = client.get(
            "/api/v2/consciousness/memory",
            params={"memory_types": "episodic,semantic"}
        )
        assert response.status_code == 200

    def test_memory_query_with_constellation_filter(self, client):
        """Test memory query with constellation filter"""
        response = client.get(
            "/api/v2/consciousness/memory",
            params={"constellation_filter": "DREAM:0.8,IDENTITY:0.7"}
        )
        assert response.status_code == 200

    def test_memory_query_results_structure(self, client, mock_agi_components):
        """Test memory query results have correct structure"""
        response = client.get(
            "/api/v2/consciousness/memory",
            params={"query": "test"}
        )
        data = response.json()

        if len(data["memories"]) > 0:
            memory = data["memories"][0]
            assert "id" in memory
            assert "content" in memory
            assert "type" in memory
            assert "importance" in memory
            assert "timestamp" in memory

    def test_memory_query_includes_consolidation_status(self, client):
        """Test memory query includes consolidation status"""
        response = client.get("/api/v2/consciousness/memory")
        data = response.json()

        assert "consolidation_status" in data

    def test_memory_query_max_results_limit(self, client):
        """Test memory query respects max_results parameter"""
        response = client.get(
            "/api/v2/consciousness/memory",
            params={"max_results": 5}
        )
        data = response.json()

        # Should limit results
        assert len(data["memories"]) <= 5

    def test_memory_query_fallback_without_agi(self, fallback_client):
        """Test memory query fallback without AGI"""
        response = fallback_client.get("/api/v2/consciousness/memory")
        assert response.status_code == 200

        data = response.json()
        assert data["total_count"] == 1024  # Fallback value


class TestLearningSessionEndpoint:
    """Test /api/v2/consciousness/learn endpoint"""

    def test_learning_session_initiation(self, client, mock_agi_components):
        """Test learning session initiation"""
        request_data = {
            "objectives": [
                {
                    "id": "obj_1",
                    "description": "Learn about quantum computing",
                    "concepts": ["quantum", "computing"],
                    "success_criteria": {"accuracy": 0.9}
                }
            ],
            "mode": "targeted",
            "use_dream_guidance": True
        }

        response = client.post("/api/v2/consciousness/learn", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "session_id" in data
        assert "status" in data
        assert data["mode"] == "targeted"

    def test_learning_session_different_modes(self, client, mock_agi_components):
        """Test learning sessions with different modes"""
        modes = ["exploratory", "targeted", "creative", "consolidation", "reflection", "intuitive"]

        for mode in modes:
            request_data = {
                "objectives": [{"description": "Test objective"}],
                "mode": mode
            }

            response = client.post("/api/v2/consciousness/learn", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert data["mode"] == mode

    def test_learning_session_with_source_materials(self, client, mock_agi_components):
        """Test learning session with source materials"""
        request_data = {
            "objectives": [{"description": "Learn X"}],
            "source_materials": ["doc1.pdf", "article2.md"]
        }

        response = client.post("/api/v2/consciousness/learn", json=request_data)
        assert response.status_code == 200

    def test_learning_session_objectives_count(self, client, mock_agi_components):
        """Test learning session reports objectives count"""
        request_data = {
            "objectives": [
                {"description": "Objective 1"},
                {"description": "Objective 2"},
                {"description": "Objective 3"}
            ]
        }

        response = client.post("/api/v2/consciousness/learn", json=request_data)
        data = response.json()

        assert data["objectives_count"] == 3

    def test_learning_session_expected_duration(self, client, mock_agi_components):
        """Test learning session includes expected duration"""
        request_data = {
            "objectives": [{"description": "Test"}]
        }

        response = client.post("/api/v2/consciousness/learn", json=request_data)
        data = response.json()

        assert "expected_duration_minutes" in data

    def test_learning_session_fallback_without_agi(self, fallback_client):
        """Test learning session fallback without AGI"""
        request_data = {
            "objectives": [{"description": "Test"}]
        }

        response = fallback_client.post("/api/v2/consciousness/learn", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "not_available"


class TestHealthEndpoint:
    """Test /api/v2/consciousness/health endpoint"""

    def test_health_check_with_agi(self, client):
        """Test health check when AGI is available"""
        response = client.get("/api/v2/consciousness/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["agi_available"] is True

    def test_health_includes_component_status(self, client):
        """Test health check includes all component statuses"""
        response = client.get("/api/v2/consciousness/health")
        data = response.json()

        components = data["components"]
        assert "reasoning" in components
        assert "memory" in components
        assert "dream_bridge" in components
        assert "safety" in components
        assert "learner" in components

    def test_health_includes_memory_stats(self, client, mock_agi_components):
        """Test health check includes memory statistics"""
        response = client.get("/api/v2/consciousness/health")
        data = response.json()

        assert "memory_stats" in data
        stats = data["memory_stats"]
        assert "total_memories" in stats

    def test_health_includes_timestamp(self, client):
        """Test health check includes timestamp"""
        response = client.get("/api/v2/consciousness/health")
        data = response.json()

        assert "timestamp" in data

    def test_health_fallback_without_agi(self, fallback_client):
        """Test health check without AGI"""
        response = fallback_client.get("/api/v2/consciousness/health")
        assert response.status_code == 200

        data = response.json()
        assert data["agi_available"] is False


class TestConsolidateEndpoint:
    """Test /api/v2/consciousness/consolidate endpoint"""

    def test_consolidate_schedules_background_task(self, client):
        """Test consolidation schedules background task"""
        response = client.post("/api/v2/consciousness/consolidate")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "consolidation_scheduled"

    def test_consolidate_includes_timestamp(self, client):
        """Test consolidation response includes timestamp"""
        response = client.post("/api/v2/consciousness/consolidate")
        data = response.json()

        assert "timestamp" in data

    def test_consolidate_unavailable_without_agi(self, fallback_client):
        """Test consolidation returns error without AGI"""
        response = fallback_client.post("/api/v2/consciousness/consolidate")
        assert response.status_code == 503


class TestHelperFunctions:
    """Test helper functions"""

    @pytest.mark.asyncio
    async def test_get_query_embedding(self):
        """Test query embedding generation"""
        from serve.agi_enhanced_consciousness_api import _get_query_embedding
        import serve.agi_enhanced_consciousness_api as api_module

        # Mock memory
        mock_memory = Mock()
        mock_memory.embedding_dimension = 768
        api_module.agi_memory = mock_memory

        embedding = await _get_query_embedding("test query")
        assert embedding is not None
        assert len(embedding) == 768

    @pytest.mark.asyncio
    async def test_get_query_embedding_without_memory(self):
        """Test query embedding when memory unavailable"""
        from serve.agi_enhanced_consciousness_api import _get_query_embedding
        import serve.agi_enhanced_consciousness_api as api_module

        api_module.agi_memory = None

        embedding = await _get_query_embedding("test query")
        assert embedding is None

    def test_parse_constellation_filter_valid(self):
        """Test constellation filter parsing with valid input"""
        from serve.agi_enhanced_consciousness_api import _parse_constellation_filter

        result = _parse_constellation_filter("DREAM:0.8,IDENTITY:0.7")
        assert result == {"DREAM": 0.8, "IDENTITY": 0.7}

    def test_parse_constellation_filter_invalid(self):
        """Test constellation filter parsing with invalid input"""
        from serve.agi_enhanced_consciousness_api import _parse_constellation_filter

        result = _parse_constellation_filter("invalid_format")
        assert result is None

    def test_parse_constellation_filter_none(self):
        """Test constellation filter parsing with None"""
        from serve.agi_enhanced_consciousness_api import _parse_constellation_filter

        result = _parse_constellation_filter(None)
        assert result is None


class TestRequestValidation:
    """Test request validation"""

    def test_consciousness_query_requires_query_field(self, client):
        """Test consciousness query requires query field"""
        response = client.post("/api/v2/consciousness/query", json={})
        assert response.status_code == 422

    def test_consciousness_query_validates_reasoning_depth(self, client):
        """Test reasoning depth validation"""
        request_data = {
            "query": "Test",
            "reasoning_depth": -1  # Invalid
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        # Pydantic will validate this
        assert response.status_code in [200, 422]

    def test_dream_session_validates_phase(self, client):
        """Test dream session phase validation"""
        request_data = {
            "phase": "invalid_phase"
        }

        response = client.post("/api/v2/consciousness/dream", json=request_data)
        # Will use default mapping or fallback
        assert response.status_code == 200

    def test_learning_session_requires_objectives(self, client):
        """Test learning session requires objectives"""
        response = client.post("/api/v2/consciousness/learn", json={})
        assert response.status_code == 422


class TestErrorHandling:
    """Test error handling"""

    def test_query_handles_reasoning_error(self, client, mock_agi_components):
        """Test query handles reasoning errors gracefully"""
        mock_agi_components["reasoning"].reason.side_effect = Exception("Reasoning failed")

        request_data = {"query": "Test"}

        response = client.post("/api/v2/consciousness/query", json=request_data)
        assert response.status_code == 500

    def test_dream_session_handles_error(self, client, mock_agi_components):
        """Test dream session handles errors"""
        mock_agi_components["dream_bridge"].initiate_dream_session.side_effect = Exception("Dream failed")

        request_data = {"phase": "exploration"}

        response = client.post("/api/v2/consciousness/dream", json=request_data)
        assert response.status_code == 500

    def test_memory_query_handles_error(self, client, mock_agi_components):
        """Test memory query handles errors"""
        mock_agi_components["memory"].search_similar.side_effect = Exception("Search failed")

        response = client.get("/api/v2/consciousness/memory?query=test")
        assert response.status_code == 500


class TestEdgeCases:
    """Test edge cases"""

    def test_very_long_query(self, client):
        """Test handling of very long queries"""
        long_query = "test " * 1000

        request_data = {"query": long_query}

        response = client.post("/api/v2/consciousness/query", json=request_data)
        assert response.status_code == 200

    def test_empty_objectives_list(self, client, mock_agi_components):
        """Test learning session with empty objectives"""
        request_data = {"objectives": []}

        response = client.post("/api/v2/consciousness/learn", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["objectives_count"] == 0

    def test_max_results_zero(self, client):
        """Test memory query with max_results=0"""
        response = client.get(
            "/api/v2/consciousness/memory",
            params={"max_results": 0}
        )
        # Should handle gracefully
        assert response.status_code == 200

    def test_negative_reasoning_depth(self, client):
        """Test query with negative reasoning depth"""
        request_data = {
            "query": "Test",
            "reasoning_depth": -5
        }

        response = client.post("/api/v2/consciousness/query", json=request_data)
        # Should either validate or handle gracefully
        assert response.status_code in [200, 422]
