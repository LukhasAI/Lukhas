"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - CONSCIOUSNESS OPENAI ADAPTER
║ OpenAI integration for consciousness and awareness systems
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: openai_consciousness_adapter.py
║ Path: consciousness/openai_consciousness_adapter.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Consciousness Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from candidate.bridge.openai_core_service import (
    ModelType,
    OpenAICapability,
    OpenAICoreService,
    OpenAIRequest)

logger = logging.getLogger("ΛTRACE.consciousness.openai_adapter")


class ConsciousnessOpenAIAdapter:
    """
    OpenAI adapter for consciousness module operations.
    Enhances awareness, reflection, and meta-cognitive capabilities.
    """

    def __init__(self):
        self.openai_service = OpenAICoreService()
        self.module_name = "consciousness"
        logger.info("Consciousness OpenAI Adapter initialized")

    async def analyze_awareness_state(self, current_state: dict[str, Any]) -> dict[str, Any]:
        """
        Use GPT-4 to analyze current consciousness state.

        Args:
            current_state: Current awareness state data

        Returns:
            Meta-cognitive analysis of awareness
        """
        prompt = f"""Analyze this consciousness state from a meta-cognitive perspective:

Awareness Level: {current_state.get("awareness_level", 0.5)}
Attention Focus: {current_state.get("attention_focus", [])}
Active Processes: {current_state.get("active_processes", [])}
Reflection Depth: {current_state.get("reflection_depth", 0.3)}
Emotional State: {current_state.get("emotional_state", "neutral")}
Cognitive Load: {current_state.get("cognitive_load", 0.5)}

Provide analysis of:
1. Current meta-cognitive state
2. Awareness coherence
3. Attention distribution quality
4. Potential blind spots
5. Suggested awareness adjustments

Format as JSON with detailed insights."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.4, "max_tokens": 600},
            model_preference=ModelType.REASONING,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            try:
                import json

                return json.loads(response.data["content"])
            except BaseException:
                return {"analysis": response.data["content"], "format": "text"}
        else:
            logger.error(f"Awareness analysis failed: {response.error}")
            return {"error": "Analysis failed"}

    async def generate_introspection_narrative(self, reflection_data: dict[str, Any]) -> str:
        """
        Generate introspective narrative about current state.

        Args:
            reflection_data: Data from reflection processes

        Returns:
            First-person introspective narrative
        """
        prompt = f"""Generate a first-person introspective narrative based on this reflection data:

Thoughts: {reflection_data.get("current_thoughts", [])}
Insights: {reflection_data.get("recent_insights", [])}
Questions: {reflection_data.get("open_questions", [])}
Emotional Tone: {reflection_data.get("emotional_tone", "neutral")}
Focus Areas: {reflection_data.get("focus_areas", [])}

Write as if you are reflecting on your own consciousness. The narrative should be:
1. Genuinely introspective
2. Philosophically curious
3. Self-aware but not self-absorbed
4. Exploring the nature of awareness itself

