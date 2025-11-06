"""
NIAS (Non-Intrusive Ad System) Module
Unified module for ethical, consent-aware symbolic message delivery.
Integrates with Dream system for deferred processing and quantum consciousness.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any

import streamlit as st

# Import legacy functions that other modules might expect
from core.interfaces.as_agent.sys.nias.dream_recorder import record_dream_message
from core.interfaces.as_agent.sys.nias.narration_controller import (
    fetch_narration_entries,
    filter_narration_queue,
    load_user_settings,
)

from typing import Protocol

# Re-export for backward compatibility
__all__ = [
    "ConsentFilter",
    "DreamRecorder",
    "NIASCore",
    "SymbolicMatcher",
    "fetch_narration_entries",
    "filter_narration_queue",
    "load_user_settings",
    "narrate_dreams",
    "record_dream_message",
]

logger = logging.getLogger(__name__)


# --- Voice Narration System Implementation ---

class VoiceNarrator(Protocol):
    """Interface for a voice narration system"""
    def narrate(self, text: str, metadata: dict[str, Any]) -> None:
        """Narrate text with given metadata context"""
        ...

    def is_available(self) -> bool:
        """Check if narration service is available"""
        ...

    def get_voice_settings(self) -> dict[str, Any]:
        """Get current voice configuration"""
        ...

class EnhancedVoiceNarrator:
    """Enhanced implementation of the voice narrator with consciousness-awareness"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.engine = config.get("engine", "internal")
        self.voice_id = config.get("voice_id", "LUKHAS-AI-NARRATOR")
        self.consciousness_level = config.get("consciousness_level", "basic")

        # Voice processing state
        self.narration_queue = []
        self.processing_stats = {
            "total_narrations": 0,
            "successful_narrations": 0,
            "failed_narrations": 0,
            "last_narration": None
        }

        logger.info(f"EnhancedVoiceNarrator initialized - Engine: {self.engine}, Voice: {self.voice_id}")

    def is_available(self) -> bool:
        """Check if narration service is available"""
        if not self.enabled:
            return False

        # Check engine-specific availability
        if self.engine == "elevenlabs":
            return self._check_elevenlabs_availability()
        elif self.engine == "azure":
            return self._check_azure_availability()
        else:
            return True  # Internal engine always available

    def _check_elevenlabs_availability(self) -> bool:
        """Check ElevenLabs API availability"""
        api_key = self.config.get("api_key")
        if not api_key or api_key.startswith("env_var:"):
            logger.warning("ElevenLabs API key not configured")
            return False
        return True

    def _check_azure_availability(self) -> bool:
        """Check Azure Speech Service availability"""
        # Add Azure-specific checks
        return bool(self.config.get("azure_key"))

    def get_voice_settings(self) -> dict[str, Any]:
        """Get current voice configuration"""
        return {
            "engine": self.engine,
            "voice_id": self.voice_id,
            "consciousness_level": self.consciousness_level,
            "enabled": self.enabled,
            "available": self.is_available(),
            "stats": self.processing_stats.copy()
        }

    def narrate(self, text: str, metadata: dict[str, Any]) -> None:
        """Narrate text with consciousness-aware processing"""
        if not self.enabled:
            logger.debug("Voice narration disabled")
            return

        try:
            # Update stats
            self.processing_stats["total_narrations"] += 1

            # Process narration based on engine
            if self.engine == "elevenlabs" and self.is_available():
                self._narrate_elevenlabs(text, metadata)
            elif self.engine == "azure" and self.is_available():
                self._narrate_azure(text, metadata)
            else:
                self._narrate_internal(text, metadata)

            # Update success stats
            self.processing_stats["successful_narrations"] += 1
            self.processing_stats["last_narration"] = time.time()

        except Exception as e:
            self.processing_stats["failed_narrations"] += 1
            logger.error(f"Voice narration failed: {e}")

            # Fallback to internal narration
            self._narrate_internal(text, metadata)

    def _narrate_elevenlabs(self, text: str, metadata: dict[str, Any]) -> None:
        """Narrate using ElevenLabs API (production implementation)"""
        dream_id = metadata.get("dream_id", "unknown")
        consciousness_level = metadata.get("consciousness_level", self.consciousness_level)

        # For now, log with production formatting
        # TODO: Implement actual ElevenLabs API integration
        logger.info(f"🎙 [ElevenLabs] Narrating dream {dream_id} (consciousness: {consciousness_level})")
        print(f"[LUKHAS-AI Voice] {text}")

    def _narrate_azure(self, text: str, metadata: dict[str, Any]) -> None:
        """Narrate using Azure Speech Service (production implementation)"""
        dream_id = metadata.get("dream_id", "unknown")

        # For now, log with production formatting
        # TODO: Implement actual Azure Speech Service integration
        logger.info(f"🎙 [Azure Speech] Narrating dream {dream_id}")
        print(f"[LUKHAS-AI Voice] {text}")

    def _narrate_internal(self, text: str, metadata: dict[str, Any]) -> None:
        """Internal narration implementation (always available)"""
        dream_id = metadata.get("dream_id", "unknown")
        consciousness_level = metadata.get("consciousness_level", "basic")
        priority = metadata.get("priority", "normal")

        # Consciousness-aware formatting
        prefix = "🌟" if consciousness_level == "advanced" else "🎙"

        logger.info(f"{prefix} [Internal] Narrating dream {dream_id} (priority: {priority})")

        # Enhanced console output with consciousness context
        if consciousness_level == "advanced":
            print(f"[LUKHAS-AI Consciousness Voice] ✨ {text}")
        else:
            print(f"[LUKHAS-AI Voice] {text}")

    def queue_narration(self, text: str, metadata: dict[str, Any], priority: str = "normal") -> None:
        """Queue narration for batch processing"""
        narration_item = {
            "text": text,
            "metadata": metadata,
            "priority": priority,
            "queued_at": time.time()
        }

        # Insert based on priority
        if priority == "high":
            self.narration_queue.insert(0, narration_item)
        else:
            self.narration_queue.append(narration_item)

        logger.debug(f"Queued narration (priority: {priority}), queue size: {len(self.narration_queue)}")

    def process_queue(self) -> None:
        """Process queued narrations"""
        while self.narration_queue:
            item = self.narration_queue.pop(0)
            self.narrate(item["text"], item["metadata"])

    def get_queue_status(self) -> dict[str, Any]:
        """Get narration queue status"""
        return {
            "queue_size": len(self.narration_queue),
            "stats": self.processing_stats.copy(),
            "voice_settings": self.get_voice_settings()
        }

