"""
LUKHAS Identity Authentication Facade
====================================
T4 architecture compliant facade that coordinates authentication components
through clean interfaces and dependency injection.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional, Protocol, runtime_checkable

from core.interfaces import CoreInterface
from core.registry import register, resolve

logger = logging.getLogger(__name__)


@dataclass
class AuthResult:
    """Result of authentication operation"""

    success: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    roles: list[str] = None
    token: Optional[str] = None
    expires_at: Optional[float] = None
    error: Optional[str] = None

    def __post_init__(self):
        self.roles = self.roles or []


@dataclass
class UserProfile:
    """User profile information"""

    user_id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        self.roles = self.roles or []
        self.metadata = self.metadata or {}


@runtime_checkable
class AuthenticatorInterface(Protocol):
    """Protocol for authentication implementations"""

    async def authenticate_user(self, username: str, password: str, **kwargs) -> AuthResult:
        """Authenticate user with username/password"""
        ...

    async def authenticate_token(self, token: str, **kwargs) -> AuthResult:
        """Authenticate user with token"""
        ...

    async def authenticate_api_key(self, api_key: str, service_name: str = "unknown") -> AuthResult:
        """Authenticate with API key"""
        ...


@runtime_checkable
class TokenManagerInterface(Protocol):
    """Protocol for token management"""

    async def generate_token(self, user_id: str, username: str, **kwargs) -> str:
        """Generate authentication token"""
        ...

    async def validate_token(self, token: str, **kwargs) -> bool:
        """Validate authentication token"""
        ...

    async def refresh_token(self, token: str, **kwargs) -> str:
        """Refresh authentication token"""
        ...


@runtime_checkable
class SessionManagerInterface(Protocol):
    """Protocol for session management"""

    async def create_session(self, user_id: str, **kwargs) -> str:
        """Create user session"""
        ...

    async def get_session(self, session_id: str, **kwargs) -> dict[str, Any]:
        """Get session information"""
        ...

    async def destroy_session(self, session_id: str, **kwargs) -> bool:
        """Destroy user session"""
        ...


class AuthenticationFacade(CoreInterface):
    """
    T4 Architecture Authentication Facade

    Provides unified authentication interface while delegating to specialized
    components discovered through the registry system.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize authentication facade"""
        self.config = config or {}
        self._authenticators: list[AuthenticatorInterface] = []
        self._token_manager: Optional[TokenManagerInterface] = None
        self._session_manager: Optional[SessionManagerInterface] = None
        self._initialized = False

    async def initialize(self):
        """Initialize facade components via registry discovery"""
        if self._initialized:
            return

        try:
            # Discover authenticators
            auth_types = ["password", "ldap", "oauth", "api_key"]
            for auth_type in auth_types:
                authenticator = resolve(f"authenticator_{auth_type}")
                if authenticator:
                    self._authenticators.append(authenticator)
                    logger.info(f"Loaded {auth_type} authenticator")

            # Discover token manager
            self._token_manager = resolve("token_manager")
            if self._token_manager:
                logger.info("Loaded token manager")

            # Discover session manager
            self._session_manager = resolve("session_manager")
            if self._session_manager:
                logger.info("Loaded session manager")

            self._initialized = True
            logger.info(f"Authentication facade initialized with {len(self._authenticators)} authenticators")

        except Exception as e:
            logger.error(f"Failed to initialize authentication facade: {e}")
            raise

    async def authenticate_user(self, username: str, password: str, **kwargs) -> AuthResult:
        """Authenticate user through available authenticators"""
        await self.initialize()

        # Try each authenticator until one succeeds
        for authenticator in self._authenticators:
            try:
                result = await authenticator.authenticate_user(username, password, **kwargs)
                if result.success:
                    return result
            except Exception as e:
                logger.warning(f"Authenticator {type(authenticator).__name__} failed: {e}")
                continue

        return AuthResult(success=False, error="Authentication failed - no valid authenticator")

    async def authenticate_token(self, token: str, **kwargs) -> AuthResult:
        """Authenticate user with token"""
        await self.initialize()

        if not self._token_manager:
            return AuthResult(success=False, error="No token manager available")

        try:
            is_valid = await self._token_manager.validate_token(token, **kwargs)
            if is_valid:
                # Extract user info from token (simplified)
                # In production, this would decode JWT or query database
                return AuthResult(
                    success=True,
                    token=token,
                    user_id="extracted_from_token",  # Placeholder
                    username="extracted_from_token",  # Placeholder
                )
            else:
                return AuthResult(success=False, error="Invalid token")
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return AuthResult(success=False, error=str(e))

    async def authenticate_api_key(self, api_key: str, service_name: str = "unknown", **kwargs) -> AuthResult:
        """Authenticate with API key"""
        await self.initialize()

        # Try each authenticator that supports API key auth
        for authenticator in self._authenticators:
            if hasattr(authenticator, "authenticate_api_key"):
                try:
                    result = await authenticator.authenticate_api_key(api_key, service_name, **kwargs)
                    if result.success:
                        return result
                except Exception as e:
                    logger.warning(f"API key auth failed for {type(authenticator).__name__}: {e}")
                    continue

        return AuthResult(success=False, error="API key authentication failed")

    async def create_session(self, user_id: str, **kwargs) -> Optional[str]:
        """Create user session"""
        await self.initialize()

        if not self._session_manager:
            logger.warning("No session manager available")
            return None

        try:
            return await self._session_manager.create_session(user_id, **kwargs)
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return None

    async def get_session(self, session_id: str, **kwargs) -> Optional[dict[str, Any]]:
        """Get session information"""
        await self.initialize()

        if not self._session_manager:
            return None

        try:
            return await self._session_manager.get_session(session_id, **kwargs)
        except Exception as e:
            logger.error(f"Session retrieval failed: {e}")
            return None

    async def destroy_session(self, session_id: str, **kwargs) -> bool:
        """Destroy user session"""
        await self.initialize()

        if not self._session_manager:
            return False

        try:
            return await self._session_manager.destroy_session(session_id, **kwargs)
        except Exception as e:
            logger.error(f"Session destruction failed: {e}")
            return False

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of authentication facade"""
        return {
            "initialized": self._initialized,
            "authenticators_count": len(self._authenticators),
            "token_manager_available": self._token_manager is not None,
            "session_manager_available": self._session_manager is not None,
        }


# Factory functions for easy access
def get_authentication_facade(config: Optional[dict[str, Any]] = None) -> AuthenticationFacade:
    """Get authentication facade instance"""
    facade = resolve("authentication_facade")
    if not facade:
        facade = AuthenticationFacade(config)
        register("authentication_facade", facade)
    return facade


# Backward compatibility functions (delegate to facade)
async def authenticate_user(username: str, password: str, **kwargs) -> AuthResult:
    """Authenticate user - backward compatibility wrapper"""
    facade = get_authentication_facade()
    return await facade.authenticate_user(username, password, **kwargs)


async def authenticate_token(token: str, **kwargs) -> AuthResult:
    """Authenticate token - backward compatibility wrapper"""
    facade = get_authentication_facade()
    return await facade.authenticate_token(token, **kwargs)


async def authenticate_api_key(api_key: str, service_name: str = "unknown", **kwargs) -> AuthResult:
    """Authenticate API key - backward compatibility wrapper"""
    facade = get_authentication_facade()
    return await facade.authenticate_api_key(api_key, service_name, **kwargs)
