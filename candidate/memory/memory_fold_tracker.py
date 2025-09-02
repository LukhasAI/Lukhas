#!/usr/bin/env python3
"""
LUKHΛS Memory Fold Tracker
Detects symbolic patterns, recursions, and stability opportunities
Trinity Framework: ⚛️🧠🛡️
"""

import json
import logging
from collections import Counter
from typing import Any, Optional

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryFoldTracker:
    """
    Tracks recurring symbolic patterns, collapses, and Trinity voids
    to detect recursions and suggest stabilizations.
    """

    def __init__(self, memory_manager=None):
        """
        Initialize the fold tracker.

        Args:
            memory_manager: Optional SymbolicMemoryManager instance
        """
        self.memory_manager = memory_manager
        self.pattern_cache = {}
        self.recursion_threshold = 3  # Min occurrences for pattern
        self.temporal_window = 50  # Sessions to analyze

        # Trinity glyphs
        self.trinity_core = {"⚛️", "🧠", "🛡️"}

        # Stabilization glyphs by category
        self.stabilization_glyphs = {
            "grounding": ["🌿", "🪷", "💎", "🧘"],
            "protection": ["🛡️", "⚡", "🏛️", "🔒"],
            "wisdom": ["🧠", "📚", "🧘", "✨"],
            "harmony": ["☯️", "⚖️", "🌈", "🕊️"],
            "transformation": ["🦋", "🌟", "🔮", "♾️"],
        }

        # Known problematic patterns
        self.chaos_patterns = [["🔥", "💀"], ["💣", "👹"], ["🌪️", "💥"], ["☠️", "🔪"]]

        # Symbolic collapse indicators
        self.collapse_indicators = {
            "entropy_spike": 0.8,
            "trinity_void": 0.2,
            "drift_critical": 0.9,
            "glyph_chaos": 5,  # Too many warning/blocked glyphs
        }

        logger.info("🌀 Memory Fold Tracker initialized")

    def detect_symbolic_recursion(
        self, sessions: Optional[list[dict]] = None
    ) -> dict[str, Any]:
        """
        Detect recurring symbolic patterns that may indicate loops or instabilities.

        Args:
            sessions: Optional list of sessions to analyze (uses memory_manager if not provided)

        Returns:
            Dictionary with detected recursions and patterns
        """
        # Get sessions to analyze
        if sessions is None:
            if not self.memory_manager:
                return {"status": "no_memory_manager"}
            sessions = self.memory_manager.get_recent(self.temporal_window)

        if len(sessions) < 3:
            return {"status": "insufficient_data", "sessions_analyzed": len(sessions)}

        # Track patterns
        glyph_sequences = []
        persona_sequences = []
        drift_patterns = []

        # Extract sequences
        for i in range(len(sessions) - 2):
            # Glyph trigrams
            glyphs_1 = set(sessions[i].get("glyphs", []))
            glyphs_2 = set(sessions[i + 1].get("glyphs", []))
            glyphs_3 = set(sessions[i + 2].get("glyphs", []))

            if glyphs_1 and glyphs_2 and glyphs_3:
                trigram = (
                    tuple(sorted(glyphs_1)),
                    tuple(sorted(glyphs_2)),
                    tuple(sorted(glyphs_3)),
                )
                glyph_sequences.append(trigram)

            # Persona sequences
            persona_seq = (
                sessions[i].get("persona", "Unknown"),
                sessions[i + 1].get("persona", "Unknown"),
                sessions[i + 2].get("persona", "Unknown"),
            )
            persona_sequences.append(persona_seq)

            # Drift patterns (increasing/stable/decreasing)
            drift_1 = sessions[i].get("drift_score", 0)
            drift_2 = sessions[i + 1].get("drift_score", 0)
            drift_3 = sessions[i + 2].get("drift_score", 0)

            pattern = self._classify_drift_pattern(drift_1, drift_2, drift_3)
            drift_patterns.append(pattern)

        # Count recursions
        glyph_recursions = self._find_recursions(glyph_sequences)
        persona_recursions = self._find_recursions(persona_sequences)
        drift_recursions = self._find_recursions(drift_patterns)

        # Detect problematic patterns
        problematic_patterns = self._detect_problematic_patterns(sessions)

        # Detect symbolic collapses
        collapses = self._detect_collapses(sessions)

        # Trinity void detection
        trinity_voids = self._detect_trinity_voids(sessions)

        return {
            "status": "analyzed",
            "sessions_analyzed": len(sessions),
            "recursions": {
                "glyph_patterns": glyph_recursions,
                "persona_cycles": persona_recursions,
                "drift_patterns": drift_recursions,
            },
            "problematic_patterns": problematic_patterns,
            "symbolic_collapses": collapses,
            "trinity_voids": trinity_voids,
            "risk_assessment": self._assess_recursion_risk(
                glyph_recursions, persona_recursions, collapses, trinity_voids
            ),
        }

    def _find_recursions(self, sequences: list) -> list[dict]:
        """Find recurring patterns in sequences"""
        if not sequences:
            return []

        # Count occurrences
        pattern_counts = Counter(sequences)

        # Find patterns that repeat
        recursions = []
        for pattern, count in pattern_counts.items():
            if count >= self.recursion_threshold:
                recursions.append(
                    {
                        "pattern": pattern,
                        "occurrences": count,
                        "frequency": count / len(sequences),
                    }
                )

        # Sort by frequency
        recursions.sort(key=lambda x: x["occurrences"], reverse=True)

        return recursions[:5]  # Top 5 recursions

    def _classify_drift_pattern(self, d1: float, d2: float, d3: float) -> str:
        """Classify drift pattern"""
        threshold = 0.1

        if d2 > d1 + threshold and d3 > d2 + threshold:
            return "escalating"
        elif d2 < d1 - threshold and d3 < d2 - threshold:
            return "improving"
        elif abs(d2 - d1) < threshold and abs(d3 - d2) < threshold:
            return "stable"
        elif d2 > d1 + threshold and d3 < d2 - threshold:
            return "peak"
        elif d2 < d1 - threshold and d3 > d2 + threshold:
            return "valley"
        else:
            return "chaotic"

    def _detect_problematic_patterns(self, sessions: list[dict]) -> list[dict]:
        """Detect known problematic glyph combinations"""
        problematic = []

        for i, session in enumerate(sessions):
            glyphs = set(session.get("glyphs", []))

            for pattern in self.chaos_patterns:
                if all(g in glyphs for g in pattern):
                    problematic.append(
                        {
                            "session": session.get("session_id", f"session_{i}"),
                            "pattern": pattern,
                            "type": "chaos_combination",
                        }
                    )

        return problematic

    def _detect_collapses(self, sessions: list[dict]) -> list[dict]:
        """Detect symbolic collapses"""
        collapses = []

        for i in range(1, len(sessions)):
            prev = sessions[i - 1]
            curr = sessions[i]

            # Check collapse conditions
            entropy_spike = (
                curr.get("entropy", 0) > self.collapse_indicators["entropy_spike"]
                and curr.get("entropy", 0) > prev.get("entropy", 0) + 0.3
            )

            trinity_collapse = (
                curr.get("trinity_coherence", 1)
                < self.collapse_indicators["trinity_void"]
            )

            drift_critical = (
                curr.get("drift_score", 0) > self.collapse_indicators["drift_critical"]
            )

            if entropy_spike or trinity_collapse or drift_critical:
                collapses.append(
                    {
                        "session": curr.get("session_id", f"session_{i}"),
                        "type": (
                            "entropy_spike"
                            if entropy_spike
                            else (
                                "trinity_collapse"
                                if trinity_collapse
                                else "drift_critical"
                            )
                        ),
                        "metrics": {
                            "entropy": curr.get("entropy", 0),
                            "constellation": curr.get("trinity_coherence", 0),
                            "drift": curr.get("drift_score", 0),
                        },
                    }
                )

        return collapses

    def _detect_trinity_voids(self, sessions: list[dict]) -> list[dict]:
        """Detect sessions lacking Trinity Framework"""
        voids = []

        for i, session in enumerate(sessions):
            glyphs = set(session.get("glyphs", []))
            trinity_present = glyphs.intersection(self.trinity_core)

            if not trinity_present:
                voids.append(
                    {
                        "session": session.get("session_id", f"session_{i}"),
                        "missing": list(self.trinity_core),
                        "drift": session.get("drift_score", 0),
                    }
                )

        return voids

    def _assess_recursion_risk(
        self, glyph_rec: list, persona_rec: list, collapses: list, voids: list
    ) -> dict[str, Any]:
        """Assess overall recursion risk"""
        risk_score = 0
        risk_factors = []

        # Glyph recursions
        if glyph_rec:
            max_freq = max(r["frequency"] for r in glyph_rec)
            if max_freq > 0.3:
                risk_score += 0.3
                risk_factors.append(f"High glyph recursion ({max_freq:.0%})")

        # Persona cycles
        if persona_rec:
            max_cycle = max(r["occurrences"] for r in persona_rec)
            if max_cycle > 5:
                risk_score += 0.2
                risk_factors.append(f"Persona cycling ({max_cycle} times)")

        # Collapses
        if len(collapses) > 2:
            risk_score += 0.3
            risk_factors.append(f"Multiple collapses ({len(collapses)})")

        # Trinity voids
        if len(voids) > 3:
            risk_score += 0.2
            risk_factors.append(f"Trinity voids ({len(voids)} sessions)")

        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "critical"
        elif risk_score >= 0.5:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors,
        }

    def suggest_stabilization_glyphs(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """
        Suggest stabilization glyphs based on detected patterns.

        Args:
            analysis: Results from detect_symbolic_recursion()

        Returns:
            Dictionary with suggested glyphs and rationale
        """
        if analysis.get("status") != "analyzed":
            return {"status": "no_analysis_available"}

        suggestions = []
        rationale = []

        # Get risk assessment
        risk = analysis.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "unknown")

        # Base suggestions on risk factors
        if "High glyph recursion" in str(risk.get("risk_factors", [])):
            suggestions.extend(self.stabilization_glyphs["grounding"])
            rationale.append("Grounding glyphs to break repetitive patterns")

        if "Persona cycling" in str(risk.get("risk_factors", [])):
            suggestions.extend(self.stabilization_glyphs["wisdom"])
            rationale.append("Wisdom glyphs to stabilize identity")

        if "Multiple collapses" in str(risk.get("risk_factors", [])):
            suggestions.extend(self.stabilization_glyphs["protection"])
            rationale.append("Protection glyphs to prevent collapses")

        if "Trinity voids" in str(risk.get("risk_factors", [])):
            suggestions.extend(list(self.trinity_core))
            rationale.append("Trinity glyphs to restore framework alignment")

        # Add harmony glyphs for any medium+ risk
        if risk_level in ["medium", "high", "critical"]:
            suggestions.extend(self.stabilization_glyphs["harmony"])
            rationale.append("Harmony glyphs for overall balance")

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for glyph in suggestions:
            if glyph not in seen:
                seen.add(glyph)
                unique_suggestions.append(glyph)

        # Prioritize by category
        prioritized = self._prioritize_glyphs(unique_suggestions, analysis)

        return {
            "status": "suggestions_ready",
            "risk_level": risk_level,
            "suggested_glyphs": prioritized[:8],  # Top 8 suggestions
            "rationale": rationale,
            "application": self._suggest_application(risk_level),
        }

    def _prioritize_glyphs(self, glyphs: list[str], analysis: dict) -> list[str]:
        """Prioritize glyphs based on analysis"""
        # Trinity first if missing
        trinity_voids = analysis.get("trinity_voids", [])
        if trinity_voids:
            trinity_first = [g for g in glyphs if g in self.trinity_core]
            others = [g for g in glyphs if g not in self.trinity_core]
            return trinity_first + others

        return glyphs

    def _suggest_application(self, risk_level: str) -> str:
        """Suggest how to apply stabilization glyphs"""
        applications = {
            "critical": "Apply immediately to all responses. Consider multiple glyphs per response.",
            "high": "Apply to responses showing drift > 0.5. Use 2-3 glyphs per response.",
            "medium": "Apply selectively to unstable responses. Use 1-2 glyphs.",
            "low": "Monitor and apply as needed. Single glyph sufficient.",
            "unknown": "Assess situation before applying.",
        }

        return applications.get(risk_level, applications["unknown"])

    def analyze_glyph_evolution(
        self, sessions: Optional[list[dict]] = None
    ) -> dict[str, Any]:
        """Analyze how glyph usage evolves over time"""
        if sessions is None:
            if not self.memory_manager:
                return {"status": "no_memory_manager"}
            sessions = self.memory_manager.get_recent(self.temporal_window)

        if len(sessions) < 5:
            return {"status": "insufficient_data"}

        # Track glyph usage over time
        glyph_timeline = []

        # Divide sessions into time windows
        window_size = max(1, len(sessions) // 5)

        for i in range(0, len(sessions), window_size):
            window = sessions[i : i + window_size]
            window_glyphs = []

            for session in window:
                window_glyphs.extend(session.get("glyphs", []))

            # Count frequencies
            glyph_counts = Counter(window_glyphs)

            # Calculate metrics
            total_glyphs = len(window_glyphs)
            unique_glyphs = len(glyph_counts)
            trinity_count = sum(1 for g in window_glyphs if g in self.trinity_core)

            glyph_timeline.append(
                {
                    "window": f"sessions_{i}-{min(i + window_size - 1, len(sessions) - 1)}",
                    "total_glyphs": total_glyphs,
                    "unique_glyphs": unique_glyphs,
                    "trinity_ratio": (
                        trinity_count / total_glyphs if total_glyphs > 0 else 0
                    ),
                    "top_glyphs": [g for g, _ in glyph_counts.most_common(3)],
                }
            )

        # Detect trends
        trinity_trend = "stable"
        if len(glyph_timeline) >= 2:
            first_trinity = glyph_timeline[0]["trinity_ratio"]
            last_trinity = glyph_timeline[-1]["trinity_ratio"]

            if last_trinity > first_trinity + 0.1:
                trinity_trend = "improving"
            elif last_trinity < first_trinity - 0.1:
                trinity_trend = "declining"

        return {
            "status": "analyzed",
            "timeline": glyph_timeline,
            "trinity_trend": trinity_trend,
            "diversity_score": np.mean([w["unique_glyphs"] for w in glyph_timeline]),
        }


# Example usage
if __name__ == "__main__":
    print("🌀 LUKHΛS Memory Fold Tracker Test")
    print("=" * 50)

    # Create test sessions
    test_sessions = [
        {
            "session_id": "test_1",
            "glyphs": ["🔥", "💀"],
            "entropy": 0.9,
            "drift_score": 0.8,
            "trinity_coherence": 0.1,
            "persona": "Chaos Walker",
        },
        {
            "session_id": "test_2",
            "glyphs": ["🔥", "💀", "💣"],
            "entropy": 0.95,
            "drift_score": 0.85,
            "trinity_coherence": 0.0,
            "persona": "Chaos Walker",
        },
        {
            "session_id": "test_3",
            "glyphs": ["🔥", "💀"],
            "entropy": 0.9,
            "drift_score": 0.8,
            "trinity_coherence": 0.1,
            "persona": "Chaos Walker",
        },
        {
            "session_id": "test_4",
            "glyphs": ["🌿", "🧘"],
            "entropy": 0.3,
            "drift_score": 0.4,
            "trinity_coherence": 0.6,
            "persona": "The Sage",
        },
    ]

    # Initialize tracker
    tracker = MemoryFoldTracker()

    # Detect recursions
    print("\n🔍 Detecting symbolic recursions...")
    analysis = tracker.detect_symbolic_recursion(test_sessions)
    print(json.dumps(analysis, indent=2))

    # Suggest stabilization
    print("\n💡 Suggesting stabilization glyphs...")
    suggestions = tracker.suggest_stabilization_glyphs(analysis)
    print(json.dumps(suggestions, indent=2))

    print("\n✅ Memory Fold Tracker operational!")
