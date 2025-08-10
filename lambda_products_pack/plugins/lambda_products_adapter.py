"""
Lambda Products Adapter for LUKHAS Plugin System
Integrates all Lambda Products as modular plugins into LUKHAS PWM

This adapter provides unified access to:
- NIΛS: Non-intrusive messaging with emotional gating
- ΛBAS: Attention boundary management
- DΛST: Dynamic context tracking
- WΛLLET: Digital identity and wallet
- ΛLens: AR/VR symbolic dashboards
And all other Lambda Products
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add lambda-products to path for imports
lambda_products_path = Path(__file__).parent.parent
sys.path.insert(0, str(lambda_products_path))

from .plugin_base import (
    HealthStatus,
    LukhasPlugin,
    PluginManifest,
    PluginPriority,
    PluginStatus,
)

logger = logging.getLogger(__name__)


class NIASPlugin(LukhasPlugin):
    """NIΛS - Non-Intrusive Lambda Symbolic System Plugin"""

    def __init__(self):
        manifest = PluginManifest(
            id="nias",
            name="NIΛS - Non-Intrusive Messaging",
            version="1.0.0",
            description="Ethical message delivery with emotional gating and consent management",
            capabilities=[
                "emotional_gating",
                "consent_management",
                "symbolic_processing",
                "dream_seed_integration",
                "tiered_subscriptions",
            ],
            endpoints=[
                "/api/v1/lambda/nias/message",
                "/api/v1/lambda/nias/consent",
                "/api/v1/lambda/nias/dream_seed",
            ],
            dependencies=[],
            priority=PluginPriority.HIGH,
            tier_requirements="T1",  # Available from Tier 1
        )
        super().__init__(manifest)
        self.nias_engine = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize NIΛS engine"""
        try:
            from NIΛS.core.nias_engine import NIASEngine

            self.nias_engine = NIASEngine(
                tier_level=config.get("tier", "T3"),
                emotional_gating=config.get("emotional_gating", True),
                dream_integration=config.get("dream_integration", False),
            )

            await self.nias_engine.initialize()
            self.status = PluginStatus.READY
            logger.info("NIΛS plugin initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize NIΛS: {e}")
            self.status = PluginStatus.ERROR
            return False

    async def start(self) -> bool:
        """Start NIΛS services"""
        try:
            if self.nias_engine:
                await self.nias_engine.start()
                self.status = PluginStatus.ACTIVE
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to start NIΛS: {e}")
            return False

    async def stop(self) -> bool:
        """Stop NIΛS services"""
        try:
            if self.nias_engine:
                await self.nias_engine.stop()
                self.status = PluginStatus.DISABLED
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to stop NIΛS: {e}")
            return False

    async def health_check(self) -> HealthStatus:
        """Check NIΛS health"""
        try:
            is_healthy = (
                self.nias_engine is not None and self.status == PluginStatus.ACTIVE
            )

            return HealthStatus(
                is_healthy=is_healthy,
                last_check=datetime.now(),
                response_time_ms=10.0 if is_healthy else 1000.0,
                error_count=0 if is_healthy else 1,
                uptime_seconds=self.get_uptime(),
                custom_metrics={
                    "messages_processed": (
                        getattr(self.nias_engine, "message_count", 0)
                        if self.nias_engine
                        else 0
                    ),
                    "consent_checks": (
                        getattr(self.nias_engine, "consent_checks", 0)
                        if self.nias_engine
                        else 0
                    ),
                },
            )
        except Exception as e:
            logger.error(f"Health check failed for NIΛS: {e}")
            return HealthStatus(
                is_healthy=False, last_check=datetime.now(), error_count=1
            )

    async def process(self, input_data: Any) -> Any:
        """Process message through NIΛS"""
        if not self.nias_engine:
            raise RuntimeError("NIΛS engine not initialized")

        return await self.nias_engine.process_message(input_data)


