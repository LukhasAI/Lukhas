#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - UNIFIED EMOTIONAL MEMORY MANAGER
║ Example of EmotionalMemoryManager with unified tier system integration
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠════════════════════════════════════════════════════════════════════════════════
║ Module: emotional_memory_manager_unified.py
║ Path: lukhas/memory/emotional_memory_manager_unified.py
║ Version: 1.0.0 | Created: 2025-07-26
║ Authors: LUKHAS AI Architecture Team
╠════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠════════════════════════════════════════════════════════════════════════════════
║ This is an example showing how to integrate the unified tier system into
║ the EmotionalMemoryManager. It demonstrates:
║ - Adding user_id parameters to all methods
║ - Using the unified tier adapter for access control
║ - Consent checking for emotional operations
║ - Tier-based feature gating
╚════════════════════════════════════════════════════════════════════════════════
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from core.identity_integration import require_identity
from core.tier_unification_adapter import (
    emotional_tier_required,
    get_unified_adapter,
)
from memory.emotional_memory_manager import EmotionalMemoryManager


class UnifiedEmotionalMemoryManager(EmotionalMemoryManager):
    """
    Enhanced EmotionalMemoryManager with unified tier system integration.

    Key enhancements:
    - User-aware operations with ΛID tracking
    - Tier-based access control using LAMBDA_TIER system
    - Consent validation for emotional data access
    - Tier-specific feature availability
    """

    def __init__(
        self, config: Optional[dict[str, Any]] = None, base_path: Optional[Path] = None
    ):
        """Initialize unified emotional memory manager."""
        super().__init__(config, base_path)

        # Get unified tier adapter
        self.tier_adapter = get_unified_adapter()

        # Tier requirements for different operations
        self.tier_requirements = {
            "basic_store": "LAMBDA_TIER_1",
            "emotional_modulation": "LAMBDA_TIER_2",
            "deep_emotional_analysis": "LAMBDA_TIER_3",
            "quantum_emotional_enhancement": "LAMBDA_TIER_4",
            "full_emotional_manipulation": "LAMBDA_TIER_5",
        }

        self.logger.info("UnifiedEmotionalMemoryManager initialized with tier system")

    @require_identity(required_tier="LAMBDA_TIER_1", check_consent="memory_access")
    async def store(
        self,
        user_id: str,
        memory_data: dict[str, Any],
        memory_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Store memory with emotional tagging and user identity.

        Args:
            user_id: User's Lambda ID
            memory_data: Memory content to store
            memory_id: Optional memory ID
            metadata: Optional metadata

        Returns:
            Dict with storage status and memory ID
        """
        # Add user context to metadata
        enhanced_metadata = {
            **(metadata or {}),
            "user_id": user_id,
            "stored_by": user_id,
            "storage_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check if user has tier for emotional modulation
        user_matrix = self.tier_adapter.emotional.get_emotional_access_matrix(user_id)

        # Apply tier-based limitations
        if not user_matrix.get("symbolic_access", False):
            # Remove symbolic data for lower tiers
            memory_data = self._strip_symbolic_data(memory_data)

        # Call parent store method
        result = await super().store(memory_data, memory_id, enhanced_metadata)

        # Add user tracking
        if result["status"] == "success":
            self._track_user_memory(user_id, result["memory_id"])

        return result

    @require_identity(required_tier="LAMBDA_TIER_1", check_consent="memory_access")
    async def retrieve(
        self, user_id: str, memory_id: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Retrieve memory with tier-based emotional modulation.

        Higher tiers get access to:
        - T1: Basic emotional state
        - T2: Emotional modulation based on current state
        - T3: Full emotional history and symbolic associations
        - T4: Quantum emotional enhancements
        - T5: Complete emotional manipulation capabilities
        """
        # Check if user owns or has access to this memory
        if not self._check_memory_access(user_id, memory_id):
            return {"status": "error", "error": "Access denied to memory"}

        # Get user's emotional access matrix
        user_matrix = self.tier_adapter.emotional.get_emotional_access_matrix(user_id)

        # Add tier-based context
        enhanced_context = {
            **(context or {}),
            "user_tier_features": user_matrix,
            "requesting_user": user_id,
        }

        # Retrieve with modulation if tier allows
        if user_matrix.get("dream_influence", False):
            result = await super().retrieve(memory_id, enhanced_context)
        else:
            # Basic retrieval without modulation
            result = await super().retrieve(memory_id, None)

        # Apply tier-based filtering
        if result["status"] == "success":
            result["data"] = self._apply_tier_filtering(result["data"], user_matrix)

        return result

    @require_identity(required_tier="LAMBDA_TIER_2", check_consent="emotional_analysis")
    async def analyze_emotional_patterns(
        self, user_id: str, time_range: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Analyze user's emotional patterns over time.

        Requires LAMBDA_TIER_2 or higher and emotional_analysis consent.
        """
        user_matrix = self.tier_adapter.emotional.get_emotional_access_matrix(user_id)
        memory_depth_hours = user_matrix.get("memory_depth", 24)

        # Get user's memories within allowed time range
        user_memories = await self._get_user_memories(user_id, memory_depth_hours)

        # Analyze patterns based on tier
        patterns = {
            "user_id": user_id,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_count": len(user_memories),
            "time_range_hours": memory_depth_hours,
        }

        if user_matrix.get("emotional_granularity") in ["enhanced", "advanced", "full"]:
            # Advanced analysis for higher tiers
            patterns.update(
                {
                    "dominant_emotions": self._analyze_dominant_emotions(user_memories),
                    "emotional_transitions": self._analyze_transitions(user_memories),
                    "valence_trends": self._analyze_valence_trends(user_memories),
                }
            )

        if user_matrix.get("symbolic_access", False):
            # Add symbolic analysis for T3+
            patterns["symbolic_associations"] = self._analyze_symbolic_patterns(
                user_memories
            )

        return patterns

    @require_identity(
        required_tier="LAMBDA_TIER_3", check_consent="emotional_modification"
    )
    async def modulate_emotional_state(
        self, user_id: str, memory_id: str, target_state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Modulate the emotional state of a memory.

        Requires LAMBDA_TIER_3+ and explicit consent for emotional modification.
        """
        # Verify ownership
        if not self._check_memory_ownership(user_id, memory_id):
            return {"status": "error", "error": "Can only modulate your own memories"}

        # Get current state
        current = await self.get_emotional_context(memory_id)
        if current["status"] == "error":
            return current

        # Apply modulation with tier-based limits
        user_matrix = self.tier_adapter.emotional.get_emotional_access_matrix(user_id)

        if user_matrix.get("emotional_granularity") == "full":
            # Full control for T5
            new_state = target_state
        else:
            # Limited modulation for lower tiers
            new_state = self._apply_modulation_limits(
                current["emotional_context"]["current_state"], target_state, user_matrix
            )

        # Update emotional state
        result = await self.update_emotional_state(memory_id, new_state)

        # Log the modification
        if result["status"] == "success":
            self._log_emotional_modification(user_id, memory_id, current, new_state)

        return result

    @emotional_tier_required("T4")  # Using emotional tier decorator
    async def quantum_enhance_emotions(
        self, user_id: str, memory_id: str
    ) -> dict[str, Any]:
        """
        Apply quantum emotional enhancement to a memory.

        This advanced feature requires EmotionalTier T4 (maps to LAMBDA_TIER_4).
        """
        # This method would integrate with quantum systems
        # For now, return a placeholder
        return {
            "status": "success",
            "memory_id": memory_id,
            "enhancement": "quantum",
            "user_id": user_id,
            "message": "Quantum enhancement requires bio-orchestrator integration",
        }

    # === Private helper methods ===

    def _check_memory_access(self, user_id: str, memory_id: str) -> bool:
        """Check if user has access to a memory."""
        # For now, users can access their own memories
        # In production, this would check ownership and sharing permissions
        return True

    def _check_memory_ownership(self, user_id: str, memory_id: str) -> bool:
        """Check if user owns a memory."""
        # Would check actual ownership in production
        return True

    def _track_user_memory(self, user_id: str, memory_id: str) -> None:
        """Track memory ownership."""
        # Would update user-memory mapping in production

    def _strip_symbolic_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Remove symbolic data for users without access."""
        cleaned = data.copy()
        symbolic_keys = ["symbolic_tags", "glyph_associations", "quantum_symbols"]
        for key in symbolic_keys:
            cleaned.pop(key, None)
        return cleaned

    def _apply_tier_filtering(
        self, data: dict[str, Any], user_matrix: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply tier-based filtering to retrieved data."""
        filtered = data.copy()

        if not user_matrix.get("symbolic_access", False):
            filtered = self._strip_symbolic_data(filtered)

        if user_matrix.get("emotional_granularity") == "basic":
            # Simplify emotional data for basic tier
            if "_emotional_modulation" in filtered:
                filtered["_emotional_modulation"] = {"applied": True, "level": "basic"}

        return filtered

    async def _get_user_memories(
        self, user_id: str, hours_limit: float
    ) -> list[dict[str, Any]]:
        """Get user's memories within time limit."""
        # Would query actual user memories in production
        return []

    def _analyze_dominant_emotions(
        self, memories: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Analyze dominant emotions in memory set."""
        # Placeholder for emotion analysis
        return {}

    def _analyze_transitions(
        self, memories: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Analyze emotional transitions."""
        # Placeholder for transition analysis
        return []

    def _analyze_valence_trends(
        self, memories: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Analyze valence trends over time."""
        # Placeholder for trend analysis
        return {}

    def _analyze_symbolic_patterns(
        self, memories: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze symbolic patterns in memories."""
        # Placeholder for symbolic analysis
        return {}

    def _apply_modulation_limits(
        self,
        current_state: dict[str, Any],
        target_state: dict[str, Any],
        user_matrix: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply tier-based limits to emotional modulation."""
        # Limit the amount of change based on tier
        granularity = user_matrix.get("emotional_granularity", "basic")

        max_changes = {
            "basic": 0.1,
            "standard": 0.3,
            "enhanced": 0.5,
            "advanced": 0.8,
            "full": 1.0,
        }

        max_change = max_changes.get(granularity, 0.1)

        # Apply limits
        limited_state = current_state.copy()
        for key in ["valence", "arousal", "intensity"]:
            if key in target_state and key in current_state:
                current_val = current_state[key]
                target_val = target_state[key]
                change = target_val - current_val
                limited_change = max(-max_change, min(max_change, change))
                limited_state[key] = current_val + limited_change

        return limited_state

    def _log_emotional_modification(
        self,
        user_id: str,
        memory_id: str,
        old_state: dict[str, Any],
        new_state: dict[str, Any],
    ) -> None:
        """Log emotional state modifications for audit."""
        self.logger.info(
            "Emotional state modified",
            user_id=user_id,
            memory_id=memory_id,
            modification_timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Example usage function
async def example_unified_usage():
    """Example of using the unified emotional memory manager."""

    # Initialize manager
    manager = UnifiedEmotionalMemoryManager()

    # Example user IDs with different tiers
    basic_user = "Λ1234567890abcdef1"  # LAMBDA_TIER_1
    advanced_user = "Λ9876543210fedcba4"  # LAMBDA_TIER_4

    # Store memory (works for all tiers with consent)
    memory_result = await manager.store(
        user_id=basic_user,
        memory_data={
            "content": "Had a wonderful day at the park",
            "location": "Central Park",
            "weather": "sunny",
        },
        metadata={"tags": ["outdoor", "relaxation"]},
    )

    memory_id = memory_result.get("memory_id")

    # Retrieve memory - basic user gets limited data
    basic_retrieval = await manager.retrieve(basic_user, memory_id)

    # Advanced user gets enhanced retrieval with modulation
    advanced_retrieval = await manager.retrieve(
        advanced_user,
        memory_id,
        context={"current_emotion": {"valence": 0.8, "arousal": 0.6}},
    )

    # Analyze patterns - requires TIER_2+
    try:
        patterns = await manager.analyze_emotional_patterns(basic_user)
    except PermissionError:
        print("Basic user cannot analyze patterns")

    # Advanced user can analyze patterns
    patterns = await manager.analyze_emotional_patterns(advanced_user)

    # Emotional modulation - requires TIER_3+
    modulation_result = await manager.modulate_emotional_state(
        advanced_user,
        memory_id,
        target_state={"valence": 0.9, "arousal": 0.7, "intensity": 0.8},
    )

    return {
        "store_result": memory_result,
        "basic_retrieval": basic_retrieval,
        "advanced_retrieval": advanced_retrieval,
        "pattern_analysis": patterns,
        "modulation_result": modulation_result,
    }
