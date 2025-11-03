"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - OPENAI DREAM INTEGRATION
║ Comprehensive OpenAI integration for dream generation, narration, and visualization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: openai_dream_integration.py
║ Path: creativity/dream/openai_dream_integration.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Dream Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module provides comprehensive OpenAI integration for the LUKHAS dream system:
║ • GPT-4 for enhanced dream narrative generation
║ • DALL-E 3 for dream image creation
║ • OpenAI TTS for dream voice narration
║ • Whisper for voice input processing
║ • Video generation preparation for SORA
║
║ Features:
║ • Asynchronous API operations
║ • Multi-modal dream experiences
║ • Voice-to-dream and dream-to-voice pipelines
║ • Image generation from dream narratives
║ • Comprehensive error handling and fallbacks
╚══════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# OpenAI imports
from openai import AsyncOpenAI, OpenAI

# Internal imports
from bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient

logger = logging.getLogger("ΛTRACE.dream.openai_integration")


class OpenAIDreamIntegration:
    """
    Comprehensive OpenAI integration for LUKHAS dream system.
    Handles text generation, image creation, voice synthesis, and voice recognition.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI dream integration.

        Args:
            api_key: Optional API key. If not provided, uses OPENAI_API_KEY env var.
        """
        # Initialize unified client for text operations
        self.text_client = UnifiedOpenAIClient(api_key)

        # Initialize direct OpenAI clients for specialized operations
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.sync_client = OpenAI(api_key=self.api_key)

        # Configuration
        self.tts_voice = "nova"  # Options: alloy, echo, fable, onyx, nova, shimmer
        self.tts_model = "tts-1-hd"  # High quality TTS
        self.whisper_model = "whisper-1"
        self.dalle_model = "dall-e-3"

        # Paths for saving outputs
        self.output_dir = Path("dream_outputs")
        self.output_dir.mkdir(exist_ok=True)

        logger.info("OpenAI Dream Integration initialized")

    # ═══════════════════════════════════════════════════════════════════
    # TEXT GENERATION - Enhanced Dream Narratives
    # ═══════════════════════════════════════════════════════════════════

    async def enhance_dream_narrative(
        self,
        base_dream: dict[str, Any],
        style: str = "surreal and poetic",
        length: str = "medium",
    ) -> dict[str, Any]:
        """
        Enhance a basic dream with rich narrative using GPT-4.

        Args:
            base_dream: Basic dream structure with theme and elements
            style: Writing style for the narrative
            length: Desired length (short, medium, long)

        Returns:
            Enhanced dream with rich narrative
        """
        # Prepare the prompt
        prompt = f"""Create a vivid, dreamlike narrative based on these elements:

Theme: {base_dream.get("narrative", {}).get("theme", "mysterious journey")}
Emotion: {base_dream.get("narrative", {}).get("primary_emotion", "wonder")}
Atmosphere: {base_dream.get("narrative", {}).get("atmosphere", "dreamlike")}
Colors: {base_dream.get("narrative", {}).get("color_palette", "ethereal")}

Style: {style}
Length: {length} (aim for {"100-150" if length == "short" else "200-300" if length == "medium" else "400-500"} words)

Create a narrative that:
1. Is highly visual and suitable for image/video generation
2. Flows like a dream with surreal transitions
3. Evokes strong emotions and sensory experiences
4. Includes specific visual details that can be rendered
5. Maintains a coherent dreamlike atmosphere

The narrative should be immersive and poetic, suitable for both reading and visual generation."""

        try:
            response = await self.text_client.creative_task(prompt, style=style)

            # Update dream with enhanced narrative
            base_dream["enhanced_narrative"] = {
                "full_text": response,
                "style": style,
                "length": length,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "gpt_model": "gpt-4",
            }

            # Generate a shorter version for image prompts
            image_prompt = await self._create_image_prompt(response)
            base_dream["image_prompt"] = image_prompt

            logger.info(f"Enhanced dream narrative created: {base_dream.get('dream_id', 'unknown')}")
            return base_dream

        except Exception as e:
            logger.error(f"Error enhancing dream narrative: {e}")
            base_dream["enhancement_error"] = str(e)
            return base_dream

    async def _create_image_prompt(self, narrative: str) -> str:
        """Create a concise image generation prompt from narrative."""
        prompt = f"""Convert this dream narrative into a concise, visual description suitable for image generation (max 100 words):

{narrative}

Focus on:
- Key visual elements
- Colors and lighting
- Atmosphere and mood
- Main subjects or scenes
- Artistic style

Make it vivid and specific for image generation."""

        response = await self.text_client.chat_completion(prompt, task="creativity", temperature=0.7, max_tokens=150)

        return response["choices"][0]["message"]["content"]

    # ═══════════════════════════════════════════════════════════════════
    # IMAGE GENERATION - DALL-E 3 Integration
    # ═══════════════════════════════════════════════════════════════════

    async def generate_dream_image(
        self,
        dream: dict[str, Any],
        size: str = "1024x1024",
        quality: str = "hd",
        style: str = "vivid",
    ) -> dict[str, Any]:
        """
        Generate an image from dream narrative using DALL-E 3.

        Args:
            dream: Dream object with narrative or image_prompt
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)
            style: Image style (vivid, natural)

        Returns:
            Updated dream with image information
        """
        # Get image prompt
        image_prompt = dream.get("image_prompt") or dream.get("narrative", {}).get("visual_prompt")

        if not image_prompt:
            logger.error("No image prompt found in dream")
            dream["image_error"] = "No image prompt available"
            return dream

        try:
            # Generate image
            response = await self.async_client.images.generate(
                model=self.dalle_model,
                prompt=image_prompt,
                size=size,
                quality=quality,
                style=style,
                response_format="b64_json",  # Get base64 for storage
            )

            # Extract image data
            image_data = response.data[0]
            image_b64 = image_data.b64_json

            # Save image
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            dream_id = dream.get("dream_id", "unknown")
            image_path = self.output_dir / f"dream_{dream_id}_{timestamp}.png"

            # Decode and save
            image_bytes = base64.b64decode(image_b64)
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # Update dream object
            dream["generated_image"] = {
                "path": str(image_path),
                "size": size,
                "quality": quality,
                "style": style,
                "revised_prompt": image_data.revised_prompt,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": self.dalle_model,
            }

            logger.info(f"Dream image generated: {image_path}")
            return dream

        except Exception as e:
            logger.error(f"Error generating dream image: {e}")
            dream["image_error"] = str(e)
            return dream

    # ═══════════════════════════════════════════════════════════════════
    # VOICE SYNTHESIS - TTS Integration
    # ═══════════════════════════════════════════════════════════════════

    async def narrate_dream(
        self, dream: dict[str, Any], voice: Optional[str] = None, speed: float = 1.0
    ) -> dict[str, Any]:
        """
        Generate voice narration for dream using OpenAI TTS.

        Args:
            dream: Dream object with narrative text
            voice: Voice to use (defaults to self.tts_voice)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            Updated dream with audio information
        """
        # Get text to narrate
        text = dream.get("enhanced_narrative", {}).get("full_text") or dream.get("narrative", {}).get("description")

        if not text:
            logger.error("No text found for narration")
            dream["audio_error"] = "No narrative text available"
            return dream

        voice = voice or self.tts_voice

        try:
            # Generate audio
            response = await self.async_client.audio.speech.create(
                model=self.tts_model, voice=voice, input=text, speed=speed
            )

            # Save audio
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            dream_id = dream.get("dream_id", "unknown")
            audio_path = self.output_dir / f"dream_{dream_id}_{timestamp}.mp3"

            # Stream to file
            response.stream_to_file(audio_path)

            # Update dream object
            dream["narration"] = {
                "path": str(audio_path),
                "voice": voice,
                "speed": speed,
                "text_length": len(text),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": self.tts_model,
            }

            logger.info(f"Dream narration generated: {audio_path}")
            return dream

        except Exception as e:
            logger.error(f"Error generating dream narration: {e}")
            dream["audio_error"] = str(e)
            return dream

    # ═══════════════════════════════════════════════════════════════════
    # VOICE RECOGNITION - Whisper Integration
    # ═══════════════════════════════════════════════════════════════════

    async def voice_to_dream_prompt(self, audio_file: str, language: Optional[str] = None) -> dict[str, Any]:
        """
        Convert voice input to dream prompt using Whisper.

        Args:
            audio_file: Path to audio file
            language: Optional language code

        Returns:
            Transcription result with dream prompt
        """
        try:
            # Open audio file
            with open(audio_file, "rb") as f:
                # Transcribe
                response = await self.async_client.audio.transcriptions.create(
                    model=self.whisper_model, file=f, language=language
                )

            # Process transcription into dream prompt
            transcribed_text = response.text

            # Enhance the transcription into a dream prompt
            enhanced_prompt = await self._enhance_voice_prompt(transcribed_text)

            result = {
                "original_audio": audio_file,
                "transcription": transcribed_text,
                "dream_prompt": enhanced_prompt,
                "language": language,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"Voice transcribed to dream prompt: {len(transcribed_text)} chars")
            return result

        except Exception as e:
            logger.error(f"Error transcribing voice: {e}")
            return {"error": str(e), "audio_file": audio_file}

    async def _enhance_voice_prompt(self, transcription: str) -> str:
        """Enhance voice transcription into a dream prompt."""
        prompt = f"""Transform this spoken description into a vivid dream scenario:

Spoken words: "{transcription}"

Create a dreamlike interpretation that:
1. Captures the essence of what was said
2. Adds surreal and symbolic elements
3. Enhances with sensory details
4. Makes it visually rich and emotionally resonant

Keep it concise but evocative."""

        response = await self.text_client.creative_task(prompt)
        return response

    # ═══════════════════════════════════════════════════════════════════
    # COMPLETE DREAM PIPELINE
    # ═══════════════════════════════════════════════════════════════════

    async def create_full_dream_experience(
        self,
        prompt: str,
        voice_input: Optional[str] = None,
        generate_image: bool = True,
        generate_audio: bool = True,
        image_size: str = "1024x1024",
    ) -> dict[str, Any]:
        """
        Create a complete multi-modal dream experience.

        Args:
            prompt: Text prompt or theme for dream
            voice_input: Optional voice input file
            generate_image: Whether to generate image
            generate_audio: Whether to generate narration
            image_size: Size for generated image

        Returns:
            Complete dream object with all generated content
        """
        dream_id = f"DREAM_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Initialize dream object
        dream = {
            "dream_id": dream_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "initial_prompt": prompt,
            "pipeline_config": {
                "generate_image": generate_image,
                "generate_audio": generate_audio,
                "image_size": image_size,
            },
        }

        try:
            # Process voice input if provided
            if voice_input:
                voice_result = await self.voice_to_dream_prompt(voice_input)
                dream["voice_input"] = voice_result
                if "dream_prompt" in voice_result:
                    prompt = voice_result["dream_prompt"]

            # Generate base dream narrative
            base_narrative = {
                "narrative": {
                    "theme": prompt,
                    "description": f"A dream about {prompt}",
                    "visual_prompt": f"Surreal dreamscape of {prompt}",
                }
            }

            # Enhance narrative with GPT-4
            dream.update(base_narrative)
            dream = await self.enhance_dream_narrative(dream)

            # Generate image if requested
            if generate_image and "image_prompt" in dream:
                dream = await self.generate_dream_image(dream, size=image_size)

            # Generate audio narration if requested
            if generate_audio and "enhanced_narrative" in dream:
                dream = await self.narrate_dream(dream)

            # Add SORA video generation prompt
            if "enhanced_narrative" in dream:
                dream["sora_prompt"] = await self._create_sora_prompt(dream)

            # Save complete dream
            self._save_dream_record(dream)

            logger.info(f"Complete dream experience created: {dream_id}")
            return dream

        except Exception as e:
            logger.error(f"Error in dream pipeline: {e}")
            dream["pipeline_error"] = str(e)
            return dream

    async def _create_sora_prompt(self, dream: dict[str, Any]) -> str:
        """Create a video generation prompt for SORA."""
        narrative = dream.get("enhanced_narrative", {}).get("full_text", "")

        prompt = f"""Convert this dream narrative into a video generation prompt for SORA:

{narrative}

Create a cinematic description that includes:
- Camera movements and angles
- Transitions between scenes
- Motion and dynamics
- Temporal progression
- Visual effects and atmosphere

Keep it under 150 words and focus on motion and cinematography."""

        response = await self.text_client.chat_completion(prompt, task="creativity", temperature=0.8, max_tokens=200)

        return response["choices"][0]["message"]["content"]

    def _save_dream_record(self, dream: dict[str, Any]):
        """Save complete dream record to JSON."""
        dream_file = self.output_dir / f"{dream['dream_id']}.json"
        with open(dream_file, "w") as f:
            json.dump(dream, f, indent=2)
        logger.info(f"Dream record saved: {dream_file}")

    async def close(self):
        """Clean up resources."""
        await self.text_client.close()
        await self.async_client.close()
        logger.info("OpenAI Dream Integration closed")


# Example usage function
async def demo_dream_creation():
    """Demonstrate the complete dream creation pipeline."""
    integration = OpenAIDreamIntegration()

    try:
        # Create a complete dream experience
        dream = await integration.create_full_dream_experience(
            prompt="a journey through memories that shimmer like stars",
            generate_image=True,
            generate_audio=True,
        )

        print(f"Dream created: {dream['dream_id']}")
        print(f"Narrative: {dream.get('enhanced_narrative', {}).get('full_text', 'N/A')[:200]}...")

        if "generated_image" in dream:
            print(f"Image saved: {dream['generated_image']['path']}")

        if "narration" in dream:
            print(f"Audio saved: {dream['narration']['path']}")

        if "sora_prompt" in dream:
            print(f"SORA prompt: {dream['sora_prompt']}")

    finally:
        await integration.close()


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_dream_creation())