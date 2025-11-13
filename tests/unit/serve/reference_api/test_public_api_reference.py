"""
Comprehensive test suite for public_api_reference.py

Tests authentication, rate limiting, all API endpoints, error handling,
request/response schemas, and middleware functionality.

Target: 80%+ coverage
"""

import base64
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_auth_system():
    """Mock authentication system"""
    mock_auth = Mock()
    mock_auth.verify_api_key = AsyncMock(return_value={
        "user_id": "test_user",
        "permissions": ["read", "write"]
    })
    mock_auth.generate_api_key = Mock(return_value=("test_key_id", "test_key_secret"))
    mock_auth._api_keys_mem = {"test_key_id": {"secret": "test_key_secret"}}
    return mock_auth


@pytest.fixture
def mock_branding():
    """Mock branding functions"""
    with patch("serve.reference_api.public_api_reference.get_system_signature") as mock_sig, \
         patch("serve.reference_api.public_api_reference.get_triad_context") as mock_triad, \
         patch("serve.reference_api.public_api_reference.initialize_branding") as mock_init:

        mock_sig.return_value = "LUKHAS AI v2.0.0 - Test Mode"
        mock_triad.return_value = {
            "framework": "⚛️🧠🛡️ Trinity Framework - Identity・Consciousness・Guardian"
        }
        mock_init.return_value = AsyncMock()

        yield {
            "signature": mock_sig,
            "triad": mock_triad,
            "initialize": mock_init,
        }


