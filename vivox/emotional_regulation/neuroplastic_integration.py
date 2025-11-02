"""
VIVOX.ERN Neuroplastic & Tag System Integration
Connects emotional regulation to neuroplastic learning and tag propagation
"""

import logging
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from core.common import get_logger
try:
    from core.tags import get_tag_registry
    from core.tags.registry import TagCategory, TagDefinition, TagRegistry
try:
    from emotion.neuroplastic_connector import EmotionConnector, connector
from .vivox_ern_core import RegulationResponse, RegulationStrategy, VADVector
        try:
        try:
            try:
        try:
        try:
        try:
            try:
        try:
        try:

logger = logging.getLogger(__name__)

            self.active_tags.add(tag_name)

            # Create tag activation context
            activation_context = {
                "user_id": user_id,
                "source": "vivox_ern",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context,
            }

            # Activate tag if registry supports it
            if hasattr(self.tag_registry, "activate_tag"):
                await self.tag_registry.activate_tag(tag_name, activation_context)

        except Exception as e:
            logger.error(f"Error activating tag {tag_name}: {e}")

    async def _check_emergent_patterns(self, current_tags: list[str], context: dict[str, Any]) -> list[str]:
        """Check for emergent patterns from tag combinations"""
        emergent_tags = []

        # Pattern: Stress + Success -> Resilience Building
        if "vivox_stress_pattern" in current_tags and "vivox_regulation_success" in current_tags:
            emergent_tags.append("resilience_building")
            emergent_tags.append("stress_mastery_developing")

        # Pattern: Multiple learning tags -> Advanced User
        learning_tags = [tag for tag in current_tags if "learning" in tag or "adaptation" in tag]
        if len(learning_tags) >= 2:
            emergent_tags.append("advanced_emotional_learner")

        # Pattern: Colony learning + Success -> Pattern Leader
        if "vivox_colony_learning" in current_tags and "vivox_regulation_success" in current_tags:
            emergent_tags.append("emotional_pattern_leader")

        return emergent_tags

    def _update_tag_history(
        self,
        tags: list[str],
        regulation_response: RegulationResponse,
        context: dict[str, Any],
        user_id: str,
    ):
        """Update tag activation history"""
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "tags_activated": tags,
            "regulation_strategy": regulation_response.strategy_used.value,
            "effectiveness": regulation_response.effectiveness,
            "emotional_state": regulation_response.regulated_state.to_dict(),
            "context": context,
        }

        self.tag_history.append(history_entry)

        # Limit history size
        if len(self.tag_history) > 1000:
            self.tag_history = self.tag_history[-800:]

    def get_tag_analytics(self, user_id: str, hours: int = 24) -> dict[str, Any]:
        """Get tag analytics for user"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        relevant_history = [
            entry
            for entry in self.tag_history
            if entry["user_id"] == user_id and datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_time
        ]

        if not relevant_history:
            return {"message": "No tag data available"}

        # Analyze tag patterns
        tag_counts = {}
        tag_effectiveness = {}

        for entry in relevant_history:
            effectiveness = entry["effectiveness"]

            for tag in entry["tags_activated"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

                if tag not in tag_effectiveness:
                    tag_effectiveness[tag] = []
                tag_effectiveness[tag].append(effectiveness)

        # Calculate average effectiveness per tag
        tag_avg_effectiveness = {tag: sum(scores) / len(scores) for tag, scores in tag_effectiveness.items()}

        # Find most effective tags
        most_effective_tags = sorted(tag_avg_effectiveness.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_tag_activations": sum(tag_counts.values()),
            "unique_tags_activated": len(tag_counts),
            "most_frequent_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_effective_tags": most_effective_tags,
            "tag_activation_trend": len(relevant_history),
            "learning_indicators": {
                "neuroplastic_adaptations": tag_counts.get("vivox_neuroplastic_adaptation", 0),
                "successful_regulations": tag_counts.get("vivox_regulation_success", 0),
                "stress_patterns_identified": tag_counts.get("vivox_stress_pattern", 0),
                "colony_learning_events": tag_counts.get("vivox_colony_learning", 0),
            },
        }
