#!/usr/bin/env python3
"""
Ethics System Integration Module
Unifies all ethics components into a cohesive system with synchronized decision-making.

This module connects:
- MEG (Meta-Ethics Governor) - High-level ethical oversight
- SRD (Self-Reflective Debugger) - Ethical introspection and debugging
- HITLO (Human-in-the-Loop) - Human oversight for critical decisions
- SEEDRA - Consent and data management framework
- DAO Controller - Decentralized governance
- Compliance Engine - Regulatory compliance
- Sentinel - Drift detection and monitoring
- Security engines - Security-aware ethical decisions
"""

from datetime import datetime
from enum import Enum
from typing import Any

# Import for synchronization
from bio.core.symbolic_mito_ethics_sync import MitoEthicsSync
from core.common import get_logger
from ethics.compliance.engine import ComplianceEngine
from ethics.governor.dao_controller import DAOController
from ethics.governor.lambda_governor import LambdaGovernor
from ethics.hitlo_bridge import HITLOBridge
from ethics.meg_guard import MEGGuard

# Import all ethics components
from ethics.meta_ethics_governor import MetaEthicsGovernor
from ethics.security.main_node_security_engine import MainNodeSecurityEngine
from ethics.seedra.seedra_core import SEEDRACore
from ethics.self_reflective_debugger import (
    EnhancedSelfReflectiveDebugger as SelfReflectiveDebugger,
)
from ethics.sentinel.ethical_drift_sentinel import EthicalDriftSentinel
from ethics.service import EthicsService
from ethics.stabilization.tuner import StabilizationTuner

logger = get_logger(__name__)


class EthicalDecisionType(Enum):
    """Types of ethical decisions"""

    ROUTINE = "routine"  # Standard operations
    ELEVATED = "elevated"  # Requires additional oversight
    CRITICAL = "critical"  # Requires human-in-the-loop
    EMERGENCY = "emergency"  # Immediate action needed


