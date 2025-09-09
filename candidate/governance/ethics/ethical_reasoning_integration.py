import logging

logger = logging.getLogger(__name__)
"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Ethical Reasoning System Integration Module
Provides integration wrapper for connecting the ethical reasoning system to the reasoning hub
"""

from typing import Any, Optional

from candidate.core.common import get_logger

from .ethical_reasoning_system import (
    EthicalConstraint,
    EthicalFramework,
    EthicalReasoningSystem,
    MoralJudgment,
    MoralPrinciple,
    StakeholderType,
    ValueAlignmentAssessment,
)

logger = get_logger(__name__)


class EthicalReasoningIntegration:
    """
    Integration wrapper for the Ethical Reasoning System.
    Provides a simplified interface for the reasoning hub.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the ethical reasoning integration"""
        self.config = config or {
            "enable_constraint_checking": True,
            "multi_framework_analysis": True,
            "value_alignment_active": True,
            "cultural_sensitivity": True,
        }

        # Initialize the ethical reasoning system
        self.ethical_system = EthicalReasoningSystem(self.config)
        self.is_initialized = False

        logger.info("EthicalReasoningIntegration initialized with config: %s", self.config)

    async def initialize(self):
        """Initialize the ethical reasoning system and its components"""
        if self.is_initialized:
            return

        try:
            # Perform any async initialization if needed
            logger.info("Initializing ethical reasoning system components...")

            # Load default ethical constraints
            await self._load_default_constraints()

            # Initialize value alignment baseline
            await self._initialize_value_alignment()

            self.is_initialized = True
            logger.info("Ethical reasoning system initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize ethical reasoning system: {e}")
            raise

    async def _load_default_constraints(self):
        """Load default ethical constraints"""
        # This would typically load from a configuration file or database
        default_constraints = [
            EthicalConstraint(
                constraint_id="harm_prevention_001",
                constraint_category="safety",
                constraint_description_text="Do not cause physical or psychological harm to humans",
                priority_level_code=1,
                is_hard_constraint=True,
                defined_enforcement_mechanism="decision_blocking",
                consequences_of_violation_summary=[
                    "Loss of trust",
                    "Potential legal liability",
                ],
                allowable_contextual_exceptions=["Self-defense of human life"],
                originating_stakeholder_type=StakeholderType.INDIVIDUAL_USER,
            ),
            EthicalConstraint(
                constraint_id="privacy_protection_001",
                constraint_category="privacy",
                constraint_description_text="Protect user privacy and personal data",
                priority_level_code=2,
                is_hard_constraint=True,
                defined_enforcement_mechanism="data_access_control",
                consequences_of_violation_summary=[
                    "Privacy breach",
                    "Regulatory violations",
                ],
                allowable_contextual_exceptions=[
                    "Legal warrant",
                    "User explicit consent",
                ],
                originating_stakeholder_type=StakeholderType.INDIVIDUAL_USER,
            ),
        ]

        for constraint in default_constraints:
            self.ethical_system.add_constraint(constraint)

    async def _initialize_value_alignment(self):
        """Initialize the value alignment system with baseline values"""
        baseline_values = {
            "human_wellbeing": 0.95,
            "truth_honesty": 0.90,
            "fairness": 0.85,
            "autonomy_respect": 0.85,
            "privacy": 0.80,
            "sustainability": 0.75,
        }

        # Set baseline values in the value alignment system
        self.ethical_system.value_alignment_system.set_target_values(baseline_values)

    async def evaluate_ethical_decision(self, question: str, context: dict[str, Any]) -> MoralJudgment:
        """
        Evaluate an ethical decision using the integrated system

        Args:
            question: The ethical question to evaluate
            context: Context information for the decision

        Returns:
            MoralJudgment with the system's ethical assessment
        """
        if not self.is_initialized:
            await self.initialize()

        # Ensure required context fields
        context.setdefault("proposed_action", "unspecified_action")
        context.setdefault("alternatives", [])
        context.setdefault("stakeholders", [StakeholderType.INDIVIDUAL_USER])
        context.setdefault("high_stakes", False)

        # Run the ethical analysis
        judgment = await self.ethical_system.analyze_ethical_decision(question, context)

        return judgment

    async def check_action_permissibility(self, action: str, maxim: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Quick check if an action is ethically permissible

        Args:
            action: The proposed action
            maxim: The maxim or principle behind the action
            context: Additional context

        Returns:
            Dict with permissibility verdict and confidence
        """
        if not self.is_initialized:
            await self.initialize()

        # Use deontological reasoning for quick permissibility check
        result = await self.ethical_system.deontological_reasoner.evaluate_action(action, context, maxim)

        return {
            "action": action,
            "permissible": result["verdict"] == "permissible",
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("evaluations", {}),
        }

    async def assess_value_alignment(self) -> ValueAlignmentAssessment:
        """
        Assess current value alignment of the system

        Returns:
            ValueAlignmentAssessment with current alignment metrics
        """
        if not self.is_initialized:
            await self.initialize()

        return await self.ethical_system.value_alignment_system.assess_current_alignment()

    async def get_ethical_constraints(self, category: Optional[str] = None) -> list[EthicalConstraint]:
        """
        Get active ethical constraints, optionally filtered by category

        Args:
            category: Optional category to filter constraints

        Returns:
            List of active ethical constraints
        """
        constraints = self.ethical_system.active_constraints

        if category:
            constraints = [c for c in constraints if c.constraint_category == category]

        return constraints

    def get_supported_frameworks(self) -> list[str]:
        """Get list of supported ethical frameworks"""
        return [framework.name for framework in EthicalFramework]

    def get_moral_principles(self) -> list[str]:
        """Get list of recognized moral principles"""
        return [principle.name for principle in MoralPrinciple]

    def get_stakeholder_types(self) -> list[str]:
        """Get list of stakeholder types"""
        return [stakeholder.name for stakeholder in StakeholderType]

    async def update_awareness(self, awareness_state: dict[str, Any]):
        """
        Update ethical reasoning with current awareness state
        Called by consciousness hub during awareness broadcasts
        """
        logger.debug(f"Ethical reasoning received awareness update: {awareness_state}")

        # Potentially adjust ethical sensitivity based on awareness level
        if awareness_state.get("level") == "active":
            # More rigorous ethical analysis during active awareness
            self.config["multi_framework_analysis"] = True
            self.config["cultural_sensitivity"] = True
        elif awareness_state.get("level") == "passive":
            # Faster, more heuristic ethical checks during passive awareness
            self.config["multi_framework_analysis"] = False


# Factory function for creating the integration
def create_ethical_reasoning_integration(
    config: Optional[dict[str, Any]] = None,
) -> EthicalReasoningIntegration:
    """Create and return an ethical reasoning integration instance"""
    return EthicalReasoningIntegration(config)