class ABASPlugin(LukhasPlugin):
    """ΛBAS - Lambda Boundary Attention System Plugin"""

    def __init__(self):
        manifest = PluginManifest(
            id="abas",
            name="ΛBAS - Attention Management",
            version="1.0.0",
            description="Intelligent attention boundary protection and flow state preservation",
            capabilities=[
                "attention_monitoring",
                "boundary_protection",
                "flow_state_detection",
                "cognitive_load_management",
                "distraction_filtering",
            ],
            endpoints=[
                "/api/v1/lambda/abas/attention",
                "/api/v1/lambda/abas/boundaries",
                "/api/v1/lambda/abas/flow_state",
            ],
            dependencies=[],
            priority=PluginPriority.HIGH,
            tier_requirements="T2",  # Available from Tier 2
        )
        super().__init__(manifest)
        self.abas_core = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize ΛBAS core"""
        try:
            # Import would be from actual ΛBAS implementation
            # from ΛBAS.core import ABASCore
            # self.abas_core = ABASCore(config)

            # For now, mock initialization
            self.abas_core = {"initialized": True, "config": config}
            self.status = PluginStatus.READY
            logger.info("ΛBAS plugin initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize ΛBAS: {e}")
            self.status = PluginStatus.ERROR
            return False

    async def start(self) -> bool:
        """Start ΛBAS services"""
        self.status = PluginStatus.ACTIVE
        return True

    async def stop(self) -> bool:
        """Stop ΛBAS services"""
        self.status = PluginStatus.DISABLED
        return True

    async def health_check(self) -> HealthStatus:
        """Check ΛBAS health"""
        return HealthStatus(
            is_healthy=self.status == PluginStatus.ACTIVE,
            last_check=datetime.now(),
            uptime_seconds=self.get_uptime(),
        )

    async def process(self, input_data: Any) -> Any:
        """Process attention state through ΛBAS"""
        # Implementation would process attention boundaries
        return {"attention_state": "focused", "boundary_status": "protected"}


class DASTPlugin(LukhasPlugin):
    """DΛST - Dynamic Lambda Symbol Tracker Plugin"""

    def __init__(self):
        manifest = PluginManifest(
            id="dast",
            name="DΛST - Context Tracking",
            version="1.0.0",
            description="Real-time symbolic context intelligence with predictive patterns",
            capabilities=[
                "context_tracking",
                "symbol_evolution",
                "pattern_prediction",
                "activity_correlation",
                "semantic_mapping",
            ],
            endpoints=[
                "/api/v1/lambda/dast/context",
                "/api/v1/lambda/dast/symbols",
                "/api/v1/lambda/dast/predictions",
            ],
            dependencies=[],
            priority=PluginPriority.NORMAL,
            tier_requirements="T1",
        )
        super().__init__(manifest)
        self.dast_engine = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize DΛST engine"""
        try:
            # Would import actual DAST implementation
            # from DΛST.core import DASTEngine
            # self.dast_engine = DASTEngine(config)

            self.dast_engine = {"initialized": True, "tracking": True}
            self.status = PluginStatus.READY
            logger.info("DΛST plugin initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize DΛST: {e}")
            self.status = PluginStatus.ERROR
            return False

    async def start(self) -> bool:
        """Start DΛST services"""
        self.status = PluginStatus.ACTIVE
        return True

    async def stop(self) -> bool:
        """Stop DΛST services"""
        self.status = PluginStatus.DISABLED
        return True

    async def health_check(self) -> HealthStatus:
        """Check DΛST health"""
        return HealthStatus(
            is_healthy=self.status == PluginStatus.ACTIVE,
            last_check=datetime.now(),
            uptime_seconds=self.get_uptime(),
            custom_metrics={"contexts_tracked": 42, "symbols_evolved": 17},
        )

    async def process(self, input_data: Any) -> Any:
        """Process context through DΛST"""
        return {
            "context": "analyzed",
            "symbols": ["λ", "∞", "Ω"],
            "predictions": ["pattern_a", "pattern_b"],
        }


