#!/usr/bin/env python3
"""
SSO Bridge - OAuth2/SAML integration stub for enterprise SSO systems
Provides symbolic glyph mapping for external identity providers
"""
import json
import logging
import secrets
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class SSOProvider:
    """SSO provider configuration"""

    provider_id: str
    provider_name: str
    provider_type: str  # oauth2, saml, openid
    endpoint_auth: str
    endpoint_token: str
    endpoint_userinfo: str
    client_id: str
    client_secret: str
    scopes: list[str]
    glyph_mapping: dict[str, str]  # Role/claim to glyph mapping
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SSOSession:
    """Active SSO session"""

    session_id: str
    provider_id: str
    user_id: str
    external_user_id: str
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_at: datetime
    scopes: list[str]
    user_claims: dict[str, Any]
    assigned_glyphs: list[str]
    created_at: datetime
    last_activity: datetime


@dataclass
class SSOTransaction:
    """SSO authentication transaction"""

    transaction_id: str
    provider_id: str
    state: str
    nonce: str
    redirect_uri: str
    requested_scopes: list[str]
    created_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None


class SSOBridge:
    """
    Single Sign-On bridge for enterprise identity providers
    Maps external claims to LUKHAS glyph-based permissions
    """

    # Standard claim to glyph mappings
    STANDARD_GLYPH_MAPPINGS = {
        # OAuth2 / OpenID Connect standard claims
        "admin": "🔐",
        "user": "🔓",
        "read": "👁️",
        "write": "✍️",
        "delete": "🗑️",
        "create": "✨",
        # Enterprise role mappings
        "manager": "👑",
        "employee": "👤",
        "contractor": "🤝",
        "guest": "🚪",
        # Department mappings
        "engineering": "⚙️",
        "security": "🛡️",
        "finance": "💰",
        "hr": "👥",
        "marketing": "📢",
        "sales": "💼",
        # Access levels
        "confidential": "🔒",
        "internal": "🏢",
        "public": "🌐",
        "restricted": "⛔",
    }

    def __init__(
        self,
        config_file: str = "sso_config.json",
        session_store: str = "sso_sessions.json",
    ):
        self.config_file = Path(config_file)
        self.session_store = Path(session_store)
        self.providers: dict[str, SSOProvider] = {}
        self.active_sessions: dict[str, SSOSession] = {}
        self.transactions: dict[str, SSOTransaction] = {}

        # Load configuration
        self._load_configuration()

        logger.info("🔗 SSO Bridge initialized")
        logger.info(f"   Configured providers: {len(self.providers)}")
        logger.info(f"   Standard glyph mappings: {len(self.STANDARD_GLYPH_MAPPINGS)}")

    def _load_configuration(self):
        """Load SSO provider configurations"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)

                # Load providers
                for provider_id, provider_config in config.get("providers", {}).items():
                    self.providers[provider_id] = SSOProvider(
                        provider_id=provider_config["provider_id"],
                        provider_name=provider_config["provider_name"],
                        provider_type=provider_config["provider_type"],
                        endpoint_auth=provider_config["endpoint_auth"],
                        endpoint_token=provider_config["endpoint_token"],
                        endpoint_userinfo=provider_config["endpoint_userinfo"],
                        client_id=provider_config["client_id"],
                        client_secret=provider_config["client_secret"],
                        scopes=provider_config.get("scopes", []),
                        glyph_mapping=provider_config.get("glyph_mapping", {}),
                        metadata=provider_config.get("metadata", {}),
                    )

            except Exception as e:
                logger.warning(f"Could not load SSO configuration: {e}")
                self._create_default_configuration()
        else:
            self._create_default_configuration()

        # Load sessions
        self._load_sessions()

    def _create_default_configuration(self):
        """Create default SSO configuration with sample providers"""
        default_config = {
            "version": "1.0.0",
            "created": datetime.now(timezone.utc).isoformat(),
            "providers": {
                "azure_ad": {
                    "provider_id": "azure_ad",
                    "provider_name": "Azure Active Directory",
                    "provider_type": "oauth2",
                    "endpoint_auth": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
                    "endpoint_token": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
                    "endpoint_userinfo": "https://graph.microsoft.com/v1.0/me",
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret",
                    "scopes": ["openid", "profile", "email", "User.Read"],
                    "glyph_mapping": {
                        "Global Administrator": "🔐",
                        "User Administrator": "👑",
                        "Security Reader": "🛡️",
                        "User": "🔓",
                    },
                    "metadata": {
                        "tenant_id": "your-tenant-id",
                        "authority": "https://login.microsoftonline.com/your-tenant-id",
                    },
                },
                "okta": {
                    "provider_id": "okta",
                    "provider_name": "Okta",
                    "provider_type": "oauth2",
                    "endpoint_auth": "https://your-domain.okta.com/oauth2/default/v1/authorize",
                    "endpoint_token": "https://your-domain.okta.com/oauth2/default/v1/token",
                    "endpoint_userinfo": "https://your-domain.okta.com/oauth2/default/v1/userinfo",
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret",
                    "scopes": ["openid", "profile", "email", "groups"],
                    "glyph_mapping": {
                        "Administrators": "🔐",
                        "Managers": "👑",
                        "Employees": "🔓",
                        "Contractors": "🤝",
                    },
                    "metadata": {"domain": "your-domain.okta.com"},
                },
                "google_workspace": {
                    "provider_id": "google_workspace",
                    "provider_name": "Google Workspace",
                    "provider_type": "oauth2",
                    "endpoint_auth": "https://accounts.google.com/o/oauth2/v2/auth",
                    "endpoint_token": "https://oauth2.googleapis.com/token",
                    "endpoint_userinfo": "https://www.googleapis.com/oauth2/v1/userinfo",
                    "client_id": "your-client-id.apps.googleusercontent.com",
                    "client_secret": "your-client-secret",
                    "scopes": ["openid", "email", "profile"],
                    "glyph_mapping": {"admin": "🔐", "user": "🔓"},
                },
            },
        }

        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)

        logger.info("📝 Created default SSO configuration")

    def _load_sessions(self):
        """Load active SSO sessions"""
        if self.session_store.exists():
            try:
                with open(self.session_store) as f:
                    data = json.load(f)

                for session_id, session_data in data.get("sessions", {}).items():
                    self.active_sessions[session_id] = SSOSession(
                        session_id=session_data["session_id"],
                        provider_id=session_data["provider_id"],
                        user_id=session_data["user_id"],
                        external_user_id=session_data["external_user_id"],
                        access_token=session_data["access_token"],
                        refresh_token=session_data.get("refresh_token"),
                        token_type=session_data["token_type"],
                        expires_at=datetime.fromisoformat(session_data["expires_at"]),
                        scopes=session_data["scopes"],
                        user_claims=session_data["user_claims"],
                        assigned_glyphs=session_data["assigned_glyphs"],
                        created_at=datetime.fromisoformat(session_data["created_at"]),
                        last_activity=datetime.fromisoformat(session_data["last_activity"]),
                    )

            except Exception as e:
                logger.warning(f"Could not load SSO sessions: {e}")

    def _save_sessions(self):
        """Save active SSO sessions"""
        data = {
            "version": "1.0.0",
            "updated": datetime.now(timezone.utc).isoformat(),
            "sessions": {},
        }

        for session_id, session in self.active_sessions.items():
            data["sessions"][session_id] = {
                "session_id": session.session_id,
                "provider_id": session.provider_id,
                "user_id": session.user_id,
                "external_user_id": session.external_user_id,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "token_type": session.token_type,
                "expires_at": session.expires_at.isoformat(),
                "scopes": session.scopes,
                "user_claims": session.user_claims,
                "assigned_glyphs": session.assigned_glyphs,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
            }

        with open(self.session_store, "w") as f:
            json.dump(data, f, indent=2)

    def initiate_sso_flow(
        self,
        provider_id: str,
        redirect_uri: str,
        requested_scopes: Optional[list[str]] = None,
    ) -> Optional[tuple[str, str]]:
        """Initiate SSO authentication flow"""
        if provider_id not in self.providers:
            logger.error(f"Unknown SSO provider: {provider_id}")
            return None

        provider = self.providers[provider_id]

        # Generate transaction
        transaction_id = str(uuid.uuid4())
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)

        # Use provider scopes if not specified
        scopes = requested_scopes or provider.scopes

        transaction = SSOTransaction(
            transaction_id=transaction_id,
            provider_id=provider_id,
            state=state,
            nonce=nonce,
            redirect_uri=redirect_uri,
            requested_scopes=scopes,
            created_at=datetime.now(timezone.utc),
        )

        self.transactions[transaction_id] = transaction

        # Build authorization URL
        auth_params = {
            "client_id": provider.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "nonce": nonce,
        }

        auth_url = f"{provider.endpoint_auth}?{urlencode(auth_params)}"

        logger.info(f"🚀 Initiated SSO flow: {provider_id}")
        logger.info(f"   Transaction: {transaction_id}")
        logger.info(f"   Scopes: {scopes}")

        return auth_url, transaction_id

    def handle_sso_callback(self, transaction_id: str, authorization_code: str, state: str) -> Optional[SSOSession]:
        """Handle SSO callback and complete authentication"""
        if transaction_id not in self.transactions:
            logger.error(f"Unknown transaction: {transaction_id}")
            return None

        transaction = self.transactions[transaction_id]

        # Verify state parameter
        if state != transaction.state:
            logger.error("State parameter mismatch")
            transaction.error_message = "State mismatch"
            return None

        provider = self.providers[transaction.provider_id]

        # Exchange authorization code for tokens (simulated)
        token_response = self._exchange_code_for_tokens(provider, authorization_code, transaction.redirect_uri)

        if not token_response:
            transaction.error_message = "Token exchange failed"
            return None

        # Get user information (simulated)
        user_info = self._get_user_info(provider, token_response["access_token"])

        if not user_info:
            transaction.error_message = "Failed to get user info"
            return None

        # Map claims to glyphs
        assigned_glyphs = self._map_claims_to_glyphs(user_info, provider.glyph_mapping)

        # Create session
        session_id = f"sso_{datetime.now(timezone.utc).timestamp()}_{provider.provider_id}"
        session = SSOSession(
            session_id=session_id,
            provider_id=provider.provider_id,
            user_id=user_info.get("sub", user_info.get("id", "unknown")),
            external_user_id=user_info.get("email", user_info.get("preferred_username", "unknown")),
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token"),
            token_type=token_response.get("token_type", "Bearer"),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=token_response.get("expires_in", 3600)),
            scopes=transaction.requested_scopes,
            user_claims=user_info,
            assigned_glyphs=assigned_glyphs,
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
        )

        # Store session
        self.active_sessions[session_id] = session

        # Complete transaction
        transaction.completed_at = datetime.now(timezone.utc)
        transaction.success = True

        # Save sessions
        self._save_sessions()

        logger.info(f"✅ SSO authentication successful: {session.external_user_id}")
        logger.info(f"   Provider: {provider.provider_name}")
        logger.info(f"   Assigned glyphs: {' '.join(assigned_glyphs)}")
        logger.info(f"   Session: {session_id}")

        return session

    def _exchange_code_for_tokens(self, provider: SSOProvider, code: str, redirect_uri: str) -> Optional[dict]:
        """Exchange authorization code for access tokens (simulated)"""
        # In a real implementation, this would make an HTTP POST to the token endpoint
        logger.info("🔄 Simulating token exchange...")

        # Simulate successful token response
        return {
            "access_token": f"at_{secrets.token_urlsafe(32)}",
            "refresh_token": f"rt_{secrets.token_urlsafe(32)}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": " ".join(provider.scopes),
        }

    def _get_user_info(self, provider: SSOProvider, access_token: str) -> Optional[dict]:
        """Get user information from provider (simulated)"""
        # In a real implementation, this would make an HTTP GET to the userinfo endpoint
        logger.info("👤 Simulating user info retrieval...")

        # Simulate user information based on provider
        if provider.provider_id == "azure_ad":
            return {
                "sub": str(uuid.uuid4()),
                "email": "user@company.com",
                "name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "roles": ["User", "Security Reader"],
                "department": "Engineering",
            }
        elif provider.provider_id == "okta":
            return {
                "sub": str(uuid.uuid4()),
                "email": "user@company.com",
                "name": "Jane Smith",
                "groups": ["Employees", "Engineering"],
            }
        elif provider.provider_id == "google_workspace":
            return {
                "sub": str(uuid.uuid4()),
                "email": "user@company.com",
                "name": "Bob Johnson",
                "picture": "https://example.com/avatar.jpg",
            }

        return None

    def _map_claims_to_glyphs(self, user_claims: dict, provider_mapping: dict[str, str]) -> list[str]:
        """Map user claims to LUKHAS glyphs"""
        assigned_glyphs = []

        # Check provider-specific mappings first
        for claim_value, glyph in provider_mapping.items():
            if self._claim_matches(user_claims, claim_value):
                assigned_glyphs.append(glyph)

        # Check standard mappings
        for claim_value, glyph in self.STANDARD_GLYPH_MAPPINGS.items():
            if self._claim_matches(user_claims, claim_value) and glyph not in assigned_glyphs:
                assigned_glyphs.append(glyph)

        # Default glyph if no matches
        if not assigned_glyphs:
            assigned_glyphs.append("🔓")  # Basic user access

        return assigned_glyphs

    def _claim_matches(self, user_claims: dict, target_value: str) -> bool:
        """Check if user claims contain a target value"""
        target_lower = target_value.lower()

        # Check common claim fields
        claim_fields = ["roles", "groups", "department", "job_title", "role"]

        for field in claim_fields:
            if field in user_claims:
                claim_data = user_claims[field]
                if isinstance(claim_data, list):
                    for item in claim_data:
                        if isinstance(item, str) and target_lower in item.lower():
                            return True
                elif isinstance(claim_data, str) and target_lower in claim_data.lower():
                    return True

        return False

    def validate_session(self, session_id: str) -> Optional[SSOSession]:
        """Validate and return SSO session if still active"""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]

        # Check if session is expired
        if datetime.now(timezone.utc) > session.expires_at:
            logger.info(f"🕐 Session expired: {session_id}")
            del self.active_sessions[session_id]
            self._save_sessions()
            return None

        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        self._save_sessions()

        return session

    def logout_session(self, session_id: str) -> bool:
        """Logout and invalidate SSO session"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        del self.active_sessions[session_id]
        self._save_sessions()

        logger.info(f"🚪 SSO session logged out: {session.external_user_id}")
        return True

    def get_user_glyphs(self, session_id: str) -> list[str]:
        """Get assigned glyphs for a session"""
        session = self.validate_session(session_id)
        return session.assigned_glyphs if session else []

    def add_provider(self, provider: SSOProvider) -> bool:
        """Add a new SSO provider"""
        self.providers[provider.provider_id] = provider

        # Update configuration file
        try:
            with open(self.config_file) as f:
                config = json.load(f)

            config["providers"][provider.provider_id] = asdict(provider)

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"➕ Added SSO provider: {provider.provider_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to save provider: {e}")
            return False

    def get_system_status(self) -> dict[str, Any]:
        """Get SSO bridge system status"""
        active_session_count = len(self.active_sessions)
        expired_sessions = 0

        for session in self.active_sessions.values():
            if datetime.now(timezone.utc) > session.expires_at:
                expired_sessions += 1

        # Provider statistics
        provider_usage = {}
        for session in self.active_sessions.values():
            provider_id = session.provider_id
            provider_usage[provider_id] = provider_usage.get(provider_id, 0) + 1

        # Glyph distribution
        glyph_usage = {}
        for session in self.active_sessions.values():
            for glyph in session.assigned_glyphs:
                glyph_usage[glyph] = glyph_usage.get(glyph, 0) + 1

        return {
            "providers_configured": len(self.providers),
            "active_sessions": active_session_count,
            "expired_sessions": expired_sessions,
            "pending_transactions": len(self.transactions),
            "provider_usage": provider_usage,
            "glyph_distribution": glyph_usage,
            "standard_mappings": len(self.STANDARD_GLYPH_MAPPINGS),
        }


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Create SSO bridge
    sso = SSOBridge(config_file="demo_sso_config.json", session_store="demo_sso_sessions.json")

    print("🔗 SSO Bridge Demo")
    print("=" * 60)

    # Test SSO flow
    print("\n🚀 Testing SSO authentication flow...")

    # Initiate flow
    auth_url, transaction_id = sso.initiate_sso_flow(
        provider_id="azure_ad",
        redirect_uri="https://lukhas.ai/auth/callback",
        requested_scopes=["openid", "profile", "email"],
    )

    print(f"   Auth URL: {auth_url[:80]}...")
    print(f"   Transaction: {transaction_id}")

    # Simulate callback
    print("\n📥 Simulating SSO callback...")
    session = sso.handle_sso_callback(
        transaction_id=transaction_id,
        authorization_code="simulated_auth_code",
        state=sso.transactions[transaction_id].state,
    )

    if session:
        print("   ✅ Authentication successful!")
        print(f"   User: {session.external_user_id}")
        print(f"   Glyphs: {' '.join(session.assigned_glyphs)}")

        # Test session validation
        print("\n🔍 Testing session validation...")
        validated = sso.validate_session(session.session_id)
        print(f"   Session valid: {'✅ YES' if validated else '❌ NO'}")

        # Test logout
        print("\n🚪 Testing logout...")
        logged_out = sso.logout_session(session.session_id)
        print(f"   Logout successful: {'✅ YES' if logged_out else '❌ NO'}")

    # System status
    print("\n📊 SSO System Status:")
    status = sso.get_system_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"     {k}: {v}")
        else:
            print(f"   {key}: {value}")

    # Cleanup demo files
    import os

    try:
        os.unlink("demo_sso_config.json")
        os.unlink("demo_sso_sessions.json")
    except BaseException:
        pass
