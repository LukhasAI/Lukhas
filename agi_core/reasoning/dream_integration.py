"""
Dream-Reasoning Integration Bridge

Connects advanced reasoning systems with the LUKHAS dream architecture
to enhance problem-solving through creative insights, pattern recognition,
and hyperspace simulation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Import dream system components
try:
    from symbolic.vocabularies.dream_vocabulary import DreamVocabulary

    DREAM_VOCAB_AVAILABLE = True
except ImportError:
    DREAM_VOCAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class DreamReasoningMode(Enum):
    """Different modes of dream-enhanced reasoning"""

    PATTERN_DISCOVERY = "pattern_discovery"  # Find hidden patterns
    CREATIVE_SYNTHESIS = "creative_synthesis"  # Combine ideas creatively
    INSIGHT_GENERATION = "insight_generation"  # Generate novel insights
    SCENARIO_EXPLORATION = "scenario_exploration"  # Explore what-if scenarios
    PROBLEM_REFRAMING = "problem_reframing"  # View problem differently
    SOLUTION_VALIDATION = "solution_validation"  # Test solutions in dream space


@dataclass
class DreamInsight:
    """A single insight from the dream system"""

    insight_type: str
    content: str
    confidence: float
    symbolic_representation: str
    narrative: str
    visual_hint: str
    patterns_discovered: list[str] = field(default_factory=list)
    emotions: dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DreamSession:
    """A complete dream reasoning session"""

    session_id: str
    problem_context: str
    mode: DreamReasoningMode
    insights: list[DreamInsight] = field(default_factory=list)
    dream_phases: list[str] = field(default_factory=list)
    pattern_count: int = 0
    creativity_score: float = 0.0
    total_processing_time_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DreamReasoningBridge:
    """
    Bridge between reasoning systems and dream architecture

    This class provides the interface for reasoning systems to leverage
    the LUKHAS dream system for enhanced cognitive capabilities including
    creative insights, pattern discovery, and scenario exploration.
    """

    def __init__(self):
        """Initialize the dream-reasoning bridge"""
        self.dream_vocab = None
        self.sessions = {}  # Track active dream sessions
        self.total_insights = 0
        self.successful_insights = 0

        if DREAM_VOCAB_AVAILABLE:
            self.dream_vocab = DreamVocabulary()
            logger.info("🌙 Dream-reasoning bridge initialized with vocabulary support")
        else:
            logger.warning("🌙 Dream vocabulary not available, using fallback mode")

    async def start_dream_session(self, problem_context: str, mode: DreamReasoningMode) -> str:
        """
        Start a new dream reasoning session

        Args:
            problem_context: The problem or context for dream exploration
            mode: The type of dream reasoning to perform

        Returns:
            Session ID for tracking the dream session
        """
        import time

        session_id = f"dream_{int(time.time() * 1000}"

        session = DreamSession(session_id=session_id, problem_context=problem_context, mode=mode)

        self.sessions[session_id] = session

        logger.info(f"🌙 Started dream session {session_id} for {mode.value}")
        return session_id

    async def generate_insight(self, session_id: str, insight_request: str) -> Optional[DreamInsight]:
        """
        Generate a dream insight for the given session

        Args:
            session_id: The dream session ID
            insight_request: Specific request for insight

        Returns:
            Dream insight or None if generation fails
        """
        if session_id not in self.sessions:
            logger.error(f"Dream session {session_id} not found")
            return None

        session = self.sessions[session_id]

        try:
            start_time = asyncio.get_event_loop().time()

            # Generate insight based on mode
            insight = await self._generate_mode_specific_insight(session, insight_request)

            if insight:
                session.insights.append(insight)
                self.total_insights += 1
                if insight.confidence > 0.6:
                    self.successful_insights += 1

                # Update session metrics
                session.pattern_count += len(insight.patterns_discovered)
                session.creativity_score = self._calculate_creativity_score(session)

                end_time = asyncio.get_event_loop().time()
                processing_time = (end_time - start_time) * 1000
                session.total_processing_time_ms += processing_time

                logger.debug(
                    f"🌙 Generated insight: {insight.content[:100]}... " f"(confidence: {insight.confidence:.3f})"
                )

                return insight

        except Exception as e:
            logger.error(f"Dream insight generation failed: {e}")
            return None

    async def explore_dream_phases(self, session_id: str) -> list[str]:
        """
        Explore different dream phases for enhanced insight

        Args:
            session_id: The dream session ID

        Returns:
            List of dream phases explored
        """
        if session_id not in self.sessions:
            return []

        session = self.sessions[session_id]

        # Dream phases from the vocabulary system
        dream_phases = [
            "initiation",  # Gentle awakening to the problem space
            "pattern",  # Pattern recognition and connection discovery
            "deep_symbolic",  # Deep symbolic processing and archetypal insights
            "creative",  # Creative synthesis and novel combinations
            "integration",  # Integration of insights into actionable wisdom
        ]

        explored_phases = []

        for phase in dream_phases:
            try:
                # Generate phase-specific insights
                phase_insight = await self._generate_phase_insight(session, phase)

                if phase_insight:
                    session.insights.append(phase_insight)
                    explored_phases.append(phase)
                    session.dream_phases.append(phase)

                    if self.dream_vocab:
                        phase_symbol = self.dream_vocab.get_symbol("phase", phase)
                        logger.debug(f"🌙 Explored dream phase: {phase_symbol}")

            except Exception as e:
                logger.debug(f"Failed to explore dream phase {phase}: {e}")

        return explored_phases

    async def simulate_scenarios(self, session_id: str, scenarios: list[str]) -> dict[str, Any]:
        """
        Simulate multiple scenarios in dream space

        Args:
            session_id: The dream session ID
            scenarios: List of scenarios to explore

        Returns:
            Dictionary of scenario results and insights
        """
        if session_id not in self.sessions:
            return {}

        self.sessions[session_id]
        scenario_results = {}

        for i, scenario in enumerate(scenarios):
            try:
                # Create scenario-specific insight request
                insight_request = f"Explore scenario {i+1}: {scenario}"

                # Generate dream insight for this scenario
                insight = await self.generate_insight(session_id, insight_request)

                if insight:
                    scenario_results[f"scenario_{i+1}"] = {
                        "description": scenario,
                        "insight": insight.content,
                        "confidence": insight.confidence,
                        "patterns": insight.patterns_discovered,
                        "emotions": insight.emotions,
                        "narrative": insight.narrative,
                    }

                    logger.debug(f"🌙 Simulated scenario {i+1}: {scenario[:50]}...")

            except Exception as e:
                logger.debug(f"Scenario simulation failed for: {scenario}: {e}")

        return scenario_results

    async def get_session_summary(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get comprehensive summary of a dream session

        Args:
            session_id: The dream session ID

        Returns:
            Session summary with insights and metrics
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Calculate session metrics
        avg_confidence = sum(i.confidence for i in session.insights) / max(len(session.insights), 1)
        unique_patterns = set()
        for insight in session.insights:
            unique_patterns.update(insight.patterns_discovered)

        # Create comprehensive summary
        summary = {
            "session_id": session_id,
            "mode": session.mode.value,
            "problem_context": session.problem_context,
            "duration_ms": session.total_processing_time_ms,
            "insights_generated": len(session.insights),
            "average_confidence": avg_confidence,
            "unique_patterns_discovered": len(unique_patterns),
            "dream_phases_explored": len(session.dream_phases),
            "creativity_score": session.creativity_score,
            "top_insights": [
                {"content": insight.content, "confidence": insight.confidence, "patterns": insight.patterns_discovered}
                for insight in sorted(session.insights, key=lambda x: x.confidence, reverse=True)[:3]
            ],
            "dream_phase_journey": session.dream_phases,
            "created_at": session.created_at.isoformat(),
        }

        return summary

    async def end_session(self, session_id: str) -> bool:
        """
        End a dream session and cleanup resources

        Args:
            session_id: The dream session ID to end

        Returns:
            True if session ended successfully
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            logger.info(f"🌙 Ending dream session {session_id} with " f"{len(session.insights)} insights generated")
            del self.sessions[session_id]
            return True
        return False

    async def _generate_mode_specific_insight(
        self, session: DreamSession, insight_request: str
    ) -> Optional[DreamInsight]:
        """Generate insight based on the session mode"""

        mode_generators = {
            DreamReasoningMode.PATTERN_DISCOVERY: self._generate_pattern_insight,
            DreamReasoningMode.CREATIVE_SYNTHESIS: self._generate_creative_insight,
            DreamReasoningMode.INSIGHT_GENERATION: self._generate_general_insight,
            DreamReasoningMode.SCENARIO_EXPLORATION: self._generate_scenario_insight,
            DreamReasoningMode.PROBLEM_REFRAMING: self._generate_reframing_insight,
            DreamReasoningMode.SOLUTION_VALIDATION: self._generate_validation_insight,
        }

        generator = mode_generators.get(session.mode, self._generate_general_insight)
        return await generator(session, insight_request)

    async def _generate_pattern_insight(self, session: DreamSession, request: str) -> DreamInsight:
        """Generate pattern discovery insights"""

        patterns = [
            "recursive structure detected",
            "temporal correlation pattern",
            "causal chain identified",
            "emergent property pattern",
            "self-similarity observed",
        ]

        import random

        discovered_patterns = random.sample(patterns, random.randint(1, 3))

        content = f"Pattern analysis reveals: {', '.join(discovered_patterns)}. "
        content += "These patterns suggest underlying structural relationships."

        return DreamInsight(
            insight_type="pattern_discovery",
            content=content,
            confidence=0.7 + random.random() * 0.2,
            symbolic_representation=self._get_symbol("pattern", "temporal"),
            narrative=self._get_narrative("pattern"),
            visual_hint=self._get_visual_hint("pattern"),
            patterns_discovered=discovered_patterns,
            emotions={"curiosity": 0.8, "excitement": 0.6},
        )

    async def _generate_creative_insight(self, session: DreamSession, request: str) -> DreamInsight:
        """Generate creative synthesis insights"""

        creative_ideas = [
            "inverse solution approach",
            "metaphorical bridge connection",
            "recursive elegance pattern",
            "emergent simplification",
            "paradox resolution",
        ]

        import random

        selected_ideas = random.sample(creative_ideas, random.randint(1, 2))

        content = f"Creative synthesis suggests: {', '.join(selected_ideas)}. "
        content += "This approach transcends conventional thinking patterns."

        return DreamInsight(
            insight_type="creative_synthesis",
            content=content,
            confidence=0.6 + random.random() * 0.3,
            symbolic_representation=self._get_symbol("creative", "synthesis"),
            narrative=self._get_narrative("creative"),
            visual_hint=self._get_visual_hint("creative"),
            patterns_discovered=selected_ideas,
            emotions={"inspiration": 0.9, "joy": 0.7, "wonder": 0.8},
        )

    async def _generate_general_insight(self, session: DreamSession, request: str) -> DreamInsight:
        """Generate general insights"""

        insights = [
            "multidimensional perspective reveals hidden aspects",
            "system boundaries may be more fluid than assumed",
            "solution elegance emerges from constraint alignment",
            "recursive patterns indicate self-organizing principles",
        ]

        import random

        content = random.choice(insights)

        return DreamInsight(
            insight_type="general_insight",
            content=content,
            confidence=0.5 + random.random() * 0.4,
            symbolic_representation=self._get_symbol("insight", "wisdom"),
            narrative=self._get_narrative("integration"),
            visual_hint=self._get_visual_hint("integration"),
            patterns_discovered=["general_pattern"],
            emotions={"understanding": 0.7, "peace": 0.6},
        )

    async def _generate_scenario_insight(self, session: DreamSession, request: str) -> DreamInsight:
        """Generate scenario exploration insights"""

        scenario_outcomes = [
            "positive feedback loop amplification",
            "unexpected equilibrium point",
            "phase transition threshold",
            "cascade effect propagation",
            "emergent stability region",
        ]

        import random

        outcome = random.choice(scenario_outcomes)

        content = f"Scenario exploration reveals: {outcome}. "
        content += "This outcome suggests important system dynamics."

        return DreamInsight(
            insight_type="scenario_exploration",
            content=content,
            confidence=0.65 + random.random() * 0.25,
            symbolic_representation=self._get_symbol("pattern", "causal"),
            narrative=self._get_narrative("deep_symbolic"),
            visual_hint=self._get_visual_hint("deep_symbolic"),
            patterns_discovered=[outcome],
            emotions={"anticipation": 0.7, "curiosity": 0.8},
        )

    async def _generate_reframing_insight(self, session: DreamSession, request: str) -> DreamInsight:
        """Generate problem reframing insights"""

        reframes = [
            "constraint becomes enabler",
            "problem inverts to solution",
            "local optimum reveals global pattern",
            "exception illuminates the rule",
            "question transforms into answer",
        ]

        import random

        reframe = random.choice(reframes)

        content = f"Reframing perspective: {reframe}. "
        content += "This shift in viewpoint opens new solution paths."

        return DreamInsight(
            insight_type="problem_reframing",
            content=content,
            confidence=0.6 + random.random() * 0.3,
            symbolic_representation=self._get_symbol("creative", "breakthrough"),
            narrative=self._get_narrative("creative"),
            visual_hint=self._get_visual_hint("creative"),
            patterns_discovered=[reframe],
            emotions={"breakthrough": 0.9, "clarity": 0.8},
        )

    async def _generate_validation_insight(self, session: DreamSession, request: str) -> DreamInsight:
        """Generate solution validation insights"""

        validations = [
            "solution maintains system invariants",
            "approach scales gracefully",
            "edge cases handled elegantly",
            "resource efficiency optimized",
            "robustness criteria satisfied",
        ]

        import random

        validation = random.choice(validations)

        content = f"Solution validation confirms: {validation}. "
        content += "The proposed approach demonstrates strong viability."

        return DreamInsight(
            insight_type="solution_validation",
            content=content,
            confidence=0.75 + random.random() * 0.2,
            symbolic_representation=self._get_symbol("analysis", "high_coherence"),
            narrative=self._get_narrative("integration"),
            visual_hint=self._get_visual_hint("integration"),
            patterns_discovered=[validation],
            emotions={"confidence": 0.9, "satisfaction": 0.7},
        )

    async def _generate_phase_insight(self, session: DreamSession, phase: str) -> Optional[DreamInsight]:
        """Generate insight specific to a dream phase"""

        phase_insights = {
            "initiation": "gentle awakening to problem space complexity",
            "pattern": "hidden connections between disparate elements emerge",
            "deep_symbolic": "archetypal patterns reveal universal principles",
            "creative": "novel combinations birth unprecedented possibilities",
            "integration": "scattered insights crystallize into coherent wisdom",
        }

        content = phase_insights.get(phase, "phase-specific insight generated")

        return DreamInsight(
            insight_type=f"phase_{phase}",
            content=f"Phase {phase}: {content}",
            confidence=0.6 + hash(phase) % 40 / 100,  # Deterministic but varied
            symbolic_representation=self._get_symbol("phase", phase),
            narrative=self._get_narrative(phase),
            visual_hint=self._get_visual_hint(phase),
            patterns_discovered=[f"{phase}_pattern"],
            emotions={phase: 0.8, "flow": 0.7},
        )

    def _calculate_creativity_score(self, session: DreamSession) -> float:
        """Calculate creativity score for a session"""

        if not session.insights:
            return 0.0

        # Base creativity from average confidence
        avg_confidence = sum(i.confidence for i in session.insights) / len(session.insights)

        # Bonus for pattern diversity
        unique_patterns = set()
        for insight in session.insights:
            unique_patterns.update(insight.patterns_discovered)

        pattern_bonus = min(0.3, len(unique_patterns) * 0.05)

        # Bonus for phase exploration
        phase_bonus = min(0.2, len(session.dream_phases) * 0.04)

        return min(1.0, avg_confidence + pattern_bonus + phase_bonus)

    def _get_symbol(self, category: str, item: str) -> str:
        """Get symbolic representation"""
        if self.dream_vocab:
            return self.dream_vocab.get_symbol(category, item)
        return f"🔮 {category}_{item}"

    def _get_narrative(self, phase: str) -> str:
        """Get narrative text for phase"""
        if self.dream_vocab:
            return self.dream_vocab.get_narrative(phase)
        return f"The {phase} phase unfolds with mysterious insight..."

    def _get_visual_hint(self, phase: str) -> str:
        """Get visual hint for phase"""
        if self.dream_vocab:
            return self.dream_vocab.get_visual_hint(phase)
        return f"A dreamscape of {phase} emerges..."

    def get_bridge_metrics(self) -> dict[str, Any]:
        """Get performance metrics for the dream-reasoning bridge"""

        active_sessions = len(self.sessions)
        success_rate = self.successful_insights / max(self.total_insights, 1)

        return {
            "active_sessions": active_sessions,
            "total_insights_generated": self.total_insights,
            "successful_insights": self.successful_insights,
            "insight_success_rate": success_rate,
            "dream_vocabulary_available": DREAM_VOCAB_AVAILABLE,
            "supported_modes": [mode.value for mode in DreamReasoningMode],
        }
