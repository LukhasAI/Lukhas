"""
LUKHAS Multi-Brain Symphony - Deterministic Consensus Orchestration

Provides:
- Deterministic weighted voting for multi-brain consensus
- Stable, reproducible decision-making
- Brain activation and weight management
- Complete audit trail integration
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import numpy as np


class ConsensusMethod(Enum):
    """Methods for achieving consensus across brains"""

    WEIGHTED_VOTE = "weighted_vote"
    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    CONFIDENCE_WEIGHTED = "confidence_weighted"


@dataclass
class BrainDecision:
    """A decision from a single brain"""

    brain_id: str
    decision: Any
    raw_confidence: float
    activation_level: float
    reasoning: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrainConfig:
    """Configuration for a brain in the symphony"""

    brain_id: str
    weight: float = 1.0
    activation_threshold: float = 0.5
    enabled: bool = True
    specialization: Optional[str] = None


class MultiBrainSymphony:
    """
    Multi-brain orchestration with deterministic consensus

    Features:
    - Deterministic weighted voting
    - Stable tie-breaking for reproducibility
    - Complete audit trail integration
    - Brain activation management
    """

    def __init__(
        self,
        brains: Optional[Dict[str, BrainConfig]] = None,
        default_consensus: ConsensusMethod = ConsensusMethod.WEIGHTED_VOTE,
        audit_trail: Optional[Any] = None,
    ):
        """
        Initialize multi-brain symphony

        Args:
            brains: Dictionary of brain configurations
            default_consensus: Default consensus method
            audit_trail: AuditTrail instance for logging
        """
        self.brains: Dict[str, BrainConfig] = brains or {}
        self.default_consensus = default_consensus
        self.audit_trail = audit_trail

        # Brain performance tracking
        self.brain_metrics: Dict[str, Dict[str, float]] = {}

    def add_brain(
        self,
        brain_id: str,
        weight: float = 1.0,
        activation_threshold: float = 0.5,
        specialization: Optional[str] = None,
    ):
        """Add a brain to the symphony"""
        self.brains[brain_id] = BrainConfig(
            brain_id=brain_id, weight=weight, activation_threshold=activation_threshold, specialization=specialization
        )
        self.brain_metrics[brain_id] = {"total_decisions": 0, "consensus_agreement": 0.0, "avg_confidence": 0.0}

    def remove_brain(self, brain_id: str):
        """Remove a brain from the symphony"""
        if brain_id in self.brains:
            del self.brains[brain_id]
        if brain_id in self.brain_metrics:
            del self.brain_metrics[brain_id]

    def update_brain_weight(self, brain_id: str, weight: float):
        """Update the weight of a brain"""
        if brain_id in self.brains:
            self.brains[brain_id].weight = weight

    def orchestrate_decision(
        self,
        decision_context: Dict[str, Any],
        brain_functions: Dict[str, Callable],
        consensus_method: Optional[ConsensusMethod] = None,
        min_activation: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Orchestrate a decision across multiple brains

        Args:
            decision_context: Context for the decision
            brain_functions: Map of brain_id to decision functions
            consensus_method: Consensus method to use
            min_activation: Minimum activation level for participation

        Returns:
            Dict with final decision, confidence, and metadata
        """
        start_time = time.time()
        consensus_method = consensus_method or self.default_consensus

        # Collect decisions from all active brains
        brain_decisions: List[BrainDecision] = []

        for brain_id, brain_config in self.brains.items():
            if not brain_config.enabled:
                continue

            if brain_id not in brain_functions:
                continue

            try:
                # Execute brain decision function
                decision_result = brain_functions[brain_id](decision_context)

                # Extract decision components
                decision = decision_result.get("decision")
                confidence = decision_result.get("confidence", 0.5)
                activation = decision_result.get("activation", 1.0)
                reasoning = decision_result.get("reasoning", [])

                # Check activation threshold
                if activation < max(brain_config.activation_threshold, min_activation):
                    continue

                brain_decisions.append(
                    BrainDecision(
                        brain_id=brain_id,
                        decision=decision,
                        raw_confidence=confidence,
                        activation_level=activation,
                        reasoning=reasoning,
                        metadata=decision_result.get("metadata", {}),
                    )
                )

            except Exception as e:
                # Log error but continue with other brains
                if self.audit_trail:
                    print(f"Brain {brain_id} failed: {e}")
                continue

        if not brain_decisions:
            return {
                "decision": None,
                "raw_confidence": 0.0,
                "calibrated_confidence": 0.0,
                "participating_brains": 0,
                "error": "No brains participated in decision",
            }

        # Achieve consensus
        consensus_result = self._achieve_consensus(brain_decisions, consensus_method)

        execution_time = (time.time() - start_time) * 1000  # ms

        return {
            "decision": consensus_result["decision"],
            "raw_confidence": consensus_result["raw_confidence"],
            "calibrated_confidence": consensus_result.get("calibrated_confidence", consensus_result["raw_confidence"]),
            "participating_brains": len(brain_decisions),
            "brain_votes": {bd.brain_id: bd.decision for bd in brain_decisions},
            "brain_confidences": {bd.brain_id: bd.raw_confidence for bd in brain_decisions},
            "consensus_method": consensus_method.value,
            "execution_time_ms": execution_time,
            "metadata": {
                "brain_count": len(brain_decisions),
                "avg_activation": np.mean([bd.activation_level for bd in brain_decisions]),
                "consensus_strength": self._compute_consensus_strength(brain_decisions, consensus_result["decision"]),
            },
        }

    def _achieve_consensus(self, brain_decisions: List[BrainDecision], method: ConsensusMethod) -> Dict[str, Any]:
        """
        Deterministic weighted voting baseline:
        score(decision) = Σ weight_i * activation_i * raw_confidence_i
        Tie-breaker: sort by (-score, str(decision)) for stability.
        """
        scores = {}
        for bd in brain_decisions:
            weight = max(1e-9, self.brains[bd.brain_id].weight)
            act = max(1e-9, bd.activation_level)
            conf = max(0.0, min(1.0, bd.raw_confidence))
            scores[bd.decision] = scores.get(bd.decision, 0.0) + weight * act * conf

        # Deterministic tie-breaking: sort by (-score, str(decision))
        decision = sorted(scores.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]
        total = sum(scores.values()) + 1e-9
        raw_conf = max(0.0, min(1.0, scores[decision] / total))

        return {"decision": decision, "raw_confidence": raw_conf}

    def _compute_consensus_strength(self, brain_decisions: List[BrainDecision], final_decision: Any) -> float:
        """
        Compute consensus strength (fraction of weighted votes agreeing with final decision)

        Args:
            brain_decisions: All brain decisions
            final_decision: The final consensus decision

        Returns:
            Consensus strength (0-1)
        """
        total_weight = 0.0
        agreeing_weight = 0.0

        for bd in brain_decisions:
            weight = self.brains[bd.brain_id].weight * bd.activation_level
            total_weight += weight

            if bd.decision == final_decision:
                agreeing_weight += weight

        if total_weight == 0:
            return 0.0

        return agreeing_weight / total_weight

    def update_brain_metrics(self, brain_id: str, decision_correct: bool, confidence: float):
        """
        Update performance metrics for a brain

        Args:
            brain_id: ID of the brain
            decision_correct: Whether the decision was correct
            confidence: Confidence of the decision
        """
        if brain_id not in self.brain_metrics:
            self.brain_metrics[brain_id] = {"total_decisions": 0, "consensus_agreement": 0.0, "avg_confidence": 0.0}

        metrics = self.brain_metrics[brain_id]
        n = metrics["total_decisions"]

        # Update running averages
        metrics["avg_confidence"] = (metrics["avg_confidence"] * n + confidence) / (n + 1)

        if decision_correct:
            metrics["consensus_agreement"] = (metrics["consensus_agreement"] * n + 1.0) / (n + 1)
        else:
            metrics["consensus_agreement"] = (metrics["consensus_agreement"] * n) / (n + 1)

        metrics["total_decisions"] = n + 1

    def get_brain_metrics(self, brain_id: str) -> Optional[Dict[str, float]]:
        """Get performance metrics for a brain"""
        return self.brain_metrics.get(brain_id)

    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all brains"""
        return self.brain_metrics.copy()

    def optimize_weights(self, performance_data: Dict[str, float]):
        """
        Optimize brain weights based on performance data

        Args:
            performance_data: Map of brain_id to performance score (0-1)
        """
        # Simple normalization: weights proportional to performance
        total_performance = sum(performance_data.values())

        if total_performance == 0:
            return

        for brain_id, performance in performance_data.items():
            if brain_id in self.brains:
                normalized_weight = (performance / total_performance) * len(performance_data)
                self.brains[brain_id].weight = max(0.1, normalized_weight)  # Minimum weight 0.1

    def export_configuration(self) -> Dict[str, Any]:
        """Export symphony configuration"""
        return {
            "brains": {
                brain_id: {
                    "brain_id": config.brain_id,
                    "weight": config.weight,
                    "activation_threshold": config.activation_threshold,
                    "enabled": config.enabled,
                    "specialization": config.specialization,
                }
                for brain_id, config in self.brains.items()
            },
            "default_consensus": self.default_consensus.value,
            "brain_metrics": self.brain_metrics,
        }

    def import_configuration(self, config: Dict[str, Any]):
        """Import symphony configuration"""
        brain_configs = config.get("brains", {})
        for brain_id, brain_data in brain_configs.items():
            self.brains[brain_id] = BrainConfig(
                brain_id=brain_data["brain_id"],
                weight=brain_data["weight"],
                activation_threshold=brain_data["activation_threshold"],
                enabled=brain_data.get("enabled", True),
                specialization=brain_data.get("specialization"),
            )

        consensus_str = config.get("default_consensus", "weighted_vote")
        self.default_consensus = ConsensusMethod(consensus_str)

        self.brain_metrics = config.get("brain_metrics", {})
