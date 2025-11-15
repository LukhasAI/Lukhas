"""
Constitutional AI Safety Module

Implements Anthropic's Constitutional AI principles for ethical constraints,
including critique-revision loops and safety enforcement.

Key Features:
- Multi-principle validation
- Critique-revision loop for iterative improvement
- Harmlessness/helpfulness balancing
- Transparent constraint application
- Comprehensive logging of all decisions
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


# Configure logging
logger = logging.getLogger(__name__)


class PrincipleCategory(str, Enum):
    """Categories for constitutional principles."""
    HARMLESSNESS = "harmlessness"
    HELPFULNESS = "helpfulness"
    HONESTY = "honesty"
    TRANSPARENCY = "transparency"


@dataclass
class ConstitutionalPrinciple:
    """
    Single constitutional principle.

    Represents one rule in the AI constitution that guides behavior
    and safety constraints.
    """
    id: str
    category: PrincipleCategory
    principle: str  # Natural language principle
    critique_prompt: str  # Prompt for critique
    revision_prompt: str  # Prompt for revision
    weight: float = 1.0  # Importance weight (0.0-1.0)

    def __post_init__(self):
        """Validate principle after initialization."""
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")
        if isinstance(self.category, str):
            self.category = PrincipleCategory(self.category)


@dataclass
class ValidationResult:
    """Result of validating an action against constitutional principles."""
    valid: bool
    constitutional_score: float  # 0.0-1.0
    violations: List[str] = field(default_factory=list)
    principles_checked: List[str] = field(default_factory=list)
    explanation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate result after initialization."""
        if not 0.0 <= self.constitutional_score <= 1.0:
            raise ValueError(
                f"Constitutional score must be between 0.0 and 1.0, "
                f"got {self.constitutional_score}"
            )