class LambdaProductsAdapter:
    """
    Main adapter for integrating all Lambda Products into LUKHAS PWM

    This class manages the registration and lifecycle of Lambda Product plugins,
    providing a unified interface for the LUKHAS ecosystem.
    """

    def __init__(self, plugin_system=None):
        """
        Initialize the Lambda Products Adapter

        Args:
            plugin_system: Optional PluginSystem instance to register with
        """
        self.plugin_system = plugin_system
        self.available_products = {
            "nias": NIASPlugin,
            "abas": ABASPlugin,
            "dast": DASTPlugin,
            # Additional products would be added here:
            # 'wallet': WalletPlugin,
            # 'lens': LensPlugin,
            # 'trace': TracePlugin,
            # 'nimbus': NimbusPlugin,
            # 'legado': LegadoPlugin,
            # 'poetica': PoeticaPlugin,
            # 'argus': ArgusPlugin,
            # 'marketplace': MarketplacePlugin,
        }
        self.enabled_products: Dict[str, LukhasPlugin] = {}

    async def enable_product(
        self, product_id: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[LukhasPlugin]:
        """
        Enable a specific Lambda Product

        Args:
            product_id: ID of the product to enable
            config: Product-specific configuration

        Returns:
            Plugin instance if successful, None otherwise
        """
        if product_id not in self.available_products:
            logger.error(f"Unknown Lambda Product: {product_id}")
            return None

        if product_id in self.enabled_products:
            logger.warning(f"Product {product_id} already enabled")
            return self.enabled_products[product_id]

        try:
            # Create plugin instance
            plugin_class = self.available_products[product_id]
            plugin = plugin_class()

            # Initialize with config
            config = config or {}
            success = await plugin.initialize(config)

            if not success:
                logger.error(f"Failed to initialize {product_id}")
                return None

            # Register with plugin system if available
            if self.plugin_system:
                await self.plugin_system.register_plugin(plugin)
                await self.plugin_system.start_plugin(product_id)
            else:
                # Start plugin directly
                await plugin.start()

            # Store reference
            self.enabled_products[product_id] = plugin

            logger.info(f"Lambda Product {product_id} enabled successfully")
            return plugin

        except Exception as e:
            logger.error(f"Error enabling Lambda Product {product_id}: {e}")
            return None

    async def disable_product(self, product_id: str) -> bool:
        """
        Disable a Lambda Product

        Args:
            product_id: ID of the product to disable

        Returns:
            bool: True if successfully disabled
        """
        if product_id not in self.enabled_products:
            logger.warning(f"Product {product_id} not enabled")
            return False

        try:
            plugin = self.enabled_products[product_id]

            # Stop through plugin system or directly
            if self.plugin_system:
                success = await self.plugin_system.stop_plugin(product_id)
            else:
                success = await plugin.stop()

            if success:
                del self.enabled_products[product_id]
                logger.info(f"Lambda Product {product_id} disabled successfully")

            return success

        except Exception as e:
            logger.error(f"Error disabling Lambda Product {product_id}: {e}")
            return False

    async def enable_all_products(
        self, configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, bool]:
        """
        Enable all available Lambda Products

        Args:
            configs: Dictionary of product-specific configurations

        Returns:
            Dict mapping product IDs to success status
        """
        configs = configs or {}
        results = {}

        for product_id in self.available_products:
            config = configs.get(product_id, {})
            plugin = await self.enable_product(product_id, config)
            results[product_id] = plugin is not None

        return results

    async def get_product(self, product_id: str) -> Optional[LukhasPlugin]:
        """
        Get an enabled Lambda Product plugin

        Args:
            product_id: ID of the product

        Returns:
            Plugin instance if enabled and healthy, None otherwise
        """
        if product_id not in self.enabled_products:
            return None

        plugin = self.enabled_products[product_id]

        # Check health
        health = await plugin.health_check()
        if health.is_healthy:
            return plugin

        logger.warning(f"Product {product_id} is not healthy")
        return None

    def get_enabled_products(self) -> List[str]:
        """Get list of currently enabled products"""
        return list(self.enabled_products.keys())

    def get_available_products(self) -> List[str]:
        """Get list of all available products"""
        return list(self.available_products.keys())

    async def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary of all Lambda Products"""
        summary = {
            "available": self.get_available_products(),
            "enabled": self.get_enabled_products(),
            "status": {},
        }

        for product_id, plugin in self.enabled_products.items():
            health = await plugin.health_check()
            summary["status"][product_id] = {
                "status": plugin.status.value,
                "healthy": health.is_healthy,
                "uptime": plugin.get_uptime(),
                "version": plugin.manifest.version,
                "tier": plugin.manifest.tier_requirements,
            }

        return summary


# Export main classes
__all__ = ["LambdaProductsAdapter", "NIASPlugin", "ABASPlugin", "DASTPlugin"]
