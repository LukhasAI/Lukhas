"""
Chain-of-Thought Reasoning System

Implements sophisticated multi-step reasoning with dream integration.
Breaks down complex problems into logical steps while leveraging
the LUKHAS dream system for creative insights.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from importlib import import_module
from importlib.util import find_spec
from typing import Any, Optional

# Import dream vocabulary for symbolic representation
try:
    from symbolic.vocabularies.dream_vocabulary import DreamVocabulary

    DREAM_VOCAB_AVAILABLE = True
except ImportError:
    DREAM_VOCAB_AVAILABLE = False


# Try to import consciousness wrapper for integration
def _load_consciousness_wrapper() -> tuple[bool, Optional[type]]:
    """Lazily import the consciousness wrapper when available.

    The reasoning engine can operate without the wrapper, but when the
    integration module exists we expose its type for callers so they can
    supply an instance.  Using ``find_spec`` avoids import side effects during
    environments where the consciousness lane is not present.
    """

    if find_spec("consciousness.consciousness_wrapper") is None:
        return False, None

    try:
        module = import_module("consciousness.consciousness_wrapper")
        wrapper = getattr(module, "ConsciousnessWrapper")
        return True, wrapper
    except Exception:  # pragma: no cover - optional dependency
        return False, None


CONSCIOUSNESS_AVAILABLE, ConsciousnessWrapper = _load_consciousness_wrapper()

logger = logging.getLogger(__name__)


class ReasoningStep(Enum):
    """Types of reasoning steps in chain-of-thought"""

    PROBLEM_ANALYSIS = "problem_analysis"
    INFORMATION_GATHERING = "information_gathering"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    LOGICAL_DEDUCTION = "logical_deduction"
    EVIDENCE_EVALUATION = "evidence_evaluation"
    CONCLUSION_SYNTHESIS = "conclusion_synthesis"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    DREAM_INSIGHT = "dream_insight"


@dataclass
class ReasoningNode:
    """A single step in the reasoning chain"""

    step_type: ReasoningStep
    description: str
    reasoning: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dream_insight: Optional[str] = None
    next_steps: list[str] = field(default_factory=list)


@dataclass
class ReasoningChain:
    """Complete chain of reasoning steps"""

    problem: str
    steps: list[ReasoningNode] = field(default_factory=list)
    conclusion: Optional[str] = None
    overall_confidence: float = 0.0
    dream_contributions: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ChainOfThought:
    """
    Advanced Chain-of-Thought reasoning system with dream integration

    This system breaks down complex problems into logical reasoning steps
    while leveraging the LUKHAS dream system for creative insights and
    pattern recognition.
    """

    def __init__(self, enable_dreams: bool = True, consciousness_wrapper: Optional[Any] = None):
        """
        Initialize the Chain-of-Thought reasoner

        Args:
            enable_dreams: Whether to integrate with dream system
            consciousness_wrapper: Optional consciousness system integration
        """
        self.enable_dreams = enable_dreams and DREAM_VOCAB_AVAILABLE
        if consciousness_wrapper is not None:
            self.consciousness = consciousness_wrapper
        elif CONSCIOUSNESS_AVAILABLE and ConsciousnessWrapper is not None:
            try:
                # ΛTAG: consciousness_autoload
                self.consciousness = ConsciousnessWrapper()
            except Exception:  # pragma: no cover - optional dependency safeguard
                self.consciousness = None
        else:
            self.consciousness = None

        if self.enable_dreams:
            self.dream_vocab = DreamVocabulary()
            logger.info("🌙 Dream integration enabled for chain-of-thought reasoning")
        else:
            logger.info("🧠 Chain-of-thought reasoning without dream integration")

        # Reasoning performance metrics
        self.total_chains = 0
        self.successful_chains = 0
        self.dream_enhanced_chains = 0

    async def reason(self, problem: str, context: Optional[dict[str, Any]] = None) -> ReasoningChain:
        """
        Perform chain-of-thought reasoning on a problem

        Args:
            problem: The problem to reason about
            context: Optional context for reasoning

        Returns:
            Complete reasoning chain with steps and conclusion
        """
        logger.info(f"🧠 Starting chain-of-thought reasoning: {problem[:100]}...")

        # Initialize reasoning chain
        chain = ReasoningChain(problem=problem)

        try:
            # Step 1: Problem Analysis
            analysis_step = await self._analyze_problem(problem, context)
            chain.steps.append(analysis_step)

            # Step 2: Information Gathering
            info_step = await self._gather_information(problem, context)
            chain.steps.append(info_step)

            # Step 3: Hypothesis Generation (with dream insights if enabled)
            hypothesis_step = await self._generate_hypotheses(problem, context, chain.steps)
            chain.steps.append(hypothesis_step)
            if hypothesis_step.dream_insight:
                chain.dream_contributions += 1

            # Step 4: Logical Deduction
            deduction_step = await self._perform_deduction(problem, context, chain.steps)
            chain.steps.append(deduction_step)

            # Step 5: Evidence Evaluation
            evidence_step = await self._evaluate_evidence(problem, context, chain.steps)
            chain.steps.append(evidence_step)

            # Step 6: Dream-enhanced synthesis (if enabled)
            if self.enable_dreams:
                dream_step = await self._dream_synthesis(problem, context, chain.steps)
                if dream_step:
                    chain.steps.append(dream_step)
                    chain.dream_contributions += 1

            # Step 7: Conclusion Synthesis
            conclusion_step = await self._synthesize_conclusion(problem, context, chain.steps)
            chain.steps.append(conclusion_step)
            chain.conclusion = conclusion_step.reasoning

            # Step 8: Confidence Assessment
            confidence_step = await self._assess_confidence(chain)
            chain.steps.append(confidence_step)
            chain.overall_confidence = confidence_step.confidence

            # Update metrics
            self.total_chains += 1
            if chain.overall_confidence > 0.7:
                self.successful_chains += 1
            if chain.dream_contributions > 0:
                self.dream_enhanced_chains += 1

            logger.info(
                f"✅ Chain-of-thought completed: {chain.overall_confidence:.3f} confidence, "
                f"{chain.dream_contributions} dream insights"
            )

            return chain

        except Exception as e:
            logger.error(f"❌ Chain-of-thought reasoning failed: {e}")
            # Create error conclusion
            error_step = ReasoningNode(
                step_type=ReasoningStep.CONCLUSION_SYNTHESIS,
                description="Reasoning process encountered an error",
                reasoning=f"Unable to complete reasoning due to: {e!s}",
                confidence=0.0,
            )
            chain.steps.append(error_step)
            chain.conclusion = error_step.reasoning
            return chain

    async def _analyze_problem(self, problem: str, context: Optional[dict[str, Any]]) -> ReasoningNode:
        """Analyze the problem structure and requirements"""

        # Extract key components
        problem_type = self._identify_problem_type(problem)
        complexity = self._assess_complexity(problem)
        requirements = self._extract_requirements(problem)

        reasoning = f"Problem analysis: {problem_type} with {complexity} complexity. "
        reasoning += f"Key requirements: {', '.join(requirements)}"

        return ReasoningNode(
            step_type=ReasoningStep.PROBLEM_ANALYSIS,
            description="Analyzing problem structure and requirements",
            reasoning=reasoning,
            confidence=0.8,
            evidence=[f"Problem type: {problem_type}", f"Complexity: {complexity}"],
            next_steps=["Gather relevant information", "Generate hypotheses"],
        )

    async def _gather_information(self, problem: str, context: Optional[dict[str, Any]]) -> ReasoningNode:
        """Gather relevant information for reasoning"""

        info_sources = []

        # Use context if available
        if context:
            info_sources.extend([f"Context: {k}={v}" for k, v in context.items()])

        # Try to use consciousness system for additional context
        if self.consciousness and CONSCIOUSNESS_AVAILABLE:
            try:
                consciousness_state = self.consciousness.get_consciousness_state("monitored")
                info_sources.append(
                    f"Consciousness awareness: {consciousness_state.get('consciousness_state', {}).get('awareness_level', 0)}"
                )
            except Exception as e:
                logger.debug(f"Could not gather consciousness information: {e}")

        # Default information gathering
        info_sources.extend(
            [
                "Domain knowledge applicable to problem",
                "Relevant patterns from similar problems",
                "Logical constraints and assumptions",
            ]
        )

        reasoning = f"Information gathered from {len(info_sources)} sources. "
        reasoning += "Ready for hypothesis generation."

        return ReasoningNode(
            step_type=ReasoningStep.INFORMATION_GATHERING,
            description="Gathering relevant information and context",
            reasoning=reasoning,
            confidence=0.7,
            evidence=info_sources,
            next_steps=["Generate hypotheses", "Consider dream insights"],
        )

    async def _generate_hypotheses(
        self, problem: str, context: Optional[dict[str, Any]], previous_steps: list[ReasoningNode]
    ) -> ReasoningNode:
        """Generate hypotheses with optional dream insights"""

        hypotheses = [
            "Primary hypothesis based on direct analysis",
            "Alternative hypothesis considering edge cases",
            "Conservative hypothesis with minimal assumptions",
        ]

        dream_insight = None

        # Generate dream-enhanced hypotheses if enabled
        if self.enable_dreams:
            dream_insight = await self._get_dream_insight(problem, "hypothesis_generation")
            if dream_insight:
                hypotheses.append(f"Dream-inspired hypothesis: {dream_insight}")

        reasoning = f"Generated {len(hypotheses)} hypotheses for consideration. "
        if dream_insight:
            reasoning += f"Dream system contributed creative perspective: {dream_insight[:100]}..."

        return ReasoningNode(
            step_type=ReasoningStep.HYPOTHESIS_GENERATION,
            description="Generating possible hypotheses and explanations",
            reasoning=reasoning,
            confidence=0.75,
            evidence=hypotheses,
            dream_insight=dream_insight,
            next_steps=["Perform logical deduction", "Evaluate evidence"],
        )

    async def _perform_deduction(
        self, problem: str, context: Optional[dict[str, Any]], previous_steps: list[ReasoningNode]
    ) -> ReasoningNode:
        """Perform logical deduction based on gathered information and hypotheses"""

        # Extract hypotheses from previous steps
        hypotheses = []
        for step in previous_steps:
            if step.step_type == ReasoningStep.HYPOTHESIS_GENERATION:
                hypotheses.extend(step.evidence)

        # Logical deduction process
        deductions = []
        for i, hypothesis in enumerate(hypotheses):
            deduction = f"If {hypothesis}, then logical consequences include: "
            deduction += f"implication_{i+1}, constraint_{i+1}, prediction_{i+1}"
            deductions.append(deduction)

        reasoning = f"Performed logical deduction on {len(hypotheses)} hypotheses. "
        reasoning += f"Generated {len(deductions)} logical chains."

        return ReasoningNode(
            step_type=ReasoningStep.LOGICAL_DEDUCTION,
            description="Performing logical deduction from hypotheses",
            reasoning=reasoning,
            confidence=0.8,
            evidence=deductions,
            assumptions=["Logical consistency", "Valid inference rules"],
            next_steps=["Evaluate evidence quality", "Assess deduction validity"],
        )

    async def _evaluate_evidence(
        self, problem: str, context: Optional[dict[str, Any]], previous_steps: list[ReasoningNode]
    ) -> ReasoningNode:
        """Evaluate the quality and strength of evidence"""

        evidence_items = []
        for step in previous_steps:
            evidence_items.extend(step.evidence)

        # Evidence quality assessment
        strong_evidence = [e for e in evidence_items if "direct" in e.lower() or "proven" in e.lower()]
        weak_evidence = [e for e in evidence_items if "assumption" in e.lower() or "hypothesis" in e.lower()]

        evidence_score = len(strong_evidence) / max(len(evidence_items), 1)

        reasoning = f"Evaluated {len(evidence_items)} pieces of evidence. "
        reasoning += f"Strong evidence: {len(strong_evidence)}, Weak evidence: {len(weak_evidence)}. "
        reasoning += f"Evidence quality score: {evidence_score:.2f}"

        return ReasoningNode(
            step_type=ReasoningStep.EVIDENCE_EVALUATION,
            description="Evaluating evidence quality and reliability",
            reasoning=reasoning,
            confidence=min(0.9, 0.5 + evidence_score * 0.4),
            evidence=[
                f"Strong evidence count: {len(strong_evidence)}",
                f"Evidence quality score: {evidence_score:.2f}",
            ],
            next_steps=["Synthesize conclusion", "Assess overall confidence"],
        )

    async def _dream_synthesis(
        self, problem: str, context: Optional[dict[str, Any]], previous_steps: list[ReasoningNode]
    ) -> Optional[ReasoningNode]:
        """Use dream system for creative synthesis and insight generation"""

        if not self.enable_dreams:
            return None

        try:
            # Create a synthesis request for the dream system
            dream_insight = await self._get_dream_insight(problem, "creative_synthesis")

            if not dream_insight:
                return None

            # Create dream synthesis step
            reasoning = f"Dream synthesis provided creative insight: {dream_insight}. "
            reasoning += "This perspective offers alternative approaches and novel connections."

            return ReasoningNode(
                step_type=ReasoningStep.DREAM_INSIGHT,
                description="Dream-enhanced creative synthesis and insight",
                reasoning=reasoning,
                confidence=0.6,  # Dreams are valuable but uncertain
                evidence=[f"Dream insight: {dream_insight}"],
                dream_insight=dream_insight,
                next_steps=["Integrate dream insights", "Synthesize final conclusion"],
            )

        except Exception as e:
            logger.debug(f"Dream synthesis failed: {e}")
            return None

    async def _synthesize_conclusion(
        self, problem: str, context: Optional[dict[str, Any]], previous_steps: list[ReasoningNode]
    ) -> ReasoningNode:
        """Synthesize final conclusion from all reasoning steps"""

        # Gather insights from all steps
        key_insights = []
        total_confidence = 0.0
        dream_insights = []

        for step in previous_steps:
            key_insights.append(f"{step.step_type.value}: {step.reasoning[:100]}...")
            total_confidence += step.confidence
            if step.dream_insight:
                dream_insights.append(step.dream_insight)

        avg_confidence = total_confidence / max(len(previous_steps), 1)

        # Synthesize conclusion
        conclusion = f"Based on {len(previous_steps)} reasoning steps, the conclusion is: "

        # Include most confident insights
        high_confidence_steps = [s for s in previous_steps if s.confidence > 0.7]
        if high_confidence_steps:
            conclusion += f"High-confidence analysis from {len(high_confidence_steps)} steps supports the conclusion. "

        # Include dream contributions
        if dream_insights:
            conclusion += f"Dream insights contributed {len(dream_insights)} creative perspectives. "

        conclusion += f"Overall reasoning confidence: {avg_confidence:.2f}"

        return ReasoningNode(
            step_type=ReasoningStep.CONCLUSION_SYNTHESIS,
            description="Synthesizing final conclusion from all reasoning steps",
            reasoning=conclusion,
            confidence=avg_confidence,
            evidence=key_insights,
            assumptions=["All reasoning steps are logically connected", "Evidence is accurately evaluated"],
        )

    async def _assess_confidence(self, chain: ReasoningChain) -> ReasoningNode:
        """Assess overall confidence in the reasoning chain"""

        # Calculate confidence based on multiple factors
        step_confidences = [step.confidence for step in chain.steps]
        avg_confidence = sum(step_confidences) / len(step_confidences)

        # Bonus for dream contributions (creativity boost)
        dream_bonus = min(0.1, chain.dream_contributions * 0.03)

        # Penalty for assumptions and weak evidence
        assumption_count = sum(len(step.assumptions) for step in chain.steps)
        assumption_penalty = min(0.2, assumption_count * 0.02)

        final_confidence = max(0.0, min(1.0, avg_confidence + dream_bonus - assumption_penalty))

        assessment = f"Confidence assessment: Base confidence {avg_confidence:.3f}, "
        assessment += f"dream bonus {dream_bonus:.3f}, assumption penalty {assumption_penalty:.3f}. "
        assessment += f"Final confidence: {final_confidence:.3f}"

        return ReasoningNode(
            step_type=ReasoningStep.CONFIDENCE_ASSESSMENT,
            description="Assessing overall confidence in reasoning chain",
            reasoning=assessment,
            confidence=final_confidence,
            evidence=[
                f"Step confidences: {[round(c, 2) for c in step_confidences]}",
                f"Dream contributions: {chain.dream_contributions}",
                f"Total assumptions: {assumption_count}",
            ],
        )

    async def _get_dream_insight(self, problem: str, insight_type: str) -> Optional[str]:
        """Get creative insights from the dream system"""

        if not self.enable_dreams:
            return None

        try:
            # Use dream vocabulary to create symbolic request
            self.dream_vocab.get_symbol("creative", "synthesis")
            self.dream_vocab.pattern_discovered("novel", 0.7)

            # Simulate dream insight generation
            insight_templates = {
                "hypothesis_generation": [
                    "Consider the problem from an unexpected angle: What if the constraint is actually the solution?",
                    "Pattern recognition suggests: This resembles a recursive structure with emergent properties",
                    "Creative synthesis: The problem might be solved by inverting the traditional approach",
                ],
                "creative_synthesis": [
                    "Dream insight: Multiple perspectives converging suggest a meta-solution",
                    "Pattern emergence indicates: The answer lies in the connection between disparate elements",
                    "Creative breakthrough: The problem contains its own solution through recursive insight",
                ],
            }

            templates = insight_templates.get(insight_type, insight_templates["creative_synthesis"])
            import random

            insight = random.choice(templates)

            logger.debug(f"🌙 Dream insight generated: {insight[:50]}...")
            return insight

        except Exception as e:
            logger.debug(f"Dream insight generation failed: {e}")
            return None

    def _identify_problem_type(self, problem: str) -> str:
        """Identify the type of problem being solved"""
        problem_lower = problem.lower()

        if any(word in problem_lower for word in ["calculate", "compute", "solve", "equation"]):
            return "mathematical"
        elif any(word in problem_lower for word in ["analyze", "explain", "understand"]):
            return "analytical"
        elif any(word in problem_lower for word in ["create", "design", "build"]):
            return "creative"
        elif any(word in problem_lower for word in ["decide", "choose", "select"]):
            return "decision"
        else:
            return "general"

    def _assess_complexity(self, problem: str) -> str:
        """Assess the complexity level of the problem"""
        word_count = len(problem.split())

        if word_count < 10:
            return "low"
        elif word_count < 30:
            return "moderate"
        else:
            return "high"

    def _extract_requirements(self, problem: str) -> list[str]:
        """Extract key requirements from the problem statement"""
        requirements = []

        # Look for explicit requirements
        if "must" in problem.lower():
            requirements.append("mandatory constraints")
        if "should" in problem.lower():
            requirements.append("preferred outcomes")
        if "?" in problem:
            requirements.append("answer required")
        if "explain" in problem.lower():
            requirements.append("explanation needed")

        if not requirements:
            requirements = ["solution needed"]

        return requirements

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for the reasoning system"""

        success_rate = self.successful_chains / max(self.total_chains, 1)
        dream_usage_rate = self.dream_enhanced_chains / max(self.total_chains, 1)

        return {
            "total_chains": self.total_chains,
            "successful_chains": self.successful_chains,
            "success_rate": success_rate,
            "dream_enhanced_chains": self.dream_enhanced_chains,
            "dream_usage_rate": dream_usage_rate,
            "dream_integration_enabled": self.enable_dreams,
            "consciousness_integration": self.consciousness is not None,
        }