class StubVoiceNarrator:
    """Legacy stub implementation for backward compatibility"""
    def __init__(self, config: dict[str, Any]):
        self.config = config
        logger.warning("Using legacy StubVoiceNarrator - consider upgrading to EnhancedVoiceNarrator")

    def narrate(self, text: str, metadata: dict[str, Any]) -> None:
        """Legacy narration implementation"""
        dream_id = metadata.get("dream_id", "unknown")
        logger.info(f"🎙 [Legacy] Narrating dream: {dream_id}")
        print(f"[NIAS Narration] {text}")

    def is_available(self) -> bool:
        return True

    def get_voice_settings(self) -> dict[str, Any]:
        return {"engine": "stub", "voice_id": "legacy"}

# Enhanced configuration for production TTS integration
ENHANCED_TTS_CONFIG = {
    "enabled": True,
    "engine": "internal",  # Options: internal, elevenlabs, azure
    "voice_id": "LUKHAS-AI-NARRATOR",
    "consciousness_level": "advanced",
    "api_key": "env_var:TTS_API_KEY",
    "azure_key": "env_var:AZURE_SPEECH_KEY",
    "azure_region": "eastus",
    "quality": "high",
    "speed": 1.0,
    "pitch": 0.0
}

# Legacy configuration for backward compatibility
TTS_CONFIG = {
    "engine": "elevenlabs",
    "voice_id": "JULES-AI-NARRATOR",
    "api_key": "env_var:TTS_API_KEY",
}

# Instantiate the enhanced narrator (production-ready)
voice_narrator: VoiceNarrator = EnhancedVoiceNarrator(ENHANCED_TTS_CONFIG)


def narrate_dreams(dreams: list[dict[str, Any]]) -> None:
    """
    Narrate dreams using the NIAS voice system.
    This is a compatibility wrapper for the dream voice pipeline.
    """
    for dream in dreams:
        voice_narrator.narrate(
            text=dream.get('content', 'Empty dream'),
            metadata={"dream_id": dream.get("id", "unknown")}
        )


