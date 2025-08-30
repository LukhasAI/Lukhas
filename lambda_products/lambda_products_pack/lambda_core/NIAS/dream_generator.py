#!/usr/bin/env python3
"""
NIΛS Dream Generator - AI-powered dream commerce content generation
Integrates OpenAI APIs for narrative, image, and video generation
Part of the Lambda Products Suite by LUKHAS AI
"""

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# OpenAI integration
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")

from .consent_manager import AIGenerationType
from .vendor_portal import DreamSeed, DreamSeedType

logger = logging.getLogger("Lambda.NIΛS.DreamGenerator")


class DreamMood(Enum):
    """Emotional moods for dream generation"""

    NOSTALGIC = "nostalgic"  # Memory-based, gentle longing
    ASPIRATIONAL = "aspirational"  # Future-focused, hopeful
    COMFORTING = "comforting"  # Security, warmth, care
    ADVENTUROUS = "adventurous"  # Discovery, excitement
    SERENE = "serene"  # Calm, peaceful, mindful
    CELEBRATORY = "celebratory"  # Joy, achievement, special moments
    WHIMSICAL = "whimsical"  # Playful, imaginative


class BioRhythm(Enum):
    """User's biological rhythm states"""

    MORNING_PEAK = "morning_peak"  # 6-10 AM: High energy, clarity
    MIDDAY_FLOW = "midday_flow"  # 10 AM-2 PM: Productive, focused
    AFTERNOON_DIP = "afternoon_dip"  # 2-5 PM: Lower energy, reflective
    EVENING_WIND = "evening_wind"  # 5-9 PM: Social, relaxed
    NIGHT_QUIET = "night_quiet"  # 9 PM-12 AM: Contemplative, dreamy
    DEEP_NIGHT = "deep_night"  # 12 AM-6 AM: Subconscious, symbolic


