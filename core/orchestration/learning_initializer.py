# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: learning_initializer.py
# MODULE: orchestration.learning_initializer
# DESCRIPTION: Initializes learning service and registers it with the service registry
# DEPENDENCIES: orchestration.service_registry, learning.service
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
Learning Service Initializer

This module is responsible for initializing the learning service and registering
it with the service registry. This prevents circular dependencies by ensuring
the learning service is initialized at the orchestration layer.
"""

import logging
from typing import Optional

import structlog

from lukhas.orchestration.service_registry import ServiceNames, register_factory

# Initialize logger
logger = logging.getLogger(__name__)
logger = structlog.get_logger("ΛTRACE.orchestration.learning_initializer")


def _create_learning_service():
    """
    Factory function to create a learning service instance.

    This function is called lazily when the learning service is first requested.
    It imports the learning module only when needed to avoid import-time circular dependencies.
    """
    logger.info("ΛTRACE: Creating learning service instance")

    try:
        # Import learning service only when needed
        from learning.service import LearningService

        # Create and return the service instance
        service = LearningService()
        logger.info("ΛTRACE: Learning service created successfully")
        return service

    except ImportError as e:
        logger.error(
            "ΛTRACE: Failed to import learning service",
            error=str(e),
            exc_info=True,
        )

        # Return a fallback service if the real one can't be imported
        logger.warning("ΛTRACE: Using fallback learning service")

        class FallbackLearningService:
            """Fallback service when the real learning service can't be imported."""

            def learn_from_data(
                self,
                user_id: str,
                data_source: dict,
                learning_mode: str = "supervised",
                learning_objectives: Optional[list] = None,
            ) -> dict:
                logger.warning("ΛTRACE: Fallback learning service - learn_from_data called")
                return {
                    "success": False,
                    "error": "Learning service not available (using fallback)",
                    "fallback": True,
                }

            def adapt_behavior(
                self,
                user_id: str,
                adaptation_context: dict,
                behavior_targets: list,
                adaptation_strategy: str = "gradual",
            ) -> dict:
                logger.warning("ΛTRACE: Fallback learning service - adapt_behavior called")
                return {
                    "success": False,
                    "error": "Learning service not available (using fallback)",
                    "fallback": True,
                }

            def synthesize_knowledge(
                self,
                user_id: str,
                knowledge_sources: list,
                synthesis_method: str = "integration",
            ) -> dict:
                logger.warning("ΛTRACE: Fallback learning service - synthesize_knowledge called")
                return {
                    "success": False,
                    "error": "Learning service not available (using fallback)",
                    "fallback": True,
                }

            def transfer_learning(
                self,
                user_id: str,
                source_domain: str,
                target_domain: str,
                knowledge_to_transfer: dict,
            ) -> dict:
                logger.warning("ΛTRACE: Fallback learning service - transfer_learning called")
                return {
                    "success": False,
                    "error": "Learning service not available (using fallback)",
                    "fallback": True,
                }

            def get_learning_metrics(self, user_id: str, include_detailed: bool = False) -> dict:
                logger.warning("ΛTRACE: Fallback learning service - get_learning_metrics called")
                return {
                    "success": False,
                    "error": "Learning service not available (using fallback)",
                    "fallback": True,
                }

        return FallbackLearningService()

    except Exception as e:
        logger.error(
            "ΛTRACE: Unexpected error creating learning service",
            error=str(e),
            exc_info=True,
        )
        raise


def initialize_learning_service():
    """
    Initialize the learning service by registering its factory with the service registry.

    This should be called during application startup, typically from the main
    initialization sequence.
    """
    logger.info("ΛTRACE: Registering learning service factory")

    # Register the factory function with the service registry
    # The actual service will be created on first access
    register_factory(ServiceNames.LEARNING, _create_learning_service)

    logger.info("ΛTRACE: Learning service factory registered successfully")


# Auto-initialize when this module is imported
# This ensures the factory is registered even if
# initialize_learning_service() isn't called explicitly
initialize_learning_service()

if __name__ == "__main__":
    # Example/test usage
    from lukhas.orchestration.service_registry import get_service

    logger.info("ΛTRACE: Testing learning service initialization")

    # Get the service (will be created on first access)
    learning_service = get_service(ServiceNames.LEARNING)

    if learning_service:
        logger.info(
            "ΛTRACE: Learning service retrieved successfully",
            service_type=type(learning_service).__name__,
        )

        # Test a method
        result = learning_service.learn_from_data(
            "test_user",
            {"elements": ["test1", "test2"], "labels": ["a", "b"]},
            "supervised",
        )
        print("Test result:", result)
    else:
        logger.error("ΛTRACE: Failed to retrieve learning service")
