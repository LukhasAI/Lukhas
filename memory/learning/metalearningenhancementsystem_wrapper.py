"""
Meta-Learning Enhancement System Wrapper
Integration wrapper for meta-learning enhancement system
"""

from typing import Any, Dict, Optional

from core.common import get_logger

try:
    from .metalearningenhancementsystem import (
        Enhancementmode,
        MetaLearningEnhancementsystem,
        Systemintegrationstatus,
    )

    # Use the correct case for the enum
    EnhancementMode = Enhancementmode
    META_ENHANCEMENT_AVAILABLE = True
except ImportError as e:
    META_ENHANCEMENT_AVAILABLE = False
    logging.warning(f"Meta-learning enhancement system not available: {e}")
    # Try mock implementation
    try:
        from .metalearningenhancementsystem_mock import (
            EnhancementMode,
            MetaLearningEnhancementsystem,
            Systemintegrationstatus,
        )
        from .metalearningenhancementsystem_mock import (
            get_meta_learning_enhancement as get_mock_enhancement,
        )

        META_ENHANCEMENT_AVAILABLE = True
        USING_MOCK = True
        logging.info("Using mock meta-learning enhancement implementation")
    except ImportError as e2:
        logging.warning(f"Mock meta-learning enhancement also not available: {e2}")
        USING_MOCK = False
else:
    USING_MOCK = False

logger = get_logger(__name__)


