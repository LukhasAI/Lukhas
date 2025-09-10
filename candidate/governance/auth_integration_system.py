#!/usr/bin/env python3

"""
🌐 ΛiD Authentication Integration System
========================================

Complete Phase 7 integration system that brings together all ΛiD authentication
governance components with the LUKHAS AI ecosystem. This is the master integration
module that orchestrates Guardian System monitoring, GLYPH communication,
constitutional AI compliance, and Trinity Framework alignment.

This module provides:
- Complete ΛiD-LUKHAS integration orchestration
- Real-time ethical oversight and bias detection
- Constitutional AI compliance validation
- GLYPH-based symbolic communication
- Trinity Framework alignment
- Comprehensive audit trail integration
- Cross-module authentication context sharing

Author: LUKHAS AI System
Version: 1.0.0
Trinity Framework: ⚛️🧠🛡️
Phase: Phase 7 - Registry Updates and Policy Integration
"""

import asyncio
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from .auth_cross_module_integration import ModuleType, auth_cross_module_integrator
from .auth_glyph_registry import auth_glyph_registry
from .auth_governance_policies import auth_governance_policy_engine

# LUKHAS governance imports
from .auth_guardian_integration import AuthenticationGuardian, AuthEventType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationHealthStatus:
    """Health status of the integration system"""

    overall_status: str  # healthy, degraded, unhealthy
    guardian_status: str
    glyph_status: str
    policy_status: str
    cross_module_status: str
    compliance_score: float
    active_alerts: list[str]
    last_checked: datetime


@dataclass
class AuthIntegrationMetrics:
    """Comprehensive integration metrics"""

    total_authentications: int
    guardian_alerts: int
    policy_violations: int
    glyph_messages: int
    cross_module_communications: int
    constitutional_violations: int
    bias_detections: int
    drift_score_average: float
    compliance_rate: float
    integration_uptime: float
    last_updated: datetime