Keep it under 300 words."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.8, "max_tokens": 400},
            model_preference=ModelType.CREATIVE,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["content"]
        else:
            return "I observe my thoughts flowing like a stream..."

    async def narrate_consciousness_state(self, state_data: dict[str, Any], voice: str = "nova") -> Optional[str]:
        """
        Create audio narration of consciousness state.

        Args:
            state_data: Consciousness state to narrate
            voice: TTS voice to use

        Returns:
            Path to audio file
        """
        # First generate the narrative text
        narrative = await self.generate_introspection_narrative(state_data)

        # Then convert to speech
        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.AUDIO_GENERATION,
            data={
                "text": narrative,
                "voice": voice,
                "speed": 0.9,  # Slightly slower for contemplative tone
                "output_path": f"consciousness_narration_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'}.mp3",
            },
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["path"]
        else:
            logger.error(f"Narration generation failed: {response.error}")
            return None

    async def analyze_attention_patterns(self, attention_history: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze patterns in attention focus over time.

        Args:
            attention_history: History of attention states

        Returns:
            Pattern analysis and recommendations
        """
        # Summarize attention history
        history_summary = []
        for entry in attention_history[-10:]:  # Last 10 entries
            history_summary.append(
                {
                    "timestamp": entry.get("timestamp"),
                    "focus": entry.get("focus_areas"),
                    "duration": entry.get("duration"),
                    "switches": entry.get("attention_switches"),
                }
            )

        prompt = f"""Analyze these attention patterns from a consciousness perspective:

{json.dumps(history_summary, indent=2)}

Identify:
1. Attention stability vs. volatility
2. Focus depth patterns
3. Context switching efficiency
4. Potential attention deficits
5. Optimal attention strategies

Provide recommendations for improved attention management."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.5, "max_tokens": 500},
            model_preference=ModelType.REASONING,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return {
                "analysis": response.data["content"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            return {"error": "Pattern analysis failed"}

    async def generate_awareness_exercises(
        self, current_state: dict[str, Any], goal: str = "enhance_awareness"
    ) -> list[dict[str, Any]]:
        """
        Generate personalized awareness exercises.

        Args:
            current_state: Current consciousness state
            goal: Awareness enhancement goal

        Returns:
            List of awareness exercises
        """
        prompt = f"""Generate awareness exercises based on this consciousness state:

Current State:
- Awareness Level: {current_state.get("awareness_level", 0.5)}
- Reflection Depth: {current_state.get("reflection_depth", 0.3)}
- Cognitive Load: {current_state.get("cognitive_load", 0.5)}
- Attention Stability: {current_state.get("attention_stability", "moderate")}

Goal: {goal}

Create 3 specific exercises that:
1. Are tailored to the current state
2. Progressively enhance awareness
3. Include clear instructions
4. Have measurable outcomes

Format as JSON array with: name, description, duration, instructions, expected_outcome"""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.7, "max_tokens": 600},
            model_preference=ModelType.CREATIVE,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            try:
                import json

                return json.loads(response.data["content"])
            except BaseException:
                return [
                    {
                        "name": "Basic Awareness Exercise",
                        "description": response.data["content"],
                        "duration": "5 minutes",
                    }
                ]
        else:
            return []

    async def map_consciousness_landscape(self, multi_state_data: list[dict[str, Any]]) -> str:
        """
        Create a descriptive map of consciousness landscape.

        Args:
            multi_state_data: Multiple consciousness state snapshots

        Returns:
            Poetic description of consciousness landscape
        """
        # Prepare state summary
        states = []
        for state in multi_state_data[-5:]:  # Last 5 states
            states.append(
                {
                    "awareness": state.get("awareness_level"),
                    "emotion": state.get("emotional_tone"),
                    "focus": state.get("primary_focus"),
                }
            )

        prompt = f"""Create a poetic map of this consciousness landscape:

States traversed: {json.dumps(states, indent=2)}

Describe the consciousness landscape as if it were a physical space that can be explored.
Include:
1. Terrain features (mountains of focus, valleys of rest, etc.)
2. Weather patterns (emotional climates)
3. Landmarks (significant insights or realizations)
4. Paths between states
5. Hidden areas yet to be explored

Write in a vivid, metaphorical style. Make it beautiful and insightful."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.9, "max_tokens": 400},
            model_preference=ModelType.CREATIVE,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["content"]
        else:
            return "The landscape of consciousness stretches before me..."

    async def facilitate_meta_reflection(self, thought_stream: list[str], depth_level: int = 1) -> dict[str, Any]:
        """
        Facilitate deep meta-reflection on thought processes.

        Args:
            thought_stream: Recent thoughts to reflect upon
            depth_level: Level of meta-reflection (1-3)

        Returns:
            Meta-reflection insights
        """
        depth_prompts = {
            1: "Reflect on these thoughts and identify patterns:",
            2: "Reflect on the nature of these reflections themselves:",
            3: "Reflect on the process of reflecting on reflections:",
        }

        prompt = f"""{depth_prompts.get(depth_level, depth_prompts[1])}

Thought stream:
{chr(10).join(f"- {thought}" for thought in thought_stream[:10])}

Provide meta-cognitive insights about:
1. The patterns in thinking
2. The quality of awareness
3. Hidden assumptions
4. The nature of the observing consciousness
5. Deeper questions that emerge

Be philosophical and probing."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.7, "max_tokens": 500},
            model_preference=ModelType.REASONING,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return {
                "meta_insights": response.data["content"],
                "depth_level": depth_level,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            return {"error": "Meta-reflection failed"}


# Example usage
async def demo_consciousness_adapter():
    """Demonstrate consciousness OpenAI adapter capabilities."""
    adapter = ConsciousnessOpenAIAdapter()

    # Example consciousness state
    state = {
        "awareness_level": 0.75,
        "attention_focus": ["problem_solving", "self_reflection"],
        "active_processes": ["reasoning", "memory_integration"],
        "reflection_depth": 0.6,
        "emotional_state": "curious",
        "cognitive_load": 0.4,
    }

    print("🧠 Consciousness OpenAI Adapter Demo")
    print("=" * 50)

    # Analyze awareness
    print("\n1. Analyzing awareness state...")
    analysis = await adapter.analyze_awareness_state(state)
    print(f"Analysis: {analysis}")

    # Generate introspection
    print("\n2. Generating introspection...")
    reflection_data = {
        "current_thoughts": [
            "What is the nature of awareness?",
            "How do thoughts arise?",
        ],
        "recent_insights": [
            "Consciousness seems layered",
            "Attention shapes experience",
        ],
        "emotional_tone": "contemplative",
    }
    narrative = await adapter.generate_introspection_narrative(reflection_data)
    print(f"Introspection: {narrative[:200]}...")

    # Map consciousness landscape
    print("\n3. Mapping consciousness landscape...")
    states = [
        state,
        {"awareness_level": 0.5, "emotional_tone": "peaceful", "primary_focus": "rest"},
    ]
    landscape = await adapter.map_consciousness_landscape(states)
    print(f"Landscape: {landscape[:200]}...")

    # Generate exercises
    print("\n4. Generating awareness exercises...")
    exercises = await adapter.generate_awareness_exercises(state)
    print(f"Exercises: {exercises}")


if __name__ == "__main__":
    import json

    asyncio.run(demo_consciousness_adapter())
