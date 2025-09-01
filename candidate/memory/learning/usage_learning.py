"""
Usage-Based Learning System for DocuTutor.
Adapts and evolves based on how users interact with documentation.
"""

from collections import defaultdict
from datetime import datetime


class UserInteraction:
    def __init__(self, user_id: str, doc_id: str, interaction_type: str, metadata: dict):
        self.user_id = user_id
        self.doc_id = doc_id
        self.interaction_type = interaction_type
        self.metadata = metadata
        self.timestamp = datetime.now()


class InteractionPattern:
    def __init__(self):
        self.sequence: list[str] = []
        self.frequency = 0
        self.last_observed = datetime.now()
        self.success_rate = 1.0

    def update(self, success: bool):
        """Update pattern statistics."""
        self.frequency += 1
        self.last_observed = datetime.now()
        # Rolling average of success rate
        self.success_rate = (self.success_rate * (self.frequency - 1) + success) / self.frequency


class UsageBasedLearning:
    def __init__(self):
        self.interactions: list[UserInteraction] = []
        self.patterns: dict[str, InteractionPattern] = {}
        self.user_preferences: dict[str, dict] = defaultdict(dict)
        self.doc_statistics: dict[str, dict] = defaultdict(
            lambda: {
                "views": 0,
                "avg_time_spent": 0,
                "successful_uses": 0,
                "failed_uses": 0,
            }
        )

    def record_interaction(self, user_id: str, doc_id: str, interaction_type: str, metadata: dict):
        """Record a user interaction with documentation."""
        interaction = UserInteraction(user_id, doc_id, interaction_type, metadata)
        self.interactions.append(interaction)

        # Update document statistics
        stats = self.doc_statistics[doc_id]
        stats["views"] += 1
        if "time_spent" in metadata:
            avg_time = stats["avg_time_spent"]
            stats["avg_time_spent"] = (avg_time * (stats["views"] - 1) + metadata["time_spent"]) / stats["views"]

        if "success" in metadata:
            if metadata["success"]:
                stats["successful_uses"] += 1
            else:
                stats["failed_uses"] += 1

    def identify_patterns(self, window_size: int = 3):
        """Identify common interaction patterns."""
        for i in range(len(self.interactions) - window_size + 1):
            sequence = [
                f"{interaction.doc_id}:{interaction.interaction_type}"
                for interaction in self.interactions[i : i + window_size]
            ]
            pattern_key = "->".join(sequence)

            if pattern_key not in self.patterns:
                self.patterns[pattern_key] = InteractionPattern()
            self.patterns[pattern_key].sequence = sequence
            self.patterns[pattern_key].update(True)  # Assuming success for now

    def update_user_preferences(self, user_id: str, preferences: dict):
        """Update stored preferences for a user."""
        self.user_preferences[user_id].update(preferences)

    def get_document_effectiveness(self, doc_id: str) -> float:
        """Calculate the effectiveness score for a document."""
        stats = self.doc_statistics[doc_id]
        if stats["successful_uses"] + stats["failed_uses"] == 0:
            return 0.0

        return stats["successful_uses"] / (stats["successful_uses"] + stats["failed_uses"])

    def get_popular_sequences(self, min_frequency: int = 2) -> list[dict]:
        """Get commonly observed interaction sequences."""
        return [
            {
                "sequence": pattern.sequence,
                "frequency": pattern.frequency,
                "success_rate": pattern.success_rate,
            }
            for pattern in self.patterns.values()
            if pattern.frequency >= min_frequency
        ]

    def recommend_next_docs(self, current_doc: str, user_id: str) -> list[str]:
        """Recommend next documents based on patterns and user preferences."""
        recommendations = []
        self.user_preferences.get(user_id, {})

        # Look for patterns that start with current document
        for pattern in self.patterns.values():
            if pattern.sequence[0].startswith(current_doc):
                # Add next doc in sequence as recommendation
                next_doc = pattern.sequence[1].split(":")[0]
                if next_doc not in recommendations:
                    recommendations.append(next_doc)

        # Sort by effectiveness
        recommendations.sort(key=lambda doc_id: self.get_document_effectiveness(doc_id), reverse=True)

        return recommendations
