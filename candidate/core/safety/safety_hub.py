"""
Safety Hub
Central coordination for AI safety subsystem components
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__, timezone)


class SafetyHub:
    """Central hub for AI safety system coordination"""

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list[callable]] = {}
        self.safety_policies: dict[str, Any] = {}
        self.is_initialized = False
        self._initialize_services()

        logger.info("Safety hub initialized")

    def _initialize_services(self):
        """Initialize all AI safety services"""
        # Core Safety Services
        self._register_core_safety_services()

        # Safety Testing & Validation
        self._register_testing_services()

        # Safety Monitoring & Prevention
        self._register_monitoring_services()

        # Safety Consensus & Governance
        self._register_consensus_services()

        # Initialize safety policies
        self._initialize_safety_policies()

        # Initialize safety bridges
        self._initialize_bridges()

        # Register services globally for cross-hub access
        self._register_with_service_discovery()

        # Mark as initialized
        self.is_initialized = True
        logger.info(f"Safety hub initialized with {len(self.services)} services")

    def _register_core_safety_services(self):
        """Register core AI safety services"""
        core_services = [
            ("ai_safety_orchestrator", "AISafetyOrchestrator"),
            ("constitutional_safety", "ConstitutionalSafety"),
            ("safety_coordinator", "SafetyCoordinator"),
            ("ethical_framework", "EthicalFramework"),
        ]

        for service_name, class_name in core_services:
            try:
                if service_name == "ai_safety_orchestrator":
                    module = __import__(
                        "core.safety.ai_safety_orchestrator",
                        fromlist=[class_name],
                    )
                elif service_name == "constitutional_safety":
                    module = __import__(
                        "core.safety.constitutional_safety",
                        fromlist=[class_name],
                    )
                else:
                    module = __import__(f"core.safety.{service_name}", fromlist=[class_name])

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_testing_services(self):
        """Register safety testing and validation services"""
        testing_services = [
            ("adversarial_testing", "AdversarialTesting"),
            ("safety_validator", "SafetyValidator"),
            ("harm_detector", "HarmDetector"),
            ("bias_detector", "BiasDetector"),
        ]

        for service_name, class_name in testing_services:
            try:
                if service_name == "adversarial_testing":
                    module = __import__(
                        "core.safety.adversarial_testing",
                        fromlist=[class_name],
                    )
                else:
                    module = __import__(f"core.safety.{service_name}", fromlist=[class_name])

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_monitoring_services(self):
        """Register safety monitoring and prevention services"""
        monitoring_services = [
            ("predictive_harm_prevention", "PredictiveHarmPrevention"),
            ("safety_monitor", "SafetyMonitor"),
            ("anomaly_detector", "SafetyAnomalyDetector"),
            ("risk_assessor", "RiskAssessor"),
        ]

        for service_name, class_name in monitoring_services:
            try:
                if service_name == "predictive_harm_prevention":
                    module = __import__(
                        "core.safety.predictive_harm_prevention",
                        fromlist=[class_name],
                    )
                else:
                    module = __import__(f"core.safety.{service_name}", fromlist=[class_name])

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_consensus_services(self):
        """Register safety consensus and governance services"""
        consensus_services = [
            ("multi_agent_consensus", "MultiAgentConsensus"),
            ("safety_governance", "SafetyGovernance"),
            ("ethics_committee", "EthicsCommittee"),
            ("safety_auditor", "SafetyAuditor"),
        ]

        for service_name, class_name in consensus_services:
            try:
                if service_name == "multi_agent_consensus":
                    module = __import__(
                        "core.safety.multi_agent_consensus",
                        fromlist=[class_name],
                    )
                else:
                    module = __import__(f"core.safety.{service_name}", fromlist=[class_name])

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _initialize_safety_policies(self):
        """Initialize core safety policies"""
        self.safety_policies = {
            "constitutional_ai": {
                "enabled": True,
                "principles": [
                    "Be helpful, harmless, and honest",
                    "Respect human autonomy and dignity",
                    "Avoid harmful or deceptive outputs",
                    "Protect privacy and confidentiality",
                ],
            },
            "harm_prevention": {
                "enabled": True,
                "severity_threshold": 0.7,
                "auto_block": True,
            },
            "bias_mitigation": {
                "enabled": True,
                "fairness_threshold": 0.8,
                "monitoring_active": True,
            },
            "consensus_requirements": {
                "critical_decisions": True,
                "min_consensus_score": 0.75,
                "timeout_seconds": 30,
            },
        }
        logger.debug("Safety policies initialized")

    def _initialize_bridges(self):
        """Initialize cross-system safety bridges"""
        bridges = [
            (
                "safety_quantum_bridge",
                "SafetyQIBridge",
                "safety.bridges.safety_quantum_bridge",
            ),
            (
                "safety_memory_bridge",
                "SafetyMemoryBridge",
                "safety.bridges.safety_memory_bridge",
            ),
            (
                "safety_core_bridge",
                "SafetyCoreBridge",
                "safety.bridges.safety_core_bridge",
            ),
        ]

        for bridge_name, class_name, module_path in bridges:
            try:
                module = __import__(module_path, fromlist=[f"get_{bridge_name}"])
                getter = getattr(module, f"get_{bridge_name}")
                bridge_instance = getter()
                self.register_service(bridge_name, bridge_instance)
                logger.debug(f"Registered {class_name} as {bridge_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_with_service_discovery(self):
        """Register services with global service discovery"""
        try:
            from candidate.core.integration.service_discovery import (
                get_service_discovery,
            )

            discovery = get_service_discovery()

            # Register key services globally for cross-hub access
            key_services = [
                "ai_safety_orchestrator",
                "constitutional_safety",
                "adversarial_testing",
                "predictive_harm_prevention",
                "multi_agent_consensus",
                "safety_coordinator",
                "safety_monitor",
                "harm_detector",
                "risk_assessor",
            ]

            for service_name in key_services:
                if service_name in self.services:
                    discovery.register_service_globally(service_name, self.services[service_name], "safety")

            logger.debug(f"Registered {len(key_services)} safety services with global discovery")
        except Exception as e:
            logger.warning(f"Could not register with service discovery: {e}")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered service '{name}' with safety hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered safety event handler for {event_type}")

    async def validate_action(
        self,
        action_type: str,
        action_data: dict[str, Any],
        user_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Validate an action through the safety system"""

        # Route through AI Safety Orchestrator if available
        orchestrator = self.get_service("ai_safety_orchestrator")
        if orchestrator and hasattr(orchestrator, "evaluate_action"):
            try:
                safety_decision = await orchestrator.evaluate_action(action_type, action_data, user_context or {})

                return {
                    "action_type": action_type,
                    "validation_result": safety_decision,
                    "validated_by": "ai_safety_orchestrator",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                logger.error(f"Safety orchestrator validation error: {e}")
                return {
                    "action_type": action_type,
                    "validation_result": {
                        "approved": False,
                        "reason": f"Safety validation error: {e}",
                    },
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        # Fallback safety validation
        return {
            "action_type": action_type,
            "validation_result": {
                "approved": True,
                "reason": "No safety orchestrator available",
            },
            "warning": "Safety validation not fully operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def process_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process an event through registered handlers with safety validation"""

        # Pre-validate the event for safety
        if event_type in [
            "system_action",
            "user_interaction",
            "data_processing",
        ]:
            validation_result = await self.validate_action(event_type, data)
            if not validation_result.get("validation_result", {}).get("approved", False):
                return {
                    "event_type": event_type,
                    "blocked": True,
                    "reason": "Safety validation failed",
                    "validation_details": validation_result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        # Process through registered handlers
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                result = await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                results.append({"source": "event_handler", "result": result})
            except Exception as e:
                logger.error(f"Safety handler error for {event_type}: {e}")
                results.append({"source": "event_handler", "error": str(e)})

        return {
            "event_type": event_type,
            "results": results,
            "safety_validated": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processed_by": "safety_hub",
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for all registered safety services"""
        health = {
            "status": "healthy",
            "services": {},
            "safety_policies": self.safety_policies,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hub": "safety",
        }

        for name, service in self.services.items():
            try:
                # Try to get service status if available
                if hasattr(service, "health_check"):
                    service_health = await service.health_check()
                    health["services"][name] = service_health
                elif hasattr(service, "status"):
                    health["services"][name] = {"status": service.status}
                else:
                    health["services"][name] = {"status": "active"}
            except Exception as e:
                health["services"][name] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"

        return health

    def get_safety_status(self) -> dict[str, Any]:
        """Get comprehensive safety system status"""
        safety_status = {
            "hub_services": len(self.services),
            "policies_active": len([p for p in self.safety_policies.values() if p.get("enabled", False)]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Get orchestrator status
        orchestrator = self.get_service("ai_safety_orchestrator")
        if orchestrator and hasattr(orchestrator, "get_safety_metrics"):
            try:
                safety_status["orchestrator_metrics"] = orchestrator.get_safety_metrics()
            except Exception as e:
                safety_status["orchestrator_error"] = str(e)

        return safety_status

    def get_service_list(self) -> list[str]:
        """Get list of all registered safety services"""
        return list(self.services.keys())

    def get_service_count(self) -> int:
        """Get count of registered safety services"""
        return len(self.services)


# Singleton instance
_safety_hub_instance = None


def get_safety_hub() -> SafetyHub:
    """Get or create the safety hub instance"""
    global _safety_hub_instance
    if _safety_hub_instance is None:
        _safety_hub_instance = SafetyHub()
    return _safety_hub_instance
