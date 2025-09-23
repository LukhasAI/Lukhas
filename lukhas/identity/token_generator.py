#!/usr/bin/env python3
"""
LUKHAS Identity Token Generator - Production Schema v1.0.0

Implements secure HMAC-based JWT token generation with ΛiD alias integration.
Provides cryptographically secure token creation with key rotation support.

Constellation Framework: Identity ⚛️ pillar with cross-system coordination.
"""

from __future__ import annotations
import hmac
import hashlib
import base64
import json
import time
import os
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from opentelemetry import trace
from prometheus_client import Counter, Histogram

from .alias_format import make_alias, ΛiDAlias

tracer = trace.get_tracer(__name__)

# Prometheus metrics
token_generation_total = Counter(
    'lukhas_token_generation_total',
    'Total tokens generated',
    ['component', 'realm', 'zone']
)

token_generation_latency_seconds = Histogram(
    'lukhas_token_generation_latency_seconds',
    'Token generation latency',
    ['component'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

token_generation_errors_total = Counter(
    'lukhas_token_generation_errors_total',
    'Token generation errors',
    ['component', 'error_type']
)


@dataclass
class TokenClaims:
    """
    Standard JWT claims with LUKHAS extensions.

    Provides type-safe access to token claims with validation.
    """
    # Standard JWT claims
    iss: str  # Issuer
    sub: str  # Subject (usually ΛiD alias)
    aud: str  # Audience
    iat: int  # Issued at
    exp: int  # Expiration
    nbf: int  # Not before
    jti: str  # JWT ID (unique token identifier)

    # LUKHAS-specific claims
    realm: str
    zone: str
    lukhas_tier: int = 1
    lukhas_namespace: str = "default"
    permissions: list[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.permissions is None:
            self.permissions = []


@dataclass
class TokenResponse:
    """
    Complete token generation response.

    Contains the generated token and associated metadata.
    """
    alias: str
    jwt: str
    kid: str  # Key ID used for signing
    exp: int  # Expiration timestamp
    claims: TokenClaims
    schema_version: str = "1.0.0"


def _b64url_encode(data: bytes) -> str:
    """
    Base64url encode without padding.

    Args:
        data: Bytes to encode

    Returns:
        Base64url encoded string without padding
    """
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    """
    Base64url decode with padding restoration.

    Args:
        data: Base64url encoded string

    Returns:
        Decoded bytes
    """
    # Restore padding
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class SecretProvider:
    """
    Abstract interface for secret key management.

    Enables integration with various secret management systems.
    """

    def get_secret(self, kid: str) -> bytes:
        """
        Retrieve secret key by key ID.

        Args:
            kid: Key identifier

        Returns:
            Secret key bytes

        Raises:
            KeyError: If key ID not found
        """
        raise NotImplementedError

    def get_current_kid(self) -> str:
        """
        Get current active key ID.

        Returns:
            Current key identifier
        """
        raise NotImplementedError


class EnvironmentSecretProvider(SecretProvider):
    """
    Environment-based secret provider for development and testing.

    Retrieves secrets from environment variables with fallback defaults.
    """

    def __init__(self, default_secret: str = "dev_secret_change_in_production"):
        """
        Initialize with default secret.

        Args:
            default_secret: Fallback secret for development
        """
        self.default_secret = default_secret.encode("utf-8")
        self.current_kid = "default-key-1"

    def get_secret(self, kid: str) -> bytes:
        """Retrieve secret from environment variable."""
        env_var = f"LUKHAS_SECRET_{kid.upper().replace('-', '_')}"
        secret = os.environ.get(env_var)

        if secret:
            return secret.encode("utf-8")

        # Return default for development
        if kid == self.current_kid:
            return self.default_secret

        raise KeyError(f"Secret not found for key ID: {kid}")

    def get_current_kid(self) -> str:
        """Return current key ID."""
        return self.current_kid


class TokenGenerator:
    """
    Secure HMAC-based JWT token generator with ΛiD alias integration.

    Provides cryptographically secure token creation with key rotation,
    comprehensive observability, and Guardian integration hooks.
    """

    def __init__(
        self,
        secret_provider: SecretProvider,
        kid: Optional[str] = None,
        ttl_seconds: int = 3600,
        issuer: str = "lukhas.ai"
    ):
        """
        Initialize token generator.

        Args:
            secret_provider: Secret key management provider
            kid: Optional key ID override
            ttl_seconds: Token time-to-live (default: 1 hour)
            issuer: JWT issuer claim
        """
        self.secret_provider = secret_provider
        self.kid = kid or secret_provider.get_current_kid()
        self.ttl_seconds = ttl_seconds
        self.issuer = issuer
        self._component_id = "TokenGenerator"

    def create(
        self,
        claims: Dict[str, Any],
        realm: Optional[str] = None,
        zone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> TokenResponse:
        """
        Create signed JWT token with ΛiD alias.

        Args:
            claims: Custom claims to include in token
            realm: Security realm (required if no alias provided)
            zone: Zone within realm (required if no alias provided)
            alias: Existing ΛiD alias (optional, will generate if not provided)

        Returns:
            Complete token response with JWT and metadata

        Raises:
            ValueError: If required parameters missing
            KeyError: If secret key not found
        """
        start_time = time.time()

        with tracer.start_as_current_span("token_generation") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("kid", self.kid)

            try:
                # Generate or use provided alias
                if alias:
                    # TODO: Validate existing alias format
                    final_alias = alias
                    # Extract realm/zone from alias for metrics
                    from .alias_format import parse_alias
                    parsed = parse_alias(alias)
                    if parsed:
                        realm = parsed.realm
                        zone = parsed.zone
                    else:
                        raise ValueError(f"Invalid alias format: {alias}")
                else:
                    if not realm or not zone:
                        raise ValueError("Must provide either alias or realm+zone")
                    final_alias = make_alias(realm, zone)

                # Create standard claims
                now = int(time.time())
                token_claims = TokenClaims(
                    iss=self.issuer,
                    sub=final_alias,
                    aud=claims.get("aud", "lukhas"),
                    iat=now,
                    exp=now + self.ttl_seconds,
                    nbf=now,
                    jti=f"{final_alias}-{now}",
                    realm=realm,
                    zone=zone,
                    lukhas_tier=claims.get("lukhas_tier", 1),
                    lukhas_namespace=claims.get("lukhas_namespace", "default"),
                    permissions=claims.get("permissions", [])
                )

                # Add custom claims
                token_dict = asdict(token_claims)
                for key, value in claims.items():
                    if key not in token_dict:
                        token_dict[key] = value

                # Create JWT
                jwt_token = self._create_jwt(token_dict)

                # Update metrics
                token_generation_total.labels(
                    component=self._component_id,
                    realm=realm,
                    zone=zone
                ).inc()

                processing_time = time.time() - start_time
                token_generation_latency_seconds.labels(
                    component=self._component_id
                ).observe(processing_time)

                span.set_attribute("alias", final_alias)
                span.set_attribute("realm", realm)
                span.set_attribute("zone", zone)
                span.set_attribute("processing_time_ms", processing_time * 1000)

                return TokenResponse(
                    alias=final_alias,
                    jwt=jwt_token,
                    kid=self.kid,
                    exp=token_claims.exp,
                    claims=token_claims
                )

            except Exception as e:
                token_generation_errors_total.labels(
                    component=self._component_id,
                    error_type=type(e).__name__
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    def _create_jwt(self, claims: Dict[str, Any]) -> str:
        """
        Create HMAC-signed JWT token.

        Args:
            claims: Token claims dictionary

        Returns:
            Complete JWT token string
        """
        # Create header
        header = {
            "alg": "HS256",
            "typ": "JWT",
            "kid": self.kid
        }

        # Encode header and payload
        header_encoded = _b64url_encode(json.dumps(header, separators=(',', ':')).encode())
        payload_encoded = _b64url_encode(json.dumps(claims, separators=(',', ':')).encode())

        # Create signing input
        signing_input = f"{header_encoded}.{payload_encoded}".encode()

        # Get secret and create signature
        secret = self.secret_provider.get_secret(self.kid)
        signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
        signature_encoded = _b64url_encode(signature)

        return f"{signing_input.decode()}.{signature_encoded}"

    def rotate_key(self, new_kid: str) -> None:
        """
        Rotate to new signing key.

        Args:
            new_kid: New key identifier

        Raises:
            KeyError: If new key not available
        """
        # Verify new key exists
        self.secret_provider.get_secret(new_kid)

        # Update current key
        old_kid = self.kid
        self.kid = new_kid

        with tracer.start_as_current_span("key_rotation") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("old_kid", old_kid)
            span.set_attribute("new_kid", new_kid)

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics.

        Returns:
            Performance metrics dictionary
        """
        return {
            "component": self._component_id,
            "current_kid": self.kid,
            "ttl_seconds": self.ttl_seconds,
            "issuer": self.issuer
        }


# Export public interface
__all__ = [
    "TokenGenerator",
    "TokenClaims",
    "TokenResponse",
    "SecretProvider",
    "EnvironmentSecretProvider"
]