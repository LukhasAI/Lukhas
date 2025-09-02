"""
🏗️ Base Module Class
===================
Common base class for all LUKHAS modules.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from .config import ModuleConfig, get_config
from .decorators import retry, with_timeout
from .glyph import GLYPHToken, create_error_glyph
from .logger import get_module_logger


class ModuleState:
    """Module lifecycle states"""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class BaseModule(ABC):
    """
    Base class for all LUKHAS modules.

    Provides common functionality:
    - Configuration management
    - Logging
    - GLYPH token handling
    - State management
    - Health checks
    - Guardian integration
    """

    def __init__(self, module_name: str, module_type: str = "generic"):
        """
        Initialize base module.

        Args:
            module_name: Unique module name
            module_type: Module type (consciousness, memory, reasoning, etc.)
        """
        self.module_name = module_name
        self.module_type = module_type
        self.module_id = f"{module_name}_{uuid.uuid4().hex[:8]}"

        # Core components
        self.logger = get_module_logger(f"{module_type}.{module_name}")
        self.config: ModuleConfig = get_config(module_name)

        # State management
        self.state = ModuleState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self.initialized_at: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None

        # Module registry
        self._dependencies: set[str] = set()
        self._capabilities: set[str] = set()

        # Metrics
        self.metrics = {
            "requests_processed": 0,
            "errors": 0,
            "average_response_time": 0.0,
            "uptime_seconds": 0.0,
        }

        # Guardian client placeholder
        self.guardian = None

    async def initialize(self) -> None:
        """Initialize the module"""
        async with self._state_lock:
            if self.state != ModuleState.UNINITIALIZED:
                self.logger.warning(f"Module already initialized (state: {self.state})")
                return

            self.state = ModuleState.INITIALIZING

        try:
            self.logger.info(f"🚀 Initializing {self.module_name}")

            # Load configuration
            await self._load_configuration()

            # Initialize Guardian client
            await self._init_guardian()

            # Module-specific initialization
            await self._initialize_module()

            # Mark as ready
            async with self._state_lock:
                self.state = ModuleState.READY
                self.initialized_at = datetime.utcnow()

            self.logger.info(f"✅ {self.module_name} initialized successfully")

        except Exception as e:
            async with self._state_lock:
                self.state = ModuleState.ERROR
            self.logger.error(f"Failed to initialize {self.module_name}: {e}")
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the module"""
        async with self._state_lock:
            if self.state == ModuleState.TERMINATED:
                return

            self.state = ModuleState.TERMINATING

        try:
            self.logger.info(f"🛑 Shutting down {self.module_name}")

            # Module-specific shutdown
            await self._shutdown_module()

            # Clean up resources
            await self._cleanup_resources()

            async with self._state_lock:
                self.state = ModuleState.TERMINATED

            self.logger.info(f"✅ {self.module_name} shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise

    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """
        Handle incoming GLYPH token.

        Args:
            token: Incoming GLYPH token

        Returns:
            Response GLYPH token
        """
        # Check state
        if self.state != ModuleState.READY:
            return create_error_glyph(
                token,
                f"Module {self.module_name} not ready (state: {self.state})",
                error_code="MODULE_NOT_READY",
            )

        # Update metrics
        self.last_activity = datetime.utcnow()
        self.metrics["requests_processed"] += 1

        # Add to trace
        token.add_to_trace(self.module_name)

        try:
            # Guardian validation
            if self.guardian and not token.get_metadata("skip_guardian"):
                approved = await self._validate_with_guardian(token)
                if not approved:
                    return create_error_glyph(
                        token,
                        "Guardian rejected the request",
                        error_code="GUARDIAN_REJECTION",
                    )

            # Process token
            response = await self._process_glyph(token)

            return response

        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error processing GLYPH: {e}")
            return create_error_glyph(token, str(e), error_code=e.__class__.__name__)

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health status dictionary
        """
        uptime = 0.0
        if self.initialized_at:
            uptime = (datetime.utcnow() - self.initialized_at).total_seconds()

        return {
            "module_name": self.module_name,
            "module_type": self.module_type,
            "module_id": self.module_id,
            "state": self.state,
            "healthy": self.state == ModuleState.READY,
            "uptime_seconds": uptime,
            "last_activity": (self.last_activity.isoformat() if self.last_activity else None),
            "metrics": self.metrics,
            "dependencies": list(self._dependencies),
            "capabilities": list(self._capabilities),
        }

    def register_capability(self, capability: str) -> None:
        """Register a module capability"""
        self._capabilities.add(capability)

    def register_dependency(self, module_name: str) -> None:
        """Register a module dependency"""
        self._dependencies.add(module_name)

    def has_capability(self, capability: str) -> bool:
        """Check if module has a capability"""
        return capability in self._capabilities

    # Abstract methods to be implemented by subclasses

    @abstractmethod
    async def _initialize_module(self) -> None:
        """Module-specific initialization logic"""

    @abstractmethod
    async def _shutdown_module(self) -> None:
        """Module-specific shutdown logic"""

    @abstractmethod
    async def _process_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Process incoming GLYPH token"""

    # Protected helper methods

    async def _load_configuration(self) -> None:
        """Load module configuration"""
        # Configuration is already loaded in __init__
        # This method can be overridden for custom loading

    async def _init_guardian(self) -> None:
        """Initialize Guardian client"""
        try:
            # Import Guardian client if available
            from lukhas.governance.client import GuardianClient

            self.guardian = GuardianClient(self.module_name)
            await self.guardian.initialize()
            self.logger.info("Guardian client initialized")
        except ImportError:
            self.logger.warning("Guardian client not available")
            self.guardian = None

    async def _validate_with_guardian(self, token: GLYPHToken) -> bool:
        """Validate request with Guardian system"""
        if not self.guardian:
            return True

        try:
            result = await self.guardian.validate_request(
                {
                    "module": self.module_name,
                    "action": token.symbol,
                    "payload": token.payload,
                    "context": token.context.to_dict(),
                }
            )

            return result.get("approved", False)

        except Exception as e:
            self.logger.error(f"Guardian validation error: {e}")
            # Fail safe - reject on error
            return False

    async def _cleanup_resources(self) -> None:
        """Clean up module resources"""
        # Override in subclasses for custom cleanup

    @retry(max_attempts=3, delay=1.0)
    @with_timeout(30.0)
    async def call_module(self, module_name: str, token: GLYPHToken) -> GLYPHToken:
        """
        Call another module with retry and timeout.

        Args:
            module_name: Target module name
            token: GLYPH token to send

        Returns:
            Response token
        """
        # This would integrate with the module registry/router
        # For now, it's a placeholder
        raise NotImplementedError("Module registry integration pending")


class StatefulModule(BaseModule):
    """Base class for modules that maintain state"""

    def __init__(self, module_name: str, module_type: str = "stateful"):
        super().__init__(module_name, module_type)
        self._state_data: dict[str, Any] = {}
        self._state_version = 0

    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        return self._state_data.get(key, default)

    async def set_state(self, key: str, value: Any) -> None:
        """Set state value"""
        self._state_data[key] = value
        self._state_version += 1

    async def update_state(self, updates: dict[str, Any]) -> None:
        """Update multiple state values"""
        self._state_data.update(updates)
        self._state_version += 1

    async def clear_state(self) -> None:
        """Clear all state"""
        self._state_data.clear()
        self._state_version += 1

    async def export_state(self) -> dict[str, Any]:
        """Export current state"""
        return {
            "module_name": self.module_name,
            "state_version": self._state_version,
            "state_data": self._state_data.copy(),
            "exported_at": datetime.utcnow().isoformat(),
        }

    async def import_state(self, state_export: dict[str, Any]) -> None:
        """Import state from export"""
        if state_export.get("module_name") != self.module_name:
            raise ValueError(f"State export is for different module: {state_export.get('module_name')}")

        self._state_data = state_export.get("state_data", {}).copy()
        self._state_version = state_export.get("state_version", 0)
