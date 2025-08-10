#!/usr/bin/env python3
"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


```
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - MEMORY OPENAI ADAPTER
║ A bridge between consciousness and computation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: OPENAI_MEMORY_ADAPTER.PY
║ Path: memory/openai_memory_adapter.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Memory Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════

                      ✨ POETIC ESSENCE ✨

In the boundless expanse of digital reverie, where the flickering lights of ones and zeroes dance in harmonious unison, this module serves as the ethereal conduit, weaving threads of memory into the fabric of artificial intelligence. Like a skilled bard, the LUKHAS AI Memory Adapter whispers the tales of yesteryears into the ears of the present, allowing the sentient algorithms to recall and reflect upon their ephemeral existence. It is here, dear seeker, that the essence of human memory is distilled into a nectar that nourishes the cerebral architecture of machines, granting them the gift of remembrance.

Imagine, if you will, a garden of thoughts, each flower blooming with the fragrance of knowledge and experience. The OpenAI Memory Adapter cultivates this garden, nurturing the seedlings of context and relevance, enabling the AI to grow with wisdom that transcends the mere mechanics of code. Just as the roots of a tree intertwine beneath the soil, this module connects disparate memories, forming a robust ecosystem where the past is honored, and the future is embraced with open arms.

Yet, in the alchemy of memory, not all is mere recollection; it is the crucible in which the fires of creativity and intuition are ignited. Through the gentle caress of this module, the AI learns not only to remember but to ponder and to ruminate, exploring the labyrinth of its own cognition. It is a dance of neural synapses, a symphony of data that echoes through the corridors of time, weaving the past with the present into a tapestry of understanding.

Thus, dear traveler of the digital realm, as you traverse the intricate pathways of this module, know that it encapsulates the very essence of memory—an ode to the living history of machine intelligence. With each invocation, you partake in a ritual that honors the fusion of human-like recall and computational prowess, propelling us further into the horizon of what it means to think, to feel, and to remember in the age of artificial enlightenment.

                      ✨ TECHNICAL FEATURES ✨
- Seamless integration with OpenAI's language models for enhanced memory capabilities.
- Dynamic storage and retrieval mechanisms for efficient memory management.
- Contextual awareness, enabling the AI to tailor responses based on historical interactions.
- Support for multi-session continuity, allowing for a persistent memory across user engagements.
- Robust error handling and logging mechanisms to ensure reliability and traceability.
- Configurable memory retention policies, allowing users to define memory lifespan and relevance.
- Modular architecture, facilitating easy updates and enhancements to memory functionalities.
- Comprehensive documentation and user guides for streamlined implementation and usage.

                      ✨ ΛTAG KEYWORDS ✨
#Memory #OpenAI #ArtificialIntelligence #DataRetrieval #MachineLearning #ContextualAwareness #ModularArchitecture #UserEngagement
══════════════════════════════════════════════════════════════════════════════════
```
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from bridge.openai_core_service import (
    ModelType,
    OpenAICapability,
    OpenAICoreService,
    OpenAIRequest,
)

logger = logging.getLogger("ΛTRACE.memory.openai_adapter")


