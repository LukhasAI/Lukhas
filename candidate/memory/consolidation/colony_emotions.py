from datetime import datetime
from typing import Any

import numpy as np

from candidate.core.colonies.base_colony import BaseColony
from lukhas.emotion.models import EmotionalState, EmotionVector

# TAG:memory
# TAG:consolidation
# TAG:neuroplastic
# TAG:colony


class EmotionalColony(BaseColony):
    """Colony for distributed emotional processing."""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["emotion_processing"])
        self.collective_emotion = EmotionalState()
        self.emotion_history: list[dict[str, Any]] = []

    async def process_stimulus(self, stimulus: dict[str, Any]) -> dict[str, Any]:
        agent_emotions = []
        for agent_id, agent in self.agents.items():
            if hasattr(agent, "evaluate_emotion"):
                emotion_vector = await agent.evaluate_emotion(stimulus)
            else:
                emotion_vector = EmotionVector()
            agent_emotions.append(
                {
                    "agent_id": agent_id,
                    "emotion": emotion_vector,
                    "confidence": getattr(agent, "emotional_confidence", 1.0),
                }
            )

        collective = self._merge_emotions(agent_emotions)
        self.collective_emotion = collective["emotion_state"]
        self.emotion_history.append(
            {
                "timestamp": datetime.now(),
                "stimulus": stimulus.get("type"),
                "collective_emotion": collective,
                "agent_count": len(agent_emotions),
            }
        )

        if collective["intensity"] > 0.8:
            await self._emotional_contagion(collective)

        return {
            "collective_emotion": collective,
            "individual_responses": agent_emotions,
            "contagion_triggered": collective["intensity"] > 0.8,
        }

    async def _emotional_contagion(self, collective: dict[str, Any]) -> None:
        # placeholder for contagion logic
        return None

    def _merge_emotions(self, agent_emotions: list[dict]) -> dict[str, Any]:
        if not agent_emotions:
            return {"emotion_state": self.collective_emotion, "intensity": 0.0}

        total_weight = sum(e["confidence"] for e in agent_emotions)
        merged_vector = EmotionVector()

        for agent_emotion in agent_emotions:
            weight = agent_emotion["confidence"] / total_weight
            emotion = agent_emotion["emotion"]
            merged_vector.joy += emotion.joy * weight
            merged_vector.sadness += emotion.sadness * weight
            merged_vector.anger += emotion.anger * weight
            merged_vector.fear += emotion.fear * weight
            merged_vector.surprise += emotion.surprise * weight
            merged_vector.disgust += emotion.disgust * weight

        intensity = np.linalg.norm(
            [
                merged_vector.joy,
                merged_vector.sadness,
                merged_vector.anger,
                merged_vector.fear,
                merged_vector.surprise,
                merged_vector.disgust,
            ]
        )

        return {
            "emotion_state": EmotionalState(vector=merged_vector),
            "intensity": min(1.0, float(intensity)),
            "dominant_emotion": merged_vector.get_dominant(),
        }
