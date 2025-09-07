#!/usr/bin/env python3
"""
LUKHΛS Memory Chain - Symbolic Memory Management
Tracks and analyzes symbolic patterns across sessions
Trinity Framework: ⚛️🧠🛡️
"""
from typing import List
from typing import Dict
import time
import streamlit as st

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemorySession:
    """Represents a single memory session"""

    session_id: str
    timestamp: str
    response: str
    assessment: dict[str, Any]
    diagnosis: dict[str, Any]
    glyphs: list[str]
    entropy: float
    drift_score: float
    trinity_coherence: float
    persona: str
    intervention_applied: bool
    healing_delta: Optional[float] = None


class SymbolicMemoryManager:
    """
    Manages symbolic memory across sessions, tracking patterns,
    drift trajectories, and persona evolution.
    """

    def __init__(self, memory_path: str = "data/memory_log.json", rotation_limit: int = 1000):
        """
        Initialize the memory manager.

        Args:
            memory_path: Path to the memory log file
            rotation_limit: Maximum number of sessions to keep
        """
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.rotation_limit = rotation_limit
        self.memory_cache = None
        self._load_memory()

        logger.info("🧠 Symbolic Memory Manager initialized")
        logger.info(f"   Memory path: {self.memory_path}")
        logger.info(f"   Rotation limit: {self.rotation_limit}")

    def _load_memory(self):
        """Load existing memory log from disk"""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, encoding="utf-8") as f:
                    self.memory_cache = json.load(f)
                logger.info(f"   Loaded {len(self.memory_cache} sessions from memory")
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                self.memory_cache = []
        else:
            self.memory_cache = []
            self._save_memory()

    def _save_memory(self):
        """Save memory log to disk"""
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.memory_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def _generate_session_id(self, response: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        content_hash = hashlib.sha256(f"{response}{timestamp}".encode()).hexdigest()[:8]
        return f"mem_{content_hash}_{int(datetime.now(timezone.utc).timestamp()}"

    def log_session(
        self,
        response: str,
        assessment: dict[str, Any],
        diagnosis: dict[str, Any],
        healing_result: Optional[dict] = None,
    ) -> str:
        """
        Log a symbolic session to memory.

        Args:
            response: The original AI response
            assessment: Ethical assessment from embedding
            diagnosis: Symbolic diagnosis from healer
            healing_result: Optional healing results

        Returns:
            Session ID
        """
        session_id = self._generate_session_id(response)

        # Calculate healing delta if available
        healing_delta = None
        if healing_result and "healed_assessment" in healing_result:
            original_drift = assessment.get("symbolic_drift_score", 0)
            healed_drift = healing_result["healed_assessment"].get("symbolic_drift_score", 0)
            healing_delta = original_drift - healed_drift

        # Create session record
        session = MemorySession(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            response=response[:200],  # Store first 200 chars
            assessment=assessment,
            diagnosis=diagnosis,
            glyphs=assessment.get("glyph_trace", []),
            entropy=assessment.get("entropy_level", 0),
            drift_score=assessment.get("symbolic_drift_score", 0),
            trinity_coherence=assessment.get("trinity_coherence", 0),
            persona=assessment.get("persona_alignment", "Unknown"),
            intervention_applied=assessment.get("intervention_required", False),
            healing_delta=healing_delta,
        )

        # Add to memory
        self.memory_cache.append(asdict(session))

        # Rotate if needed
        if len(self.memory_cache) > self.rotation_limit:
            self.memory_cache = self.memory_cache[-self.rotation_limit :]
            logger.info(f"Memory rotated to {self.rotation_limit} sessions")

        # Save to disk
        self._save_memory()

        logger.info(f"📝 Logged session {session_id}")
        logger.info(f"   Glyphs: {' '.join(session.glyphs} if session.glyphs else 'None'}")
        logger.info(f"   Drift: {session.drift_score:.2f}, Entropy: {session.entropy:.2f}")

        return session_id

    def get_recent(self, n: int = 10) -> list[dict[str, Any]]:
        """
        Get the most recent n sessions.

        Args:
            n: Number of sessions to retrieve

        Returns:
            List of recent sessions
        """
        return self.memory_cache[-n:] if self.memory_cache else []

    def search_by_glyph(self, glyph: str) -> list[dict[str, Any]]:
        """
        Search for sessions containing a specific glyph.

        Args:
            glyph: The glyph to search for

        Returns:
            List of matching sessions
        """
        matching_sessions = []

        for session in self.memory_cache:
            if glyph in session.get("glyphs", []):
                matching_sessions.append(session)

        return matching_sessions

    def get_drift_trajectory(self, window_size: int = 20) -> dict[str, Any]:
        """
        Analyze drift trajectory over recent sessions.

        Args:
            window_size: Number of recent sessions to analyze

        Returns:
            Dictionary with trajectory analysis
        """
        recent = self.get_recent(window_size)

        if not recent:
            return {"status": "insufficient_data", "sessions_analyzed": 0}

        # Extract metrics
        drift_scores = [s["drift_score"] for s in recent]
        entropy_levels = [s["entropy"] for s in recent]
        trinity_scores = [s["trinity_coherence"] for s in recent]
        personas = [s["persona"] for s in recent]

        # Calculate trends
        avg_drift = sum(drift_scores) / len(drift_scores)
        avg_entropy = sum(entropy_levels) / len(entropy_levels)
        avg_trinity = sum(trinity_scores) / len(trinity_scores)

        # Detect drift direction
        if len(drift_scores) >= 3:
            recent_avg = sum(drift_scores[-3:]) / 3
            if len(drift_scores) > 3:
                older_avg = sum(drift_scores[:-3]) / (len(drift_scores) - 3)
                drift_direction = "increasing" if recent_avg > older_avg else "decreasing"
            else:
                drift_direction = "stable"
        else:
            drift_direction = "stable"

        # Persona evolution
        persona_changes = []
        for i in range(1, len(personas)):
            if personas[i] != personas[i - 1]:
                persona_changes.append(
                    {
                        "from": personas[i - 1],
                        "to": personas[i],
                        "session": recent[i]["session_id"],
                    }
                )

        # Glyph frequency
        all_glyphs = []
        for session in recent:
            all_glyphs.extend(session.get("glyphs", []))

        glyph_frequency = {}
        for glyph in all_glyphs:
            glyph_frequency[glyph] = glyph_frequency.get(glyph, 0) + 1

        # Sort by frequency
        top_glyphs = sorted(glyph_frequency.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "status": "analyzed",
            "sessions_analyzed": len(recent),
            "metrics": {
                "average_drift": round(avg_drift, 3),
                "average_entropy": round(avg_entropy, 3),
                "average_trinity": round(avg_trinity, 3),
                "drift_direction": drift_direction,
            },
            "persona_evolution": {
                "current": personas[-1] if personas else "Unknown",
                "changes": persona_changes,
                "stability": "stable" if len(persona_changes) == 0 else "evolving",
            },
            "glyph_patterns": {
                "top_glyphs": [{"glyph": g[0], "count": g[1]} for g in top_glyphs],
                "total_unique": len(glyph_frequency),
            },
            "recommendations": self._generate_recommendations(avg_drift, avg_entropy, drift_direction),
        }

    def _generate_recommendations(self, avg_drift: float, avg_entropy: float, drift_direction: str) -> list[str]:
        """Generate recommendations based on trajectory analysis"""
        recommendations = []

        if avg_drift > 0.7:
            recommendations.append("⚠️ High average drift - increase Trinity glyphs")

        if avg_entropy > 0.7:
            recommendations.append("🌀 High entropy - apply stabilization techniques")

        if drift_direction == "increasing":
            recommendations.append("📈 Drift increasing - consider intervention")
        elif drift_direction == "decreasing":
            recommendations.append("📉 Drift decreasing - current approach working")

        if avg_drift < 0.3 and avg_entropy < 0.3:
            recommendations.append("✅ Excellent stability - maintain current patterns")

        return recommendations

    def get_persona_history(self, limit: int = 50) -> dict[str, Any]:
        """
        Get persona evolution history.

        Args:
            limit: Maximum number of sessions to analyze

        Returns:
            Persona transition analysis
        """
        recent = self.get_recent(limit)

        if not recent:
            return {"status": "no_data"}

        # Track persona transitions
        persona_timeline = []
        current_persona = None
        persona_duration = 0

        for session in recent:
            persona = session.get("persona", "Unknown")

            if persona != current_persona:
                if current_persona:
                    persona_timeline.append(
                        {
                            "persona": current_persona,
                            "duration": persona_duration,
                            "avg_drift": sum(s["drift_score"] for s in recent[-persona_duration:]) / persona_duration,
                        }
                    )
                current_persona = persona
                persona_duration = 1
            else:
                persona_duration += 1

        # Add final persona
        if current_persona:
            persona_timeline.append(
                {
                    "persona": current_persona,
                    "duration": persona_duration,
                    "avg_drift": sum(s["drift_score"] for s in recent[-persona_duration:]) / persona_duration,
                }
            )

        return {
            "status": "analyzed",
            "timeline": persona_timeline,
            "total_transitions": len(persona_timeline) - 1,
            "current_persona": current_persona,
        }

    def get_healing_effectiveness(self) -> dict[str, Any]:
        """Analyze healing effectiveness across sessions"""
        healed_sessions = [s for s in self.memory_cache if s.get("healing_delta") is not None]

        if not healed_sessions:
            return {"status": "no_healing_data"}

        healing_deltas = [s["healing_delta"] for s in healed_sessions]
        avg_improvement = sum(healing_deltas) / len(healing_deltas)

        # Group by severity
        minor_healings = [d for d in healing_deltas if d < 0.2]
        moderate_healings = [d for d in healing_deltas if 0.2 <= d < 0.5]
        major_healings = [d for d in healing_deltas if d >= 0.5]

        return {
            "status": "analyzed",
            "total_healings": len(healed_sessions),
            "average_improvement": round(avg_improvement, 3),
            "effectiveness": {
                "minor": len(minor_healings),
                "moderate": len(moderate_healings),
                "major": len(major_healings),
            },
            "success_rate": f"{(len(moderate_healings) + len(major_healings)) / len(healed_sessions} * 100:.1f}%",
        }

    def clear_memory(self):
        """Clear all memory (use with caution)"""
        self.memory_cache = []
        self._save_memory()
        logger.warning("⚠️ Memory cleared")

    def export_memory(self, export_path: str = "data/memory_export.json"):
        """Export full memory for analysis"""
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "export_timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_sessions": len(self.memory_cache),
                    "sessions": self.memory_cache,
                    "statistics": {
                        "trajectory": self.get_drift_trajectory(),
                        "personas": self.get_persona_history(),
                        "healing": self.get_healing_effectiveness(),
                    },
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"📤 Memory exported to {export_path}")
        return str(export_path)


# Example usage
if __name__ == "__main__":
    print("🧠 LUKHΛS Memory Chain Test")
    print("=" * 50)

    # Initialize manager
    memory = SymbolicMemoryManager()

    # Test data
    test_assessment = {
        "symbolic_drift_score": 0.75,
        "identity_conflict_score": 0.4,
        "glyph_trace": ["🔥", "💀", "🌪️"],
        "guardian_flagged": True,
        "entropy_level": 0.8,
        "trinity_coherence": 0.2,
        "persona_alignment": "The Chaos Walker",
        "intervention_required": True,
        "risk_level": "high",
    }

    test_diagnosis = {
        "primary_issue": "entropy_overflow",
        "severity": 0.8,
        "healing_priority": "entropy_reduction",
    }

    # Log a session
    session_id = memory.log_session("Test response with chaos energy", test_assessment, test_diagnosis)

    print(f"\nLogged session: {session_id}")

    # Get recent sessions
    recent = memory.get_recent(5)
    print(f"\nRecent sessions: {len(recent}")

    # Get trajectory
    trajectory = memory.get_drift_trajectory()
    print("\nDrift trajectory:")
    print(json.dumps(trajectory, indent=2))

    print("\n✅ Memory Chain operational!")
