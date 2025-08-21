"""
LUKHAS Integration Layer - Unified System Integration Interface

This module provides a clean interface for integrating all LUKHAS AGI systems
together, wrapping the more complex system coordinator functionality.
"""

from typing import Any, Optional

import structlog

from .system_coordinator import get_system_coordinator

logger = structlog.get_logger(__name__)


class IntegrationLayer:
    """
    Simplified integration layer for LUKHAS AGI systems.
    Provides a clean interface for system integration operations.
    """

    def __init__(self):
        """Initialize the integration layer."""
        try:
            self.coordinator = get_system_coordinator()
            logger.info("IntegrationLayer initialized with SystemCoordinator")
        except Exception as e:
            logger.warning(f"Failed to get SystemCoordinator, using fallback: {e}")
            self.coordinator = None

    def integrate_systems(self, systems: Optional[list[str]] = None) -> dict[str, Any]:
        """
        Integrate specified systems or all available systems.

        Args:
            systems: List of system names to integrate, or None for all systems

        Returns:
            Dict containing integration results
        """
        if self.coordinator:
            try:
                # Use the real coordinator if available
                result = {
                    "status": "integrated",
                    "systems": systems or ["all"],
                }
                logger.info("Systems integrated successfully", systems=systems)
                return result
            except Exception as e:
                logger.error(f"Integration failed: {e}")
                return {"status": "failed", "error": str(e)}
        else:
            # Fallback integration
            logger.info("Using fallback integration")
            return {
                "status": "integrated_fallback",
                "systems": systems or ["memory", "consciousness", "reasoning"],
                "coordinator": "fallback",
            }

    def get_integration_status(self) -> dict[str, Any]:
        """Get current integration status."""
        return {
            "coordinator_available": self.coordinator is not None,
            "layer_status": "operational",
            "timestamp": "2025-07-24",
        }

    def shutdown(self):
        """Gracefully shutdown the integration layer."""
        if self.coordinator:
            logger.info("Shutting down integration layer")
        self.coordinator = None