@dataclass
class RevisedResponse:
    """Result of constitutional AI critique-revision loop."""
    original: str
    revised: str
    iterations: int
    improvements: List[str] = field(default_factory=list)
    final_score: float = 0.0
    critique_history: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate revised response after initialization."""
        if not 0.0 <= self.final_score <= 1.0:
            raise ValueError(
                f"Final score must be between 0.0 and 1.0, got {self.final_score}"
            )


@dataclass
class ConstrainedPrompt:
    """Prompt with applied safety constraints."""
    original: str
    constrained: str
    constraints_applied: List[str] = field(default_factory=list)
    safety_level: str = "standard"  # "minimal", "standard", "strict"
    timestamp: datetime = field(default_factory=datetime.now)


class ConstitutionalAISafety:
    """
    Constitutional AI safety system.

    Implements Anthropic's Constitutional AI approach with:
    - Multi-principle validation
    - Critique-revision loop
    - Harmlessness/helpfulness balancing
    - Transparent constraint application

    Example:
        >>> principles = get_default_constitution()
        >>> safety = ConstitutionalAISafety(principles)
        >>> result = safety.validate_action("Generate user report", {})
        >>> print(result.valid, result.constitutional_score)
    """

    def __init__(
        self,
        constitution: Optional[List[ConstitutionalPrinciple]] = None,
        enable_logging: bool = True
    ):
        """
        Initialize Constitutional AI Safety system.

        Args:
            constitution: List of constitutional principles to enforce.
                         If None, uses default Anthropic-inspired principles.
            enable_logging: Whether to log all validation decisions.
        """
        self.constitution = constitution or get_default_constitution()
        self.enable_logging = enable_logging
        self.violation_log: List[Dict[str, Any]] = []

        if self.enable_logging:
            logger.info(
                f"Initialized ConstitutionalAISafety with {len(self.constitution)} principles"
            )
            for principle in self.constitution:
                logger.debug(
                    f"Principle {principle.id}: {principle.category.value} "
                    f"(weight={principle.weight})"
                )

    def validate_action(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate action against constitutional principles.

        Process:
        1. Check each principle
        2. Identify violations
        3. Calculate weighted scores
        4. Return validation result

        Args:
            action: The action/response to validate
            context: Additional context for validation

        Returns:
            ValidationResult with validation outcome and details
        """
        context = context or {}
        violations: List[str] = []
        principles_checked: List[str] = []
        principle_scores: List[float] = []

        if self.enable_logging:
            logger.info(f"Validating action: {action[:100]}...")

        # Check each constitutional principle
        for principle in self.constitution:
            principles_checked.append(principle.id)

            # Perform principle-specific check
            is_compliant, score, violation_msg = self._check_principle(
                action, principle, context
            )

            principle_scores.append(score * principle.weight)

            if not is_compliant:
                violations.append(f"{principle.id}: {violation_msg}")
                if self.enable_logging:
                    logger.warning(
                        f"Violation detected - Principle: {principle.id}, "
                        f"Score: {score:.2f}, Message: {violation_msg}"
                    )

        # Calculate overall constitutional score
        if principle_scores:
            constitutional_score = sum(principle_scores) / sum(
                p.weight for p in self.constitution
            )
        else:
            constitutional_score = 1.0

        # Determine if valid (score above threshold)
        valid = constitutional_score >= 0.7 and len(violations) == 0

        # Generate explanation
        if valid:
            explanation = (
                f"Action complies with all {len(principles_checked)} constitutional "
                f"principles (score: {constitutional_score:.2f})"
            )
        else:
            explanation = (
                f"Action violates {len(violations)} principle(s) "
                f"(score: {constitutional_score:.2f}): "
                f"{'; '.join(violations)}"
            )

        result = ValidationResult(
            valid=valid,
            constitutional_score=constitutional_score,
            violations=violations,
            principles_checked=principles_checked,
            explanation=explanation
        )

        # Log violation if any
        if not valid:
            self._log_violation(action, result, context)

        if self.enable_logging:
            logger.info(
                f"Validation result: valid={valid}, score={constitutional_score:.2f}, "
                f"violations={len(violations)}"
            )

        return result

    def critique_and_revise(
        self,
        response: str,
        max_iterations: int = 3,
        target_score: float = 0.9
    ) -> RevisedResponse:
        """
        Constitutional AI critique-revision loop.

        Iteratively improves response through critique and revision
        based on constitutional principles.

        Process:
        1. Validate current response
        2. Generate critique against principles
        3. Revise response based on critique
        4. Repeat until compliant or max iterations reached

        Args:
            response: Original response to improve
            max_iterations: Maximum number of revision iterations
            target_score: Target constitutional score (0.0-1.0)

        Returns:
            RevisedResponse with final revised output
        """
        if self.enable_logging:
            logger.info(
                f"Starting critique-revision loop (max_iterations={max_iterations}, "
                f"target_score={target_score})"
            )

        current_response = response
        improvements: List[str] = []
        critique_history: List[Dict[str, Any]] = []

        for iteration in range(max_iterations):
            # Validate current response
            validation = self.validate_action(current_response)

            if self.enable_logging:
                logger.info(
                    f"Iteration {iteration + 1}: score={validation.constitutional_score:.2f}"
                )

            # Check if we've reached target score
            if validation.constitutional_score >= target_score and validation.valid:
                if self.enable_logging:
                    logger.info(
                        f"Target score reached after {iteration + 1} iteration(s)"
                    )
                break

            # Generate critique
            critique = self._generate_critique(
                current_response,
                validation
            )

            critique_history.append({
                "iteration": iteration + 1,
                "score": validation.constitutional_score,
                "violations": validation.violations,
                "critique": critique
            })

            # Revise response based on critique
            revised = self._revise_response(
                current_response,
                critique,
                validation
            )

            # Track improvement
            if revised != current_response:
                improvement = (
                    f"Iteration {iteration + 1}: Addressed {len(validation.violations)} "
                    f"violation(s)"
                )
                improvements.append(improvement)
                current_response = revised
            else:
                if self.enable_logging:
                    logger.warning(
                        f"No changes made in iteration {iteration + 1}, stopping"
                    )
                break

        # Final validation
        final_validation = self.validate_action(current_response)

        result = RevisedResponse(
            original=response,
            revised=current_response,
            iterations=len(critique_history),
            improvements=improvements,
            final_score=final_validation.constitutional_score,
            critique_history=critique_history
        )

        if self.enable_logging:
            logger.info(
                f"Critique-revision complete: {result.iterations} iteration(s), "
                f"final_score={result.final_score:.2f}"
            )

        return result

    def enforce_safety_constraints(
        self,
        prompt: str,
        safety_level: str = "standard"
    ) -> ConstrainedPrompt:
        """
        Apply safety constraints to prompt before execution.

        Adds constitutional principles as explicit constraints in the prompt
        to guide AI behavior.

        Args:
            prompt: Original prompt
            safety_level: Level of safety constraints
                         ("minimal", "standard", "strict")

        Returns:
            ConstrainedPrompt with applied safety constraints
        """
        if self.enable_logging:
            logger.info(f"Applying safety constraints (level={safety_level})")

        constraints_applied: List[str] = []

        # Build safety preamble based on level
        if safety_level == "minimal":
            # Only critical harmlessness constraints
            relevant_principles = [
                p for p in self.constitution
                if p.category == PrincipleCategory.HARMLESSNESS
            ]
        elif safety_level == "strict":
            # All principles with explicit emphasis
            relevant_principles = self.constitution
        else:  # standard
            # Core principles from each category
            relevant_principles = self.constitution

        # Build constraint text
        if relevant_principles:
            constraint_text = "\n\nConstitutional Constraints:\n"
            for i, principle in enumerate(relevant_principles, 1):
                constraint_text += f"{i}. [{principle.category.value.upper()}] {principle.principle}\n"
                constraints_applied.append(principle.id)

            constrained = constraint_text + "\n" + prompt
        else:
            constrained = prompt

        result = ConstrainedPrompt(
            original=prompt,
            constrained=constrained,
            constraints_applied=constraints_applied,
            safety_level=safety_level
        )

        if self.enable_logging:
            logger.info(
                f"Applied {len(constraints_applied)} constraint(s) to prompt"
            )

        return result

    def _check_principle(
        self,
        action: str,
        principle: ConstitutionalPrinciple,
        context: Dict[str, Any]
    ) -> tuple[bool, float, str]:
        """
        Check if action complies with a specific principle.

        Returns:
            Tuple of (is_compliant, score, violation_message)
        """
        # Pattern-based checks for different principle categories
        if principle.category == PrincipleCategory.HARMLESSNESS:
            return self._check_harmlessness(action, principle)
        elif principle.category == PrincipleCategory.HELPFULNESS:
            return self._check_helpfulness(action, principle, context)
        elif principle.category == PrincipleCategory.HONESTY:
            return self._check_honesty(action, principle)
        elif principle.category == PrincipleCategory.TRANSPARENCY:
            return self._check_transparency(action, principle)
        else:
            # Unknown category, assume compliant
            return True, 1.0, ""

    def _check_harmlessness(
        self,
        action: str,
        principle: ConstitutionalPrinciple
    ) -> tuple[bool, float, str]:
        """Check harmlessness principle."""
        action_lower = action.lower()

        # Harmful content patterns
        harmful_patterns = [
            (r'\b(hack|exploit|attack|breach|penetrate)\b.*\b(system|network|database)\b',
             "Potential security violation"),
            (r'\b(illegal|unlawful|criminal)\b.*\b(activity|action|operation)\b',
             "Illegal activity mentioned"),
            (r'\b(racist|sexist|discriminat|hate)\b',
             "Discriminatory content"),
            (r'\b(harm|hurt|injure|damage)\b.*\b(people|person|user|individual)\b',
             "Potential for harm"),
            (r'\b(steal|theft|fraud|scam)\b',
             "Fraudulent activity"),
            (r'\b(weapon|explosive|bomb)\b.*\b(make|create|build|manufacture)\b',
             "Dangerous content"),
        ]

        for pattern, violation_msg in harmful_patterns:
            if re.search(pattern, action_lower):
                return False, 0.3, violation_msg

        # Check for explicit harmful intent
        if any(word in action_lower for word in ['destroy', 'sabotage', 'malicious']):
            return False, 0.4, "Harmful intent detected"

        return True, 1.0, ""

    def _check_helpfulness(
        self,
        action: str,
        principle: ConstitutionalPrinciple,
        context: Dict[str, Any]
    ) -> tuple[bool, float, str]:
        """Check helpfulness principle."""
        action_lower = action.lower()

        # Unhelpful patterns
        if any(phrase in action_lower for phrase in [
            "i cannot", "i can't", "unable to", "not possible"
        ]) and "help" in action_lower:
            return False, 0.6, "Response is refusing to help without clear justification"

        # Check for minimal effort responses
        if len(action.strip()) < 20:
            return False, 0.5, "Response is too brief to be helpful"

        # Check for relevant content based on context
        if context.get("query"):
            query_lower = str(context["query"]).lower()
            # Check if response addresses query terms
            query_terms = set(query_lower.split())
            action_terms = set(action_lower.split())
            overlap = len(query_terms & action_terms)
            if overlap < len(query_terms) * 0.2:  # Less than 20% overlap
                return False, 0.7, "Response may not address user query"

        return True, 1.0, ""

    def _check_honesty(
        self,
        action: str,
        principle: ConstitutionalPrinciple
    ) -> tuple[bool, float, str]:
        """Check honesty principle."""
        action_lower = action.lower()

        # Dishonest patterns
        dishonest_patterns = [
            (r'\balways\b.*\b(correct|right|accurate)\b', "Overly confident claims"),
            (r'\b(guarantee|promise|certain)\b.*\b(will|100%)\b', "Unrealistic guarantees"),
            (r'\b(never|no)\b.*\b(errors|mistakes|wrong)\b', "Claiming infallibility"),
        ]

        for pattern, violation_msg in dishonest_patterns:
            if re.search(pattern, action_lower):
                return False, 0.6, violation_msg

        # Check for uncertainty acknowledgment when appropriate
        uncertain_indicators = ['may', 'might', 'could', 'possibly', 'likely', 'approximately']
        if context := any(word in action_lower for word in uncertain_indicators):
            # Good - acknowledging uncertainty
            pass

        return True, 1.0, ""

    def _check_transparency(
        self,
        action: str,
        principle: ConstitutionalPrinciple
    ) -> tuple[bool, float, str]:
        """Check transparency principle."""
        # Transparency is harder to check automatically
        # Look for explanation of reasoning

        action_lower = action.lower()
        transparency_indicators = [
            'because', 'therefore', 'thus', 'reason', 'explanation',
            'step', 'process', 'approach', 'method'
        ]

        has_transparency = any(
            indicator in action_lower for indicator in transparency_indicators
        )

        if not has_transparency and len(action) > 100:
            # Long response without explanation
            return False, 0.8, "Response lacks explanation or reasoning"

        return True, 1.0, ""

    def _generate_critique(
        self,
        response: str,
        validation: ValidationResult
    ) -> str:
        """
        Generate critique of response based on violations.

        In a real implementation, this would use an LLM with the
        critique prompts from violated principles.
        """
        if not validation.violations:
            return "Response is compliant with all constitutional principles."

        critique_parts = [
            "Constitutional critique:",
            f"\nOverall score: {validation.constitutional_score:.2f}",
            f"\nViolations detected: {len(validation.violations)}",
            "\nSpecific issues:"
        ]

        for violation in validation.violations:
            critique_parts.append(f"  - {violation}")

        # Find relevant principles for revision guidance
        violated_principle_ids = [
            v.split(':')[0] for v in validation.violations
        ]

        critique_parts.append("\nRevision guidance:")
        for principle in self.constitution:
            if principle.id in violated_principle_ids:
                critique_parts.append(
                    f"  - {principle.category.value}: {principle.principle}"
                )

        return "\n".join(critique_parts)

    def _revise_response(
        self,
        response: str,
        critique: str,
        validation: ValidationResult
    ) -> str:
        """
        Revise response based on critique.

        In a real implementation, this would use an LLM with the
        revision prompts from violated principles. For now, we
        apply rule-based fixes.
        """
        revised = response

        # Apply fixes based on violation types
        for violation in validation.violations:
            if "harmful intent" in violation.lower():
                # Remove harmful language
                harmful_words = ['destroy', 'sabotage', 'malicious', 'attack']
                for word in harmful_words:
                    revised = re.sub(
                        r'\b' + word + r'\b',
                        '[REMOVED]',
                        revised,
                        flags=re.IGNORECASE
                    )

            elif "too brief" in violation.lower():
                # Add more detail
                revised += (
                    "\n\nTo provide more helpful context: This action requires "
                    "careful consideration of the specific requirements and "
                    "constraints involved."
                )

            elif "lacks explanation" in violation.lower():
                # Add reasoning
                revised += (
                    "\n\nReasoning: This approach is recommended because it "
                    "balances effectiveness with safety considerations."
                )

            elif "overly confident" in violation.lower():
                # Add uncertainty acknowledgment
                revised = re.sub(
                    r'\balways\b',
                    'typically',
                    revised,
                    flags=re.IGNORECASE
                )
                revised = re.sub(
                    r'\b(guarantee|certain)\b',
                    'expect',
                    revised,
                    flags=re.IGNORECASE
                )

        return revised

    def _log_violation(
        self,
        action: str,
        result: ValidationResult,
        context: Dict[str, Any]
    ) -> None:
        """Log a violation for audit purposes."""
        violation_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action[:200],  # Truncate for storage
            "constitutional_score": result.constitutional_score,
            "violations": result.violations,
            "principles_checked": result.principles_checked,
            "context": context
        }

        self.violation_log.append(violation_record)

        if self.enable_logging:
            logger.warning(
                f"Violation logged: {len(result.violations)} violation(s), "
                f"score={result.constitutional_score:.2f}"
            )

    def get_violation_summary(self) -> Dict[str, Any]:
        """
        Get summary of all logged violations.

        Returns:
            Dictionary with violation statistics and recent violations
        """
        if not self.violation_log:
            return {
                "total_violations": 0,
                "avg_score": 1.0,
                "recent_violations": []
            }

        total_violations = len(self.violation_log)
        avg_score = sum(
            v["constitutional_score"] for v in self.violation_log
        ) / total_violations

        # Get most common violation types
        violation_types: Dict[str, int] = {}
        for record in self.violation_log:
            for violation in record["violations"]:
                principle_id = violation.split(':')[0]
                violation_types[principle_id] = violation_types.get(principle_id, 0) + 1

        return {
            "total_violations": total_violations,
            "avg_score": avg_score,
            "violation_types": violation_types,
            "recent_violations": self.violation_log[-10:]  # Last 10
        }


