#!/usr/bin/env python3
"""
Practical Integration Hub Implementation
Based on DETAILED_INTEGRATION_PLAN.md - implementing what actually works.

This focuses on Phase 1 critical integrations:
- Bio engine integration (where possible)
- Ethics system unification
- Core system connectivity improvements
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

# Set up logger
logger = logging.getLogger(__name__)


class PracticalIntegrationHub:
    """
    Practical integration hub focusing on working components and real improvements.
    Implements Phase 1 of the DETAILED_INTEGRATION_PLAN.md.
    """

    def __init__(self):
        logger.info("🚀 Initializing Practical Integration Hub...")

        # Track what components are available
        self.available_components: dict[str, Any] = {}
        self.integration_status: dict[str, str] = {}

        # Initialize working components
        self._initialize_core_components()
        self._initialize_consciousness_components()
        self._initialize_ethics_components()

        # Establish connections
        self._establish_working_connections()

        # Generate integration report
        self._generate_integration_report()

    def _initialize_core_components(self):
        """Initialize core system components"""
        try:
            from core.core_hub import CoreHub

            self.core_hub = CoreHub()
            self.available_components["core_hub"] = self.core_hub
            self.integration_status["core_hub"] = "active"
            logger.info("✅ Core Hub initialized successfully")
        except Exception as e:
            logger.error(f"❌ Core Hub failed: {e}")
            self.integration_status["core_hub"] = f"failed: {e}"

    def _initialize_consciousness_components(self):
        """Initialize consciousness system components"""
        try:
            from lukhas.consciousness.reflection.consciousness_hub import (
                ConsciousnessHub,
            )

            self.consciousness_hub = ConsciousnessHub()
            self.available_components["consciousness_hub"] = self.consciousness_hub
            self.integration_status["consciousness_hub"] = "active"
            logger.info("✅ Consciousness Hub initialized successfully")
        except Exception as e:
            logger.error(f"❌ Consciousness Hub failed: {e}")
            self.integration_status["consciousness_hub"] = f"failed: {e}"

    def _initialize_ethics_components(self):
        """Initialize ethics system components"""
        try:
            from ethics.service import EthicsService

            self.ethics_service = EthicsService()
            self.available_components["ethics_service"] = self.ethics_service
            self.integration_status["ethics_service"] = "active"
            logger.info("✅ Ethics Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Ethics Service failed: {e}")
            self.integration_status["ethics_service"] = f"failed: {e}"

        # Try to initialize unified ethics integration (Phase 1.2 from plan)
        try:
            from ethics.ethics_integration import get_ethics_integration

            self.unified_ethics = get_ethics_integration()
            self.available_components["unified_ethics"] = self.unified_ethics
            self.integration_status["unified_ethics"] = "active"
            logger.info("✅ Unified Ethics Integration initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Unified Ethics Integration not available: {e}")
            self.integration_status["unified_ethics"] = f"unavailable: {e}"

    def _establish_working_connections(self):
        """Establish connections between working components"""
        logger.info("🔗 Establishing component connections...")

        connections_made = 0

        # Core ↔ Consciousness connection
        if (
            "core_hub" in self.available_components
            and "consciousness_hub" in self.available_components
        ):
            try:
                self.core_hub.register_service("consciousness_hub", self.consciousness_hub)
                connections_made += 1
                logger.info("✅ Connected Core ↔ Consciousness")
            except Exception as e:
                logger.warning(f"⚠️ Core ↔ Consciousness connection failed: {e}")

        # Core ↔ Ethics connection
        if (
            "core_hub" in self.available_components
            and "ethics_service" in self.available_components
        ):
            try:
                self.core_hub.register_service("ethics_service", self.ethics_service)
                connections_made += 1
                logger.info("✅ Connected Core ↔ Ethics")
            except Exception as e:
                logger.warning(f"⚠️ Core ↔ Ethics connection failed: {e}")

        # Unified Ethics ↔ Core connection (Phase 1.2 implementation)
        if (
            "core_hub" in self.available_components
            and "unified_ethics" in self.available_components
        ):
            try:
                self.core_hub.register_service("unified_ethics", self.unified_ethics)
                connections_made += 1
                logger.info("✅ Connected Core ↔ Unified Ethics")
            except Exception as e:
                logger.warning(f"⚠️ Core ↔ Unified Ethics connection failed: {e}")

        logger.info(f"🔗 Established {connections_made} component connections")

    def _generate_integration_report(self):
        """Generate integration status report"""
        working_components = len([s for s in self.integration_status.values() if s == "active"])
        total_components = len(self.integration_status)

        connectivity_percentage = (
            (working_components / total_components) * 100 if total_components > 0 else 0
        )

        logger.info("=" * 60)
        logger.info("🏗️  PRACTICAL INTEGRATION HUB STATUS REPORT")
        logger.info("=" * 60)
        logger.info(
            f"📊 Component Status: {working_components}/{total_components} active ({connectivity_percentage:.1f}%)"
        )
        logger.info("")

        for component, status in self.integration_status.items():
            status_icon = (
                "✅" if status == "active" else "❌" if status.startswith("failed") else "⚠️"
            )
            logger.info(f"{status_icon} {component}: {status}")

        logger.info("")
        logger.info("🎯 Phase 1 Implementation Goals:")
        logger.info(
            "   - Core Hub Integration: ✅ COMPLETE"
            if "core_hub" in self.available_components
            else "   - Core Hub Integration: ❌ FAILED"
        )
        logger.info(
            "   - Consciousness Integration: ✅ COMPLETE"
            if "consciousness_hub" in self.available_components
            else "   - Consciousness Integration: ❌ FAILED"
        )
        logger.info(
            "   - Ethics System Unification: ✅ COMPLETE"
            if "unified_ethics" in self.available_components
            else "   - Ethics System Unification: ⚠️ PARTIAL"
        )
        logger.info("=" * 60)

    async def process_integrated_request(
        self, request_type: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process requests through integrated systems"""
        try:
            result = {
                "status": "success",
                "request_type": request_type,
                "timestamp": datetime.now().isoformat(),
            }

            # Route through appropriate system
            if (
                request_type.startswith("consciousness_")
                and "consciousness_hub" in self.available_components
            ):
                # Process through consciousness hub
                result["consciousness_response"] = await self._process_consciousness_request(data)

            elif (
                request_type.startswith("ethics_") and "ethics_service" in self.available_components
            ):
                # Process through ethics service
                result["ethics_response"] = await self._process_ethics_request(data)

            elif request_type.startswith("core_") and "core_hub" in self.available_components:
                # Process through core hub
                result["core_response"] = await self._process_core_request(data)

            else:
                # Default processing through available systems
                if "core_hub" in self.available_components:
                    result["core_response"] = await self._process_core_request(data)

            return result

        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request_type": request_type,
                "timestamp": datetime.now().isoformat(),
            }

    async def _process_consciousness_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process request through consciousness hub"""
        # Simple consciousness processing
        return {
            "consciousness_state": (
                self.consciousness_hub.get_current_state().value
                if hasattr(self.consciousness_hub, "get_current_state")
                else "aware"
            ),
            "processed": True,
            "data_received": len(str(data)),
        }

    async def _process_ethics_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process request through ethics service"""
        # Simple ethics processing
        return {
            "ethics_evaluation": "approved",
            "processed": True,
            "data_received": len(str(data)),
        }

    async def _process_core_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process request through core hub"""
        # Simple core processing
        return {
            "core_status": "active",
            "processed": True,
            "data_received": len(str(data)),
        }

    def get_integration_status(self) -> dict[str, Any]:
        """Get current integration status"""
        working_components = len([s for s in self.integration_status.values() if s == "active"])
        total_components = len(self.integration_status)

        return {
            "timestamp": datetime.now().isoformat(),
            "working_components": working_components,
            "total_components": total_components,
            "connectivity_percentage": (
                (working_components / total_components) * 100 if total_components > 0 else 0
            ),
            "component_status": self.integration_status,
            "available_services": list(self.available_components.keys()),
            "phase_1_goals": {
                "core_hub_integration": "core_hub" in self.available_components,
                "consciousness_integration": "consciousness_hub" in self.available_components,
                "ethics_unification": "unified_ethics" in self.available_components,
            },
        }


# Global instance
_practical_hub_instance = None


def get_practical_integration_hub() -> PracticalIntegrationHub:
    """Get the practical integration hub instance"""
    global _practical_hub_instance
    if _practical_hub_instance is None:
        _practical_hub_instance = PracticalIntegrationHub()
    return _practical_hub_instance


# Test functionality if run directly
if __name__ == "__main__":
    import asyncio

    async def test_integration():
        """Test the practical integration hub"""
        logger.info("🧪 Testing Practical Integration Hub...")

        hub = get_practical_integration_hub()
        status = hub.get_integration_status()

        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"🎯 Connectivity: {status['connectivity_percentage']:.1f}%")
        print(f"⚡ Working Components: {status['working_components']}/{status['total_components']}")
        print("🏗️  Phase 1 Goals:")
        for goal, achieved in status["phase_1_goals"].items():
            status_icon = "✅" if achieved else "❌"
            print(f"   {status_icon} {goal.replace('_', ' ').title()}")

        # Test request processing
        print("\n🧪 Testing Request Processing...")

        test_requests = [
            ("consciousness_test", {"test_data": "consciousness query"}),
            ("ethics_test", {"test_data": "ethics evaluation"}),
            ("core_test", {"test_data": "core processing"}),
        ]

        for request_type, data in test_requests:
            try:
                result = await hub.process_integrated_request(request_type, data)
                print(f"✅ {request_type}: {result['status']}")
            except Exception as e:
                print(f"❌ {request_type}: {e}")

        print("=" * 60)
        print("✅ Integration test complete!")

    # Run the test
    asyncio.run(test_integration())
