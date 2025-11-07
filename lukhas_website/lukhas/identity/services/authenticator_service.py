"""
LUKHAS Identity Authenticator Services
=====================================
Collection of authenticator implementations for different authentication methods.
Implements AuthenticatorInterface for T4 architecture compliance.
"""

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..facades.authentication_facade import AuthenticatorInterface, AuthResult

logger = logging.getLogger(__name__)


@dataclass
class UserCredentials:
    """User credentials for password authentication"""
    username: str
    password_hash: str
    salt: str
    roles: list[str] = None
    active: bool = True

    def __post_init__(self):
        self.roles = self.roles or []


class PasswordAuthenticator(AuthenticatorInterface):
    """
    Password-based authenticator with secure hashing
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize password authenticator"""
        self.config = config or {}
        self.users: dict[str, UserCredentials] = {}
        self.failed_attempts: dict[str, int] = {}
        self.lockout_threshold = self.config.get("lockout_threshold", 5)
        self.lockout_duration = self.config.get("lockout_duration_seconds", 300)  # 5 minutes
        self._load_users()

    def _load_users(self):
        """Load user credentials (in production, this would be from database)"""
        # Load from config or environment
        default_users = self.config.get("default_users", [])

        for user_config in default_users:
            username = user_config["username"]
            password = user_config["password"]
            roles = user_config.get("roles", ["user"])

            # Hash password
            salt = os.urandom(32).hex()
            password_hash = self._hash_password(password, salt)

            self.users[username] = UserCredentials(
                username=username,
                password_hash=password_hash,
                salt=salt,
                roles=roles
            )

        logger.info(f"Loaded {len(self.users)} users for password authentication")

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hex(password.encode(), salt.encode(), 100000)

    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        return hmac.compare_digest(password_hash, self._hash_password(password, salt))

    def _is_locked_out(self, username: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        attempts = self.failed_attempts.get(username, 0)
        return attempts >= self.lockout_threshold

    def _record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1

    def _clear_failed_attempts(self, username: str):
        """Clear failed attempts on successful login"""
        self.failed_attempts.pop(username, None)

    async def authenticate_user(self, username: str, password: str, **kwargs) -> AuthResult:
        """Authenticate user with username/password"""
        try:
            # Check lockout
            if self._is_locked_out(username):
                return AuthResult(
                    success=False,
                    error="Account locked due to too many failed attempts"
                )

            # Get user credentials
            user_creds = self.users.get(username)
            if not user_creds:
                self._record_failed_attempt(username)
                return AuthResult(
                    success=False,
                    error="Invalid username or password"
                )

            # Check if account is active
            if not user_creds.active:
                return AuthResult(
                    success=False,
                    error="Account is deactivated"
                )

            # Verify password
            if not self._verify_password(password, user_creds.password_hash, user_creds.salt):
                self._record_failed_attempt(username)
                return AuthResult(
                    success=False,
                    error="Invalid username or password"
                )

            # Successful authentication
            self._clear_failed_attempts(username)
            return AuthResult(
                success=True,
                user_id=f"user_{username}",
                username=username,
                roles=user_creds.roles.copy()
            )

        except Exception as e:
            logger.error(f"Password authentication failed: {e}")
            return AuthResult(
                success=False,
                error="Authentication error occurred"
            )

    async def authenticate_token(self, token: str, **kwargs) -> AuthResult:
        """Password authenticator doesn't handle tokens"""
        return AuthResult(
            success=False,
            error="Token authentication not supported by password authenticator"
        )

    async def authenticate_api_key(self, api_key: str, service_name: str = "unknown") -> AuthResult:
        """Password authenticator doesn't handle API keys"""
        return AuthResult(
            success=False,
            error="API key authentication not supported by password authenticator"
        )

    def add_user(self, username: str, password: str, roles: Optional[list[str]] = None) -> bool:
        """Add new user (for management purposes)"""
        try:
            if username in self.users:
                return False

            roles = roles or ["user"]
            salt = os.urandom(32).hex()
            password_hash = self._hash_password(password, salt)

            self.users[username] = UserCredentials(
                username=username,
                password_hash=password_hash,
                salt=salt,
                roles=roles
            )

            logger.info(f"Added user {username}")
            return True
        except Exception as e:
            logger.error(f"User addition failed: {e}")
            return False

    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account"""
        try:
            user = self.users.get(username)
            if user:
                user.active = False
                logger.info(f"Deactivated user {username}")
                return True
            return False
        except Exception as e:
            logger.error(f"User deactivation failed: {e}")
            return False


class ApiKeyAuthenticator(AuthenticatorInterface):
    """
    API key-based authenticator
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize API key authenticator"""
        self.config = config or {}
        self.api_keys: dict[str, dict] = {}
        self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from configuration"""
        # Load from config
        api_keys_config = self.config.get("api_keys", [])
        for key_config in api_keys_config:
            api_key = key_config["key"]
            self.api_keys[api_key] = {
                "service_name": key_config.get("service_name", "unknown"),
                "roles": key_config.get("roles", ["api_user"]),
                "active": key_config.get("active", True)
            }

        # Load from environment
        env_api_key = os.getenv("LUKHAS_API_KEY")
        if env_api_key:
            self.api_keys[env_api_key] = {
                "service_name": "lukhas_system",
                "roles": ["admin", "api_user"],
                "active": True
            }

        logger.info(f"Loaded {len(self.api_keys)} API keys")

    async def authenticate_user(self, username: str, password: str, **kwargs) -> AuthResult:
        """API key authenticator doesn't handle username/password"""
        return AuthResult(
            success=False,
            error="Username/password authentication not supported by API key authenticator"
        )

    async def authenticate_token(self, token: str, **kwargs) -> AuthResult:
        """API key authenticator doesn't handle tokens"""
        return AuthResult(
            success=False,
            error="Token authentication not supported by API key authenticator"
        )

    async def authenticate_api_key(self, api_key: str, service_name: str = "unknown") -> AuthResult:
        """Authenticate with API key"""
        try:
            key_info = self.api_keys.get(api_key)
            if not key_info:
                return AuthResult(
                    success=False,
                    error="Invalid API key"
                )

            if not key_info.get("active", True):
                return AuthResult(
                    success=False,
                    error="API key is deactivated"
                )

            return AuthResult(
                success=True,
                user_id=f"api_{key_info['service_name']}",
                username=f"api_user_{service_name}",
                roles=key_info["roles"].copy()
            )

        except Exception as e:
            logger.error(f"API key authentication failed: {e}")
            return AuthResult(
                success=False,
                error="API key authentication error occurred"
            )

    def add_api_key(self, api_key: str, service_name: str, roles: Optional[list[str]] = None) -> bool:
        """Add new API key"""
        try:
            if api_key in self.api_keys:
                return False

            self.api_keys[api_key] = {
                "service_name": service_name,
                "roles": roles or ["api_user"],
                "active": True
            }

            logger.info(f"Added API key for service {service_name}")
            return True
        except Exception as e:
            logger.error(f"API key addition failed: {e}")
            return False

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        try:
            key_info = self.api_keys.get(api_key)
            if key_info:
                key_info["active"] = False
                logger.info(f"Revoked API key for service {key_info['service_name']}")
                return True
            return False
        except Exception as e:
            logger.error(f"API key revocation failed: {e}")
            return False


# Factory functions
def create_password_authenticator(config: Optional[dict[str, Any]] = None) -> PasswordAuthenticator:
    """Create password authenticator instance"""
    return PasswordAuthenticator(config)


def create_api_key_authenticator(config: Optional[dict[str, Any]] = None) -> ApiKeyAuthenticator:
    """Create API key authenticator instance"""
    return ApiKeyAuthenticator(config)
