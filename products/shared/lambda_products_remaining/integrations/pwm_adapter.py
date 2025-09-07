"""
Lambda Products Adapter for Lukhas  Integration
Bridges Lambda Products into the advanced Lukhas  system

This adapter enables Lambda Products to work as plugins within the
sophisticated Lukhas  architecture, leveraging its existing
plugin registry and module registry systems.
"""

import logging
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from plugins.plugin_base import HealthStatus, LukhasPlugin, PluginManifest, PluginPriority, PluginStatus

# Add Lukhas  to path
lukhas_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
sys.path.insert(0, str(lukhas_path))

# Import Lukhas  components
try:
    from core.module_registry import ModuleInfo, ModuleRegistry, TierLevel
    from core.plugin_registry import Plugin, PluginRegistry, PluginType

    LUKHAS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Lukhas  components not available: {e}")
    LUKHAS_AVAILABLE = False

    # Define fallbacks
    class Plugin:
        pass

    class PluginType(Enum):
        SYMBOLIC_PROCESSOR = "symbolic_processor"

    class TierLevel:
        GUEST = 0
        VISITOR = 1
        FRIEND = 2
        TRUSTED = 3


# Add Lambda Products to path
lambda_products_path = Path(__file__).parent.parent
sys.path.insert(0, str(lambda_products_path))


logger = logging.getLogger(__name__)