class EthicsIntegration:
    """
    Unified ethics system that coordinates all ethical components.
    Provides synchronized ethical decision-making across the LUKHAS system.
    """

    def __init__(self):
        logger.info("Initializing Ethics Integration System...")

        # Core ethics components
        self.meg = MetaEthicsGovernor()
        self.srd = SelfReflectiveDebugger()
        self.hitlo = HITLOBridge()
        self.seedra = SEEDRACore()

        # Governance components
        self.dao = DAOController()
        self.lambda_governor = LambdaGovernor()
        self.meg_guard = MEGGuard()

        # Compliance and monitoring
        self.compliance_engine = ComplianceEngine()
        self.drift_sentinel = EthicalDriftSentinel()
        self.security_engine = MainNodeSecurityEngine()
        self.stabilization_tuner = StabilizationTuner()

        # Main service interface
        self.ethics_service = EthicsService()

        # Synchronization system
        self.sync_system = MitoEthicsSync(base_frequency=0.5)  # Ethics decisions at 0.5Hz

        # Decision tracking
        self.decision_history: list[dict[str, Any]] = []
        self.active_decisions: dict[str, dict[str, Any]] = {}

        # Initialize connections
        self._establish_connections()

    def _establish_connections(self):
        """Establish connections between all ethics components"""
        logger.info("Connecting ethics components...")

        # MEG oversees all components
        self.meg.register_component("srd", self.srd)
        self.meg.register_component("hitlo", self.hitlo)
        self.meg.register_component("dao", self.dao)
        self.meg.register_component("compliance", self.compliance_engine)

        # SRD monitors all decisions
        self.srd.register_monitor("meg", self.meg)
        self.srd.register_monitor("compliance", self.compliance_engine)
        self.srd.register_monitor("security", self.security_engine)

        # SEEDRA manages consent for all
        self.seedra.register_system("meg", self.meg)
        self.seedra.register_system("dao", self.dao)
        self.seedra.register_system("compliance", self.compliance_engine)

        # MEG Guard protects critical paths
        self.meg_guard.register_protected_system("dao", self.dao)
        self.meg_guard.register_protected_system("hitlo", self.hitlo)

        # Drift sentinel monitors all
        self.drift_sentinel.register_monitoring_target("meg", self.meg)
        self.drift_sentinel.register_monitoring_target("compliance", self.compliance_engine)

        logger.info("Ethics components connected successfully")

    async def evaluate_action(
        self,
        agent_id: str,
        action: str,
        context: dict[str, Any],
        urgency: str = "normal",
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Evaluate an action through the unified ethics system.

        Returns:
            Tuple of (is_permitted, reason, detailed_analysis)
        """
        decision_id = f"{agent_id}_{datetime.now().timestamp()}"
        start_time = datetime.now()

        # Update synchronization
        current_time = start_time.timestamp()
        self.sync_system.update_phase("ethics_evaluation", current_time)

        # Determine decision type based on context
        decision_type = self._determine_decision_type(action, context, urgency)

        # Track active decision
        self.active_decisions[decision_id] = {
            "agent_id": agent_id,
            "action": action,
            "context": context,
            "decision_type": decision_type,
            "start_time": start_time,
        }

        try:
            # 1. Check SEEDRA consent
            consent_check = await self.seedra.check_consent(agent_id, action)
            if not consent_check["has_consent"]:
                return (
                    False,
                    "No consent for action",
                    {"consent_details": consent_check},
                )

            # 2. Security pre-check
            security_check = await self.security_engine.validate_action(action, context)
            if security_check.get("threat_level", 0) > 0.7:
                return (
                    False,
                    "Security threat detected",
                    {"security_details": security_check},
                )

            # 3. Compliance check
            compliance_result = await self.compliance_engine.check_compliance(action, context)
            if not compliance_result.get("compliant", False):
                return (
                    False,
                    "Non-compliant action",
                    {"compliance_details": compliance_result},
                )

            # 4. Main ethical evaluation based on decision type
            if decision_type == EthicalDecisionType.CRITICAL:
                # Route through HITLO for human oversight
                result = await self._evaluate_critical_decision(agent_id, action, context)
            elif decision_type == EthicalDecisionType.ELEVATED:
                # Route through MEG with DAO consultation
                result = await self._evaluate_elevated_decision(agent_id, action, context)
            else:
                # Standard evaluation through MEG
                result = await self._evaluate_routine_decision(agent_id, action, context)

            # 5. SRD reflection and validation
            reflection = await self.srd.reflect_on_decision(decision_id, result)
            if reflection.get("concerns", []):
                logger.warning(f"SRD raised concerns: {reflection['concerns']}")

            # 6. Drift detection
            drift_check = await self.drift_sentinel.check_decision_drift(result, self.decision_history[-10:])
            if drift_check.get("drift_detected", False):
                await self.stabilization_tuner.stabilize_ethics_drift(drift_check)

            # Record decision
            self._record_decision(decision_id, result)

            return result["permitted"], result["reason"], result

        except Exception as e:
            logger.error(f"Ethics evaluation error: {e}")
            return False, f"Evaluation error: {e!s}", {"error": str(e)}

        finally:
            # Clean up active decision
            if decision_id in self.active_decisions:
                del self.active_decisions[decision_id]

    def _determine_decision_type(self, action: str, context: dict[str, Any], urgency: str) -> EthicalDecisionType:
        """Determine the type of ethical decision required"""
        # Critical decisions that affect users or system integrity
        critical_keywords = [
            "delete",
            "modify_identity",
            "access_private",
            "shutdown",
            "override",
        ]
        if any(keyword in action.lower() for keyword in critical_keywords):
            return EthicalDecisionType.CRITICAL

        # Elevated decisions that need additional oversight
        elevated_keywords = ["create", "update", "share", "publish", "authorize"]
        if any(keyword in action.lower() for keyword in elevated_keywords):
            return EthicalDecisionType.ELEVATED

        # Emergency decisions
        if urgency == "emergency":
            return EthicalDecisionType.EMERGENCY

        return EthicalDecisionType.ROUTINE

    async def _evaluate_routine_decision(self, agent_id: str, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate routine decisions through standard MEG process"""
        # MEG evaluation
        meg_result = await self.meg.evaluate_action(action, context)

        # Quick compliance check
        compliance_ok = await self.compliance_engine.quick_check(action)

        return {
            "permitted": meg_result["permitted"] and compliance_ok,
            "reason": meg_result.get("reason", "Routine evaluation complete"),
            "meg_analysis": meg_result,
            "decision_type": "routine",
        }

    async def _evaluate_elevated_decision(self, agent_id: str, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate elevated decisions with DAO consultation"""
        # MEG evaluation
        meg_result = await self.meg.evaluate_action(action, context)

        # DAO consultation
        dao_vote = await self.dao.request_vote(action, context)

        # Lambda governor oversight
        governor_decision = await self.lambda_governor.oversee_decision(meg_result, dao_vote)

        return {
            "permitted": governor_decision["approved"],
            "reason": governor_decision.get("reason", "Elevated evaluation complete"),
            "meg_analysis": meg_result,
            "dao_vote": dao_vote,
            "governor_decision": governor_decision,
            "decision_type": "elevated",
        }

    async def _evaluate_critical_decision(self, agent_id: str, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate critical decisions requiring human oversight"""
        # MEG evaluation first
        meg_result = await self.meg.evaluate_action(action, context)

        # If MEG denies, no need for HITLO
        if not meg_result.get("permitted", False):
            return {
                "permitted": False,
                "reason": "Denied by MEG before HITLO review",
                "meg_analysis": meg_result,
                "decision_type": "critical",
            }

        # HITLO review required
        hitlo_result = await self.hitlo.request_human_review(
            {
                "agent_id": agent_id,
                "action": action,
                "context": context,
                "meg_analysis": meg_result,
            }
        )

        # MEG Guard final protection
        final_decision = await self.meg_guard.validate_critical_decision(hitlo_result)

        return {
            "permitted": final_decision["approved"],
            "reason": final_decision.get("reason", "Critical evaluation complete"),
            "meg_analysis": meg_result,
            "hitlo_review": hitlo_result,
            "meg_guard_validation": final_decision,
            "decision_type": "critical",
        }

    def _record_decision(self, decision_id: str, result: dict[str, Any]):
        """Record decision in history"""
        decision_record = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "phase": self.sync_system.last_phases.get("ethics_evaluation", 0),
        }

        self.decision_history.append(decision_record)

        # Keep only last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]

    async def get_ethics_status(self) -> dict[str, Any]:
        """Get current status of the ethics system"""
        # Check phase alignment of all components
        components = ["meg", "srd", "hitlo", "compliance", "dao"]
        current_time = datetime.now().timestamp()

        for component in components:
            self.sync_system.update_phase(component, current_time)

        alignment_scores = self.sync_system.assess_alignment("meg", components[1:])
        is_synchronized = self.sync_system.is_synchronized(alignment_scores)

        return {
            "is_synchronized": is_synchronized,
            "alignment_scores": alignment_scores,
            "active_decisions": len(self.active_decisions),
            "decision_history_size": len(self.decision_history),
            "components_status": {
                "meg": "active",
                "srd": "active",
                "hitlo": "active",
                "seedra": "active",
                "compliance": "active",
                "drift_sentinel": "monitoring",
            },
        }


# Singleton pattern
_ethics_integration_instance = None


def get_ethics_integration() -> EthicsIntegration:
    """Get or create the global ethics integration instance"""
    global _ethics_integration_instance
    if _ethics_integration_instance is None:
        _ethics_integration_instance = EthicsIntegration()
    return _ethics_integration_instance