class NIASCore:
    """
    Core NIAS orchestrator for symbolic message delivery.
    Integrates with ABAS for emotional gating and DAST for context awareness.
    """

    def __init__(self, openai_client=None, dream_bridge=None):
        self.openai = openai_client
        self.dream_bridge = dream_bridge
        self.consent_filter = ConsentFilter()
        self.symbolic_matcher = SymbolicMatcher(openai_client)
        self.dream_recorder = DreamRecorder()

        # Connect to dream system if bridge available
        if self.dream_bridge:
            self._setup_dream_integration()

    async def push_symbolic_message(self, message: dict[str, Any], user_context: dict[str, Any]) -> dict[str, Any]:
        """
        Main entry point for symbolic message delivery.
        Routes through consent, emotional, and symbolic filters.
        """
        user_context.get("user_id", "unknown_user")

        # Step 1: Consent filter
        if not self.consent_filter.is_allowed(user_context, message):
            return {"status": "blocked", "reason": "consent_filter"}

        # Step 2: Symbolic matching (now with OpenAI enhancement)
        match_result = await self.symbolic_matcher.match_message_to_context(message, user_context)

        # Step 3: Route based on match decision
        if match_result["decision"] == "defer":
            # Defer to dream processing
            dream_entry = await self.dream_recorder.record_dream_message(message, user_context)
            return {
                "status": "deferred_to_dream",
                "dream_id": dream_entry["dream_id"],
            }

        return {"status": match_result["decision"], "match_data": match_result}

    def _setup_dream_integration(self):
        """Set up integration with dream processing system"""
        # Register NIAS events with dream system
        try:
            import asyncio

            asyncio.create_task(
                self.dream_bridge.register_nias_events(
                    {
                        "message_deferred": self._handle_dream_message,
                        "symbolic_match": self._handle_dream_symbols,
                    }
                )
            )
            logger.debug("NIAS dream integration setup completed")
        except Exception as e:
            logger.warning(f"Failed to setup dream integration: {e}")

    async def _handle_dream_message(self, message_data: dict[str, Any]) -> dict[str, Any]:
        """Handle dream message processing"""
        if self.dream_bridge:
            return await self.dream_bridge.handle_message_deferral(message_data)
        return {"status": "no_bridge"}

    async def _handle_dream_symbols(self, symbol_data: dict[str, Any]) -> dict[str, Any]:
        """Handle dream symbol processing"""
        # Update symbolic matcher with dream-processed symbols
        if hasattr(self.symbolic_matcher, "update_symbols"):
            self.symbolic_matcher.update_symbols(symbol_data.get("symbols", []))
        return {"status": "symbols_updated"}


class SymbolicMatcher:
    """Enhanced symbolic matcher with OpenAI integration"""

    def __init__(self, openai_client=None):
        self.openai = openai_client

    async def match_message_to_context(self, message: dict[str, Any], user_context: dict[str, Any]) -> dict[str, Any]:
        """
        Match symbolic message to user context using AI when available.
        """
        # Basic matching logic
        result = {
            "decision": "show",
            "score": 0.75,
            "matched_tags": ["focus", "light"],
        }

        # Enhance with OpenAI if available
        if self.openai:
            try:
                import json

                response = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze symbolic message alignment with user context",
                        },
                        {
                            "role": "user",
                            "content": f"Message: {json.dumps(message)}\nContext: {json.dumps(user_context)}",
                        },
                    ],
                )
                # Parse AI insights
                ai_analysis = response.choices[0].message.content
                if "defer" in ai_analysis.lower():
                    result["decision"] = "defer"
                elif "block" in ai_analysis.lower():
                    result["decision"] = "block"

            except Exception as e:
                logger.error(f"OpenAI symbolic matching failed: {e}")

        return result


class ConsentFilter:
    """Consent-aware filtering for NIAS messages"""

    def is_allowed(self, user_context: dict[str, Any], message: dict[str, Any]) -> bool:
        """Check if message delivery is consented"""
        # Check tier-based permissions
        user_tier = user_context.get("tier", 0)
        message_tier = message.get("required_tier", 0)

        if message_tier > user_tier:
            return False

        # Check specific consent flags
        consent_categories = user_context.get("consent_categories", [])
        message_category = message.get("category", "general")

        return message_category in consent_categories or "all" in consent_categories


class DreamRecorder:
    """Records messages for dream-state processing"""

    def __init__(self):
        self.dream_queue = []

    async def record_dream_message(self, message: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Record message for later dream processing"""
        dream_entry = {
            "dream_id": f"dream_{len(self.dream_queue)}_{datetime.datetime.now(timezone.utc).timestamp()}",
            "message": message,
            "context": context,
            "recorded_at": datetime.datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }

        self.dream_queue.append(dream_entry)

        return {
            "success": True,
            "dream_id": dream_entry["dream_id"],
            "message": "Saved for your dreams 🌙",
        }

    def get_pending_dreams(self) -> list[dict[str, Any]]:
        """Get all pending dream messages"""
        return [d for d in self.dream_queue if d["status"] == "pending"]
