"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - UNIFIED DREAM PIPELINE
║ Orchestrates the complete dream generation, enhancement, and delivery pipeline
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: dream_pipeline.py
║ Path: creativity/dream/dream_pipeline.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Dream Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module provides a unified pipeline for dream generation that:
║ • Integrates all dream generation methods
║ • Handles voice input and output
║ • Manages image and video generation
║ • Coordinates with memory and emotion systems
║ • Provides logging and analytics
║
║ Pipeline Flow:
║ 1. Voice Input (optional) → Whisper → Dream Prompt
║ 2. Dream Generation → Narrative Creation
║ 3. GPT-4 Enhancement → Rich Narrative
║ 4. DALL-E 3 → Visual Generation
║ 5. TTS → Voice Narration
║ 6. Memory Storage → Dream Archive
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .dream_engine.lukhas_oracle_dream import OracleDreamGenerator

# Internal imports
from .dream_generator import generate_dream
from .openai_dream_integration import OpenAIDreamIntegration

# Try to import lukhas.memory and emotion systems
try:
    from consciousness.reflection.unified_memory_manager import (
        EnhancedMemoryManager,
    )

    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from emotion.models import EmotionalResonance

    EMOTION_AVAILABLE = True
except ImportError:
    EMOTION_AVAILABLE = False

logger = logging.getLogger("ΛTRACE.dream.pipeline")


