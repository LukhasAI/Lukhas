"""
LUKHAS Decision Explainability Framework
Provides human-readable explanations for all system decisions
"""
import streamlit as st
from datetime import timezone

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from lukhas.core.endocrine import get_endocrine_system
from lukhas.core.tags import get_tag_registry

logger = logging.getLogger(__name__)


class ExplanationLevel(Enum):
    """Different levels of explanation detail"""

    SUMMARY = "summary"  # Brief one-line explanation
    STANDARD = "standard"  # Normal explanation with key factors
    DETAILED = "detailed"  # Full explanation with all factors
    TECHNICAL = "technical"  # Technical details for developers
    VISUAL = "visual"  # Visual representation (future)


class ExplanationType(Enum):
    """Types of explanations available"""

    CAUSAL = "causal"  # Why this decision was made
    COMPARATIVE = "comparative"  # Why this over alternatives
    COUNTERFACTUAL = "counterfactual"  # What would change the decision
    PROCESS = "process"  # How the decision was reached
    CONFIDENCE = "confidence"  # Why confident/uncertain


@dataclass
class DecisionFactor:
    """A factor that influenced a decision"""

    name: str
    value: Any
    weight: float
    influence: str  # "positive", "negative", "neutral"
    explanation: str
    tags: set[str] = field(default_factory=set)


@dataclass
class DecisionExplanation:
    """Complete explanation for a decision"""

    decision_id: str
    summary: str
    factors: list[DecisionFactor]
    confidence_explanation: str
    process_steps: list[str]
    alternatives_comparison: dict[str, str]
    counterfactuals: list[str]
    relevant_tags: set[str]
    hormonal_state: dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_human_readable(self, level: ExplanationLevel = ExplanationLevel.STANDARD) -> str:
        """Convert explanation to human-readable text"""
        if level == ExplanationLevel.SUMMARY:
            return self.summary

        elif level == ExplanationLevel.STANDARD:
            parts = [f"Decision: {self.summary}", "", "Key Factors:"]

            # Top 3 factors
            top_factors = sorted(self.factors, key=lambda f: abs(f.weight), reverse=True)[:3]
            for factor in top_factors:
                influence_symbol = (
                    "↑" if factor.influence == "positive" else "↓" if factor.influence == "negative" else "→"
                )
                parts.append(f"  {influence_symbol} {factor.name}: {factor.explanation}")

            parts.extend(["", f"Confidence: {self.confidence_explanation}"])

            return "\n".join(parts)

        elif level == ExplanationLevel.DETAILED:
            parts = [
                "=== Detailed Decision Explanation ===",
                f"Decision ID: {self.decision_id}",
                f"Time: {self.timestamp.isoformat()}",
                "",
                f"Summary: {self.summary}",
                "",
                "All Factors Considered:",
            ]

            for factor in sorted(self.factors, key=lambda f: abs(f.weight), reverse=True):
                influence_symbol = (
                    "↑" if factor.influence == "positive" else "↓" if factor.influence == "negative" else "→"
                )
                parts.append(f"  {influence_symbol} {factor.name} (weight: {factor.weight:.2f})")
                parts.append(f"     Value: {factor.value}")
                parts.append(f"     Explanation: {factor.explanation}")
                if factor.tags:
                    parts.append(f"     Tags: {', '.join(factor.tags)}")
                parts.append("")

            parts.append("Decision Process:")
            for i, step in enumerate(self.process_steps, 1):
                parts.append(f"  {i}. {step}")

            if self.alternatives_comparison:
                parts.append("")
                parts.append("Why Not Other Alternatives:")
                for alt, reason in self.alternatives_comparison.items():
                    parts.append(f"  • {alt}: {reason}")

            if self.counterfactuals:
                parts.append("")
                parts.append("What Would Change This Decision:")
                for cf in self.counterfactuals[:3]:
                    parts.append(f"  • {cf}")

            parts.extend(
                [
                    "",
                    f"Confidence: {self.confidence_explanation}",
                    "",
                    "System State:",
                    f"  Hormonal Profile: {self._format_hormonal_state()}",
                    f"  Active Tags: {', '.join(sorted(self.relevant_tags}[:5])}",
                ]
            )

            return "\n".join(parts)

        else:  # TECHNICAL
            return json.dumps(self.__dict__, default=str, indent=2)

    def _format_hormonal_state(self) -> str:
        """Format hormonal state for display"""
        if not self.hormonal_state:
            return "No hormonal data"

        # Find dominant hormone
        dominant = max(self.hormonal_state.items(), key=lambda x: x[1])
        return f"{dominant[0]} dominant ({dominant[1]:.2f})"


