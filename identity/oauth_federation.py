"""
LUKHAS PWM OAuth Federation & Enterprise Identity System
=======================================================
Comprehensive federated authentication supporting:
- OAuth providers (Apple, Google, Microsoft, GitHub, etc.)
- Enterprise/institutional user ID prefixes  
- Temporary user allocation and account linking
- Multi-provider account management

Architecture:
- Provider-agnostic OAuth flow
- Enterprise user ID namespacing (org-john_doe, stanford-alice_smith)
- Temporary user IDs for unverified accounts
- Account linking and migration workflows
"""

import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

from .identity_core import AccessTier, identity_core


class OAuthProvider(Enum):
    """Supported OAuth providers."""
    APPLE = "apple"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    DISCORD = "discord"


class UserIDType(Enum):
    """Types of user ID allocation."""
    STANDARD = "standard"          # Regular user: john_doe
    ENTERPRISE = "enterprise"      # Enterprise: acme-john_doe
    INSTITUTIONAL = "institutional" # Academic: stanford-alice_smith
    TEMPORARY = "temporary"        # Temp: temp_abc123
    FEDERATED = "federated"        # OAuth: google_123456789


class EnterpriseConfig(BaseModel):
    """Configuration for enterprise/institutional domains."""
    organization_id: str = Field(..., description="Short org identifier (e.g., 'acme', 'stanford')")
    domain_pattern: str = Field(..., description="Email domain pattern (e.g., '*.company.com')")
    display_name: str = Field(..., description="Human readable name")
    default_tier: AccessTier = Field(AccessTier.T2, description="Default tier for org users")
    auto_verify: bool = Field(False, description="Auto-verify users from this domain")
    sso_required: bool = Field(False, description="Require SSO for this org")
    user_id_format: str = Field("{org_id}-{username}", description="User ID format template")

    class Config:
        use_enum_values = True


class OAuthProviderConfig(BaseModel):
    """OAuth provider configuration."""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    userinfo_url: str
    scopes: List[str]
    enabled: bool = True

    class Config:
        use_enum_values = True


class FederatedUser(BaseModel):
    """Federated user account information."""
    lukhas_user_id: str
    provider: OAuthProvider
    provider_user_id: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    organization_id: Optional[str] = None
    is_temporary: bool = False
    verified: bool = False
    linked_accounts: List[str] = []  # Other provider accounts
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        use_enum_values = True