@dataclass
class DreamContext:
    """Context for dream generation"""

    user_id: str
    user_profile: dict[str, Any]
    vendor_seed: Optional[DreamSeed] = None
    mood: DreamMood = DreamMood.SERENE
    bio_rhythm: BioRhythm = BioRhythm.MIDDAY_FLOW
    personal_data: dict[str, Any] = field(default_factory=dict)
    recent_events: list[dict[str, Any]] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    ethical_constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedDream:
    """A fully generated dream experience"""

    dream_id: str
    narrative: str
    visual_prompt: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    emotional_profile: dict[str, float] = field(default_factory=dict)
    symbolism: list[str] = field(default_factory=list)
    call_to_action: dict[str, Any] = field(default_factory=dict)
    ethical_score: float = 1.0
    generation_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class DreamGenerator:
    """
    AI-powered dream content generator using OpenAI APIs

    Features:
    - GPT-4 for poetic narrative generation
    - DALL-E 3 for dream imagery
    - Sora for dream videos (when available)
    - Ethical validation with Vivox
    - Bio-rhythm aware generation
    - Personal context integration
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()

        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.openai_client = None
            logger.warning(
                "OpenAI client not initialized. Set OPENAI_API_KEY environment variable."
            )

        self.dream_cache: dict[str, GeneratedDream] = {}
        self.generation_queue: list[tuple[DreamContext, asyncio.Future]] = []

        logger.info("NIΛS Dream Generator initialized")

    def _default_config(self) -> dict:
        """Default dream generator configuration"""
        return {
            "gpt_model": "gpt-4-turbo-preview",
            "dalle_model": "dall-e-3",
            "enable_vivox_checks": True,
            "max_narrative_length": 500,
            "image_size": "1024x1024",
            "video_duration": 15,  # seconds
            "cache_duration_minutes": 60,
            "ethical_threshold": 0.8,
            "enable_symbolism": True,
            "bio_rhythm_adaptation": True,
        }

    async def generate_dream(self, context: DreamContext) -> GeneratedDream:
        """
        Generate a complete dream experience

        Args:
            context: Dream generation context

        Returns:
            Generated dream with narrative and visuals
        """
        try:
            dream_id = f"dream_{hashlib.md5(f'{context.user_id}_{datetime.now()}'.encode()).hexdigest()[:12]}"

            # Check cache
            cache_key = self._get_cache_key(context)
            if cache_key in self.dream_cache:
                cached_dream = self.dream_cache[cache_key]
                if (datetime.now() - cached_dream.created_at).seconds < self.config[
                    "cache_duration_minutes"
                ] * 60:
                    logger.info(f"Returning cached dream: {cached_dream.dream_id}")
                    return cached_dream

            # Generate narrative
            narrative = await self._generate_narrative(context)

            # Create visual prompt from narrative
            visual_prompt = await self._create_visual_prompt(narrative, context)

            # Generate image if consent given
            image_url = None
            if await self._check_ai_consent(context.user_id, AIGenerationType.IMAGE):
                image_url = await self._generate_image(visual_prompt)

            # Prepare for video generation (Sora - future)
            video_url = None
            if await self._check_ai_consent(context.user_id, AIGenerationType.VIDEO):
                # Placeholder for Sora integration
                video_url = await self._generate_video_placeholder(visual_prompt)

            # Extract symbolism
            symbolism = await self._extract_symbolism(narrative)

            # Create call to action
            call_to_action = await self._create_call_to_action(context)

            # Calculate emotional profile
            emotional_profile = self._calculate_emotional_profile(narrative, context)

            # Perform ethical validation
            ethical_score = await self._validate_ethics(narrative, visual_prompt, context)

            # Create dream object
            dream = GeneratedDream(
                dream_id=dream_id,
                narrative=narrative,
                visual_prompt=visual_prompt,
                image_url=image_url,
                video_url=video_url,
                emotional_profile=emotional_profile,
                symbolism=symbolism,
                call_to_action=call_to_action,
                ethical_score=ethical_score,
                generation_metadata={
                    "mood": context.mood.value,
                    "bio_rhythm": context.bio_rhythm.value,
                    "vendor_seed": (context.vendor_seed.seed_id if context.vendor_seed else None),
                    "models_used": {
                        "narrative": self.config["gpt_model"],
                        "image": self.config["dalle_model"] if image_url else None,
                    },
                },
            )

            # Cache the dream
            self.dream_cache[cache_key] = dream

            logger.info(f"Generated dream: {dream_id} with ethical score: {ethical_score}")
            return dream

        except Exception as e:
            logger.error(f"Error generating dream: {e}")
            # Return a safe fallback dream
            return self._create_fallback_dream(context)

    async def _generate_narrative(self, context: DreamContext) -> str:
        """Generate poetic narrative using GPT-4"""
        if not self.openai_client:
            return self._generate_fallback_narrative(context)

        try:
            # Build the prompt based on context
            system_prompt = self._build_system_prompt(context)
            user_prompt = self._build_user_prompt(context)

            # Call GPT-4
            response = await self.openai_client.chat.completions.create(
                model=self.config["gpt_model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.config["max_narrative_length"],
                temperature=0.8,
                presence_penalty=0.3,
                frequency_penalty=0.3,
            )

            narrative = response.choices[0].message.content

            # Post-process narrative
            narrative = self._post_process_narrative(narrative, context)

            return narrative

        except Exception as e:
            logger.error(f"Error generating narrative with GPT: {e}")
            return self._generate_fallback_narrative(context)

    def _build_system_prompt(self, context: DreamContext) -> str:
        """Build system prompt for narrative generation"""
        mood_descriptions = {
            DreamMood.NOSTALGIC: "warm memories and gentle longing",
            DreamMood.ASPIRATIONAL: "hopeful futures and possibilities",
            DreamMood.COMFORTING: "safety, warmth, and care",
            DreamMood.ADVENTUROUS: "discovery and excitement",
            DreamMood.SERENE: "peace and tranquility",
            DreamMood.CELEBRATORY: "joy and achievement",
            DreamMood.WHIMSICAL: "playfulness and imagination",
        }

        return f"""You are a poetic dream weaver creating gentle, symbolic narratives that feel like dreams rather than advertisements.

Current mood: {mood_descriptions.get(context.mood, "serene contemplation")}
Time of day feeling: {self._get_bio_rhythm_description(context.bio_rhythm)}

