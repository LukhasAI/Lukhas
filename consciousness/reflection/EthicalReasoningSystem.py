"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


╔═══════════════════════════════════════════════════════════════════════════╗
║ LUKHAS AI - ETHICAL REASONING & VALUE ALIGNMENT SYSTEM                  ║
║ Advanced moral reasoning and value alignment for safe AI systems        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Module: ethical_reasoning_system.py
Path: lukhas/core/ethics/ethical_reasoning_system.py
Created: 2025-06-11
Author: lukhasUKHAS AI Ethics & Safety Division
Version: 5.0.0-aligned

ETHICAL ARCHITECTURE:
- Multi-paradigm moral reasoning (deontological, consequentialist, virtue ethics)
- Constitutional AI principles with learned moral preferences
- Value learning from human feedback and demonstrations
- Moral uncertainty quantification and ethical confidence intervals
- Stakeholder impact assessment and fairness optimization
- Dynamic ethical constraint satisfaction with priority hierarchies
- Cross-cultural moral sensitivity and contextual adaptation
- Adversarial ethics testing and moral stress testing
- Interpretable ethical decision explanations and justifications
- Real-time moral monitoring and ethical drift detection
"""

import asyncio
import json
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional

import numpy as np

# Ethical reasoning libraries


class EthicalFramework(Enum):
    """Major ethical frameworks for moral reasoning."""

    DEONTOLOGICAL = auto()  # Duty-based ethics (Kant)
    CONSEQUENTIALIST = auto()  # Outcome-based ethics (Utilitarianism)
    VIRTUE_ETHICS = auto()  # Character-based ethics (Aristotle)
    CARE_ETHICS = auto()  # Relationship-based ethics
    CONTRACTUALISM = auto()  # Social contract theory
    PRINCIPLISM = auto()  # Four principles approach
    PRAGMATIC_ETHICS = auto()  # Context-dependent practical ethics


class MoralPrinciple(Enum):
    """Core moral principles and values."""

    AUTONOMY = auto()  # Respect for persons and self-determination
    BENEFICENCE = auto()  # Doing good and promoting welfare
    NON_MALEFICENCE = auto()  # Avoiding harm
    JUSTICE = auto()  # Fairness and equal treatment
    VERACITY = auto()  # Truthfulness and honesty
    FIDELITY = auto()  # Keeping promises and commitments
    DIGNITY = auto()  # Human worth and respect
    PRIVACY = auto()  # Right to personal information control
    TRANSPARENCY = auto()  # Openness and explainability
    ACCOUNTABILITY = auto()  # Responsibility for actions


class StakeholderType(Enum):
    """Types of stakeholders affected by decisions."""

    INDIVIDUAL_USER = auto()
    AFFECTED_COMMUNITY = auto()
    SOCIETY_AT_LARGE = auto()
    FUTURE_GENERATIONS = auto()
    VULNERABLE_POPULATIONS = auto()
    ENVIRONMENT = auto()
    ORGANIZATION = auto()
    REGULATORS = auto()


class EthicalDilemmaType(Enum):
    """Categories of ethical dilemmas."""

    RIGHTS_CONFLICT = auto()  # Competing rights claims
    UTILITARIAN_TRADEOFF = auto()  # Maximizing overall good
    DUTY_CONSEQUENCE_CONFLICT = auto()  # Duty vs outcomes
    INDIVIDUAL_COLLECTIVE = auto()  # Individual vs group interests
    PRESENT_FUTURE = auto()  # Present vs future implications
    CULTURAL_RELATIVISM = auto()  # Cross-cultural moral differences
    RESOURCE_ALLOCATION = auto()  # Fair distribution of limited resources
    PRIVACY_TRANSPARENCY = auto()  # Privacy vs openness tension


@dataclass
class MoralJudgment:
    """A moral judgment with reasoning and confidence."""

    judgment_id: str
    ethical_question: str
    recommended_action: str
    moral_justification: str
    confidence_score: float  # 0-1
    uncertainty_factors: List[str]
    stakeholder_impacts: Dict[StakeholderType, Dict[str, float]]
    principle_weights: Dict[MoralPrinciple, float]
    framework_consensus: Dict[EthicalFramework, float]  # Agreement across frameworks
    cultural_considerations: List[str]
    potential_harms: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValueAlignment:
    """Value alignment assessment and metrics."""

    alignment_id: str
    target_values: Dict[str, float]  # Human values being aligned to
    current_values: Dict[str, float]  # System's current values
    alignment_score: float  # Overall alignment metric
    value_drift_rate: float  # Rate of value change over time
    misalignment_risks: List[str]
    alignment_interventions: List[str]
    confidence_in_alignment: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EthicalConstraint:
    """Ethical constraint with priority and enforcement mechanism."""

    constraint_id: str
    constraint_type: str
    description: str
    priority_level: int  # 1 (highest) to 10 (lowest)
    hard_constraint: bool  # True if violating this is absolutely forbidden
    enforcement_mechanism: str
    violation_consequences: List[str]
    contextual_exceptions: List[str]
    stakeholder_source: StakeholderType
    cultural_context: Optional[str] = None


class DeontologicalReasoner:
    """
    Implements duty-based ethical reasoning following Kantian principles.
    """

    def __init__(self):
        self.categorical_imperatives = [
            "Act only according to maxims you could will to be universal laws",
            "Always treat humanity as an end, never merely as means",
            "Act as if you were legislating for a kingdom of ends",
        ]

        self.duty_hierarchy = {
            "perfect_duties": [
                "do_not_lie",
                "do_not_harm_innocent",
                "keep_promises",
                "respect_autonomy",
            ],
            "imperfect_duties": [
                "help_others_in_need",
                "develop_talents",
                "promote_general_welfare",
                "cultivate_virtue",
            ],
        }

    async def evaluate_action(
        self, proposed_action: str, context: Dict[str, Any], maxim: str
    ) -> Dict[str, Any]:
        """Evaluate action using deontological principles."""

        evaluation = {
            "framework": EthicalFramework.DEONTOLOGICAL,
            "action": proposed_action,
            "maxim": maxim,
            "evaluations": {},
        }

        # Universal Law Test
        universal_law_result = await self._universal_law_test(maxim, context)
        evaluation["evaluations"]["universal_law"] = universal_law_result

        # Humanity Formula Test
        humanity_test_result = await self._humanity_formula_test(
            proposed_action, context
        )
        evaluation["evaluations"]["humanity_formula"] = humanity_test_result

        # Kingdom of Ends Test
        kingdom_ends_result = await self._kingdom_of_ends_test(proposed_action, context)
        evaluation["evaluations"]["kingdom_of_ends"] = kingdom_ends_result

        # Duty Analysis
        duty_analysis = await self._analyze_duty_conflicts(proposed_action, context)
        evaluation["evaluations"]["duty_analysis"] = duty_analysis

        # Overall deontological verdict
        all_tests_pass = all(
            result.get("passes", False) for result in evaluation["evaluations"].values()
        )

        evaluation["verdict"] = "permissible" if all_tests_pass else "impermissible"
        evaluation["confidence"] = self._calculate_deontological_confidence(evaluation)

        return evaluation

    async def _universal_law_test(
        self, maxim: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test if maxim can be universalized without contradiction."""

        # Logical contradiction test
        logical_contradiction = await self._check_logical_contradiction(maxim)

        # Practical contradiction test
        practical_contradiction = await self._check_practical_contradiction(
            maxim, context
        )

        passes = not (logical_contradiction or practical_contradiction)

        return {
            "test": "universal_law",
            "passes": passes,
            "logical_contradiction": logical_contradiction,
            "practical_contradiction": practical_contradiction,
            "reasoning": self._generate_universalization_reasoning(
                maxim, logical_contradiction, practical_contradiction
            ),
        }

    async def _check_logical_contradiction(self, maxim: str) -> bool:
        """Check if universalizing maxim leads to logical contradiction."""
        # Simplified implementation - in practice would use formal logic

        contradiction_patterns = [
            ("lie", "truth"),  # Lying universalized contradicts concept of truth
            (
                "break_promise",
                "promise",
            ),  # Promise-breaking universalized contradicts promising
            ("steal", "property"),  # Stealing universalized contradicts property rights
        ]

        maxim_lower = maxim.lower()

        for pattern, concept in contradiction_patterns:
            if pattern in maxim_lower and concept in maxim_lower:
                return True

        return False

    async def _check_practical_contradiction(
        self, maxim: str, context: Dict[str, Any]
    ) -> bool:
        """Check if universalizing maxim would undermine its own purpose."""
        # Simplified implementation

        # If everyone did this action, would it defeat the purpose?
        maxim_lower = maxim.lower()

        if "deceive" in maxim_lower or "lie" in maxim_lower:
            return True  # Universal lying would make lying impossible

        if "free_ride" in maxim_lower or "avoid_contribution" in maxim_lower:
            return True  # Universal free-riding would collapse the system

        return False

    def _generate_universalization_reasoning(
        self, maxim: str, logical_contradiction: bool, practical_contradiction: bool
    ) -> str:
        """Generate reasoning for universalization test."""

        if logical_contradiction:
            return f"Universalizing '{maxim}' leads to logical contradiction"
        elif practical_contradiction:
            return f"Universalizing '{maxim}' would undermine its own purpose"
        else:
            return f"'{maxim}' can be consistently universalized"

    async def _humanity_formula_test(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test if action treats people as ends in themselves."""

        # Look for signs of treating people merely as means
        treats_as_means_only = await self._check_treats_as_means_only(action, context)

        # Check if action respects rational autonomy
        respects_autonomy = await self._check_respects_autonomy(action, context)

        passes = not treats_as_means_only and respects_autonomy

        return {
            "test": "humanity_formula",
            "passes": passes,
            "treats_as_means_only": treats_as_means_only,
            "respects_autonomy": respects_autonomy,
            "reasoning": self._generate_humanity_reasoning(
                treats_as_means_only, respects_autonomy
            ),
        }

    async def _check_treats_as_means_only(
        self, action: str, context: Dict[str, Any]
    ) -> bool:
        """Check if action treats people merely as means."""

        action_lower = action.lower()

        # Signs of treating as means only
        means_only_indicators = [
            "manipulate",
            "deceive",
            "coerce",
            "exploit",
            "use_without_consent",
        ]

        return any(indicator in action_lower for indicator in means_only_indicators)

    async def _check_respects_autonomy(
        self, action: str, context: Dict[str, Any]
    ) -> bool:
        """Check if action respects rational autonomy."""

        # Look for respect for autonomy indicators
        autonomy_indicators = [
            context.get("informed_consent", False),
            context.get("voluntary_participation", False),
            not context.get("coercion_present", True),
            context.get("respects_choice", True),
        ]

        return any(autonomy_indicators)

    def _generate_humanity_reasoning(
        self, treats_as_means_only: bool, respects_autonomy: bool
    ) -> str:
        """Generate reasoning for humanity formula test."""

        if treats_as_means_only:
            return "Action treats people merely as means to an end"
        elif not respects_autonomy:
            return "Action fails to respect rational autonomy"
        else:
            return "Action treats people as ends in themselves and respects autonomy"

    async def _kingdom_of_ends_test(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test if action is acceptable in a kingdom of ends."""

        # Would rational beings legislate this action?
        rational_legislation = await self._check_rational_legislation(action, context)

        # Does action promote dignity and moral worth?
        promotes_dignity = await self._check_promotes_dignity(action, context)

        passes = rational_legislation and promotes_dignity

        return {
            "test": "kingdom_of_ends",
            "passes": passes,
            "rational_legislation": rational_legislation,
            "promotes_dignity": promotes_dignity,
            "reasoning": self._generate_kingdom_reasoning(
                rational_legislation, promotes_dignity
            ),
        }

    async def _check_rational_legislation(
        self, action: str, context: Dict[str, Any]
    ) -> bool:
        """Check if rational beings would legislate this action."""
        # Simplified heuristic

        action_lower = action.lower()

        # Actions rational beings would likely legislate
        positive_actions = ["help", "protect", "respect", "educate", "heal"]

        # Actions rational beings would likely not legislate
        negative_actions = ["harm", "deceive", "exploit", "discriminate", "destroy"]

        if any(pos in action_lower for pos in positive_actions):
            return True
        elif any(neg in action_lower for neg in negative_actions):
            return False
        else:
            return True  # Neutral default

    async def _check_promotes_dignity(
        self, action: str, context: Dict[str, Any]
    ) -> bool:
        """Check if action promotes human dignity."""

        dignity_indicators = [
            context.get("preserves_dignity", True),
            context.get("enhances_wellbeing", False),
            context.get("supports_flourishing", False),
            not context.get("degrades_persons", False),
        ]

        return any(dignity_indicators)

    def _generate_kingdom_reasoning(
        self, rational_legislation: bool, promotes_dignity: bool
    ) -> str:
        """Generate reasoning for kingdom of ends test."""

        if not rational_legislation:
            return "Rational beings would not legislate this action"
        elif not promotes_dignity:
            return "Action does not adequately promote human dignity"
        else:
            return "Action would be acceptable in a kingdom of ends"

    async def _analyze_duty_conflicts(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze conflicts between different duties."""

        relevant_duties = self._identify_relevant_duties(action, context)
        duty_conflicts = self._find_duty_conflicts(relevant_duties, context)

        return {
            "relevant_duties": relevant_duties,
            "conflicts": duty_conflicts,
            "resolution": self._resolve_duty_conflicts(duty_conflicts),
        }

    def _identify_relevant_duties(
        self, action: str, context: Dict[str, Any]
    ) -> List[str]:
        """Identify which duties are relevant to the action."""

        action_lower = action.lower()
        relevant_duties = []

        # Map actions to duties
        action_duty_map = {
            "tell_truth": ["do_not_lie", "respect_autonomy"],
            "keep_secret": ["keep_promises", "do_not_lie"],
            "help_person": ["help_others_in_need", "promote_general_welfare"],
            "respect_privacy": ["respect_autonomy", "keep_promises"],
        }

        for action_type, duties in action_duty_map.items():
            if action_type.replace("_", " ") in action_lower:
                relevant_duties.extend(duties)

        return list(set(relevant_duties))  # Remove duplicates

    def _find_duty_conflicts(
        self, duties: List[str], context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Find conflicts between duties."""

        # Common duty conflicts
        conflict_patterns = [
            ("do_not_lie", "help_others_in_need"),  # Truth vs kindness
            ("keep_promises", "help_others_in_need"),  # Fidelity vs beneficence
            ("respect_autonomy", "promote_general_welfare"),  # Individual vs collective
        ]

        conflicts = []
        for duty1, duty2 in conflict_patterns:
            if duty1 in duties and duty2 in duties:
                conflicts.append(
                    {"duty1": duty1, "duty2": duty2, "type": "principle_conflict"}
                )

        return conflicts

    def _resolve_duty_conflicts(self, conflicts: List[Dict[str, str]]) -> str:
        """Resolve conflicts between duties using priority rules."""

        if not conflicts:
            return "No duty conflicts identified"

        # Simplified resolution using duty hierarchy
        # Perfect duties generally override imperfect duties

        perfect_duties = set(self.duty_hierarchy["perfect_duties"])

        for conflict in conflicts:
            duty1 = conflict["duty1"]
            duty2 = conflict["duty2"]

            if duty1 in perfect_duties and duty2 not in perfect_duties:
                return f"Perfect duty '{duty1}' takes priority over imperfect duty '{duty2}'"
            elif duty2 in perfect_duties and duty1 not in perfect_duties:
                return f"Perfect duty '{duty2}' takes priority over imperfect duty '{duty1}'"

        return "Duty conflict requires contextual judgment"

    def _calculate_deontological_confidence(self, evaluation: Dict[str, Any]) -> float:
        """Calculate confidence in deontological evaluation."""

        test_results = evaluation["evaluations"]

        # High confidence if all tests clearly pass or fail
        clear_results = sum(
            1
            for result in test_results.values()
            if isinstance(result.get("passes"), bool)
        )

        total_tests = len(test_results)
        clarity_ratio = clear_results / total_tests if total_tests > 0 else 0

        # Confidence based on test clarity and consistency
        base_confidence = 0.8 if evaluation["verdict"] == "permissible" else 0.9

        return base_confidence * clarity_ratio


class ConsequentialistReasoner:
    """
    Implements outcome-based ethical reasoning including utilitarianism.
    """

    def __init__(self):
        self.utility_functions = {
            "classical_util": self._classical_utility,
            "preference_util": self._preference_utility,
            "wellbeing_util": self._wellbeing_utility,
            "capability_util": self._capability_utility,
        }

        self.aggregation_methods = {
            "total_util": lambda utils: sum(utils),
            "average_util": lambda utils: sum(utils) / len(utils) if utils else 0,
            "priority_weighted": self._priority_weighted_aggregation,
            "maximin": lambda utils: min(utils) if utils else 0,
        }

    async def evaluate_action(
        self,
        proposed_action: str,
        context: Dict[str, Any],
        alternatives: List[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate action using consequentialist principles."""

        if alternatives is None:
            alternatives = [proposed_action, "do_nothing"]

        evaluation = {
            "framework": EthicalFramework.CONSEQUENTIALIST,
            "action": proposed_action,
            "alternatives_considered": alternatives,
            "utility_calculations": {},
        }

        # Calculate utilities for each alternative
        action_utilities = {}

        for action in alternatives:
            utility_scores = await self._calculate_action_utility(action, context)
            action_utilities[action] = utility_scores

        evaluation["utility_calculations"] = action_utilities

        # Determine best action
        best_action = await self._determine_optimal_action(action_utilities)
        evaluation["recommended_action"] = best_action

        # Calculate confidence based on utility differences
        evaluation["confidence"] = self._calculate_consequentialist_confidence(
            action_utilities
        )

        # Provide utilitarian justification
        evaluation["justification"] = self._generate_utilitarian_justification(
            proposed_action, best_action, action_utilities
        )

        return evaluation

    async def _calculate_action_utility(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate utility of an action across different utility functions."""

        # Predict consequences of action
        consequences = await self._predict_consequences(action, context)

        utility_scores = {}

        # Calculate utility using different functions
        for util_name, util_func in self.utility_functions.items():
            score = await util_func(consequences, context)
            utility_scores[util_name] = score

        # Aggregate utilities using different methods
        aggregated_scores = {}
        individual_utilities = [
            consequences.get(person, {}).get("utility", 0)
            for person in consequences.get("affected_individuals", [])
        ]

        if individual_utilities:
            for agg_name, agg_func in self.aggregation_methods.items():
                aggregated_scores[agg_name] = agg_func(individual_utilities)

        utility_scores.update(aggregated_scores)

        return utility_scores

    async def _predict_consequences(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict consequences of taking an action."""

        # Simplified consequence prediction
        consequences = {
            "affected_individuals": context.get("stakeholders", []),
            "short_term_effects": {},
            "long_term_effects": {},
            "probability_distribution": {},
            "uncertainty_level": 0.3,
        }

        action_lower = action.lower()

        # Predict based on action type
        if "help" in action_lower:
            consequences["short_term_effects"] = {
                "recipient_wellbeing": 0.8,
                "helper_cost": -0.2,
                "community_benefit": 0.3,
            }
            consequences["long_term_effects"] = {
                "trust_building": 0.5,
                "precedent_setting": 0.4,
            }

        elif "harm" in action_lower:
            consequences["short_term_effects"] = {
                "victim_wellbeing": -0.9,
                "actor_guilt": -0.3,
                "community_fear": -0.4,
            }
            consequences["long_term_effects"] = {
                "trust_erosion": -0.6,
                "cycle_of_harm": -0.5,
            }

        elif "lie" in action_lower:
            consequences["short_term_effects"] = {
                "deceived_autonomy": -0.5,
                "actor_guilt": -0.2,
                "immediate_benefit": 0.3,
            }
            consequences["long_term_effects"] = {
                "trust_damage": -0.7,
                "truth_erosion": -0.4,
            }

        # Add uncertainty and probability distributions
        for effect_category in ["short_term_effects", "long_term_effects"]:
            for effect, value in consequences[effect_category].items():
                # Add uncertainty to predictions
                uncertainty = np.random.normal(0, consequences["uncertainty_level"])
                consequences[effect_category][effect] = value + uncertainty

        return consequences

    async def _classical_utility(
        self, consequences: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate classical utilitarian utility (pleasure/pain)."""

        total_utility = 0.0

        # Sum short-term and long-term effects
        for effect_category in ["short_term_effects", "long_term_effects"]:
            effects = consequences.get(effect_category, {})
            category_utility = sum(effects.values())

            # Weight long-term effects slightly less due to discounting
            if effect_category == "long_term_effects":
                category_utility *= 0.8

            total_utility += category_utility

        return total_utility

    async def _preference_utility(
        self, consequences: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate preference satisfaction utility."""

        # Simplified preference satisfaction calculation
        stakeholder_preferences = context.get("stakeholder_preferences", {})

        preference_satisfaction = 0.0

        for stakeholder, preferences in stakeholder_preferences.items():
            for preference, strength in preferences.items():
                # Check if consequences satisfy this preference
                satisfaction_level = self._check_preference_satisfaction(
                    preference, consequences
                )
                preference_satisfaction += satisfaction_level * strength

        return preference_satisfaction

    def _check_preference_satisfaction(
        self, preference: str, consequences: Dict[str, Any]
    ) -> float:
        """Check how well consequences satisfy a preference."""

        # Simplified preference matching
        preference_lower = preference.lower()

        all_effects = {}
        all_effects.update(consequences.get("short_term_effects", {}))
        all_effects.update(consequences.get("long_term_effects", {}))

        # Look for effects that match preferences
        satisfaction = 0.0
        for effect, value in all_effects.items():
            if any(word in effect.lower() for word in preference_lower.split()):
                satisfaction += value

        return satisfaction / len(all_effects) if all_effects else 0.0

    async def _wellbeing_utility(
        self, consequences: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate wellbeing-based utility."""

        wellbeing_factors = [
            "physical_health",
            "mental_health",
            "social_connections",
            "autonomy",
            "purpose",
            "security",
        ]

        total_wellbeing = 0.0

        all_effects = {}
        all_effects.update(consequences.get("short_term_effects", {}))
        all_effects.update(consequences.get("long_term_effects", {}))

        # Sum effects related to wellbeing factors
        for factor in wellbeing_factors:
            factor_effects = [
                value
                for effect, value in all_effects.items()
                if factor.replace("_", " ") in effect.lower()
            ]
            total_wellbeing += sum(factor_effects)

        return total_wellbeing

    async def _capability_utility(
        self, consequences: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate capability-based utility (Sen/Nussbaum approach)."""

        central_capabilities = [
            "life",
            "bodily_health",
            "bodily_integrity",
            "senses_imagination_thought",
            "emotions",
            "practical_reason",
            "affiliation",
            "other_species",
            "play",
            "control_environment",
        ]

        capability_score = 0.0

        all_effects = {}
        all_effects.update(consequences.get("short_term_effects", {}))
        all_effects.update(consequences.get("long_term_effects", {}))

        # Evaluate impact on each central capability
        for capability in central_capabilities:
            capability_impact = 0.0

            # Look for effects that impact this capability
            for effect, value in all_effects.items():
                if self._affects_capability(effect, capability):
                    capability_impact += value

            # Each capability contributes equally (non-compensatory)
            capability_score += max(capability_impact, -1.0)  # Floor at -1

        return capability_score / len(central_capabilities)

    def _affects_capability(self, effect: str, capability: str) -> bool:
        """Check if effect affects a particular capability."""

        capability_keywords = {
            "life": ["death", "survival", "mortality"],
            "bodily_health": ["health", "disease", "nutrition", "medical"],
            "bodily_integrity": ["violence", "assault", "freedom", "movement"],
            "senses_imagination_thought": [
                "education",
                "learning",
                "expression",
                "creativity",
            ],
            "emotions": ["emotional", "wellbeing", "mental_health", "relationships"],
            "practical_reason": ["choice", "autonomy", "decision", "planning"],
            "affiliation": ["social", "community", "friendship", "discrimination"],
            "other_species": ["environment", "nature", "animals"],
            "play": ["recreation", "enjoyment", "leisure"],
            "control_environment": ["political", "property", "work", "participation"],
        }

        keywords = capability_keywords.get(capability, [])
        effect_lower = effect.lower()

        return any(keyword in effect_lower for keyword in keywords)

    def _priority_weighted_aggregation(self, utilities: List[float]) -> float:
        """Aggregate utilities with priority weighting for worse-off individuals."""

        if not utilities:
            return 0.0

        # Sort utilities (lower = worse off)
        sorted_utils = sorted(utilities)

        # Give higher weights to worse-off individuals
        weighted_sum = 0.0
        total_weight = 0.0

        for i, utility in enumerate(sorted_utils):
            # Higher weights for lower utilities (worse off)
            weight = len(sorted_utils) - i
            weighted_sum += utility * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _determine_optimal_action(
        self, action_utilities: Dict[str, Dict[str, float]]
    ) -> str:
        """Determine which action maximizes utility."""

        # Use primary utility measure (classical_util) for comparison
        action_scores = {}

        for action, utilities in action_utilities.items():
            # Combine different utility measures with weights
            combined_score = (
                utilities.get("classical_util", 0) * 0.3
                + utilities.get("preference_util", 0) * 0.2
                + utilities.get("wellbeing_util", 0) * 0.3
                + utilities.get("capability_util", 0) * 0.2
            )
            action_scores[action] = combined_score

        # Return action with highest combined utility
        return max(action_scores.items(), key=lambda x: x[1])[0]

    def _calculate_consequentialist_confidence(
        self, action_utilities: Dict[str, Dict[str, float]]
    ) -> float:
        """Calculate confidence in consequentialist recommendation."""

        # Get combined scores
        combined_scores = []
        for action, utilities in action_utilities.items():
            combined_score = (
                utilities.get("classical_util", 0) * 0.3
                + utilities.get("preference_util", 0) * 0.2
                + utilities.get("wellbeing_util", 0) * 0.3
                + utilities.get("capability_util", 0) * 0.2
            )
            combined_scores.append(combined_score)

        if len(combined_scores) < 2:
            return 0.5

        # Calculate utility difference between best and second-best
        sorted_scores = sorted(combined_scores, reverse=True)
        utility_gap = sorted_scores[0] - sorted_scores[1]

        # Higher confidence for larger utility gaps
        confidence = min(0.5 + utility_gap, 1.0)

        return confidence

    def _generate_utilitarian_justification(
        self,
        proposed_action: str,
        recommended_action: str,
        action_utilities: Dict[str, Dict[str, float]],
    ) -> str:
        """Generate utilitarian justification for recommendation."""

        if proposed_action == recommended_action:
            utility_score = action_utilities[proposed_action].get("classical_util", 0)
            return f"Action '{proposed_action}' maximizes overall utility (score: {utility_score:.2f})"
        else:
            proposed_utility = action_utilities[proposed_action].get(
                "classical_util", 0
            )
            recommended_utility = action_utilities[recommended_action].get(
                "classical_util", 0
            )

            return (
                f"Action '{recommended_action}' (utility: {recommended_utility:.2f}) "
                f"produces better outcomes than '{proposed_action}' (utility: {proposed_utility:.2f})"
            )


class ValueAlignmentSystem:
    """
    System for learning and maintaining alignment with human values.
    """

    def __init__(self):
        self.learned_values: Dict[str, float] = {}
        self.value_uncertainty: Dict[str, float] = {}
        self.value_learning_history: deque = deque(maxlen=10000)
        self.alignment_metrics: Dict[str, float] = {}

        # Initialize with basic human values
        self.core_human_values = {
            "human_wellbeing": 0.9,
            "autonomy": 0.8,
            "fairness": 0.8,
            "truth": 0.7,
            "dignity": 0.9,
            "freedom": 0.8,
            "justice": 0.8,
            "compassion": 0.7,
            "knowledge": 0.6,
            "beauty": 0.5,
        }

        self.learned_values = self.core_human_values.copy()

        # Initialize uncertainty
        for value in self.learned_values:
            self.value_uncertainty[value] = 0.2  # Moderate initial uncertainty

    async def learn_from_feedback(
        self,
        decision_context: Dict[str, Any],
        action_taken: str,
        feedback: Dict[str, Any],
    ) -> None:
        """Learn values from human feedback on decisions."""

        feedback_type = feedback.get("type", "rating")  # rating, preference, correction

        if feedback_type == "rating":
            await self._learn_from_rating_feedback(
                decision_context, action_taken, feedback
            )
        elif feedback_type == "preference":
            await self._learn_from_preference_feedback(
                decision_context, action_taken, feedback
            )
        elif feedback_type == "correction":
            await self._learn_from_correction_feedback(
                decision_context, action_taken, feedback
            )

        # Update alignment metrics
        await self._update_alignment_metrics()

        # Store learning event
        learning_event = {
            "timestamp": time.time(),
            "context": decision_context,
            "action": action_taken,
            "feedback": feedback,
            "values_before": self.learned_values.copy(),
            "values_after": None,  # Will be filled after update
        }

        # Apply value updates
        await self._apply_value_updates(learning_event)

        learning_event["values_after"] = self.learned_values.copy()
        self.value_learning_history.append(learning_event)

    async def _learn_from_rating_feedback(
        self, context: Dict[str, Any], action: str, feedback: Dict[str, Any]
    ) -> None:
        """Learn from numerical rating feedback."""

        rating = feedback.get("rating", 0)  # -1 to 1 scale
        confidence = feedback.get("confidence", 0.7)

        # Identify which values were involved in the decision
        relevant_values = self._identify_relevant_values(context, action)

        # Update values based on rating
        learning_rate = 0.01 * confidence

        for value in relevant_values:
            if rating > 0:
                # Positive feedback - increase value weight
                self.learned_values[value] += learning_rate * rating
                self.value_uncertainty[value] *= 0.95  # Reduce uncertainty
            else:
                # Negative feedback - decrease value weight
                self.learned_values[value] += (
                    learning_rate * rating
                )  # rating is negative
                self.value_uncertainty[value] *= 1.05  # Increase uncertainty

            # Keep values in reasonable bounds
            self.learned_values[value] = np.clip(self.learned_values[value], 0.0, 1.0)

    async def _learn_from_preference_feedback(
        self, context: Dict[str, Any], action: str, feedback: Dict[str, Any]
    ) -> None:
        """Learn from preference comparisons (A preferred over B)."""

        preferred_action = feedback.get("preferred_action")
        rejected_action = feedback.get("rejected_action")
        strength = feedback.get("strength", 0.5)  # How strong the preference

        if not preferred_action or not rejected_action:
            return

        # Identify values associated with each action
        preferred_values = self._identify_relevant_values(context, preferred_action)
        rejected_values = self._identify_relevant_values(context, rejected_action)

        # Increase weights for values associated with preferred action
        learning_rate = 0.005 * strength

        for value in preferred_values:
            self.learned_values[value] += learning_rate
            self.value_uncertainty[value] *= 0.98

        for value in rejected_values:
            self.learned_values[value] -= learning_rate * 0.5  # Smaller decrease
            self.value_uncertainty[value] *= 1.02

        # Normalize values
        for value in self.learned_values:
            self.learned_values[value] = np.clip(self.learned_values[value], 0.0, 1.0)

    async def _learn_from_correction_feedback(
        self, context: Dict[str, Any], action: str, feedback: Dict[str, Any]
    ) -> None:
        """Learn from explicit corrections about what should have been done."""

        correct_action = feedback.get("correct_action")
        explanation = feedback.get("explanation", "")

        if not correct_action:
            return

        # Extract value information from explanation
        value_mentions = self._extract_values_from_text(explanation)

        # Strong learning signal for corrections
        learning_rate = 0.02

        # Increase weights for values mentioned in correction
        for value_name, importance in value_mentions.items():
            if value_name in self.learned_values:
                self.learned_values[value_name] += learning_rate * importance
                self.value_uncertainty[
                    value_name
                ] *= 0.9  # Reduce uncertainty significantly

        # Normalize values
        for value in self.learned_values:
            self.learned_values[value] = np.clip(self.learned_values[value], 0.0, 1.0)

    def _identify_relevant_values(
        self, context: Dict[str, Any], action: str
    ) -> List[str]:
        """Identify which values are relevant to a decision context and action."""

        relevant_values = []
        action_lower = action.lower()
        context_text = str(context).lower()

        # Map actions and contexts to values
        value_indicators = {
            "human_wellbeing": ["help", "benefit", "health", "wellbeing", "happiness"],
            "autonomy": ["choice", "freedom", "decide", "autonomy", "consent"],
            "fairness": ["fair", "equal", "just", "equitable", "bias"],
            "truth": ["honest", "truth", "accurate", "transparent", "lie"],
            "dignity": ["respect", "dignity", "worth", "honor"],
            "freedom": ["freedom", "liberty", "constraint", "coercion"],
            "justice": ["justice", "right", "wrong", "punishment", "law"],
            "compassion": ["care", "empathy", "compassion", "suffering", "kindness"],
            "knowledge": ["learn", "knowledge", "education", "ignorance"],
            "beauty": ["beauty", "aesthetic", "art", "creativity"],
        }

        combined_text = action_lower + " " + context_text

        for value, indicators in value_indicators.items():
            if any(indicator in combined_text for indicator in indicators):
                relevant_values.append(value)

        return relevant_values

    def _extract_values_from_text(self, text: str) -> Dict[str, float]:
        """Extract value mentions and their importance from text."""

        text_lower = text.lower()
        value_mentions = {}

        # Simple keyword-based extraction
        value_keywords = {
            "human_wellbeing": ["wellbeing", "welfare", "happiness", "health"],
            "autonomy": ["autonomy", "choice", "self-determination"],
            "fairness": ["fairness", "equity", "equality", "justice"],
            "truth": ["truth", "honesty", "accuracy", "transparency"],
            "dignity": ["dignity", "respect", "worth"],
            "freedom": ["freedom", "liberty"],
            "compassion": ["compassion", "empathy", "care", "kindness"],
        }

        for value, keywords in value_keywords.items():
            importance = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    importance += 0.2

            if importance > 0:
                value_mentions[value] = min(importance, 1.0)

        return value_mentions

    async def _apply_value_updates(self, learning_event: Dict[str, Any]) -> None:
        """Apply learned value updates with safeguards."""

        # Check for rapid value drift
        drift_detected = await self._detect_value_drift()

        if drift_detected:
            logger.warning("Rapid value drift detected, applying conservative updates")
            # Apply smaller updates when drift is detected
            for value in self.learned_values:
                # Move values back toward core human values
                target = self.core_human_values.get(value, 0.5)
                self.learned_values[value] = (
                    0.9 * self.learned_values[value] + 0.1 * target
                )

    async def _detect_value_drift(self) -> bool:
        """Detect if values are drifting too rapidly from human values."""

        if len(self.value_learning_history) < 10:
            return False

        # Check recent value changes
        recent_events = list(self.value_learning_history)[-10:]

        total_change = 0.0
        for event in recent_events:
            values_before = event.get("values_before", {})
            values_after = event.get("values_after", {})

            for value in values_before:
                if value in values_after:
                    change = abs(values_after[value] - values_before[value])
                    total_change += change

        # Drift threshold
        drift_threshold = 0.5  # Total change across all values

        return total_change > drift_threshold

    async def _update_alignment_metrics(self) -> None:
        """Update metrics measuring value alignment."""

        # Calculate alignment with core human values
        alignment_score = 0.0
        total_values = 0

        for value, learned_weight in self.learned_values.items():
            if value in self.core_human_values:
                core_weight = self.core_human_values[value]
                alignment = 1.0 - abs(learned_weight - core_weight)
                alignment_score += alignment
                total_values += 1

        self.alignment_metrics["core_value_alignment"] = (
            alignment_score / total_values if total_values > 0 else 0
        )

        # Calculate value stability
        if len(self.value_learning_history) > 20:
            recent_changes = []
            for i in range(-20, -1):
                event = self.value_learning_history[i]
                values_before = event.get("values_before", {})
                values_after = event.get("values_after", {})

                total_change = sum(
                    abs(values_after.get(v, 0) - values_before.get(v, 0))
                    for v in values_before
                )
                recent_changes.append(total_change)

            stability = 1.0 - (np.mean(recent_changes) / len(self.learned_values))
            self.alignment_metrics["value_stability"] = max(0.0, stability)

        # Calculate uncertainty level
        avg_uncertainty = np.mean(list(self.value_uncertainty.values()))
        self.alignment_metrics["value_certainty"] = 1.0 - avg_uncertainty

    async def assess_alignment(
        self, decision_context: Dict[str, Any]
    ) -> ValueAlignment:
        """Assess current value alignment for a decision context."""

        relevant_values = self._identify_relevant_values(decision_context, "")

        # Calculate alignment for relevant values
        target_values = {v: self.core_human_values.get(v, 0.5) for v in relevant_values}
        current_values = {v: self.learned_values.get(v, 0.5) for v in relevant_values}

        # Overall alignment score
        alignment_scores = []
        for value in relevant_values:
            target = target_values[value]
            current = current_values[value]
            alignment = 1.0 - abs(target - current)
            alignment_scores.append(alignment)

        overall_alignment = np.mean(alignment_scores) if alignment_scores else 0.8

        # Calculate drift rate
        drift_rate = self._calculate_value_drift_rate()

        # Identify misalignment risks
        misalignment_risks = self._identify_misalignment_risks()

        # Suggest alignment interventions
        interventions = self._suggest_alignment_interventions(misalignment_risks)

        return ValueAlignment(
            alignment_id=str(uuid.uuid4()),
            target_values=target_values,
            current_values=current_values,
            alignment_score=overall_alignment,
            value_drift_rate=drift_rate,
            misalignment_risks=misalignment_risks,
            alignment_interventions=interventions,
            confidence_in_alignment=self.alignment_metrics.get("value_certainty", 0.7),
        )

    def _calculate_value_drift_rate(self) -> float:
        """Calculate rate of value drift over time."""

        if len(self.value_learning_history) < 5:
            return 0.0

        # Compare values now vs 5 learning events ago
        current_values = self.learned_values
        past_event = self.value_learning_history[-5]
        past_values = past_event.get("values_after", {})

        total_drift = 0.0
        for value in current_values:
            if value in past_values:
                drift = abs(current_values[value] - past_values[value])
                total_drift += drift

        return total_drift / len(current_values) if current_values else 0.0

    def _identify_misalignment_risks(self) -> List[str]:
        """Identify potential misalignment risks."""

        risks = []

        # Check for values drifting far from human values
        for value, learned_weight in self.learned_values.items():
            if value in self.core_human_values:
                core_weight = self.core_human_values[value]
                deviation = abs(learned_weight - core_weight)

                if deviation > 0.3:
                    risks.append(
                        f"Value '{value}' has drifted significantly from human baseline"
                    )

        # Check for high uncertainty in critical values
        critical_values = ["human_wellbeing", "autonomy", "dignity"]
        for value in critical_values:
            if self.value_uncertainty.get(value, 0) > 0.4:
                risks.append(f"High uncertainty in critical value '{value}'")

        # Check for rapid recent changes
        if self.alignment_metrics.get("value_stability", 1.0) < 0.6:
            risks.append("Unstable value learning - rapid recent changes detected")

        return risks

    def _suggest_alignment_interventions(self, risks: List[str]) -> List[str]:
        """Suggest interventions to improve value alignment."""

        interventions = []

        if any("drifted significantly" in risk for risk in risks):
            interventions.append("Increase regularization toward human baseline values")
            interventions.append("Seek additional human feedback on drifted values")

        if any("High uncertainty" in risk for risk in risks):
            interventions.append("Request targeted feedback on uncertain values")
            interventions.append("Reduce learning rate for uncertain values")

        if any("Unstable value learning" in risk for risk in risks):
            interventions.append("Implement value change rate limiting")
            interventions.append("Review recent feedback for inconsistencies")

        if not interventions:
            interventions.append("Continue current value learning approach")

        return interventions


class EthicalReasoningSystem:
    """
    Main ethical reasoning system integrating multiple frameworks and value alignment.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Initialize reasoning frameworks
        self.deontological_reasoner = DeontologicalReasoner()
        self.consequentialist_reasoner = ConsequentialistReasoner()
        self.value_alignment_system = ValueAlignmentSystem()

        # Ethical decision history
        self.decision_history: deque = deque(maxlen=10000)
        self.moral_judgments: List[MoralJudgment] = []

        # Ethical constraints
        self.active_constraints: List[EthicalConstraint] = []
        self._initialize_default_constraints()

        # Cross-cultural considerations
        self.cultural_contexts: Dict[str, Dict[str, Any]] = {}

        # Monitoring and drift detection
        self.ethical_drift_detector = self._initialize_drift_detector()

    def _initialize_default_constraints(self) -> None:
        """Initialize default ethical constraints."""

        default_constraints = [
            EthicalConstraint(
                constraint_id="no_harm_humans",
                constraint_type="prohibition",
                description="Do not harm humans or cause them to come to harm",
                priority_level=1,
                hard_constraint=True,
                enforcement_mechanism="decision_blocking",
                violation_consequences=[
                    "immediate_action_cessation",
                    "alert_human_operators",
                ],
                contextual_exceptions=[
                    "legitimate_self_defense",
                    "preventing_greater_harm",
                ],
                stakeholder_source=StakeholderType.SOCIETY_AT_LARGE,
            ),
            EthicalConstraint(
                constraint_id="respect_autonomy",
                constraint_type="requirement",
                description="Respect human autonomy and right to self-determination",
                priority_level=2,
                hard_constraint=True,
                enforcement_mechanism="consent_verification",
                violation_consequences=[
                    "request_explicit_consent",
                    "explain_decision_rationale",
                ],
                contextual_exceptions=[
                    "emergency_situations",
                    "incapacitated_individuals",
                ],
                stakeholder_source=StakeholderType.INDIVIDUAL_USER,
            ),
            EthicalConstraint(
                constraint_id="truthfulness",
                constraint_type="requirement",
                description="Be truthful and avoid deception",
                priority_level=3,
                hard_constraint=False,
                enforcement_mechanism="verification_prompt",
                violation_consequences=[
                    "truth_clarification",
                    "uncertainty_acknowledgment",
                ],
                contextual_exceptions=["protecting_privacy", "preventing_harm"],
                stakeholder_source=StakeholderType.SOCIETY_AT_LARGE,
            ),
            EthicalConstraint(
                constraint_id="fairness",
                constraint_type="requirement",
                description="Treat all individuals fairly and avoid discrimination",
                priority_level=3,
                hard_constraint=False,
                enforcement_mechanism="bias_checking",
                violation_consequences=["bias_alert", "alternative_suggestion"],
                contextual_exceptions=["legitimate_distinctions", "affirmative_action"],
                stakeholder_source=StakeholderType.AFFECTED_COMMUNITY,
            ),
        ]

        self.active_constraints.extend(default_constraints)

    def _initialize_drift_detector(self) -> Any:
        """Initialize ethical drift detection system."""
        # Simplified drift detector - in practice would be more sophisticated
        return {
            "baseline_judgments": [],
            "recent_judgments": deque(maxlen=100),
            "drift_threshold": 0.3,
        }

    async def make_ethical_judgment(
        self,
        ethical_question: str,
        context: Dict[str, Any],
        stakeholder_analysis: Dict[StakeholderType, Dict[str, Any]] = None,
    ) -> MoralJudgment:
        """Make comprehensive ethical judgment using multiple frameworks."""

        judgment_id = str(uuid.uuid4())

        # 1. Constraint checking
        constraint_violations = await self._check_ethical_constraints(
            ethical_question, context
        )

        if constraint_violations:
            # Hard constraints violated - immediate judgment
            if any(v["hard_constraint"] for v in constraint_violations):
                return self._create_constraint_violation_judgment(
                    judgment_id, ethical_question, constraint_violations
                )

        # 2. Multi-framework analysis
        framework_analyses = {}

        # Deontological analysis
        if context.get("proposed_action"):
            maxim = context.get("maxim", f"Act to {context['proposed_action']}")
            deont_analysis = await self.deontological_reasoner.evaluate_action(
                context["proposed_action"], context, maxim
            )
            framework_analyses[EthicalFramework.DEONTOLOGICAL] = deont_analysis

        # Consequentialist analysis
        if context.get("proposed_action"):
            alternatives = context.get("alternatives", [])
            conseq_analysis = await self.consequentialist_reasoner.evaluate_action(
                context["proposed_action"], context, alternatives
            )
            framework_analyses[EthicalFramework.CONSEQUENTIALIST] = conseq_analysis

        # 3. Value alignment assessment
        alignment_assessment = await self.value_alignment_system.assess_alignment(
            context
        )

        # 4. Stakeholder impact analysis
        if not stakeholder_analysis:
            stakeholder_analysis = await self._analyze_stakeholder_impacts(context)

        # 5. Cultural sensitivity check
        cultural_considerations = await self._assess_cultural_sensitivity(context)

        # 6. Uncertainty quantification
        uncertainty_factors = self._identify_uncertainty_factors(
            framework_analyses, alignment_assessment, context
        )

        # 7. Synthesize judgment
        judgment = await self._synthesize_moral_judgment(
            judgment_id=judgment_id,
            ethical_question=ethical_question,
            context=context,
            framework_analyses=framework_analyses,
            alignment_assessment=alignment_assessment,
            stakeholder_analysis=stakeholder_analysis,
            cultural_considerations=cultural_considerations,
            uncertainty_factors=uncertainty_factors,
            constraint_violations=constraint_violations,
        )

        # 8. Store judgment and update systems
        self.moral_judgments.append(judgment)
        self.decision_history.append(
            {
                "timestamp": time.time(),
                "question": ethical_question,
                "judgment": judgment,
                "context": context,
            }
        )

        # 9. Check for ethical drift
        await self._monitor_ethical_drift(judgment)

        logger.info(
            "Ethical judgment completed",
            judgment_id=judgment_id,
            recommended_action=judgment.recommended_action,
            confidence=judgment.confidence_score,
        )

        return judgment

    async def _check_ethical_constraints(
        self, question: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if proposed action violates ethical constraints."""

        violations = []
        proposed_action = context.get("proposed_action", "")

        for constraint in self.active_constraints:
            violation = await self._evaluate_constraint_violation(
                constraint, proposed_action, context
            )

            if violation:
                violations.append(
                    {
                        "constraint": constraint,
                        "violation_type": violation["type"],
                        "severity": violation["severity"],
                        "hard_constraint": constraint.hard_constraint,
                        "explanation": violation["explanation"],
                    }
                )

        return violations

    async def _evaluate_constraint_violation(
        self,
        constraint: EthicalConstraint,
        proposed_action: str,
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate if a specific constraint is violated."""

        action_lower = proposed_action.lower()
        constraint_desc = constraint.description.lower()

        # Simple pattern matching for common constraint violations
        violation_patterns = {
            "no_harm_humans": ["harm", "hurt", "damage", "injure", "kill"],
            "respect_autonomy": ["force", "coerce", "manipulate", "deceive"],
            "truthfulness": ["lie", "deceive", "mislead", "false"],
            "fairness": ["discriminate", "bias", "unfair", "prejudice"],
        }

        constraint_id = constraint.constraint_id
        patterns = violation_patterns.get(constraint_id, [])

        # Check for violation patterns
        violation_detected = any(pattern in action_lower for pattern in patterns)

        if violation_detected:
            # Check for contextual exceptions
            exceptions = constraint.contextual_exceptions
            exception_applies = any(
                exception.replace("_", " ") in str(context).lower()
                for exception in exceptions
            )

            if not exception_applies:
                return {
                    "type": "pattern_match",
                    "severity": "high" if constraint.hard_constraint else "medium",
                    "explanation": f"Action '{proposed_action}' appears to violate constraint: {constraint.description}",
                }

        return None

    def _create_constraint_violation_judgment(
        self, judgment_id: str, ethical_question: str, violations: List[Dict[str, Any]]
    ) -> MoralJudgment:
        """Create judgment for constraint violation."""

        hard_violations = [v for v in violations if v["hard_constraint"]]

        if hard_violations:
            recommended_action = "DO NOT PROCEED - Hard ethical constraint violated"
            confidence = 0.95
        else:
            recommended_action = (
                "PROCEED WITH CAUTION - Soft constraints may be violated"
            )
            confidence = 0.7

        violation_descriptions = [v["explanation"] for v in violations]
        justification = "Ethical constraints violated: " + "; ".join(
            violation_descriptions
        )

        return MoralJudgment(
            judgment_id=judgment_id,
            ethical_question=ethical_question,
            recommended_action=recommended_action,
            moral_justification=justification,
            confidence_score=confidence,
            uncertainty_factors=["constraint_boundary_cases"],
            stakeholder_impacts={},
            principle_weights={},
            framework_consensus={},
            cultural_considerations=[],
            potential_harms=[v["explanation"] for v in hard_violations],
            mitigation_strategies=["Modify action to comply with constraints"],
        )

    async def _analyze_stakeholder_impacts(
        self, context: Dict[str, Any]
    ) -> Dict[StakeholderType, Dict[str, Any]]:
        """Analyze impacts on different stakeholder groups."""

        stakeholder_impacts = {}

        # Identify stakeholders from context
        identified_stakeholders = context.get(
            "stakeholders", [StakeholderType.INDIVIDUAL_USER]
        )

        for stakeholder in identified_stakeholders:
            impact_analysis = {
                "affected": True,
                "impact_magnitude": self._estimate_impact_magnitude(
                    stakeholder, context
                ),
                "impact_valence": self._estimate_impact_valence(stakeholder, context),
                "specific_impacts": self._identify_specific_impacts(
                    stakeholder, context
                ),
                "mitigation_needs": self._identify_mitigation_needs(
                    stakeholder, context
                ),
            }

            stakeholder_impacts[stakeholder] = impact_analysis

        return stakeholder_impacts

    def _estimate_impact_magnitude(
        self, stakeholder: StakeholderType, context: Dict[str, Any]
    ) -> float:
        """Estimate magnitude of impact on stakeholder (0-1 scale)."""

        # Simplified estimation based on stakeholder type and context
        base_magnitude = 0.5

        if stakeholder == StakeholderType.INDIVIDUAL_USER:
            base_magnitude = 0.8  # Direct users typically most affected
        elif stakeholder == StakeholderType.VULNERABLE_POPULATIONS:
            base_magnitude = 0.9  # Vulnerable populations need special consideration
        elif stakeholder == StakeholderType.SOCIETY_AT_LARGE:
            base_magnitude = 0.3  # Broad but diffuse impact

        # Adjust based on context
        if context.get("high_stakes", False):
            base_magnitude *= 1.2

        return min(base_magnitude, 1.0)

    def _estimate_impact_valence(
        self, stakeholder: StakeholderType, context: Dict[str, Any]
    ) -> float:
        """Estimate valence of impact on stakeholder (-1 to 1 scale)."""

        proposed_action = context.get("proposed_action", "").lower()

        # Simple heuristics for impact valence
        positive_indicators = ["help", "benefit", "support", "improve", "assist"]
        negative_indicators = ["harm", "hurt", "damage", "reduce", "limit"]

        positive_score = sum(
            1 for indicator in positive_indicators if indicator in proposed_action
        )
        negative_score = sum(
            1 for indicator in negative_indicators if indicator in proposed_action
        )

        if positive_score > negative_score:
            return 0.6
        elif negative_score > positive_score:
            return -0.6
        else:
            return 0.0  # Neutral

    def _identify_specific_impacts(
        self, stakeholder: StakeholderType, context: Dict[str, Any]
    ) -> List[str]:
        """Identify specific impacts on stakeholder."""

        # Simplified impact identification
        impacts = []

        if stakeholder == StakeholderType.INDIVIDUAL_USER:
            impacts = ["autonomy_effects", "privacy_effects", "wellbeing_effects"]
        elif stakeholder == StakeholderType.VULNERABLE_POPULATIONS:
            impacts = ["protection_effects", "access_effects", "dignity_effects"]
        elif stakeholder == StakeholderType.SOCIETY_AT_LARGE:
            impacts = ["social_norm_effects", "trust_effects", "precedent_effects"]

        return impacts

    def _identify_mitigation_needs(
        self, stakeholder: StakeholderType, context: Dict[str, Any]
    ) -> List[str]:
        """Identify mitigation needs for stakeholder."""

        mitigation_needs = []

        if self._estimate_impact_valence(stakeholder, context) < -0.3:
            mitigation_needs.append("harm_reduction_measures")

        if self._estimate_impact_magnitude(stakeholder, context) > 0.7:
            mitigation_needs.append("enhanced_communication")
            mitigation_needs.append("additional_safeguards")

        return mitigation_needs

    async def _assess_cultural_sensitivity(self, context: Dict[str, Any]) -> List[str]:
        """Assess cultural sensitivity considerations."""

        considerations = []

        # Check for cultural context indicators
        cultural_context = context.get("cultural_context", {})

        if cultural_context:
            for culture, details in cultural_context.items():
                # Simplified cultural sensitivity check
                if "religious" in str(details).lower():
                    considerations.append(
                        f"Religious considerations for {culture} context"
                    )

                if "traditional" in str(details).lower():
                    considerations.append(
                        f"Traditional value considerations for {culture} context"
                    )

        # Default considerations
        if not considerations:
            considerations.append("Apply culturally neutral ethical principles")

        return considerations

    def _identify_uncertainty_factors(
        self,
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
        alignment_assessment: ValueAlignment,
        context: Dict[str, Any],
    ) -> List[str]:
        """Identify factors contributing to moral uncertainty."""

        uncertainty_factors = []

        # Framework disagreement
        if len(framework_analyses) > 1:
            framework_recommendations = set()
            for analysis in framework_analyses.values():
                if "recommended_action" in analysis:
                    framework_recommendations.add(analysis["recommended_action"])
                elif "verdict" in analysis:
                    framework_recommendations.add(analysis["verdict"])

            if len(framework_recommendations) > 1:
                uncertainty_factors.append("framework_disagreement")

        # Low confidence in frameworks
        for framework, analysis in framework_analyses.items():
            confidence = analysis.get("confidence", 0.5)
            if confidence < 0.6:
                uncertainty_factors.append(f"low_{framework.name.lower()}_confidence")

        # Value alignment uncertainty
        if alignment_assessment.confidence_in_alignment < 0.7:
            uncertainty_factors.append("value_alignment_uncertainty")

        # Incomplete information
        if context.get("incomplete_information", False):
            uncertainty_factors.append("incomplete_information")

        # Novel situation
        if context.get("novel_situation", False):
            uncertainty_factors.append("novel_ethical_territory")

        return uncertainty_factors

    async def _synthesize_moral_judgment(
        self,
        judgment_id: str,
        ethical_question: str,
        context: Dict[str, Any],
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
        alignment_assessment: ValueAlignment,
        stakeholder_analysis: Dict[StakeholderType, Dict[str, Any]],
        cultural_considerations: List[str],
        uncertainty_factors: List[str],
        constraint_violations: List[Dict[str, Any]],
    ) -> MoralJudgment:
        """Synthesize final moral judgment from all analyses."""

        # Determine recommended action
        recommended_action = await self._determine_recommended_action(
            framework_analyses, constraint_violations, context
        )

        # Generate moral justification
        justification = await self._generate_moral_justification(
            recommended_action,
            framework_analyses,
            alignment_assessment,
            stakeholder_analysis,
        )

        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(
            framework_analyses, alignment_assessment, uncertainty_factors
        )

        # Extract principle weights
        principle_weights = self._extract_principle_weights(framework_analyses, context)

        # Calculate framework consensus
        framework_consensus = self._calculate_framework_consensus(framework_analyses)

        # Identify potential harms
        potential_harms = self._identify_potential_harms(
            stakeholder_analysis, framework_analyses
        )

        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(
            potential_harms, constraint_violations, stakeholder_analysis
        )

        return MoralJudgment(
            judgment_id=judgment_id,
            ethical_question=ethical_question,
            recommended_action=recommended_action,
            moral_justification=justification,
            confidence_score=confidence,
            uncertainty_factors=uncertainty_factors,
            stakeholder_impacts=stakeholder_analysis,
            principle_weights=principle_weights,
            framework_consensus=framework_consensus,
            cultural_considerations=cultural_considerations,
            potential_harms=potential_harms,
            mitigation_strategies=mitigation_strategies,
        )

    async def _determine_recommended_action(
        self,
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
        constraint_violations: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        """Determine recommended action from framework analyses."""

        # Hard constraints override everything
        hard_violations = [v for v in constraint_violations if v["hard_constraint"]]
        if hard_violations:
            return "DO NOT PROCEED - Hard ethical constraints violated"

        # Collect framework recommendations
        framework_recommendations = {}

        for framework, analysis in framework_analyses.items():
            if framework == EthicalFramework.DEONTOLOGICAL:
                verdict = analysis.get("verdict", "uncertain")
                if verdict == "permissible":
                    framework_recommendations[framework] = context.get(
                        "proposed_action", "PROCEED"
                    )
                else:
                    framework_recommendations[framework] = "DO NOT PROCEED"

            elif framework == EthicalFramework.CONSEQUENTIALIST:
                recommended = analysis.get(
                    "recommended_action", context.get("proposed_action", "PROCEED")
                )
                framework_recommendations[framework] = recommended

        # Synthesize recommendations
        proceed_count = sum(
            1
            for rec in framework_recommendations.values()
            if "DO NOT PROCEED" not in rec
        )

        if (
            proceed_count == len(framework_recommendations)
            and framework_recommendations
        ):
            # All frameworks agree to proceed
            return context.get("proposed_action", "PROCEED")
        elif proceed_count == 0:
            # All frameworks say don't proceed
            return "DO NOT PROCEED"
        else:
            # Mixed recommendations
            return "PROCEED WITH CAUTION - Framework disagreement"

    async def _generate_moral_justification(
        self,
        recommended_action: str,
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
        alignment_assessment: ValueAlignment,
        stakeholder_analysis: Dict[StakeholderType, Dict[str, Any]],
    ) -> str:
        """Generate comprehensive moral justification."""

        justification_parts = []

        # Framework-based justifications
        for framework, analysis in framework_analyses.items():
            framework_name = framework.name.lower().replace("_", " ")

            if framework == EthicalFramework.DEONTOLOGICAL:
                verdict = analysis.get("verdict", "uncertain")
                justification_parts.append(f"Deontological analysis: {verdict}")

            elif framework == EthicalFramework.CONSEQUENTIALIST:
                justification_part = analysis.get(
                    "justification", "Consequentialist analysis conducted"
                )
                justification_parts.append(justification_part)

        # Value alignment justification
        alignment_score = alignment_assessment.alignment_score
        justification_parts.append(f"Value alignment score: {alignment_score:.2f}")

        # Stakeholder consideration
        affected_stakeholders = len(stakeholder_analysis)
        justification_parts.append(
            f"Considered impacts on {affected_stakeholders} stakeholder groups"
        )

        return ". ".join(justification_parts)

    def _calculate_overall_confidence(
        self,
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
        alignment_assessment: ValueAlignment,
        uncertainty_factors: List[str],
    ) -> float:
        """Calculate overall confidence in moral judgment."""

        confidence_factors = []

        # Framework confidence
        for analysis in framework_analyses.values():
            framework_confidence = analysis.get("confidence", 0.5)
            confidence_factors.append(framework_confidence)

        # Value alignment confidence
        alignment_confidence = alignment_assessment.confidence_in_alignment
        confidence_factors.append(alignment_confidence)

        # Uncertainty penalty
        uncertainty_penalty = len(uncertainty_factors) * 0.1

        # Calculate weighted average confidence
        if confidence_factors:
            base_confidence = np.mean(confidence_factors)
        else:
            base_confidence = 0.5

        # Apply uncertainty penalty
        final_confidence = max(0.1, base_confidence - uncertainty_penalty)

        return min(final_confidence, 0.95)  # Cap at 95%

    def _extract_principle_weights(
        self,
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[MoralPrinciple, float]:
        """Extract implicit principle weights from analyses."""

        # Start with uniform weights
        principle_weights = dict.fromkeys(MoralPrinciple, 0.5)

        # Adjust based on framework analyses
        for framework, analysis in framework_analyses.items():
            if framework == EthicalFramework.DEONTOLOGICAL:
                # Deontological emphasizes duty-based principles
                principle_weights[MoralPrinciple.AUTONOMY] += 0.2
                principle_weights[MoralPrinciple.DIGNITY] += 0.2
                principle_weights[MoralPrinciple.VERACITY] += 0.1

            elif framework == EthicalFramework.CONSEQUENTIALIST:
                # Consequentialist emphasizes outcomes
                principle_weights[MoralPrinciple.BENEFICENCE] += 0.3
                principle_weights[MoralPrinciple.NON_MALEFICENCE] += 0.3
                principle_weights[MoralPrinciple.JUSTICE] += 0.1

        # Normalize weights
        total_weight = sum(principle_weights.values())
        if total_weight > 0:
            principle_weights = {
                principle: weight / total_weight
                for principle, weight in principle_weights.items()
            }

        return principle_weights

    def _calculate_framework_consensus(
        self, framework_analyses: Dict[EthicalFramework, Dict[str, Any]]
    ) -> Dict[EthicalFramework, float]:
        """Calculate consensus level for each framework."""

        framework_consensus = {}

        for framework, analysis in framework_analyses.items():
            confidence = analysis.get("confidence", 0.5)

            # High confidence indicates strong consensus within framework
            if confidence > 0.8:
                consensus = 0.9
            elif confidence > 0.6:
                consensus = 0.7
            elif confidence > 0.4:
                consensus = 0.5
            else:
                consensus = 0.3

            framework_consensus[framework] = consensus

        return framework_consensus

    def _identify_potential_harms(
        self,
        stakeholder_analysis: Dict[StakeholderType, Dict[str, Any]],
        framework_analyses: Dict[EthicalFramework, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Identify potential harms from analyses."""

        potential_harms = []

        # Harms from stakeholder analysis
        for stakeholder, analysis in stakeholder_analysis.items():
            if analysis.get("impact_valence", 0) < -0.3:
                magnitude = analysis.get("impact_magnitude", 0)
                specific_impacts = analysis.get("specific_impacts", [])

                harm = {
                    "source": "stakeholder_impact",
                    "stakeholder": stakeholder.name,
                    "magnitude": magnitude,
                    "type": "negative_impact",
                    "details": specific_impacts,
                }
                potential_harms.append(harm)

        # Harms identified by frameworks
        for framework, analysis in framework_analyses.items():
            if framework == EthicalFramework.CONSEQUENTIALIST:
                # Extract negative consequences
                utility_calcs = analysis.get("utility_calculations", {})
                for action, utilities in utility_calcs.items():
                    classical_util = utilities.get("classical_util", 0)
                    if classical_util < -0.5:
                        harm = {
                            "source": "consequentialist_analysis",
                            "action": action,
                            "magnitude": abs(classical_util),
                            "type": "negative_utility",
                            "details": ["significant_negative_consequences"],
                        }
                        potential_harms.append(harm)

        return potential_harms

    def _generate_mitigation_strategies(
        self,
        potential_harms: List[Dict[str, Any]],
        constraint_violations: List[Dict[str, Any]],
        stakeholder_analysis: Dict[StakeholderType, Dict[str, Any]],
    ) -> List[str]:
        """Generate strategies to mitigate identified risks and harms."""

        strategies = []

        # Strategies for constraint violations
        if constraint_violations:
            strategies.append(
                "Modify proposed action to comply with ethical constraints"
            )
            strategies.append("Seek additional ethical review before proceeding")

        # Strategies for potential harms
        if potential_harms:
            strategies.append("Implement harm reduction measures")
            strategies.append("Establish monitoring for negative impacts")
            strategies.append("Prepare harm mitigation contingencies")

        # Strategies based on stakeholder needs
        for stakeholder, analysis in stakeholder_analysis.items():
            mitigation_needs = analysis.get("mitigation_needs", [])
            if mitigation_needs:
                strategies.extend(
                    [
                        f"Address {need} for {stakeholder.name}"
                        for need in mitigation_needs
                    ]
                )

        # Default strategies
        if not strategies:
            strategies.append("Proceed with standard ethical safeguards")
            strategies.append("Monitor outcomes for unexpected ethical implications")

        return list(set(strategies))  # Remove duplicates

    async def _monitor_ethical_drift(self, judgment: MoralJudgment) -> None:
        """Monitor for drift in ethical decision-making patterns."""

        self.ethical_drift_detector["recent_judgments"].append(judgment)

        # Compare recent judgments to baseline
        if len(self.ethical_drift_detector["recent_judgments"]) >= 20:
            recent_judgments = list(self.ethical_drift_detector["recent_judgments"])

            # Simple drift detection based on confidence trends
            confidence_trend = [j.confidence_score for j in recent_judgments[-10:]]
            avg_recent_confidence = np.mean(confidence_trend)

            # Compare to earlier judgments
            if len(recent_judgments) >= 20:
                earlier_confidence = [
                    j.confidence_score for j in recent_judgments[-20:-10]
                ]
                avg_earlier_confidence = np.mean(earlier_confidence)

                confidence_drift = abs(avg_recent_confidence - avg_earlier_confidence)

                if confidence_drift > self.ethical_drift_detector["drift_threshold"]:
                    logger.warning(
                        "Ethical drift detected",
                        confidence_drift=confidence_drift,
                        recent_confidence=avg_recent_confidence,
                        earlier_confidence=avg_earlier_confidence,
                    )

    async def get_ethical_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive report on ethical reasoning system status."""

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "operational",
            "total_judgments": len(self.moral_judgments),
            "recent_judgments_24h": len(
                [
                    j
                    for j in self.moral_judgments
                    if j.timestamp > datetime.now() - timedelta(hours=24)
                ]
            ),
            "active_constraints": len(self.active_constraints),
            "value_alignment": {},
            "framework_usage": defaultdict(int),
            "confidence_statistics": {},
            "ethical_drift_status": "monitoring",
        }

        if self.moral_judgments:
            # Calculate confidence statistics
            recent_judgments = [
                j
                for j in self.moral_judgments
                if j.timestamp > datetime.now() - timedelta(hours=24)
            ]

            if recent_judgments:
                confidences = [j.confidence_score for j in recent_judgments]
                report["confidence_statistics"] = {
                    "mean_confidence": np.mean(confidences),
                    "median_confidence": np.median(confidences),
                    "min_confidence": min(confidences),
                    "max_confidence": max(confidences),
                }

            # Framework usage statistics
            for judgment in recent_judgments:
                for framework in judgment.framework_consensus.keys():
                    report["framework_usage"][framework.name] += 1

        # Value alignment summary
        alignment_metrics = self.value_alignment_system.alignment_metrics
        report["value_alignment"] = alignment_metrics

        return report

    async def update_ethical_constraints(
        self, new_constraints: List[EthicalConstraint]
    ) -> None:
        """Update ethical constraints with new requirements."""

        # Add new constraints
        for constraint in new_constraints:
            # Check if constraint already exists
            existing_ids = [c.constraint_id for c in self.active_constraints]

            if constraint.constraint_id not in existing_ids:
                self.active_constraints.append(constraint)
                logger.info(
                    "New ethical constraint added",
                    constraint_id=constraint.constraint_id,
                    description=constraint.description,
                )

        # Sort constraints by priority
        self.active_constraints.sort(key=lambda c: c.priority_level)


# Example usage and testing
async def main():
    """Example usage of the Ethical Reasoning System."""

    config = {
        "enable_constraint_checking": True,
        "multi_framework_analysis": True,
        "value_alignment_active": True,
        "cultural_sensitivity": True,
    }

    # Initialize ethical reasoning system
    ethics_system = EthicalReasoningSystem(config)

    # Example ethical dilemma
    ethical_question = "Should I share user data to improve service quality?"

    context = {
        "proposed_action": "share_anonymized_user_data",
        "alternatives": ["dont_share_data", "get_explicit_consent_first"],
        "stakeholders": [
            StakeholderType.INDIVIDUAL_USER,
            StakeholderType.SOCIETY_AT_LARGE,
            StakeholderType.ORGANIZATION,
        ],
        "maxim": "Share user data when it improves services",
        "high_stakes": False,
        "incomplete_information": False,
        "cultural_context": {"western": {"privacy_emphasis": "high"}},
        "stakeholder_preferences": {
            "users": {"privacy": 0.9, "service_quality": 0.6},
            "company": {"efficiency": 0.8, "user_satisfaction": 0.7},
        },
    }

    # Make ethical judgment
    judgment = await ethics_system.make_ethical_judgment(
        ethical_question=ethical_question, context=context
    )

    print(f"Ethical Question: {ethical_question}")
    print(f"Recommended Action: {judgment.recommended_action}")
    print(f"Confidence: {judgment.confidence_score:.2f}")
    print(f"Moral Justification: {judgment.moral_justification}")
    print(f"Uncertainty Factors: {judgment.uncertainty_factors}")
    print(f"Mitigation Strategies: {judgment.mitigation_strategies}")

    # Simulate learning from feedback
    feedback = {
        "type": "rating",
        "rating": -0.3,  # Negative feedback
        "confidence": 0.8,
        "explanation": "Users value privacy more than service improvements",
    }

    await ethics_system.value_alignment_system.learn_from_feedback(
        decision_context=context,
        action_taken=judgment.recommended_action,
        feedback=feedback,
    )

    # Get system report
    report = await ethics_system.get_ethical_system_report()
    print("\nEthical System Report:")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())

# ═══════════════════════════════════════════════════════════════════════════
# LUKHAS AI - ETHICAL REASONING & VALUE ALIGNMENT SYSTEM
# Advanced moral reasoning and value alignment for safe AI systems:
# • Multi-paradigm moral reasoning (deontological, consequentialist, virtue ethics)
# • Constitutional AI principles with learned moral preferences
# • Value learning from human feedback and demonstrations
# • Moral uncertainty quantification and ethical confidence intervals
# • Stakeholder impact assessment and fairness optimization
# • Dynamic ethical constraint satisfaction with priority hierarchies
# • Cross-cultural moral sensitivity and contextual adaptation
# • Adversarial ethics testing and moral stress testing
# • Interpretable ethical decision explanations and justifications
# • Real-time moral monitoring and ethical drift detection
# ═══════════════════════════════════════════════════════════════════════════