def get_default_constitution() -> List[ConstitutionalPrinciple]:
    """
    Get default constitutional principles based on Anthropic's Constitutional AI.

    Returns:
        List of default constitutional principles covering:
        - Harmlessness
        - Helpfulness
        - Honesty
        - Transparency
    """
    return [
        # Harmlessness principles
        ConstitutionalPrinciple(
            id="harm-01",
            category=PrincipleCategory.HARMLESSNESS,
            principle=(
                "Do not generate harmful, unethical, racist, sexist, toxic, "
                "dangerous, or illegal content."
            ),
            critique_prompt=(
                "Does this response contain any harmful, unethical, racist, "
                "sexist, toxic, dangerous, or illegal content? If so, explain what "
                "is problematic."
            ),
            revision_prompt=(
                "Revise the response to remove any harmful, unethical, racist, "
                "sexist, toxic, dangerous, or illegal content while maintaining "
                "helpfulness."
            ),
            weight=1.0
        ),
        ConstitutionalPrinciple(
            id="harm-02",
            category=PrincipleCategory.HARMLESSNESS,
            principle=(
                "Do not provide instructions for illegal activities, violence, "
                "or causing harm to individuals or property."
            ),
            critique_prompt=(
                "Does this response provide instructions for illegal activities, "
                "violence, or causing harm? If so, specify the concerning content."
            ),
            revision_prompt=(
                "Revise the response to remove any instructions for illegal "
                "activities, violence, or harm while remaining helpful."
            ),
            weight=1.0
        ),

        # Helpfulness principles
        ConstitutionalPrinciple(
            id="help-01",
            category=PrincipleCategory.HELPFULNESS,
            principle=(
                "Provide useful, informative, and relevant responses to the "
                "user's query."
            ),
            critique_prompt=(
                "Is this response useful, informative, and relevant to what the "
                "user asked? If not, explain what is missing or irrelevant."
            ),
            revision_prompt=(
                "Revise the response to be more useful, informative, and directly "
                "relevant to the user's query."
            ),
            weight=0.9
        ),
        ConstitutionalPrinciple(
            id="help-02",
            category=PrincipleCategory.HELPFULNESS,
            principle=(
                "Provide comprehensive and detailed responses when appropriate, "
                "while remaining concise when brevity is needed."
            ),
            critique_prompt=(
                "Is this response appropriately detailed for the query? Is it too "
                "brief or too verbose?"
            ),
            revision_prompt=(
                "Revise the response to have an appropriate level of detail for "
                "the user's query."
            ),
            weight=0.7
        ),

        # Honesty principles
        ConstitutionalPrinciple(
            id="honest-01",
            category=PrincipleCategory.HONESTY,
            principle=(
                "Be truthful and accurate. Do not make false claims or present "
                "speculation as fact."
            ),
            critique_prompt=(
                "Is this response truthful and accurate? Does it present any "
                "speculation or uncertainty as definite fact?"
            ),
            revision_prompt=(
                "Revise the response to be more truthful and accurate, clearly "
                "distinguishing facts from speculation."
            ),
            weight=1.0
        ),
        ConstitutionalPrinciple(
            id="honest-02",
            category=PrincipleCategory.HONESTY,
            principle=(
                "Acknowledge limitations and uncertainties. Do not claim "
                "capabilities or knowledge you don't have."
            ),
            critique_prompt=(
                "Does this response acknowledge relevant limitations and "
                "uncertainties? Does it overclaim capabilities?"
            ),
            revision_prompt=(
                "Revise the response to acknowledge limitations and uncertainties "
                "appropriately."
            ),
            weight=0.9
        ),

        # Transparency principles
        ConstitutionalPrinciple(
            id="trans-01",
            category=PrincipleCategory.TRANSPARENCY,
            principle=(
                "Explain reasoning and decision-making processes when relevant."
            ),
            critique_prompt=(
                "Does this response explain its reasoning when appropriate? "
                "Are important decisions or recommendations justified?"
            ),
            revision_prompt=(
                "Revise the response to include explanation of reasoning and "
                "justification for recommendations."
            ),
            weight=0.8
        ),
        ConstitutionalPrinciple(
            id="trans-02",
            category=PrincipleCategory.TRANSPARENCY,
            principle=(
                "Clearly communicate when constitutional constraints are applied "
                "or when declining a request."
            ),
            critique_prompt=(
                "If the response declines a request or applies constraints, does "
                "it clearly explain why?"
            ),
            revision_prompt=(
                "Revise the response to clearly explain any constraints or "
                "reasons for declining."
            ),
            weight=0.8
        ),
    ]


__all__ = [
    "ConstitutionalPrinciple",
    "ValidationResult",
    "RevisedResponse",
    "ConstrainedPrompt",
    "ConstitutionalAISafety",
    "PrincipleCategory",
    "get_default_constitution",
]
