#!/usr/bin/env python3
"""
OIDC Discovery Document Provider - OpenID Connect Discovery 1.0 with T4/0.01% Excellence

Provides .well-known/openid-configuration endpoint and metadata with comprehensive
security validation, performance optimization, and fail-closed design.

Features:
- OpenID Connect Discovery 1.0 specification compliance
- OIDC Basic Client Profile conformance
- Security hardening and validation
- Performance-optimized caching (<50ms discovery)
- Metadata integrity validation
- Custom LUKHAS extension support
- Fail-closed security design

T4/0.01% Excellence: Production-ready discovery with zero security bypasses
"""

from __future__ import annotations
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from urllib.parse import urlparse
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger(__name__)

@dataclass
class DiscoveryDocument:
    """OpenID Connect Discovery 1.0 compliant configuration document with security validation."""

    # REQUIRED OpenID Connect Discovery metadata
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str
    userinfo_endpoint: str
    response_types_supported: List[str]
    subject_types_supported: List[str]
    id_token_signing_alg_values_supported: List[str]

    # OAuth2 Authorization Server metadata (RFC 8414)
    scopes_supported: List[str]
    token_endpoint_auth_methods_supported: List[str]
    code_challenge_methods_supported: List[str]
    grant_types_supported: List[str]

    # LUKHAS-specific extensions
    lukhas_tier_claim: str = "lukhas_tier"
    lukhas_namespace_claim: str = "lukhas_namespace"
    lukhas_permissions_claim: str = "permissions"

    # Optional but recommended
    revocation_endpoint: Optional[str] = None
    introspection_endpoint: Optional[str] = None
    registration_endpoint: Optional[str] = None

    # Security and validation metadata
    document_hash: Optional[str] = field(default=None, init=False)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)
    expires_at: Optional[datetime] = field(default=None, init=False)
    security_validated: bool = field(default=False, init=False)
    validation_errors: List[str] = field(default_factory=list, init=False)

    def validate_security(self) -> bool:
        """Validate security configuration of discovery document."""
        self.validation_errors.clear()

        # Validate all endpoints use HTTPS
        endpoints = [
            ('issuer', self.issuer),
            ('authorization_endpoint', self.authorization_endpoint),
            ('token_endpoint', self.token_endpoint),
            ('jwks_uri', self.jwks_uri),
            ('userinfo_endpoint', self.userinfo_endpoint),
        ]

        for endpoint_name, endpoint_url in endpoints:
            if not self._validate_https_endpoint(endpoint_url, endpoint_name):
                self.validation_errors.append(f"{endpoint_name} must use HTTPS")

        # Validate response types are secure
        if 'token' in self.response_types_supported or 'id_token' in self.response_types_supported:
            self.validation_errors.append("Implicit flow response types are discouraged")

        # Validate signing algorithms exclude 'none'
        if 'none' in self.id_token_signing_alg_values_supported:
            self.validation_errors.append("'none' algorithm not allowed for ID tokens")

        # Validate PKCE is required
        if 'S256' not in self.code_challenge_methods_supported:
            self.validation_errors.append("PKCE with S256 method must be supported")

        # Validate required scopes
        if 'openid' not in self.scopes_supported:
            self.validation_errors.append("'openid' scope must be supported")

        # Validate issuer matches endpoint domains
        issuer_domain = urlparse(self.issuer).netloc
        for endpoint_name, endpoint_url in endpoints[1:]:  # Skip issuer itself
            endpoint_domain = urlparse(endpoint_url).netloc
            if endpoint_domain != issuer_domain:
                self.validation_errors.append(
                    f"{endpoint_name} domain must match issuer domain"
                )

        self.security_validated = len(self.validation_errors) == 0
        return self.security_validated

    def _validate_https_endpoint(self, url: str, name: str) -> bool:
        """Validate endpoint uses HTTPS."""
        try:
            parsed = urlparse(url)
            return parsed.scheme == 'https'
        except Exception:
            return False

    def generate_document_hash(self) -> str:
        """Generate cryptographic hash of document for integrity validation."""
        doc_dict = self.to_dict()
        # Remove dynamic fields for consistent hashing
        doc_dict.pop('lukhas_extensions', None)

        doc_json = json.dumps(doc_dict, sort_keys=True, separators=(',', ':'))
        self.document_hash = hashlib.sha256(doc_json.encode('utf-8')).hexdigest()
        return self.document_hash

    def verify_document_integrity(self, expected_hash: Optional[str] = None) -> bool:
        """Verify document integrity against stored or provided hash."""
        current_hash = self.generate_document_hash()

        if expected_hash:
            return current_hash == expected_hash
        elif self.document_hash:
            return current_hash == self.document_hash

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenID Connect Discovery JSON format with security metadata."""
        result = {}

        # Core OIDC Discovery fields
        result.update({
            "issuer": self.issuer,
            "authorization_endpoint": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "jwks_uri": self.jwks_uri,
            "userinfo_endpoint": self.userinfo_endpoint,
            "response_types_supported": self.response_types_supported,
            "subject_types_supported": self.subject_types_supported,
            "id_token_signing_alg_values_supported": self.id_token_signing_alg_values_supported,
            "scopes_supported": self.scopes_supported,
            "token_endpoint_auth_methods_supported": self.token_endpoint_auth_methods_supported,
            "code_challenge_methods_supported": self.code_challenge_methods_supported,
            "grant_types_supported": self.grant_types_supported,
        })

        # Optional endpoints
        if self.revocation_endpoint:
            result["revocation_endpoint"] = self.revocation_endpoint
        if self.introspection_endpoint:
            result["introspection_endpoint"] = self.introspection_endpoint
        if self.registration_endpoint:
            result["registration_endpoint"] = self.registration_endpoint

        # LUKHAS extensions (following OIDC extension guidelines)
        result["lukhas_extensions"] = {
            "tier_claim": self.lukhas_tier_claim,
            "namespace_claim": self.lukhas_namespace_claim,
            "permissions_claim": self.lukhas_permissions_claim,
            "tiered_auth_supported": True,
            "guardian_validation": True,
            "webauthn_supported": True,
            "fail_closed_design": True,
            "t4_excellence": True,
            "version": "1.0.0",
            "generated_at": self.generated_at.isoformat(),
            "security_validated": self.security_validated,
            "document_hash": self.document_hash
        }

        # Security metadata for monitoring
        if self.expires_at:
            result["expires_at"] = self.expires_at.isoformat()

        return result


class DiscoveryProvider:
    """
    OpenID Connect Discovery document provider with T4/0.01% Excellence.

    Features:
    - Performance-optimized caching (<50ms discovery)
    - Security validation and integrity checking
    - Fail-closed design for security errors
    - Comprehensive metadata validation
    - Production monitoring and metrics
    """

    def __init__(self, base_url: str, custom_config: Optional[Dict[str, Any]] = None):
        """
        Initialize discovery provider with security validation.

        Args:
            base_url: Base URL for the OIDC provider (e.g., https://auth.lukhas.ai)
            custom_config: Optional custom configuration overrides
        """
        self.base_url = base_url.rstrip('/')
        self.custom_config = custom_config or {}
        self.fail_closed = self.custom_config.get('fail_closed', True)

        # Caching and performance
        self._cached_document: Optional[DiscoveryDocument] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=self.custom_config.get('cache_ttl_minutes', 30))

        # Security tracking
        self._security_events: List[Dict[str, Any]] = []
        self._validation_failures = 0

        logger.info("DiscoveryProvider initialized",
                   base_url=self.base_url,
                   fail_closed=self.fail_closed,
                   cache_ttl_minutes=self._cache_ttl.total_seconds() / 60)

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get OpenID Connect Discovery document with performance and security validation."""
        start_time = time.perf_counter()

        with tracer.start_span("oidc.get_discovery_document") as span:
            try:
                # Check cache validity
                cache_valid = (
                    self._cached_document is not None and
                    self._cache_timestamp is not None and
                    datetime.now(timezone.utc) - self._cache_timestamp < self._cache_ttl
                )

                if cache_valid and self._cached_document.security_validated:
                    span.set_attribute("oidc.cache_hit", True)
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("oidc.latency_ms", latency_ms)

                    logger.debug("Discovery document cache hit",
                               latency_ms=latency_ms,
                               cache_age_minutes=(datetime.now(timezone.utc) - self._cache_timestamp).total_seconds() / 60)

                    return self._cached_document

                # Build new document
                span.set_attribute("oidc.cache_miss", True)
                document = await self._build_discovery_document()

                # Validate security
                if not document.validate_security():
                    self._validation_failures += 1

                    security_event = {
                        'event_type': 'discovery_validation_failure',
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'errors': document.validation_errors,
                        'fail_closed': self.fail_closed
                    }
                    self._security_events.append(security_event)

                    logger.error("Discovery document security validation failed",
                               errors=document.validation_errors,
                               fail_closed=self.fail_closed)

                    if self.fail_closed:
                        raise SecurityValidationError(
                            f"Discovery document security validation failed: {document.validation_errors}"
                        )

                # Generate integrity hash
                document.generate_document_hash()

                # Cache the validated document
                self._cached_document = document
                self._cache_timestamp = datetime.now(timezone.utc)

                latency_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("oidc.latency_ms", latency_ms)
                span.set_attribute("oidc.security_validated", document.security_validated)

                logger.info("Discovery document generated",
                          latency_ms=latency_ms,
                          security_validated=document.security_validated,
                          validation_errors=len(document.validation_errors))

                # Performance target validation (<50ms)
                if latency_ms > 50:
                    logger.warning("Discovery document latency exceeded target",
                                 latency_ms=latency_ms,
                                 target_ms=50)

                return document

            except Exception as e:
                logger.error("Discovery document generation error",
                           error=str(e),
                           fail_closed=self.fail_closed)

                if self.fail_closed:
                    raise

                # Return cached document if available
                if self._cached_document:
                    logger.warning("Returning cached document due to error")
                    return self._cached_document

                raise

    async def _build_discovery_document(self) -> DiscoveryDocument:
        """Build the discovery document with comprehensive security configuration."""
        # Security-hardened configuration following OpenID Connect Discovery 1.0 and T4 excellence
        config = {
            "issuer": self.base_url,
            "authorization_endpoint": f"{self.base_url}/oauth2/authorize",
            "token_endpoint": f"{self.base_url}/oauth2/token",
            "jwks_uri": f"{self.base_url}/.well-known/jwks.json",
            "userinfo_endpoint": f"{self.base_url}/oauth2/userinfo",

            # Security-hardened response types (Authorization Code Flow only)
            "response_types_supported": ["code"],

            # Subject types (public for simplicity, pairwise for privacy)
            "subject_types_supported": ["public", "pairwise"],

            # Strong signing algorithms (exclude 'none')
            "id_token_signing_alg_values_supported": ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],

            # Comprehensive scope support
            "scopes_supported": [
                "openid", "profile", "email", "phone", "address",
                "lukhas:tier", "lukhas:admin", "lukhas:identity",
                "lukhas:namespace", "lukhas:guardian"
            ],

            # Client authentication methods (secure defaults)
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic", "client_secret_post",
                "private_key_jwt", "client_secret_jwt"
            ],

            # PKCE support (S256 only for security)
            "code_challenge_methods_supported": ["S256"],

            # Grant types (secure subset)
            "grant_types_supported": ["authorization_code", "refresh_token"],

            # Token management endpoints
            "revocation_endpoint": f"{self.base_url}/oauth2/revoke",
            "introspection_endpoint": f"{self.base_url}/oauth2/introspect",
            "registration_endpoint": f"{self.base_url}/oauth2/register",
        }

        # Apply custom overrides with validation
        safe_custom_config = self._validate_custom_config(self.custom_config)
        config.update(safe_custom_config)

        # Create document with validation
        document = DiscoveryDocument(**config)

        # Set expiration for cache management
        document.expires_at = datetime.now(timezone.utc) + self._cache_ttl

        return document

    def _validate_custom_config(self, custom_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate custom configuration for security compliance."""
        safe_config = {}
        security_violations = []

        for key, value in custom_config.items():
            # Skip internal/security fields
            if key.startswith('_') or key in ['fail_closed', 'cache_ttl_minutes']:
                continue

            # Validate specific security-sensitive fields
            if key == 'response_types_supported':
                # Only allow secure response types
                safe_types = [t for t in value if t in ['code']]
                if len(safe_types) != len(value):
                    security_violations.append(
                        f"Removed insecure response types: {set(value) - set(safe_types)}"
                    )
                safe_config[key] = safe_types

            elif key == 'id_token_signing_alg_values_supported':
                # Exclude 'none' algorithm
                safe_algs = [alg for alg in value if alg != 'none']
                if 'none' in value:
                    security_violations.append("Removed 'none' algorithm from ID token signing")
                safe_config[key] = safe_algs

            elif key == 'code_challenge_methods_supported':
                # Only allow S256
                if 'S256' not in value:
                    security_violations.append("Added required S256 PKCE method")
                    safe_config[key] = ['S256'] + [m for m in value if m != 'plain']
                else:
                    safe_config[key] = [m for m in value if m != 'plain']

            elif key == 'token_endpoint_auth_methods_supported':
                # Remove 'none' if present for public clients
                secure_methods = [m for m in value if m != 'none']
                if 'none' in value:
                    security_violations.append("Removed 'none' client authentication method")
                safe_config[key] = secure_methods

            else:
                safe_config[key] = value

        if security_violations and self.fail_closed:
            logger.warning("Security violations in custom config",
                         violations=security_violations,
                         fail_closed=self.fail_closed)

        return safe_config

    def invalidate_cache(self):
        """Invalidate the cached discovery document."""
        self._cached_document = None
        self._cache_timestamp = None
        logger.info("Discovery document cache invalidated")

    async def validate_client_metadata(self, client_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate client metadata against discovery document."""
        discovery_doc = await self.get_discovery_document()
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Validate redirect URIs
        redirect_uris = client_metadata.get('redirect_uris', [])
        for uri in redirect_uris:
            if not uri.startswith('https://'):
                validation_result['errors'].append(f"Redirect URI must use HTTPS: {uri}")
                validation_result['valid'] = False

        # Validate response types
        response_types = client_metadata.get('response_types', [])
        supported_response_types = set(discovery_doc.response_types_supported)
        for response_type in response_types:
            if response_type not in supported_response_types:
                validation_result['errors'].append(
                    f"Unsupported response type: {response_type}"
                )
                validation_result['valid'] = False

        # Validate grant types
        grant_types = client_metadata.get('grant_types', [])
        supported_grant_types = set(discovery_doc.grant_types_supported)
        for grant_type in grant_types:
            if grant_type not in supported_grant_types:
                validation_result['errors'].append(f"Unsupported grant type: {grant_type}")
                validation_result['valid'] = False

        # Validate scopes
        scope = client_metadata.get('scope', '')
        if scope:
            requested_scopes = set(scope.split())
            supported_scopes = set(discovery_doc.scopes_supported)
            unsupported_scopes = requested_scopes - supported_scopes
            if unsupported_scopes:
                validation_result['warnings'].append(
                    f"Unsupported scopes: {unsupported_scopes}"
                )

        return validation_result

    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics for monitoring."""
        return {
            'validation_failures': self._validation_failures,
            'security_events': len(self._security_events),
            'cache_hits': 1 if self._cached_document else 0,
            'cache_age_minutes': (
                (datetime.now(timezone.utc) - self._cache_timestamp).total_seconds() / 60
                if self._cache_timestamp else 0
            ),
            'last_validation_time': (
                self._cached_document.generated_at.isoformat()
                if self._cached_document else None
            ),
            'document_hash': (
                self._cached_document.document_hash
                if self._cached_document else None
            )
        }


class SecurityValidationError(Exception):
    """Exception raised for discovery document security validation failures."""
    pass


def create_default_discovery_provider() -> DiscoveryProvider:
    """Create discovery provider with environment-based configuration and security defaults."""
    base_url = os.getenv("LUKHAS_OIDC_ISSUER", "https://localhost:8000")

    # Environment-based customization with security validation
    custom_config = {
        'fail_closed': os.getenv("OIDC_FAIL_CLOSED", "true").lower() == "true",
        'cache_ttl_minutes': int(os.getenv("OIDC_CACHE_TTL_MINUTES", "30"))
    }

    # Override specific fields if provided
    if custom_issuer := os.getenv("OIDC_ISSUER"):
        custom_config["issuer"] = custom_issuer

    if custom_jwks := os.getenv("OIDC_JWKS_URI"):
        custom_config["jwks_uri"] = custom_jwks

    # Security-specific environment variables
    if os.getenv("OIDC_REQUIRE_PKCE", "true").lower() == "true":
        custom_config["code_challenge_methods_supported"] = ["S256"]

    if os.getenv("OIDC_DISABLE_IMPLICIT", "true").lower() == "true":
        custom_config["response_types_supported"] = ["code"]

    return DiscoveryProvider(base_url, custom_config)