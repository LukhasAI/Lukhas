"""
🧠 Auto Consciousness - Unified Consciousness Interface
=====================================================

Provides automatic consciousness assessment and decision-making capabilities
for the LUKHAS AI system. This module combines awareness assessment,
decision-making, and consciousness state management.

Author: LUKHAS AI System
Version: 1.0.0
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

# Import LUKHAS components
try:
    from ...awareness.awareness_engine import AwarenessEngine
except ImportError:
    AwarenessEngine = None

try:
    from ...reasoning.reasoning_engine import ReasoningEngine
except ImportError:
    ReasoningEngine = None

try:
    from ...states.shared_state import SharedState
except ImportError:
    SharedState = None


logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessState:
    """Represents the current consciousness state"""

    awareness_level: float
    attention_focus: list[str]
    decision_confidence: float
    reasoning_depth: int
    timestamp: datetime
    active_contexts: dict[str, Any]


class AutoConsciousness:
    """
    🧠 Auto Consciousness - Unified consciousness processing system

    Provides automatic consciousness assessment, decision-making, and state management
    with integration across awareness, reasoning, and memory systems.
    """

    def __init__(self, enable_awareness=True, enable_reasoning=True):
        """Initialize Auto Consciousness system"""
        self.consciousness_id = f"auto_consciousness_{datetime.now(timezone.utc).timestamp()}"
        self.active = True
        self.state_history: list[ConsciousnessState] = []

        # Initialize components
        self.components = {}

        if enable_awareness and AwarenessEngine:
            try:
                self.components["awareness"] = AwarenessEngine()
            except Exception as e:
                logger.warning(f"Could not initialize AwarenessEngine: {e}")

        if enable_reasoning and ReasoningEngine:
            try:
                self.components["reasoning"] = ReasoningEngine()
            except Exception as e:
                logger.warning(f"Could not initialize ReasoningEngine: {e}")

        # Initialize shared state
        if SharedState:
            try:
                self.components["shared_state"] = SharedState()
            except Exception as e:
                logger.warning(f"Could not initialize SharedState: {e}")

        # Initialize consciousness state
        self.current_state = ConsciousnessState(
            awareness_level=0.5,
            attention_focus=["initialization"],
            decision_confidence=0.7,
            reasoning_depth=1,
            timestamp=datetime.now(timezone.utc),
            active_contexts={},
        )

        logger.info(f"Auto Consciousness initialized: {self.consciousness_id}")

    async def assess_awareness(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Assess awareness level based on input stimuli

        Args:
            input_data: Dictionary containing stimulus, context, and metadata

        Returns:
            Dictionary with awareness assessment results
        """
        try:
            stimulus = input_data.get("stimulus", "unknown")
            context = input_data.get("context", {})
            metadata = input_data.get("metadata", {})

            # Calculate awareness level based on stimulus importance and context
            importance = context.get("importance", 0.5)
            source_reliability = 0.8 if metadata.get("source") == "test" else 0.6

            # Awareness calculation
            base_awareness = min(importance * source_reliability, 1.0)

            # Adjust for attention focus
            attention_boost = 0.1 if stimulus in self.current_state.attention_focus else 0.0
            awareness_level = min(base_awareness + attention_boost, 1.0)

            # Update consciousness state
            self.current_state = ConsciousnessState(
                awareness_level=awareness_level,
                attention_focus=[stimulus, *self.current_state.attention_focus[:4]],  # Keep last 5
                decision_confidence=self.current_state.decision_confidence,
                reasoning_depth=self.current_state.reasoning_depth,
                timestamp=datetime.now(timezone.utc),
                active_contexts={**self.current_state.active_contexts, **context},
            )

            # Add to state history
            self.state_history.append(self.current_state)

            # Keep only last 100 states
            if len(self.state_history) > 100:
                self.state_history = self.state_history[-100:]

            return {
                "awareness_level": awareness_level,
                "attention_focus": self.current_state.attention_focus,
                "processing_depth": self.current_state.reasoning_depth,
                "confidence": base_awareness,
                "stimulus_recognized": True,
                "response_generated": True,
                "timestamp": self.current_state.timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Awareness assessment failed: {e}")
            return {
                "awareness_level": 0.1,
                "attention_focus": ["error"],
                "processing_depth": 0,
                "confidence": 0.0,
                "stimulus_recognized": False,
                "response_generated": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def make_decision(self, decision_input: dict[str, Any]) -> dict[str, Any]:
        """
        Make a decision based on input scenario and options

        Args:
            decision_input: Dictionary with scenario, options, and context

        Returns:
            Dictionary with decision results
        """
        try:
            scenario = decision_input.get("scenario", "unknown")
            options = decision_input.get("options", ["unknown"])
            context = decision_input.get("context", {})

            # Simple decision logic based on context
            urgency = context.get("urgency", "low")
            risk = context.get("risk", "low")

            # Decision scoring
            scores = {}
            for option in options:
                base_score = 0.5

                # Adjust based on option type
                if option == "proceed":
                    base_score += 0.3 if urgency == "high" else 0.1
                    base_score -= 0.2 if risk == "high" else 0.0
                elif option == "pause":
                    base_score += 0.2 if risk == "high" else -0.1
                    base_score += 0.1 if urgency == "medium" else 0.0
                elif option == "abort":
                    base_score += 0.4 if risk == "critical" else -0.3
                    base_score -= 0.3 if urgency == "high" else 0.0

                scores[option] = max(0.0, min(1.0, base_score))

            # Select best option
            best_option = max(scores.keys(), key=lambda k: scores[k])
            confidence = scores[best_option]

            # Generate reasoning
            reasoning = [
                f"Analyzed scenario: {scenario}",
                f"Considered context: urgency={urgency}, risk={risk}",
                f"Evaluated {len(options)} options",
                f"Selected {best_option} with score {confidence:.2f}",
            ]

            # Alternative options (excluding the chosen one)
            alternatives = [opt for opt in options if opt != best_option]

            # Update consciousness state
            self.current_state.decision_confidence = confidence
            self.current_state.reasoning_depth = len(reasoning)

            return {
                "decision": best_option,
                "confidence": confidence,
                "reasoning": reasoning,
                "alternatives": alternatives,
                "scenario": scenario,
                "scores": scores,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            return {
                "decision": "abort",
                "confidence": 0.1,
                "reasoning": [f"Decision failed: {e!s}"],
                "alternatives": [],
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def get_consciousness_state(self) -> dict[str, Any]:
        """Get current consciousness state"""
        return {
            "consciousness_id": self.consciousness_id,
            "active": self.active,
            "current_state": {
                "awareness_level": self.current_state.awareness_level,
                "attention_focus": self.current_state.attention_focus,
                "decision_confidence": self.current_state.decision_confidence,
                "reasoning_depth": self.current_state.reasoning_depth,
                "timestamp": self.current_state.timestamp.isoformat(),
                "active_contexts": self.current_state.active_contexts,
            },
            "components_available": list(self.components.keys()),
            "state_history_length": len(self.state_history),
        }

    async def process_stimulus(self, stimulus: Any) -> dict[str, Any]:
        """Process a stimulus through the consciousness system"""
        # Convert stimulus to standard format
        if isinstance(stimulus, str):
            input_data = {
                "stimulus": stimulus,
                "context": {"importance": 0.5},
                "metadata": {"source": "direct"},
            }
        elif isinstance(stimulus, dict):
            input_data = stimulus
        else:
            input_data = {
                "stimulus": str(stimulus),
                "context": {"importance": 0.3},
                "metadata": {"source": "converted"},
            }

        # Assess awareness
        awareness_result = await self.assess_awareness(input_data)

        # If awareness is high enough, make a decision if options are available
        if awareness_result["awareness_level"] > 0.6:
            decision_input = {
                "scenario": input_data["stimulus"],
                "options": ["process", "defer", "ignore"],
                "context": input_data.get("context", {}),
            }
            decision_result = await self.make_decision(decision_input)
        else:
            decision_result = {
                "decision": "defer",
                "confidence": awareness_result["awareness_level"],
                "reasoning": ["Low awareness level, deferring processing"],
                "alternatives": ["ignore"],
            }

        return {
            "stimulus": input_data["stimulus"],
            "awareness": awareness_result,
            "decision": decision_result,
            "consciousness_state": await self.get_consciousness_state(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def is_available(self) -> bool:
        """Check if consciousness system is available and functional"""
        return self.active

    async def shutdown(self) -> None:
        """Gracefully shutdown the consciousness system"""
        logger.info(f"Auto Consciousness shutting down: {self.consciousness_id}")
        self.active = False


# Export main class
__all__ = ["AutoConsciousness"]


# Alias for expected name
AutoConsciousnessEngine = AutoConsciousness
