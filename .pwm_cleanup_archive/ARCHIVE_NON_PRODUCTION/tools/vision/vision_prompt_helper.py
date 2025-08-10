#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Vision Prompt Helper

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

This module provides helper functions for vision prompt management and memory
visualization.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Configure module logger
logger = logging.getLogger("ΛTRACE.core.vision_prompt_helper")

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "vision_prompt_helper"


class VisionPromptHelper:
    """Manages vision prompts for memory visualization."""

    def __init__(self, prompts_path: Optional[str] = None):
        """
        Initialize the vision prompt helper.

        Args:
            prompts_path: Path to vision prompts JSON file
        """
        self.prompts_path = prompts_path or "core/vision/lukhas_vision_prompts.json"
        self.prompts_cache = None
        self._load_prompts()

    def _load_prompts(self):
        """Load vision prompts from file."""
        try:
            path = Path(self.prompts_path)
            if path.exists():
                with open(path) as f:
                    self.prompts_cache = json.load(f)
                logger.info(f"Loaded vision prompts from {path}")
            else:
                logger.warning(f"Vision prompts file not found at {path}")
                self.prompts_cache = self._get_default_prompts()
        except Exception as e:
            logger.error(f"Failed to load vision prompts: {e}")
            self.prompts_cache = self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, str]:
        """Returns default vision prompts."""
        return {
            "emotion_joy": "🌟 Bright, warm colors with dancing light particles",
            "emotion_sadness": "🌧️ Soft blues and grays with gentle rain",
            "emotion_fear": "🌑 Dark shadows with sharp contrasts",
            "emotion_anger": "🔥 Intense reds and oranges with dynamic movement",
            "emotion_trust": "🤝 Calm greens and blues with stable patterns",
            "emotion_surprise": "✨ Burst of colors with expanding patterns",
            "emotion_neutral": "☁️ Balanced grays with steady flow",
            "emotion_peaceful": "🌊 Gentle waves in soft pastels",
            "default": "🖼️ Abstract patterns reflecting the emotional state",
        }

    def get_vision_prompt(
        self,
        emotion: str,
        fold_timestamp: Optional[datetime] = None,
        user_tier: int = 0,
    ) -> Dict[str, Any]:
        """
        Get vision prompt for a given emotion and context.

        Args:
            emotion: The emotion to get prompt for
            fold_timestamp: Timestamp of the memory fold
            user_tier: User's access tier

        Returns:
            Dictionary with vision prompt and metadata
        """
        if not self.prompts_cache:
            self._load_prompts()

        # Determine time period and season
        time_period = "day"
        season = "neutral"

        if fold_timestamp:
            hour = fold_timestamp.hour
            if 5 <= hour < 12:
                time_period = "morning"
            elif 12 <= hour < 18:
                time_period = "afternoon"
            elif 18 <= hour < 22:
                time_period = "evening"
            else:
                time_period = "night"

            month = fold_timestamp.month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "autumn"

        # Build prompt keys
        specific_key = f"{emotion}_{time_period}_{season}"
        general_key = f"emotion_{emotion}"

        # Get prompt with fallbacks
        prompt_text = self.prompts_cache.get(
            specific_key,
            self.prompts_cache.get(
                general_key,
                self.prompts_cache.get("default", "🖼️ Visual memory representation"),
            ),
        )

        # Build metadata based on tier
        metadata = {"style": "dreamlike_watercolor", "ambient_ready": user_tier >= 3}

        if user_tier >= 4:
            metadata.update(
                {"emotion_blend": True, "transition_style": "emotional_morph"}
            )

        if user_tier >= 5:
            metadata.update(
                {
                    "advanced_synthesis": True,
                    "memory_projection": True,
                    "time_context": {"period": time_period, "season": season},
                }
            )

        return {
            "prompt": prompt_text,
            "metadata": metadata,
            "emotion": emotion,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def add_custom_prompt(self, key: str, prompt: str) -> bool:
        """
        Add a custom vision prompt.

        Args:
            key: The key for the prompt
            prompt: The prompt text

        Returns:
            True if successful
        """
        try:
            if not self.prompts_cache:
                self.prompts_cache = {}

            self.prompts_cache[key] = prompt

            # Save to file
            path = Path(self.prompts_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w") as f:
                json.dump(self.prompts_cache, f, indent=2)

            logger.info(f"Added custom prompt: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to add custom prompt: {e}")
            return False


"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
