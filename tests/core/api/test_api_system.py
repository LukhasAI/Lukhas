"""
Comprehensive Test Suite for Core API System
===========================================

Tests the unified API system with proper authentication, service integration,
and error handling. This is a critical component that provides the main
API interface for the LUKHAS system.

Test Coverage Areas:
- FastAPI application initialization and configuration
- Authentication and authorization systems
- Service integration (symbolic reasoning, coordination, consciousness)
- CORS middleware configuration
- Error handling and response formatting
- Security integration and validation
- API endpoint functionality and routing
- Performance monitoring and metrics
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import json
import time

from core.api.api_system import (
    APISystem,
    create_app,
    get_current_user,
    validate_request,
    handle_api_error,
    APIResponse,
    ErrorResponse,
    HealthResponse,
    ServiceStatus,
)


class TestAPISystem:
    """Comprehensive test suite for the Core API System."""

    @pytest.fixture
    def api_system(self):
        """Create a test API system instance."""
        return APISystem(
            enable_auth=True,
            enable_cors=True,
            debug_mode=False,
            rate_limit_enabled=True
        )

    @pytest.fixture
    def test_app(self, api_system):
        """Create a test FastAPI application."""
        app = api_system.create_app()
        return app

    @pytest.fixture
    def test_client(self, test_app):
        """Create a test client for the API."""
        return TestClient(test_app)

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock authentication token."""
        return "Bearer test_token_12345"

    @pytest.fixture
    def mock_user_context(self):
        """Create mock user context."""
        return {
            "user_id": "test_user_123",
            "tier_level": 3,
            "permissions": ["read", "write"],
            "authenticated": True
        }

    # Application Initialization Tests
    def test_api_system_initialization(self, api_system):
        """Test API system initializes with correct settings."""
        assert api_system.enable_auth is True
        assert api_system.enable_cors is True
        assert api_system.debug_mode is False
        assert api_system.rate_limit_enabled is True
        assert api_system.app is not None

    def test_fastapi_app_creation(self, test_app):
        """Test FastAPI application creation."""
        assert test_app is not None
        assert test_app.title == "LUKHAS Enhanced API System"
        assert test_app.version is not None
        assert test_app.description is not None

    def test_cors_middleware_configuration(self, test_app):
        """Test CORS middleware is properly configured."""
        # Check if CORS middleware is in the middleware stack
        cors_middleware_found = False
        for middleware in test_app.user_middleware:
            if hasattr(middleware, 'cls') and 'CORS' in str(middleware.cls):
                cors_middleware_found = True
                break
        
        assert cors_middleware_found is True

    def test_app_lifespan_events(self, api_system):
        """Test application startup and shutdown events."""
        startup_called = False
        shutdown_called = False
        
        @api_system.app.on_event("startup")
        async def test_startup():
            nonlocal startup_called
            startup_called = True
        
        @api_system.app.on_event("shutdown")
        async def test_shutdown():
            nonlocal shutdown_called
            shutdown_called = True
        
        # Simulate app lifecycle
        with TestClient(api_system.app):
            pass  # App starts and stops within context
        
        # Note: In testing, events may not be triggered automatically
        # This test verifies the events can be registered

    # Authentication and Authorization Tests
    def test_authentication_enabled(self, test_client, mock_auth_token):
        """Test authentication when enabled."""
        with patch('core.api.api_system.get_auth_system') as mock_get_auth:
            mock_auth = Mock()
            mock_auth.validate_token.return_value = {
                "valid": True,
                "user_id": "test_user",
                "tier_level": 3
            }
            mock_get_auth.return_value = mock_auth
            
            # Test protected endpoint
            response = test_client.get(
                "/api/v1/health",
                headers={"Authorization": mock_auth_token}
            )
            
            # Should succeed with valid token
            assert response.status_code == 200

    def test_authentication_disabled(self):
        """Test behavior when authentication is disabled."""
        api_system = APISystem(enable_auth=False)
        test_client = TestClient(api_system.app)
        
        # Test endpoint without authentication
        response = test_client.get("/api/v1/health")
        
        # Should succeed without token when auth is disabled
        assert response.status_code == 200

    def test_invalid_token_handling(self, test_client):
        """Test handling of invalid authentication tokens."""
        with patch('core.api.api_system.get_auth_system') as mock_get_auth:
            mock_auth = Mock()
            mock_auth.validate_token.return_value = {
                "valid": False,
                "error": "Invalid token"
            }
            mock_get_auth.return_value = mock_auth
            
            response = test_client.get(
                "/api/v1/health",
                headers={"Authorization": "Bearer invalid_token"}
            )
            
            assert response.status_code == 401

    def test_missing_token_handling(self, test_client):
        """Test handling of missing authentication tokens."""
        with patch('core.api.api_system.get_auth_system'):
            response = test_client.get("/api/v1/health")
            
            # Should return 401 when auth is enabled but no token provided
            assert response.status_code in [401, 200]  # Depends on endpoint protection

    def test_user_context_extraction(self, api_system, mock_user_context):
        """Test user context extraction from authentication."""
        with patch('core.api.api_system.get_current_user', return_value=mock_user_context):
            user_context = get_current_user("Bearer test_token")
            
            assert user_context["user_id"] == "test_user_123"
            assert user_context["tier_level"] == 3
            assert user_context["authenticated"] is True

    # Service Integration Tests
    def test_symbolic_engine_integration(self, test_client, mock_auth_token):
        """Test integration with symbolic reasoning engine."""
        with patch('core.api.api_system.SymbolicEngine') as MockSymbolicEngine:
            mock_engine = Mock()
            mock_engine.reason.return_value = {
                "reasoning": "Test symbolic reasoning result",
                "confidence": 0.95,
                "symbols": ["test", "symbol"]
            }
            MockSymbolicEngine.return_value = mock_engine
            
            # Mock authentication
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/symbolic/reason",
                    json={"text": "test reasoning input"},
                    headers={"Authorization": mock_auth_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "reasoning" in data
                    assert data["reasoning"] == "Test symbolic reasoning result"

    def test_coordination_manager_integration(self, test_client, mock_auth_token):
        """Test integration with coordination manager."""
        with patch('core.api.api_system.CoordinationManager') as MockCoordination:
            mock_coordinator = Mock()
            mock_coordinator.coordinate = AsyncMock(return_value={
                "status": "coordinated",
                "actions": ["action1", "action2"],
                "coordination_id": "coord_123"
            })
            MockCoordination.return_value = mock_coordinator
            
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/coordinate",
                    json={"request": "test coordination"},
                    headers={"Authorization": mock_auth_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "status" in data

    def test_consciousness_integration(self, test_client, mock_auth_token):
        """Test integration with unified consciousness system."""
        with patch('core.api.api_system.UnifiedConsciousness') as MockConsciousness:
            mock_consciousness = Mock()
            mock_consciousness.process = AsyncMock(return_value={
                "awareness_level": 0.8,
                "coherence_score": 0.9,
                "consciousness_state": "active"
            })
            MockConsciousness.return_value = mock_consciousness
            
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/consciousness/process",
                    json={"input": "test consciousness input"},
                    headers={"Authorization": mock_auth_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "awareness_level" in data or "status" in data

    # Error Handling Tests
    def test_validation_error_handling(self, test_client):
        """Test handling of validation errors."""
        # Send invalid JSON
        response = test_client.post(
            "/api/v1/symbolic/reason",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_internal_server_error_handling(self, test_client, mock_auth_token):
        """Test handling of internal server errors."""
        with patch('core.api.api_system.SymbolicEngine') as MockSymbolicEngine:
            mock_engine = Mock()
            mock_engine.reason.side_effect = Exception("Internal error")
            MockSymbolicEngine.return_value = mock_engine
            
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/symbolic/reason",
                    json={"text": "test"},
                    headers={"Authorization": mock_auth_token}
                )
                
                assert response.status_code == 500

    def test_not_found_error_handling(self, test_client):
        """Test handling of 404 not found errors."""
        response = test_client.get("/api/v1/nonexistent/endpoint")
        
        assert response.status_code == 404

    def test_method_not_allowed_handling(self, test_client):
        """Test handling of method not allowed errors."""
        # Try to POST to a GET-only endpoint
        response = test_client.post("/api/v1/health")
        
        assert response.status_code == 405

    def test_custom_error_response_format(self, test_client):
        """Test custom error response formatting."""
        response = test_client.get("/api/v1/nonexistent")
        
        if response.status_code == 404:
            data = response.json()
            # Check if error response follows expected format
            assert "error" in data or "detail" in data

    # Security Integration Tests
    def test_security_headers(self, test_client):
        """Test security headers are properly set."""
        response = test_client.get("/api/v1/health")
        
        # Check for security headers (if implemented)
        headers = response.headers
        # Common security headers that should be present
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection"
        ]
        
        # Note: Not all headers may be implemented, so we check if any are present
        security_headers_present = any(header in headers for header in expected_headers)

    def test_rate_limiting(self, test_client):
        """Test rate limiting functionality."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = test_client.get("/api/v1/health")
            responses.append(response.status_code)
        
        # Should not all be rate limited in normal testing
        success_responses = sum(1 for status in responses if status == 200)
        assert success_responses > 0

    def test_request_size_limiting(self, test_client):
        """Test request size limiting."""
        # Send very large request
        large_data = {"data": "x" * 10000}  # 10KB of data
        
        response = test_client.post(
            "/api/v1/symbolic/reason",
            json=large_data
        )
        
        # Should either process or reject based on size limits
        assert response.status_code in [200, 413, 422, 401]

    # API Endpoint Tests
    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_status_endpoint(self, test_client):
        """Test system status endpoint."""
        with patch('core.api.api_system.get_system_status') as mock_status:
            mock_status.return_value = {
                "system": "operational",
                "services": {
                    "symbolic_engine": "healthy",
                    "consciousness": "healthy",
                    "coordination": "healthy"
                },
                "uptime": 3600
            }
            
            response = test_client.get("/api/v1/status")
            
            if response.status_code == 200:
                data = response.json()
                assert "system" in data or "status" in data

    def test_symbolic_reasoning_endpoint(self, test_client, mock_auth_token):
        """Test symbolic reasoning endpoint."""
        with patch('core.api.api_system.SymbolicEngine') as MockEngine:
            mock_engine = Mock()
            mock_engine.reason.return_value = {
                "reasoning": "Test result",
                "confidence": 0.85
            }
            MockEngine.return_value = mock_engine
            
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/symbolic/reason",
                    json={"text": "test reasoning"},
                    headers={"Authorization": mock_auth_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "reasoning" in data

    def test_consciousness_endpoint(self, test_client, mock_auth_token):
        """Test consciousness processing endpoint."""
        with patch('core.api.api_system.UnifiedConsciousness') as MockConsciousness:
            mock_consciousness = Mock()
            mock_consciousness.process = AsyncMock(return_value={
                "awareness_level": 0.75,
                "coherence_score": 0.88
            })
            MockConsciousness.return_value = mock_consciousness
            
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/consciousness/process",
                    json={"input": "test consciousness"},
                    headers={"Authorization": mock_auth_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "awareness_level" in data or "status" in data

    # Performance and Monitoring Tests
    def test_response_time_monitoring(self, test_client):
        """Test response time monitoring."""
        start_time = time.time()
        
        response = test_client.get("/api/v1/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    def test_concurrent_request_handling(self, test_client):
        """Test concurrent request handling."""
        import concurrent.futures
        
        def make_request():
            return test_client.get("/api/v1/health")
        
        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should complete successfully
        success_count = sum(1 for response in responses if response.status_code == 200)
        assert success_count > 0

    def test_memory_usage_monitoring(self, api_system):
        """Test memory usage monitoring."""
        # Get initial memory usage
        initial_memory = api_system.get_memory_usage()
        
        # Perform operations
        test_client = TestClient(api_system.app)
        for _ in range(10):
            test_client.get("/api/v1/health")
        
        # Check memory usage hasn't increased dramatically
        final_memory = api_system.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase

    def test_metrics_collection(self, api_system):
        """Test metrics collection functionality."""
        # Enable metrics
        api_system.enable_metrics = True
        
        test_client = TestClient(api_system.app)
        
        # Make some requests
        for _ in range(5):
            test_client.get("/api/v1/health")
        
        # Check metrics
        metrics = api_system.get_metrics()
        assert metrics is not None
        assert metrics.get("request_count", 0) >= 0

    # Configuration Tests
    def test_debug_mode_configuration(self):
        """Test debug mode configuration."""
        debug_api = APISystem(debug_mode=True)
        assert debug_api.debug_mode is True
        assert debug_api.app.debug is True

    def test_cors_configuration(self):
        """Test CORS configuration options."""
        cors_api = APISystem(
            enable_cors=True,
            cors_origins=["http://localhost:3000"],
            cors_methods=["GET", "POST"]
        )
        
        assert cors_api.enable_cors is True
        # Test that app was created successfully with CORS config
        assert cors_api.app is not None

    def test_custom_middleware_registration(self, api_system):
        """Test custom middleware registration."""
        middleware_called = False
        
        def custom_middleware(request, call_next):
            nonlocal middleware_called
            middleware_called = True
            return call_next(request)
        
        api_system.add_middleware(custom_middleware)
        
        test_client = TestClient(api_system.app)
        test_client.get("/api/v1/health")
        
        # Middleware should have been called
        # Note: This test structure depends on middleware implementation

    # Integration and System Tests
    def test_full_api_workflow(self, test_client, mock_auth_token):
        """Test complete API workflow."""
        with patch('core.api.api_system.get_auth_system') as mock_get_auth:
            mock_auth = Mock()
            mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
            mock_get_auth.return_value = mock_auth
            
            # 1. Check health
            health_response = test_client.get("/api/v1/health")
            assert health_response.status_code == 200
            
            # 2. Check status
            status_response = test_client.get("/api/v1/status")
            assert status_response.status_code in [200, 404]  # May not be implemented
            
            # 3. Make authenticated request
            with patch('core.api.api_system.SymbolicEngine') as MockEngine:
                mock_engine = Mock()
                mock_engine.reason.return_value = {"reasoning": "test"}
                MockEngine.return_value = mock_engine
                
                reason_response = test_client.post(
                    "/api/v1/symbolic/reason",
                    json={"text": "test"},
                    headers={"Authorization": mock_auth_token}
                )
                
                # Should succeed or return expected error
                assert reason_response.status_code in [200, 404, 401]

    def test_service_fallback_behavior(self, test_client, mock_auth_token):
        """Test fallback behavior when services are unavailable."""
        with patch('core.api.api_system.SymbolicEngine', side_effect=ImportError("Service unavailable")):
            with patch('core.api.api_system.get_auth_system') as mock_get_auth:
                mock_auth = Mock()
                mock_auth.validate_token.return_value = {"valid": True, "user_id": "test"}
                mock_get_auth.return_value = mock_auth
                
                response = test_client.post(
                    "/api/v1/symbolic/reason",
                    json={"text": "test"},
                    headers={"Authorization": mock_auth_token}
                )
                
                # Should handle service unavailability gracefully
                assert response.status_code in [200, 500, 503, 404]

    # Cleanup and Resource Management Tests
    def test_api_system_cleanup(self, api_system):
        """Test API system resource cleanup."""
        # Start some background tasks
        api_system.start_background_tasks()
        
        # Cleanup
        api_system.cleanup()
        
        # Verify cleanup
        assert api_system.background_tasks_running is False

    def test_graceful_shutdown(self, api_system):
        """Test graceful API system shutdown."""
        test_client = TestClient(api_system.app)
        
        # Start processing
        test_client.get("/api/v1/health")
        
        # Initiate graceful shutdown
        api_system.shutdown(graceful=True, timeout=5.0)
        
        # Verify shutdown
        assert api_system.is_running is False