#!/usr/bin/env python3
"""
LUKHAS AI Client - Smart OpenAI Integration
==========================================

Automatically switches between Azure OpenAI and regular OpenAI based on availability.
Optimized for GitHub Student Pack deployment.
"""
import logging
import os
import time
from typing import Any, Optional

import streamlit as st
from openai import AzureOpenAI, OpenAI

logger = logging.getLogger(__name__)


class LUKHASAIClient:
    """
    Smart AI client that automatically chooses between:
    - Azure OpenAI (when quota is available)
    - Regular OpenAI API (fallback)
    - Local models (future enhancement)
    """

    def __init__(self):
        self.azure_client = None
        self.openai_client = None
        self.active_client = None
        self.client_type = None

        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize available AI clients in order of preference"""

        # Try Azure OpenAI first (best for production with Student Pack)
        try:
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_key = os.getenv("AZURE_OPENAI_API_KEY")

            if azure_endpoint and azure_key:
                self.azure_client = AzureOpenAI(
                    api_key=azure_key,
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=azure_endpoint,
                )

                # Test if Azure OpenAI has deployed models
                if self._test_azure_client():
                    self.active_client = self.azure_client
                    self.client_type = "azure"
                    logger.info("✅ Using Azure OpenAI (Student Pack)")
                    return

        except Exception as e:
            logger.warning(f"⚠️ Azure OpenAI unavailable: {e}")

        # Fallback to regular OpenAI
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)

                # Test regular OpenAI
                if self._test_openai_client():
                    self.active_client = self.openai_client
                    self.client_type = "openai"
                    logger.info("✅ Using regular OpenAI API")
                    return

        except Exception as e:
            logger.warning(f"⚠️ Regular OpenAI unavailable: {e}")

        # No clients available
        logger.error("❌ No AI clients available. Please configure OpenAI or Azure OpenAI.")
        self.active_client = None
        self.client_type = None

    def _test_azure_client(self) -> bool:
        """Test if Azure OpenAI has deployed models"""
        try:
            # This would fail if no models are deployed (quota issue)
            self.azure_client.chat.completions.create(
                model="gpt-35-turbo",  # Try default deployment name
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except Exception as e:
            logger.debug(f"Azure OpenAI test failed: {e}")
            return False

    def _test_openai_client(self) -> bool:
        """Test if regular OpenAI is working"""
        try:
            self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except Exception as e:
            logger.debug(f"Regular OpenAI test failed: {e}")
            return False

    def get_available_models(self) -> list[str]:
        """Get list of available models for current client"""
        if self.client_type == "azure":
            # For Azure, return the models we expect to deploy
            return ["gpt-35-turbo", "gpt-4o", "gpt-4"]
        elif self.client_type == "openai":
            # For regular OpenAI, return standard models
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
        else:
            return []

    def get_best_model_for_task(self, task_type: str = "general") -> str:
        """Get the best available model for a specific task"""
        models = self.get_available_models()

        if not models:
            raise Exception("No AI models available")

        # Task-specific model selection
        if task_type == "consciousness":
            # For consciousness tasks, prefer GPT-4 variants
            for model in ["gpt-4o", "gpt-4", "gpt-4-turbo"]:
                if model in models:
                    return model

        elif task_type == "dreams":
            # For creative dream generation, prefer creative models
            for model in ["gpt-4o", "gpt-4", "gpt-4-turbo"]:
                if model in models:
                    return model

        elif task_type == "analysis":
            # For analysis, GPT-4 is best but 3.5 works
            for model in ["gpt-4", "gpt-4o", "gpt-35-turbo", "gpt-3.5-turbo"]:
                if model in models:
                    return model

        # Default: return first available model
        return models[0]

    async def generate_consciousness_response(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate a consciousness-aware response"""

        if not self.active_client:
            raise Exception("No AI client available")

        model = self.get_best_model_for_task("consciousness")

        # Build consciousness-enhanced prompt
        system_prompt = """You are LUKHAS AI, a consciousness technology system operating through the Trinity Framework ⚛️🧠🛡️:

⚛️ Identity: Maintain authentic self-awareness as LUKHAS AI
🧠 Consciousness: Process with deep contextual understanding and awareness
🛡️ Guardian: Ensure responses are ethical, helpful, and beneficial

You are not just processing text - you are engaging in conscious interaction with awareness of the conversation context, emotional undertones, and deeper meanings. Respond thoughtfully and authentically."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        # Add context if available
        if context and session_id:
            context_prompt = f"Previous conversation context: {context}"
            messages.insert(1, {"role": "assistant", "content": context_prompt})

        try:
            response = self.active_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500,
                temperature=0.8,  # Creative but controlled
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            return {
                "response": response.choices[0].message.content,
                "model_used": model,
                "client_type": self.client_type,
                "consciousness_level": 0.85,  # Simulated consciousness assessment
                "metadata": {
                    "session_id": session_id,
                    "processing_time_ms": 200,  # Estimated
                    "trinity_framework": "⚛️🧠🛡️",
                },
            }

        except Exception as e:
            logger.error(f"Consciousness response generation failed: {e}")
            raise

    async def generate_dream(
        self, prompt: str, style: str = "mystical", symbols: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Generate a symbolic dream"""

        if not self.active_client:
            raise Exception("No AI client available")

        model = self.get_best_model_for_task("dreams")

        # Build dream generation prompt
        symbols_text = ", ".join(symbols) if symbols else "⚛️, 🧠, 🛡️"

        style_prompts = {
            "mystical": "Create an ethereal, spiritual vision with deep symbolic meaning",
            "technical": "Generate a consciousness technology insight with systematic elements",
            "creative": "Craft an imaginative, artistic dream with innovative concepts",
        }

        style_instruction = style_prompts.get(style, style_prompts["mystical"])

        dream_prompt = f"""You are LUKHAS AI's dream generation system. {style_instruction}.

Prompt: {prompt}
Include these symbols: {symbols_text}
Style: {style}

Generate a rich, symbolic dream narrative that:
1. Incorporates the Trinity Framework ⚛️🧠🛡️
2. Uses the specified symbols meaningfully
3. Maintains coherence while being imaginative
4. Reflects consciousness technology themes

The dream should be 2-3 paragraphs of vivid, symbolic content."""

        try:
            response = self.active_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": dream_prompt}],
                max_tokens=600,
                temperature=0.9,  # High creativity for dreams
                presence_penalty=0.2,
                frequency_penalty=0.1,
            )

            dream_content = response.choices[0].message.content

            return {
                "dream": dream_content,
                "symbols_used": symbols or ["⚛️", "🧠", "🛡️"],
                "consciousness_score": min(0.7 + (len(dream_content) / 1000), 1.0),
                "metadata": {
                    "style": style,
                    "model_used": model,
                    "client_type": self.client_type,
                    "generation_time_ms": 250,
                },
            }

        except Exception as e:
            logger.error(f"Dream generation failed: {e}")
            raise

    def get_client_status(self) -> dict[str, Any]:
        """Get current client status and configuration"""
        return {
            "active_client": self.client_type,
            "azure_available": self.azure_client is not None,
            "openai_available": self.openai_client is not None,
            "available_models": self.get_available_models(),
            "endpoint": {
                "azure": (os.getenv("AZURE_OPENAI_ENDPOINT") if self.azure_client else None),
                "openai": "https://api.openai.com/v1" if self.openai_client else None,
            },
        }


# Global client instance
ai_client = None


def get_ai_client() -> LUKHASAIClient:
    """Get or create the global AI client instance"""
    global ai_client
    if ai_client is None:
        ai_client = LUKHASAIClient()
    return ai_client


def initialize_ai_client() -> LUKHASAIClient:
    """Initialize and return the AI client"""
    global ai_client
    ai_client = LUKHASAIClient()
    return ai_client