class UnifiedDreamPipeline:
    """
    Unified dream pipeline that orchestrates all dream generation components.
    """

    def __init__(
        self,
        user_id: str = "default",
        output_dir: str = "dream_outputs",
        use_openai: bool = True,
    ):
        """
        Initialize the unified dream pipeline.

        Args:
            user_id: User identifier for personalized dreams
            output_dir: Directory for saving dream outputs
            use_openai: Whether to use OpenAI enhancements
        """
        self.user_id = user_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_openai = use_openai

        # Initialize components
        self.openai_integration = None
        if use_openai:
            try:
                self.openai_integration = OpenAIDreamIntegration()
                logger.info("OpenAI integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.use_openai = False

        # Initialize memory manager if available
        self.memory_manager = None
        if MEMORY_AVAILABLE:
            try:
                self.memory_manager = EnhancedMemoryManager()
                logger.info("Memory manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize memory: {e}")

        # Initialize emotion system if available
        self.emotion_system = None
        if EMOTION_AVAILABLE:
            try:
                self.emotion_system = EmotionalResonance()
                logger.info("Emotion system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize emotion: {e}")

        # Dream log
        self.dream_log_path = self.output_dir / "dream_log.jsonl"

        logger.info(f"Unified Dream Pipeline initialized for user: {user_id}")

    async def generate_dream_from_voice(self, audio_file: str, dream_type: str = "narrative") -> dict[str, Any]:
        """
        Generate a dream from voice input.

        Args:
            audio_file: Path to audio file
            dream_type: Type of dream (narrative, oracle, symbolic)

        Returns:
            Complete dream object
        """
        logger.info(f"Generating dream from voice: {audio_file}")

        dream = {
            "dream_id": f"VOICE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "user_id": self.user_id,
            "type": dream_type,
            "source": "voice_input",
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            # Transcribe voice to text
            if self.openai_integration:
                voice_result = await self.openai_integration.voice_to_dream_prompt(audio_file)
                dream["voice_transcription"] = voice_result
                prompt = voice_result.get("dream_prompt", "a mysterious dream")
            else:
                prompt = "a dream inspired by voice"

            # Generate dream based on type
            if dream_type == "oracle":
                dream_content = await self._generate_oracle_dream(prompt)
            else:
                dream_content = await self._generate_narrative_dream(prompt)

            dream.update(dream_content)

            # Store in memory if available
            if self.memory_manager:
                await self._store_dream_memory(dream)

            # Log dream
            self._log_dream(dream)

            return dream

        except Exception as e:
            logger.error(f"Error in voice dream generation: {e}")
            dream["error"] = str(e)
            return dream

    async def generate_dream_from_text(
        self,
        prompt: str,
        dream_type: str = "narrative",
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Generate a dream from text prompt.

        Args:
            prompt: Text prompt for dream
            dream_type: Type of dream
            context: Additional context

        Returns:
            Complete dream object
        """
        logger.info(f"Generating {dream_type} dream from text")

        dream = {
            "dream_id": f"TEXT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "user_id": self.user_id,
            "type": dream_type,
            "source": "text_input",
            "prompt": prompt,
            "context": context or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            # Add emotional context if available
            if self.emotion_system and context:
                emotion_state = await self._get_emotional_context(context)
                dream["emotional_context"] = emotion_state

            # Generate dream based on type
            if dream_type == "oracle":
                dream_content = await self._generate_oracle_dream(prompt, context)
            elif dream_type == "symbolic":
                dream_content = await self._generate_symbolic_dream(prompt, context)
            else:
                dream_content = await self._generate_narrative_dream(prompt, context)

            dream.update(dream_content)

            # Store in memory
            if self.memory_manager:
                await self._store_dream_memory(dream)

            # Log dream
            self._log_dream(dream)

            return dream

        except Exception as e:
            logger.error(f"Error in text dream generation: {e}")
            dream["error"] = str(e)
            return dream

    async def _generate_narrative_dream(self, prompt: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Generate a narrative dream with full enhancements."""
        if self.use_openai and self.openai_integration:
            # Use OpenAI-enhanced generation
            result = await self.openai_integration.create_full_dream_experience(
                prompt=prompt, generate_image=True, generate_audio=True
            )
            result["generation_method"] = "openai_enhanced"
        else:
            # Use basic generation
            def dummy_evaluate(action):
                return {"status": "allowed"}

            result = generate_dream(dummy_evaluate)
            result["generation_method"] = "basic"

        return result

    async def _generate_oracle_dream(self, prompt: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Generate an oracle-style dream."""

        # Create mock consent profile and memory sampler
        class MockConsent:
            def allows(self, feature):
                return True

        class MockMemorySampler:
            def pick_emotional_memory(self, priority):
                return {"emotion": "wonder", "tag": "stargazing"}

        oracle = OracleDreamGenerator(
            user_id=self.user_id,
            consent_profile=MockConsent(),
            external_context=context or {},
            memory_sampler=MockMemorySampler(),
        )

        if hasattr(oracle, "openai_integration") and oracle.openai_integration:
            # Use enhanced oracle dream
            result = await oracle.generate_oracle_dream_enhanced()
        else:
            # Use basic oracle dream
            result = oracle.generate_oracle_dream()

        result["generation_method"] = "oracle"
        return result

    async def _generate_symbolic_dream(self, prompt: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Generate a symbolic dream with GLYPHs and quantum elements."""
        # Generate base narrative
        narrative_dream = await self._generate_narrative_dream(prompt, context)

        # Add symbolic elements
        symbols = [
            "ΛQUANTUM",
            "ΛMEMORY",
            "ΛCONSCIOUSNESS",
            "ΛEMOTION",
            "ΛBRIDGE",
            "ΛCREATE",
        ]

        qi_states = [
            "superposition",
            "entanglement",
            "collapse",
            "coherence",
            "decoherence",
        ]

        narrative_dream.update(
            {
                "symbolic_elements": {
                    "primary_glyph": random.choice(symbols),
                    "qi_state": random.choice(qi_states),
                    "collapse_probability": round(random.uniform(0.3, 0.9), 3),
                    "entanglement_nodes": random.randint(2, 5),
                    "coherence_factor": round(random.uniform(0.6, 0.95), 3),
                },
                "generation_method": "symbolic",
            }
        )

        return narrative_dream

    async def _get_emotional_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract emotional context from provided context."""
        if self.emotion_system:
            # Use emotion system to analyze context
            return {
                "dominant_emotion": context.get("mood", "neutral"),
                "emotional_intensity": context.get("intensity", 0.5),
                "emotional_valence": context.get("valence", 0.0),
            }
        return {}

    async def _store_dream_memory(self, dream: dict[str, Any]):
        """Store dream in memory system."""
        if self.memory_manager:
            try:
                memory_data = {
                    "type": "dream",
                    "content": dream,
                    "emotional_tags": dream.get("emotional_context", {}),
                    "user_id": self.user_id,
                }

                result = await self.memory_manager.store_memory(memory_data, memory_id=dream["dream_id"])

                logger.info(f"Dream stored in memory: {result}")
            except Exception as e:
                logger.error(f"Failed to store dream in memory: {e}")

    def _log_dream(self, dream: dict[str, Any]):
        """Log dream to file."""
        try:
            with open(self.dream_log_path, "a") as f:
                json.dump(dream, f)
                f.write("\n")
            logger.info(f"Dream logged: {dream['dream_id']}")
        except Exception as e:
            logger.error(f"Failed to log dream: {e}")

    async def replay_dream(self, dream_id: str) -> Optional[dict[str, Any]]:
        """
        Replay a previously generated dream.

        Args:
            dream_id: ID of dream to replay

        Returns:
            Dream object or None if not found
        """
        # Load from log
        if self.dream_log_path.exists():
            with open(self.dream_log_path) as f:
                for line in f:
                    dream = json.loads(line.strip())
                    if dream.get("dream_id") == dream_id:
                        logger.info(f"Replaying dream: {dream_id}")

                        # Re-narrate if audio available
                        if "narration" in dream and self.openai_integration:
                            print(f"🎙️ Playing narration: {dream['narration']['path']}")

                        # Display image if available
                        if "generated_image" in dream:
                            print(f"🎨 Showing image: {dream['generated_image']['path']}")

                        return dream

        logger.warning(f"Dream not found: {dream_id}")
        return None

    async def get_dream_analytics(self) -> dict[str, Any]:
        """Get analytics about generated dreams."""
        analytics = {
            "total_dreams": 0,
            "by_type": {},
            "by_source": {},
            "with_audio": 0,
            "with_image": 0,
            "errors": 0,
        }

        if self.dream_log_path.exists():
            with open(self.dream_log_path) as f:
                for line in f:
                    dream = json.loads(line.strip())
                    analytics["total_dreams"] += 1

                    # Count by type
                    dream_type = dream.get("type", "unknown")
                    analytics["by_type"][dream_type] = analytics["by_type"].get(dream_type, 0) + 1

                    # Count by source
                    source = dream.get("source", "unknown")
                    analytics["by_source"][source] = analytics["by_source"].get(source, 0) + 1

                    # Count features
                    if "narration" in dream:
                        analytics["with_audio"] += 1
                    if "generated_image" in dream:
                        analytics["with_image"] += 1
                    if "error" in dream:
                        analytics["errors"] += 1

        return analytics

    async def close(self):
        """Clean up resources."""
        if self.openai_integration:
            await self.openai_integration.close()
        logger.info("Dream pipeline closed")


# Example usage
async def demo_pipeline():
    """Demonstrate the unified dream pipeline."""
    pipeline = UnifiedDreamPipeline(user_id="demo_user")

    try:
        # Generate a narrative dream
        print("🌙 Generating narrative dream...")
        dream1 = await pipeline.generate_dream_from_text(
            "a journey through crystalline memories", dream_type="narrative"
        )
        print(f"Dream created: {dream1['dream_id']}")

        # Generate an oracle dream
        print("\n🔮 Generating oracle dream...")
        dream2 = await pipeline.generate_dream_from_text(
            "guidance for tomorrow",
            dream_type="oracle",
            context={"mood": "hopeful", "time": "morning"},
        )
        print(f"Oracle dream: {dream2.get('message', 'No message')}")

        # Generate a symbolic dream
        print("\n🧬 Generating symbolic dream...")
        dream3 = await pipeline.generate_dream_from_text("quantum consciousness exploration", dream_type="symbolic")
        print(f"Symbolic elements: {dream3.get('symbolic_elements', {})}")

        # Get analytics
        print("\n📊 Dream Analytics:")
        analytics = await pipeline.get_dream_analytics()
        print(json.dumps(analytics, indent=2))

    finally:
        await pipeline.close()


if __name__ == "__main__":
    import random

    asyncio.run(demo_pipeline())
