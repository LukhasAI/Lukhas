import asyncio
from typing import Dict, Any, List

from core.swarm import SwarmAgent
from core.swarm import AgentColony as SymbioticSwarm  # reuse simple colony
from voice.synthesis import VoiceSynthesis


class VoiceSwarmAgent(SwarmAgent):
    """Agent specialized in voice generation."""

    def __init__(self, agent_id: str, voice_params: Dict[str, Any]):
        super().__init__(agent_id, None)
        self.synthesizer = VoiceSynthesis()
        self.specialization = voice_params.get("specialization", "general")

    async def generate_phoneme(self, text_segment: str, context: Dict[str, Any]):
        if self.specialization == "emotion":
            return await self.synthesizer.synthesize(text_segment, emotion=context.get("emotion"))
        else:
            return await self.synthesizer.synthesize(text_segment)


class SwarmVoiceGenerator:
    """Distributed voice generation using swarm."""

    def __init__(self):
        self.voice_swarm = self._create_voice_swarm()
        self.audio_buffer: List[Any] = []

    def _create_voice_swarm(self) -> SymbioticSwarm:
        swarm = SymbioticSwarm("voice-synthesis")
        specializations = [
            ("phoneme", {"specialization": "phoneme"}),
            ("emotion", {"specialization": "emotion"}),
        ]
        for i, (spec_type, params) in enumerate(specializations):
            agent = VoiceSwarmAgent(f"voice-{spec_type}-{i}", params)
            swarm.agents[f"voice-{spec_type}-{i}"] = agent
        return swarm

    def _segment_text(self, text: str) -> List[str]:
        return text.split()

    async def generate_speech(self, text: str, voice_params: Dict[str, Any]) -> List[Any]:
        segments = self._segment_text(text)
        tasks = []
        for i, segment in enumerate(segments):
            context = {
                "position": i / len(segments),
                "emotion": voice_params.get("emotion", "neutral"),
            }
            agent = list(self.voice_swarm.agents.values())[i % len(self.voice_swarm.agents)]
            tasks.append(agent.generate_phoneme(segment, context))
        phonemes = await asyncio.gather(*tasks)
        self.audio_buffer.extend(phonemes)
        return phonemes
