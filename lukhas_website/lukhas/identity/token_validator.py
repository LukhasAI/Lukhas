#!/usr/bin/env python3
"""
LUKHAS Identity Token Validator - Production Schema v1.0.0

Implements secure HMAC-based JWT token validation with constant-time comparison,
Guardian integration, and comprehensive observability for the ΛiD Token System.

Security Features:
- Constant-time HMAC comparison to prevent timing attacks
- Token structure validation with comprehensive error handling
- Guardian ethical validation hooks
- Rate limiting and abuse detection
- Comprehensive audit logging

Constellation Framework: Identity ⚛️ + Guardian 🛡️ + Memory 🗃️ coordination.
"""

from __future__ import annotations
import hmac
import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from opentelemetry import trace
from prometheus_client import Counter, Histogram, Gauge

from .alias_format import parse_alias, ΛiDAlias, validate_alias_format
from .token_generator import SecretProvider, _b64url_decode
from .tier_system import TierLevel, normalize_tier

tracer = trace.get_tracer(__name__)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs):
        return self
    def inc(self, amount=1):
        pass
    def observe(self, amount):
        pass
    def set(self, value):
        pass

try:
    token_validation_total = Counter(
        'lukhas_token_validation_total',
        'Total token validations',
        ['component', 'result', 'error_type']
    )
except ValueError:
    token_validation_total = MockMetric()