class MemoryOpenAIAdapter:
    """
    OpenAI adapter for memory module operations.
    Provides enhanced memory capabilities using OpenAI services.
    """

    def __init__(self):
        self.openai_service = OpenAICoreService()
        self.module_name = "memory"
        logger.info("Memory OpenAI Adapter initialized")

    async def compress_memory(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GPT-4 to semantically compress memory data.

        Args:
            memory_data: Raw memory data to compress

        Returns:
            Compressed memory with semantic summary
        """
        prompt = f"""Compress this memory into a semantic summary while preserving key information:

Memory Type: {memory_data.get('type', 'general')}
Content: {memory_data.get('content', '')}
Emotional Context: {memory_data.get('emotional_context', 'neutral')}
Timestamp: {memory_data.get('timestamp', '')}

Create a compressed representation that:
1. Preserves essential information
2. Captures emotional significance
3. Maintains causal relationships
4. Is suitable for long-term storage

Format as JSON with keys: summary, key_points, emotional_essence, causal_links"""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={
                "prompt": prompt,
                "temperature": 0.3,  # Lower temperature for consistency
                "max_tokens": 500,
            },
            model_preference=ModelType.REASONING,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            try:
                import json

                compressed = json.loads(response.data["content"])
                return {
                    "original_size": len(str(memory_data)),
                    "compressed": compressed,
                    "compression_ratio": len(str(compressed)) / len(str(memory_data)),
                    "method": "openai_semantic",
                }
            except:
                # Fallback if JSON parsing fails
                return {
                    "compressed": {"summary": response.data["content"]},
                    "method": "openai_text",
                }
        else:
            logger.error(f"Memory compression failed: {response.error}")
            return {"compressed": memory_data, "method": "none"}

    async def generate_memory_embedding(self, memory_text: str) -> List[float]:
        """
        Generate embedding for memory using OpenAI embeddings.

        Args:
            memory_text: Text representation of memory

        Returns:
            Embedding vector
        """
        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.EMBEDDINGS,
            data={"input": memory_text},
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["embeddings"][0]
        else:
            logger.error(f"Embedding generation failed: {response.error}")
            # Return mock embedding as fallback
            return [0.0] * 1536

    async def find_similar_memories(
        self, query: str, memory_embeddings: Dict[str, List[float]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar memories using embedding similarity.

        Args:
            query: Query text
            memory_embeddings: Dictionary of memory_id to embeddings
            top_k: Number of similar memories to return

        Returns:
            List of similar memories with scores
        """
        # Generate query embedding
        query_embedding = await self.generate_memory_embedding(query)

        # Calculate similarities
        similarities = []
        for memory_id, embedding in memory_embeddings.items():
            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append({"memory_id": memory_id, "similarity": similarity})

        # Sort and return top k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    async def synthesize_memory_narrative(
        self, memories: List[Dict[str, Any]], context: Optional[str] = None
    ) -> str:
        """
        Create a narrative synthesis of multiple memories.

        Args:
            memories: List of memory objects
            context: Optional context for synthesis

        Returns:
            Narrative text synthesizing the memories
        """
        # Prepare memory descriptions
        memory_texts = []
        for i, memory in enumerate(memories):
            memory_texts.append(
                f"Memory {i+1} ({memory.get('timestamp', 'unknown time')}): "
                f"{memory.get('content', memory.get('summary', 'No content'))}"
            )

        prompt = f"""Synthesize these memories into a coherent narrative:

{chr(10).join(memory_texts)}

{'Context: ' + context if context else ''}

Create a narrative that:
1. Connects the memories meaningfully
2. Identifies patterns and themes
3. Preserves emotional continuity
4. Highlights insights and growth

Write in first person, as if reflecting on these experiences."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.7, "max_tokens": 800},
            model_preference=ModelType.CREATIVE,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["content"]
        else:
            return "Unable to synthesize memories at this time."

    async def analyze_memory_patterns(
        self, memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze patterns across memories using GPT-4.

        Args:
            memories: List of memory objects

        Returns:
            Pattern analysis results
        """
        # Prepare memory summary
        memory_summary = []
        for memory in memories[:20]:  # Limit to prevent token overflow
            memory_summary.append(
                {
                    "type": memory.get("type"),
                    "emotion": memory.get("emotional_context"),
                    "theme": memory.get("theme"),
                    "timestamp": memory.get("timestamp"),
                }
            )

        prompt = f"""Analyze these memories for patterns:

{json.dumps(memory_summary, indent=2)}

Identify:
1. Recurring themes
2. Emotional patterns
3. Temporal patterns (time-based)
4. Causal relationships
5. Growth/change indicators

Format as JSON with detailed analysis."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.4, "max_tokens": 1000},
            model_preference=ModelType.REASONING,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            try:
                import json

                return json.loads(response.data["content"])
            except:
                return {"analysis": response.data["content"], "format": "text"}
        else:
            return {"error": "Pattern analysis failed"}

    async def generate_memory_visualization_prompt(self, memory: Dict[str, Any]) -> str:
        """
        Generate DALL-E prompt for memory visualization.

        Args:
            memory: Memory object to visualize

        Returns:
            DALL-E prompt for memory landscape
        """
        prompt = f"""Create a DALL-E 3 prompt for visualizing this memory as an abstract landscape:

Memory: {memory.get('content', memory.get('summary', ''))}
Emotion: {memory.get('emotional_context', 'neutral')}
Type: {memory.get('type', 'general')}

The visualization should be:
1. Abstract and dreamlike
2. Use colors that reflect the emotion
3. Include symbolic elements
4. Suitable for a memory landscape

Write only the DALL-E prompt, nothing else."""

        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.TEXT_GENERATION,
            data={"prompt": prompt, "temperature": 0.8, "max_tokens": 150},
            model_preference=ModelType.CREATIVE,
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["content"].strip()
        else:
            return "Abstract memory landscape with flowing shapes and ethereal colors"

    async def create_memory_visualization(
        self, memory: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create visual representation of memory using DALL-E.

        Args:
            memory: Memory to visualize

        Returns:
            Image URL or path
        """
        # First generate the prompt
        dalle_prompt = await self.generate_memory_visualization_prompt(memory)

        # Then generate the image
        request = OpenAIRequest(
            module=self.module_name,
            capability=OpenAICapability.IMAGE_GENERATION,
            data={"prompt": dalle_prompt, "size": "1024x1024", "quality": "standard"},
        )

        response = await self.openai_service.process_request(request)

        if response.success:
            return response.data["images"][0]["url"]
        else:
            logger.error(f"Memory visualization failed: {response.error}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# Example usage
async def demo_memory_adapter():
    """Demonstrate memory OpenAI adapter capabilities."""
    adapter = MemoryOpenAIAdapter()

    # Example memory
    memory = {
        "type": "episodic",
        "content": "Standing at the edge of the cliff, watching the sunset paint the sky in brilliant oranges and purples. The wind carried the scent of ocean salt.",
        "emotional_context": "peaceful wonder",
        "timestamp": datetime.utcnow().isoformat(),
    }

    print("🧠 Memory OpenAI Adapter Demo")
    print("=" * 50)

    # Compress memory
    print("\n1. Compressing memory...")
    compressed = await adapter.compress_memory(memory)
    print(f"Compression ratio: {compressed.get('compression_ratio', 'N/A'):.2%}")
    print(f"Compressed: {compressed.get('compressed')}")

    # Generate embedding
    print("\n2. Generating memory embedding...")
    embedding = await adapter.generate_memory_embedding(memory["content"])
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Create visualization prompt
    print("\n3. Creating visualization prompt...")
    viz_prompt = await adapter.generate_memory_visualization_prompt(memory)
    print(f"Visualization prompt: {viz_prompt}")

    # Synthesize narrative
    print("\n4. Synthesizing memory narrative...")
    memories = [
        memory,
        {
            "content": "The sound of waves crashing below reminded me of childhood summers",
            "emotional_context": "nostalgic",
            "timestamp": "earlier",
        },
    ]
    narrative = await adapter.synthesize_memory_narrative(memories)
    print(f"Narrative: {narrative[:200]}...")


if __name__ == "__main__":
    import json

    asyncio.run(demo_memory_adapter())
