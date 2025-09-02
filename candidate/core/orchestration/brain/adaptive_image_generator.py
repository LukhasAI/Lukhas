"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: adaptive_image_generator.py
Advanced: adaptive_image_generator.py
Integration Date: 2025-05-31T07:55:27.762144
"""

import asyncio
import logging
from typing import Optional

from candidate.bridge.llm_wrappers.unified_openai_client import (
    UnifiedOpenAIClient as GPTClient,
)
from integrations.openai.dalle_client import DALLEClient

logger = logging.getLogger(__name__)


class AdaptiveImageGenerator:
    """
    Generates context-aware images that match user needs and preferences.
    Design philosophy emphasizes clarity and purposeful visuals.
    """

    def __init__(self, api_config=None):
        self.default_style = "minimalist"
        self.cached_generations = {}
        self.max_cache_size = 100
        self.generation_quality = "standard"
        self.active_requests = set()
        self.request_limiter = asyncio.Semaphore(5)  # Limit concurrent generations

        # Initialize API clients
        self.dalle_client = DALLEClient(api_key=api_config.get("api_key") if api_config else None)
        self.gpt_client = GPTClient(api_key=api_config.get("api_key") if api_config else None)

        # Style mapping for DALL-E
        self.style_mapping = {
            "minimalist": "natural",  # DALL-E style parameter
            "futuristic": "vivid",  # DALL-E style parameter
            "natural": "natural",
            "professional": "natural",
            "vibrant": "vivid",
        }

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        size: str = "1024x1024",
        user_context: Optional[dict] = None,
        priority: int = 1,
    ) -> dict:
        """
        Generate an image based on text prompt with contextual awareness
        """
        style = style or self.default_style

        # Check cache first
        cache_key = f"{prompt}:{style}:{size}"
        if cache_key in self.cached_generations:
            logger.info(f"Using cached image for prompt: {prompt[:30]}...")
            return self.cached_generations[cache_key]

        # Add request tracking
        request_id = self._generate_request_id()
        self.active_requests.add(request_id)

        try:
            async with self.request_limiter:
                # Enhance prompt based on user context
                enhanced_prompt = await self._enhance_prompt(prompt, user_context, style)

                logger.info(f"Generating image with prompt: {enhanced_prompt[:50]}...")

                # Call DALL-E API for actual generation
                image_result = await self._generate_with_dalle(enhanced_prompt, size, style)

                # Add to cache
                self._update_cache(cache_key, image_result)

                return image_result

        except Exception as e:
            logger.error(f"Error generating image: {e!s}")
            return {
                "error": str(e),
                "fallback_image_url": "https://example.com/error-placeholder.png",
            }
        finally:
            self.active_requests.remove(request_id)

    async def _enhance_prompt(self, prompt: str, user_context: Optional[dict], style: str) -> str:
        """Enhance the prompt with style guidance and user context"""
        style_guidance = {
            "minimalist": "clean, simple lines, lots of white space, elegant typography",
            "futuristic": "sleek, advanced technology aesthetic, subtle glow effects",
            "natural": "organic forms, earthy colors, soft lighting",
            "professional": "clean, corporate style, muted colors, structured layout",
            "vibrant": "bold colors, dynamic composition, energetic feel",
        }

        style_prompt = style_guidance.get(style, style_guidance["minimalist"])

        # Integrate user preferences if available
        user_style = ""
        if user_context:
            if "visual_preferences" in user_context:
                user_style = f", {user_context['visual_preferences']}"

            # Include user's aesthetic preferences if available
            if "aesthetic_preference" in user_context:
                user_style += f", {user_context['aesthetic_preference']} aesthetic"

            # Adapt to user's color preferences if available
            if "color_preference" in user_context:
                user_style += f", {user_context['color_preference']} color palette"

        base_prompt = f"{prompt}, {style_prompt}{user_style}, high quality"

        # Use GPT to optimize the prompt if available
        try:
            optimized_prompt = await self.gpt_client.generate_image_prompt(base_prompt)
            return optimized_prompt
        except Exception as e:
            logger.warning(f"Error optimizing prompt with GPT: {e!s}. Using base prompt.")
            return base_prompt

    async def _generate_with_dalle(self, prompt: str, size: str, style: str) -> dict:
        """Generate image using DALL-E"""
        # Map our style to DALL-E's style parameter
        dalle_style = self.style_mapping.get(style, "natural")

        # Call DALL-E API
        dalle_result = await self.dalle_client.generate_image(
            prompt=prompt,
            size=size,
            quality=self.generation_quality,
            style=dalle_style,
            n=1,
        )

        # Check for errors
        if "error" in dalle_result:
            logger.error(f"DALL-E generation error: {dalle_result['error']}")
            return {
                "error": dalle_result["error"],
                "fallback_image_url": "https://example.com/error-placeholder.png",
            }

        # Format the result
        result = {
            "image_url": (dalle_result["urls"][0] if dalle_result["urls"] else None),
            "local_path": (dalle_result["local_paths"][0] if dalle_result["local_paths"] else None),
            "prompt": prompt,
            "style": style,
            "size": size,
            "created_at": dalle_result["timestamp"],
        }

        return result

    def _update_cache(self, key: str, result: dict) -> None:
        """Update the generation cache with LRU policy"""
        if len(self.cached_generations) >= self.max_cache_size:
            # Remove oldest item (simple implementation)
            self.cached_generations.pop(next(iter(self.cached_generations)))

        self.cached_generations[key] = result

    def _generate_request_id(self) -> str:
        """Generate a unique ID for the request"""
        import uuid

        return str(uuid.uuid4())

    async def close(self):
        """Clean up resources"""
        await self.dalle_client.close()
        await self.gpt_client.close()
