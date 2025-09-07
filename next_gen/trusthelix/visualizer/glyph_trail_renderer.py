#!/usr/bin/env python3
"""
Glyph Trail Renderer - Visualizes trust mutations and symbolic reversals
Creates visual representations of glyph transformations over time
"""
import streamlit as st
from datetime import timezone

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class GlyphTrail:
    """Visual representation of a glyph's journey"""

    glyph_type: str  # "trust", "biometric", "consent"
    trail: list[str]
    timestamps: list[datetime]
    mutations: list[dict[str, str]]
    reversals: list[int]  # Indices where reversals occurred

    def to_visual_string(self) -> str:
        """Convert trail to visual string with arrows"""
        visual = []
        for i, glyph in enumerate(self.trail):
            if i in self.reversals:
                visual.append(f"[{glyph}]")  # Mark reversals
            else:
                visual.append(glyph)

            if i < len(self.trail) - 1:
                visual.append("→")

        return " ".join(visual)

    def get_journey_summary(self) -> dict:
        """Summarize the glyph's journey"""
        return {
            "type": self.glyph_type,
            "start": self.trail[0] if self.trail else None,
            "current": self.trail[-1] if self.trail else None,
            "total_changes": len(self.trail) - 1,
            "reversals": len(self.reversals),
            "visual": self.to_visual_string(),
        }


