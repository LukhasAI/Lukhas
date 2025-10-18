"""
LUKHAS Ethics Service - Module API Interface

This service provides ethical assessment capabilities for the AGI system.
All operations are logged via ΛTRACE and respect user consent and tier access.

Key functions:
- assess_action: Evaluate if an action is ethically permissible
- check_compliance: Verify compliance with regulations
- evaluate_safety: Assess safety implications of decisions
- audit_decision: Log and audit ethical decisions

Integration with lukhas-id:
- All assessments require valid user identity
- Actions are logged for full audit trails
- Consent is checked for sensitive evaluations
"""

import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# Add parent directory to path for identity interface
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from governance.identity.interface import IdentityClient
except ImportError:
    # Fallback for development
    class IdentityClient:
        def verify_user_access(self, user_id: str, required_tier: str = "LAMBDA_TIER_1") -> bool:
            return True

        def check_consent(self, user_id: str, action: str) -> bool:
            return True

        def log_activity(self, activity_type: str, user_id: str, metadata: dict[str, Any]) -> None:
            print(f"ETHICS_LOG: {activity_type} by {user_id}: {metadata}")


class EthicsService:
    """
    Main ethics assessment service for the LUKHAS AGI system.

    Provides ethical evaluation capabilities with full integration to
    the identity system for access control and audit logging.
    """

    def __init__(self):
        """Initialize the ethics service with identity integration."""
        self.identity_client = IdentityClient()
        self.ethics_rules = self._load_ethics_rules()

    def assess_action(self, user_id: str, action: str, context: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
        """
        Assess whether a proposed action is ethically permissible.

        Args:
            user_id: The user requesting the assessment
            action: Description of the action to assess
            context: Additional context for the assessment

        Returns:
            Tuple[bool, str, Dict]: (is_permitted, reason, assessment_details)
        """
        # Verify user access
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_1"):
            return False, "Insufficient access for ethics assessment", {}

        # Check consent for ethics evaluation
        if not self.identity_client.check_consent(user_id, "ethics_assessment"):
            return False, "User consent required for ethics assessment", {}

        # Perform ethical assessment
        try:
            assessment = self._evaluate_action_ethics(action, context)

            # Log the assessment
            self.identity_client.log_activity(
                "ethics_assessment",
                user_id,
                {
                    "action": action,
                    "context": context,
                    "assessment": assessment,
                    "permitted": assessment.get("permitted", False),
                    "confidence": assessment.get("confidence", 0.0),
                },
            )

            return (
                assessment.get("permitted", False),
                assessment.get("reason", "Assessment completed"),
                assessment,
            )

        except Exception as e:
            error_msg = f"Ethics assessment error: {e!s}"
            self.identity_client.log_activity("ethics_error", user_id, {"action": action, "error": error_msg})
            return False, error_msg, {}

    def check_compliance(self, user_id: str, regulation: str, data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        """
        Check compliance with specific regulations (GDPR, AI Act, etc.).

        Args:
            user_id: The user requesting compliance check
            regulation: Name of regulation to check (e.g., "GDPR", "EU_AI_ACT")
            data: Data or action to check for compliance

        Returns:
            Tuple[bool, Dict]: (is_compliant, compliance_report)
        """
        # Verify user has sufficient tier for compliance checks
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
            return False, {"error": "Insufficient tier for compliance checking"}

        try:
            compliance_result = self._check_regulation_compliance(regulation, data)

            # Log compliance check
            self.identity_client.log_activity(
                "compliance_check",
                user_id,
                {
                    "regulation": regulation,
                    "compliant": compliance_result.get("compliant", False),
                    "violations": compliance_result.get("violations", []),
                    "recommendations": compliance_result.get("recommendations", []),
                },
            )

            return compliance_result.get("compliant", False), compliance_result

        except Exception as e:
            error_report = {"error": f"Compliance check failed: {e!s}"}
            self.identity_client.log_activity("compliance_error", user_id, {"regulation": regulation, "error": str(e)})
            return False, error_report

    def evaluate_safety(self, user_id: str, operation: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate safety implications of an operation.

        Args:
            user_id: The user requesting safety evaluation
            operation: The operation to evaluate
            parameters: Operation parameters

        Returns:
            Dict: Safety evaluation report
        """
        # Check user access and consent
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_1"):
            return {"safe": False, "reason": "Access denied"}

        if not self.identity_client.check_consent(user_id, "safety_evaluation"):
            return {"safe": False, "reason": "Consent required"}

        try:
            safety_assessment = self._assess_operation_safety(operation, parameters)

            # Log safety evaluation
            self.identity_client.log_activity(
                "safety_evaluation",
                user_id,
                {
                    "operation": operation,
                    "parameters": parameters,
                    "safety_score": safety_assessment.get("safety_score", 0.0),
                    "risks": safety_assessment.get("risks", []),
                    "safe": safety_assessment.get("safe", False),
                },
            )

            return safety_assessment

        except Exception as e:
            error_result = {"safe": False, "error": str(e)}
            self.identity_client.log_activity("safety_error", user_id, {"operation": operation, "error": str(e)})
            return error_result

    def audit_decision(self, user_id: str, decision: str, reasoning: str, context: dict[str, Any]) -> None:
        """
        Audit an ethical decision for transparency and accountability.

        Args:
            user_id: The user making the decision
            decision: The decision made
            reasoning: Ethical reasoning behind the decision
            context: Additional context
        """
        if self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_1"):
            self.identity_client.log_activity(
                "ethics_decision_audit",
                user_id,
                {
                    "decision": decision,
                    "reasoning": reasoning,
                    "context": context,
                    "audit_timestamp": datetime.now(timezone.utc).isoformat(),
                    "ethics_version": self._get_ethics_version(),
                },
            )

    def _load_ethics_rules(self) -> dict[str, Any]:
        """Load ethics rules and principles."""
        return {
            "core_principles": [
                "human_autonomy",
                "harm_prevention",
                "fairness",
                "transparency",
                "accountability",
            ],
            "prohibited_actions": [
                "privacy_violation",
                "manipulation",
                "discrimination",
                "harmful_content_generation",
            ],
            "consent_required": [
                "personal_data_processing",
                "creative_content_generation",
                "memory_access",
                "behavior_analysis",
            ],
        }

    def _evaluate_action_ethics(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Core ethics evaluation logic."""
        assessment = {
            "permitted": True,
            "confidence": 0.8,
            "reason": "Action appears ethically permissible",
            "concerns": [],
            "recommendations": [],
        }

        # Check against prohibited actions
        for prohibited in self.ethics_rules["prohibited_actions"]:
            if prohibited.lower() in action.lower():
                assessment.update(
                    {
                        "permitted": False,
                        "reason": f"Action involves prohibited activity: {prohibited}",
                        "confidence": 0.9,
                    }
                )
                break

        # Check for potential ethical concerns
        if "data" in action.lower() and "personal" in str(context).lower():
            assessment["concerns"].append("Personal data handling detected")
            assessment["recommendations"].append("Ensure proper consent and data protection")

        return assessment

    def _check_regulation_compliance(self, regulation: str, data: dict[str, Any]) -> dict[str, Any]:
        """Check compliance with specific regulations."""
        result = {
            "compliant": True,
            "regulation": regulation,
            "violations": [],
            "recommendations": [],
        }

        if regulation.upper() == "GDPR":
            # Basic GDPR compliance checks
            if "personal_data" in data and not data.get("consent_obtained", False):
                result["violations"].append("Personal data processing without explicit consent")
                result["compliant"] = False

            if not data.get("data_protection_measures", False):
                result["recommendations"].append("Implement data protection measures")

        elif regulation.upper() == "EU_AI_ACT":
            # Basic EU AI Act compliance checks
            if data.get("ai_system_risk", "").lower() in ["high", "critical"]:
                if not data.get("human_oversight", False):
                    result["violations"].append("High-risk AI system lacks human oversight")
                    result["compliant"] = False

        return result

    def _assess_operation_safety(self, operation: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Assess safety of an operation."""
        safety_score = 0.8  # Default safe score
        risks = []

        # Basic safety checks
        if "delete" in operation.lower() or "remove" in operation.lower():
            safety_score -= 0.2
            risks.append("Destructive operation detected")

        if "network" in operation.lower() or "external" in operation.lower():
            safety_score -= 0.1
            risks.append("External network access")

        return {
            "safe": safety_score > 0.5,
            "safety_score": safety_score,
            "risks": risks,
            "recommendations": ["Monitor operation closely"] if risks else [],
        }

    def _get_ethics_version(self) -> str:
        """Get current ethics framework version."""
        return "LUKHAS_ETHICS_v1.0"

    async def initialize_ethics_network(self) -> None:
        """Connect ethics to all decision-making systems"""
        try:
            # Store registered observers
            if not hasattr(self, "ethics_observers"):
                self.ethics_observers = {}

            # Store registered validators
            if not hasattr(self, "ethics_validators"):
                self.ethics_validators = {}

            # Setup decision intercept chain
            await self.setup_decision_intercept_chain()

            print("Ethics network initialized successfully")
        except Exception as e:
            print(f"Failed to initialize ethics network: {e}")

    async def register_observer(self, observer_id: str, callback: callable) -> None:
        """Register an ethics observer"""
        if not hasattr(self, "ethics_observers"):
            self.ethics_observers = {}

        self.ethics_observers[observer_id] = callback

        # Log registration
        self.identity_client.log_activity(
            "ethics_observer_registered",
            "system",
            {"observer_id": observer_id, "timestamp": datetime.now(timezone.utc).isoformat()},
        )

    async def register_privacy_handler(self, handler_id: str, handler: Any) -> None:
        """Register a privacy handler"""
        if not hasattr(self, "privacy_handlers"):
            self.privacy_handlers = {}

        self.privacy_handlers[handler_id] = handler

        # Log registration
        self.identity_client.log_activity(
            "privacy_handler_registered",
            "system",
            {"handler_id": handler_id, "timestamp": datetime.now(timezone.utc).isoformat()},
        )

    async def register_ethics_observer(self, observer: Any) -> None:
        """Register an ethics observer from another system"""
        if not hasattr(self, "system_observers"):
            self.system_observers = []

        self.system_observers.append(observer)

        # Log registration
        self.identity_client.log_activity(
            "system_observer_registered",
            "system",
            {
                "observer_type": type(observer).__name__,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def register_ethics_validator(self, validator: Any) -> None:
        """Register an ethics validator from another system"""
        if not hasattr(self, "ethics_validators"):
            self.ethics_validators = {}

        validator_id = f"validator_{len(self.ethics_validators)}"
        self.ethics_validators[validator_id] = validator

        # Log registration
        self.identity_client.log_activity(
            "ethics_validator_registered",
            "system",
            {"validator_id": validator_id, "timestamp": datetime.now(timezone.utc).isoformat()},
        )

    async def setup_decision_intercept_chain(self) -> None:
        """Setup decision intercept chain for ethics validation"""
        # In production, this would set up actual intercept chains
        # For now, we'll initialize the configuration
        self.decision_intercept_config = {
            "enabled": True,
            "intercept_points": ["pre_decision", "post_decision", "critical_action"],
            "validation_threshold": 0.8,
            "bypass_allowed": False,
        }

        # Log setup
        self.identity_client.log_activity(
            "decision_intercept_configured",
            "system",
            {
                "config": self.decision_intercept_config,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# Module API functions for easy import
def assess_action(
    user_id: str, action: str, context: Optional[dict[str, Any]] = None
) -> tuple[bool, str, dict[str, Any]]:
    """Simplified API for action assessment."""
    service = EthicsService()
    return service.assess_action(user_id, action, context or {})


def check_compliance(user_id: str, regulation: str, data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Simplified API for compliance checking."""
    service = EthicsService()
    return service.check_compliance(user_id, regulation, data)


def evaluate_safety(user_id: str, operation: str, parameters: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Simplified API for safety evaluation."""
    service = EthicsService()
    return service.evaluate_safety(user_id, operation, parameters or {})


if __name__ == "__main__":
    # Example usage
    ethics = EthicsService()

    test_user = "test_lambda_user_001"

    # Test action assessment
    permitted, reason, details = ethics.assess_action(
        test_user, "Generate creative content", {"type": "story", "audience": "general"}
    )
    print(f"Action assessment: {permitted} - {reason}")

    # Test compliance check
    compliant, report = ethics.check_compliance(test_user, "GDPR", {"personal_data": True, "consent_obtained": True})
    print(f"GDPR compliance: {compliant}")

    # Test safety evaluation
    safety = ethics.evaluate_safety(test_user, "memory_access", {"scope": "user_data", "purpose": "analysis"})
    print(f"Safety assessment: {safety.get('safe', False)}")
