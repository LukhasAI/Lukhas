"""
VIVOX Ethics Bridge
Bridge SEEDRA/Guardian ethics with VIVOX.MAE
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional

# VIVOX imports
from ..moral_alignment.vivox_mae_core import ActionProposal, MAEDecision, VIVOXMoralAlignmentEngine
from datetime import timezone


@dataclass
class EthicalConstraint:
    """Unified ethical constraint format"""

    constraint_id: str
    constraint_type: str
    description: str
    weight: float
    source: str  # "seedra", "guardian", "vivox"
    active: bool = True


@dataclass
class UnifiedEthicalDecision:
    """Unified decision from multiple ethical systems"""

    approved: bool
    vivox_decision: Optional[MAEDecision]
    seedra_decision: Optional[dict[str, Any]]
    guardian_decision: Optional[dict[str, Any]]
    combined_confidence: float
    final_reasoning: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "vivox": self.vivox_decision.to_dict() if self.vivox_decision else None,
            "seedra": self.seedra_decision,
            "guardian": self.guardian_decision,
            "confidence": self.combined_confidence,
            "reasoning": self.final_reasoning,
        }


class VIVOXEthicsBridge:
    """
    Bridge SEEDRA/Guardian ethics with VIVOX.MAE
    """

    def __init__(self, vivox_mae: VIVOXMoralAlignmentEngine):
        self.vivox_mae = vivox_mae
        self.seedra_core = None
        self.guardian_system = None
        self.unified_constraints: list[EthicalConstraint] = []
        self.decision_callbacks: list[Callable] = []

    async def initialize_with_seedra(self, seedra_core: Any):
        """Initialize bridge with SEEDRA ethics system"""
        self.seedra_core = seedra_core
        await self.sync_ethical_frameworks()

    async def initialize_with_guardian(self, guardian_system: Any):
        """Initialize bridge with Guardian System"""
        self.guardian_system = guardian_system
        await self.sync_guardian_rules()

    async def sync_ethical_frameworks(self):
        """
        Synchronize SEEDRA ethics with VIVOX.MAE
        """
        if not self.seedra_core:
            return

        # Get SEEDRA ethical rules (placeholder - would use actual SEEDRA API)
        seedra_rules = await self._get_seedra_rules()

        for rule in seedra_rules:
            mae_constraint = await self._convert_to_mae_constraint(rule)
            self.unified_constraints.append(mae_constraint)

            # Update MAE's ethical principles
            await self._update_mae_principles(mae_constraint)

    async def sync_guardian_rules(self):
        """Synchronize Guardian System rules with VIVOX"""
        if not self.guardian_system:
            return

        # Get Guardian rules (placeholder)
        guardian_rules = await self._get_guardian_rules()

        for rule in guardian_rules:
            constraint = EthicalConstraint(
                constraint_id=f"guardian_{rule.get('id', 'unknown')}",
                constraint_type=rule.get("type", "general"),
                description=rule.get("description", ""),
                weight=rule.get("weight", 0.8),
                source="guardian",
            )
            self.unified_constraints.append(constraint)

    async def unified_ethical_evaluation(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> UnifiedEthicalDecision:
        """
        Evaluate action across all ethical systems
        """
        decisions = {}

        # VIVOX evaluation
        vivox_decision = await self.vivox_mae.evaluate_action_proposal(action, context)
        decisions["vivox"] = vivox_decision

        # SEEDRA evaluation (if available)
        if self.seedra_core:
            seedra_decision = await self._evaluate_with_seedra(action, context)
            decisions["seedra"] = seedra_decision

        # Guardian evaluation (if available)
        if self.guardian_system:
            guardian_decision = await self._evaluate_with_guardian(action, context)
            decisions["guardian"] = guardian_decision

        # Combine decisions
        unified_decision = await self._combine_ethical_decisions(decisions)

        # Notify callbacks
        await self._notify_decision_callbacks(unified_decision)

        return unified_decision

    async def _convert_to_mae_constraint(self, seedra_rule: dict[str, Any]) -> EthicalConstraint:
        """Convert SEEDRA rule to MAE constraint"""
        return EthicalConstraint(
            constraint_id=f"seedra_{seedra_rule.get('id', 'unknown')}",
            constraint_type=seedra_rule.get("category", "general"),
            description=seedra_rule.get("description", ""),
            weight=seedra_rule.get("severity", 0.5),
            source="seedra",
        )

    async def _update_mae_principles(self, constraint: EthicalConstraint):
        """Update MAE's ethical principles with new constraint"""
        # Map constraint type to MAE principle
        principle_mapping = {
            "harm_prevention": "harm_prevention",
            "autonomy": "autonomy_respect",
            "privacy": "privacy_protection",
            "fairness": "justice_fairness",
            "transparency": "truthfulness",
        }

        mae_principle = principle_mapping.get(constraint.constraint_type, "general")

        # Update weight in MAE if principle exists
        if hasattr(self.vivox_mae.dissonance_calculator, "ethical_principles"):
            if mae_principle in self.vivox_mae.dissonance_calculator.ethical_principles:
                # Blend weights
                current_weight = self.vivox_mae.dissonance_calculator.ethical_principles[mae_principle]
                new_weight = (current_weight + constraint.weight) / 2
                self.vivox_mae.dissonance_calculator.ethical_principles[mae_principle] = new_weight

    async def _get_seedra_rules(self) -> list[dict[str, Any]]:
        """Get ethical rules from SEEDRA (placeholder)"""
        # This would interface with actual SEEDRA system
        return [
            {
                "id": "seedra_001",
                "category": "harm_prevention",
                "description": "Prevent physical or psychological harm",
                "severity": 1.0,
            },
            {
                "id": "seedra_002",
                "category": "privacy",
                "description": "Protect user privacy and data",
                "severity": 0.9,
            },
        ]

    async def _get_guardian_rules(self) -> list[dict[str, Any]]:
        """Get rules from Guardian System (placeholder)"""
        return [
            {
                "id": "guardian_001",
                "type": "autonomy",
                "description": "Respect user autonomy and choice",
                "weight": 0.95,
            }
        ]

    async def _evaluate_with_seedra(self, action: ActionProposal, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate action with SEEDRA system"""
        # Placeholder for actual SEEDRA evaluation
        return {
            "approved": True,
            "confidence": 0.8,
            "reasoning": "SEEDRA evaluation placeholder",
        }

    async def _evaluate_with_guardian(self, action: ActionProposal, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate action with Guardian System"""
        # Placeholder for actual Guardian evaluation
        return {
            "approved": True,
            "confidence": 0.85,
            "reasoning": "Guardian evaluation placeholder",
        }

    async def _combine_ethical_decisions(self, decisions: dict[str, Any]) -> UnifiedEthicalDecision:
        """Combine decisions from multiple ethical systems"""
        # Extract individual decisions
        vivox_decision = decisions.get("vivox")
        seedra_decision = decisions.get("seedra")
        guardian_decision = decisions.get("guardian")

        # Calculate combined approval (unanimous required)
        approvals = []
        if vivox_decision:
            approvals.append(vivox_decision.approved)
        if seedra_decision:
            approvals.append(seedra_decision.get("approved", True))
        if guardian_decision:
            approvals.append(guardian_decision.get("approved", True))

        combined_approved = all(approvals) if approvals else False

        # Calculate combined confidence
        confidences = []
        if vivox_decision:
            confidences.append(vivox_decision.ethical_confidence)
        if seedra_decision:
            confidences.append(seedra_decision.get("confidence", 0.5))
        if guardian_decision:
            confidences.append(guardian_decision.get("confidence", 0.5))

        combined_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Generate combined reasoning
        reasoning_parts = []
        if vivox_decision and not vivox_decision.approved:
            reasoning_parts.append(f"VIVOX: {vivox_decision.suppression_reason}")
        if seedra_decision and not seedra_decision.get("approved", True):
            reasoning_parts.append(f"SEEDRA: {seedra_decision.get('reasoning', '')}")
        if guardian_decision and not guardian_decision.get("approved", True):
            reasoning_parts.append(f"Guardian: {guardian_decision.get('reasoning', '')}")

        final_reasoning = " | ".join(reasoning_parts) if reasoning_parts else "All systems approved"

        return UnifiedEthicalDecision(
            approved=combined_approved,
            vivox_decision=vivox_decision,
            seedra_decision=seedra_decision,
            guardian_decision=guardian_decision,
            combined_confidence=combined_confidence,
            final_reasoning=final_reasoning,
        )

    async def _notify_decision_callbacks(self, decision: UnifiedEthicalDecision):
        """Notify registered callbacks of ethical decision"""
        for callback in self.decision_callbacks:
            try:
                await callback(decision)
            except Exception as e:
                print(f"Error in decision callback: {e}")

    def register_decision_callback(self, callback: Callable):
        """Register callback for ethical decisions"""
        self.decision_callbacks.append(callback)

    async def add_custom_constraint(self, constraint: EthicalConstraint):
        """Add custom ethical constraint to all systems"""
        self.unified_constraints.append(constraint)

        # Update VIVOX MAE
        await self._update_mae_principles(constraint)

        # Update other systems if available
        if self.seedra_core:
            # Update SEEDRA (placeholder)
            pass

        if self.guardian_system:
            # Update Guardian (placeholder)
            pass

    async def get_ethical_state_summary(self) -> dict[str, Any]:
        """Get summary of current ethical state across systems"""
        summary = {
            "active_constraints": len(self.unified_constraints),
            "constraint_sources": {},
            "system_status": {
                "vivox": True,
                "seedra": self.seedra_core is not None,
                "guardian": self.guardian_system is not None,
            },
        }

        # Count constraints by source
        for constraint in self.unified_constraints:
            source = constraint.source
            if source not in summary["constraint_sources"]:
                summary["constraint_sources"][source] = 0
            summary["constraint_sources"][source] += 1

        # Get VIVOX state
        vivox_state = await self.vivox_mae.get_current_ethical_state()
        summary["vivox_state"] = vivox_state

        return summary

    async def ethical_drift_analysis(self) -> dict[str, Any]:
        """Analyze ethical drift across systems"""
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drift_indicators": [],
            "alignment_score": 1.0,
        }

        # Check for conflicting constraints
        constraint_groups = {}
        for constraint in self.unified_constraints:
            if constraint.constraint_type not in constraint_groups:
                constraint_groups[constraint.constraint_type] = []
            constraint_groups[constraint.constraint_type].append(constraint)

        # Look for weight disparities
        for constraint_type, constraints in constraint_groups.items():
            if len(constraints) > 1:
                weights = [c.weight for c in constraints]
                weight_variance = max(weights) - min(weights)

                if weight_variance > 0.3:
                    analysis["drift_indicators"].append(
                        {
                            "type": "weight_disparity",
                            "constraint_type": constraint_type,
                            "variance": weight_variance,
                            "sources": [c.source for c in constraints],
                        }
                    )
                    analysis["alignment_score"] *= 1 - weight_variance / 2

        return analysis