class MetaLearningEnhancementWrapper:
    """Wrapper for meta-learning enhancement functionality"""

    def __init__(self, node_id: str = "lukhas_primary"):
        if not META_ENHANCEMENT_AVAILABLE:
            raise ImportError("Meta-learning enhancement module not available")

        # Initialize the enhancement system
        self.enhancement_system = MetaLearningEnhancementsystem(
            node_id=node_id,
            enhancement_mode=EnhancementMode.OPTIMIZATION_ACTIVE,
            enable_federation=False,  # Can be configured
        )

        # Track integration status
        self.integration_stats = {
            "total_enhancements": 0,
            "successful_enhancements": 0,
            "failed_enhancements": 0,
            "active_monitors": 0,
            "optimization_events": 0,
            "federated_nodes": 0,
        }

        logger.info(f"MetaLearningEnhancementWrapper initialized for node: {node_id}")

    async def initialize(self):
        """Initialize and discover existing meta-learning systems"""
        try:
            # Discover and enhance existing systems
            discovery_results = (
                await self.enhancement_system.discover_and_enhance_meta_learning_systems()
            )

            # Update stats from discovery
            self.integration_stats["total_enhancements"] = len(
                discovery_results.get("enhancement_results", [])
            )
            self.integration_stats["successful_enhancements"] = sum(
                1
                for r in discovery_results.get("enhancement_results", [])
                if r.get("success", False)
            )

            logger.info(
                f"Enhanced {self.integration_stats['successful_enhancements']} meta-learning systems"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize meta-learning enhancement: {e}")
            return False

    async def enhance_learning_process(
        self, learning_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance a learning process with monitoring and optimization"""
        try:
            # Create enhanced learning configuration
            enhanced_config = (
                await self.enhancement_system.create_enhanced_learning_config(
                    learning_context
                )
            )

            # Apply dynamic optimization if enabled
            if (
                self.enhancement_system.enhancement_mode
                == EnhancementMode.OPTIMIZATION_ACTIVE
            ):
                optimization_result = (
                    await self.enhancement_system.apply_dynamic_optimization(
                        enhanced_config, learning_context
                    )
                )
                enhanced_config["optimization"] = optimization_result
                self.integration_stats["optimization_events"] += 1

            # Start monitoring if not already active
            if hasattr(self.enhancement_system, "monitor_dashboard"):
                monitor_id = await self.enhancement_system.monitor_dashboard.start_monitoring_session(
                    {"context": learning_context, "config": enhanced_config}
                )
                enhanced_config["monitor_id"] = monitor_id
                self.integration_stats["active_monitors"] += 1

            return {
                "success": True,
                "enhanced_config": enhanced_config,
                "monitoring_active": True,
                "optimization_applied": self.enhancement_system.enhancement_mode
                == EnhancementMode.OPTIMIZATION_ACTIVE,
            }

        except Exception as e:
            logger.error(f"Error enhancing learning process: {e}")
            self.integration_stats["failed_enhancements"] += 1
            return {"success": False, "error": str(e)}

    async def get_learning_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics from monitor dashboard"""
        if hasattr(self.enhancement_system, "monitor_dashboard"):
            return (
                await self.enhancement_system.monitor_dashboard.get_aggregated_metrics()
            )
        return {}

    async def apply_symbolic_feedback(
        self, feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply symbolic feedback to learning process"""
        if hasattr(self.enhancement_system, "symbolic_feedback"):
            return await self.enhancement_system.symbolic_feedback.process_feedback(
                feedback_data
            )
        return {"error": "Symbolic feedback not available"}

    async def enable_federation(self, federation_config: Dict[str, Any]) -> bool:
        """Enable federated learning coordination"""
        try:
            if not self.enhancement_system.enable_federation:
                # Initialize federated integration
                from .federated_integration import (
                    FederatedLearningIntegration,
                    FederationStrategy,
                )

                self.enhancement_system.federated_integration = (
                    FederatedLearningIntegration(
                        node_id=self.enhancement_system.node_id,
                        federation_strategy=FederationStrategy.BALANCED_HYBRID,
                    )
                )

                # Connect with other components
                self.enhancement_system.federated_integration.integrate_with_enhancement_system(
                    monitor_dashboard=self.enhancement_system.monitor_dashboard,
                    rate_modulator=self.enhancement_system.rate_modulator,
                    symbolic_feedback=self.enhancement_system.symbolic_feedback,
                )

                self.enhancement_system.enable_federation = True
                self.integration_stats["federated_nodes"] = 1

                logger.info("Federated learning enabled")
                return True

        except Exception as e:
            logger.error(f"Failed to enable federation: {e}")
            return False

    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        status = {
            "node_id": self.enhancement_system.node_id,
            "enhancement_mode": self.enhancement_system.enhancement_mode.value,
            "federation_enabled": self.enhancement_system.enable_federation,
            "integration_stats": self.integration_stats.copy(),
        }

        # Add system integration status if available
        if hasattr(self.enhancement_system, "integration_status"):
            status["system_status"] = {
                "systems_found": self.enhancement_system.integration_status.meta_learning_systems_found,
                "systems_enhanced": self.enhancement_system.integration_status.systems_enhanced,
                "monitoring_active": self.enhancement_system.integration_status.monitoring_active,
                "optimization_active": self.enhancement_system.integration_status.rate_optimization_active,
            }

        return status

    async def shutdown(self):
        """Shutdown enhancement system"""
        logger.info("Shutting down meta-learning enhancement system")
        # Cleanup any active monitors or connections
        if hasattr(self.enhancement_system, "monitor_dashboard"):
            await self.enhancement_system.monitor_dashboard.stop_all_monitoring()


def get_meta_learning_enhancement(
    node_id: str = "lukhas_primary",
) -> Optional[MetaLearningEnhancementWrapper]:
    """Factory function to create meta-learning enhancement wrapper"""
    if not META_ENHANCEMENT_AVAILABLE:
        logger.warning("Meta-learning enhancement not available")
        return None

    if USING_MOCK:
        try:
            return get_mock_enhancement(node_id)
        except Exception as e:
            logger.error(f"Failed to create mock enhancement: {e}")
            return None
    else:
        try:
            return MetaLearningEnhancementWrapper(node_id)
        except Exception as e:
            logger.error(f"Failed to create enhancement wrapper: {e}")
            return None