class LUKHASAuthIntegrationSystem:
    """
    🌐 Complete ΛiD-LUKHAS Authentication Integration System

    Master orchestrator for Phase 7 integration bringing together all
    authentication governance components with comprehensive ethical oversight.
    """

    def __init__(
        self,
        config: Optional[dict[str, Any]] = None,
        enable_guardian: bool = True,
        enable_glyph_registry: bool = True,
        enable_policies: bool = True,
        enable_cross_module: bool = True,
    ):
        """
        Initialize the complete authentication integration system

        Args:
            config: Integration configuration
            enable_guardian: Enable Guardian System integration
            enable_glyph_registry: Enable GLYPH registry integration
            enable_policies: Enable governance policies
            enable_cross_module: Enable cross-module communication
        """
        self.config = config or self._get_default_config()
        self.system_id = str(uuid.uuid4())
        self.startup_time = datetime.now(timezone.utc)

        # Integration components
        self.guardian_enabled = enable_guardian
        self.glyph_enabled = enable_glyph_registry
        self.policies_enabled = enable_policies
        self.cross_module_enabled = enable_cross_module

        # Initialize components
        self.guardian = (
            AuthenticationGuardian(
                drift_threshold=self.config.get("guardian", {}).get("drift_threshold", 0.15),
                enable_bias_detection=True,
                enable_constitutional_ai=True,
            )
            if enable_guardian
            else None
        )

        self.glyph_registry = auth_glyph_registry if enable_glyph_registry else None
        self.policy_engine = auth_governance_policy_engine if enable_policies else None
        self.cross_module_integrator = auth_cross_module_integrator if enable_cross_module else None

        # Integration state
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.integration_metrics = AuthIntegrationMetrics(
            total_authentications=0,
            guardian_alerts=0,
            policy_violations=0,
            glyph_messages=0,
            cross_module_communications=0,
            constitutional_violations=0,
            bias_detections=0,
            drift_score_average=0.0,
            compliance_rate=1.0,
            integration_uptime=0.0,
            last_updated=datetime.now(timezone.utc),
        )

        # Health monitoring
        self.health_status = IntegrationHealthStatus(
            overall_status="initializing",
            guardian_status="unknown",
            glyph_status="unknown",
            policy_status="unknown",
            cross_module_status="unknown",
            compliance_score=0.0,
            active_alerts=[],
            last_checked=datetime.now(timezone.utc),
        )

        # Alert thresholds
        self.alert_thresholds = {
            "drift_score": 0.15,
            "compliance_rate": 0.95,
            "constitutional_violations": 5,
            "bias_detections": 3,
            "policy_violations": 10,
        }

        logger.info(f"LUKHAS Authentication Integration System initialized: {self.system_id}")

    def _get_default_config(self) -> dict[str, Any]:
        """Get default integration configuration"""
        return {
            "guardian": {
                "drift_threshold": 0.15,
                "bias_detection": True,
                "constitutional_ai": True,
                "alert_on_violation": True,
            },
            "glyph_registry": {
                "jwt_encoding": True,
                "cross_module_communication": True,
                "symbolic_identity": True,
            },
            "policies": {
                "enforcement_level": "strict",
                "auto_remediation": True,
                "audit_violations": True,
            },
            "cross_module": {
                "propagate_context": True,
                "trinity_integration": True,
                "real_time_sync": True,
            },
            "monitoring": {
                "health_check_interval": 300,  # 5 minutes
                "metrics_update_interval": 60,  # 1 minute
                "alert_cooldown": 600,  # 10 minutes
            },
        }

    async def initialize(self) -> bool:
        """Initialize the integration system"""
        try:
            logger.info("Initializing LUKHAS Authentication Integration System...")

            # Initialize cross-module integration
            if self.cross_module_enabled and self.cross_module_integrator:
                # Register core authentication module
                await self.cross_module_integrator.register_module(
                    ModuleType.IDENTITY,
                    {"name": "lambda_auth", "version": "1.0.0"},
                    message_handler=self._handle_cross_module_message,
                )
                logger.info("Cross-module integration initialized")

            # Perform initial health check
            await self._update_health_status()

            # Start background monitoring
            asyncio.create_task(self._background_monitoring())

            self.health_status.overall_status = "healthy"
            logger.info(f"Integration system initialized successfully: {self.system_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize integration system: {e}")
            self.health_status.overall_status = "unhealthy"
            self.health_status.active_alerts.append(f"Initialization failed: {e!s}")
            return False

    async def process_authentication_event(
        self,
        user_id: str,
        event_type: str,
        auth_context: dict[str, Any],
        tier_level: str,
        outcome: str,
    ) -> dict[str, Any]:
        """
        Process authentication event through complete integration pipeline

        Args:
            user_id: User identifier
            event_type: Type of authentication event
            auth_context: Authentication context and metadata
            tier_level: User tier level (T1-T5)
            outcome: Event outcome (success/failure/denied)

        Returns:
            Complete integration result with all component outputs
        """
        try:
            integration_start = datetime.now(timezone.utc)
            result = {
                "user_id": user_id,
                "event_type": event_type,
                "tier_level": tier_level,
                "outcome": outcome,
                "timestamp": integration_start.isoformat(),
                "integration_id": str(uuid.uuid4()),
                "components": {},
                "alerts": [],
                "recommendations": [],
                "glyph_data": {},
                "cross_module_results": {},
                "overall_status": "processing",
            }

            # Convert event type to AuthEventType
            auth_event = self._convert_to_auth_event_type(event_type)

            # Phase 1: Guardian System Monitoring
            if self.guardian_enabled and self.guardian:
                guardian_result = await self.guardian.monitor_auth_event(
                    event_type=auth_event,
                    user_id=user_id,
                    tier_level=tier_level,
                    outcome=outcome,
                    context=auth_context,
                )

                result["components"]["guardian"] = guardian_result

                # Handle Guardian alerts
                if guardian_result.get("alert_triggered", False):
                    self.integration_metrics.guardian_alerts += 1
                    result["alerts"].append(
                        {
                            "type": "guardian_alert",
                            "message": "Guardian System detected ethical concern",
                            "drift_score": guardian_result.get("drift_score", 0.0),
                            "severity": ("high" if guardian_result.get("drift_score", 0.0) >= 0.8 else "medium"),
                        }
                    )

                # Track constitutional violations
                if not guardian_result.get("constitutional_valid", True):
                    self.integration_metrics.constitutional_violations += 1

                # Track bias detections
                if guardian_result.get("bias_flags"):
                    self.integration_metrics.bias_detections += 1

                result["recommendations"].extend(guardian_result.get("recommendations", []))

            # Phase 2: Policy Compliance Assessment
            if self.policies_enabled and self.policy_engine:
                # Enhance auth context with Guardian results
                enhanced_context = {**auth_context}
                if "guardian" in result["components"]:
                    enhanced_context.update(
                        {
                            "constitutional_valid": result["components"]["guardian"].get("constitutional_valid", True),
                            "bias_flags": result["components"]["guardian"].get("bias_flags", []),
                            "drift_score": result["components"]["guardian"].get("drift_score", 0.0),
                            "guardian_monitoring": True,
                        }
                    )

                policy_assessment = await self.policy_engine.assess_compliance(
                    auth_context=enhanced_context,
                    tier_level=tier_level,
                    include_recommendations=True,
                )

                result["components"]["policies"] = {
                    "compliant": policy_assessment.compliant,
                    "violations": len(policy_assessment.violations),
                    "risk_score": policy_assessment.risk_score,
                    "recommendations": policy_assessment.recommendations,
                }

                # Handle policy violations
                if not policy_assessment.compliant:
                    self.integration_metrics.policy_violations += len(policy_assessment.violations)
                    for violation in policy_assessment.violations:
                        result["alerts"].append(
                            {
                                "type": "policy_violation",
                                "message": f"Policy violation: {violation.violation_type}",
                                "severity": violation.severity.value,
                                "policy_id": violation.policy_rule_id,
                            }
                        )

                result["recommendations"].extend(policy_assessment.recommendations)

            # Phase 3: GLYPH Registry Integration
            if self.glyph_enabled and self.glyph_registry:
                # Create symbolic identity if needed
                access_context = {
                    "granted": outcome == "success",
                    "scopes": auth_context.get("scopes", []),
                    "constitutional_valid": result["components"].get("guardian", {}).get("constitutional_valid", True),
                    "requires_guardian_oversight": any(alert["type"] == "guardian_alert" for alert in result["alerts"]),
                }

                session_context = {
                    "active": outcome == "success",
                    "session_id": auth_context.get("session_id", str(uuid.uuid4())),
                    "consciousness_integration": auth_context.get("consciousness_integration", False),
                }

                symbolic_identity = self.glyph_registry.create_symbolic_identity(
                    user_id=user_id,
                    tier_level=tier_level,
                    access_context=access_context,
                    session_context=session_context,
                )

                # Encode JWT GLYPH claims
                glyph_claims = self.glyph_registry.encode_jwt_glyph_claims(
                    user_id=user_id,
                    tier_level=tier_level,
                    scopes=auth_context.get("scopes", []),
                    session_id=session_context["session_id"],
                    metadata={
                        "guardian_monitoring": "guardian" in result["components"],
                        "constitutional_valid": access_context["constitutional_valid"],
                        "drift_detected": result["components"].get("guardian", {}).get("drift_score", 0.0) >= 0.15,
                        "bias_detected": bool(result["components"].get("guardian", {}).get("bias_flags", [])),
                    },
                )

                result["components"]["glyph"] = {
                    "symbolic_identity": asdict(symbolic_identity),
                    "jwt_claims": glyph_claims,
                    "glyph_version": "1.0.0",
                }

                result["glyph_data"] = {
                    "composite_glyph": symbolic_identity.composite_glyph,
                    "trinity_glyph": symbolic_identity.trinity_glyph,
                    "jwt_glyph_identity": glyph_claims.get("glyph_identity"),
                }

                self.integration_metrics.glyph_messages += 1

            # Phase 4: Cross-Module Integration
            if self.cross_module_enabled and self.cross_module_integrator:
                # Prepare enhanced context for cross-module propagation
                cross_module_context = {
                    **auth_context,
                    "integration_results": result["components"],
                    "symbolic_identity": result["glyph_data"].get("composite_glyph"),
                    "constitutional_valid": result["components"].get("guardian", {}).get("constitutional_valid", True),
                    "guardian_monitoring": "guardian" in result["components"],
                    "policy_compliant": result["components"].get("policies", {}).get("compliant", True),
                    "tier_level": tier_level,
                    "outcome": outcome,
                }

                # Propagate to relevant modules based on event type and outcome
                target_modules = self._determine_target_modules(event_type, outcome, auth_context)

                propagation_results = await self.cross_module_integrator.propagate_auth_context(
                    user_id=user_id,
                    auth_event=auth_event,
                    auth_context=cross_module_context,
                    target_modules=target_modules,
                )

                result["components"]["cross_module"] = {
                    "target_modules": [m.value for m in target_modules],
                    "propagation_results": propagation_results,
                    "successful_propagations": sum(1 for success in propagation_results.values() if success),
                }

                result["cross_module_results"] = propagation_results
                self.integration_metrics.cross_module_communications += len(target_modules)

            # Phase 5: Session Management
            if outcome == "success":
                self.active_sessions[user_id] = {
                    "session_id": auth_context.get("session_id"),
                    "tier_level": tier_level,
                    "symbolic_identity": result["glyph_data"].get("composite_glyph"),
                    "start_time": integration_start,
                    "last_activity": integration_start,
                    "integration_results": result["components"],
                }
            elif outcome in ["failure", "logout", "expired"]:
                if user_id in self.active_sessions:
                    del self.active_sessions[user_id]

                # Clean up cross-module contexts
                if self.cross_module_enabled and self.cross_module_integrator:
                    await self.cross_module_integrator.cleanup_user_contexts(user_id)

            # Phase 6: Final Integration Assessment
            integration_duration = (datetime.now(timezone.utc) - integration_start).total_seconds()

            # Calculate overall status
            has_critical_alerts = any(alert.get("severity") == "critical" for alert in result["alerts"])
            has_high_alerts = any(alert.get("severity") == "high" for alert in result["alerts"])

            if has_critical_alerts:
                result["overall_status"] = "critical"
            elif has_high_alerts:
                result["overall_status"] = "alert"
            elif result["alerts"]:
                result["overall_status"] = "warning"
            else:
                result["overall_status"] = "success"

            # Update metrics
            self.integration_metrics.total_authentications += 1
            self._update_integration_metrics(result)

            # Add performance data
            result["performance"] = {
                "integration_duration_ms": round(integration_duration * 1000, 2),
                "components_processed": len(result["components"]),
                "alerts_generated": len(result["alerts"]),
                "recommendations_count": len(result["recommendations"]),
            }

            logger.info(f"Authentication event processed: {user_id} - {result['overall_status']}")

            return result

        except Exception as e:
            logger.error(f"Error processing authentication event: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "event_type": event_type,
                "overall_status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _convert_to_auth_event_type(self, event_type: str) -> AuthEventType:
        """Convert string event type to AuthEventType enum"""
        event_mapping = {
            "login_attempt": AuthEventType.LOGIN_ATTEMPT,
            "login_success": AuthEventType.LOGIN_SUCCESS,
            "login_failure": AuthEventType.LOGIN_FAILURE,
            "tier_assignment": AuthEventType.TIER_ASSIGNMENT,
            "scope_check": AuthEventType.SCOPE_CHECK,
            "session_create": AuthEventType.SESSION_CREATE,
            "session_terminate": AuthEventType.SESSION_TERMINATE,
            "bias_detection": AuthEventType.BIAS_DETECTION,
            "constitutional_violation": AuthEventType.CONSTITUTIONAL_VIOLATION,
        }

        return event_mapping.get(event_type, AuthEventType.LOGIN_ATTEMPT)

    def _determine_target_modules(
        self, event_type: str, outcome: str, auth_context: dict[str, Any]
    ) -> list[ModuleType]:
        """Determine target modules for cross-module propagation"""
        target_modules = []

        # Always include core modules for successful authentication
        if outcome == "success":
            target_modules.extend([ModuleType.CONSCIOUSNESS, ModuleType.MEMORY, ModuleType.GUARDIAN])

        # Include specific modules based on scopes
        scopes = auth_context.get("scopes", [])
        if any("matriz:" in scope for scope in scopes):
            target_modules.append(ModuleType.CREATIVITY)

        if any("consciousness:" in scope for scope in scopes):
            target_modules.append(ModuleType.REASONING)

        if any("memory:" in scope for scope in scopes):
            target_modules.append(ModuleType.MEMORY)

        if any("quantum:" in scope for scope in scopes):
            target_modules.append(ModuleType.QUANTUM)

        if any("bio:" in scope for scope in scopes):
            target_modules.append(ModuleType.BIO)

        # Include Guardian for security events
        if (
            event_type
            in [
                "constitutional_violation",
                "bias_detection",
                "login_failure",
            ]
            and ModuleType.GUARDIAN not in target_modules
        ):
            target_modules.append(ModuleType.GUARDIAN)

        # Remove duplicates while preserving order
        seen = set()
        unique_modules = []
        for module in target_modules:
            if module not in seen:
                seen.add(module)
                unique_modules.append(module)

        return unique_modules

    def _update_integration_metrics(self, result: dict[str, Any]) -> None:
        """Update integration metrics based on processing result"""
        # Update compliance rate
        total_auth = self.integration_metrics.total_authentications
        if total_auth > 0:
            violations = self.integration_metrics.policy_violations + self.integration_metrics.constitutional_violations
            self.integration_metrics.compliance_rate = max(0.0, 1.0 - (violations / total_auth))

        # Update average drift score
        if "guardian" in result.get("components", {}):
            drift_score = result["components"]["guardian"].get("drift_score", 0.0)
            current_avg = self.integration_metrics.drift_score_average
            self.integration_metrics.drift_score_average = (current_avg * (total_auth - 1) + drift_score) / total_auth

        # Update uptime
        uptime_seconds = (datetime.now(timezone.utc) - self.startup_time).total_seconds()
        self.integration_metrics.integration_uptime = uptime_seconds / 3600  # Convert to hours

        self.integration_metrics.last_updated = datetime.now(timezone.utc)

    async def _handle_cross_module_message(self, message: Any) -> None:
        """Handle incoming cross-module messages"""
        try:
            logger.info(f"Received cross-module message: {message}")
            # Process incoming messages from other modules
            # This could include feedback, status updates, or requests

        except Exception as e:
            logger.error(f"Error handling cross-module message: {e}")

    async def _background_monitoring(self) -> None:
        """Background monitoring and health checks"""
        try:
            while True:
                # Health status update
                await self._update_health_status()

                # Metrics update
                await self._update_metrics()

                # Alert processing
                await self._process_alerts()

                # Wait for next cycle
                await asyncio.sleep(self.config["monitoring"]["health_check_interval"])

        except Exception as e:
            logger.error(f"Background monitoring error: {e}")

    async def _update_health_status(self) -> None:
        """Update system health status"""
        try:
            # Check Guardian status
            if self.guardian_enabled and self.guardian:
                guardian_summary = self.guardian.get_drift_summary()
                self.health_status.guardian_status = guardian_summary.get("status", "unknown")
            else:
                self.health_status.guardian_status = "disabled"

            # Check GLYPH registry status
            if self.glyph_enabled and self.glyph_registry:
                glyph_stats = self.glyph_registry.get_registry_stats()
                self.health_status.glyph_status = "healthy" if glyph_stats["total_glyphs"] > 0 else "unhealthy"
            else:
                self.health_status.glyph_status = "disabled"

            # Check policy engine status
            if self.policies_enabled and self.policy_engine:
                policy_summary = self.policy_engine.get_violation_summary()
                violation_rate = policy_summary["total_violations"] / max(
                    1, self.integration_metrics.total_authentications
                )
                self.health_status.policy_status = "healthy" if violation_rate < 0.1 else "degraded"
            else:
                self.health_status.policy_status = "disabled"

            # Check cross-module integration status
            if self.cross_module_enabled and self.cross_module_integrator:
                integration_status = self.cross_module_integrator.get_integration_status()
                self.health_status.cross_module_status = integration_status.get("status", "unknown")
            else:
                self.health_status.cross_module_status = "disabled"

            # Calculate compliance score
            self.health_status.compliance_score = self.integration_metrics.compliance_rate

            # Determine overall status
            component_statuses = [
                self.health_status.guardian_status,
                self.health_status.glyph_status,
                self.health_status.policy_status,
                self.health_status.cross_module_status,
            ]

            enabled_statuses = [status for status in component_statuses if status != "disabled"]

            if any(status == "unhealthy" for status in enabled_statuses):
                self.health_status.overall_status = "unhealthy"
            elif any(status == "degraded" for status in enabled_statuses):
                self.health_status.overall_status = "degraded"
            else:
                self.health_status.overall_status = "healthy"

            self.health_status.last_checked = datetime.now(timezone.utc)

        except Exception as e:
            logger.error(f"Error updating health status: {e}")
            self.health_status.overall_status = "error"

    async def _update_metrics(self) -> None:
        """Update integration metrics"""
        # Metrics are updated in real-time during event processing
        pass

    async def _process_alerts(self) -> None:
        """Process and manage active alerts"""
        try:
            current_alerts = []

            # Check thresholds
            if self.integration_metrics.drift_score_average >= self.alert_thresholds["drift_score"]:
                current_alerts.append(f"High average drift score: {self.integration_metrics.drift_score_average:.3f}")

            if self.integration_metrics.compliance_rate < self.alert_thresholds["compliance_rate"]:
                current_alerts.append(f"Low compliance rate: {self.integration_metrics.compliance_rate:.3f}")

            if self.integration_metrics.constitutional_violations >= self.alert_thresholds["constitutional_violations"]:
                current_alerts.append(
                    f"High constitutional violations: {self.integration_metrics.constitutional_violations}"
                )

            if self.integration_metrics.bias_detections >= self.alert_thresholds["bias_detections"]:
                current_alerts.append(f"Multiple bias detections: {self.integration_metrics.bias_detections}")

            if self.integration_metrics.policy_violations >= self.alert_thresholds["policy_violations"]:
                current_alerts.append(f"High policy violations: {self.integration_metrics.policy_violations}")

            self.health_status.active_alerts = current_alerts

        except Exception as e:
            logger.error(f"Error processing alerts: {e}")

    async def get_integration_status(self) -> dict[str, Any]:
        """Get comprehensive integration system status"""
        return {
            "system_id": self.system_id,
            "startup_time": self.startup_time.isoformat(),
            "health_status": asdict(self.health_status),
            "metrics": asdict(self.integration_metrics),
            "active_sessions": len(self.active_sessions),
            "component_status": {
                "guardian_enabled": self.guardian_enabled,
                "glyph_enabled": self.glyph_enabled,
                "policies_enabled": self.policies_enabled,
                "cross_module_enabled": self.cross_module_enabled,
            },
            "configuration": self.config,
            "version": "1.0.0",
            "phase": "Phase 7 - Registry Updates and Policy Integration",
            "trinity_framework": "⚛️🧠🛡️",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    async def export_integration_report(
        self, include_sessions: bool = False, include_metrics: bool = True
    ) -> dict[str, Any]:
        """Export comprehensive integration report"""
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "system_status": await self.get_integration_status(),
            "summary": {
                "total_authentications": self.integration_metrics.total_authentications,
                "overall_health": self.health_status.overall_status,
                "compliance_rate": self.integration_metrics.compliance_rate,
                "average_drift_score": self.integration_metrics.drift_score_average,
                "active_alerts": len(self.health_status.active_alerts),
            },
        }

        if include_metrics:
            report["detailed_metrics"] = asdict(self.integration_metrics)

        if include_sessions:
            report["active_sessions"] = {
                user_id: {
                    **session_data,
                    "start_time": session_data["start_time"].isoformat(),
                    "last_activity": session_data["last_activity"].isoformat(),
                }
                for user_id, session_data in self.active_sessions.items()
            }

        # Component-specific reports
        if self.guardian and self.guardian_enabled:
            report["guardian_summary"] = self.guardian.get_drift_summary()

        if self.glyph_registry and self.glyph_enabled:
            report["glyph_registry_stats"] = self.glyph_registry.get_registry_stats()

        if self.policy_engine and self.policies_enabled:
            report["policy_violations_summary"] = self.policy_engine.get_violation_summary()

        if self.cross_module_integrator and self.cross_module_enabled:
            report["cross_module_status"] = self.cross_module_integrator.get_integration_status()

        return report

    async def cleanup(self) -> None:
        """Cleanup integration system resources"""
        try:
            # Clean up all active sessions
            for user_id in list(self.active_sessions.keys()):
                if self.cross_module_enabled and self.cross_module_integrator:
                    await self.cross_module_integrator.cleanup_user_contexts(user_id)

            self.active_sessions.clear()

            logger.info("Integration system cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global integration system instance
lukhas_auth_integration_system = LUKHASAuthIntegrationSystem()


# Export main class and instance
__all__ = [
    "AuthIntegrationMetrics",
    "IntegrationHealthStatus",
    "LUKHASAuthIntegrationSystem",
    "lukhas_auth_integration_system",
]
