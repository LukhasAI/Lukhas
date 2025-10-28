"""
Comprehensive Test Suite for API Middleware System
=================================================

Tests the API Middleware System, the security and authentication layer that
protects LUKHAS REST API endpoints. This system implements JWT validation,
API key authentication, tier-based access control, rate limiting, and
comprehensive request monitoring for secure API operations.

Test Coverage Areas:
- JWT token validation and authentication
- API key authentication and authorization
- Tier-based access control and permissions
- Rate limiting and request throttling
- Request logging and monitoring systems
- Security validation and threat detection
- Performance optimization and scalability
- Error handling and security response protocols
"""
import pytest
import time
import jwt
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from core.interfaces.api.v1.v1.rest.middleware import (
    AuthenticationMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    SecurityMiddleware,
    TierValidationMiddleware,
    validate_jwt_token,
    validate_api_key,
    check_rate_limit,
    log_api_request,
    validate_tier_access,
    create_security_headers,
)


class TestAPIMiddleware:
    """Comprehensive test suite for the API Middleware System."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI request for testing."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/v1/test"
        request.headers = {
            "Authorization": "Bearer valid_token",
            "X-API-Key": "test_api_key",
            "User-Agent": "LUKHAS-Test/1.0",
            "X-Forwarded-For": "192.168.1.100"
        }
        request.client = Mock()
        request.client.host = "192.168.1.100"
        request.state = Mock()
        request.state.user_id = "test_user_123"
        request.state.tier = "premium"
        return request

    @pytest.fixture
    def valid_jwt_token(self):
        """Create a valid JWT token for testing."""
        payload = {
            "user_id": "test_user_123",
            "tier": "premium",
            "lambda_id": "λ_test_123",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "iss": "lukhas-auth"
        }
        return jwt.encode(payload, "test_secret", algorithm="HS256")

    @pytest.fixture
    def expired_jwt_token(self):
        """Create an expired JWT token for testing."""
        payload = {
            "user_id": "test_user_123",
            "tier": "basic",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "iss": "lukhas-auth"
        }
        return jwt.encode(payload, "test_secret", algorithm="HS256")

    @pytest.fixture
    def authentication_middleware(self):
        """Create authentication middleware instance."""
        return AuthenticationMiddleware(
            jwt_secret="test_secret",
            jwt_algorithm="HS256",
            api_key_validation_enabled=True,
            tier_validation_enabled=True
        )

    @pytest.fixture
    def rate_limit_middleware(self):
        """Create rate limit middleware instance."""
        return RateLimitMiddleware(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_limit=10,
            enable_tier_based_limits=True
        )

    @pytest.fixture
    def logging_middleware(self):
        """Create logging middleware instance."""
        return LoggingMiddleware(
            log_requests=True,
            log_responses=True,
            log_performance=True,
            sensitive_fields=["Authorization", "X-API-Key"]
        )

    @pytest.fixture
    def security_middleware(self):
        """Create security middleware instance."""
        return SecurityMiddleware(
            enable_cors=True,
            enable_csrf_protection=True,
            enable_security_headers=True,
            allowed_origins=["https://lukhas.ai"],
            max_request_size=1024*1024  # 1MB
        )

    # Authentication Middleware Tests
    def test_authentication_middleware_initialization(self, authentication_middleware):
        """Test authentication middleware initializes correctly."""
        assert authentication_middleware.jwt_secret == "test_secret"
        assert authentication_middleware.jwt_algorithm == "HS256"
        assert authentication_middleware.api_key_validation_enabled is True
        assert authentication_middleware.tier_validation_enabled is True

    @pytest.mark.asyncio
    async def test_jwt_token_validation_valid(self, authentication_middleware, mock_request, valid_jwt_token):
        """Test JWT token validation with valid token."""
        # Set valid token in request
        mock_request.headers["Authorization"] = f"Bearer {valid_jwt_token}"
        
        # Validate token
        result = await authentication_middleware.validate_request(mock_request)
        
        # Verify validation success
        assert result.authentication_successful is True
        assert result.user_id == "test_user_123"
        assert result.tier == "premium"

    @pytest.mark.asyncio
    async def test_jwt_token_validation_expired(self, authentication_middleware, mock_request, expired_jwt_token):
        """Test JWT token validation with expired token."""
        # Set expired token in request
        mock_request.headers["Authorization"] = f"Bearer {expired_jwt_token}"
        
        # Validate token
        with pytest.raises(HTTPException) as exc_info:
            await authentication_middleware.validate_request(mock_request)
        
        # Verify proper error response
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_jwt_token_validation_invalid_signature(self, authentication_middleware, mock_request):
        """Test JWT token validation with invalid signature."""
        # Create token with wrong signature
        invalid_token = jwt.encode(
            {"user_id": "test", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong_secret",
            algorithm="HS256"
        )
        mock_request.headers["Authorization"] = f"Bearer {invalid_token}"
        
        # Validate token
        with pytest.raises(HTTPException) as exc_info:
            await authentication_middleware.validate_request(mock_request)
        
        # Verify proper error response
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_jwt_token_validation_malformed(self, authentication_middleware, mock_request):
        """Test JWT token validation with malformed token."""
        # Set malformed token
        mock_request.headers["Authorization"] = "Bearer invalid.token.format"
        
        # Validate token
        with pytest.raises(HTTPException) as exc_info:
            await authentication_middleware.validate_request(mock_request)
        
        # Verify proper error response
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_api_key_validation_valid(self, authentication_middleware, mock_request):
        """Test API key validation with valid key."""
        # Mock API key validation
        with patch('core.interfaces.api.v1.v1.rest.middleware.validate_api_key_format') as mock_validate:
            mock_validate.return_value = True
            
            # Set valid API key
            mock_request.headers["X-API-Key"] = "valid_api_key_123"
            mock_request.headers.pop("Authorization", None)  # Remove JWT token
            
            # Validate request
            result = await authentication_middleware.validate_request(mock_request)
            
            # Verify validation success
            assert result.authentication_successful is True

    @pytest.mark.asyncio
    async def test_api_key_validation_invalid(self, authentication_middleware, mock_request):
        """Test API key validation with invalid key."""
        # Mock API key validation
        with patch('core.interfaces.api.v1.v1.rest.middleware.validate_api_key_format') as mock_validate:
            mock_validate.return_value = False
            
            # Set invalid API key
            mock_request.headers["X-API-Key"] = "invalid_key"
            mock_request.headers.pop("Authorization", None)  # Remove JWT token
            
            # Validate request
            with pytest.raises(HTTPException) as exc_info:
                await authentication_middleware.validate_request(mock_request)
            
            # Verify proper error response
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_missing_authentication(self, authentication_middleware, mock_request):
        """Test request with missing authentication."""
        # Remove all authentication headers
        mock_request.headers.pop("Authorization", None)
        mock_request.headers.pop("X-API-Key", None)
        
        # Validate request
        with pytest.raises(HTTPException) as exc_info:
            await authentication_middleware.validate_request(mock_request)
        
        # Verify proper error response
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Rate Limiting Middleware Tests
    def test_rate_limit_middleware_initialization(self, rate_limit_middleware):
        """Test rate limit middleware initializes correctly."""
        assert rate_limit_middleware.requests_per_minute == 60
        assert rate_limit_middleware.requests_per_hour == 1000
        assert rate_limit_middleware.burst_limit == 10
        assert rate_limit_middleware.enable_tier_based_limits is True

    @pytest.mark.asyncio
    async def test_rate_limit_within_limits(self, rate_limit_middleware, mock_request):
        """Test rate limiting within allowed limits."""
        # First request should be allowed
        result = await rate_limit_middleware.check_rate_limit(mock_request)
        
        assert result.request_allowed is True
        assert result.remaining_requests > 0

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, rate_limit_middleware, mock_request):
        """Test rate limiting when limits are exceeded."""
        # Simulate many requests to exceed limit
        for _ in range(65):  # Exceed 60 requests per minute
            try:
                await rate_limit_middleware.check_rate_limit(mock_request)
            except HTTPException:
                break
        
        # Next request should be rate limited
        with pytest.raises(HTTPException) as exc_info:
            await rate_limit_middleware.check_rate_limit(mock_request)
        
        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_tier_based_rate_limiting(self, rate_limit_middleware, mock_request):
        """Test tier-based rate limiting."""
        # Test premium tier (higher limits)
        mock_request.state.tier = "premium"
        result = await rate_limit_middleware.check_rate_limit(mock_request)
        premium_limit = result.rate_limit_per_minute
        
        # Test basic tier (lower limits)
        mock_request.state.tier = "basic"
        result = await rate_limit_middleware.check_rate_limit(mock_request)
        basic_limit = result.rate_limit_per_minute
        
        # Premium should have higher limits
        assert premium_limit > basic_limit

    @pytest.mark.asyncio
    async def test_burst_protection(self, rate_limit_middleware, mock_request):
        """Test burst protection functionality."""
        # Send burst of requests
        burst_responses = []
        for _ in range(15):  # Exceed burst limit of 10
            try:
                result = await rate_limit_middleware.check_rate_limit(mock_request)
                burst_responses.append(result)
            except HTTPException as e:
                burst_responses.append(e)
        
        # Some requests should be blocked due to burst protection
        blocked_requests = [r for r in burst_responses if isinstance(r, HTTPException)]
        assert len(blocked_requests) > 0

    @pytest.mark.asyncio
    async def test_ip_based_rate_limiting(self, rate_limit_middleware):
        """Test IP-based rate limiting."""
        # Create requests from different IPs
        request1 = Mock(spec=Request)
        request1.client = Mock()
        request1.client.host = "192.168.1.100"
        request1.state = Mock()
        request1.state.tier = "basic"
        
        request2 = Mock(spec=Request)
        request2.client = Mock()
        request2.client.host = "192.168.1.101"
        request2.state = Mock()
        request2.state.tier = "basic"
        
        # Both should be allowed initially
        result1 = await rate_limit_middleware.check_rate_limit(request1)
        result2 = await rate_limit_middleware.check_rate_limit(request2)
        
        assert result1.request_allowed is True
        assert result2.request_allowed is True

    # Logging Middleware Tests
    def test_logging_middleware_initialization(self, logging_middleware):
        """Test logging middleware initializes correctly."""
        assert logging_middleware.log_requests is True
        assert logging_middleware.log_responses is True
        assert logging_middleware.log_performance is True
        assert "Authorization" in logging_middleware.sensitive_fields

    @pytest.mark.asyncio
    async def test_request_logging(self, logging_middleware, mock_request):
        """Test request logging functionality."""
        with patch('core.interfaces.api.v1.v1.rest.middleware.logger') as mock_logger:
            # Log request
            await logging_middleware.log_request(mock_request)
            
            # Verify logging was called
            mock_logger.info.assert_called()
            
            # Check that sensitive fields are masked
            log_call = mock_logger.info.call_args
            log_data = str(log_call)
            assert "Bearer valid_token" not in log_data  # Should be masked

    @pytest.mark.asyncio
    async def test_response_logging(self, logging_middleware, mock_request):
        """Test response logging functionality."""
        with patch('core.interfaces.api.v1.v1.rest.middleware.logger') as mock_logger:
            # Create mock response
            response = JSONResponse(content={"status": "success"}, status_code=200)
            
            # Log response
            await logging_middleware.log_response(mock_request, response, processing_time=0.15)
            
            # Verify logging was called
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_performance_logging(self, logging_middleware, mock_request):
        """Test performance logging functionality."""
        with patch('core.interfaces.api.v1.v1.rest.middleware.logger') as mock_logger:
            # Log performance metrics
            await logging_middleware.log_performance(
                request=mock_request,
                processing_time=0.25,
                memory_usage=128.5,
                cpu_usage=15.2
            )
            
            # Verify performance logging
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args
            log_message = str(log_call)
            assert "0.25" in log_message  # Processing time
            assert "128.5" in log_message  # Memory usage

    @pytest.mark.asyncio
    async def test_sensitive_data_masking(self, logging_middleware, mock_request):
        """Test sensitive data masking in logs."""
        # Add more sensitive data
        mock_request.headers["X-API-Key"] = "secret_api_key_123"
        mock_request.headers["Authorization"] = "Bearer secret_jwt_token"
        
        with patch('core.interfaces.api.v1.v1.rest.middleware.logger') as mock_logger:
            # Log request with sensitive data
            await logging_middleware.log_request(mock_request)
            
            # Verify sensitive data is masked
            log_call = mock_logger.info.call_args
            log_data = str(log_call)
            assert "secret_api_key_123" not in log_data
            assert "secret_jwt_token" not in log_data
            assert "***MASKED***" in log_data

    # Security Middleware Tests
    def test_security_middleware_initialization(self, security_middleware):
        """Test security middleware initializes correctly."""
        assert security_middleware.enable_cors is True
        assert security_middleware.enable_csrf_protection is True
        assert security_middleware.enable_security_headers is True
        assert "https://lukhas.ai" in security_middleware.allowed_origins

    @pytest.mark.asyncio
    async def test_security_headers_addition(self, security_middleware, mock_request):
        """Test security headers addition."""
        # Create mock response
        response = JSONResponse(content={"test": "data"})
        
        # Add security headers
        secured_response = await security_middleware.add_security_headers(mock_request, response)
        
        # Verify security headers
        assert "X-Content-Type-Options" in secured_response.headers
        assert "X-Frame-Options" in secured_response.headers
        assert "X-XSS-Protection" in secured_response.headers
        assert "Strict-Transport-Security" in secured_response.headers

    @pytest.mark.asyncio
    async def test_cors_validation(self, security_middleware, mock_request):
        """Test CORS validation."""
        # Set origin header
        mock_request.headers["Origin"] = "https://lukhas.ai"
        
        # Validate CORS
        result = await security_middleware.validate_cors(mock_request)
        
        assert result.cors_allowed is True

    @pytest.mark.asyncio
    async def test_cors_blocked(self, security_middleware, mock_request):
        """Test CORS blocking for unauthorized origins."""
        # Set unauthorized origin
        mock_request.headers["Origin"] = "https://malicious-site.com"
        
        # Validate CORS
        with pytest.raises(HTTPException) as exc_info:
            await security_middleware.validate_cors(mock_request)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_request_size_validation(self, security_middleware, mock_request):
        """Test request size validation."""
        # Mock request with large content
        mock_request.headers["Content-Length"] = "2097152"  # 2MB, exceeds 1MB limit
        
        # Validate request size
        with pytest.raises(HTTPException) as exc_info:
            await security_middleware.validate_request_size(mock_request)
        
        assert exc_info.value.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    @pytest.mark.asyncio
    async def test_csrf_protection(self, security_middleware, mock_request):
        """Test CSRF protection."""
        # Set CSRF token
        mock_request.headers["X-CSRF-Token"] = "valid_csrf_token"
        
        # Mock CSRF validation
        with patch('core.interfaces.api.v1.v1.rest.middleware.validate_csrf_token') as mock_validate:
            mock_validate.return_value = True
            
            result = await security_middleware.validate_csrf(mock_request)
            assert result.csrf_valid is True

    # Tier Validation Middleware Tests
    @pytest.mark.asyncio
    async def test_tier_validation_premium_access(self):
        """Test tier validation for premium features."""
        tier_middleware = TierValidationMiddleware()
        
        # Mock premium user request
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.tier = "premium"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/premium/feature"
        
        # Validate tier access
        result = await tier_middleware.validate_tier_access(mock_request)
        
        assert result.access_granted is True

    @pytest.mark.asyncio
    async def test_tier_validation_basic_blocked(self):
        """Test tier validation blocking basic users from premium features."""
        tier_middleware = TierValidationMiddleware()
        
        # Mock basic user request to premium endpoint
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.tier = "basic"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/premium/feature"
        
        # Validate tier access
        with pytest.raises(HTTPException) as exc_info:
            await tier_middleware.validate_tier_access(mock_request)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_tier_validation_enterprise_features(self):
        """Test tier validation for enterprise features."""
        tier_middleware = TierValidationMiddleware()
        
        # Mock enterprise user request
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.tier = "enterprise"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/enterprise/analytics"
        
        # Validate tier access
        result = await tier_middleware.validate_tier_access(mock_request)
        
        assert result.access_granted is True

    # Performance and Scalability Tests
    @pytest.mark.asyncio
    async def test_middleware_performance(self, authentication_middleware, mock_request, valid_jwt_token):
        """Test middleware performance under load."""
        mock_request.headers["Authorization"] = f"Bearer {valid_jwt_token}"
        
        start_time = time.time()
        
        # Process multiple requests
        for _ in range(50):
            await authentication_middleware.validate_request(mock_request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process quickly
        assert processing_time < 2.0  # Under 2 seconds for 50 validations
        avg_time_per_request = processing_time / 50
        assert avg_time_per_request < 0.04  # Under 40ms per request

    @pytest.mark.asyncio
    async def test_concurrent_middleware_processing(self, authentication_middleware, valid_jwt_token):
        """Test concurrent middleware processing."""
        # Create multiple mock requests
        requests = []
        for i in range(10):
            request = Mock(spec=Request)
            request.headers = {"Authorization": f"Bearer {valid_jwt_token}"}
            request.state = Mock()
            requests.append(request)
        
        # Process requests concurrently
        tasks = [authentication_middleware.validate_request(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        # Verify all requests were processed successfully
        assert len(results) == 10
        assert all(result.authentication_successful for result in results)

    def test_memory_efficiency_under_load(self, rate_limit_middleware):
        """Test memory efficiency under sustained load."""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many rate limit checks
        for i in range(100):
            # Simulate different IPs to avoid rate limiting
            mock_request = Mock(spec=Request)
            mock_request.client = Mock()
            mock_request.client.host = f"192.168.1.{i % 255}"
            mock_request.state = Mock()
            mock_request.state.tier = "basic"
            
            asyncio.run(rate_limit_middleware.check_rate_limit(mock_request))
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify reasonable memory usage
        object_growth = final_objects - initial_objects
        assert object_growth < 300  # Should not create excessive objects

    # Error Handling and Security Tests
    @pytest.mark.asyncio
    async def test_malicious_request_handling(self, security_middleware):
        """Test handling of malicious requests."""
        # Create request with malicious headers
        malicious_request = Mock(spec=Request)
        malicious_request.headers = {
            "X-Forwarded-For": "'; DROP TABLE users; --",
            "User-Agent": "<script>alert('xss')</script>",
            "Origin": "javascript:alert('xss')"
        }
        malicious_request.client = Mock()
        malicious_request.client.host = "192.168.1.100"
        
        # Should handle malicious request safely
        with pytest.raises(HTTPException):
            await security_middleware.validate_cors(malicious_request)

    @pytest.mark.asyncio
    async def test_jwt_bombing_protection(self, authentication_middleware, mock_request):
        """Test protection against JWT bombing attacks."""
        # Create extremely large JWT token
        large_payload = {"data": "x" * 10000}  # Large payload
        large_token = jwt.encode(large_payload, "test_secret", algorithm="HS256")
        
        mock_request.headers["Authorization"] = f"Bearer {large_token}"
        
        # Should reject oversized tokens
        with pytest.raises(HTTPException):
            await authentication_middleware.validate_request(mock_request)

    @pytest.mark.asyncio
    async def test_timing_attack_protection(self, authentication_middleware, mock_request):
        """Test protection against timing attacks."""
        # Measure timing for valid and invalid tokens
        valid_times = []
        invalid_times = []
        
        for _ in range(5):
            # Valid token timing
            mock_request.headers["Authorization"] = "Bearer valid_token"
            start_time = time.time()
            try:
                await authentication_middleware.validate_request(mock_request)
            except:
                pass
            valid_times.append(time.time() - start_time)
            
            # Invalid token timing
            mock_request.headers["Authorization"] = "Bearer invalid_token"
            start_time = time.time()
            try:
                await authentication_middleware.validate_request(mock_request)
            except:
                pass
            invalid_times.append(time.time() - start_time)
        
        # Timing should be relatively consistent (protection against timing attacks)
        avg_valid_time = sum(valid_times) / len(valid_times)
        avg_invalid_time = sum(invalid_times) / len(invalid_times)
        
        # Difference should be minimal (< 50% variation)
        time_difference = abs(avg_valid_time - avg_invalid_time)
        assert time_difference < max(avg_valid_time, avg_invalid_time) * 0.5

    # Integration and Compatibility Tests
    @pytest.mark.asyncio
    async def test_middleware_chain_processing(self, authentication_middleware, rate_limit_middleware, logging_middleware):
        """Test processing through complete middleware chain."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer valid_token"}
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.state = Mock()
        mock_request.state.tier = "premium"
        
        # Process through authentication
        auth_result = await authentication_middleware.validate_request(mock_request)
        assert auth_result.authentication_successful is True
        
        # Process through rate limiting
        rate_result = await rate_limit_middleware.check_rate_limit(mock_request)
        assert rate_result.request_allowed is True
        
        # Process through logging
        await logging_middleware.log_request(mock_request)
        # Logging should complete without errors

    @pytest.mark.asyncio
    async def test_middleware_error_propagation(self, authentication_middleware, mock_request):
        """Test proper error propagation through middleware."""
        # Set invalid authentication
        mock_request.headers["Authorization"] = "Bearer invalid_token"
        
        # Should propagate authentication error
        with pytest.raises(HTTPException) as exc_info:
            await authentication_middleware.validate_request(mock_request)
        
        # Error should be properly formatted
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in str(exc_info.value.detail) or exc_info.value.detail is not None

    # Cleanup and Resource Management Tests
    def test_middleware_resource_cleanup(self, rate_limit_middleware):
        """Test middleware resource cleanup."""
        # Verify no resource leaks during normal operation
        initial_cache_size = len(rate_limit_middleware._request_cache) if hasattr(rate_limit_middleware, '_request_cache') else 0
        
        # Process some requests
        for i in range(10):
            mock_request = Mock(spec=Request)
            mock_request.client = Mock()
            mock_request.client.host = f"192.168.1.{i}"
            mock_request.state = Mock()
            mock_request.state.tier = "basic"
            
            asyncio.run(rate_limit_middleware.check_rate_limit(mock_request))
        
        # Cache should not grow excessively
        final_cache_size = len(rate_limit_middleware._request_cache) if hasattr(rate_limit_middleware, '_request_cache') else 0
        assert final_cache_size - initial_cache_size <= 10  # Should not exceed reasonable bounds