class OAuthFederationManager:
    """Manages OAuth federation and enterprise user IDs."""

    def __init__(self):
        self.providers: Dict[OAuthProvider, OAuthProviderConfig] = {}
        self.enterprises: Dict[str, EnterpriseConfig] = {}
        self.federated_users: Dict[str, FederatedUser] = {}  # In production: database
        self.temp_users: Dict[str, Dict] = {}  # Temporary user storage

        # Load default configurations
        self._load_default_configs()

    def _load_default_configs(self):
        """Load default OAuth provider and enterprise configurations."""

        # Default OAuth providers
        default_providers = {
            OAuthProvider.APPLE: OAuthProviderConfig(
                provider=OAuthProvider.APPLE,
                client_id="your.bundle.id",  # Configure with actual Apple client ID
                client_secret="",  # Apple uses JWT instead
                authorization_url="https://appleid.apple.com/auth/authorize",
                token_url="https://appleid.apple.com/auth/token",
                userinfo_url="",  # Apple provides user info in token response
                scopes=["name", "email"]
            ),
            OAuthProvider.GOOGLE: OAuthProviderConfig(
                provider=OAuthProvider.GOOGLE,
                client_id="your-google-client-id.apps.googleusercontent.com",
                client_secret="your-google-client-secret",
                authorization_url="https://accounts.google.com/o/oauth2/auth",
                token_url="https://oauth2.googleapis.com/token",
                userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
                scopes=["openid", "email", "profile"]
            ),
            OAuthProvider.GITHUB: OAuthProviderConfig(
                provider=OAuthProvider.GITHUB,
                client_id="your-github-client-id",
                client_secret="your-github-client-secret",
                authorization_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                userinfo_url="https://api.github.com/user",
                scopes=["user:email"]
            )
        }

        self.providers = default_providers

        # Default enterprise configurations
        self.enterprises = {
            "openai": EnterpriseConfig(
                organization_id="openai",
                domain_pattern="*.openai.com",
                display_name="OpenAI",
                default_tier=AccessTier.T5,  # Full access for OpenAI reviewers
                auto_verify=True,
                user_id_format="openai-{username}"
            ),
            "stanford": EnterpriseConfig(
                organization_id="stanford",
                domain_pattern="*.stanford.edu",
                display_name="Stanford University",
                default_tier=AccessTier.T3,
                auto_verify=True,
                user_id_format="stanford-{username}"
            ),
            "mit": EnterpriseConfig(
                organization_id="mit",
                domain_pattern="*.mit.edu",
                display_name="MIT",
                default_tier=AccessTier.T3,
                auto_verify=True,
                user_id_format="mit-{username}"
            )
        }

    def generate_oauth_url(self, provider: OAuthProvider, redirect_uri: str, state: str = None) -> str:
        """Generate OAuth authorization URL."""

        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not configured")

        config = self.providers[provider]
        if not config.enabled:
            raise ValueError(f"Provider {provider} is disabled")

        params = {
            "client_id": config.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(config.scopes),
            "response_type": "code",
            "state": state or secrets.token_urlsafe(32)
        }

        # Provider-specific parameters
        if provider == OAuthProvider.APPLE:
            params["response_mode"] = "form_post"

        return f"{config.authorization_url}?{urlencode(params)}"

    async def handle_oauth_callback(
        self,
        provider: OAuthProvider,
        code: str,
        redirect_uri: str,
        state: str = None
    ) -> Dict[str, Any]:
        """Handle OAuth callback and create/link user account."""

        try:
            # Exchange code for token
            token_data = await self._exchange_code_for_token(provider, code, redirect_uri)

            # Get user info from provider
            user_info = await self._get_user_info(provider, token_data["access_token"])

            # Determine organization from email
            org_config = self._get_organization_from_email(user_info["email"])

            # Generate or retrieve LUKHAS user ID
            lukhas_user_id = await self._allocate_lukhas_user_id(
                provider=provider,
                provider_user_id=str(user_info["id"]),
                email=user_info["email"],
                display_name=user_info.get("name"),
                organization=org_config
            )

            # Create or update federated user
            federated_user = await self._create_or_update_federated_user(
                lukhas_user_id=lukhas_user_id,
                provider=provider,
                provider_user_id=str(user_info["id"]),
                email=user_info["email"],
                display_name=user_info.get("name"),
                avatar_url=user_info.get("picture"),
                organization_id=org_config.organization_id if org_config else None
            )

            # Generate LUKHAS token
            tier = org_config.default_tier if org_config else AccessTier.T2
            metadata = {
                "email": user_info["email"],
                "display_name": user_info.get("name"),
                "provider": provider.value,
                "provider_user_id": str(user_info["id"]),
                "organization": org_config.organization_id if org_config else None,
                "federated": True,
                "verified": org_config.auto_verify if org_config else False,
                "oauth_login": True
            }

            token = identity_core.create_token(lukhas_user_id, tier, metadata)
            glyphs = identity_core.generate_identity_glyph(lukhas_user_id)

            return {
                "success": True,
                "user_id": lukhas_user_id,
                "display_name": federated_user.display_name,
                "email": federated_user.email,
                "token": token,
                "tier": tier.value,
                "glyphs": glyphs,
                "provider": provider.value,
                "organization": org_config.organization_id if org_config else None,
                "is_new_user": federated_user.created_at > datetime.now(timezone.utc) - timedelta(minutes=5),
                "federated": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"OAuth login failed: {str(e)}",
                "provider": provider.value
            }

    async def _exchange_code_for_token(self, provider: OAuthProvider, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        config = self.providers[provider]

        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.token_url,
                data=data,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    async def _get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        config = self.providers[provider]

        if provider == OAuthProvider.APPLE:
            # Apple provides user info in token response
            # This is a simplified implementation
            return {"id": "apple_user", "email": "user@apple.com", "name": "Apple User"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                config.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()

    def _get_organization_from_email(self, email: str) -> Optional[EnterpriseConfig]:
        """Determine organization from email domain."""
        domain = email.split("@")[1].lower()

        for org_id, config in self.enterprises.items():
            pattern = config.domain_pattern.replace("*", "")
            if domain.endswith(pattern.lstrip(".")):
                return config

        return None

    async def _allocate_lukhas_user_id(
        self,
        provider: OAuthProvider,
        provider_user_id: str,
        email: str,
        display_name: Optional[str],
        organization: Optional[EnterpriseConfig]
    ) -> str:
        """Allocate LUKHAS user ID based on provider and organization."""

        # Check if user already exists from this provider
        existing_user = self._find_user_by_provider(provider, provider_user_id)
        if existing_user:
            return existing_user.lukhas_user_id

        # Check if user exists by email (account linking)
        existing_by_email = self._find_user_by_email(email)
        if existing_by_email:
            # Link this OAuth account to existing user
            existing_by_email.linked_accounts.append(f"{provider.value}:{provider_user_id}")
            return existing_by_email.lukhas_user_id

        # Generate new user ID
        if organization:
            # Enterprise/institutional user ID
            username = email.split("@")[0].replace(".", "_").lower()
            user_id = organization.user_id_format.format(
                org_id=organization.organization_id,
                username=username
            )
        else:
            # Standard federated user ID
            base_username = email.split("@")[0].replace(".", "_").lower()

            # Check if standard username is available
            if not self._is_user_id_taken(base_username):
                user_id = base_username
            else:
                # Create provider-prefixed ID
                user_id = f"{provider.value}_{provider_user_id[:8]}"

        return user_id

    async def _create_or_update_federated_user(
        self,
        lukhas_user_id: str,
        provider: OAuthProvider,
        provider_user_id: str,
        email: str,
        display_name: Optional[str],
        avatar_url: Optional[str],
        organization_id: Optional[str]
    ) -> FederatedUser:
        """Create or update federated user record."""

        existing = self.federated_users.get(lukhas_user_id)

        if existing:
            # Update existing user
            existing.last_login = datetime.now(timezone.utc)
            existing.display_name = display_name or existing.display_name
            existing.avatar_url = avatar_url or existing.avatar_url
            return existing
        else:
            # Create new federated user
            federated_user = FederatedUser(
                lukhas_user_id=lukhas_user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url,
                organization_id=organization_id,
                is_temporary=False,
                verified=organization_id is not None,  # Auto-verify org users
                created_at=datetime.now(timezone.utc),
                last_login=datetime.now(timezone.utc)
            )

            self.federated_users[lukhas_user_id] = federated_user
            return federated_user

    def create_temporary_user(self, provider: OAuthProvider, email: str) -> str:
        """Create temporary user ID for incomplete OAuth flows."""
        temp_id = f"temp_{secrets.token_hex(8)}"

        self.temp_users[temp_id] = {
            "provider": provider.value,
            "email": email,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)
        }

        return temp_id

    def link_accounts(self, primary_user_id: str, secondary_provider: OAuthProvider, secondary_user_id: str) -> bool:
        """Link multiple OAuth accounts to the same LUKHAS user."""
        primary_user = self.federated_users.get(primary_user_id)
        if not primary_user:
            return False

        link_identifier = f"{secondary_provider.value}:{secondary_user_id}"
        if link_identifier not in primary_user.linked_accounts:
            primary_user.linked_accounts.append(link_identifier)

        return True

    def _find_user_by_provider(self, provider: OAuthProvider, provider_user_id: str) -> Optional[FederatedUser]:
        """Find user by OAuth provider and provider user ID."""
        for user in self.federated_users.values():
            if user.provider == provider and user.provider_user_id == provider_user_id:
                return user
        return None

    def _find_user_by_email(self, email: str) -> Optional[FederatedUser]:
        """Find user by email address."""
        for user in self.federated_users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def _is_user_id_taken(self, user_id: str) -> bool:
        """Check if LUKHAS user ID is already taken."""
        return user_id in self.federated_users

    def get_organization_configs(self) -> Dict[str, EnterpriseConfig]:
        """Get all enterprise/institutional configurations."""
        return self.enterprises.copy()

    def add_organization(self, org_id: str, config: EnterpriseConfig):
        """Add new enterprise/institutional configuration."""
        self.enterprises[org_id] = config

    def get_user_info(self, user_id: str) -> Optional[FederatedUser]:
        """Get federated user information."""
        return self.federated_users.get(user_id)

    def cleanup_temporary_users(self):
        """Clean up expired temporary users."""
        now = datetime.now(timezone.utc)
        expired = [
            temp_id for temp_id, data in self.temp_users.items()
            if data["expires_at"] < now
        ]

        for temp_id in expired:
            del self.temp_users[temp_id]


# Global instance
oauth_federation = OAuthFederationManager()


# Convenience functions
def get_apple_login_url(redirect_uri: str) -> str:
    """Get Apple Sign-In URL."""
    return oauth_federation.generate_oauth_url(OAuthProvider.APPLE, redirect_uri)


def get_google_login_url(redirect_uri: str) -> str:
    """Get Google Sign-In URL."""
    return oauth_federation.generate_oauth_url(OAuthProvider.GOOGLE, redirect_uri)


async def handle_apple_callback(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Handle Apple Sign-In callback."""
    return await oauth_federation.handle_oauth_callback(OAuthProvider.APPLE, code, redirect_uri)


async def handle_google_callback(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Handle Google Sign-In callback."""
    return await oauth_federation.handle_oauth_callback(OAuthProvider.GOOGLE, code, redirect_uri)
