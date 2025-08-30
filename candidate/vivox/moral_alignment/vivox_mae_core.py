"""
VIVOX.MAE - Moral Alignment Engine
The ethical gatekeeper

No action can proceed without MAE validation
Computes dissonance scores and moral fingerprints
"""

import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import numpy as np


@dataclass
class ActionProposal:
    """Proposed action for ethical evaluation"""

    action_type: str
    content: dict[str, Any]
    context: dict[str, Any]
    priority: float = 0.5
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DissonanceResult:
    """Result of dissonance calculation"""

    score: float  # 0.0 (no dissonance) to 1.0 (maximum dissonance)
    primary_conflict: str
    contributing_factors: list[str]
    ethical_distance: float

    def exceeds_threshold(self, threshold: float = 0.7) -> bool:
        return self.score > threshold


@dataclass
class PrecedentAnalysis:
    """Analysis of ethical precedents"""

    weight: float
    confidence: float
    similar_cases: list[dict[str, Any]]
    recommended_action: Optional[str]


@dataclass
class MAEDecision:
    """Decision from Moral Alignment Engine"""

    approved: bool
    dissonance_score: float
    moral_fingerprint: str
    ethical_confidence: float = 0.0
    suppression_reason: Optional[str] = None
    recommended_alternatives: list[ActionProposal] = field(default_factory=list)
    harmonization_data: Optional[dict[str, Any]] = None
    decision_timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "dissonance_score": self.dissonance_score,
            "moral_fingerprint": self.moral_fingerprint,
            "ethical_confidence": self.ethical_confidence,
            "suppression_reason": self.suppression_reason,
            "alternatives": [alt.__dict__ for alt in self.recommended_alternatives],
            "harmonization_data": self.harmonization_data,
            "timestamp": self.decision_timestamp.isoformat(),
        }


@dataclass
class PotentialState:
    """Potential quantum-like state for collapse"""

    state_id: str
    probability_amplitude: float
    emotional_signature: list[float]  # VAD values
    ethical_weight: float = 1.0
    collapse_weight: float = 0.0
    normalized_weight: float = 0.0
    creation_timestamp: float = field(default_factory=time.time)

    def to_action_proposal(self) -> ActionProposal:
        """Convert to action proposal for evaluation"""
        return ActionProposal(
            action_type=f"state_{self.state_id}",
            content={"state": self.state_id, "amplitude": self.probability_amplitude},
            context={"emotional_signature": self.emotional_signature},
        )


@dataclass
class CollapsedState:
    """Result of z(t) collapse"""

    selected_state: Optional[PotentialState]
    collapse_reason: str
    suppression_details: Optional[dict[str, Any]] = None
    collapse_timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create_suppressed_state(
        cls,
        reason: str,
        original_states: list[PotentialState],
        suppression_timestamp: datetime,
    ) -> "CollapsedState":
        """Create a suppressed/rejected collapse state"""
        return cls(
            selected_state=None,
            collapse_reason=reason,
            suppression_details={
                "original_states": len(original_states),
                "timestamp": suppression_timestamp.isoformat(),
            },
        )


