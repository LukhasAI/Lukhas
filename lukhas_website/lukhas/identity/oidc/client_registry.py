#!/usr/bin/env python3
"""
OIDC Client Registry - OAuth2 Client Management

Manages OAuth2 client registration, authentication, and metadata.
Supports both static configuration and dynamic client registration.

T4/0.01% Excellence: Guardian integration for client validation.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from opentelemetry import trace
from prometheus_client import Counter, Gauge

tracer = trace.get_tracer(__name__)


# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs):
        return self

    def inc(self, amount=1):
        pass

    def set(self, value):
        pass


try:
    client_auth_total = Counter(
        "lukhas_oidc_client_auth_total", "Total client authentication attempts", ["client_id", "auth_method", "result"]
    )
    registered_clients_total = Gauge("lukhas_oidc_registered_clients_total", "Total registered OAuth2 clients")
except ValueError:
    client_auth_total = MockMetric()
    registered_clients_total = MockMetric()


class ClientType(Enum):
    """OAuth2 client types per RFC 6749."""

    CONFIDENTIAL = "confidential"
    PUBLIC = "public"


class ApplicationType(Enum):
    """OIDC application types."""

    WEB = "web"
    NATIVE = "native"
    SPA = "spa"  # Single Page Application


@dataclass
class OIDCClient:
    """OAuth2/OIDC client registration data."""

    # Basic client information
    client_id: str
    client_name: str
    client_type: ClientType
    application_type: ApplicationType

    # Authentication
    client_secret: Optional[str] = None
    client_secret_expires_at: Optional[int] = None

    # Redirect URIs and scopes
    redirect_uris: List[str] = field(default_factory=list)
    post_logout_redirect_uris: List[str] = field(default_factory=list)
    allowed_scopes: Set[str] = field(default_factory=lambda: {"openid"})

    # Grant types and response types
    grant_types: Set[str] = field(default_factory=lambda: {"authorization_code"})
    response_types: Set[str] = field(default_factory=lambda: {"code"})

    # Token configuration
    access_token_lifetime: int = 3600  # 1 hour
    refresh_token_lifetime: int = 86400 * 30  # 30 days
    id_token_lifetime: int = 300  # 5 minutes

    # PKCE requirements
    require_pkce: bool = True
    require_pkce_s256: bool = True

    # Metadata
    created_at: int = field(default_factory=lambda: int(time.time()))
    last_used_at: Optional[int] = None
    is_active: bool = True

    # LUKHAS-specific extensions
    allowed_tiers: Set[str] = field(default_factory=lambda: {"T1", "T2"})
    require_guardian_approval: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = asdict(self)
        # Convert enums to strings
        result["client_type"] = self.client_type.value
        result["application_type"] = self.application_type.value
        # Convert sets to lists for JSON serialization
        result["allowed_scopes"] = list(self.allowed_scopes)
        result["grant_types"] = list(self.grant_types)
        result["response_types"] = list(self.response_types)
        result["allowed_tiers"] = list(self.allowed_tiers)
        return result

    def is_redirect_uri_allowed(self, redirect_uri: str) -> bool:
        """Check if redirect URI is allowed for this client."""
        return redirect_uri in self.redirect_uris

    def is_scope_allowed(self, scope: str) -> bool:
        """Check if scope is allowed for this client."""
        return scope in self.allowed_scopes

    def is_grant_type_allowed(self, grant_type: str) -> bool:
        """Check if grant type is allowed for this client."""
        return grant_type in self.grant_types

    def is_tier_allowed(self, tier: str) -> bool:
        """Check if authentication tier is allowed for this client."""
        return tier in self.allowed_tiers

    def verify_secret(self, provided_secret: str) -> bool:
        """Verify client secret using constant-time comparison."""
        if not self.client_secret:
            return False
        return secrets.compare_digest(self.client_secret, provided_secret)

    def update_last_used(self):
        """Update last used timestamp."""
        self.last_used_at = int(time.time())


class ClientRegistry:
    """OAuth2 client registry with Guardian integration."""

    def __init__(self, guardian_client=None):
        """Initialize client registry with optional Guardian validation."""
        self._clients: Dict[str, OIDCClient] = {}
        self.guardian_client = guardian_client
        self._load_default_clients()

    def _load_default_clients(self):
        """Load default LUKHAS clients for development and testing."""
        # Development web client
        dev_client = OIDCClient(
            client_id="lukhas-dev-web",
            client_name="LUKHAS Development Web Client",
            client_type=ClientType.CONFIDENTIAL,
            application_type=ApplicationType.WEB,
            client_secret=self._generate_client_secret(),
            redirect_uris=["http://localhost:3000/callback", "http://localhost:8080/callback"],
            allowed_scopes={"openid", "profile", "email", "lukhas:tier"},
            allowed_tiers={"T1", "T2", "T3", "T4", "T5"},
        )

        # Public SPA client (no secret)
        spa_client = OIDCClient(
            client_id="lukhas-spa",
            client_name="LUKHAS Single Page Application",
            client_type=ClientType.PUBLIC,
            application_type=ApplicationType.SPA,
            redirect_uris=["http://localhost:3000/callback"],
            allowed_scopes={"openid", "profile"},
            allowed_tiers={"T1", "T2", "T3"},
            require_pkce=True,
            require_pkce_s256=True,
        )

        # Mobile/native client
        native_client = OIDCClient(
            client_id="lukhas-mobile",
            client_name="LUKHAS Mobile Application",
            client_type=ClientType.PUBLIC,
            application_type=ApplicationType.NATIVE,
            redirect_uris=["lukhas://oauth/callback", "http://localhost:8080/callback"],
            allowed_scopes={"openid", "profile", "lukhas:tier"},
            allowed_tiers={"T1", "T2", "T3", "T4", "T5"},
            require_pkce=True,
        )

        for client in [dev_client, spa_client, native_client]:
            self._clients[client.client_id] = client

        registered_clients_total.set(len(self._clients))

    def register_client(self, client_data: Dict[str, Any]) -> OIDCClient:
        """Register a new OAuth2 client."""
        with tracer.start_span("oidc.register_client") as span:
            # Generate client ID and secret
            client_id = f"lukhas-{secrets.token_urlsafe(16)}"
            client_secret = self._generate_client_secret() if client_data.get("client_type") == "confidential" else None

            # Create client object
            client = OIDCClient(client_id=client_id, client_secret=client_secret, **client_data)

            # Guardian validation for high-privilege clients
            if client.require_guardian_approval and self.guardian_client:
                guardian_result = self._validate_with_guardian(client)
                if not guardian_result.get("approved", False):
                    raise ValueError(f"Guardian rejected client registration: {guardian_result.get('reason')}")

            self._clients[client_id] = client
            registered_clients_total.set(len(self._clients))

            span.set_attribute("oidc.client_id", client_id)
            span.set_attribute("oidc.client_type", client.client_type.value)

            return client

    def get_client(self, client_id: str) -> Optional[OIDCClient]:
        """Get client by ID."""
        return self._clients.get(client_id)

    def authenticate_client(self, client_id: str, client_secret: Optional[str] = None) -> Optional[OIDCClient]:
        """Authenticate OAuth2 client."""
        with tracer.start_span("oidc.authenticate_client") as span:
            span.set_attribute("oidc.client_id", client_id)

            client = self.get_client(client_id)
            if not client or not client.is_active:
                client_auth_total.labels(client_id=client_id, auth_method="secret", result="client_not_found").inc()
                return None

            # Public clients don't require secret authentication
            if client.client_type == ClientType.PUBLIC:
                if client_secret is not None:
                    client_auth_total.labels(
                        client_id=client_id, auth_method="secret", result="secret_not_required"
                    ).inc()
                    return None

                client.update_last_used()
                client_auth_total.labels(client_id=client_id, auth_method="public", result="success").inc()
                span.set_attribute("oidc.auth_method", "public")
                return client

            # Confidential clients require secret authentication
            if not client_secret or not client.verify_secret(client_secret):
                client_auth_total.labels(client_id=client_id, auth_method="secret", result="invalid_secret").inc()
                return None

            client.update_last_used()
            client_auth_total.labels(client_id=client_id, auth_method="secret", result="success").inc()
            span.set_attribute("oidc.auth_method", "secret")

            return client

    def list_clients(self, active_only: bool = True) -> List[OIDCClient]:
        """List all registered clients."""
        clients = list(self._clients.values())
        if active_only:
            clients = [c for c in clients if c.is_active]
        return clients

    def deactivate_client(self, client_id: str) -> bool:
        """Deactivate a client (soft delete)."""
        if client := self.get_client(client_id):
            client.is_active = False
            registered_clients_total.set(len([c for c in self._clients.values() if c.is_active]))
            return True
        return False

    def update_client(self, client_id: str, updates: Dict[str, Any]) -> Optional[OIDCClient]:
        """Update client configuration."""
        if client := self.get_client(client_id):
            # Update allowed fields (security consideration)
            allowed_updates = {
                "client_name",
                "redirect_uris",
                "post_logout_redirect_uris",
                "allowed_scopes",
                "access_token_lifetime",
                "refresh_token_lifetime",
                "id_token_lifetime",
                "allowed_tiers",
            }

            for key, value in updates.items():
                if key in allowed_updates:
                    setattr(client, key, value)

            return client
        return None

    def _generate_client_secret(self) -> str:
        """Generate cryptographically secure client secret."""
        return secrets.token_urlsafe(32)

    def _validate_with_guardian(self, client: OIDCClient) -> Dict[str, Any]:
        """Validate client registration with Guardian system."""
        # Placeholder for Guardian integration
        # In production, this would call Guardian for policy validation
        return {"approved": True, "reason": "Development mode"}


# Singleton instance for application use
_default_registry: Optional[ClientRegistry] = None


def get_default_client_registry() -> ClientRegistry:
    """Get the default client registry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ClientRegistry()
    return _default_registry