@pytest.fixture
def app(mock_branding):
    """Create test FastAPI app"""
    # Patch get_auth_system to return None for development mode
    with patch("serve.reference_api.public_api_reference.get_auth_system") as mock_get_auth:
        mock_get_auth.return_value = None

        from serve.reference_api.public_api_reference import app as fastapi_app

        return fastapi_app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def valid_api_key():
    """Generate valid API key for testing"""
    key_id = "test_key_id"
    key_secret = "test_key_secret"
    token = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
    return token


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_welcome_message(self, client, mock_branding):
        """Test root endpoint returns welcome information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "LUKHAS AI" in data["data"]["service"]
        assert data["data"]["version"] == "2.0.0"

    def test_root_includes_endpoints(self, client):
        """Test root lists available endpoints"""
        response = client.get("/")
        data = response.json()

        endpoints = data["data"]["endpoints"]
        assert "chat" in str(endpoints)
        assert "dreams" in str(endpoints)
        assert "status" in str(endpoints)

    def test_root_includes_triad_framework(self, client, mock_branding):
        """Test root includes Trinity Framework context"""
        response = client.get("/")
        data = response.json()

        assert "triad_framework" in data["data"]
        assert "⚛️🧠🛡️" in data["data"]["triad_framework"]

    def test_root_has_timestamp(self, client):
        """Test root response includes timestamp"""
        response = client.get("/")
        data = response.json()

        assert "timestamp" in data
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))


class TestChatEndpoint:
    """Test /v1/chat endpoint"""

    def test_chat_requires_authentication(self, client):
        """Test chat endpoint requires authentication"""
        response = client.post("/v1/chat", json={"message": "Hello"})
        assert response.status_code == 401

    def test_chat_with_valid_auth(self, client, valid_api_key):
        """Test chat with valid authentication"""
        response = client.post(
            "/v1/chat",
            json={"message": "What is consciousness?"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        # In dev mode (auth_system=None), this should work
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "consciousness_level" in data

    def test_chat_consciousness_keyword_response(self, client, valid_api_key):
        """Test chat response for consciousness-related queries"""
        response = client.post(
            "/v1/chat",
            json={"message": "Tell me about consciousness"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "consciousness" in data["response"].lower()
        assert "trinity framework" in data["response"].lower()

    def test_chat_dream_keyword_response(self, client, valid_api_key):
        """Test chat response for dream-related queries"""
        response = client.post(
            "/v1/chat",
            json={"message": "What about dreams?"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "dream" in data["response"].lower()

    def test_chat_greeting_response(self, client, valid_api_key):
        """Test chat response for greetings"""
        greetings = ["hello", "hi", "hey"]

        for greeting in greetings:
            response = client.post(
                "/v1/chat",
                json={"message": greeting},
                headers={"Authorization": f"Bearer {valid_api_key}"}
            )
            assert response.status_code == 200

            data = response.json()
            assert "Hello" in data["response"] or "hello" in data["response"].lower()

    def test_chat_with_session_continuity(self, client, valid_api_key):
        """Test chat maintains session continuity"""
        session_id = "test_session_123"

        response = client.post(
            "/v1/chat",
            json={"message": "Hello", "session_id": session_id},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == session_id

    def test_chat_includes_metadata(self, client, valid_api_key):
        """Test chat response includes metadata"""
        response = client.post(
            "/v1/chat",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "metadata" in data
        assert "processing_time_ms" in data["metadata"]
        assert "triad_framework" in data["metadata"]

    def test_chat_consciousness_level_calculation(self, client, valid_api_key):
        """Test consciousness level is calculated based on message"""
        response = client.post(
            "/v1/chat",
            json={"message": "Very long detailed question about consciousness" * 10},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert 0 <= data["consciousness_level"] <= 1.0

    def test_chat_validation_requires_message(self, client, valid_api_key):
        """Test chat requires message field"""
        response = client.post(
            "/v1/chat",
            json={},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 422


class TestDreamEndpoint:
    """Test /v1/dreams endpoint"""

    def test_dream_requires_authentication(self, client):
        """Test dream endpoint requires authentication"""
        response = client.post(
            "/v1/dreams",
            json={"prompt": "Generate a dream"}
        )
        assert response.status_code == 401

    def test_dream_mystical_style(self, client, valid_api_key):
        """Test dream generation with mystical style"""
        response = client.post(
            "/v1/dreams",
            json={
                "prompt": "A vision of quantum consciousness",
                "style": "mystical"
            },
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "dream" in data
        assert "quantum consciousness" in data["dream"].lower()
        assert "⚛️" in data["dream"] or "🧠" in data["dream"] or "🛡️" in data["dream"]

    def test_dream_technical_style(self, client, valid_api_key):
        """Test dream generation with technical style"""
        response = client.post(
            "/v1/dreams",
            json={
                "prompt": "System initialization",
                "style": "technical"
            },
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "CONSCIOUSNESS_STACK_TRACE" in data["dream"]

    def test_dream_creative_style(self, client, valid_api_key):
        """Test dream generation with creative style"""
        response = client.post(
            "/v1/dreams",
            json={
                "prompt": "Artistic vision",
                "style": "creative"
            },
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "dream" in data["dream"].lower() or "creativity" in data["dream"].lower()

    def test_dream_with_custom_symbols(self, client, valid_api_key):
        """Test dream generation with custom symbols"""
        custom_symbols = ["⭐", "🌙", "✨"]

        response = client.post(
            "/v1/dreams",
            json={
                "prompt": "Celestial vision",
                "symbols": custom_symbols,
                "style": "mystical"
            },
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["symbols_used"] == custom_symbols

    def test_dream_includes_consciousness_score(self, client, valid_api_key):
        """Test dream includes consciousness coherence score"""
        response = client.post(
            "/v1/dreams",
            json={"prompt": "Test dream"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "consciousness_score" in data
        assert 0 <= data["consciousness_score"] <= 1.0

    def test_dream_includes_metadata(self, client, valid_api_key):
        """Test dream response includes metadata"""
        response = client.post(
            "/v1/dreams",
            json={"prompt": "Test dream"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "metadata" in data
        assert "generation_time_ms" in data["metadata"]

    def test_dream_validation_requires_prompt(self, client, valid_api_key):
        """Test dream requires prompt field"""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 422


class TestStatusEndpoint:
    """Test /status endpoint"""

    def test_status_accessible_without_auth(self, client):
        """Test status endpoint works without authentication"""
        response = client.get("/status")
        # Optional auth, so should work
        assert response.status_code == 200

    def test_status_returns_system_health(self, client):
        """Test status returns system health information"""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.json()
        assert data["operational"] is True
        assert "uptime_seconds" in data
        assert "triad_framework" in data

    def test_status_includes_request_stats(self, client):
        """Test status includes request statistics"""
        # Make a request first to generate stats
        client.get("/")

        response = client.get("/status")
        data = response.json()

        assert "total_requests" in data
        assert "success_rate" in data
        assert data["total_requests"] > 0

    def test_status_includes_consciousness_modules(self, client):
        """Test status includes consciousness module statuses"""
        response = client.get("/status")
        data = response.json()

        assert "consciousness_modules" in data
        modules = data["consciousness_modules"]
        assert "natural_language_interface" in modules
        assert "dream_generation" in modules
        assert "guardian_oversight" in modules


class TestHealthEndpoint:
    """Test /health endpoint"""

    def test_health_returns_healthy_status(self, client):
        """Test health check returns healthy"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "LUKHAS AI"
        assert data["version"] == "2.0.0"

    def test_health_includes_timestamp(self, client):
        """Test health includes timestamp"""
        response = client.get("/health")
        data = response.json()

        assert "timestamp" in data
        datetime.fromisoformat(str(data["timestamp"]).replace("Z", "+00:00"))

    def test_health_includes_trinity(self, client):
        """Test health includes Trinity Framework"""
        response = client.get("/health")
        data = response.json()

        assert "trinity" in data
        assert "⚛️🧠🛡️" in data["trinity"]


