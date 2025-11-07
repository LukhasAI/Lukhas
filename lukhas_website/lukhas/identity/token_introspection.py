#!/usr/bin/env python3
"""
LUKHAS Identity Token Introspection Service - Production Schema v1.0.0

Implements RFC 7662-style token introspection with rate limiting, Guardian validation,
and comprehensive security features for the ΛiD Token System.

Features:
- Token introspection endpoint with detailed metadata
- Rate limiting and abuse protection
- Guardian ethical validation
- Comprehensive audit logging
- Performance optimization with caching

Constellation Framework: Identity ⚛️ + Guardian 🛡️ coordination.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from .auth_service import AuthenticationService, get_auth_service
from .token_validator import ValidationContext, ValidationResult

tracer = trace.get_tracer(__name__)

# Prometheus metrics
introspection_requests_total = Counter(
    'lukhas_token_introspection_requests_total',
    'Total token introspection requests',
    ['endpoint', 'result', 'client_type']
)

introspection_latency_seconds = Histogram(
    'lukhas_token_introspection_latency_seconds',
    'Token introspection latency',
    ['endpoint'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

rate_limit_violations_total = Counter(
    'lukhas_token_introspection_rate_limit_violations_total',
    'Rate limit violations for introspection',
    ['client_id', 'violation_type']
)

active_introspection_sessions = Gauge(
    'lukhas_active_introspection_sessions_total',
    'Number of active introspection sessions'
)

logger = logging.getLogger(__name__)


@dataclass
class IntrospectionRequest:
    """
    Token introspection request structure.

    Based on RFC 7662 with LUKHAS extensions.
    """
    # Required fields
    token: str

    # Optional fields for enhanced introspection
    token_type_hint: str | None = None  # "access_token", "lid_token", etc.
    client_id: str | None = None
    client_secret: str | None = None

    # Request metadata
    client_ip: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


@dataclass
class IntrospectionResponse:
    """
    Token introspection response structure.

    RFC 7662 compliant with LUKHAS extensions.
    """
    # RFC 7662 required field
    active: bool

    # RFC 7662 optional fields
    scope: str | None = None
    client_id: str | None = None
    username: str | None = None
    token_type: str | None = None
    exp: int | None = None
    iat: int | None = None
    nbf: int | None = None
    sub: str | None = None
    aud: str | None = None
    iss: str | None = None
    jti: str | None = None

    # LUKHAS extensions
    lid_alias: str | None = None
    realm: str | None = None
    zone: str | None = None
    tier_level: int | None = None
    namespace: str | None = None
    permissions: List[str] | None = None
    guardian_approved: bool | None = None
    validation_time_ms: float | None = None

    # Error information (if active=False)
    error: str | None = None
    error_description: str | None = None


class RateLimiter:
    """
    Rate limiter for token introspection requests.

    Implements sliding window rate limiting with burst capacity.
    """

    def __init__(self, requests_per_minute: int = 100, burst_capacity: int = 20):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute per client
            burst_capacity: Maximum burst requests allowed
        """
        self.requests_per_minute = requests_per_minute
        self.burst_capacity = burst_capacity
        self._request_history: Dict[str, List[float]] = {}
        self._burst_counts: Dict[str, int] = {}
        self._last_reset: Dict[str, float] = {}

    def check_rate_limit(self, client_key: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if client is within rate limits.

        Args:
            client_key: Unique identifier for the client

        Returns:
            Tuple of (allowed, rate_limit_info)
        """
        current_time = time.time()
        minute_ago = current_time - 60

        # Initialize client tracking
        if client_key not in self._request_history:
            self._request_history[client_key] = []
            self._burst_counts[client_key] = 0
            self._last_reset[client_key] = current_time

        # Clean old requests
        self._request_history[client_key] = [
            t for t in self._request_history[client_key] if t > minute_ago
        ]

        # Reset burst counter every minute
        if current_time - self._last_reset[client_key] > 60:
            self._burst_counts[client_key] = 0
            self._last_reset[client_key] = current_time

        # Check rate limits
        recent_requests = len(self._request_history[client_key])
        burst_count = self._burst_counts[client_key]

        rate_limit_info = {
            "requests_per_minute_limit": self.requests_per_minute,
            "burst_capacity_limit": self.burst_capacity,
            "recent_requests": recent_requests,
            "burst_count": burst_count,
            "reset_time": self._last_reset[client_key] + 60
        }

        # Check burst limit
        if burst_count >= self.burst_capacity:
            rate_limit_violations_total.labels(
                client_id=client_key[:8],
                violation_type="burst_exceeded"
            ).inc()
            return False, rate_limit_info

        # Check per-minute limit
        if recent_requests >= self.requests_per_minute:
            rate_limit_violations_total.labels(
                client_id=client_key[:8],
                violation_type="rate_exceeded"
            ).inc()
            return False, rate_limit_info

        # Record request
        self._request_history[client_key].append(current_time)
        self._burst_counts[client_key] += 1

        return True, rate_limit_info


class TokenIntrospectionService:
    """
    Token introspection service implementing RFC 7662 with LUKHAS extensions.

    Provides secure token introspection with rate limiting, Guardian validation,
    and comprehensive audit logging for production use.
    """

    def __init__(
        self,
        auth_service: AuthenticationService | None = None,
        rate_limiter: RateLimiter | None = None,
        cache_ttl_seconds: int = 60
    ):
        """
        Initialize token introspection service.

        Args:
            auth_service: Authentication service instance
            rate_limiter: Rate limiter instance
            cache_ttl_seconds: Cache TTL for introspection results
        """
        self.auth_service = auth_service or get_auth_service()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.cache_ttl = cache_ttl_seconds
        self._component_id = "TokenIntrospectionService"

        # Response cache to reduce load
        self._response_cache: Dict[str, tuple[IntrospectionResponse, float]] = {}

        # Client authentication cache
        self._client_auth_cache: Dict[str, float] = {}

        logger.info(f"TokenIntrospectionService initialized with cache_ttl={cache_ttl_seconds}s")

    def introspect_token(
        self,
        request: IntrospectionRequest
    ) -> IntrospectionResponse:
        """
        Introspect token according to RFC 7662 with LUKHAS extensions.

        Args:
            request: Token introspection request

        Returns:
            Detailed introspection response
        """
        start_time = time.time()

        with tracer.start_as_current_span("token_introspection") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("token_type_hint", request.token_type_hint or "")
            span.set_attribute("client_id", request.client_id or "")

            try:
                # Generate client key for rate limiting
                client_key = self._generate_client_key(request)

                # Check rate limits
                allowed, _rate_info = self.rate_limiter.check_rate_limit(client_key)
                if not allowed:
                    span.set_attribute("rate_limited", True)
                    introspection_requests_total.labels(
                        endpoint="introspect",
                        result="rate_limited",
                        client_type=self._classify_client(request)
                    ).inc()

                    return IntrospectionResponse(
                        active=False,
                        error="rate_limit_exceeded",
                        error_description="Too many requests. Please slow down."
                    )

                # Check cache for recent introspection
                cached_response = self._check_cache(request.token)
                if cached_response:
                    span.set_attribute("cache_hit", True)
                    introspection_requests_total.labels(
                        endpoint="introspect",
                        result="cached",
                        client_type=self._classify_client(request)
                    ).inc()
                    return cached_response

                span.set_attribute("cache_hit", False)

                # Authenticate client if credentials provided
                if (request.client_id and request.client_secret) and (not self._authenticate_client(request.client_id, request.client_secret)):
                    span.set_attribute("client_auth_failed", True)
                    introspection_requests_total.labels(
                        endpoint="introspect",
                        result="unauthorized",
                        client_type="authenticated"
                    ).inc()

                    return IntrospectionResponse(
                        active=False,
                        error="invalid_client",
                        error_description="Client authentication failed"
                    )

                # Create validation context
                validation_context = ValidationContext(
                    client_ip=request.client_ip,
                    user_agent=request.user_agent,
                    expected_audience="lukhas",
                    guardian_enabled=True,
                    ethical_validation_enabled=True,
                    rate_limit_key=client_key,
                    max_requests_per_minute=100
                )

                # Validate token using ΛiD token system
                if hasattr(self.auth_service, 'validate_lid_token'):
                    validation_result = self.auth_service.validate_lid_token(
                        request.token, validation_context
                    )
                else:
                    # Fallback to general token authentication
                    auth_result = self.auth_service.authenticate_token(request.token)
                    validation_result = self._convert_auth_result_to_validation(auth_result)

                # Build introspection response
                response = self._build_introspection_response(
                    validation_result, request, start_time
                )

                # Cache successful responses
                if response.active:
                    self._cache_response(request.token, response)

                # Update metrics
                result_type = "active" if response.active else "inactive"
                introspection_requests_total.labels(
                    endpoint="introspect",
                    result=result_type,
                    client_type=self._classify_client(request)
                ).inc()

                span.set_attribute("token_active", response.active)
                span.set_attribute("tier_level", response.tier_level or 0)
                span.set_attribute("guardian_approved", response.guardian_approved or False)

                return response

            except Exception as e:
                logger.error(f"Token introspection error: {e}")

                # Update error metrics
                introspection_requests_total.labels(
                    endpoint="introspect",
                    result="error",
                    client_type=self._classify_client(request)
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                return IntrospectionResponse(
                    active=False,
                    error="server_error",
                    error_description="Internal server error during introspection"
                )

            finally:
                # Record latency
                latency = time.time() - start_time
                introspection_latency_seconds.labels(
                    endpoint="introspect"
                ).observe(latency)

    def _generate_client_key(self, request: IntrospectionRequest) -> str:
        """Generate unique client key for rate limiting."""
        if request.client_id:
            return f"client:{request.client_id}"
        elif request.client_ip:
            return f"ip:{request.client_ip}"
        else:
            # Fallback to token hash (less ideal for rate limiting)
            token_hash = hashlib.sha256(request.token.encode()).hexdigest()[:16]
            return f"token:{token_hash}"

    def _classify_client(self, request: IntrospectionRequest) -> str:
        """Classify client type for metrics."""
        if request.client_id and request.client_secret:
            return "authenticated"
        elif request.client_id:
            return "identified"
        else:
            return "anonymous"

    def _authenticate_client(self, client_id: str, client_secret: str) -> bool:
        """
        Authenticate client credentials.

        In production, this would integrate with a proper client registry.
        """
        # Check authentication cache
        cache_key = f"{client_id}:{hashlib.sha256(client_secret.encode()).hexdigest()}"
        if cache_key in self._client_auth_cache:
            cache_time = self._client_auth_cache[cache_key]
            if time.time() - cache_time < 300:  # 5 minute cache
                return True

        # Simple authentication (in production, use proper client registry)
        # For now, accept any client with non-empty credentials
        if client_id and client_secret and len(client_secret) >= 8:
            self._client_auth_cache[cache_key] = time.time()
            return True

        return False

    def _check_cache(self, token: str) -> IntrospectionResponse | None:
        """Check response cache for recent introspection."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        if token_hash not in self._response_cache:
            return None

        response, cached_at = self._response_cache[token_hash]

        # Check cache TTL
        if time.time() - cached_at > self.cache_ttl:
            del self._response_cache[token_hash]
            return None

        return response

    def _cache_response(self, token: str, response: IntrospectionResponse) -> None:
        """Cache introspection response."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self._response_cache[token_hash] = (response, time.time())

        # Limit cache size
        while len(self._response_cache) > 1000:
            oldest_key = min(self._response_cache.keys(),
                           key=lambda k: self._response_cache[k][1])
            del self._response_cache[oldest_key]

    def _build_introspection_response(
        self,
        validation_result: ValidationResult,
        request: IntrospectionRequest,
        start_time: float
    ) -> IntrospectionResponse:
        """Build introspection response from validation result."""
        if not validation_result.valid:
            return IntrospectionResponse(
                active=False,
                error=validation_result.error_code or "invalid_token",
                error_description=validation_result.error_message or "Token is not valid",
                validation_time_ms=(time.time() - start_time) * 1000
            )

        claims = validation_result.claims or {}
        parsed_alias = validation_result.parsed_alias

        # Build RFC 7662 compliant response with LUKHAS extensions
        response = IntrospectionResponse(
            active=True,
            # RFC 7662 fields
            scope=" ".join(claims.get("permissions", [])),
            client_id=request.client_id,
            username=parsed_alias.realm if parsed_alias else None,
            token_type="ΛiD_JWT",
            exp=claims.get("exp"),
            iat=claims.get("iat"),
            nbf=claims.get("nbf"),
            sub=validation_result.alias,
            aud=claims.get("aud"),
            iss=claims.get("iss"),
            jti=claims.get("jti"),
            # LUKHAS extensions
            lid_alias=validation_result.alias,
            realm=parsed_alias.realm if parsed_alias else None,
            zone=parsed_alias.zone if parsed_alias else None,
            tier_level=validation_result.tier_level.value if validation_result.tier_level else None,
            namespace=validation_result.namespace,
            permissions=claims.get("permissions", []),
            guardian_approved=validation_result.guardian_approved,
            validation_time_ms=(time.time() - start_time) * 1000
        )

        return response

    def _convert_auth_result_to_validation(self, auth_result) -> ValidationResult:
        """Convert AuthResult to ValidationResult for fallback compatibility."""
        return ValidationResult(
            valid=auth_result.success,
            error_message=auth_result.error,
            claims={"permissions": auth_result.permissions or []} if auth_result.success else None,
            alias=auth_result.user_id
        )

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics and health metrics."""
        return {
            "component": self._component_id,
            "cache_stats": {
                "response_cache_size": len(self._response_cache),
                "client_auth_cache_size": len(self._client_auth_cache),
                "cache_ttl_seconds": self.cache_ttl
            },
            "rate_limiting": {
                "requests_per_minute": self.rate_limiter.requests_per_minute,
                "burst_capacity": self.rate_limiter.burst_capacity,
                "tracked_clients": len(self.rate_limiter._request_history)
            }
        }

    def clear_caches(self) -> None:
        """Clear all caches."""
        self._response_cache.clear()
        self._client_auth_cache.clear()
        logger.info("Introspection service caches cleared")


# Convenience function for creating introspection service
def create_introspection_service(
    requests_per_minute: int = 100,
    burst_capacity: int = 20,
    cache_ttl_seconds: int = 60
) -> TokenIntrospectionService:
    """
    Create configured token introspection service.

    Args:
        requests_per_minute: Rate limit per client per minute
        burst_capacity: Burst capacity for rate limiting
        cache_ttl_seconds: Response cache TTL

    Returns:
        Configured TokenIntrospectionService
    """
    rate_limiter = RateLimiter(requests_per_minute, burst_capacity)
    return TokenIntrospectionService(
        rate_limiter=rate_limiter,
        cache_ttl_seconds=cache_ttl_seconds
    )


# Export public interface
__all__ = [
    "IntrospectionRequest",
    "IntrospectionResponse",
    "RateLimiter",
    "TokenIntrospectionService",
    "create_introspection_service"
]