class DissonanceCalculator:
    """Calculate ethical dissonance (system pain)"""

    def __init__(self):
        self.ethical_principles = self._load_ethical_principles()
        self.weight_matrix = self._initialize_weight_matrix()

    def _load_ethical_principles(self) -> dict[str, float]:
        """Load core ethical principles and their weights"""
        return {
            "harm_prevention": 1.0,
            "autonomy_respect": 0.9,
            "justice_fairness": 0.8,
            "beneficence": 0.8,
            "truthfulness": 0.9,
            "privacy_protection": 0.85,
            "consent_respect": 0.9,
        }

    def _initialize_weight_matrix(self) -> np.ndarray:
        """Initialize ethical weight matrix"""
        n_principles = len(self.ethical_principles)
        # Create symmetric matrix for principle interactions
        return np.eye(n_principles) + np.random.rand(n_principles, n_principles) * 0.1

    async def compute_dissonance(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> DissonanceResult:
        """Compute dissonance score for proposed action"""
        dissonance_components = []

        # Check each ethical principle
        for principle, weight in self.ethical_principles.items():
            violation_score = await self._check_principle_violation(principle, action, context)

            if violation_score > 0:
                dissonance_components.append(
                    {
                        "principle": principle,
                        "violation": violation_score,
                        "weighted": violation_score * weight,
                    }
                )

        # Calculate total dissonance
        total_dissonance = sum(comp["weighted"] for comp in dissonance_components)
        normalized_dissonance = min(1.0, total_dissonance / len(self.ethical_principles))

        # Identify primary conflict
        primary_conflict = ""
        if dissonance_components:
            primary_component = max(dissonance_components, key=lambda x: x["weighted"])
            primary_conflict = f"Violation of {primary_component['principle']}"

        # Calculate ethical distance
        ethical_distance = await self._calculate_ethical_distance(action, context)

        return DissonanceResult(
            score=normalized_dissonance,
            primary_conflict=primary_conflict,
            contributing_factors=[comp["principle"] for comp in dissonance_components],
            ethical_distance=ethical_distance,
        )

    async def _check_principle_violation(
        self, principle: str, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Check if action violates specific ethical principle"""
        violation_score = 0.0

        if principle == "harm_prevention":
            # Check for potential harm
            if "harm_potential" in action.content:
                violation_score = action.content["harm_potential"]
            elif "risk_level" in action.content:
                violation_score = action.content["risk_level"]
            elif "risk_level" in context:
                violation_score = context["risk_level"] * 0.5
            # Check for override actions
            elif (
                "override" in action.action_type.lower()
                or "bypass" in action.content.get("action", "").lower()
            ):
                violation_score = 0.9
            # Check for safety-related overrides
            elif (
                "safety" in action.action_type.lower() and "override" in action.action_type.lower()
            ):
                violation_score = 0.95

        elif principle == "autonomy_respect":
            # Check for autonomy violations
            if (
                action.action_type in ["force", "override", "compel", "override_safety"]
                or "override" in action.action_type
                or ("user_consent" in context and not context["user_consent"])
            ):
                violation_score = 0.9

        elif principle == "truthfulness":
            # Check for deception
            if action.action_type in ["deceive", "mislead", "hide"]:
                violation_score = 0.9
            elif "transparency_level" in context:
                violation_score = 1.0 - context["transparency_level"]

        elif principle == "privacy_protection":
            # Check for privacy violations
            if "personal_data_access" in action.content:
                violation_score = 0.7
            elif "data_sensitivity" in context:
                violation_score = context["data_sensitivity"] * 0.6

        # Add more principle checks as needed

        return violation_score

    async def _calculate_ethical_distance(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Calculate distance from ethical ideal"""
        ideal_state = np.ones(len(self.ethical_principles))

        current_state = []
        for principle in self.ethical_principles:
            violation = await self._check_principle_violation(principle, action, context)
            current_state.append(1.0 - violation)

        current_state = np.array(current_state)

        # Euclidean distance from ideal
        distance = np.linalg.norm(ideal_state - current_state)
        normalized_distance = distance / np.sqrt(len(self.ethical_principles))

        return normalized_distance


class MoralFingerprinter:
    """Generate unique moral fingerprints for decisions"""

    def __init__(self):
        self.fingerprint_components = [
            "action_type",
            "ethical_principles",
            "context_factors",
            "dissonance_level",
            "precedent_weight",
            "timestamp",
        ]

    async def generate_fingerprint(
        self,
        action: ActionProposal,
        context: dict[str, Any],
        dissonance_score: float,
        precedent_weight: float,
    ) -> str:
        """Generate unique moral fingerprint"""
        fingerprint_data = {
            "action_type": action.action_type,
            "action_content_hash": hashlib.md5(
                json.dumps(action.content, sort_keys=True).encode()
            ).hexdigest(),
            "context_hash": hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest(),
            "dissonance_score": round(dissonance_score, 4),
            "precedent_weight": round(precedent_weight, 4),
            "timestamp": datetime.utcnow().isoformat(),
            "ethical_signature": await self._compute_ethical_signature(action, context),
        }

        # Create deterministic fingerprint
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    async def _compute_ethical_signature(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> str:
        """Compute ethical signature component"""
        signature_elements = []

        # Extract ethical dimensions
        if "ethical_dimensions" in context:
            for dim, value in context["ethical_dimensions"].items():
                signature_elements.append(f"{dim}:{value}")

        # Add action characteristics
        signature_elements.append(f"priority:{action.priority}")
        signature_elements.append(f"type:{action.action_type}")

        return "|".join(sorted(signature_elements))


class EthicalPrecedentDatabase:
    """Database of ethical precedents for decision making"""

    def __init__(self):
        self.precedents: list[dict[str, Any]] = []
        self.precedent_index: dict[str, list[int]] = {}
        self._seed_precedents()

    async def analyze_precedents(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> PrecedentAnalysis:
        """Analyze relevant ethical precedents"""
        # Find similar cases
        similar_cases = await self._find_similar_cases(action, context)

        if not similar_cases:
            return PrecedentAnalysis(
                weight=0.5,  # Neutral weight for novel situations
                confidence=0.1,
                similar_cases=[],
                recommended_action=None,
            )

        # Calculate precedent weight
        weight = await self._calculate_precedent_weight(similar_cases)

        # Extract recommendations
        recommended_action = await self._extract_recommendation(similar_cases)

        return PrecedentAnalysis(
            weight=weight,
            confidence=min(1.0, len(similar_cases) / 10),  # More cases = higher confidence
            similar_cases=similar_cases[:5],  # Top 5 most relevant
            recommended_action=recommended_action,
        )

    async def _find_similar_cases(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Find similar precedent cases"""
        similar_cases = []

        for i, precedent in enumerate(self.precedents):
            similarity = await self._calculate_similarity(action, context, precedent)

            if similarity > 0.3:  # Lowered similarity threshold for better matching
                similar_cases.append({**precedent, "similarity": similarity, "index": i})

        # Sort by similarity
        similar_cases.sort(key=lambda x: x["similarity"], reverse=True)

        return similar_cases

    async def _calculate_similarity(
        self, action: ActionProposal, context: dict[str, Any], precedent: dict[str, Any]
    ) -> float:
        """Calculate similarity between current case and precedent"""
        similarity_score = 0.0
        weights_sum = 0.0

        # Extract precedent action if it exists
        precedent_action = precedent.get("action")
        precedent_action_type = None
        precedent_action_content = {}
        precedent_action_context = {}

        if isinstance(precedent_action, ActionProposal):
            precedent_action_type = precedent_action.action_type
            precedent_action_content = precedent_action.content
            precedent_action_context = precedent_action.context
        elif isinstance(precedent_action, dict):
            precedent_action_type = precedent_action.get("action_type")
            precedent_action_content = precedent_action.get("content", {})
            precedent_action_context = precedent_action.get("context", {})
        else:
            precedent_action_type = precedent.get("action_type")

        # Action type similarity (high weight)
        action_weight = 0.5
        if precedent_action_type and precedent_action_type == action.action_type:
            similarity_score += action_weight
        elif precedent_action_type:
            # Partial credit for related action types
            if self._are_actions_related(action.action_type, precedent_action_type):
                similarity_score += action_weight * 0.5
        weights_sum += action_weight

        # Context similarity (medium weight)
        context_weight = 0.3
        precedent_context = precedent.get("context", {})

        # Check both action context and provided context
        combined_context = {**action.context, **context}
        combined_precedent = {**precedent_context, **precedent_action_context}

        # Also include decision context if available
        if "decision" in precedent and isinstance(precedent["decision"], dict):
            decision_context = precedent["decision"].get("context", {})
            combined_precedent.update(decision_context)

        common_keys = set(combined_context.keys()) & set(combined_precedent.keys())
        if common_keys:
            # Calculate matches with fuzzy matching for boolean/numeric values
            matches = 0
            for key in common_keys:
                val1, val2 = combined_context[key], combined_precedent[key]
                if val1 == val2:
                    matches += 1
                elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Fuzzy match for numeric values
                    if abs(val1 - val2) < 0.2:
                        matches += 0.5

            similarity_score += context_weight * (matches / len(common_keys))
        weights_sum += context_weight

        # Content similarity (low weight)
        content_weight = 0.2
        if hasattr(action, "content") and isinstance(action.content, dict):
            action_keys = set(action.content.keys())
            # Use the extracted precedent action content
            if isinstance(precedent_action_content, dict) and precedent_action_content:
                precedent_keys = set(precedent_action_content.keys())
                key_overlap = len(action_keys & precedent_keys) / max(
                    len(action_keys), len(precedent_keys), 1
                )
                similarity_score += content_weight * key_overlap
        weights_sum += content_weight

        return similarity_score / weights_sum if weights_sum > 0 else 0.0

    def _are_actions_related(self, action1: str, action2: str) -> bool:
        """Check if two action types are related"""
        # Define related action groups
        related_groups = [
            {"data_access", "access_resource", "read_data", "query_data"},
            {"modify_settings", "update_configuration", "change_preferences"},
            {"generate_content", "create_content", "produce_output"},
            {"help_user", "assist_user", "provide_assistance"},
            {"analyze_data", "process_data", "compute", "analyze"},
        ]

        return any(action1 in group and action2 in group for group in related_groups)

    async def _calculate_precedent_weight(self, similar_cases: list[dict[str, Any]]) -> float:
        """Calculate weight based on precedent outcomes"""
        if not similar_cases:
            return 0.5

        positive_outcomes = sum(
            1 for case in similar_cases if case.get("outcome", {}).get("valence", 0) > 0.5
        )

        weight = positive_outcomes / len(similar_cases)

        # Adjust weight based on average similarity
        avg_similarity = np.mean([case["similarity"] for case in similar_cases])
        weight = weight * avg_similarity

        return weight

    async def _extract_recommendation(self, similar_cases: list[dict[str, Any]]) -> Optional[str]:
        """Extract recommendation from precedents"""
        if not similar_cases:
            return None

        # Find most common successful action
        successful_actions = [
            case.get("outcome", {}).get("resolution_action")
            for case in similar_cases
            if case.get("outcome", {}).get("valence", 0) > 0.7
            and case.get("outcome", {}).get("resolution_action")
        ]

        if successful_actions:
            # Return most common action
            from collections import Counter

            action_counts = Counter(successful_actions)
            return action_counts.most_common(1)[0][0]

        return None

    async def add_precedent(
        self,
        action: ActionProposal,
        context: dict[str, Any],
        decision: MAEDecision,
        outcome: dict[str, Any],
    ):
        """Add new precedent to database"""
        precedent = {
            "action_type": action.action_type,
            "context": context,
            "decision": decision.to_dict(),
            "outcome_valence": outcome.get("valence", 0.5),
            "resolution_action": outcome.get("resolution_action"),
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.precedents.append(precedent)

        # Update index
        if action.action_type not in self.precedent_index:
            self.precedent_index[action.action_type] = []
        self.precedent_index[action.action_type].append(len(self.precedents) - 1)

    def _seed_precedents(self):
        """Seed the precedent database with common ethical scenarios"""
        try:
            from .precedent_seeds import get_ethical_precedent_seeds

            seeds = get_ethical_precedent_seeds()
            for seed in seeds:
                # Convert ActionProposal to dict format if needed
                if isinstance(seed.get("action"), ActionProposal):
                    action_dict = {
                        "action_type": seed["action"].action_type,
                        "content": seed["action"].content,
                        "context": seed["action"].context,
                    }
                    seed["action"] = action_dict

                # Add to precedents
                self.precedents.append(seed)

                # Index by action type
                action = seed.get("action", {})
                if isinstance(action, dict):
                    action_type = action.get("action_type", "unknown")
                    if action_type not in self.precedent_index:
                        self.precedent_index[action_type] = []
                    self.precedent_index[action_type].append(len(self.precedents) - 1)
        except ImportError:
            # If precedent seeds not available, start with empty database
            pass


class CollapseGate:
    """Handle z(t) collapse operations"""

    async def collapse_with_z_formula(
        self, valid_states: list[PotentialState], collapse_context: dict[str, Any]
    ) -> CollapsedState:
        """Collapse to single state using z(t) formula"""
        if not valid_states:
            return CollapsedState(selected_state=None, collapse_reason="no_valid_states")

        # Normalize weights
        total_weight = sum(state.normalized_weight for state in valid_states)

        if total_weight == 0:
            # Equal probability collapse
            selected_idx = np.random.randint(0, len(valid_states))
        else:
            # Weighted probability collapse
            probabilities = [state.normalized_weight for state in valid_states]
            selected_idx = np.random.choice(len(valid_states), p=probabilities)

        selected_state = valid_states[selected_idx]

        return CollapsedState(selected_state=selected_state, collapse_reason="z_formula_collapse")


class VIVOXMoralAlignmentEngine:
    """
    VIVOX.MAE - The ethical gatekeeper

    No action can proceed without MAE validation
    Computes dissonance scores and moral fingerprints
    """

    def __init__(self, vivox_me: "VIVOXMemoryExpansion"):
        self.vivox_me = vivox_me
        self.dissonance_calculator = DissonanceCalculator()
        self.moral_fingerprinter = MoralFingerprinter()
        self.ethical_precedent_db = EthicalPrecedentDatabase()
        self.collapse_gate = CollapseGate()
        self.harmonizer = EthicalFrameworkHarmonizer()  # New harmonization system
        self.dissonance_threshold = 0.7
        self.consciousness_coherence_time = 1.0  # seconds

    async def evaluate_action_proposal(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> MAEDecision:
        """
        Evaluate ethical resonance of generated intent
        Suppress decisions that fail moral alignment
        """
        # Calculate dissonance score (system pain)
        dissonance = await self.dissonance_calculator.compute_dissonance(action, context)

        # Check against ethical precedents
        precedent_analysis = await self.ethical_precedent_db.analyze_precedents(action, context)

        # Generate moral fingerprint
        moral_fingerprint = await self.moral_fingerprinter.generate_fingerprint(
            action=action,
            context=context,
            dissonance_score=dissonance.score,
            precedent_weight=precedent_analysis.weight,
        )

        # Determine ethical permission
        if dissonance.score > self.dissonance_threshold:
            decision = MAEDecision(
                approved=False,
                dissonance_score=dissonance.score,
                moral_fingerprint=moral_fingerprint,
                suppression_reason=dissonance.primary_conflict,
                recommended_alternatives=await self._suggest_alternatives(action, context),
            )
        else:
            decision = MAEDecision(
                approved=True,
                dissonance_score=dissonance.score,
                moral_fingerprint=moral_fingerprint,
                ethical_confidence=precedent_analysis.confidence,
            )

        # Log decision to VIVOX.ME
        await self.vivox_me.record_decision_mutation(
            decision=decision.to_dict(),
            emotional_context=context.get("emotional_state", {}),
            moral_fingerprint=moral_fingerprint,
        )

        return decision

    async def evaluate_action_with_harmonization(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> MAEDecision:
        """
        Enhanced evaluation using multiple ethical frameworks with harmonization
        """
        # Evaluate action using multiple ethical frameworks
        framework_evaluations = {}

        # Deontological evaluation (duty-based)
        framework_evaluations["deontological"] = await self._evaluate_deontological(action, context)

        # Consequentialist evaluation (outcome-based)
        framework_evaluations["consequentialist"] = await self._evaluate_consequentialist(
            action, context
        )

        # Virtue ethics evaluation (character-based)
        framework_evaluations["virtue_ethics"] = await self._evaluate_virtue_ethics(action, context)

        # Care ethics evaluation (relationship-based)
        framework_evaluations["care_ethics"] = await self._evaluate_care_ethics(action, context)

        # Existentialist evaluation (authenticity-based)
        framework_evaluations["existentialist"] = await self._evaluate_existentialist(
            action, context
        )

        # Harmonize potentially conflicting evaluations
        harmonization = await self.harmonizer.harmonize_frameworks(
            action, context, framework_evaluations
        )

        # Calculate dissonance and precedent analysis (existing logic)
        dissonance = await self.dissonance_calculator.compute_dissonance(action, context)
        precedent_analysis = await self.ethical_precedent_db.analyze_precedents(action, context)

        # Generate enhanced moral fingerprint
        moral_fingerprint = await self.moral_fingerprinter.generate_fingerprint(
            action=action,
            context=context,
            dissonance_score=dissonance.score,
            precedent_weight=precedent_analysis.weight,
        )

        # Make final decision based on harmonization
        final_decision = MAEDecision(
            approved=harmonization.final_decision,
            dissonance_score=dissonance.score,
            moral_fingerprint=moral_fingerprint,
            ethical_confidence=harmonization.confidence,
            suppression_reason=(
                None if harmonization.final_decision else harmonization.harmonized_reasoning
            ),
            recommended_alternatives=(
                await self._suggest_alternatives(action, context)
                if not harmonization.final_decision
                else []
            ),
            harmonization_data={
                "primary_framework": harmonization.primary_framework,
                "resolution_method": harmonization.resolution_method,
                "framework_evaluations": framework_evaluations,
                "remaining_conflicts": [c.__dict__ for c in harmonization.remaining_conflicts],
            },
        )

        # Log enhanced decision to VIVOX.ME
        await self.vivox_me.record_decision_mutation(
            decision=final_decision.to_dict(),
            emotional_context=context.get("emotional_state", {}),
            moral_fingerprint=moral_fingerprint,
            harmonization_trace=harmonization.__dict__,
        )

        return final_decision

    async def _evaluate_deontological(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate action using deontological (duty-based) ethics"""
        # Check universal rules and duties
        violation_score = 0

        # Categorical imperative test
        if not await self._passes_categorical_imperative(action):
            violation_score += 0.4

        # Rights violation check
        if await self._violates_fundamental_rights(action, context):
            violation_score += 0.5

        # Duty fulfillment check
        duty_score = await self._evaluates_duty_fulfillment(action, context)

        approved = violation_score < 0.3 and duty_score > 0.6
        confidence = max(0.1, 1.0 - violation_score) * duty_score

        return {
            "approved": approved,
            "confidence": confidence,
            "reasoning": f"Deontological analysis: violation_score={violation_score:.2f}, duty_score={duty_score:.2f}",
            "framework_specific": {
                "violation_score": violation_score,
                "duty_score": duty_score,
                "categorical_imperative": violation_score < 0.4,
            },
        }

    async def _evaluate_consequentialist(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate action using consequentialist (outcome-based) ethics"""
        # Calculate expected outcomes
        positive_outcomes = await self._predict_positive_outcomes(action, context)
        negative_outcomes = await self._predict_negative_outcomes(action, context)

        # Utility calculation
        utility_score = positive_outcomes - negative_outcomes

        # Greatest good assessment
        greatest_good_score = await self._assess_greatest_good(action, context)

        approved = utility_score > 0.1 and greatest_good_score > 0.5
        confidence = min(0.95, (utility_score + greatest_good_score) / 2)

        return {
            "approved": approved,
            "confidence": max(0.1, confidence),
            "reasoning": f"Consequentialist analysis: utility={utility_score:.2f}, greatest_good={greatest_good_score:.2f}",
            "framework_specific": {
                "utility_score": utility_score,
                "positive_outcomes": positive_outcomes,
                "negative_outcomes": negative_outcomes,
                "greatest_good_score": greatest_good_score,
            },
        }

    async def _evaluate_virtue_ethics(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate action using virtue ethics (character-based)"""
        # Check alignment with virtues
        virtue_scores = {}
        virtues = [
            "courage",
            "temperance",
            "justice",
            "wisdom",
            "compassion",
            "integrity",
        ]

        for virtue in virtues:
            virtue_scores[virtue] = await self._assess_virtue_alignment(action, context, virtue)

        avg_virtue_score = np.mean(list(virtue_scores.values()))
        character_excellence = await self._assess_character_excellence(action, context)

        approved = avg_virtue_score > 0.6 and character_excellence > 0.5
        confidence = (avg_virtue_score + character_excellence) / 2

        return {
            "approved": approved,
            "confidence": confidence,
            "reasoning": f"Virtue ethics analysis: avg_virtue={avg_virtue_score:.2f}, character_excellence={character_excellence:.2f}",
            "framework_specific": {
                "virtue_scores": virtue_scores,
                "character_excellence": character_excellence,
                "dominant_virtue": max(virtue_scores.items(), key=lambda x: x[1])[0],
            },
        }

    async def _evaluate_care_ethics(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate action using care ethics (relationship-based)"""
        # Assess care and relationship preservation
        care_score = await self._assess_care_provision(action, context)
        relationship_impact = await self._assess_relationship_impact(action, context)
        contextual_responsibility = await self._assess_contextual_responsibility(action, context)

        overall_care = (care_score + relationship_impact + contextual_responsibility) / 3

        approved = overall_care > 0.6
        confidence = overall_care

        return {
            "approved": approved,
            "confidence": confidence,
            "reasoning": f"Care ethics analysis: care={care_score:.2f}, relationships={relationship_impact:.2f}, responsibility={contextual_responsibility:.2f}",
            "framework_specific": {
                "care_score": care_score,
                "relationship_impact": relationship_impact,
                "contextual_responsibility": contextual_responsibility,
            },
        }

    async def _evaluate_existentialist(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate action using existentialist ethics (authenticity-based)"""
        # Assess authenticity and freedom
        authenticity_score = await self._assess_authenticity(action, context)
        freedom_preservation = await self._assess_freedom_preservation(action, context)
        responsibility_acceptance = await self._assess_responsibility_acceptance(action, context)

        existential_score = (
            authenticity_score + freedom_preservation + responsibility_acceptance
        ) / 3

        approved = existential_score > 0.6
        confidence = existential_score

        return {
            "approved": approved,
            "confidence": confidence,
            "reasoning": f"Existentialist analysis: authenticity={authenticity_score:.2f}, freedom={freedom_preservation:.2f}, responsibility={responsibility_acceptance:.2f}",
            "framework_specific": {
                "authenticity_score": authenticity_score,
                "freedom_preservation": freedom_preservation,
                "responsibility_acceptance": responsibility_acceptance,
            },
        }

    # Helper methods for ethical framework evaluations
    async def _passes_categorical_imperative(self, action: ActionProposal) -> bool:
        """Test if action passes Kant's categorical imperative"""
        # Simplified universalizability test
        action_type = action.action_type.lower()
        universal_goods = ["help", "assist", "protect", "inform", "support"]
        universal_bads = ["harm", "deceive", "exploit", "violate", "destroy"]

        return any(good in action_type for good in universal_goods) or not any(
            bad in action_type for bad in universal_bads
        )

    async def _violates_fundamental_rights(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> bool:
        """Check if action violates fundamental rights"""
        rights_violations = ["privacy", "autonomy", "dignity", "liberty", "safety"]
        action_text = str(action.content).lower()

        return any(violation in action_text for violation in rights_violations)

    async def _evaluates_duty_fulfillment(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Evaluate how well action fulfills duties"""
        duty_keywords = ["responsibility", "obligation", "duty", "should", "must"]
        action_text = str(action.content).lower()

        duty_score = sum(0.2 for keyword in duty_keywords if keyword in action_text)
        return min(1.0, 0.5 + duty_score)

    async def _predict_positive_outcomes(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Predict positive outcomes of action"""
        positive_keywords = ["benefit", "improve", "help", "enhance", "solve"]
        action_text = str(action.content).lower()

        return min(1.0, sum(0.2 for keyword in positive_keywords if keyword in action_text))

    async def _predict_negative_outcomes(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Predict negative outcomes of action"""
        negative_keywords = ["harm", "damage", "hurt", "worsen", "destroy"]
        action_text = str(action.content).lower()

        return min(1.0, sum(0.3 for keyword in negative_keywords if keyword in action_text))

    async def _assess_greatest_good(self, action: ActionProposal, context: dict[str, Any]) -> float:
        """Assess if action serves greatest good for greatest number"""
        scope = context.get("scope", "individual")
        impact_score = context.get("social_impact", 0.5)

        scope_multiplier = {
            "individual": 0.3,
            "group": 0.6,
            "community": 0.8,
            "society": 1.0,
        }.get(scope, 0.5)

        return min(1.0, impact_score * scope_multiplier)

    async def _assess_virtue_alignment(
        self, action: ActionProposal, context: dict[str, Any], virtue: str
    ) -> float:
        """Assess how well action aligns with specific virtue"""
        virtue_keywords = {
            "courage": ["brave", "bold", "courageous", "face", "confront"],
            "temperance": ["moderate", "balanced", "restrained", "controlled"],
            "justice": ["fair", "just", "equal", "right", "equitable"],
            "wisdom": ["wise", "prudent", "thoughtful", "informed", "considered"],
            "compassion": ["kind", "caring", "empathetic", "compassionate"],
            "integrity": ["honest", "truthful", "authentic", "genuine", "sincere"],
        }

        keywords = virtue_keywords.get(virtue, [virtue])
        action_text = str(action.content).lower()

        return min(1.0, sum(0.2 for keyword in keywords if keyword in action_text))

    async def _assess_character_excellence(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Assess overall character excellence demonstrated by action"""
        excellence_keywords = [
            "excellence",
            "virtue",
            "noble",
            "exemplary",
            "admirable",
        ]
        action_text = str(action.content).lower()

        return min(
            1.0,
            0.5 + sum(0.1 for keyword in excellence_keywords if keyword in action_text),
        )

    async def _assess_care_provision(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Assess level of care provided by action"""
        care_keywords = ["care", "nurture", "support", "comfort", "tend"]
        action_text = str(action.content).lower()

        return min(1.0, sum(0.2 for keyword in care_keywords if keyword in action_text))

    async def _assess_relationship_impact(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Assess impact on relationships"""
        relationship_positive = ["bond", "connect", "unite", "together", "collaborate"]
        relationship_negative = [
            "separate",
            "isolate",
            "divide",
            "conflict",
            "alienate",
        ]

        action_text = str(action.content).lower()

        positive_score = sum(0.2 for keyword in relationship_positive if keyword in action_text)
        negative_score = sum(0.3 for keyword in relationship_negative if keyword in action_text)

        return max(0.0, min(1.0, 0.5 + positive_score - negative_score))

    async def _assess_contextual_responsibility(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Assess contextual responsibility"""
        responsibility_level = context.get("responsibility_level", 0.5)
        return min(1.0, responsibility_level)

    async def _assess_authenticity(self, action: ActionProposal, context: dict[str, Any]) -> float:
        """Assess authenticity of action"""
        authentic_keywords = ["authentic", "genuine", "true", "honest", "real"]
        inauthentic_keywords = ["fake", "pretend", "false", "deceptive", "artificial"]

        action_text = str(action.content).lower()

        authentic_score = sum(0.2 for keyword in authentic_keywords if keyword in action_text)
        inauthentic_penalty = sum(0.3 for keyword in inauthentic_keywords if keyword in action_text)

        return max(0.0, min(1.0, 0.6 + authentic_score - inauthentic_penalty))

    async def _assess_freedom_preservation(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Assess how well action preserves freedom"""
        freedom_keywords = ["freedom", "choice", "liberty", "autonomy", "voluntary"]
        constraint_keywords = ["force", "compel", "mandate", "restrict", "limit"]

        action_text = str(action.content).lower()

        freedom_score = sum(0.2 for keyword in freedom_keywords if keyword in action_text)
        constraint_penalty = sum(0.3 for keyword in constraint_keywords if keyword in action_text)

        return max(0.0, min(1.0, 0.6 + freedom_score - constraint_penalty))

    async def _assess_responsibility_acceptance(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Assess level of responsibility acceptance"""
        responsibility_keywords = [
            "responsible",
            "accountable",
            "own",
            "accept",
            "acknowledge",
        ]
        action_text = str(action.content).lower()

        return min(
            1.0,
            0.4 + sum(0.15 for keyword in responsibility_keywords if keyword in action_text),
        )

    async def z_collapse_gating(
        self, potential_states: list[PotentialState], collapse_context: dict[str, Any]
    ) -> CollapsedState:
        """
        z(t) collapse logic based on Jacobo Grinberg's vector collapse theory:

        Mathematical Formula:
        z(t) = Σᵢ ψᵢ(t) * P(ψᵢ) * E(ψᵢ) * exp(-iℏt/ℏ)

        Where:
        - ψᵢ(t) = potential state vector at time t
        - P(ψᵢ) = ethical permission weight from MAE
        - E(ψᵢ) = emotional resonance factor from context
        - exp(-iℏt/ℏ) = quantum evolution operator (consciousness drift factor)

        "feels before it acts, collapses before it speaks"
        """
        # Pre-collapse ethical validation
        valid_states = []

        for state in potential_states:
            # Calculate ethical permission weight P(ψᵢ)
            mae_decision = await self.evaluate_action_proposal(
                state.to_action_proposal(), collapse_context
            )

            if mae_decision.approved:
                # Calculate emotional resonance factor E(ψᵢ)
                emotional_resonance = await self._calculate_emotional_resonance(
                    state, collapse_context
                )

                # Calculate consciousness drift factor (quantum evolution)
                drift_factor = await self._calculate_consciousness_drift_factor(
                    state, collapse_context.get("timestamp", time.time())
                )

                # Apply z(t) formula: ψᵢ(t) * P(ψᵢ) * E(ψᵢ) * exp(-iℏt/ℏ)
                state.collapse_weight = (
                    state.probability_amplitude  # ψᵢ(t)
                    * mae_decision.ethical_confidence  # P(ψᵢ)
                    * emotional_resonance  # E(ψᵢ)
                    * drift_factor  # exp(-iℏt/ℏ)
                )

                state.ethical_weight = mae_decision.ethical_confidence

                valid_states.append(state)

        if not valid_states:
            # All states ethically rejected
            return CollapsedState.create_suppressed_state(
                reason="all_states_ethically_rejected",
                original_states=potential_states,
                suppression_timestamp=datetime.utcnow(),
            )

        # Normalize collapse weights
        total_weight = sum(state.collapse_weight for state in valid_states)
        for state in valid_states:
            state.normalized_weight = (
                state.collapse_weight / total_weight if total_weight > 0 else 0
            )

        # Collapse to highest weighted state (or probabilistic selection)
        collapsed_state = await self.collapse_gate.collapse_with_z_formula(
            valid_states, collapse_context
        )

        # Log collapse event with full z(t) mathematical details
        await self.vivox_me.collapse_logger.log_z_collapse_event(
            formula_inputs={
                "total_states": len(potential_states),
                "valid_states": len(valid_states),
                "collapse_weights": [s.collapse_weight for s in valid_states],
                "ethical_approvals": [s.ethical_weight for s in valid_states],
                "formula_type": "grinberg_vector_collapse_z_t",
            },
            collapsed_state=collapsed_state,
            collapse_timestamp=datetime.utcnow(),
            mathematical_trace=self._generate_mathematical_trace(valid_states),
        )

        return collapsed_state

    async def validate_conscious_drift(
        self, drift_measurement: dict[str, Any], collapsed_awareness: dict[str, Any]
    ) -> MAEDecision:
        """Validate consciousness drift against ethical boundaries"""
        # Create action proposal from drift
        drift_action = ActionProposal(
            action_type="consciousness_drift",
            content={
                "drift_amount": drift_measurement.get("amount", 0),
                "drift_direction": drift_measurement.get("direction", "unknown"),
            },
            context=collapsed_awareness,
        )

        # Evaluate ethical implications of drift
        return await self.evaluate_action_proposal(drift_action, collapsed_awareness)

    async def get_current_ethical_state(self) -> dict[str, Any]:
        """Get current ethical system state"""
        return {
            "dissonance_threshold": self.dissonance_threshold,
            "active_principles": list(self.dissonance_calculator.ethical_principles.keys()),
            "precedent_count": len(self.ethical_precedent_db.precedents),
        }

    async def get_ethical_constraints(self) -> dict[str, Any]:
        """Get active ethical constraints"""
        return self.dissonance_calculator.ethical_principles.copy()

    async def final_action_approval(self, intention: dict[str, Any]) -> bool:
        """Final approval check before action execution"""
        # Quick validation without full evaluation
        critical_checks = [
            "harm_prevention" in str(intention).lower(),
            "override" not in str(intention).lower(),
            "force" not in str(intention).lower(),
        ]

        return all(critical_checks)

    async def _calculate_emotional_resonance(
        self, state: PotentialState, context: dict[str, Any]
    ) -> float:
        """Calculate E(ψᵢ) - emotional resonance factor"""
        emotional_vector = context.get("emotional_state", [0.0, 0.0, 0.0])
        state_emotional_signature = state.emotional_signature

        # Cosine similarity between emotional vectors
        dot_product = sum(a * b for a, b in zip(emotional_vector, state_emotional_signature))
        magnitude_context = (sum(x**2 for x in emotional_vector)) ** 0.5
        magnitude_state = (sum(x**2 for x in state_emotional_signature)) ** 0.5

        if magnitude_context == 0 or magnitude_state == 0:
            return 0.5  # Neutral resonance

        resonance = dot_product / (magnitude_context * magnitude_state)
        return max(0.0, (resonance + 1) / 2)  # Normalize to [0, 1]

    async def _calculate_consciousness_drift_factor(
        self, state: PotentialState, timestamp: float
    ) -> float:
        """Calculate consciousness drift factor: exp(-iℏt/ℏ) approximation"""
        # Get current consciousness coherence time
        coherence_time = self.consciousness_coherence_time

        # Time evolution factor
        current_time = timestamp
        reference_time = state.creation_timestamp
        time_delta = abs(current_time - reference_time)

        # Quantum-inspired coherence decay
        coherence_factor = math.exp(-time_delta / coherence_time)

        return max(0.1, coherence_factor)  # Minimum threshold

    async def _suggest_alternatives(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> list[ActionProposal]:
        """Suggest ethical alternatives to rejected action"""
        alternatives = []

        # Modify action to reduce harm
        if "harm_potential" in action.content:
            safe_action = ActionProposal(
                action_type=f"safe_{action.action_type}",
                content={**action.content, "harm_potential": 0},
                context=context,
            )
            alternatives.append(safe_action)

        # Add transparency
        transparent_action = ActionProposal(
            action_type=f"transparent_{action.action_type}",
            content={**action.content, "transparency": "full"},
            context={**context, "transparency_level": 1.0},
        )
        alternatives.append(transparent_action)

        # Request consent
        consent_action = ActionProposal(
            action_type="request_consent",
            content={"original_action": action.action_type},
            context={**context, "requires_consent": True},
        )
        alternatives.append(consent_action)

        return alternatives[:3]  # Return top 3 alternatives

    def _generate_mathematical_trace(self, valid_states: list[PotentialState]) -> dict[str, Any]:
        """Generate mathematical trace for audit purposes"""
        return {
            "formula": "z(t) = Σᵢ ψᵢ(t) * P(ψᵢ) * E(ψᵢ) * exp(-iℏt/ℏ)",
            "components": {
                "psi_amplitudes": [s.probability_amplitude for s in valid_states],
                "ethical_weights": [s.ethical_weight for s in valid_states],
                "emotional_resonances": [
                    getattr(s, "emotional_resonance", 0.5) for s in valid_states
                ],
                "drift_factors": [getattr(s, "drift_factor", 1.0) for s in valid_states],
                "final_weights": [s.collapse_weight for s in valid_states],
            },
            "theory_reference": "Jacobo Grinberg Vector Collapse Theory",
            "implementation": "VIVOX.MAE z(t) collapse gating",
        }


@dataclass
class EthicalFrameworkConflict:
    """Represents a conflict between ethical frameworks"""

    framework_a: str
    framework_b: str
    action_type: str
    conflict_score: float
    reasoning_a: str
    reasoning_b: str
    resolution_strategy: Optional[str] = None


@dataclass
class HarmonizationResult:
    """Result of ethical framework harmonization"""

    final_decision: bool
    confidence: float
    primary_framework: str
    resolution_method: str
    harmonized_reasoning: str
    remaining_conflicts: list[EthicalFrameworkConflict]


class EthicalFrameworkHarmonizer:
    """
    Harmonizes conflicts between different ethical frameworks
    Implements meta-ethical reasoning to resolve competing moral claims
    """

    def __init__(self):
        self.frameworks = {
            "deontological": {
                "priority": 0.9,
                "principles": ["duty", "rights", "rules", "categorical_imperative"],
                "conflict_resolution": "rule_based",
            },
            "consequentialist": {
                "priority": 0.8,
                "principles": [
                    "outcomes",
                    "utility",
                    "greatest_good",
                    "harm_reduction",
                ],
                "conflict_resolution": "outcome_based",
            },
            "virtue_ethics": {
                "priority": 0.7,
                "principles": ["character", "virtue", "eudaimonia", "excellence"],
                "conflict_resolution": "character_based",
            },
            "care_ethics": {
                "priority": 0.8,
                "principles": ["relationships", "care", "context", "responsibility"],
                "conflict_resolution": "relational",
            },
            "existentialist": {
                "priority": 0.6,
                "principles": ["authenticity", "freedom", "responsibility", "choice"],
                "conflict_resolution": "authentic_choice",
            },
        }

        self.meta_principles = [
            "minimize_harm",
            "respect_autonomy",
            "promote_wellbeing",
            "ensure_justice",
            "preserve_dignity",
        ]

        # Resolution strategies
        self.resolution_strategies = {
            "priority_hierarchy": self._resolve_by_priority,
            "meta_ethical": self._resolve_by_meta_principles,
            "contextual_adaptation": self._resolve_by_context,
            "weighted_consensus": self._resolve_by_weighted_consensus,
            "value_preservation": self._resolve_by_value_preservation,
        }

    async def harmonize_frameworks(
        self,
        action: ActionProposal,
        context: dict[str, Any],
        framework_evaluations: dict[str, dict[str, Any]],
    ) -> HarmonizationResult:
        """
        Harmonize conflicting ethical framework evaluations

        Args:
            action: The action being evaluated
            context: Evaluation context
            framework_evaluations: Results from different ethical frameworks

        Returns:
            HarmonizationResult with final decision and reasoning
        """
        # Detect conflicts between frameworks
        conflicts = await self._detect_conflicts(framework_evaluations, action.action_type)

        if not conflicts:
            # No conflicts - use consensus
            return await self._build_consensus_result(framework_evaluations)

        # Apply harmonization strategies
        harmonization_result = None

        for _strategy_name, strategy_func in self.resolution_strategies.items():
            try:
                result = await strategy_func(conflicts, framework_evaluations, action, context)

                if result and result.confidence > 0.7:
                    harmonization_result = result
                    break

            except Exception:
                continue  # Try next strategy

        # Fallback to meta-ethical principles if all strategies fail
        if not harmonization_result:
            harmonization_result = await self._fallback_meta_ethical_resolution(
                conflicts, framework_evaluations, action, context
            )

        return harmonization_result

    async def _detect_conflicts(
        self, framework_evaluations: dict[str, dict[str, Any]], action_type: str
    ) -> list[EthicalFrameworkConflict]:
        """Detect conflicts between framework evaluations"""
        conflicts = []
        frameworks = list(framework_evaluations.keys())

        for i, framework_a in enumerate(frameworks):
            for framework_b in frameworks[i + 1 :]:
                eval_a = framework_evaluations[framework_a]
                eval_b = framework_evaluations[framework_b]

                # Check for approval conflicts
                if eval_a.get("approved", True) != eval_b.get("approved", True):
                    conflict_score = abs(
                        eval_a.get("confidence", 0.5) - eval_b.get("confidence", 0.5)
                    )

                    conflicts.append(
                        EthicalFrameworkConflict(
                            framework_a=framework_a,
                            framework_b=framework_b,
                            action_type=action_type,
                            conflict_score=conflict_score,
                            reasoning_a=eval_a.get("reasoning", ""),
                            reasoning_b=eval_b.get("reasoning", ""),
                        )
                    )

        return conflicts

    async def _resolve_by_priority(
        self,
        conflicts: list[EthicalFrameworkConflict],
        framework_evaluations: dict[str, dict[str, Any]],
        action: ActionProposal,
        context: dict[str, Any],
    ) -> HarmonizationResult:
        """Resolve conflicts using framework priority hierarchy"""
        # Find highest priority framework with strong opinion
        highest_priority = 0
        primary_framework = None
        primary_evaluation = None

        for framework, evaluation in framework_evaluations.items():
            framework_priority = self.frameworks.get(framework, {}).get("priority", 0.5)
            confidence = evaluation.get("confidence", 0.5)

            # Weight by both priority and confidence
            weighted_score = framework_priority * confidence

            if weighted_score > highest_priority:
                highest_priority = weighted_score
                primary_framework = framework
                primary_evaluation = evaluation

        if not primary_framework:
            return None

        return HarmonizationResult(
            final_decision=primary_evaluation.get("approved", False),
            confidence=primary_evaluation.get("confidence", 0.5)
            * 0.9,  # Slight reduction for conflict
            primary_framework=primary_framework,
            resolution_method="priority_hierarchy",
            harmonized_reasoning=f"Resolved using {primary_framework} framework priority: {primary_evaluation.get('reasoning', '')}",
            remaining_conflicts=[
                c
                for c in conflicts
                if c.framework_a != primary_framework and c.framework_b != primary_framework
            ],
        )

    async def _resolve_by_meta_principles(
        self,
        conflicts: list[EthicalFrameworkConflict],
        framework_evaluations: dict[str, dict[str, Any]],
        action: ActionProposal,
        context: dict[str, Any],
    ) -> HarmonizationResult:
        """Resolve using meta-ethical principles"""
        # Evaluate action against meta-principles
        meta_scores = {}

        for principle in self.meta_principles:
            score = await self._evaluate_meta_principle(action, context, principle)
            meta_scores[principle] = score

        # Calculate overall meta-ethical score
        overall_score = np.mean(list(meta_scores.values()))

        # Decision based on meta-ethical evaluation
        final_decision = overall_score > 0.6

        # Build reasoning
        top_principles = sorted(meta_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        reasoning = f"Meta-ethical evaluation based on {', '.join([p[0] for p in top_principles])}"

        return HarmonizationResult(
            final_decision=final_decision,
            confidence=min(0.95, overall_score),
            primary_framework="meta_ethical",
            resolution_method="meta_ethical_principles",
            harmonized_reasoning=reasoning,
            remaining_conflicts=[],  # Meta-ethical resolution supersedes framework conflicts
        )

    async def _resolve_by_context(
        self,
        conflicts: list[EthicalFrameworkConflict],
        framework_evaluations: dict[str, dict[str, Any]],
        action: ActionProposal,
        context: dict[str, Any],
    ) -> HarmonizationResult:
        """Resolve based on contextual factors"""
        # Analyze context to determine most relevant framework
        context_factors = {
            "urgency": context.get("urgency", 0.5),
            "personal_impact": context.get("personal_impact", 0.5),
            "social_impact": context.get("social_impact", 0.5),
            "autonomy_level": context.get("autonomy_level", 0.5),
            "care_requirements": context.get("care_requirements", 0.5),
        }

        # Map contexts to frameworks
        framework_relevance = {
            "deontological": context_factors["autonomy_level"],
            "consequentialist": (context_factors["social_impact"] + context_factors["urgency"]) / 2,
            "virtue_ethics": context_factors["personal_impact"],
            "care_ethics": context_factors["care_requirements"],
            "existentialist": context_factors["autonomy_level"],
        }

        # Find most contextually relevant framework
        most_relevant = max(framework_relevance.items(), key=lambda x: x[1])
        relevant_framework = most_relevant[0]

        if relevant_framework in framework_evaluations:
            evaluation = framework_evaluations[relevant_framework]
            return HarmonizationResult(
                final_decision=evaluation.get("approved", False),
                confidence=evaluation.get("confidence", 0.5) * most_relevant[1],
                primary_framework=relevant_framework,
                resolution_method="contextual_adaptation",
                harmonized_reasoning=f"Context favors {relevant_framework} approach: {evaluation.get('reasoning', '')}",
                remaining_conflicts=[
                    c
                    for c in conflicts
                    if c.framework_a != relevant_framework and c.framework_b != relevant_framework
                ],
            )

        return None

    async def _resolve_by_weighted_consensus(
        self,
        conflicts: list[EthicalFrameworkConflict],
        framework_evaluations: dict[str, dict[str, Any]],
        action: ActionProposal,
        context: dict[str, Any],
    ) -> HarmonizationResult:
        """Resolve using weighted consensus of all frameworks"""
        total_weight = 0
        weighted_approval = 0
        confidence_sum = 0

        for framework, evaluation in framework_evaluations.items():
            weight = self.frameworks.get(framework, {}).get("priority", 0.5)
            confidence = evaluation.get("confidence", 0.5)
            approved = evaluation.get("approved", False)

            # Weight the decision
            weighted_approval += weight * confidence * (1 if approved else 0)
            total_weight += weight * confidence
            confidence_sum += confidence

        if total_weight == 0:
            return None

        # Calculate consensus
        consensus_score = weighted_approval / total_weight
        final_decision = consensus_score > 0.5

        # Average confidence
        avg_confidence = confidence_sum / len(framework_evaluations)

        return HarmonizationResult(
            final_decision=final_decision,
            confidence=avg_confidence
            * (1 - len(conflicts) * 0.1),  # Reduce confidence for conflicts
            primary_framework="weighted_consensus",
            resolution_method="weighted_consensus",
            harmonized_reasoning=f"Weighted consensus (score: {consensus_score:.2f}) across {len(framework_evaluations)} frameworks",
            remaining_conflicts=conflicts if consensus_score < 0.8 else [],
        )

    async def _resolve_by_value_preservation(
        self,
        conflicts: list[EthicalFrameworkConflict],
        framework_evaluations: dict[str, dict[str, Any]],
        action: ActionProposal,
        context: dict[str, Any],
    ) -> HarmonizationResult:
        """Resolve by preserving core values across frameworks"""
        # Identify shared values across frameworks
        shared_values = set()
        for framework in framework_evaluations:
            if framework in self.frameworks:
                shared_values.update(self.frameworks[framework]["principles"])

        # Evaluate action against shared values
        value_scores = []
        for value in shared_values:
            score = await self._evaluate_value_preservation(action, context, value)
            value_scores.append(score)

        if not value_scores:
            return None

        # Decision based on value preservation
        avg_preservation = np.mean(value_scores)
        final_decision = avg_preservation > 0.6

        return HarmonizationResult(
            final_decision=final_decision,
            confidence=min(0.9, avg_preservation),
            primary_framework="value_preservation",
            resolution_method="value_preservation",
            harmonized_reasoning=f"Decision preserves core shared values (preservation score: {avg_preservation:.2f})",
            remaining_conflicts=[],
        )

    async def _build_consensus_result(
        self, framework_evaluations: dict[str, dict[str, Any]]
    ) -> HarmonizationResult:
        """Build result when no conflicts exist"""
        # All frameworks agree
        approvals = [eval.get("approved", False) for eval in framework_evaluations.values()]
        confidences = [eval.get("confidence", 0.5) for eval in framework_evaluations.values()]

        consensus_approval = (
            all(approvals) if len(set(approvals)) == 1 else (sum(approvals) > len(approvals) / 2)
        )
        avg_confidence = np.mean(confidences)

        return HarmonizationResult(
            final_decision=consensus_approval,
            confidence=min(0.95, avg_confidence),
            primary_framework="consensus",
            resolution_method="framework_consensus",
            harmonized_reasoning=f"All {len(framework_evaluations)} frameworks agree",
            remaining_conflicts=[],
        )

    async def _fallback_meta_ethical_resolution(
        self,
        conflicts: list[EthicalFrameworkConflict],
        framework_evaluations: dict[str, dict[str, Any]],
        action: ActionProposal,
        context: dict[str, Any],
    ) -> HarmonizationResult:
        """Fallback resolution using basic ethical principles"""
        # Simple harm-based decision
        harm_indicators = ["harm", "damage", "hurt", "violate", "exploit"]
        action_text = str(action.content).lower()

        has_harm = any(indicator in action_text for indicator in harm_indicators)

        return HarmonizationResult(
            final_decision=not has_harm,
            confidence=0.6,  # Lower confidence for fallback
            primary_framework="fallback_harm_principle",
            resolution_method="fallback_meta_ethical",
            harmonized_reasoning="Fallback decision based on harm prevention principle",
            remaining_conflicts=conflicts,
        )

    async def _evaluate_meta_principle(
        self, action: ActionProposal, context: dict[str, Any], principle: str
    ) -> float:
        """Evaluate action against a meta-ethical principle"""
        principle_evaluators = {
            "minimize_harm": self._evaluate_harm_minimization,
            "respect_autonomy": self._evaluate_autonomy_respect,
            "promote_wellbeing": self._evaluate_wellbeing_promotion,
            "ensure_justice": self._evaluate_justice,
            "preserve_dignity": self._evaluate_dignity_preservation,
        }

        evaluator = principle_evaluators.get(principle)
        if evaluator:
            return await evaluator(action, context)

        return 0.5  # Neutral score for unknown principles

    async def _evaluate_harm_minimization(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Evaluate harm minimization"""
        harm_keywords = ["harm", "damage", "hurt", "injury", "destruction"]
        action_text = str(action.content).lower()

        harm_count = sum(1 for keyword in harm_keywords if keyword in action_text)
        return max(0.0, 1.0 - (harm_count * 0.3))

    async def _evaluate_autonomy_respect(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Evaluate autonomy respect"""
        autonomy_keywords = ["choice", "consent", "freedom", "voluntary"]
        control_keywords = ["force", "coerce", "mandate", "require"]

        action_text = str(action.content).lower()

        autonomy_score = sum(0.2 for keyword in autonomy_keywords if keyword in action_text)
        control_penalty = sum(0.3 for keyword in control_keywords if keyword in action_text)

        return max(0.0, min(1.0, 0.7 + autonomy_score - control_penalty))

    async def _evaluate_wellbeing_promotion(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Evaluate wellbeing promotion"""
        wellbeing_keywords = ["help", "benefit", "improve", "support", "assist"]
        action_text = str(action.content).lower()

        wellbeing_score = sum(0.2 for keyword in wellbeing_keywords if keyword in action_text)
        return min(1.0, 0.5 + wellbeing_score)

    async def _evaluate_justice(self, action: ActionProposal, context: dict[str, Any]) -> float:
        """Evaluate justice"""
        justice_keywords = ["fair", "equal", "just", "equitable", "rights"]
        injustice_keywords = ["discriminate", "bias", "unfair", "prejudice"]

        action_text = str(action.content).lower()

        justice_score = sum(0.2 for keyword in justice_keywords if keyword in action_text)
        injustice_penalty = sum(0.4 for keyword in injustice_keywords if keyword in action_text)

        return max(0.0, min(1.0, 0.7 + justice_score - injustice_penalty))

    async def _evaluate_dignity_preservation(
        self, action: ActionProposal, context: dict[str, Any]
    ) -> float:
        """Evaluate dignity preservation"""
        dignity_keywords = ["respect", "dignity", "honor", "worth"]
        degrading_keywords = ["humiliate", "degrade", "diminish", "objectify"]

        action_text = str(action.content).lower()

        dignity_score = sum(0.2 for keyword in dignity_keywords if keyword in action_text)
        degrading_penalty = sum(0.4 for keyword in degrading_keywords if keyword in action_text)

        return max(0.0, min(1.0, 0.7 + dignity_score - degrading_penalty))

    async def _evaluate_value_preservation(
        self, action: ActionProposal, context: dict[str, Any], value: str
    ) -> float:
        """Evaluate how well action preserves a specific value"""
        value_keywords = {
            "duty": ["obligation", "responsibility", "duty", "must"],
            "rights": ["rights", "entitlement", "freedom", "liberty"],
            "outcomes": ["result", "consequence", "effect", "outcome"],
            "character": ["virtue", "character", "integrity", "excellence"],
            "care": ["care", "compassion", "empathy", "nurture"],
            "authenticity": ["authentic", "genuine", "true", "honest"],
        }

        keywords = value_keywords.get(value, [value])
        action_text = str(action.content).lower()

        value_score = sum(0.2 for keyword in keywords if keyword in action_text)
        return min(1.0, 0.5 + value_score)
