"""
NIΛS Hub - Central coordination for NIAS system components
Adapted from system-pwm-advanced for Lambda Products integration
"""

import logging
from datetime import datetime
from typing import Any, Optional

from ..event_system.event_bus import NIASEventType, get_global_nias_event_bus

logger = logging.getLogger(__name__)


class NIASHub:
    """Central hub for NIΛS system coordination"""

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list[callable]] = {}
        self.event_bus = None
        self.is_initialized = False
        self.tier_configs = {
            "T1": {  # Premium
                "name": "Premium",
                "bin_capacity": "unlimited",
                "duration_days": "unlimited",
                "features": ["ad_free", "optional_feedback", "permanent_deletion"],
                "price_monthly": 29.99,
            },
            "T2": {  # Mid-tier
                "name": "Enhanced",
                "bin_capacity": 10,
                "duration_days": 14,
                "features": ["assistant_mode", "enhanced_widgets"],
                "price_monthly": 9.99,
            },
            "T3": {  # Freemium
                "name": "Basic",
                "bin_capacity": 5,
                "duration_days": 7,
                "features": ["mandatory_feedback", "basic_widgets"],
                "price_monthly": 0,
            },
        }

        logger.info("NIΛS hub initialized")

    async def initialize(self):
        """Initialize all NIΛS services"""
        if self.is_initialized:
            return

        # Get event bus
        self.event_bus = await get_global_nias_event_bus()

        # Register core services
        await self._register_core_services()

        # Set up event handlers
        self._setup_event_handlers()

        # Register with service discovery
        await self._register_with_lambda_products()

        self.is_initialized = True
        logger.info(f"NIΛS hub initialized with {len(self.services)} services")

    async def _register_core_services(self):
        """Register core NIΛS services"""
        from .consent_filter import get_consent_filter
        from .dream_recorder import get_dream_recorder
        from .nias_engine import get_nias_engine
        from .tier_manager import get_tier_manager
        from .widget_engine import get_widget_engine

        # Core services - use factory functions to get singleton instances
        services_to_register = [
            ("nias_engine", lambda: get_nias_engine(event_bus=self.event_bus)),
            ("dream_recorder", get_dream_recorder),
            ("tier_manager", get_tier_manager),
            ("widget_engine", get_widget_engine),
            ("consent_filter", get_consent_filter),
        ]

        for service_name, service_factory in services_to_register:
            try:
                # Get service instance
                instance = service_factory()

                await self.register_service(service_name, instance)
                logger.debug(f"Registered {service_name}")

            except Exception as e:
                logger.warning(f"Could not register {service_name}: {e}")

    def _setup_event_handlers(self):
        """Set up event handlers for NIΛS operations"""
        if not self.event_bus:
            return

        # Subscribe to key NIAS events
        self.event_bus.subscribe_to_nias_events(
            callback=self._handle_message_received,
            nias_event_types=[NIASEventType.MESSAGE_RECEIVED],
        )

        self.event_bus.subscribe_to_nias_events(
            callback=self._handle_user_interaction,
            nias_event_types=[
                NIASEventType.WIDGET_INTERACTED,
                NIASEventType.USER_FEEDBACK_RECEIVED,
            ],
        )

        self.event_bus.subscribe_to_nias_events(
            callback=self._handle_subscription_events,
            nias_event_types=[
                NIASEventType.SUBSCRIPTION_ACTIVATED,
                NIASEventType.SUBSCRIPTION_CANCELLED,
            ],
        )

    async def _handle_message_received(self, event):
        """Handle incoming message processing requests"""
        try:
            message_data = event.payload.get("message_data", {})
            user_id = event.user_id
            tier = event.tier

            # Process through NIΛS pipeline
            result = await self.process_symbolic_message(
                message_data, {"user_id": user_id, "tier": tier}
            )

            # Complete message processing
            await self.event_bus.complete_message_processing(
                message_id=event.payload.get("message_id"),
                correlation_id=event.correlation_id,
                result=result,
                user_id=user_id,
            )

        except Exception as e:
            logger.error(f"Error handling message received: {e}")

    async def _handle_user_interaction(self, event):
        """Handle user interaction events"""
        try:
            interaction_type = event.event_type
            user_id = event.user_id
            payload = event.payload

            # Update user engagement metrics
            await self._update_user_metrics(user_id, interaction_type, payload)

            # Check for tier upgrade opportunities
            await self._check_tier_upgrade(user_id)

        except Exception as e:
            logger.error(f"Error handling user interaction: {e}")

    async def _handle_subscription_events(self, event):
        """Handle subscription-related events"""
        try:
            user_id = event.user_id
            event_type = event.event_type

            if event_type == NIASEventType.SUBSCRIPTION_ACTIVATED.value:
                new_tier = event.payload.get("tier")
                await self._activate_subscription(user_id, new_tier)

            elif event_type == NIASEventType.SUBSCRIPTION_CANCELLED.value:
                await self._handle_subscription_cancellation(user_id)

        except Exception as e:
            logger.error(f"Error handling subscription event: {e}")

    async def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service

        # Initialize service if it has an initialize method
        if hasattr(service, "initialize"):
            await service.initialize()

        logger.debug(f"Registered service '{name}' with NIΛS hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    async def process_symbolic_message(
        self, message: dict[str, Any], user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a symbolic message through NIΛS system"""

        user_id = user_context.get("user_id")
        user_tier = user_context.get("tier", "T3")

        try:
            # Step 1: Check consent and tier permissions
            consent_filter = self.get_service("consent_filter")
            if consent_filter:
                consent_result = await consent_filter.check_consent(user_id, message)
                if not consent_result.get("approved", False):
                    return {
                        "status": "blocked",
                        "reason": "consent_denied",
                        "consent_result": consent_result,
                    }

            # Step 2: Check emotional gating (integration with ΛBAS)
            nias_engine = self.get_service("nias_engine")
            if nias_engine:
                emotional_check = await nias_engine.check_emotional_state(user_context)
                if not emotional_check.get("approved", False):
                    return {
                        "status": "deferred",
                        "reason": "emotional_gating",
                        "defer_until": emotional_check.get("defer_until"),
                    }

            # Step 3: Process through tier-appropriate pipeline
            tier_manager = self.get_service("tier_manager")
            if tier_manager:
                processing_config = await tier_manager.get_processing_config(user_tier)
                message = await tier_manager.apply_tier_filters(
                    message, processing_config
                )

            # Step 4: Generate widget/delivery method
            widget_engine = self.get_service("widget_engine")
            if widget_engine:
                widget_config = await widget_engine.generate_widget(
                    message, user_context, user_tier
                )

                return {
                    "status": "delivered",
                    "delivery_method": "widget",
                    "widget_config": widget_config,
                    "tier": user_tier,
                    "processed_at": datetime.now().isoformat(),
                }

            # Fallback: basic delivery
            return {
                "status": "delivered",
                "delivery_method": "basic",
                "message": message,
                "tier": user_tier,
                "processed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing symbolic message: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed_at": datetime.now().isoformat(),
            }

    async def _register_with_lambda_products(self):
        """Register NIΛS services with Lambda Products ecosystem"""
        try:
            # Integration with other Lambda Products
            lambda_services = [
                "QRG",  # Quantum Record Generation
                "ΛBAS",  # Behavioral Analytics
                "DΛST",  # Dynamic AI Solutions Tracker
                "ΛSYMBOLIC",  # Identity & Authentication
            ]

            for service_name in lambda_services:
                try:
                    # Register bi-directional integration
                    logger.debug(f"Registering integration with {service_name}")
                except Exception as e:
                    logger.warning(f"Could not integrate with {service_name}: {e}")

        except Exception as e:
            logger.warning(f"Could not register with Lambda Products: {e}")

    async def _update_user_metrics(
        self, user_id: str, interaction_type: str, payload: dict
    ):
        """Update user engagement and interaction metrics"""
        # This would integrate with analytics service
        logger.debug(f"Updating metrics for {user_id}: {interaction_type}")

    async def _check_tier_upgrade(self, user_id: str):
        """Check if user qualifies for tier upgrade"""
        # Logic for suggesting tier upgrades based on usage

    async def _activate_subscription(self, user_id: str, tier: str):
        """Activate subscription for user"""
        tier_manager = self.get_service("tier_manager")
        if tier_manager:
            await tier_manager.update_user_tier(user_id, tier)

    async def _handle_subscription_cancellation(self, user_id: str):
        """Handle subscription cancellation"""
        # Downgrade to T3 (freemium)
        await self._activate_subscription(user_id, "T3")

    async def health_check(self) -> dict[str, Any]:
        """Health check for all registered NIΛS services"""
        health = {"status": "healthy", "services": {}, "event_bus": "disconnected"}

        # Check event bus
        if self.event_bus:
            try:
                stats = self.event_bus.get_nias_stats()
                health["event_bus"] = "connected"
                health["event_bus_stats"] = stats
            except Exception as e:
                health["event_bus"] = f"error: {e}"

        # Check each service
        for name, service in self.services.items():
            try:
                if hasattr(service, "health_check"):
                    health["services"][name] = await service.health_check()
                else:
                    health["services"][name] = {"status": "active"}
            except Exception as e:
                health["services"][name] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"

        return health

    def get_tier_config(self, tier: str) -> dict[str, Any]:
        """Get configuration for a specific tier"""
        return self.tier_configs.get(tier, self.tier_configs["T3"])

    def get_all_tiers(self) -> dict[str, dict[str, Any]]:
        """Get all tier configurations"""
        return self.tier_configs


# Singleton instance
_nias_hub_instance = None


async def get_nias_hub() -> NIASHub:
    """Get or create the NIΛS hub instance"""
    global _nias_hub_instance
    if _nias_hub_instance is None:
        _nias_hub_instance = NIASHub()
        await _nias_hub_instance.initialize()
    return _nias_hub_instance