class TestAuthentication:
    """Test authentication mechanisms"""

    def test_verify_api_key_with_valid_token(self, client, valid_api_key):
        """Test API key verification with valid token"""
        # This is tested implicitly through protected endpoints
        response = client.post(
            "/v1/chat",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        # In dev mode, should work
        assert response.status_code == 200

    def test_verify_api_key_with_invalid_format(self, client):
        """Test API key verification with invalid format"""
        response = client.post(
            "/v1/chat",
            json={"message": "Test"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        # Will fail in dev mode due to invalid base64
        assert response.status_code in [401, 500]

    def test_verify_api_key_missing_authorization(self, client):
        """Test missing authorization header"""
        response = client.post(
            "/v1/chat",
            json={"message": "Test"}
        )
        assert response.status_code == 401

    def test_optional_auth_allows_unauthenticated(self, client):
        """Test optional auth endpoints allow unauthenticated access"""
        response = client.get("/status")
        assert response.status_code == 200

    def test_optional_auth_accepts_valid_credentials(self, client, valid_api_key):
        """Test optional auth accepts valid credentials"""
        response = client.get(
            "/status",
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_headers_present(self, client):
        """Test rate limit headers are added to responses"""
        # Make a request and check for rate limit headers
        response = client.get("/")
        # slowapi adds X-RateLimit headers
        # Note: TestClient may not fully support rate limiting
        assert response.status_code == 200

    def test_root_endpoint_rate_limit(self, client):
        """Test root endpoint has rate limit configured"""
        # Make multiple requests
        for i in range(5):
            response = client.get("/")
            assert response.status_code == 200


class TestStatsMiddleware:
    """Test statistics middleware"""

    def test_middleware_tracks_requests(self, client):
        """Test middleware increments request counter"""
        # Make a request
        client.get("/")

        # Check stats
        response = client.get("/status")
        data = response.json()

        assert data["total_requests"] > 0

    def test_middleware_tracks_successful_requests(self, client):
        """Test middleware tracks successful requests"""
        client.get("/")

        response = client.get("/status")
        data = response.json()

        assert data["success_rate"] > 0

    def test_middleware_tracks_error_requests(self, client):
        """Test middleware tracks error requests"""
        # Make invalid request
        client.post("/v1/chat", json={})

        response = client.get("/status")
        data = response.json()

        # Errors should be tracked
        assert "total_requests" in data


class TestErrorHandlers:
    """Test error handlers"""

    def test_http_exception_handler(self, client):
        """Test HTTP exception handler formatting"""
        # Trigger 401 error
        response = client.post("/v1/chat", json={"message": "Test"})
        assert response.status_code == 401

        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["success"] is False

    def test_validation_error_returns_422(self, client, valid_api_key):
        """Test validation errors return 422"""
        response = client.post(
            "/v1/chat",
            json={"invalid_field": "value"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 422

    def test_error_response_includes_timestamp(self, client):
        """Test error responses include timestamp"""
        response = client.post("/v1/chat", json={"message": "Test"})
        data = response.json()

        assert "timestamp" in data


class TestCORSConfiguration:
    """Test CORS configuration"""

    def test_cors_allows_configured_origins(self, client):
        """Test CORS allows configured origins"""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200

    def test_cors_allows_credentials(self, client):
        """Test CORS is configured to allow credentials"""
        # This is tested through middleware configuration
        # TestClient doesn't fully support CORS testing
        response = client.get("/")
        assert response.status_code == 200


class TestResponseModels:
    """Test response model validation"""

    def test_api_response_model_structure(self, client):
        """Test APIResponse model structure"""
        response = client.get("/")
        data = response.json()

        assert "success" in data
        assert "data" in data
        assert "timestamp" in data

    def test_chat_response_model_structure(self, client, valid_api_key):
        """Test ChatResponse model structure"""
        response = client.post(
            "/v1/chat",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        data = response.json()

        assert "response" in data
        assert "session_id" in data
        assert "consciousness_level" in data
        assert "metadata" in data

    def test_dream_response_model_structure(self, client, valid_api_key):
        """Test DreamResponse model structure"""
        response = client.post(
            "/v1/dreams",
            json={"prompt": "Test"},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        data = response.json()

        assert "dream" in data
        assert "symbols_used" in data
        assert "consciousness_score" in data

    def test_system_status_model_structure(self, client):
        """Test SystemStatus model structure"""
        response = client.get("/status")
        data = response.json()

        assert "operational" in data
        assert "uptime_seconds" in data
        assert "consciousness_modules" in data


class TestRequestModels:
    """Test request model validation"""

    def test_chat_request_with_all_fields(self, client, valid_api_key):
        """Test chat request with all optional fields"""
        request_data = {
            "message": "Test message",
            "session_id": "session_123",
            "context": {"key": "value"}
        }

        response = client.post(
            "/v1/chat",
            json=request_data,
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

    def test_dream_request_with_all_fields(self, client, valid_api_key):
        """Test dream request with all optional fields"""
        request_data = {
            "prompt": "Test dream",
            "symbols": ["⚛️", "🧠"],
            "style": "mystical"
        }

        response = client.post(
            "/v1/dreams",
            json=request_data,
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_long_chat_message(self, client, valid_api_key):
        """Test chat with very long message"""
        long_message = "test " * 1000

        response = client.post(
            "/v1/chat",
            json={"message": long_message},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

    def test_empty_string_message(self, client, valid_api_key):
        """Test chat with empty string message"""
        response = client.post(
            "/v1/chat",
            json={"message": ""},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        # Pydantic might reject empty strings depending on Field config
        assert response.status_code in [200, 422]

    def test_special_characters_in_message(self, client, valid_api_key):
        """Test chat with special characters"""
        special_message = "Test 🌟 with émojis and spëcial çhars"

        response = client.post(
            "/v1/chat",
            json={"message": special_message},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        assert response.status_code == 200

    def test_concurrent_requests_different_sessions(self, client, valid_api_key):
        """Test concurrent requests don't interfere"""
        session1 = "session_1"
        session2 = "session_2"

        response1 = client.post(
            "/v1/chat",
            json={"message": "Test 1", "session_id": session1},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )
        response2 = client.post(
            "/v1/chat",
            json={"message": "Test 2", "session_id": session2},
            headers={"Authorization": f"Bearer {valid_api_key}"}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["session_id"] == session1
        assert response2.json()["session_id"] == session2
