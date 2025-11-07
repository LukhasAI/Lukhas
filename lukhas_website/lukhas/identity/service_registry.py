"""
LUKHAS Identity Service Registry
===============================
Coordinates all identity services and registers them with the global registry.
Provides T4 architecture compliant service discovery and initialization.
"""

# Schedule auto-initialization
import asyncio
import logging
from typing import Any, Optional

from core.registry import register, resolve

from .facades.authentication_facade import AuthenticationFacade
from .services.authenticator_service import ApiKeyAuthenticator, PasswordAuthenticator
from .services.session_service import SessionService
from .services.token_service import TokenService

logger = logging.getLogger(__name__)


class IdentityServiceRegistry:
    """
    Central registry for all identity services
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize service registry"""
        self.config = config or {}
        self._services: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize and register all identity services"""
        if self._initialized:
            return

        try:
            # Initialize core services
            await self._initialize_token_service()
            await self._initialize_session_service()
            await self._initialize_authenticators()
            await self._initialize_facade()

            self._initialized = True
            logger.info("Identity services initialized and registered")

        except Exception as e:
            logger.error(f"Identity service initialization failed: {e}")
            raise

    async def _initialize_token_service(self):
        """Initialize and register token service"""
        token_config = self.config.get("token_service", {})
        token_service = TokenService(token_config)

        # Register with both local and global registry
        self._services["token_manager"] = token_service
        register("token_manager", token_service)

        logger.info("Token service registered")

    async def _initialize_session_service(self):
        """Initialize and register session service"""
        session_config = self.config.get("session_service", {})
        session_service = SessionService(session_config)

        # Register with both local and global registry
        self._services["session_manager"] = session_service
        register("session_manager", session_service)

        logger.info("Session service registered")

    async def _initialize_authenticators(self):
        """Initialize and register authenticator services"""
        # Password authenticator
        password_config = self.config.get("password_authenticator", {
            "default_users": [
                {"username": "admin", "password": "admin", "roles": ["admin", "user"]},
                {"username": "user", "password": "user", "roles": ["user"]}
            ]
        })
        password_auth = PasswordAuthenticator(password_config)
        self._services["authenticator_password"] = password_auth
        register("authenticator_password", password_auth)

        # API Key authenticator
        api_key_config = self.config.get("api_key_authenticator", {})
        api_key_auth = ApiKeyAuthenticator(api_key_config)
        self._services["authenticator_api_key"] = api_key_auth
        register("authenticator_api_key", api_key_auth)

        logger.info("Authenticator services registered")

    async def _initialize_facade(self):
        """Initialize and register authentication facade"""
        facade_config = self.config.get("facade", {})
        auth_facade = AuthenticationFacade(facade_config)
        await auth_facade.initialize()

        # Register with both local and global registry
        self._services["authentication_facade"] = auth_facade
        register("authentication_facade", auth_facade)
        register("auth_service", auth_facade)  # Legacy alias

        logger.info("Authentication facade registered")

    def get_service(self, service_name: str) -> Any:
        """Get service by name"""
        return self._services.get(service_name) or resolve(service_name)

    async def get_health_status(self) -> dict[str, Any]:
        """Get health status of all services"""
        if not self._initialized:
            return {"initialized": False}

        health_status = {"initialized": True, "services": {}}

        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'get_health_status'):
                    health_status["services"][service_name] = service.get_health_status()
                else:
                    health_status["services"][service_name] = {"available": True}
            except Exception as e:
                health_status["services"][service_name] = {
                    "available": False,
                    "error": str(e)
                }

        return health_status

    async def shutdown(self):
        """Shutdown all services"""
        logger.info("Shutting down identity services")

        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'shutdown'):
                    await service.shutdown()
                logger.debug(f"Shutdown {service_name}")
            except Exception as e:
                logger.error(f"Error shutting down {service_name}: {e}")

        self._services.clear()
        self._initialized = False


# Global registry instance
_identity_registry: Optional[IdentityServiceRegistry] = None


async def initialize_identity_services(config: Optional[dict[str, Any]] = None) -> IdentityServiceRegistry:
    """Initialize identity services and return registry"""
    global _identity_registry

    if _identity_registry is None:
        _identity_registry = IdentityServiceRegistry(config)
        await _identity_registry.initialize()

    return _identity_registry


def get_identity_service_registry() -> Optional[IdentityServiceRegistry]:
    """Get the global identity service registry"""
    return _identity_registry


async def get_identity_service(service_name: str) -> Any:
    """Get identity service by name"""
    if _identity_registry:
        return _identity_registry.get_service(service_name)
    return None


# Convenience functions for backward compatibility
async def get_auth_service(config: Optional[dict[str, Any]] = None):
    """Get authentication service - backward compatibility"""
    registry = await initialize_identity_services(config)
    return registry.get_service("authentication_facade")


# Auto-initialize with default config if imported
async def _auto_initialize():
    """Auto-initialize identity services with default config"""
    try:
        await initialize_identity_services()
    except Exception as e:
        logger.debug(f"Auto-initialization failed: {e}")



if not _identity_registry:
    # Only auto-initialize in async context
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_auto_initialize())
    except RuntimeError:
        # No event loop running, skip auto-initialization
        pass