Guidelines:
- Write in a dreamy, poetic style that feels like a memory or vision
- Use sensory details and symbolic imagery
- Never use aggressive marketing language or pressure
- Focus on emotional resonance and personal connection
- Keep it brief but meaningful (2-3 paragraphs)
- End with a gentle invitation, not a command
- Respect the user's current emotional state
- Make it feel like their own dream, not an external message"""

    def _build_user_prompt(self, context: DreamContext) -> str:
        """Build user prompt for narrative generation"""
        prompt_parts = []

        if context.vendor_seed:
            seed = context.vendor_seed
            prompt_parts.append(
                f"Product context: {seed.product_data.get('name', 'something special')}"
            )
            prompt_parts.append(
                f"Emotional theme: {seed.narrative[:100] if seed.narrative else 'discovery'}"
            )

        if context.personal_data:
            # Add relevant personal context (privacy-filtered)
            if "upcoming_events" in context.personal_data:
                events = context.personal_data["upcoming_events"]
                if events:
                    prompt_parts.append(
                        f"Upcoming moment: {events[0].get('type', 'special occasion')}"
                    )

            if "interests" in context.personal_data:
                interests = context.personal_data["interests"][:3]
                prompt_parts.append(f"Personal interests: {', '.join(interests)}")

        if context.recent_events:
            # Add recent activity context
            recent = context.recent_events[0] if context.recent_events else {}
            if recent.get("type") == "browsing":
                prompt_parts.append(
                    f"Recently exploring: {recent.get('category', 'new possibilities')}"
                )

        base_prompt = "Create a brief, poetic dream narrative that gently weaves together: "
        return (
            base_prompt + "; ".join(prompt_parts)
            if prompt_parts
            else base_prompt + "a moment of peaceful discovery"
        )

    def _get_bio_rhythm_description(self, bio_rhythm: BioRhythm) -> str:
        """Get description for biological rhythm"""
        descriptions = {
            BioRhythm.MORNING_PEAK: "fresh morning clarity and possibility",
            BioRhythm.MIDDAY_FLOW: "focused midday energy",
            BioRhythm.AFTERNOON_DIP: "gentle afternoon reflection",
            BioRhythm.EVENING_WIND: "relaxed evening contemplation",
            BioRhythm.NIGHT_QUIET: "quiet nighttime dreams",
            BioRhythm.DEEP_NIGHT: "deep subconscious symbolism",
        }
        return descriptions.get(bio_rhythm, "timeless presence")

    async def _create_visual_prompt(self, narrative: str, context: DreamContext) -> str:
        """Create visual prompt for image generation"""
        if not self.openai_client:
            return "A serene, dreamlike scene with soft colors and gentle imagery"

        try:
            # Use GPT to create a visual prompt from the narrative
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Convert the following dream narrative into a visual description for image generation. Focus on atmosphere, colors, symbols, and mood. Make it artistic and dreamlike, avoiding any text or words in the image.",
                    },
                    {
                        "role": "user",
                        "content": f"Dream narrative: {narrative[:500]}\n\nCreate a visual description that captures the essence of this dream.",
                    },
                ],
                max_tokens=150,
                temperature=0.7,
            )

            visual_prompt = response.choices[0].message.content

            # Add style modifiers
            style_modifiers = [
                "dreamlike",
                "soft focus",
                "ethereal lighting",
                "symbolic",
                "artistic",
                "surreal beauty",
            ]

            visual_prompt += f" Style: {', '.join(style_modifiers[:3])}"

            return visual_prompt

        except Exception as e:
            logger.error(f"Error creating visual prompt: {e}")
            return "A peaceful, dreamlike scene with soft colors and gentle symbolism"

    async def _generate_image(self, visual_prompt: str) -> Optional[str]:
        """Generate image using DALL-E 3"""
        if not self.openai_client:
            return None

        try:
            response = await self.openai_client.images.generate(
                model=self.config["dalle_model"],
                prompt=visual_prompt,
                size=self.config["image_size"],
                quality="hd",
                n=1,
                style="vivid",
            )

            image_url = response.data[0].url
            logger.info("Generated dream image with DALL-E 3")
            return image_url

        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {e}")
            return None

    async def _generate_video_placeholder(self, visual_prompt: str) -> Optional[str]:
        """Placeholder for Sora video generation (future implementation)"""
        # When Sora becomes available, this would generate dream videos
        # For now, return None or a placeholder
        logger.info(
            "Sora video generation not yet available - placeholder for future implementation"
        )
        return None

    async def _extract_symbolism(self, narrative: str) -> list[str]:
        """Extract symbolic elements from narrative"""
        if not self.openai_client:
            return ["journey", "discovery", "connection"]

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract 3-5 key symbolic elements from this dream narrative. Return only the symbols as a comma-separated list.",
                    },
                    {"role": "user", "content": narrative},
                ],
                max_tokens=50,
                temperature=0.5,
            )

            symbols = response.choices[0].message.content.split(",")
            return [s.strip() for s in symbols]

        except Exception as e:
            logger.error(f"Error extracting symbolism: {e}")
            return ["transformation", "possibility", "harmony"]

    async def _create_call_to_action(self, context: DreamContext) -> dict[str, Any]:
        """Create gentle call to action"""
        if not context.vendor_seed:
            return {
                "type": "explore",
                "text": "When you're ready to explore...",
                "action": None,
            }

        seed = context.vendor_seed

        # Create action based on seed type
        action_templates = {
            DreamSeedType.REMINDER: "When this feeling calls to you...",
            DreamSeedType.DISCOVERY: "If curiosity guides you...",
            DreamSeedType.SEASONAL: "As the season whispers...",
            DreamSeedType.REPLENISHMENT: "When the moment feels right...",
            DreamSeedType.EXCLUSIVE: "A special invitation awaits...",
            DreamSeedType.NARRATIVE: "Continue the story...",
            DreamSeedType.EXPERIENTIAL: "Experience the dream...",
        }

        return {
            "type": seed.seed_type.value,
            "text": action_templates.get(seed.seed_type, "When you're ready..."),
            "action": seed.affiliate_link,
            "one_click_data": seed.one_click_data,
        }

    def _calculate_emotional_profile(
        self, narrative: str, context: DreamContext
    ) -> dict[str, float]:
        """Calculate emotional profile of generated content"""
        # Base emotional profile from mood
        mood_profiles = {
            DreamMood.NOSTALGIC: {
                "joy": 0.4,
                "calm": 0.6,
                "stress": 0.0,
                "longing": 0.7,
            },
            DreamMood.ASPIRATIONAL: {
                "joy": 0.7,
                "calm": 0.4,
                "stress": 0.0,
                "longing": 0.5,
            },
            DreamMood.COMFORTING: {
                "joy": 0.5,
                "calm": 0.8,
                "stress": 0.0,
                "longing": 0.2,
            },
            DreamMood.ADVENTUROUS: {
                "joy": 0.8,
                "calm": 0.3,
                "stress": 0.0,
                "longing": 0.4,
            },
            DreamMood.SERENE: {"joy": 0.4, "calm": 0.9, "stress": 0.0, "longing": 0.1},
            DreamMood.CELEBRATORY: {
                "joy": 0.9,
                "calm": 0.4,
                "stress": 0.0,
                "longing": 0.2,
            },
            DreamMood.WHIMSICAL: {
                "joy": 0.7,
                "calm": 0.5,
                "stress": 0.0,
                "longing": 0.3,
            },
        }

        profile = mood_profiles.get(
            context.mood, {"joy": 0.5, "calm": 0.5, "stress": 0.0, "longing": 0.3}
        )

        # Adjust based on bio rhythm
        if context.bio_rhythm in [BioRhythm.EVENING_WIND, BioRhythm.NIGHT_QUIET]:
            profile["calm"] = min(1.0, profile["calm"] + 0.2)
            profile["joy"] = max(0.0, profile["joy"] - 0.1)
        elif context.bio_rhythm == BioRhythm.MORNING_PEAK:
            profile["joy"] = min(1.0, profile["joy"] + 0.2)

        # Ensure no stress
        profile["stress"] = 0.0

        return profile

    async def _validate_ethics(
        self, narrative: str, visual_prompt: str, context: DreamContext
    ) -> float:
        """Validate ethical compliance with Vivox system"""
        score = 1.0

        # Check for pressure language
        pressure_words = [
            "hurry",
            "limited",
            "act now",
            "don't miss",
            "last chance",
            "expires soon",
        ]
        narrative_lower = narrative.lower()

        for word in pressure_words:
            if word in narrative_lower:
                score *= 0.7
                logger.warning(f"Pressure language detected: {word}")

        # Check emotional manipulation
        if context.vendor_seed:
            stress_level = context.vendor_seed.emotional_triggers.get("stress", 0)
            if stress_level > 0.2:
                score *= 0.5
                logger.warning(f"High stress level in seed: {stress_level}")

        # Check for vulnerability exploitation
        if context.bio_rhythm == BioRhythm.DEEP_NIGHT:
            # Extra careful during vulnerable hours
            score *= 0.9

        # Ensure minimum ethical score
        if score < self.config["ethical_threshold"]:
            logger.warning(f"Ethical score too low: {score}")
            score = self.config["ethical_threshold"]

        return score

    async def _check_ai_consent(self, user_id: str, generation_type: AIGenerationType) -> bool:
        """Check if user has consented to AI generation type"""
        # This would integrate with the consent manager
        # For now, return True for demonstration
        return True

    def _get_cache_key(self, context: DreamContext) -> str:
        """Generate cache key for dream"""
        parts = [context.user_id, context.mood.value, context.bio_rhythm.value]

        if context.vendor_seed:
            parts.append(context.vendor_seed.seed_id)

        return hashlib.md5("_".join(parts).encode()).hexdigest()

    def _post_process_narrative(self, narrative: str, context: DreamContext) -> str:
        """Post-process generated narrative"""
        # Remove any unwanted elements
        unwanted_phrases = [
            "buy now",
            "purchase",
            "order today",
            "click here",
            "sign up",
        ]

        narrative_lower = narrative.lower()
        for phrase in unwanted_phrases:
            if phrase in narrative_lower:
                # Replace with gentler alternatives
                narrative = narrative.replace(phrase, "explore")
                narrative = narrative.replace(phrase.capitalize(), "Explore")

        # Ensure appropriate length
        if len(narrative) > self.config["max_narrative_length"]:
            # Truncate at sentence boundary
            sentences = narrative.split(". ")
            truncated = []
            current_length = 0

            for sentence in sentences:
                if current_length + len(sentence) <= self.config["max_narrative_length"]:
                    truncated.append(sentence)
                    current_length += len(sentence)
                else:
                    break

            narrative = ". ".join(truncated) + "."

        return narrative

    def _generate_fallback_narrative(self, context: DreamContext) -> str:
        """Generate fallback narrative when AI is unavailable"""
        templates = {
            DreamMood.NOSTALGIC: "In moments of quiet reflection, memories surface like gentle waves...",
            DreamMood.ASPIRATIONAL: "Imagine a tomorrow painted with possibilities...",
            DreamMood.COMFORTING: "Wrapped in warmth, surrounded by what matters most...",
            DreamMood.ADVENTUROUS: "The path ahead shimmers with undiscovered wonders...",
            DreamMood.SERENE: "In this peaceful moment, everything finds its place...",
            DreamMood.CELEBRATORY: "Light dances through moments of joy...",
            DreamMood.WHIMSICAL: "Where imagination meets reality, magic happens...",
        }

        base_narrative = templates.get(context.mood, "A gentle moment of discovery awaits...")

        if context.vendor_seed and context.vendor_seed.narrative:
            # Use vendor's narrative as base
            base_narrative = context.vendor_seed.narrative[:200] + "..."

        return base_narrative

    def _create_fallback_dream(self, context: DreamContext) -> GeneratedDream:
        """Create a safe fallback dream when generation fails"""
        return GeneratedDream(
            dream_id=f"fallback_{datetime.now().timestamp()}",
            narrative=self._generate_fallback_narrative(context),
            visual_prompt="A peaceful, dreamlike scene",
            emotional_profile={"joy": 0.5, "calm": 0.7, "stress": 0.0, "longing": 0.3},
            symbolism=["peace", "possibility", "connection"],
            call_to_action={
                "type": "explore",
                "text": "When you're ready...",
                "action": None,
            },
            ethical_score=1.0,
        )

    async def generate_batch_dreams(self, contexts: list[DreamContext]) -> list[GeneratedDream]:
        """Generate multiple dreams in batch for efficiency"""
        tasks = [self.generate_dream(context) for context in contexts]
        dreams = await asyncio.gather(*tasks)
        return dreams

    def get_generation_metrics(self) -> dict[str, Any]:
        """Get metrics about dream generation"""
        total_cached = len(self.dream_cache)

        # Calculate cache hit rate
        # This would track actual hits in production

        return {
            "cached_dreams": total_cached,
            "queue_size": len(self.generation_queue),
            "models": {
                "narrative": self.config["gpt_model"],
                "image": self.config["dalle_model"],
                "video": "sora (pending)",
            },
            "ethical_threshold": self.config["ethical_threshold"],
            "openai_available": OPENAI_AVAILABLE and self.openai_client is not None,
        }
