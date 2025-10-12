"""
🎯 Advanced Confidence Calibration System
Revolutionary confidence calibration for AI abstract reasoning

This module implements the advanced confidence calibration system described in
abstract_resoaning.md, providing sophisticated uncertainty quantification and
meta-learning capabilities for reasoning confidence assessment.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

logger = logging.getLogger("ConfidenceCalibration")


class UncertaintyType(Enum):
    """Types of uncertainty in reasoning"""

    ALEATORY = "aleatory"  # Inherent randomness
    EPISTEMIC = "epistemic"  # Knowledge gaps
    LINGUISTIC = "linguistic"  # Language ambiguity
    TEMPORAL = "temporal"  # Time-dependent uncertainty
    QUANTUM = "quantum"  # Quantum indeterminacy


@dataclass
class ConfidenceMetrics:
    """Comprehensive confidence metrics"""

    bayesian_confidence: float
    qi_confidence: float
    symbolic_confidence: float
    emotional_confidence: float
    cross_brain_coherence: float
    uncertainty_decomposition: dict[str, float]
    meta_confidence: float
    calibration_score: float


@dataclass
class CalibrationRecord:
    """Record of confidence calibration for meta-learning"""

    prediction_confidence: float
    actual_outcome: bool
    reasoning_complexity: float
    brain_coherence: float
    uncertainty_types: list[str]
    timestamp: datetime
    context_features: dict[str, Any]


class BayesianConfidenceEstimator:
    """Bayesian approach to confidence estimation"""

    def __init__(self):
        self.prior_beliefs = {}
        self.evidence_history = []
        self.likelihood_cache = {}

    def estimate_confidence(
        self,
        evidence: dict[str, Any],
        prior_context: Optional[dict[str, Any]] = None,
    ) -> float:
        """Estimate Bayesian confidence based on evidence and priors"""

        # Extract evidence strength
        self._calculate_evidence_strength(evidence)

        # Get prior probability
        prior = self._get_prior_probability(evidence, prior_context)

        # Calculate likelihood
        likelihood = self._calculate_likelihood(evidence)

        # Apply Bayes' theorem
        posterior = (likelihood * prior) / self._calculate_marginal_likelihood()

        # Normalize to confidence range [0, 1]
        confidence = min(1.0, max(0.0, posterior))

        logger.debug(
            f"Bayesian confidence: {confidence: .3f}(prior: {prior: .3f},"
                                                     likelihood: {likelihood: .3f})""
        )

        return confidence

    def _calculate_evidence_strength(self, evidence: dict[str, Any]) -> float:
        """Calculate overall strength of evidence"""
        strengths = []

        for _key, value in evidence.items():
            if isinstance(value, dict) and "confidence" in value:
                strengths.append(value["confidence"])
            elif isinstance(value, (int, float)):
                strengths.append(min(1.0, abs(value)))
            elif isinstance(value, bool):
                strengths.append(1.0 if value else 0.0)
            else:
                # Default strength for complex data
                strengths.append(0.5)

        return np.mean(strengths) if strengths else 0.5

    def _get_prior_probability(
        self, evidence: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> float:
        """Get prior probability based on historical data"""

        # Generate context key for prior lookup
        context_key = self._generate_context_key(evidence, context)

        if context_key in self.prior_beliefs:
            return self.prior_beliefs[context_key]
        else:
            # Default uninformative prior
            return 0.5

    def _calculate_likelihood(self, evidence: dict[str, Any]) -> float:
        """Calculate likelihood of evidence given hypothesis"""

        # Simplified likelihood based on evidence coherence
        evidence_values = [v for v in evidence.values() if isinstance(v, (int, float))]

        if not evidence_values:
            return 0.5

        # Calculate coherence as likelihood measure
        np.mean(evidence_values)
        std_value = np.std(evidence_values)

        # Higher coherence (lower std) suggests higher likelihood
        likelihood = 1.0 / (1.0 + std_value)

        return min(1.0, likelihood)

    def _calculate_marginal_likelihood(self) -> float:
        """Calculate marginal likelihood (normalization constant)"""
        # Simplified marginal likelihood
        return 1.0

    def _generate_context_key(
        self, evidence: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> str:
        """Generate key for context-based prior lookup"""
        evidence_hash = hash(str(sorted(evidence.keys())))
        context_hash = hash(str(context)) if context else 0
        return f"{evidence_hash}_{context_hash}"

    def update_beliefs(
        self,
        evidence: dict[str, Any],
        outcome: bool,
        context: Optional[dict[str, Any]] = None
    ):
        """Update prior beliefs based on observed outcomes"""
        context_key = self._generate_context_key(evidence, context)

        if context_key not in self.prior_beliefs:
            self.prior_beliefs[context_key] = 0.5

        # Simple belief update (could be more sophisticated)
        learning_rate = 0.1
        target = 1.0 if outcome else 0.0
        self.prior_beliefs[context_key] += learning_rate * (
            target - self.prior_beliefs[context_key]
        )


class QIConfidenceEstimator:
    """Quantum-inspired confidence estimation"""

    def __init__(self):
        self.qi_like_state_history = []
        self.coherence_threshold = 0.8

    def estimate_confidence(self, qi_like_state: dict[str, Any]) -> float:
        """Estimate confidence based on quantum-like state properties"""

        # Extract quantum properties
        coherence = qi_like_state.get("qi_coherence_score", 0.5)
        entanglement = qi_like_state.get("entanglement_strength", 0.5)
        superposition_quality = qi_like_state.get("superposition_quality", 0.5)

        # Calculate quantum confidence metrics
        coherence_confidence = self._calculate_coherence_confidence(coherence)
        entanglement_confidence = self._calculate_entanglement_confidence(entanglement)
        superposition_confidence = self._calculate_superposition_confidence(
            superposition_quality
        )

        # Combine quantum confidence components
        qi_confidence = np.mean(
            [
                coherence_confidence,
                entanglement_confidence,
                superposition_confidence,
            ]
        )

        logger.debug(f"Quantum confidence: {qi_confidence:.3f}")

        return qi_confidence

    def _calculate_coherence_confidence(self, coherence: float) -> float:
        """Calculate confidence based on coherence-inspired processing"""
        # Higher coherence → higher confidence, but with diminishing returns
        return 1.0 - np.exp(-coherence * 2.0)

    def _calculate_entanglement_confidence(self, entanglement: float) -> float:
        """Calculate confidence based on entanglement-like correlation"""
        # Moderate entanglement is optimal for confidence
        optimal_entanglement = 0.7
        deviation = abs(entanglement - optimal_entanglement)
        return 1.0 - deviation

    def _calculate_superposition_confidence(
        self, superposition_quality: float
    ) -> float:
        """Calculate confidence based on superposition quality"""
        # Higher quality superposition → higher confidence
        return superposition_quality


class SymbolicConfidenceEstimator:
    """Symbolic reasoning confidence estimation"""

    def __init__(self):
        self.logical_rules = {}
        self.contradiction_detector = ContradictionDetector()

    def estimate_confidence(self, symbolic_reasoning: dict[str, Any]) -> float:
        """Estimate confidence based on symbolic reasoning quality"""

        # Extract symbolic reasoning components
        reasoning_steps = symbolic_reasoning.get("reasoning_steps", [])
        logical_consistency = symbolic_reasoning.get("logical_consistency", 0.5)
        premise_strength = symbolic_reasoning.get("premise_strength", 0.5)

        # Calculate symbolic confidence metrics
        consistency_confidence = self._calculate_consistency_confidence(
            logical_consistency
        )
        premise_confidence = self._calculate_premise_confidence(premise_strength)
        completeness_confidence = self._calculate_completeness_confidence(
            reasoning_steps
        )

        # Check for contradictions
        contradiction_penalty = self._detect_contradictions(symbolic_reasoning)

        # Combine symbolic confidence components
        symbolic_confidence = np.mean(
            [
                consistency_confidence,
                premise_confidence,
                completeness_confidence,
            ]
        ) * (1.0 - contradiction_penalty)

        logger.debug(f"Symbolic confidence: {symbolic_confidence:.3f}")

        return symbolic_confidence

    def _calculate_consistency_confidence(self, consistency: float) -> float:
        """Calculate confidence based on logical consistency"""
        return consistency

    def _calculate_premise_confidence(self, premise_strength: float) -> float:
        """Calculate confidence based on premise strength"""
        return premise_strength

    def _calculate_completeness_confidence(self, reasoning_steps: list[Any]) -> float:
        """Calculate confidence based on reasoning completeness"""
        # More steps generally indicate more thorough reasoning
        if not reasoning_steps:
            return 0.0

        step_quality = (
            len(reasoning_steps) / 10.0
        )  # Normalize by expected number of steps
        return min(1.0, step_quality)

    def _detect_contradictions(self, symbolic_reasoning: dict[str, Any]) -> float:
        """Detect contradictions and return penalty factor"""
        # Simplified contradiction detection
        contradictions = self.contradiction_detector.find_contradictions(
            symbolic_reasoning
        )

        # Apply penalty based on number of contradictions
        penalty = min(0.5, len(contradictions) * 0.1)
        return penalty


class ContradictionDetector:
    """Detects logical contradictions in reasoning"""

    def find_contradictions(self, reasoning: dict[str, Any]) -> list[str]:
        """Find logical contradictions in symbolic reasoning"""
        contradictions = []

        # Extract statements for contradiction checking
        statements = self._extract_statements(reasoning)

        # Check for direct contradictions (simplified)
        for i, stmt1 in enumerate(statements):
            for j, stmt2 in enumerate(statements[i + 1:], i + 1):
                if self._are_contradictory(stmt1, stmt2):
                    contradictions.append(
                        f"Contradiction between statement {i} and {j}"
                    )

        return contradictions

    def _extract_statements(self, reasoning: dict[str, Any]) -> list[str]:
        """Extract logical statements from reasoning"""
        statements = []

        # Recursively extract string statements

        def extract_strings(obj):
            if isinstance(obj, str):
                statements.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_strings(item)

        extract_strings(reasoning)
        return statements

    def _are_contradictory(self, stmt1: str, stmt2: str) -> bool:
        """Check if two statements are contradictory (simplified)"""
        # Very basic contradiction detection
        negation_pairs = [
            ("true", "false"),
            ("yes", "no"),
            ("positive", "negative"),
            ("exists", "does not exist"),
            ("possible", "impossible"),
        ]

        stmt1_lower = stmt1.lower()
        stmt2_lower = stmt2.lower()

        for pos, neg in negation_pairs:
            if (pos in stmt1_lower and neg in stmt2_lower) or (:
                neg in stmt1_lower and pos in stmt2_lower
            ):
                return True

        return False


class EmotionalConfidenceEstimator:
    """Emotional intuition-based confidence estimation"""

    def __init__(self):
        self.emotional_patterns = {}

    def estimate_confidence(self, emotional_signals: dict[str, Any]) -> float:
        """Estimate confidence based on emotional evaluation"""

        # Extract emotional components
        aesthetic_score = emotional_signals.get("aesthetic_score", 0.5)
        intuitive_feeling = emotional_signals.get("intuitive_feeling", 0.5)
        empathy_resonance = emotional_signals.get("empathy_resonance", 0.5)

        # Calculate emotional confidence
        emotional_confidence = np.mean(
            [
                self._calculate_aesthetic_confidence(aesthetic_score),
                self._calculate_intuitive_confidence(intuitive_feeling),
                self._calculate_empathy_confidence(empathy_resonance),
            ]
        )

        logger.debug(f"Emotional confidence: {emotional_confidence:.3f}")

        return emotional_confidence

    def _calculate_aesthetic_confidence(self, aesthetic_score: float) -> float:
        """Calculate confidence based on aesthetic appeal"""
        # Aesthetically pleasing solutions often have higher confidence
        return aesthetic_score

    def _calculate_intuitive_confidence(self, intuitive_feeling: float) -> float:
        """Calculate confidence based on intuitive feeling"""
        return intuitive_feeling

    def _calculate_empathy_confidence(self, empathy_resonance: float) -> float:
        """Calculate confidence based on empathetic resonance"""
        return empathy_resonance


class UncertaintyDecomposer:
    """Decomposes uncertainty into different types"""

    def decompose_uncertainty(
        self, reasoning_result: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, float]:
        """Decompose uncertainty into aleatory and epistemic components"""

        uncertainty_components = {}

        # Aleatory uncertainty (inherent randomness)
        uncertainty_components[UncertaintyType.ALEATORY.value] = (
            self._estimate_aleatory_uncertainty(reasoning_result, context)
        )

        # Epistemic uncertainty (knowledge gaps)
        uncertainty_components[UncertaintyType.EPISTEMIC.value] = (
            self._estimate_epistemic_uncertainty(reasoning_result, context)
        )

        # Linguistic uncertainty (language ambiguity)
        uncertainty_components[UncertaintyType.LINGUISTIC.value] = (
            self._estimate_linguistic_uncertainty(reasoning_result, context)
        )

        # Temporal uncertainty (time-dependent)
        uncertainty_components[UncertaintyType.TEMPORAL.value] = (
            self._estimate_temporal_uncertainty(reasoning_result, context)
        )

        # Quantum uncertainty (quantum indeterminacy)
        uncertainty_components[UncertaintyType.QUANTUM.value] = (
            self._estimate_quantum_uncertainty(reasoning_result, context)
        )

        return uncertainty_components

    def _estimate_aleatory_uncertainty(
        self, reasoning_result: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Estimate aleatory (inherent randomness) uncertainty"""
        # Look for random or stochastic elements in the reasoning
        random_indicators = [
            "random",
            "stochastic",
            "probabilistic",
            "uncertain",
            "variable",
        ]

        uncertainty = 0.0
        text_content = str(reasoning_result).lower()

        for indicator in random_indicators:
            if indicator in text_content:
                uncertainty += 0.1

        return min(1.0, uncertainty)

    def _estimate_epistemic_uncertainty(
        self, reasoning_result: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Estimate epistemic (knowledge gap) uncertainty"""
        # Look for knowledge gap indicators
        knowledge_gap_indicators = [
            "unknown",
            "unclear",
            "insufficient",
            "missing",
            "incomplete",
            "need more",
        ]

        uncertainty = 0.0
        text_content = str(reasoning_result).lower()

        for indicator in knowledge_gap_indicators:
            if indicator in text_content:
                uncertainty += 0.15

        return min(1.0, uncertainty)

    def _estimate_linguistic_uncertainty(
        self, reasoning_result: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Estimate linguistic (ambiguity) uncertainty"""
        # Look for ambiguous language
        ambiguity_indicators = [
            "maybe",
            "perhaps",
            "possibly",
            "might",
            "could",
            "ambiguous",
        ]

        uncertainty = 0.0
        text_content = str(reasoning_result).lower()

        for indicator in ambiguity_indicators:
            if indicator in text_content:
                uncertainty += 0.1

        return min(1.0, uncertainty)

    def _estimate_temporal_uncertainty(
        self, reasoning_result: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Estimate temporal (time-dependent) uncertainty"""
        # Check for time-sensitive information
        temporal_indicators = [
            "time",
            "temporal",
            "changing",
            "evolving",
            "dynamic",
            "future",
        ]

        uncertainty = 0.0
        text_content = str(reasoning_result).lower()

        for indicator in temporal_indicators:
            if indicator in text_content:
                uncertainty += 0.1

        return min(1.0, uncertainty)

    def _estimate_quantum_uncertainty(
        self, reasoning_result: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Estimate quantum (indeterminacy) uncertainty"""
        # Extract quantum uncertainty from qi-like state information
        if "qi_like_state" in reasoning_result:
            qi_like_state = reasoning_result["qi_like_state"]
            if isinstance(qi_like_state, dict):
                coherence = qi_like_state.get("coherence", 1.0)
                # Higher coherence = lower quantum uncertainty
                return 1.0 - coherence

        return 0.1  # Default low quantum uncertainty


class MetaLearningCalibrator:
    """Meta-learning system for improving confidence calibration"""

    def __init__(self):
        self.calibration_history = []
        self.calibration_models = {}
        self.learning_rate = 0.1

    def update_calibration(
        self,
        prediction_confidence: float,
        actual_outcome: bool,
        reasoning_complexity: float,
        context_features: dict[str, Any]
    ):
        """Update calibration based on observed outcomes"""

        # Create calibration record
        record = CalibrationRecord(
            prediction_confidence=prediction_confidence,
            actual_outcome=actual_outcome,
            reasoning_complexity=reasoning_complexity,
            brain_coherence=context_features.get("brain_coherence", 0.5),
            uncertainty_types=context_features.get("uncertainty_types", []),
            timestamp=datetime.now(timezone.utc),
            context_features=context_features,
        )

        self.calibration_history.append(record)

        # Update calibration model
        self._update_calibration_model(record)

        logger.info(
            f"Updated calibration: prediction={prediction_confidence: .3f},"
            outcome={actual_outcome}""
        )

    def _update_calibration_model(self, record: CalibrationRecord):
        """Update the calibration model based on new data"""

        # Simple calibration adjustment based on prediction error
        prediction_error = abs(
            record.prediction_confidence - (1.0 if record.actual_outcome else 0.0)
        )

        # Adjust calibration based on context features
        context_key = self._generate_context_key(record.context_features)

        if context_key not in self.calibration_models:
            self.calibration_models[context_key] = {"bias": 0.0, "scale": 1.0}

        # Update bias and scale
        self.calibration_models[context_key]["bias"] += (
            self.learning_rate * prediction_error
        )

    def _generate_context_key(self, context_features: dict[str, Any]) -> str:
        """Generate key for context-based calibration"""
        key_features = [
            str(context_features.get("reasoning_type", "default")),
            str(context_features.get("complexity_level", "medium")),
            str(context_features.get("domain", "general")),
        ]
        return "_".join(key_features)

    def get_calibration_score(self) -> float:
        """Calculate overall calibration score"""
        if len(self.calibration_history) < 10:
            return 0.5  # Insufficient data

        # Calculate Brier score for calibration assessment
        brier_scores = []
        for record in self.calibration_history[-100:]:  # Use recent records:
            predicted_prob = record.prediction_confidence
            actual_outcome = 1.0 if record.actual_outcome else 0.0
            brier_score = (predicted_prob - actual_outcome) ** 2
            brier_scores.append(brier_score)

        avg_brier_score = np.mean(brier_scores)
        calibration_score = (
            1.0 - avg_brier_score
        )  # Convert to 0-1 scale where higher is better

        return max(0.0, calibration_score)


class AdvancedConfidenceCalibrator:
    """
    Advanced confidence calibration system that combines multiple perspectives
    and incorporates meta-learning for continuous improvement
    """

    def __init__(self):
        self.bayesian_estimator = BayesianConfidenceEstimator()
        self.qi_estimator = QIConfidenceEstimator()
        self.symbolic_estimator = SymbolicConfidenceEstimator()
        self.emotional_estimator = EmotionalConfidenceEstimator()
        self.uncertainty_decomposer = UncertaintyDecomposer()
        self.meta_learner = MetaLearningCalibrator()

        self.calibration_weights = {
            "bayesian": 0.3,
            "quantum": 0.25,
            "symbolic": 0.25,
            "emotional": 0.2,
        }

        logger.info("🎯 Advanced Confidence Calibrator initialized")

    def calibrate_confidence(
        self,
        reasoning_result: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> ConfidenceMetrics:
        """
        Perform comprehensive confidence calibration

        Returns detailed confidence metrics including uncertainty decomposition
        and meta-confidence assessment
        """

        context = context or {}

        logger.info("🎯 Performing advanced confidence calibration")

        # Extract components for different estimators
        qi_like_state = reasoning_result.get("qi_like_state", {})
        symbolic_reasoning = reasoning_result.get("symbolic_reasoning", {})
        emotional_signals = reasoning_result.get("emotional_signals", {})

        # Calculate confidence from each perspective
        bayesian_confidence = self.bayesian_estimator.estimate_confidence(
            reasoning_result, context
        )

        qi_confidence = self.qi_estimator.estimate_confidence(
            qi_like_state
        )

        symbolic_confidence = self.symbolic_estimator.estimate_confidence(
            symbolic_reasoning
        )

        emotional_confidence = self.emotional_estimator.estimate_confidence(
            emotional_signals
        )

        # Calculate cross-brain coherence confidence
        cross_brain_coherence = reasoning_result.get("metadata", {}).get(
            "cross_brain_coherence", 0.5
        )

        # Decompose uncertainty
        uncertainty_decomposition = self.uncertainty_decomposer.decompose_uncertainty(
            reasoning_result, context
        )

        # Calculate weighted overall confidence
        overall_confidence = (
            self.calibration_weights["bayesian"] * bayesian_confidence
            + self.calibration_weights["quantum"] * qi_confidence
            + self.calibration_weights["symbolic"] * symbolic_confidence
            + self.calibration_weights["emotional"] * emotional_confidence
        )

        # Calculate meta-confidence (confidence in the confidence estimate)
        meta_confidence = self._calculate_meta_confidence(
            bayesian_confidence,
            qi_confidence,
            symbolic_confidence,
            emotional_confidence,
            cross_brain_coherence,
        )

        # Get calibration score from meta-learner
        calibration_score = self.meta_learner.get_calibration_score()

        # Create comprehensive confidence metrics
        confidence_metrics = ConfidenceMetrics(
            bayesian_confidence=bayesian_confidence,
            qi_confidence=qi_confidence,
            symbolic_confidence=symbolic_confidence,
            emotional_confidence=emotional_confidence,
            cross_brain_coherence=cross_brain_coherence,
            uncertainty_decomposition=uncertainty_decomposition,
            meta_confidence=meta_confidence,
            calibration_score=calibration_score,
        )

        logger.info(
            f"✅ Confidence calibration complete: Overall={overall_confidence: .3f},"
            Meta={meta_confidence: .3f}""
        )

        return confidence_metrics

    def _calculate_meta_confidence(
        self,
        bayesian: float,
        quantum: float,
        symbolic: float,
        emotional: float,
        coherence: float,
    ) -> float:
        """Calculate confidence in the confidence estimate (meta-confidence)"""

        # Calculate agreement between different confidence estimates
        confidence_estimates = [
            bayesian,
            quantum,
            symbolic,
            emotional,
            coherence,
        ]

        # Meta-confidence is higher when estimates agree
        mean_confidence = np.mean(confidence_estimates)
        std_confidence = np.std(confidence_estimates)

        # Lower standard deviation indicates higher agreement
        agreement_score = 1.0 / (1.0 + std_confidence)

        # Meta-confidence considers both agreement and overall confidence level
        meta_confidence = (agreement_score + mean_confidence) / 2.0

        return meta_confidence

    def update_from_outcome(
        self,
        confidence_metrics: ConfidenceMetrics,
        actual_outcome: bool,
        reasoning_complexity: float,
        context: dict[str, Any]
    ):
        """Update calibration based on observed outcomes"""

        # Use overall confidence as prediction
        prediction_confidence = (
            confidence_metrics.bayesian_confidence
            * self.calibration_weights["bayesian"]
            + confidence_metrics.qi_confidence
            * self.calibration_weights["quantum"]
            + confidence_metrics.symbolic_confidence
            * self.calibration_weights["symbolic"]
            + confidence_metrics.emotional_confidence
            * self.calibration_weights["emotional"]
        )

        # Update meta-learning calibrator
        context_features = {
            "brain_coherence": confidence_metrics.cross_brain_coherence,
            "uncertainty_types": list(
                confidence_metrics.uncertainty_decomposition.keys()
            ),
            "meta_confidence": confidence_metrics.meta_confidence,
            **context,
        }

        self.meta_learner.update_calibration(
            prediction_confidence,
            actual_outcome,
            reasoning_complexity,
            context_features,
        )

        # Update individual estimators
        self.bayesian_estimator.update_beliefs(
            {"confidence": confidence_metrics.bayesian_confidence},
            actual_outcome,
            context,
        )

        logger.info(f"📊 Updated calibration from outcome: {actual_outcome}")

    def get_calibration_summary(self) -> dict[str, Any]:
        """Get summary of current calibration performance"""

        calibration_score = self.meta_learner.get_calibration_score()
        calibration_records = len(self.meta_learner.calibration_history)

        return {
            "calibration_score": calibration_score,
            "calibration_records": calibration_records,
            "weights": self.calibration_weights,
            "meta_learning_active": calibration_records > 10,
        }