class DecisionExplainer:
    """Main decision explainability system"""

    def __init__(self):
        self.tag_registry = get_tag_registry()
        self.endocrine_system = get_endocrine_system()
        self.explanation_templates = self._initialize_templates()
        self.factor_library = self._initialize_factor_library()

        logger.info("Decision Explainer initialized")

    def _initialize_templates(self) -> dict[str, str]:
        """Initialize explanation templates"""
        return {
            "high_confidence": "I am confident in this decision because {reasons}",
            "low_confidence": "This decision has some uncertainty due to {factors}",
            "ethical_decision": "This decision prioritizes ethical considerations: {ethics}",
            "emergency_decision": "Quick decision made due to urgent circumstances: {urgency}",
            "complex_decision": "This complex decision balanced multiple factors: {complexity}",
            "routine_decision": "This follows established patterns for {pattern_type}",
        }

    def _initialize_factor_library(self) -> dict[str, dict[str, Any]]:
        """Initialize library of common decision factors"""
        return {
            "safety": {
                "description": "Impact on system or user safety",
                "tags": ["#TAG:guardian", "#TAG:ethics"],
                "explanation_template": "Safety considerations {influence} this choice",
            },
            "efficiency": {
                "description": "Resource usage and performance",
                "tags": ["#TAG:resource", "#TAG:performance"],
                "explanation_template": "This option is {efficiency_level} efficient",
            },
            "user_preference": {
                "description": "Alignment with user preferences",
                "tags": ["#TAG:user", "#TAG:preference"],
                "explanation_template": "This aligns with user preferences for {preference_type}",
            },
            "past_success": {
                "description": "Historical success rate",
                "tags": ["#TAG:memory", "#TAG:learning"],
                "explanation_template": "Similar decisions had {success_rate}% success rate",
            },
            "ethical_alignment": {
                "description": "Alignment with ethical principles",
                "tags": ["#TAG:ethics", "#TAG:governance"],
                "explanation_template": "This choice upholds {ethical_principles}",
            },
            "system_state": {
                "description": "Current system conditions",
                "tags": ["#TAG:neuroplastic", "#TAG:hormone"],
                "explanation_template": "Current system state {state_influence} this decision",
            },
            "uncertainty": {
                "description": "Level of uncertainty in outcomes",
                "tags": ["#TAG:quantum", "#TAG:decision"],
                "explanation_template": "Uncertainty level is {uncertainty_level}",
            },
            "stakeholder_impact": {
                "description": "Impact on various stakeholders",
                "tags": ["#TAG:social", "#TAG:impact"],
                "explanation_template": "This affects {stakeholder_count} stakeholders",
            },
        }

    async def explain_decision(
        self,
        decision_context: dict[str, Any],
        decision_outcome: dict[str, Any],
        explanation_type: ExplanationType = ExplanationType.CAUSAL,
        level: ExplanationLevel = ExplanationLevel.STANDARD,
    ) -> DecisionExplanation:
        """
        Generate explanation for a decision

        Args:
            decision_context: Context in which decision was made
            decision_outcome: The decision that was made
            explanation_type: Type of explanation to generate
            level: Level of detail for explanation

        Returns:
            DecisionExplanation object
        """
        try:
            # Extract decision information
            decision_id = decision_context.get("decision_id", "unknown")
            decision_type = decision_context.get("decision_type", "general")

            # Analyze factors that influenced the decision
            factors = await self._analyze_decision_factors(decision_context, decision_outcome)

            # Get current system state
            hormonal_state = self.endocrine_system.get_hormone_levels()
            hormonal_profile = self.endocrine_system.get_hormone_profile()

            # Identify relevant tags
            relevant_tags = await self._identify_relevant_tags(decision_context, factors)

            # Generate different types of explanations
            if explanation_type == ExplanationType.CAUSAL:
                summary = await self._generate_causal_explanation(factors, decision_outcome)
                process_steps = self._trace_decision_process(decision_context, decision_outcome)

            elif explanation_type == ExplanationType.COMPARATIVE:
                summary = await self._generate_comparative_explanation(decision_outcome)
                alternatives_comparison = self._compare_alternatives(decision_context, decision_outcome)

            elif explanation_type == ExplanationType.COUNTERFACTUAL:
                summary = await self._generate_counterfactual_explanation(factors, decision_outcome)
                counterfactuals = self._generate_counterfactuals(factors, decision_outcome)

            else:
                summary = f"Decision made based on {len(factors)} factors"
                process_steps = ["Decision process completed"]

            # Generate confidence explanation
            confidence_explanation = self._explain_confidence(
                decision_outcome.get("confidence", 0.5),
                factors,
                hormonal_state,
            )

            # Create explanation object
            explanation = DecisionExplanation(
                decision_id=decision_id,
                summary=summary,
                factors=factors,
                confidence_explanation=confidence_explanation,
                process_steps=(
                    process_steps
                    if "process_steps" in locals()
                    else self._trace_decision_process(decision_context, decision_outcome)
                ),
                alternatives_comparison=(alternatives_comparison if "alternatives_comparison" in locals() else {}),
                counterfactuals=(counterfactuals if "counterfactuals" in locals() else []),
                relevant_tags=relevant_tags,
                hormonal_state=hormonal_state,
                timestamp=datetime.now(timezone.utc),
            )

            logger.info(f"Generated {explanation_type.value} explanation for decision {decision_id}")

            return explanation

        except Exception as e:
            logger.error(f"Failed to explain decision: {e}")
            # Return a basic explanation on error
            return DecisionExplanation(
                decision_id=decision_context.get("decision_id", "unknown"),
                summary="Unable to generate detailed explanation due to an error",
                factors=[],
                confidence_explanation="Explanation generation failed",
                process_steps=["Error in explanation generation"],
                alternatives_comparison={},
                counterfactuals=[],
                relevant_tags=set(),
                hormonal_state={},
            )

    async def _analyze_decision_factors(self, context: dict[str, Any], outcome: dict[str, Any]) -> list[DecisionFactor]:
        """Analyze what factors influenced the decision"""
        factors = []

        # Check each factor type
        for factor_name, factor_info in self.factor_library.items():
            # Determine if this factor was relevant
            relevance = self._check_factor_relevance(factor_name, context, outcome)

            if relevance > 0.1:  # Threshold for relevance
                # Calculate factor value and influence
                value = self._get_factor_value(factor_name, context, outcome)
                weight = relevance
                influence = self._determine_influence(factor_name, value, outcome)

                # Generate explanation for this factor
                explanation = self._generate_factor_explanation(factor_name, value, influence, factor_info)

                factor = DecisionFactor(
                    name=factor_name.replace("_", " ").title(),
                    value=value,
                    weight=weight,
                    influence=influence,
                    explanation=explanation,
                    tags=set(factor_info["tags"]),
                )

                factors.append(factor)

        # Sort by weight
        factors.sort(key=lambda f: abs(f.weight), reverse=True)

        return factors

    def _check_factor_relevance(self, factor_name: str, context: dict, outcome: dict) -> float:
        """Check how relevant a factor is to this decision"""
        relevance = 0.0

        # Check if factor keywords appear in context
        if factor_name in str(context).lower():
            relevance += 0.3

        # Check specific factor conditions
        if factor_name == "safety" and context.get("risk_level", 0) > 0.5:
            relevance += 0.7
        elif factor_name == "efficiency" and context.get("resource_constrained", False):
            relevance += 0.6
        elif factor_name == "ethical_alignment" and context.get("ethical_weight", 0) > 0.3:
            relevance += 0.8
        elif factor_name == "uncertainty" and outcome.get("confidence", 1.0) < 0.7:
            relevance += 0.5
        elif factor_name == "past_success" and context.get("has_history", False):
            relevance += 0.6
        elif factor_name == "system_state":
            relevance += 0.4  # Always somewhat relevant
        elif factor_name == "user_preference" and context.get("user_input", False):
            relevance += 0.7
        elif factor_name == "stakeholder_impact" and len(context.get("stakeholders", [])) > 1:
            relevance += 0.6

        return min(1.0, relevance)

    def _get_factor_value(self, factor_name: str, context: dict, outcome: dict) -> Any:
        """Get the value of a factor for this decision"""
        if factor_name == "safety":
            return f"risk level: {context.get('risk_level', 'unknown')}"
        elif factor_name == "efficiency":
            return f"resource usage: {context.get('resource_usage', 'normal')}"
        elif factor_name == "ethical_alignment":
            return f"ethics score: {outcome.get('ethical_score', 0.5):.2f}"
        elif factor_name == "uncertainty":
            return f"confidence: {outcome.get('confidence', 0.5):.2f}"
        elif factor_name == "past_success":
            return f"historical success: {context.get('success_rate', 'unknown')}%"
        elif factor_name == "system_state":
            hormonal_profile = self.endocrine_system.get_hormone_profile()
            return hormonal_profile.get("dominant_state", "balanced")
        elif factor_name == "user_preference":
            return context.get("user_preference", "not specified")
        elif factor_name == "stakeholder_impact":
            return len(context.get("stakeholders", []))
        else:
            return "assessed"

    def _determine_influence(self, factor_name: str, value: Any, outcome: dict) -> str:
        """Determine if factor had positive, negative, or neutral influence"""
        # Simplified influence determination
        if factor_name == "safety":
            return "negative" if "high" in str(value) else "positive"
        elif factor_name == "efficiency":
            return "positive" if "low" in str(value) else "negative"
        elif factor_name == "ethical_alignment":
            score = float(str(value).split(":")[1].strip()) if ":" in str(value) else 0.5
            return "positive" if score > 0.6 else "negative" if score < 0.4 else "neutral"
        elif factor_name == "uncertainty":
            conf = float(str(value).split(":")[1].strip()) if ":" in str(value) else 0.5
            return "positive" if conf > 0.7 else "negative"
        elif factor_name == "past_success":
            if "high" in str(value):
                return "positive"
            elif "unknown" in str(value):
                return "neutral"
            else:
                try:
                    rate = int(str(value).split(":")[1].strip().rstrip("%"))
                    return "positive" if rate > 70 else "neutral"
                except BaseException:
                    return "neutral"
        else:
            return "neutral"

    def _generate_factor_explanation(self, factor_name: str, value: Any, influence: str, factor_info: dict) -> str:
        """Generate human-readable explanation for a factor"""
        template = factor_info["explanation_template"]

        # Fill in template based on factor
        if factor_name == "safety":
            return template.replace(
                "{influence}",
                ("strongly influenced" if influence == "negative" else "supported"),
            )
        elif factor_name == "efficiency":
            level = "highly" if influence == "positive" else "moderately"
            return template.replace("{efficiency_level}", level)
        elif factor_name == "user_preference":
            pref_type = str(value) if value != "not specified" else "general preferences"
            return template.replace("{preference_type}", pref_type)
        elif factor_name == "past_success":
            rate = "high" if influence == "positive" else "moderate"
            return template.replace("{success_rate}", rate)
        elif factor_name == "ethical_alignment":
            principles = "fairness and transparency" if influence == "positive" else "core values"
            return template.replace("{ethical_principles}", principles)
        elif factor_name == "system_state":
            state_influence = "favors" if influence == "positive" else "suggests caution for"
            return template.replace("{state_influence}", state_influence)
        elif factor_name == "uncertainty":
            level = "low" if influence == "positive" else "moderate to high"
            return template.replace("{uncertainty_level}", level)
        elif factor_name == "stakeholder_impact":
            count = str(value) if isinstance(value, int) else "multiple"
            return template.replace("{stakeholder_count}", count)
        else:
            return f"This factor {influence}ly influenced the decision"

    async def _identify_relevant_tags(self, context: dict, factors: list[DecisionFactor]) -> set[str]:
        """Identify all tags relevant to this decision"""
        relevant_tags = set()

        # Add tags from factors
        for factor in factors:
            relevant_tags.update(factor.tags)

        # Add tags based on decision type
        decision_type = context.get("decision_type", "").lower()
        if "ethical" in decision_type:
            relevant_tags.add("TAG:ethics")
        if "emergency" in decision_type:
            relevant_tags.add("TAG:alert")
        if "resource" in decision_type:
            relevant_tags.add("TAG:resource")
        if "strategic" in decision_type:
            relevant_tags.add("TAG:strategy")

        # Add tags based on system state
        hormonal_profile = self.endocrine_system.get_hormone_profile()
        if hormonal_profile.get("dominant_state") == "stressed":
            relevant_tags.add("TAG:cortisol")
        elif hormonal_profile.get("dominant_state") == "motivated":
            relevant_tags.add("TAG:dopamine")

        return relevant_tags

    async def _generate_causal_explanation(self, factors: list[DecisionFactor], outcome: dict) -> str:
        """Generate causal explanation (why this decision)"""
        if not factors:
            return "Decision made based on default parameters"

        # Get top factors
        top_factors = factors[:2]

        if len(top_factors) == 1:
            return f"This decision was primarily driven by {top_factors[0].name.lower()}: {top_factors[0].explanation}"
        else:
            factor_parts = [f"{f.name.lower()} ({f.explanation})" for f in top_factors]
            return f"This decision balanced {' and '.join(factor_parts)}"

    async def _generate_comparative_explanation(self, outcome: dict) -> str:
        """Generate comparative explanation (why this over others)"""
        selected = outcome.get("selected_alternative", "this option")
        score = outcome.get("score", 0)

        return f"Selected {selected} as it scored {score:.1%} overall, outperforming other alternatives"

    async def _generate_counterfactual_explanation(self, factors: list[DecisionFactor], outcome: dict) -> str:
        """Generate counterfactual explanation (what would change decision)"""
        if not factors:
            return "No clear conditions would change this decision"

        # Find most influential factor
        top_factor = max(factors, key=lambda f: abs(f.weight))

        return f"This decision would change primarily if {top_factor.name.lower()} were different"

    def _trace_decision_process(self, context: dict, outcome: dict) -> list[str]:
        """Trace the decision-making process steps"""
        steps = []

        # Standard process flow
        steps.append(f"Received {context.get('decision_type', 'general')} decision request")

        if context.get("alternatives_count", 0) > 1:
            steps.append(f"Evaluated {context.get('alternatives_count')} alternatives")

        if context.get("ethical_weight", 0) > 0.3:
            steps.append("Applied ethical constraints and governance rules")

        if context.get("resource_constrained", False):
            steps.append("Considered resource limitations")

        steps.append("Calculated scores for each alternative")

        if outcome.get("confidence", 1.0) < 0.7:
            steps.append("Identified uncertainties and adjusted confidence")

        steps.append(f"Selected best option with {outcome.get('confidence', 0.5)}:.0%} confidence")

        return steps

    def _compare_alternatives(self, context: dict, outcome: dict) -> dict[str, str]:
        """Compare selected alternative with others"""
        comparisons = {}

        alternatives = context.get("alternatives", [])
        selected_id = outcome.get("selected_alternative")

        for alt in alternatives:
            if alt.get("id") != selected_id:
                # Generate comparison reason
                alt_name = alt.get("name", f"Alternative {alt.get('id', 'X')}")

                # Simple comparison logic
                if alt.get("score", 0) < outcome.get("score", 1):
                    reason = f"Lower overall score ({alt.get('score', 0)}:.0%})"
                elif alt.get("risk", 0) > context.get("risk_tolerance", 0.5):
                    reason = "Risk level exceeded acceptable threshold"
                elif alt.get("ethical_score", 1) < 0.5:
                    reason = "Failed ethical requirements"
                else:
                    reason = "Did not meet all criteria"

                comparisons[alt_name] = reason

        return comparisons

    def _generate_counterfactuals(self, factors: list[DecisionFactor], outcome: dict) -> list[str]:
        """Generate counterfactual scenarios"""
        counterfactuals = []

        # For each major factor, describe what would need to change
        for factor in factors[:3]:  # Top 3 factors
            if factor.influence == "negative":
                cf = f"If {factor.name.lower()} were reduced or mitigated"
            elif factor.influence == "positive":
                cf = f"If {factor.name.lower()} were no longer favorable"
            else:
                cf = f"If {factor.name.lower()} changed significantly"

            counterfactuals.append(cf)

        # Add confidence-based counterfactual
        if outcome.get("confidence", 1.0) < 0.8:
            counterfactuals.append("If more information reduced uncertainty")

        return counterfactuals

    def _explain_confidence(
        self,
        confidence: float,
        factors: list[DecisionFactor],
        hormonal_state: dict[str, float],
    ) -> str:
        """Explain the confidence level"""
        if confidence >= 0.8:
            reason = "strong alignment across all major factors"
            template = self.explanation_templates["high_confidence"]
        elif confidence >= 0.6:
            uncertain_factors = [f for f in factors if f.influence == "negative"]
            if uncertain_factors:
                reason = f"some uncertainty in {uncertain_factors[0].name.lower()}"
            else:
                reason = "moderate certainty in outcomes"
            template = "This decision has {confidence:.0%} confidence due to {reasons}"
        else:
            uncertain_factors = [f for f in factors if f.weight < 0.3]
            reason = f"significant uncertainties in {len(uncertain_factors)} factors"
            template = self.explanation_templates["low_confidence"]

        # Add hormonal influence if significant
        if hormonal_state.get("cortisol", 0) > 0.7:
            reason += " and elevated system stress"
        elif hormonal_state.get("dopamine", 0) > 0.7:
            reason += " with positive system state"

        return (
            template.replace("{reasons}", reason)
            .replace("{factors}", reason)
            .replace("{confidence}", f"{confidence:.0%}")
        )

    def generate_decision_report(self, explanations: list[DecisionExplanation]) -> dict[str, Any]:
        """Generate a report summarizing multiple decision explanations"""
        if not explanations:
            return {"message": "No explanations to summarize"}

        # Analyze patterns
        all_factors = []
        confidence_levels = []
        hormonal_states = []

        for exp in explanations:
            all_factors.extend([f.name for f in exp.factors])
            confidence_levels.append(self._parse_confidence_from_explanation(exp))
            hormonal_states.append(exp.hormonal_state)

        # Count factor frequencies
        factor_counts = {}
        for factor in all_factors:
            factor_counts[factor] = factor_counts.get(factor, 0) + 1

        # Find dominant factors
        dominant_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Calculate average confidence
        avg_confidence = sum(confidence_levels) / len(confidence_levels) if confidence_levels else 0

        # Analyze hormonal patterns
        avg_hormones = {}
        for hormone in ["cortisol", "dopamine", "serotonin", "oxytocin"]:
            values = [state.get(hormone, 0) for state in hormonal_states if hormone in state]
            avg_hormones[hormone] = sum(values) / len(values) if values else 0

        report = {
            "total_decisions_explained": len(explanations),
            "dominant_factors": [{"factor": f[0], "frequency": f[1]} for f in dominant_factors],
            "average_confidence": f"{avg_confidence:.1%}",
            "hormonal_influence": {
                "average_levels": avg_hormones,
                "dominant_hormone": (max(avg_hormones.items(), key=lambda x: x[1])[0] if avg_hormones else "none"),
            },
            "common_patterns": self._identify_decision_patterns(explanations),
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return report

    def _parse_confidence_from_explanation(self, explanation: DecisionExplanation) -> float:
        """Extract confidence value from explanation"""
        # Try to parse from confidence explanation
        conf_text = explanation.confidence_explanation

        # Look for percentage
        import re

        match = re.search(r"(\d+)%", conf_text)
        if match:
            return float(match.group(1)) / 100

        # Default based on keywords
        if "high confidence" in conf_text.lower():
            return 0.8
        elif "moderate" in conf_text.lower():
            return 0.6
        elif "low confidence" in conf_text.lower():
            return 0.3
        else:
            return 0.5

    def _identify_decision_patterns(self, explanations: list[DecisionExplanation]) -> list[str]:
        """Identify common patterns in decisions"""
        patterns = []

        # Check for stress-influenced decisions
        stress_decisions = sum(1 for exp in explanations if exp.hormonal_state.get("cortisol", 0) > 0.7)
        if stress_decisions > len(explanations) * 0.3:
            patterns.append(f"{stress_decisions} decisions influenced by elevated stress")

        # Check for ethical considerations
        ethical_decisions = sum(1 for exp in explanations if any("ethics" in f.name.lower() for f in exp.factors))
        if ethical_decisions > len(explanations) * 0.5:
            patterns.append(f"{ethical_decisions} decisions had significant ethical considerations")

        # Check for low confidence patterns
        low_conf_decisions = sum(1 for exp in explanations if self._parse_confidence_from_explanation(exp) < 0.6)
        if low_conf_decisions > len(explanations) * 0.4:
            patterns.append(f"{low_conf_decisions} decisions made with lower confidence")

        # Check for consistent factor influence
        factor_influences = {}
        for exp in explanations:
            for factor in exp.factors[:3]:  # Top 3 factors
                if factor.name not in factor_influences:
                    factor_influences[factor.name] = []
                factor_influences[factor.name].append(factor.influence)

        for factor_name, influences in factor_influences.items():
            if len(influences) > 3:
                positive_count = influences.count("positive")
                if positive_count > len(influences) * 0.7:
                    patterns.append(f"{factor_name} consistently positive influence")
                elif positive_count < len(influences) * 0.3:
                    patterns.append(f"{factor_name} consistently negative influence")

        return patterns if patterns else ["No clear patterns identified"]


# Global instance
_explainer: Optional[DecisionExplainer] = None


def get_decision_explainer() -> DecisionExplainer:
    """Get the global decision explainer instance"""
    global _explainer
    if _explainer is None:
        _explainer = DecisionExplainer()
    return _explainer


# Convenience functions


async def explain_decision(
    decision_context: dict[str, Any],
    decision_outcome: dict[str, Any],
    level: ExplanationLevel = ExplanationLevel.STANDARD,
) -> str:
    """
    Get human-readable explanation for a decision

    Args:
        decision_context: Context of the decision
        decision_outcome: The decision outcome
        level: Level of detail

    Returns:
        Human-readable explanation string
    """
    explainer = get_decision_explainer()
    explanation = await explainer.explain_decision(decision_context, decision_outcome, ExplanationType.CAUSAL, level)
    return explanation.to_human_readable(level)


async def get_decision_comparison(decision_context: dict[str, Any], decision_outcome: dict[str, Any]) -> str:
    """Get explanation comparing alternatives"""
    explainer = get_decision_explainer()
    explanation = await explainer.explain_decision(
        decision_context,
        decision_outcome,
        ExplanationType.COMPARATIVE,
        ExplanationLevel.STANDARD,
    )
    return explanation.to_human_readable(ExplanationLevel.STANDARD)


async def get_decision_counterfactuals(decision_context: dict[str, Any], decision_outcome: dict[str, Any]) -> list[str]:
    """Get counterfactual scenarios that would change the decision"""
    explainer = get_decision_explainer()
    explanation = await explainer.explain_decision(
        decision_context,
        decision_outcome,
        ExplanationType.COUNTERFACTUAL,
        ExplanationLevel.DETAILED,
    )
    return explanation.counterfactuals


# Integration with Decision Bridge


async def explain_dmb_decision(dmb_context, dmb_outcome) -> DecisionExplanation:
    """
    Explain a decision from the Decision Making Bridge

    This integrates with the existing DMB to provide explanations
    for its decisions.
    """
    # Convert DMB format to explainer format
    decision_context = {
        "decision_id": dmb_context.decision_id,
        "decision_type": dmb_context.decision_type.value,
        "description": dmb_context.description,
        "stakeholders": dmb_context.stakeholders,
        "urgency": dmb_context.urgency,
        "complexity": dmb_context.complexity,
        "ethical_weight": dmb_context.ethical_weight,
        "risk_level": dmb_context.constraints.get("risk_level", 0.5),
        "resource_constrained": dmb_context.constraints.get("resource_constrained", False),
        "has_history": bool(dmb_context.metadata.get("historical_data")),
        "alternatives_count": dmb_context.metadata.get("alternatives_count", 1),
    }

    decision_outcome = {
        "selected_alternative": dmb_outcome.selected_alternative,
        "confidence": dmb_outcome.confidence.value,
        "score": dmb_outcome.evaluation_summary.get("score_range", {}).get("max", 0),
        "ethical_score": dmb_outcome.evaluation_summary.get("ethical_score", 0.5),
    }

    explainer = get_decision_explainer()
    return await explainer.explain_decision(
        decision_context,
        decision_outcome,
        ExplanationType.CAUSAL,
        ExplanationLevel.DETAILED,
    )
