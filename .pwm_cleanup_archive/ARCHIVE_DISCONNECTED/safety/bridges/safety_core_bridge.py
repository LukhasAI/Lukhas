"""
Safety-Core Bridge
Bidirectional communication bridge between Safety and Core systems
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SafetyCoreBridge:
    """
    Bridge for communication between Safety and Core systems.

    Provides:
    - Safety Policies ↔ Core Enforcement
    - Safety Monitoring ↔ Core Events
    - Safety Validation ↔ Core Operations
    - Safety Alerts ↔ Core Response
    - Safety Recovery ↔ Core Resilience
    """

    def __init__(self):
        self.safety_hub = None
        self.core_hub = None
        self.event_mappings = {}
        self.is_connected = False

        logger.info("Safety-Core Bridge initialized")

    async def connect(self) -> bool:
        """Establish connection between Safety and Core systems"""
        try:
            from safety.safety_hub import get_safety_hub

            from core.core_hub import get_core_hub

            self.safety_hub = get_safety_hub()
            self.core_hub = get_core_hub()

            self.setup_event_mappings()

            self.is_connected = True
            logger.info("Bridge connected between Safety and Core systems")
            return True

        except Exception as e:
            logger.error(f"Failed to connect Safety-Core bridge: {e}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # Safety -> Core events
            "safety_policy_update": "core_policy_enforcement",
            "safety_validation_request": "core_operation_validation",
            "safety_alert_triggered": "core_emergency_response",
            "safety_recovery_initiated": "core_resilience_activation",
            "safety_monitoring_active": "core_event_tracking",
            # Core -> Safety events
            "core_operation_request": "safety_validation_required",
            "core_event_occurred": "safety_monitoring_update",
            "core_anomaly_detected": "safety_alert_assessment",
            "core_failure_detected": "safety_recovery_required",
            "core_policy_violation": "safety_enforcement_needed",
        }

    async def safety_to_core(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forward event from Safety to Core system"""
        if not self.is_connected:
            await self.connect()

        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed_data = self.transform_data_safety_to_core(data)

            if self.core_hub:
                result = await self.core_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from Safety to Core")
                return result

            return {"error": "core hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Safety to Core: {e}")
            return {"error": str(e)}

    async def core_to_safety(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forward event from Core to Safety system"""
        if not self.is_connected:
            await self.connect()

        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed_data = self.transform_data_core_to_safety(data)

            if self.safety_hub:
                result = await self.safety_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from Core to Safety")
                return result

            return {"error": "safety hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Core to Safety: {e}")
            return {"error": str(e)}

    def transform_data_safety_to_core(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from Safety to Core"""
        return {
            "source_system": "safety",
            "target_system": "core",
            "data": data,
            "core_context": {
                "enforcement_level": data.get("enforcement_level", "standard"),
                "policy_type": data.get("policy_type", "general"),
                "priority": data.get("priority", "normal"),
            },
            "timestamp": self._get_timestamp(),
        }

    def transform_data_core_to_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from Core to Safety"""
        return {
            "source_system": "core",
            "target_system": "safety",
            "data": data,
            "safety_context": {
                "operation_type": data.get("operation_type", "general"),
                "risk_level": data.get("risk_level", "low"),
                "validation_required": data.get("validation_required", True),
            },
            "timestamp": self._get_timestamp(),
        }

    async def validate_core_operation(
        self, operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate core operation against safety policies"""
        safety_data = {
            "validation_type": "core_operation",
            "operation": operation_data,
            "required_checks": ["policy", "constraints", "risks"],
        }

        return await self.core_to_safety("core_operation_request", safety_data)

    async def enforce_safety_policy(
        self, policy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce safety policy in core system"""
        core_data = {
            "enforcement_type": "safety_policy",
            "policy": policy_data,
            "enforcement_mode": policy_data.get("mode", "strict"),
        }

        return await self.safety_to_core("safety_policy_update", core_data)

    async def handle_core_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle core anomaly with safety assessment"""
        safety_data = {
            "anomaly_type": "core_system",
            "anomaly_data": anomaly_data,
            "assessment_required": True,
            "auto_response": anomaly_data.get("severity", "low") == "critical",
        }

        return await self.core_to_safety("core_anomaly_detected", safety_data)

    async def initiate_safety_recovery(
        self, failure_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate safety recovery for core failure"""
        core_data = {
            "recovery_type": "safety_guided",
            "failure_info": failure_data,
            "recovery_strategy": failure_data.get("strategy", "graceful_degradation"),
        }

        return await self.safety_to_core("safety_recovery_initiated", core_data)

    async def sync_safety_core_policies(self) -> bool:
        """Synchronize safety policies with core enforcement"""
        try:
            # Get safety policies
            safety_policies = await self.get_safety_policies()

            # Get core enforcement status
            core_enforcement = await self.get_core_enforcement()

            # Cross-synchronize
            await self.safety_to_core(
                "safety_policy_sync",
                {"policies": safety_policies, "sync_type": "full_policy_update"},
            )

            await self.core_to_safety(
                "core_enforcement_sync",
                {
                    "enforcement_status": core_enforcement,
                    "sync_type": "policy_compliance_check",
                },
            )

            logger.debug("Safety-Core policy synchronization completed")
            return True

        except Exception as e:
            logger.error(f"Policy synchronization failed: {e}")
            return False

    async def get_safety_policies(self) -> Dict[str, Any]:
        """Get current safety policies"""
        if self.safety_hub:
            policy_manager = self.safety_hub.get_service("policy_manager")
            if policy_manager and hasattr(policy_manager, "get_all_policies"):
                return policy_manager.get_all_policies()

        return {"policies": [], "count": 0}

    async def get_core_enforcement(self) -> Dict[str, Any]:
        """Get core enforcement status"""
        if self.core_hub:
            enforcement = self.core_hub.get_service("policy_enforcement")
            if enforcement and hasattr(enforcement, "get_status"):
                return enforcement.get_status()

        return {"active_policies": 0, "enforcement_level": "standard"}

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the bridge"""
        return {
            "bridge_status": "healthy" if self.is_connected else "disconnected",
            "safety_hub_available": self.safety_hub is not None,
            "core_hub_available": self.core_hub is not None,
            "event_mappings": len(self.event_mappings),
            "timestamp": self._get_timestamp(),
        }


# Singleton instance
_safety_core_bridge_instance = None


def get_safety_core_bridge() -> SafetyCoreBridge:
    """Get or create the Safety-Core bridge instance"""
    global _safety_core_bridge_instance
    if _safety_core_bridge_instance is None:
        _safety_core_bridge_instance = SafetyCoreBridge()
    return _safety_core_bridge_instance
