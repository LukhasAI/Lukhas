#!/usr/bin/env python3
"""
NIAS-Dream Bridge
Connects NIAS symbolic message processing with Dream quantum states.
Enables consent-aware dream injection and quantum consciousness integration.
"""
from consciousness.qi import qi
import streamlit as st
from datetime import timezone

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class DreamInjectionMode(Enum):
    """Modes for injecting messages into dream states"""

    GENTLE = "gentle"  # Low-intensity, background processing
    SYMBOLIC = "symbolic"  # Rich symbolic interpretation
    NARRATIVE = "narrative"  # Story-based integration
    QUANTUM = "quantum"  # Quantum superposition processing


@dataclass
class DreamMessage:
    """Message prepared for dream injection"""

    message_id: str
    original_message: dict[str, Any]
    symbolic_interpretation: str
    emotional_context: dict[str, float]
    injection_mode: DreamInjectionMode
    priority: float = 0.5
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class NIASDreamBridge:
    """
    Bridge between NIAS symbolic messages and Dream processing.

    This bridge handles:
    - Translation of NIAS messages to dream-compatible formats
    - Consent-aware dream injection
    - Quantum state preparation for dream processing
    - OpenAI-enhanced symbolic interpretation
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        # Component connections
        self.nias_core = None
        self.dream_adapter = None
        self.qi_hub = None

        # Dream queue
        self.dream_queue: list[DreamMessage] = []
        self.processing_task = None
        self.is_processing = False

        logger.info("NIAS-Dream Bridge initialized")

    def inject_components(
        self,
        nias_core: Any = None,
        dream_adapter: Any = None,
        qi_hub: Any = None,
    ) -> None:
        """Inject component dependencies"""
        self.nias_core = nias_core
        self.dream_adapter = dream_adapter
        self.qi_hub = qi_hub

        # Start dream processing loop
        if not self.processing_task:
            self.processing_task = asyncio.create_task(self._dream_processing_loop())

        logger.info("Components injected into NIAS-Dream Bridge")

    async def bridge_to_dream(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        reason: str = "emotional_safety",
    ) -> dict[str, Any]:
        """
        Bridge a NIAS message to dream processing.

        This is called when a message cannot be delivered directly due to
        emotional safety, user preference, or other constraints.
        """
        try:
            # Analyze message for dream suitability
            dream_analysis = await self._analyze_for_dream(message, user_context, reason)

            # Create dream message
            dream_msg = DreamMessage(
                message_id=f"nias_dream_{datetime.now(timezone.utc).timestamp(}",
                original_message=message,
                symbolic_interpretation=dream_analysis["interpretation"],
                emotional_context=dream_analysis["emotional_context"],
                injection_mode=DreamInjectionMode(dream_analysis["mode"]),
                priority=dream_analysis["priority"],
            )

            # Add to dream queue
            self.dream_queue.append(dream_msg)

            # Sort by priority
            self.dream_queue.sort(key=lambda x: x.priority, reverse=True)

            return {
                "success": True,
                "dream_id": dream_msg.message_id,
                "mode": dream_msg.injection_mode.value,
                "message": self._get_poetic_response(reason),
            }

        except Exception as e:
            logger.error(f"Failed to bridge to dream: {e}")
            return {"success": False, "error": str(e)}

    async def _analyze_for_dream(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        reason: str,
    ) -> dict[str, Any]:
        """Analyze message for dream processing using AI"""
        if self.openai:
            try:
                analysis = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are the NIAS-Dream bridge analyzer.
                        Analyze how to best integrate this message into dream processing.
                        Consider: emotional safety, symbolic meaning, narrative potential,
                        and quantum consciousness states.""",
                        },
                        {
                            "role": "user",
                            "content": f"""Message: {json.dumps(message)}
                        User Context: {json.dumps(user_context)}
                        Deferral Reason: {reason}""",
                        },
                    ],
                    functions=[
                        {
                            "name": "analyze_dream_integration",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "interpretation": {"type": "string"},
                                    "mode": {
                                        "type": "string",
                                        "enum": [
                                            "gentle",
                                            "symbolic",
                                            "narrative",
                                            "quantum",
                                        ],
                                    },
                                    "priority": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                    "emotional_context": {
                                        "type": "object",
                                        "properties": {
                                            "safety": {"type": "number"},
                                            "receptivity": {"type": "number"},
                                            "symbolic_density": {"type": "number"},
                                        },
                                    },
                                    "dream_seeds": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": [
                                    "interpretation",
                                    "mode",
                                    "priority",
                                    "emotional_context",
                                ],
                            },
                        }
                    ],
                    function_call={"name": "analyze_dream_integration"},
                )

                func_result = json.loads(analysis.choices[0].message.function_call.arguments)
                return func_result

            except Exception as e:
                logger.error(f"OpenAI dream analysis failed: {e}")

        # Fallback analysis
        return {
            "interpretation": "Message saved for gentle dream processing",
            "mode": "gentle",
            "priority": 0.5,
            "emotional_context": {
                "safety": 0.8,
                "receptivity": 0.6,
                "symbolic_density": 0.5,
            },
        }

    def _get_poetic_response(self, reason: str) -> str:
        """Get poetic response based on deferral reason"""
        responses = {
            "emotional_safety": "This moment wasn't meant for this 🕊️",
            "stress_threshold": "Rest now, we'll meet in dreams 🌙",
            "cognitive_overload": "Your mind seeks quieter shores 🌊",
            "user_preference": "Saved for when stars align ✨",
            "dream_preference": "Into the dream realm it flows 💫",
            "default": "Held gently for another time 🫧",
        }
        return responses.get(reason, responses["default"])

    async def _dream_processing_loop(self):
        """Background loop for processing dream queue"""
        self.is_processing = True

        while self.is_processing:
            try:
                if self.dream_queue and self.dream_adapter:
                    # Process oldest high-priority message
                    dream_msg = self.dream_queue.pop(0)

                    # Check if user is in dream-receptive state
                    if await self._is_dream_ready(dream_msg):
                        await self._inject_into_dream(dream_msg)
                    else:
                        # Re-queue for later
                        self.dream_queue.append(dream_msg)

                # Sleep before next check
                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Dream processing loop error: {e}")
                await asyncio.sleep(30)  # Longer sleep on error

    async def _is_dream_ready(self, dream_msg: DreamMessage) -> bool:
        """Check if conditions are right for dream injection"""
        # TODO: Check actual dream state from dream adapter
        # For now, simple time-based check
        age = (datetime.now(timezone.utc) - dream_msg.created_at).total_seconds()

        # High priority messages can be injected sooner
        min_age = 60 * (1 - dream_msg.priority)  # 0-60 seconds based on priority

        return age >= min_age

    async def _inject_into_dream(self, dream_msg: DreamMessage) -> None:
        """Inject message into dream processing"""
        try:
            if dream_msg.injection_mode == DreamInjectionMode.QUANTUM:
                # Prepare for quantum processing
                await self._prepare_quantum_dream(dream_msg)

            # Create dream payload
            dream_payload = {
                "message_id": dream_msg.message_id,
                "content": dream_msg.original_message,
                "interpretation": dream_msg.symbolic_interpretation,
                "mode": dream_msg.injection_mode.value,
                "emotional_context": dream_msg.emotional_context,
            }

            # Inject into dream system
            if self.dream_adapter:
                result = await self.dream_adapter.inject_dream_content(dream_payload)
                logger.info(f"Dream injection result: {result}")

            # Update quantum consciousness if available
            if self.qi_hub:
                await self.qi_hub.process_consciousness_event(
                    agent_id=dream_msg.original_message.get("user_id", "unknown"),
                    event_type="dream_injection",
                    event_data={"dream_content": dream_payload},
                )

        except Exception as e:
            logger.error(f"Failed to inject into dream: {e}")

    async def _prepare_quantum_dream(self, dream_msg: DreamMessage) -> None:
        """Prepare quantum states for dream processing"""
        if self.qi_hub and self.openai:
            try:
                # Generate quantum interpretation
                qi_prep = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Prepare quantum superposition states for dream processing.
                        Create parallel interpretations that can exist simultaneously.""",
                        },
                        {
                            "role": "user",
                            "content": f"Dream Message: {dream_msg.symbolic_interpretation}",
                        },
                    ],
                    n=3,  # Generate 3 quantum states
                    temperature=0.9,
                )

                # Create superposition in quantum hub
                states = [choice.message.content for choice in qi_prep.choices]
                await self.qi_hub.create_superposition_state(
                    agent_id=dream_msg.original_message.get("user_id", "unknown"),
                    states=states,
                )

            except Exception as e:
                logger.error(f"Quantum dream preparation failed: {e}")

    async def extract_dream_insights(self, user_id: str, time_window: int = 3600) -> dict[str, Any]:
        """Extract insights from recent dream processing"""
        recent_dreams = [
            msg for msg in self.dream_queue if (datetime.now(timezone.utc) - msg.created_at).total_seconds() < time_window
        ]

        insights = {
            "user_id": user_id,
            "dream_count": len(recent_dreams),
            "common_themes": [],
            "emotional_trajectory": {},
            "symbolic_patterns": [],
        }

        if self.openai and recent_dreams:
            try:
                # Analyze dream patterns with AI
                dream_data = [
                    {
                        "interpretation": msg.symbolic_interpretation,
                        "emotional_context": msg.emotional_context,
                        "mode": msg.injection_mode.value,
                    }
                    for msg in recent_dreams
                ]

                analysis = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Analyze dream patterns for insights.
                        Identify themes, emotional trajectories, and symbolic patterns.""",
                        },
                        {"role": "user", "content": json.dumps(dream_data)},
                    ],
                )

                insights["ai_analysis"] = analysis.choices[0].message.content

            except Exception as e:
                logger.error(f"Dream insight extraction failed: {e}")

        return insights

    async def create_dream_narrative(self, dream_messages: list[DreamMessage]) -> str:
        """Create unified narrative from multiple dream messages"""
        if not dream_messages:
            return "No dreams to weave together."

        if self.openai:
            try:
                # Extract interpretations
                interpretations = [msg.symbolic_interpretation for msg in dream_messages]

                narrative = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Create a cohesive, poetic dream narrative.
                        Weave together symbolic elements into a meaningful story.""",
                        },
                        {
                            "role": "user",
                            "content": f"Dream elements: {json.dumps(interpretations}",
                        },
                    ],
                    temperature=0.8,
                )

                return narrative.choices[0].message.content

            except Exception as e:
                logger.error(f"Dream narrative creation failed: {e}")

        # Fallback narrative
        return "Dreams flow like rivers, carrying messages of light and shadow..."

    async def visualize_dream(self, dream_narrative: str) -> Optional[str]:
        """Generate visual representation of dream using DALL-E"""
        if self.openai:
            try:
                # Create dream prompt
                prompt = f"Ethereal, symbolic dream visualization: {dream_narrative[:200]}. Soft, flowing, abstract art style with gentle colors."

                response = await self.openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    style="vivid",
                )

                return response.data[0].url

            except Exception as e:
                logger.error(f"Dream visualization failed: {e}")

        return None

    def get_dream_statistics(self) -> dict[str, Any]:
        """Get statistics about dream processing"""
        total_dreams = len(self.dream_queue)

        mode_counts = {}
        for mode in DreamInjectionMode:
            mode_counts[mode.value] = sum(1 for msg in self.dream_queue if msg.injection_mode == mode)

        avg_priority = sum(msg.priority for msg in self.dream_queue) / total_dreams if total_dreams > 0 else 0

        return {
            "total_pending": total_dreams,
            "mode_distribution": mode_counts,
            "average_priority": avg_priority,
            "oldest_dream_age": (
                (datetime.now(timezone.utc) - min(msg.created_at for msg in self.dream_queue)).total_seconds()
                if self.dream_queue
                else 0
            ),
        }

    async def shutdown(self):
        """Gracefully shutdown the bridge"""
        self.is_processing = False
        if self.processing_task:
            await self.processing_task
        logger.info("NIAS-Dream Bridge shutdown complete")


# Singleton instance
_bridge_instance = None


def get_nias_dream_bridge(
    openai_api_key: Optional[str] = None,
) -> NIASDreamBridge:
    """Get or create the singleton NIAS-Dream Bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = NIASDreamBridge(openai_api_key)
    return _bridge_instance
