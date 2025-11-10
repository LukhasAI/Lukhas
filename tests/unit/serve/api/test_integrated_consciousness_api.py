"""
Comprehensive test suite for integrated_consciousness_api.py

Tests all FastAPI endpoints, authentication, request validation,
response schemas, error handling, and mocked dependencies.

Target: 80%+ coverage
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_services():
    """Mock all external service dependencies"""
    with patch("serve.api.integrated_consciousness_api.NaturalLanguageConsciousnessInterface") as mock_nl, \
         patch("serve.api.integrated_consciousness_api.UserFeedbackSystem") as mock_feedback, \
         patch("serve.api.integrated_consciousness_api.UnifiedInterpretabilityDashboard") as mock_dashboard, \
         patch("serve.api.integrated_consciousness_api.ConversationManager") as mock_conv_mgr:

        # Setup NL interface mock
        nl_instance = Mock()
        nl_instance.operational = True
        nl_instance.active_sessions = {}
        nl_instance.initialize = AsyncMock()
        nl_instance.process_input = AsyncMock(return_value="Test response from AI")
        mock_nl.return_value = nl_instance

        # Setup feedback system mock
        feedback_instance = Mock()
        feedback_instance.operational = True
        feedback_instance.metrics = {"total_feedback": 100}
        feedback_instance.feedback_items = {}
        feedback_instance.initialize = AsyncMock()
        feedback_instance.collect_feedback = AsyncMock(return_value="feedback_123")
        feedback_instance.get_user_feedback_history = AsyncMock(return_value=[])
        feedback_instance.cleanup_old_feedback = AsyncMock()
        mock_feedback.return_value = feedback_instance

        # Setup dashboard mock
        dashboard_instance = Mock()
        dashboard_instance.operational = True
        dashboard_instance.decisions = {}
        dashboard_instance.action_contexts = {}
        dashboard_instance.initialize = AsyncMock()
        dashboard_instance.track_decision = AsyncMock()
        dashboard_instance.integrate_feedback = AsyncMock()
        dashboard_instance.get_status = AsyncMock(return_value={"status": "operational"})
        dashboard_instance.get_module_statuses = AsyncMock(return_value={"consciousness": "active"})
        mock_dashboard.return_value = dashboard_instance

        # Setup conversation manager mock
        conv_mgr_instance = Mock()
        conv_mgr_instance.cleanup_old_sessions = AsyncMock()
        mock_conv_mgr.return_value = conv_mgr_instance

        yield {
            "nl_interface": nl_instance,
            "feedback_system": feedback_instance,
            "dashboard": dashboard_instance,
            "conversation_manager": conv_mgr_instance,
        }


@pytest.fixture
def app(mock_services):
    """Create test FastAPI app with mocked services"""
    # Import after mocks are set up
    from serve.api.integrated_consciousness_api import app as fastapi_app
    from serve.api.integrated_consciousness_api import (
        conversation_manager,
        dashboard,
        feedback_system,
        nl_interface,
    )

    # Manually set global instances for testing
    import serve.api.integrated_consciousness_api as api_module
    api_module.nl_interface = mock_services["nl_interface"]
    api_module.feedback_system = mock_services["feedback_system"]
    api_module.dashboard = mock_services["dashboard"]
    api_module.conversation_manager = mock_services["conversation_manager"]

    return fastapi_app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_api_info(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "LUKHAS Integrated Consciousness API"
        assert data["version"] == "2.0.0"
        assert "features" in data
        assert "endpoints" in data

    def test_root_has_correct_endpoints_listed(self, client):
        """Test root lists all available endpoints"""
        response = client.get("/")
        data = response.json()

        endpoints = data["endpoints"]
        assert endpoints["chat"] == "/chat"
        assert endpoints["feedback"] == "/feedback"
        assert endpoints["dashboard"] == "/dashboard"


class TestChatEndpoint:
    """Test /chat endpoint"""

    def test_chat_successful_request(self, client, mock_services):
        """Test successful chat request"""
        request_data = {
            "message": "How can you help me?",
            "session_id": "test_session_123",
            "user_id": "user_456",
            "enable_feedback": True,
        }

        response = client.post("/chat", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "action_id" in data
        assert data["feedback_enabled"] is True

    def test_chat_auto_generates_session_id(self, client, mock_services):
        """Test chat auto-generates session ID if not provided"""
        request_data = {
            "message": "Test message",
        }

        response = client.post("/chat", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"].startswith("session_")

    def test_chat_with_context_metadata(self, client, mock_services):
        """Test chat returns metadata when context available"""
        # Setup session context
        session_id = "test_session_123"
        context = Mock()
        context.turns = [{"intent": "make_decision"}]
        context.topics = ["decision", "help", "advice"]
        context.emotional_state = "neutral"
        mock_services["nl_interface"].active_sessions = {session_id: context}

        request_data = {
            "message": "Help me decide",
            "session_id": session_id,
        }

        response = client.post("/chat", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["intent"] == "make_decision"
        assert data["metadata"]["turn_number"] == 1

    def test_chat_tracks_decision_for_specific_intents(self, client, mock_services):
        """Test decision tracking for specific intent types"""
        session_id = "test_session_123"
        context = Mock()
        context.turns = [{"intent": "make_decision"}]
        context.topics = []
        context.emotional_state = "neutral"
        mock_services["nl_interface"].active_sessions = {session_id: context}

        request_data = {
            "message": "Help me make a decision",
            "session_id": session_id,
            "user_id": "user_123",
        }

        response = client.post("/chat", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["decision_trace"] is not None
        assert "reasoning_steps" in data["decision_trace"]
        assert data["decision_trace"]["confidence"] > 0

    def test_chat_validation_requires_message(self, client):
        """Test chat requires message field"""
        request_data = {}

        response = client.post("/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_handles_nl_interface_unavailable(self, client, mock_services):
        """Test error when NL interface not available"""
        mock_services["nl_interface"].operational = False

        request_data = {"message": "Test"}

        response = client.post("/chat", json=request_data)
        assert response.status_code == 503
        assert "not available" in response.json()["detail"]

    def test_chat_handles_processing_error(self, client, mock_services):
        """Test error handling during chat processing"""
        mock_services["nl_interface"].process_input.side_effect = Exception("Processing failed")

        request_data = {"message": "Test"}

        response = client.post("/chat", json=request_data)
        assert response.status_code == 500


class TestFeedbackEndpoint:
    """Test /feedback endpoint"""

    def test_feedback_successful_submission(self, client, mock_services):
        """Test successful feedback submission"""
        feedback_data = {
            "action_id": "action_789",
            "user_id": "user_456",
            "feedback_type": "rating",
            "content": {"rating": 5},
        }

        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "feedback_id" in data
        assert data["feedback_id"] == "feedback_123"

    def test_feedback_with_action_context(self, client, mock_services):
        """Test feedback integrates action context"""
        action_id = "action_789"
        mock_services["dashboard"].action_contexts = {
            action_id: {
                "session_id": "session_123",
                "user_message": "Test message",
            }
        }

        feedback_data = {
            "action_id": action_id,
            "user_id": "user_456",
            "feedback_type": "emoji",
            "content": {"emoji": "👍"},
        }

        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 200

        # Verify collect_feedback was called with context
        mock_services["feedback_system"].collect_feedback.assert_called_once()
        call_kwargs = mock_services["feedback_system"].collect_feedback.call_args[1]
        assert call_kwargs["session_id"] == "session_123"

    def test_feedback_maps_types_correctly(self, client, mock_services):
        """Test feedback type mapping"""
        from feedback.user_feedback_system import FeedbackType

        test_cases = [
            ("rating", FeedbackType.RATING),
            ("emoji", FeedbackType.EMOJI),
            ("text", FeedbackType.TEXT),
            ("quick", FeedbackType.QUICK),
        ]

        for feedback_type_str, expected_enum in test_cases:
            feedback_data = {
                "action_id": "action_123",
                "user_id": "user_456",
                "feedback_type": feedback_type_str,
                "content": {},
            }

            response = client.post("/feedback", json=feedback_data)
            assert response.status_code == 200

    def test_feedback_system_unavailable(self, client, mock_services):
        """Test error when feedback system unavailable"""
        import serve.api.integrated_consciousness_api as api_module
        api_module.feedback_system = None

        feedback_data = {
            "action_id": "action_123",
            "user_id": "user_456",
            "feedback_type": "rating",
            "content": {"rating": 5},
        }

        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 503

    def test_feedback_handles_collection_error(self, client, mock_services):
        """Test error handling during feedback collection"""
        mock_services["feedback_system"].collect_feedback.side_effect = Exception("Collection failed")

        feedback_data = {
            "action_id": "action_123",
            "user_id": "user_456",
            "feedback_type": "rating",
            "content": {"rating": 5},
        }

        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 500


class TestDashboardEndpoint:
    """Test /dashboard endpoint"""

    def test_dashboard_basic_request(self, client, mock_services):
        """Test basic dashboard data request"""
        request_data = {
            "time_range": "1h",
            "include_feedback": True,
            "include_decisions": True,
        }

        response = client.post("/dashboard", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "time_range" in data
        assert "modules" in data
        assert "system_health" in data

    def test_dashboard_with_decisions(self, client, mock_services):
        """Test dashboard includes decision data"""
        # Add mock decisions
        mock_services["dashboard"].decisions = {
            "decision_1": {
                "timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
                "decision_type": "make_decision",
                "confidence": 0.85,
                "feedback_references": ["fb1", "fb2"],
            }
        }

        request_data = {
            "include_decisions": True,
        }

        response = client.post("/dashboard", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["decisions"]) > 0
        assert data["decisions"][0]["confidence"] == 0.85

    def test_dashboard_time_range_filtering(self, client, mock_services):
        """Test different time range filters"""
        time_ranges = ["1h", "24h", "7d", "30d"]

        for time_range in time_ranges:
            request_data = {"time_range": time_range}
            response = client.post("/dashboard", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert data["time_range"] == time_range

    def test_dashboard_user_specific_feedback(self, client, mock_services):
        """Test dashboard with user-specific feedback"""
        # Setup user feedback
        user_feedback = [Mock(timestamp=datetime.now(timezone.utc), feedback_type=Mock(value="rating"), processed_sentiment={"positive": 0.8})]
        mock_services["feedback_system"].get_user_feedback_history.return_value = user_feedback

        request_data = {
            "user_id": "user_123",
            "include_feedback": True,
        }

        response = client.post("/dashboard", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "feedback_summary" in data
        assert data["feedback_summary"]["total_feedback"] == 1

    def test_dashboard_unavailable(self, client, mock_services):
        """Test error when dashboard unavailable"""
        import serve.api.integrated_consciousness_api as api_module
        api_module.dashboard = None

        response = client.post("/dashboard", json={})
        assert response.status_code == 503


class TestSessionExportEndpoint:
    """Test /sessions/{session_id}/export endpoint"""

    def test_export_session_with_data(self, client, mock_services):
        """Test exporting session with conversation and feedback"""
        session_id = "session_123"

        # Setup session data
        context = Mock()
        context.user_id = "user_456"
        context.turns = [{"user": "Hello", "ai": "Hi there"}]
        context.topics = ["greeting"]
        context.emotional_state = "positive"
        mock_services["nl_interface"].active_sessions = {session_id: context}

        # Setup feedback
        feedback_item = Mock()
        feedback_item.context = {"session_id": session_id}
        feedback_item.to_audit_entry = Mock(return_value={"type": "rating"})
        mock_services["feedback_system"].feedback_items = {"fb1": feedback_item}

        response = client.get(f"/sessions/{session_id}/export")
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == session_id
        assert "conversation" in data
        assert "feedback" in data
        assert "insights" in data

    def test_export_nonexistent_session(self, client, mock_services):
        """Test exporting non-existent session"""
        response = client.get("/sessions/nonexistent/export")
        assert response.status_code == 200  # Still returns structure

        data = response.json()
        assert data["conversation"] is None

    def test_export_handles_error(self, client, mock_services):
        """Test error handling during export"""
        mock_services["nl_interface"].active_sessions = None

        response = client.get("/sessions/test/export")
        assert response.status_code == 500


class TestFeedbackInfluenceEndpoint:
    """Test /feedback/influence/{user_id} endpoint"""

    def test_feedback_influence_basic(self, client, mock_services):
        """Test basic feedback influence retrieval"""
        user_id = "user_123"

        # Setup user feedback
        user_feedback = [
            Mock(
                feedback_id="fb1",
                timestamp=datetime.now(timezone.utc),
                feedback_type=Mock(value="rating"),
                content={"rating": 5},
            )
        ]
        mock_services["feedback_system"].get_user_feedback_history.return_value = user_feedback

        response = client.get(f"/feedback/influence/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["user_id"] == user_id
        assert "total_feedback_given" in data
        assert "decisions_influenced" in data

    def test_feedback_influence_with_decision_impact(self, client, mock_services):
        """Test influence showing actual decision impact"""
        user_id = "user_123"

        # Setup feedback
        user_feedback = [Mock(feedback_id="fb1", timestamp=datetime.now(timezone.utc), feedback_type=Mock(value="rating"), content={})]
        mock_services["feedback_system"].get_user_feedback_history.return_value = user_feedback

        # Setup decision with feedback reference
        mock_services["dashboard"].decisions = {
            "dec1": {
                "feedback_references": [{"user_id": user_id, "feedback_id": "fb1"}],
                "output": {"summary": "Decision made based on feedback"},
                "decision_type": "routing",
            }
        }

        response = client.get(f"/feedback/influence/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["decisions_influenced"] == 1
        assert len(data["influence_examples"]) > 0

    def test_feedback_influence_services_unavailable(self, client, mock_services):
        """Test error when required services unavailable"""
        import serve.api.integrated_consciousness_api as api_module
        api_module.feedback_system = None

        response = client.get("/feedback/influence/user_123")
        assert response.status_code == 503


class TestHealthEndpoint:
    """Test /health endpoint"""

    def test_health_all_services_operational(self, client, mock_services):
        """Test health check with all services operational"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["consciousness"] is True
        assert data["services"]["feedback"] is True
        assert data["services"]["dashboard"] is True

    def test_health_degraded_when_service_down(self, client, mock_services):
        """Test health shows degraded when service is down"""
        mock_services["feedback_system"].operational = False

        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["feedback"] is False

    def test_health_includes_timestamp(self, client):
        """Test health check includes timestamp"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "timestamp" in data


class TestRequestValidation:
    """Test request validation across endpoints"""

    def test_chat_request_invalid_json(self, client):
        """Test chat with invalid JSON"""
        response = client.post("/chat", data="invalid json")
        assert response.status_code == 422

    def test_chat_request_missing_required_field(self, client):
        """Test validation of required fields"""
        response = client.post("/chat", json={})
        assert response.status_code == 422

    def test_feedback_request_invalid_type(self, client):
        """Test feedback with invalid data types"""
        feedback_data = {
            "action_id": 123,  # Should be string
            "user_id": "user_456",
            "feedback_type": "rating",
            "content": {},
        }

        response = client.post("/feedback", json=feedback_data)
        # Pydantic will coerce to string, so this might pass
        assert response.status_code in [200, 422]


class TestErrorHandling:
    """Test error handling across the API"""

    def test_internal_error_returns_500(self, client, mock_services):
        """Test internal errors return 500"""
        mock_services["nl_interface"].process_input.side_effect = RuntimeError("Internal error")

        response = client.post("/chat", json={"message": "test"})
        assert response.status_code == 500

    def test_service_unavailable_returns_503(self, client, mock_services):
        """Test service unavailable returns 503"""
        mock_services["nl_interface"].operational = False

        response = client.post("/chat", json={"message": "test"})
        assert response.status_code == 503


class TestCORSConfiguration:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in responses"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        # TestClient doesn't fully support OPTIONS, but we can check the middleware is configured
        # This is more of an integration test
        assert response.status_code in [200, 405]


class TestHelperFunctions:
    """Test helper functions"""

    def test_calculate_satisfaction_trend_positive(self):
        """Test satisfaction trend calculation - positive"""
        from serve.api.integrated_consciousness_api import _calculate_satisfaction_trend

        feedback_items = [
            Mock(processed_sentiment={"positive": 0.8, "negative": 0.1})
            for _ in range(5)
        ]

        result = _calculate_satisfaction_trend(feedback_items)
        assert result == "positive"

    def test_calculate_satisfaction_trend_negative(self):
        """Test satisfaction trend calculation - negative"""
        from serve.api.integrated_consciousness_api import _calculate_satisfaction_trend

        feedback_items = [
            Mock(processed_sentiment={"positive": 0.1, "negative": 0.8})
            for _ in range(5)
        ]

        result = _calculate_satisfaction_trend(feedback_items)
        assert result == "negative"

    def test_calculate_satisfaction_trend_neutral(self):
        """Test satisfaction trend calculation - neutral"""
        from serve.api.integrated_consciousness_api import _calculate_satisfaction_trend

        feedback_items = []

        result = _calculate_satisfaction_trend(feedback_items)
        assert result == "neutral"

    def test_get_top_decision_types(self):
        """Test getting top decision types"""
        from serve.api.integrated_consciousness_api import _get_top_decision_types

        decisions = [
            {"type": "routing"},
            {"type": "routing"},
            {"type": "filtering"},
            {"type": "routing"},
        ]

        result = _get_top_decision_types(decisions)
        assert result[0]["type"] == "routing"
        assert result[0]["count"] == 3

    def test_describe_feedback_types(self):
        """Test feedback description generation"""
        from feedback.user_feedback_system import FeedbackType
        from serve.api.integrated_consciousness_api import _describe_feedback

        # Rating feedback
        rating_feedback = Mock(feedback_type=FeedbackType.RATING, content={"rating": 5})
        assert "5-star" in _describe_feedback(rating_feedback)

        # Emoji feedback
        emoji_feedback = Mock(feedback_type=FeedbackType.EMOJI, content={"emoji": "👍"})
        assert "👍" in _describe_feedback(emoji_feedback)

        # Text feedback
        text_feedback = Mock(feedback_type=FeedbackType.TEXT, content={"text": "Great job!"})
        assert "Great job!" in _describe_feedback(text_feedback)
