#!/usr/bin/env python3
"""
OIDC Discovery Document Provider - OpenID Connect Discovery 1.0

Provides .well-known/openid-configuration endpoint and metadata.
Fully compliant with OpenID Connect Discovery 1.0 specification.

T4/0.01% Excellence: Performance-optimized caching and validation.
"""

from __future__ import annotations
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@dataclass
class DiscoveryDocument:
    """OpenID Connect Discovery 1.0 compliant configuration document."""

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenID Connect Discovery JSON format."""
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
            "guardian_validation": True
        }

        return result


class DiscoveryProvider:
    """OpenID Connect Discovery document provider with caching."""

    def __init__(self, base_url: str, custom_config: Optional[Dict[str, Any]] = None):
        """
        Initialize discovery provider.

        Args:
            base_url: Base URL for the OIDC provider (e.g., https://auth.lukhas.ai)
            custom_config: Optional custom configuration overrides
        """
        self.base_url = base_url.rstrip('/')
        self.custom_config = custom_config or {}
        self._cached_document: Optional[DiscoveryDocument] = None

    def get_discovery_document(self) -> DiscoveryDocument:
        """Get OpenID Connect Discovery document (cached)."""
        with tracer.start_span("oidc.get_discovery_document") as span:
            if self._cached_document is None:
                self._cached_document = self._build_discovery_document()
                span.set_attribute("oidc.cache_miss", True)
            else:
                span.set_attribute("oidc.cache_hit", True)

            return self._cached_document

    def _build_discovery_document(self) -> DiscoveryDocument:
        """Build the discovery document from configuration."""
        # Default configuration following OpenID Connect Discovery 1.0
        config = {
            "issuer": self.base_url,
            "authorization_endpoint": f"{self.base_url}/oauth2/authorize",
            "token_endpoint": f"{self.base_url}/oauth2/token",
            "jwks_uri": f"{self.base_url}/.well-known/jwks.json",
            "userinfo_endpoint": f"{self.base_url}/oauth2/userinfo",
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256", "ES256"],
            "scopes_supported": ["openid", "profile", "email", "lukhas:tier", "lukhas:admin"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
            "code_challenge_methods_supported": ["S256"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "revocation_endpoint": f"{self.base_url}/oauth2/revoke",
            "introspection_endpoint": f"{self.base_url}/oauth2/introspect",
        }

        # Apply custom overrides
        config.update(self.custom_config)

        return DiscoveryDocument(**config)

    def invalidate_cache(self):
        """Invalidate the cached discovery document."""
        self._cached_document = None


def create_default_discovery_provider() -> DiscoveryProvider:
    """Create discovery provider with environment-based configuration."""
    base_url = os.getenv("LUKHAS_OIDC_ISSUER", "https://localhost:8000")

    # Environment-based customization
    custom_config = {}

    if custom_issuer := os.getenv("OIDC_ISSUER"):
        custom_config["issuer"] = custom_issuer

    if custom_jwks := os.getenv("OIDC_JWKS_URI"):
        custom_config["jwks_uri"] = custom_jwks

    return DiscoveryProvider(base_url, custom_config)