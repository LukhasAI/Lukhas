from datetime import datetime, timezone
"""
NIAS (Non-Intrusive Ad System) Module
Unified module for ethical, consent-aware symbolic message delivery.
Integrates with Dream system for deferred processing and quantum consciousness.
"""
import time
import streamlit as st

import logging
from typing import Any

# Import legacy functions that other modules might expect
from lukhas.core.interfaces.as_agent.sys.nias.dream_recorder import record_dream_message
from lukhas.core.interfaces.as_agent.sys.nias.narration_controller import (
    fetch_narration_entries,
    filter_narration_queue,
    load_user_settings,
)

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


def narrate_dreams(dreams: list[dict[str, Any]]) -> None:
    """
    Narrate dreams using the NIAS voice system.
    This is a compatibility wrapper for the dream voice pipeline.
    """
    for dream in dreams:
        logger.info(f"🎙 Narrating dream: {dream.get('id', 'unknown')}")
        # TODO: Integrate with actual voice narration system
        print(f"[NIAS Narration] {dream.get('content', 'Empty dream')}")


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
        import datetime

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