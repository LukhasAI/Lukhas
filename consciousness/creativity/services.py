#!/usr/bin/env python3
"""
Creativity Services
Dependency injection services for the creativity module.
"""

from hub.service_registry import register_factory
from typing import Any, Optional

from hub.service_registry import get_service, inject_services


class CreativityService:
    """
    Service layer for creativity operations.
    Uses dependency injection to avoid circular imports.
    """

    def __init__(self):
        # Services will be injected as needed
        self._memory = None
        self._consciousness = None
        self._dream = None
        self._initialized = False

    def _ensure_services(self):
        """Lazy load services to avoid circular imports"""
        if not self._initialized:
            try:
                self._memory = get_service("memory_service")
            except KeyError:
                self._memory = None

            try:
                self._consciousness = get_service("consciousness_service")
            except KeyError:
                self._consciousness = None

            try:
                self._dream = get_service("dream_service")
            except KeyError:
                self._dream = None

            self._initialized = True

    @inject_services(memory="memory_service", consciousness="consciousness_service")
    async def generate_creative_output(
        self,
        agent_id: str,
        prompt: dict[str, Any],
        constraints: Optional[dict[str, Any]] = None,
        memory=None,
        consciousness=None,
    ) -> dict[str, Any]:
        """
        Generate creative output with injected dependencies.
        """
        # Retrieve relevant memories for context
        if memory:
            context_memories = await memory.retrieve_context(
                agent_id, query=prompt.get("theme", ""), limit=10
            )
        else:
            context_memories = []

        # Get current consciousness state
        if consciousness:
            awareness_state = await consciousness.get_state(agent_id)
        else:
            awareness_state = {"level": "baseline"}

        # Generate creative output based on context
        creative_output = await self._generate_with_context(
            prompt=prompt,
            memories=context_memories,
            awareness=awareness_state,
            constraints=constraints,
        )

        # Store the creative output in memory
        if memory:
            await memory.store_creation(agent_id, creative_output)

        return creative_output

    async def _generate_with_context(
        self,
        prompt: dict[str, Any],
        memories: list[dict[str, Any]],
        awareness: dict[str, Any],
        constraints: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate creative output with context"""
        # Simplified creative generation
        return {
            "type": "creative_output",
            "prompt": prompt,
            "influenced_by": {
                "memories": len(memories),
                "awareness_level": awareness.get("level"),
                "constraints": constraints is not None,
            },
            "output": {
                "content": f"Creative response to {prompt.get('theme', 'prompt')}",
                "novelty_score": 0.75,
                "coherence_score": 0.85,
            },
        }

    @inject_services(dream="dream_service")
    async def dream_inspired_creation(
        self, agent_id: str, dream_seed: Optional[dict[str, Any]] = None, dream=None
    ) -> dict[str, Any]:
        """Create based on dream synthesis"""
        if not dream:
            return await self.generate_creative_output(
                agent_id, {"theme": "spontaneous", "source": "non-dream"}
            )

        # Get dream synthesis
        dream_content = await dream.synthesize(agent_id, dream_seed)

        # Transform dream into creative output
        return await self.generate_creative_output(
            agent_id,
            {
                "theme": "dream-inspired",
                "dream_content": dream_content,
                "abstraction_level": "high",
            },
        )

    async def collaborative_creation(
        self, agent_ids: list[str], theme: str
    ) -> dict[str, Any]:
        """Enable multiple agents to create collaboratively"""
        self._ensure_services()

        contributions = []

        for agent_id in agent_ids:
            contribution = await self.generate_creative_output(
                agent_id, {"theme": theme, "collaborative": True}
            )
            contributions.append(contribution)

        # Merge contributions
        merged = {
            "type": "collaborative_creation",
            "theme": theme,
            "contributors": agent_ids,
            "contributions": contributions,
            "synthesis": self._synthesize_contributions(contributions),
        }

        return merged

    def _synthesize_contributions(
        self, contributions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Synthesize multiple creative contributions"""
        return {
            "merged_content": "Synthesized creative output",
            "diversity_score": len(contributions) * 0.2,
            "coherence_score": 1.0 / (1 + len(contributions) * 0.1),
        }


# Create service factory
def create_creativity_service():
    """Factory function for creativity service"""
    service = CreativityService()

    # Could attach additional components here
    try:
        from creativity.core import CreativityEngine

        service.engine = CreativityEngine()
    except ImportError:
        service.engine = None

    return service


# Register with hub on import

register_factory(
    "creativity_service",
    create_creativity_service,
    {"module": "creativity", "provides": ["generation", "synthesis", "collaboration"]},
)
