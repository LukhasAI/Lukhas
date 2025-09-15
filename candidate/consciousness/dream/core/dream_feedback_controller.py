# ΛFILE_INDEX
# ΛORIGIN_AGENT: Jules-03
# ΛPHASE: 4
# ΛTAG: dream_feedback_2.0, symbolic_redirect, drift_snapshot

"""
Dream Feedback Controller 2.0

Purpose:
- Monitors driftScore across sessions
- Detects threshold-crossing drift events
- Triggers dream redirection using stored symbolic snapshots
"""
from collections.abc import Mapping
from typing import Any, Optional

from candidate.core.common import get_logger
from dream.core.dream_snapshot import DreamSnapshotStore
from lukhas.memory.emotional import EmotionalMemory

logger = get_logger(__name__)


class DreamFeedbackController:
    def __init__(self, drift_threshold=0.22):
        self.drift_threshold = drift_threshold
        self.snapshot_store = DreamSnapshotStore()
        self.emotional_memory = EmotionalMemory()

    def check_drift_event(self, drift_score: float, current_emotion) -> bool:
        self.emotional_memory.affect_delta("dream_feedback", current_emotion)
        return drift_score >= self.drift_threshold

    def trigger_redirection(self, user_id: str, current_emotion: dict) -> dict:
        """Fetches best-fit past snapshot and proposes symbolic redirect."""
        candidates = self.snapshot_store.get_recent_snapshots(user_id)
        best_match, score_details = self._select_redirect(candidates, current_emotion)

        if best_match:
            logger.debug(
                "ΛTAG:symbolic_redirect dream_id=%s score=%.3f emotion=%.3f recency=%.3f stability=%.3f",
                best_match.get("dream_id", "<unknown>"),
                score_details["combined"],
                score_details["emotion_similarity"],
                score_details["recency_weight"],
                score_details["stability_weight"],
            )
        else:
            logger.debug(
                "ΛTAG:symbolic_redirect no viable snapshot match for user_id=%s",
                user_id,
            )

        symbolic_reason = (
            "High driftScore detected – converging via dream memory reentry"
            if best_match
            else "High driftScore detected – symbolic redirect unavailable"
        )
        return {
            "action": "redirect",
            "target_snapshot": best_match,
            "symbolic_reason": symbolic_reason,
        }

    def _select_redirect(
        self,
        snapshots: list[dict[str, Any]],
        emotion: Optional[Mapping[str, Any]],
    ) -> tuple[Optional[dict[str, Any]], dict[str, float]]:
        if not snapshots:
            return None, {
                "combined": 0.0,
                "emotion_similarity": 0.0,
                "recency_weight": 0.0,
                "stability_weight": 0.0,
            }

        best_snapshot: Optional[dict[str, Any]] = None
        best_score = float("-inf")
        best_details: dict[str, float] = {}

        for index, snapshot in enumerate(snapshots):
            score, details = self._score_snapshot(snapshot, emotion, index)
            if score > best_score:
                best_score = score
                best_snapshot = snapshot
                best_details = details

        return best_snapshot, best_details

    def _score_snapshot(
        self,
        snapshot: Mapping[str, Any],
        emotion: Optional[Mapping[str, Any]],
        position: int,
    ) -> tuple[float, dict[str, float]]:
        emotion_similarity = self._compute_emotion_similarity(
            snapshot.get("emotional_context"),
            emotion,
        )
        recency_weight = 1.0 / (position + 1)
        stability_weight = self._compute_stability_weight(snapshot)

        # ΛTAG: symbolic_match_score
        combined = (
            (emotion_similarity * 0.65)
            + (recency_weight * 0.25)
            + (stability_weight * 0.10)
        )

        details = {
            "combined": combined,
            "emotion_similarity": emotion_similarity,
            "recency_weight": recency_weight,
            "stability_weight": stability_weight,
        }
        return combined, details

    def _compute_emotion_similarity(
        self,
        snapshot_emotion: Any,
        current_emotion: Optional[Mapping[str, Any]],
    ) -> float:
        snapshot_map = self._normalize_emotion_map(snapshot_emotion)
        current_map = self._normalize_emotion_map(current_emotion)

        if not snapshot_map or not current_map:
            return 0.0

        dimensions = set(snapshot_map) | set(current_map)
        overlap = sum(
            min(snapshot_map.get(dimension, 0.0), current_map.get(dimension, 0.0))
            for dimension in dimensions
        )
        total = sum(
            max(snapshot_map.get(dimension, 0.0), current_map.get(dimension, 0.0))
            for dimension in dimensions
        )

        if total == 0:
            return 0.0

        similarity = overlap / total
        return max(0.0, min(similarity, 1.0))

    def _compute_stability_weight(self, snapshot: Mapping[str, Any]) -> float:
        drift_value = snapshot.get("driftScore", snapshot.get("drift_score"))
        try:
            drift_numeric = float(drift_value)
        except (TypeError, ValueError):
            drift_numeric = 0.0

        drift_numeric = max(0.0, min(drift_numeric, 1.0))
        return 1.0 - drift_numeric  # ΛTAG: driftScore

    def _normalize_emotion_map(self, emotion: Any) -> dict[str, float]:
        if not emotion:
            return {}

        if isinstance(emotion, Mapping):
            if "dimensions" in emotion and isinstance(emotion["dimensions"], Mapping):
                base = emotion["dimensions"]
            elif "values" in emotion and isinstance(emotion["values"], Mapping):
                base = emotion["values"]
            else:
                base = emotion

            normalized: dict[str, float] = {}
            for key, value in base.items():
                if isinstance(value, (int, float)):
                    normalized[str(key)] = float(value)

            if not normalized and isinstance(emotion.get("dominant"), str):
                dominant_intensity = emotion.get("intensity", 1.0)
                if isinstance(dominant_intensity, (int, float)):
                    normalized[str(emotion["dominant"])] = float(dominant_intensity)
                else:
                    normalized[str(emotion["dominant"])] = 1.0

            return normalized

        if isinstance(emotion, list):
            return {str(item): 1.0 for item in emotion if isinstance(item, str)}

        if isinstance(emotion, str):
            return {emotion: 1.0}

        return {}