class LambdaProductsPlugin(Plugin):
    """
    Base class for Lambda Products as Lukhas  plugins
    """

    def __init__(self, lambda_plugin: LukhasPlugin):
        self.lambda_plugin = lambda_plugin
        self.initialized = False

    def get_plugin_type(self) -> PluginType:
        """Lambda Products are symbolic processors"""
        return PluginType.SYMBOLIC_PROCESSOR

    def get_plugin_name(self) -> str:
        """Return Lambda Product name"""
        return self.lambda_plugin.manifest.id

    def get_version(self) -> str:
        """Return Lambda Product version"""
        return self.lambda_plugin.manifest.version

    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the Lambda Product"""
        if not self.initialized:
            success = await self.lambda_plugin.initialize(config)
            if success:
                success = await self.lambda_plugin.start()
                self.initialized = success
        return self.initialized

    async def process(self, input_data: Any) -> Any:
        """Process data through Lambda Product"""
        if not self.initialized:
            raise RuntimeError(f"{self.get_plugin_name()} not initialized")
        return await self.lambda_plugin.process(input_data)

    async def health_check(self) -> dict[str, Any]:
        """Check health status"""
        health = await self.lambda_plugin.health_check()
        return {
            "healthy": health.is_healthy,
            "cpu_usage": health.cpu_usage,
            "memory_usage": health.memory_usage,
            "response_time_ms": health.response_time_ms,
            "uptime": health.uptime_seconds,
        }


class LukhasIntegrationAdapter:
    """
    Adapter for integrating Lambda Products into Lukhas  system
    """

    def __init__(self):
        self.plugin_registry = None
        self.module_registry = None
        self.registered_products = {}

        if LUKHAS_AVAILABLE:
            self.plugin_registry = PluginRegistry()
            self.module_registry = ModuleRegistry()

    def get_tier_requirement(self, product_id: str) -> int:
        """Get minimum tier requirement for a Lambda Product"""
        tier_map = {
            "nias": TierLevel.FRIEND,  # T2 - Tier 2
            "abas": TierLevel.FRIEND,  # T2 - Tier 2
            "dast": TierLevel.TRUSTED,  # T3 - Tier 3
            "wallet": TierLevel.TRUSTED,  # T3 - Tier 3
            "lens": TierLevel.FRIEND,  # T2 - Tier 2
            "poetica": TierLevel.VISITOR,  # T1 - Tier 1
        }
        return tier_map.get(product_id, TierLevel.VISITOR)

    async def auto_register_all_products(self) -> list[str]:
        """Auto-register all Lambda Products with"""
        registered = []

        if not LUKHAS_AVAILABLE:
            return registered

        # Import all Lambda Products
        try:
            from plugins.lambda_products_adapter import get_all_lambda_products

            products = get_all_lambda_products()

            for product in products:
                if await self.register_lambda_product(product):
                    registered.append(product.manifest.id)
        except Exception as e:
            logger.error(f"Failed to auto-register products: {e}")

        return registered

    async def connect_consciousness_layer(self) -> bool:
        """Connect to Lukhas consciousness layer"""
        try:
            # Check if consciousness module is available
            pass

            return True
        except ImportError:
            return False

    async def register_lambda_product(
        self, lambda_plugin: LukhasPlugin, config: Optional[dict[str, Any]] = None
    ) -> bool:
        """Register a Lambda Product with Lukhas"""

        if not LUKHAS_AVAILABLE:
            logger.warning("Lukhas  not available, running in standalone mode")
            return False

        try:
            # Create  plugin wrapper
            _plugin = LambdaProductsPlugin(lambda_plugin)

            # Always initialize with config (use empty dict if not provided)
            init_config = config if config else {}
            await _plugin.initialize(init_config)

            # Register with plugin registry
            self.plugin_registry.register_plugin(_plugin)

            # Create module info for module registry
            module_info = ModuleInfo(
                module_id=f"lambda_{lambda_plugin.manifest.id}",
                name=lambda_plugin.manifest.name,
                version=lambda_plugin.manifest.version,
                path=f"lambda_products.{lambda_plugin.manifest.id}",
                instance=_plugin,
                min_tier=self.get_tier_requirement(lambda_plugin.manifest.id),
                permissions=set(lambda_plugin.manifest.capabilities),
                dependencies=lambda_plugin.manifest.dependencies,
                health_status=("healthy" if lambda_plugin.status == PluginStatus.ACTIVE else "unknown"),
            )

            # Register with module registry - use correct API signature
            self.module_registry.register_module(
                module_id=module_info.module_id,
                module_instance=_plugin,
                name=module_info.name,
                version=module_info.version,
                path=module_info.path,
                min_tier=module_info.min_tier,
                permissions=module_info.permissions,
                dependencies=module_info.dependencies,
            )

            # Track registration
            self.registered_products[lambda_plugin.manifest.id] = {
                "plugin": _plugin,
                "module_info": module_info,
                "lambda_plugin": lambda_plugin,
            }

            logger.info(f"✅ Registered {lambda_plugin.manifest.name} with Lukhas ")
            return True

        except Exception as e:
            logger.error(f"Failed to register {lambda_plugin.manifest.id}: {e}")
            return False

    async def validate_tier_access(self, product_id: str, user_tier: int) -> bool:
        """Validate if user tier has access to Lambda Product"""
        required_tier = self.get_tier_requirement(product_id)
        has_access = user_tier >= required_tier

        if not has_access:
            logger.warning(f"Access denied to {product_id}: User tier {user_tier} < Required {required_tier}")

        return has_access

    async def process_with_tier_check(self, product_id: str, input_data: Any, user_tier: int) -> Optional[Any]:
        """Process data through Lambda Product with tier validation"""

        # Check tier access
        if not await self.validate_tier_access(product_id, user_tier):
            return {
                "error": "Insufficient tier level",
                "required": self.get_tier_requirement(product_id),
            }

        # Get registered product
        if product_id not in self.registered_products:
            return {"error": f"Product {product_id} not registered"}

        # Process through product
        _plugin = self.registered_products[product_id]["plugin"]
        return await _plugin.process(input_data)

    async def get_system_status(self) -> dict[str, Any]:
        """Get overall system status"""
        status = {
            "_available": LUKHAS_AVAILABLE,
            "registered_products": list(self.registered_products.keys()),
            "health_status": {},
        }

        # Get health for each product
        for product_id, info in self.registered_products.items():
            try:
                health = await info["plugin"].health_check()
                status["health_status"][product_id] = health
            except Exception as e:
                status["health_status"][product_id] = {"error": str(e)}

        return status

    def get_module_registry_info(self) -> dict[str, Any]:
        """Get module registry information"""
        if not LUKHAS_AVAILABLE or not self.module_registry:
            return {"available": False}

        modules = {}
        for product_id, info in self.registered_products.items():
            module_info = info["module_info"]
            modules[product_id] = {
                "module_id": module_info.module_id,
                "name": module_info.name,
                "version": module_info.version,
                "min_tier": module_info.min_tier,
                "permissions": list(module_info.permissions),
                "health": module_info.health_status,
                "access_count": module_info.access_count,
            }

        return {"available": True, "modules": modules}


# Example Lambda Product implementations for
class NIASPlugin(LukhasPlugin):
    """NIΛS adapted for  integration"""

    def __init__(self):
        manifest = PluginManifest(
            id="nias",
            name="NIΛS - Non-Intrusive Messaging",
            version="2.0.0",
            description="Emotional gating and consent-based messaging for ",
            capabilities=["emotional_filtering", "consent_management", "tier_gating"],
            dependencies=[],
            priority=PluginPriority.HIGH,
            tier_requirements="T2",
        )
        super().__init__(manifest)
        self.message_queue = []
        self.tier_limits = {
            TierLevel.VISITOR: 5,
            TierLevel.FRIEND: 10,
            TierLevel.TRUSTED: 20,
        }

    async def initialize(self, config: dict[str, Any]) -> bool:
        self.config = config
        self.tier = config.get("user_tier", TierLevel.VISITOR)
        return True

    async def start(self) -> bool:
        self.status = PluginStatus.ACTIVE
        return True

    async def stop(self) -> bool:
        self.status = PluginStatus.DISABLED
        return True

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            is_healthy=True,
            last_check=datetime.now(timezone.utc),
            cpu_usage=5.0,
            memory_usage=50.0,
            response_time_ms=2.0,
            uptime_seconds=self.get_uptime(),
        )

    async def process(self, input_data: Any) -> dict[str, Any]:
        """Process message with emotional gating and tier limits"""

        # Check tier-based queue limit
        max_queue = self.tier_limits.get(self.tier, 5)

        # Emotional gating
        emotion = input_data.get("emotional_state", "neutral")
        consent = input_data.get("consent", False)

        if not consent:
            return {"delivered": False, "reason": "no_consent"}

        if emotion in ["stressed", "overwhelmed", "anxious"] and len(self.message_queue) < max_queue:
            self.message_queue.append(input_data.get("message"))
            return {
                "delivered": False,
                "queued": True,
                "queue_size": len(self.message_queue),
            }

        return {
            "delivered": True,
            "message": input_data.get("message"),
            "emotion_state": emotion,
            "tier": self.tier,
        }


class ABASPlugin(LukhasPlugin):
    """ΛBAS adapted for  integration"""

    def __init__(self):
        manifest = PluginManifest(
            id="abas",
            name="ΛBAS - Attention Boundary System",
            version="2.0.0",
            description="Attention management integrated with  consciousness",
            capabilities=[
                "boundary_protection",
                "flow_detection",
                "distraction_filtering",
            ],
            dependencies=["consciousness"],
            priority=PluginPriority.HIGH,
            tier_requirements="T2",
        )
        super().__init__(manifest)
        self.flow_state = False
        self.boundary_active = False

    async def initialize(self, config: dict[str, Any]) -> bool:
        self.config = config
        return True

    async def start(self) -> bool:
        self.status = PluginStatus.ACTIVE
        self.boundary_active = True
        return True

    async def stop(self) -> bool:
        self.status = PluginStatus.DISABLED
        self.boundary_active = False
        return True

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            is_healthy=True,
            last_check=datetime.now(timezone.utc),
            cpu_usage=3.0,
            memory_usage=40.0,
            response_time_ms=1.5,
            uptime_seconds=self.get_uptime(),
        )

    async def process(self, input_data: Any) -> dict[str, Any]:
        """Process attention management requests"""

        action = input_data.get("action")

        if action == "enter_flow":
            self.flow_state = True
            return {"status": "flow_active", "boundary": "protected"}

        elif action == "exit_flow":
            self.flow_state = False
            return {"status": "flow_inactive", "boundary": "open"}

        elif "interruption" in input_data:
            priority = input_data.get("priority", "low")

            if self.flow_state and priority in ["low", "medium"]:
                return {"allowed": False, "reason": "flow_protection"}

            return {"allowed": True, "processed": True}

        return {
            "flow_state": self.flow_state,
            "boundary_active": self.boundary_active,
            "attention_state": "focused" if self.flow_state else "available",
        }


class DASTPlugin(LukhasPlugin):
    """DΛST adapted for  integration"""

    def __init__(self):
        manifest = PluginManifest(
            id="dast",
            name="DΛST - Dynamic Adaptive Symbol Tracking",
            version="2.0.0",
            description="Context tracking integrated with  memory systems",
            capabilities=[
                "context_tracking",
                "pattern_recognition",
                "symbol_evolution",
            ],
            dependencies=["memory"],
            priority=PluginPriority.NORMAL,
            tier_requirements="T3",
        )
        super().__init__(manifest)
        self.context_buffer = []
        self.symbols = {}

    async def initialize(self, config: dict[str, Any]) -> bool:
        self.config = config
        self.max_context = config.get("context_depth", 100)
        return True

    async def start(self) -> bool:
        self.status = PluginStatus.ACTIVE
        return True

    async def stop(self) -> bool:
        self.status = PluginStatus.DISABLED
        return True

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            is_healthy=True,
            last_check=datetime.now(timezone.utc),
            cpu_usage=8.0,
            memory_usage=120.0,
            response_time_ms=5.0,
            uptime_seconds=self.get_uptime(),
        )

    async def process(self, input_data: Any) -> dict[str, Any]:
        """Track context and symbols"""

        if "event" in input_data:
            # Add to context buffer
            self.context_buffer.append(input_data["event"])
            if len(self.context_buffer) > self.max_context:
                self.context_buffer.pop(0)

        if "symbol_update" in input_data:
            # Track symbol evolution
            symbol = input_data["symbol_update"]
            symbol_id = symbol.get("symbol")
            if symbol_id not in self.symbols:
                self.symbols[symbol_id] = []
            self.symbols[symbol_id].append(symbol)

        if "query" in input_data:
            query = input_data["query"]

            if query == "current_context":
                return {"context": self.context_buffer[-10:]}

            elif query == "symbol_evolution":
                symbol_id = input_data.get("symbol")
                if symbol_id in self.symbols:
                    return {
                        "evolution": self.symbols[symbol_id],
                        "current_meaning": self.symbols[symbol_id][-1].get("meaning"),
                    }

        return {
            "context": "tracked",
            "symbols": list(self.symbols.keys())[:5],
            "predictions": ["pattern_a", "pattern_b"],
        }