class GlyphTrailRenderer:
    """
    Renders visual trails of glyph mutations and trust evolution
    Tracks reversals, cycles, and drift patterns
    """

    # Glyph categories for tracking
    GLYPH_CATEGORIES = {
        "trust": ["🔐", "🔓", "🔒"],
        "biometric": ["🧬", "🌱", "🦠"],
        "consent": ["🪷", "🌸", "🥀", "🌫️"],
        "drift": ["🌿", "🌀", "🌪️"],
        "special": ["✨", "🚨", "💫", "🌟"],
    }

    # Reversal patterns
    REVERSAL_PATTERNS = {
        "trust_lock": ["🔓", "🔐", "🔒"],
        "consent_revoke": ["🌸", "🪷", "🥀", "🌫️"],
        "biometric_decay": ["🌱", "🧬", "🦠"],
        "drift_storm": ["🌿", "🌀", "🌪️"],
    }

    def __init__(self):
        self.user_trails: dict[str, dict[str, GlyphTrail]] = {}
        self.global_patterns: list[dict] = []
        logger.info("🎨 Glyph Trail Renderer initialized")

    def track_mutation(
        self,
        user_id: str,
        from_glyph: str,
        to_glyph: str,
        timestamp: datetime,
        reason: str = "",
    ):
        """Track a single glyph mutation"""
        # Determine glyph category
        category = self._get_glyph_category(from_glyph) or self._get_glyph_category(to_glyph)

        if not category:
            logger.warning(f"Unknown glyph category for {from_glyph} → {to_glyph}")
            return

        # Initialize user trails if needed
        if user_id not in self.user_trails:
            self.user_trails[user_id] = {}

        if category not in self.user_trails[user_id]:
            self.user_trails[user_id][category] = GlyphTrail(
                glyph_type=category,
                trail=[from_glyph],
                timestamps=[timestamp],
                mutations=[],
                reversals=[],
            )

        trail = self.user_trails[user_id][category]

        # Check for reversal
        is_reversal = self._is_reversal(trail.trail, to_glyph)
        if is_reversal:
            trail.reversals.append(len(trail.trail))

        # Add to trail
        trail.trail.append(to_glyph)
        trail.timestamps.append(timestamp)
        trail.mutations.append(
            {
                "from": from_glyph,
                "to": to_glyph,
                "reason": reason,
                "timestamp": timestamp.isoformat(),
            }
        )

        # Track global patterns
        self._track_global_pattern(user_id, category, from_glyph, to_glyph, is_reversal)

        logger.info(f"🎯 Tracked: {from_glyph} → {to_glyph} ({category})")

    def _get_glyph_category(self, glyph: str) -> Optional[str]:
        """Determine which category a glyph belongs to"""
        for category, glyphs in self.GLYPH_CATEGORIES.items():
            if glyph in glyphs:
                return category
        return None

    def _is_reversal(self, trail: list[str], new_glyph: str) -> bool:
        """Check if this mutation represents a reversal"""
        if len(trail) < 2:
            return False

        # Check if going back to a previous state
        if new_glyph in trail[:-1]:
            return True

        # Check known reversal patterns
        for pattern in self.REVERSAL_PATTERNS.values():
            # Check if current sequence matches a reversal pattern
            for i in range(len(pattern) - 1):
                if len(trail) >= 1 and trail[-1] == pattern[i] and new_glyph == pattern[i + 1]:
                    return True

        return False

    def _track_global_pattern(
        self,
        user_id: str,
        category: str,
        from_glyph: str,
        to_glyph: str,
        is_reversal: bool,
    ):
        """Track patterns across all users"""
        pattern = {
            "user_id": user_id,
            "category": category,
            "mutation": f"{from_glyph}→{to_glyph}",
            "is_reversal": is_reversal,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.global_patterns.append(pattern)

    def render_user_journey(self, user_id: str) -> dict[str, str]:
        """Render complete journey for a user"""
        if user_id not in self.user_trails:
            return {"error": "User not found"}

        journey = {}
        for category, trail in self.user_trails[user_id].items():
            journey[f"{category}_journey"] = trail.to_visual_string()

        return journey

    def render_drift_progression(self, user_id: str) -> str:
        """Render drift progression visualization"""
        if user_id not in self.user_trails or "drift" not in self.user_trails[user_id]:
            return "🌿"  # Default stable

        drift_trail = self.user_trails[user_id]["drift"]
        return drift_trail.to_visual_string()

    def get_reversal_report(self, user_id: Optional[str] = None) -> dict:
        """Generate report on reversals"""
        if user_id:
            if user_id not in self.user_trails:
                return {"user": user_id, "reversals": 0, "details": []}

            reversal_details = []
            total_reversals = 0

            for category, trail in self.user_trails[user_id].items():
                for idx in trail.reversals:
                    if idx < len(trail.trail):
                        reversal_details.append(
                            {
                                "category": category,
                                "at_position": idx,
                                "glyph": trail.trail[idx],
                                "timestamp": (
                                    trail.timestamps[idx].isoformat() if idx < len(trail.timestamps) else None
                                ),
                            }
                        )
                total_reversals += len(trail.reversals)

            return {
                "user": user_id,
                "reversals": total_reversals,
                "details": reversal_details,
            }
        else:
            # Global reversal report
            reversal_count = sum(1 for p in self.global_patterns if p["is_reversal"])
            return {
                "total_reversals": reversal_count,
                "reversal_rate": (reversal_count / len(self.global_patterns) if self.global_patterns else 0),
                "common_reversals": self._get_common_reversals(),
            }

    def _get_common_reversals(self) -> list[dict]:
        """Find most common reversal patterns"""
        reversal_counts = {}

        for pattern in self.global_patterns:
            if pattern["is_reversal"]:
                key = pattern["mutation"]
                reversal_counts[key] = reversal_counts.get(key, 0) + 1

        # Sort by frequency
        sorted_reversals = sorted(reversal_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"pattern": pattern, "count": count} for pattern, count in sorted_reversals[:5]]

    def export_visual_manifest(self) -> dict:
        """Export complete visual manifest"""
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_users": len(self.user_trails),
            "total_mutations": len(self.global_patterns),
            "user_journeys": {},
        }

        # Add each user's journey
        for user_id, trails in self.user_trails.items():
            user_journey = {}
            for category, trail in trails.items():
                user_journey[category] = trail.get_journey_summary()
            manifest["user_journeys"][user_id] = user_journey

        # Add global statistics
        manifest["statistics"] = {
            "reversal_report": self.get_reversal_report(),
            "category_distribution": self._get_category_distribution(),
            "mutation_frequency": self._get_mutation_frequency(),
        }

        return manifest

    def _get_category_distribution(self) -> dict[str, int]:
        """Get distribution of mutations by category"""
        distribution = {}
        for pattern in self.global_patterns:
            category = pattern["category"]
            distribution[category] = distribution.get(category, 0) + 1
        return distribution

    def _get_mutation_frequency(self) -> list[dict]:
        """Get most frequent mutations"""
        mutation_counts = {}

        for pattern in self.global_patterns:
            key = pattern["mutation"]
            mutation_counts[key] = mutation_counts.get(key, 0) + 1

        # Sort by frequency
        sorted_mutations = sorted(mutation_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"mutation": mutation, "frequency": count} for mutation, count in sorted_mutations[:10]]

    def render_symbolic_reversal(self, glyph_sequence: list[str]) -> str:
        """Render a symbolic reversal sequence with special formatting"""
        if not glyph_sequence:
            return ""

        # Mark the reversal point
        visual = []
        for i, glyph in enumerate(glyph_sequence):
            if i == len(glyph_sequence) - 1:
                visual.append(f"⟲{glyph}")  # Reversal symbol
            else:
                visual.append(glyph)
                visual.append("→")

        return " ".join(visual)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    renderer = GlyphTrailRenderer()

    # Simulate a user journey with mutations and reversals
    user_id = "test_user_001"
    mutations = [
        ("🔐", "🔓", "Authentication success"),
        ("🧬", "🌱", "Trust growing"),
        ("🪷", "🌸", "Consent granted"),
        ("🌿", "🌿", "Drift stable"),
        ("🔓", "🔐", "Security check"),  # Reversal
        ("🌸", "🪷", "Consent normalized"),  # Reversal
        ("🌿", "🌀", "Drift increasing"),
        ("🔐", "🔒", "Emergency lock"),  # Further reversal
        ("🌀", "🌪️", "Drift critical"),
        ("🪷", "🥀", "Consent revoked"),  # Reversal pattern
    ]

    print("🎨 Simulating Glyph Trail Rendering")
    print("=" * 60)

    for from_g, to_g, reason in mutations:
        renderer.track_mutation(user_id, from_g, to_g, datetime.now(timezone.utc), reason)

    # Render journey
    journey = renderer.render_user_journey(user_id)
    print("\n📍 User Journey Visualization:")
    for key, value in journey.items():
        print(f"   {key}: {value}")

    # Get reversal report
    reversal_report = renderer.get_reversal_report(user_id)
    print("\n⟲ Reversal Report:")
    print(f"   Total reversals: {reversal_report['reversals']}")
    for detail in reversal_report["details"]:
        print(f"   - {detail['category']}: position {detail['at_position']} ({detail['glyph']})")

    # Export manifest
    manifest = renderer.export_visual_manifest()
    print("\n📋 Visual Manifest Summary:")
    print(f"   Total users: {manifest['total_users']}")
    print(f"   Total mutations: {manifest['total_mutations']}")
    print(f"   Category distribution: {manifest['statistics']['category_distribution']}")

    # Show symbolic reversal
    reversal_seq = ["🌸", "🪷", "🥀", "🌫️"]
    print("\n🔄 Symbolic Reversal:")
    print(f"   {renderer.render_symbolic_reversal(reversal_seq}")