try:
    token_validation_latency_seconds = Histogram(
        'lukhas_token_validation_latency_seconds',
        'Token validation latency',
        ['component'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
except ValueError:
    token_validation_latency_seconds = MockMetric()

try:
    token_validation_errors_total = Counter(
        'lukhas_token_validation_errors_total',
        'Token validation errors',
        ['component', 'error_type']
    )
except ValueError:
    token_validation_errors_total = MockMetric()

try:
    active_tokens_gauge = Gauge(
        'lukhas_active_tokens_total',
        'Number of active tokens in cache',
        ['component']
    )
except ValueError:
    active_tokens_gauge = MockMetric()

try:
    guardian_validation_total = Counter(
        'lukhas_guardian_validation_total',
        'Guardian ethical validations',
        ['component', 'action', 'result']
    )
except ValueError:
    guardian_validation_total = MockMetric()

logger = logging.getLogger(__name__)


@dataclass
class ValidationContext:
    """
    Context information for token validation.

    Provides comprehensive context for validation decisions,
    Guardian integration, and audit logging.
    """
    # Request context
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None

    # Authentication context
    expected_audience: Optional[str] = None
    required_tier: Optional[TierLevel] = None
    required_permissions: Optional[List[str]] = None

    # Security context
    max_token_age_seconds: int = 3600
    allow_expired_grace_period: int = 60  # 1 minute grace period
    enforce_issuer: bool = True

    # Guardian integration
    guardian_enabled: bool = True
    ethical_validation_enabled: bool = True

    # Rate limiting context
    rate_limit_key: Optional[str] = None
    max_requests_per_minute: int = 100


@dataclass
class ValidationResult:
    """
    Comprehensive token validation result.

    Contains validation status, parsed claims, security metrics,
    and Guardian ethical assessment.
    """
    # Validation status
    valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # Token claims (if valid)
    alias: Optional[str] = None
    claims: Optional[Dict[str, Any]] = None
    parsed_alias: Optional[ΛiDAlias] = None

    # Security metrics
    validation_time_ms: float = 0.0
    token_age_seconds: Optional[float] = None
    signature_valid: bool = False
    structure_valid: bool = False

    # Guardian assessment
    guardian_approved: bool = True
    guardian_reason: Optional[str] = None
    ethical_score: Optional[float] = None

    # Metadata
    kid: Optional[str] = None
    issuer: Optional[str] = None
    tier_level: Optional[TierLevel] = None
    namespace: Optional[str] = None


class TokenValidationError(Exception):
    """Base exception for token validation errors"""

    def __init__(self, message: str, error_code: str = "validation_error"):
        super().__init__(message)
        self.error_code = error_code


class TokenExpiredError(TokenValidationError):
    """Token has expired"""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, "token_expired")


class TokenStructureError(TokenValidationError):
    """Token structure is invalid"""

    def __init__(self, message: str = "Invalid token structure"):
        super().__init__(message, "invalid_structure")


class TokenSignatureError(TokenValidationError):
    """Token signature is invalid"""

    def __init__(self, message: str = "Invalid token signature"):
        super().__init__(message, "invalid_signature")


class GuardianBlockedError(TokenValidationError):
    """Token validation blocked by Guardian"""

    def __init__(self, message: str = "Token validation blocked by Guardian"):
        super().__init__(message, "guardian_blocked")


class TokenValidator:
    """
    Secure HMAC-based JWT token validator with Guardian integration.

    Provides cryptographically secure token validation with constant-time
    comparison, comprehensive observability, and Guardian ethical validation.

    Security Features:
    - Constant-time HMAC comparison
    - Rate limiting and abuse detection
    - Comprehensive audit logging
    - Guardian ethical validation hooks
    - Namespace-aware validation
    """

    def __init__(
        self,
        secret_provider: SecretProvider,
        guardian_validator: Optional[Callable] = None,
        cache_size: int = 10000,
        cache_ttl_seconds: int = 300
    ):
        """
        Initialize token validator.

        Args:
            secret_provider: Secret key management provider
            guardian_validator: Optional Guardian validation function
            cache_size: Maximum number of tokens to cache
            cache_ttl_seconds: Cache time-to-live in seconds
        """
        self.secret_provider = secret_provider
        self.guardian_validator = guardian_validator
        self._component_id = "TokenValidator"

        # Token cache for performance (LRU-style)
        self._token_cache: Dict[str, Tuple[ValidationResult, float]] = {}
        self._cache_size = cache_size
        self._cache_ttl = cache_ttl_seconds

        # Rate limiting storage
        self._rate_limit_store: Dict[str, List[float]] = {}

        # Known token revocations (in production, this would be external)
        self._revoked_tokens: set[str] = set()

        logger.info(f"TokenValidator initialized with cache_size={cache_size}, ttl={cache_ttl_seconds}s")

    def validate(
        self,
        token: str,
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """
        Validate JWT token with comprehensive security checks.

        Args:
            token: JWT token string to validate
            context: Validation context with requirements and constraints

        Returns:
            Comprehensive validation result

        Raises:
            TokenValidationError: If validation fails with specific error types
        """
        start_time = time.time()
        context = context or ValidationContext()

        with tracer.start_as_current_span("token_validation") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("guardian_enabled", context.guardian_enabled)
            span.set_attribute("expected_audience", context.expected_audience or "")

            try:
                # Check cache first for performance
                cached_result = self._check_cache(token)
                if cached_result:
                    span.set_attribute("cache_hit", True)
                    return self._update_result_timing(cached_result, start_time)

                span.set_attribute("cache_hit", False)

                # Rate limiting check
                if context.rate_limit_key:
                    if not self._check_rate_limit(context.rate_limit_key, context.max_requests_per_minute):
                        raise TokenValidationError("Rate limit exceeded", "rate_limit_exceeded")

                # Parse and validate token structure
                header, payload, signature = self._parse_token_structure(token)

                # Validate claims structure
                claims = self._validate_claims_structure(payload)

                # Extract key information
                kid = header.get("kid")
                alias = claims.get("sub")

                if not kid:
                    raise TokenStructureError("Missing key ID in token header")

                if not alias:
                    raise TokenStructureError("Missing subject (alias) in token claims")

                # Validate alias format
                parsed_alias = self._validate_alias(alias)

                # Verify signature with constant-time comparison
                signature_valid = self._verify_signature_constant_time(
                    token, header, payload, signature, kid
                )

                if not signature_valid:
                    raise TokenSignatureError("Token signature verification failed")

                # Validate token timing
                self._validate_token_timing(claims, context)

                # Check token revocation
                if self._is_token_revoked(token, claims):
                    raise TokenValidationError("Token has been revoked", "token_revoked")

                # Guardian ethical validation
                guardian_result = self._guardian_validation(claims, context)

                # Build validation result
                result = ValidationResult(
                    valid=True,
                    alias=alias,
                    claims=claims,
                    parsed_alias=parsed_alias,
                    signature_valid=signature_valid,
                    structure_valid=True,
                    kid=kid,
                    issuer=claims.get("iss"),
                    tier_level=self._extract_tier_level(claims),
                    namespace=claims.get("lukhas_namespace", "default"),
                    guardian_approved=guardian_result["approved"],
                    guardian_reason=guardian_result.get("reason"),
                    ethical_score=guardian_result.get("score"),
                    token_age_seconds=time.time() - claims.get("iat", time.time())
                )

                # Cache successful validation
                self._cache_result(token, result)

                # Update metrics
                token_validation_total.labels(
                    component=self._component_id,
                    result="success",
                    error_type="none"
                ).inc()

                span.set_attribute("validation_success", True)
                span.set_attribute("alias", alias)
                span.set_attribute("tier_level", str(result.tier_level))
                span.set_attribute("namespace", result.namespace)

                return self._update_result_timing(result, start_time)

            except TokenValidationError as e:
                # Handle known validation errors
                error_result = ValidationResult(
                    valid=False,
                    error_code=e.error_code,
                    error_message=str(e)
                )

                # Update metrics
                token_validation_errors_total.labels(
                    component=self._component_id,
                    error_type=e.error_code
                ).inc()

                token_validation_total.labels(
                    component=self._component_id,
                    result="error",
                    error_type=e.error_code
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("error_code", e.error_code)

                return self._update_result_timing(error_result, start_time)

            except Exception as e:
                # Handle unexpected errors
                logger.error(f"Unexpected token validation error: {e}")

                error_result = ValidationResult(
                    valid=False,
                    error_code="internal_error",
                    error_message="Internal validation error"
                )

                # Update metrics
                token_validation_errors_total.labels(
                    component=self._component_id,
                    error_type="internal_error"
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                return self._update_result_timing(error_result, start_time)

    def _parse_token_structure(self, token: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
        """
        Parse JWT token structure with comprehensive validation.

        Returns:
            Tuple of (header, payload, signature)
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise TokenStructureError(f"Invalid JWT structure: expected 3 parts, got {len(parts)}")

            header_encoded, payload_encoded, signature_encoded = parts

            # Decode header
            try:
                header_bytes = _b64url_decode(header_encoded)
                header = json.loads(header_bytes.decode("utf-8"))
            except Exception as e:
                raise TokenStructureError(f"Invalid header encoding: {e}")

            # Decode payload
            try:
                payload_bytes = _b64url_decode(payload_encoded)
                payload = json.loads(payload_bytes.decode("utf-8"))
            except Exception as e:
                raise TokenStructureError(f"Invalid payload encoding: {e}")

            # Validate header structure
            if not isinstance(header, dict):
                raise TokenStructureError("Header must be a JSON object")

            if header.get("alg") != "HS256":
                raise TokenStructureError(f"Unsupported algorithm: {header.get('alg')}")

            if header.get("typ") != "JWT":
                raise TokenStructureError(f"Invalid token type: {header.get('typ')}")

            # Validate payload structure
            if not isinstance(payload, dict):
                raise TokenStructureError("Payload must be a JSON object")

            return header, payload, signature_encoded

        except TokenStructureError:
            raise
        except Exception as e:
            raise TokenStructureError(f"Token parsing failed: {e}")

    def _validate_claims_structure(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JWT claims structure and required fields.

        Args:
            claims: Token claims dictionary

        Returns:
            Validated claims dictionary
        """
        required_fields = ["iss", "sub", "aud", "iat", "exp", "jti"]
        missing_fields = [field for field in required_fields if field not in claims]

        if missing_fields:
            raise TokenStructureError(f"Missing required claims: {missing_fields}")

        # Validate claim types
        if not isinstance(claims.get("iss"), str):
            raise TokenStructureError("Issuer (iss) must be a string")

        if not isinstance(claims.get("sub"), str):
            raise TokenStructureError("Subject (sub) must be a string")

        if not isinstance(claims.get("aud"), str):
            raise TokenStructureError("Audience (aud) must be a string")

        # Validate numeric timestamps
        for field in ["iat", "exp", "nbf"]:
            if field in claims and not isinstance(claims[field], (int, float)):
                raise TokenStructureError(f"{field} must be a numeric timestamp")

        return claims

    def _validate_alias(self, alias: str) -> ΛiDAlias:
        """
        Validate ΛiD alias format and integrity.

        Args:
            alias: ΛiD alias string

        Returns:
            Parsed ΛiDAlias object
        """
        # Validate alias format
        is_valid, error_msg = validate_alias_format(alias)
        if not is_valid:
            raise TokenStructureError(f"Invalid alias format: {error_msg}")

        # Parse alias structure
        parsed = parse_alias(alias)
        if not parsed:
            raise TokenStructureError(f"Failed to parse alias: {alias}")

        return parsed

    def _verify_signature_constant_time(
        self,
        token: str,
        header: Dict[str, Any],
        payload: Dict[str, Any],
        signature_encoded: str,
        kid: str
    ) -> bool:
        """
        Verify token signature using constant-time comparison.

        Args:
            token: Complete JWT token
            header: Parsed header dictionary
            payload: Parsed payload dictionary
            signature_encoded: Base64url encoded signature
            kid: Key identifier

        Returns:
            True if signature is valid
        """
        try:
            # Get secret key
            secret = self.secret_provider.get_secret(kid)

            # Extract signing input (header.payload)
            parts = token.rsplit(".", 1)
            if len(parts) != 2:
                return False

            signing_input = parts[0].encode("utf-8")

            # Calculate expected signature
            expected_signature = hmac.new(secret, signing_input, hashlib.sha256).digest()

            # Decode provided signature
            try:
                provided_signature = _b64url_decode(signature_encoded)
            except Exception:
                return False

            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, provided_signature)

        except Exception as e:
            logger.warning(f"Signature verification error: {e}")
            return False

    def _validate_token_timing(self, claims: Dict[str, Any], context: ValidationContext) -> None:
        """
        Validate token timing constraints (expiration, not-before, etc).

        Args:
            claims: Token claims dictionary
            context: Validation context with timing requirements
        """
        current_time = time.time()

        # Check token expiration
        exp = claims.get("exp")
        if exp and current_time > (exp + context.allow_expired_grace_period):
            raise TokenExpiredError(f"Token expired at {datetime.fromtimestamp(exp, timezone.utc)}")

        # Check not-before time
        nbf = claims.get("nbf")
        if nbf and current_time < nbf:
            raise TokenValidationError(
                f"Token not valid before {datetime.fromtimestamp(nbf, timezone.utc)}",
                "not_yet_valid"
            )

        # Check issued-at time (prevent future tokens)
        iat = claims.get("iat")
        if iat and iat > (current_time + 60):  # 60 second clock skew tolerance
            raise TokenValidationError("Token issued in the future", "future_token")

        # Check maximum token age
        if iat and (current_time - iat) > context.max_token_age_seconds:
            raise TokenValidationError("Token exceeds maximum age", "token_too_old")

    def _guardian_validation(self, claims: Dict[str, Any], context: ValidationContext) -> Dict[str, Any]:
        """
        Perform Guardian ethical validation of token usage.

        Args:
            claims: Token claims dictionary
            context: Validation context

        Returns:
            Guardian validation result
        """
        if not context.guardian_enabled or not self.guardian_validator:
            return {"approved": True, "reason": "Guardian validation disabled"}

        try:
            # Prepare Guardian validation context
            guardian_context = {
                "action_type": "token_validation",
                "token_claims": claims,
                "validation_context": {
                    "client_ip": context.client_ip,
                    "user_agent": context.user_agent,
                    "expected_audience": context.expected_audience,
                    "required_tier": str(context.required_tier) if context.required_tier else None
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Call Guardian validator
            guardian_result = self.guardian_validator(guardian_context)

            # Update metrics
            guardian_validation_total.labels(
                component=self._component_id,
                action="token_validation",
                result="approved" if guardian_result.get("approved", True) else "blocked"
            ).inc()

            if not guardian_result.get("approved", True):
                raise GuardianBlockedError(guardian_result.get("reason", "Guardian validation failed"))

            return guardian_result

        except GuardianBlockedError:
            raise
        except Exception as e:
            logger.warning(f"Guardian validation error: {e}")
            # Fail open for Guardian errors unless strict mode
            if context.ethical_validation_enabled:
                raise GuardianBlockedError(f"Guardian validation error: {e}")
            return {"approved": True, "reason": f"Guardian error (fail-open): {e}"}

    def _extract_tier_level(self, claims: Dict[str, Any]) -> Optional[TierLevel]:
        """Extract and normalize tier level from token claims."""
        tier_value = claims.get("lukhas_tier")
        if tier_value is None:
            return None

        try:
            return normalize_tier(tier_value)
        except ValueError:
            logger.warning(f"Invalid tier value in token: {tier_value}")
            return None

    def _check_cache(self, token: str) -> Optional[ValidationResult]:
        """Check token cache for previous validation result."""
        if token not in self._token_cache:
            return None

        result, cached_at = self._token_cache[token]

        # Check cache TTL
        if time.time() - cached_at > self._cache_ttl:
            del self._token_cache[token]
            return None

        return result

    def _cache_result(self, token: str, result: ValidationResult) -> None:
        """Cache validation result with LRU eviction."""
        # Only cache successful validations
        if not result.valid:
            return

        # Evict oldest entries if cache is full
        while len(self._token_cache) >= self._cache_size:
            oldest_token = min(self._token_cache.keys(),
                             key=lambda k: self._token_cache[k][1])
            del self._token_cache[oldest_token]

        self._token_cache[token] = (result, time.time())

        # Update cache metrics
        active_tokens_gauge.labels(component=self._component_id).set(len(self._token_cache))

    def _check_rate_limit(self, key: str, max_requests_per_minute: int) -> bool:
        """Check rate limiting for validation requests."""
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old entries
        if key in self._rate_limit_store:
            self._rate_limit_store[key] = [
                t for t in self._rate_limit_store[key] if t > minute_ago
            ]
        else:
            self._rate_limit_store[key] = []

        # Check rate limit
        if len(self._rate_limit_store[key]) >= max_requests_per_minute:
            return False

        # Record current request
        self._rate_limit_store[key].append(current_time)
        return True

    def _is_token_revoked(self, token: str, claims: Dict[str, Any]) -> bool:
        """Check if token has been revoked."""
        # Check by token ID (jti)
        jti = claims.get("jti")
        if jti and jti in self._revoked_tokens:
            return True

        # Check by token hash (for specific token revocation)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash in self._revoked_tokens

    def _update_result_timing(self, result: ValidationResult, start_time: float) -> ValidationResult:
        """Update result with timing information and metrics."""
        validation_time = (time.time() - start_time) * 1000  # Convert to ms
        result.validation_time_ms = validation_time

        # Update latency metrics
        token_validation_latency_seconds.labels(
            component=self._component_id
        ).observe((time.time() - start_time))

        return result

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a specific token.

        Args:
            token: JWT token to revoke

        Returns:
            True if revocation successful
        """
        try:
            # Parse token to get JTI
            _, payload, _ = self._parse_token_structure(token)
            jti = payload.get("jti")

            if jti:
                self._revoked_tokens.add(jti)

            # Also revoke by token hash
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self._revoked_tokens.add(token_hash)

            # Remove from cache if present
            if token in self._token_cache:
                del self._token_cache[token]

            logger.info(f"Token revoked: jti={jti[:8]}...")
            return True

        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get token cache statistics."""
        return {
            "cache_size": len(self._token_cache),
            "cache_limit": self._cache_size,
            "cache_ttl_seconds": self._cache_ttl,
            "revoked_tokens": len(self._revoked_tokens),
            "rate_limit_entries": len(self._rate_limit_store)
        }

    def clear_cache(self) -> None:
        """Clear all cached validation results."""
        self._token_cache.clear()
        active_tokens_gauge.labels(component=self._component_id).set(0)
        logger.info("Token validation cache cleared")

    def verify(self, token: str, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Alias for validate method for backward compatibility."""
        return self.validate(token, context)


# Export public interface
__all__ = [
    "TokenValidator",
    "ValidationContext",
    "ValidationResult",
    "TokenValidationError",
    "TokenExpiredError",
    "TokenStructureError",
    "TokenSignatureError",
    "GuardianBlockedError"
]