import logging

logger = logging.getLogger(__name__)
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Module: snapshot_redirection_controller.py
Author: Jules 03
Date: 2025-07-18
Description: Controller to detect emotional drift in dream snapshots and redirect dream narratives.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from trace.drift_harmonizer import DriftHarmonizer
from typing import Any, Optional

import numpy as np

from dream.core.dream_snapshot import DreamSnapshotStore
from dream.stability.redirect_forecaster import RedirectForecaster
from lukhas.core.common import get_logger
from lukhas.memory.emotional import EmotionalMemory, EmotionVector

logger = get_logger(__name__)


class SnapshotRedirectionController:
    """
    Detects emotional drift in dream snapshots and redirects dream narratives.
    """

    def __init__(
        self,
        emotional_memory: EmotionalMemory,
        snapshot_store: DreamSnapshotStore,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initializes the SnapshotRedirectionController.

        Args:
            emotional_memory (EmotionalMemory): The emotional memory system.
            snapshot_store (DreamSnapshotStore): The dream snapshot store.
            config (Optional[Dict[str, Any]], optional): Configuration options. Defaults to None.
        """
        self.emotional_memory = emotional_memory
        self.snapshot_store = snapshot_store
        self.config = config or {}
        self.drift_threshold = self.config.get("drift_threshold", 0.5)
        self.redirect_log_path = Path("dream/logs/redirect_log.jsonl")
        self.redirect_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_redirects = 0
        self.redirect_buffer = self.config.get("redirect_buffer", 3)
        self.recent_redirects = []
        self.forecaster = RedirectForecaster()

    def check_and_redirect(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Checks for emotional drift and redirects the dream narrative if needed.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[Dict[str, Any]]: A new dream seed if redirection is needed, otherwise None.
        """
        if self.session_redirects > 3:
            logger.warning("Redirect overload detected. Halting redirection for this session.")
            return {
                "seed_type": "narrative_redirection",
                "narrative_name": "redirect_overload",
            }

        if len(self.recent_redirects) >= self.redirect_buffer:
            logger.info("Redirect throttle active. Skipping redirection check.")
            self.recent_redirects.pop(0)
            return None

        recent_snapshots = self.snapshot_store.get_recent_snapshots(user_id)
        if len(recent_snapshots) < 2:
            return None

        emotional_drift = self._calculate_emotional_drift(recent_snapshots)
        if emotional_drift is not None and emotional_drift > self.drift_threshold:
            self.session_redirects += 1
            self.recent_redirects.append(datetime.now(timezone.utc))
            new_narrative = self._select_new_narrative(emotional_drift)
            self._log_redirect(recent_snapshots[-1], emotional_drift, new_narrative)
            return new_narrative

        return None

    def _calculate_emotional_drift(self, snapshots: list[dict[str, Any]]) -> Optional[float]:
        """
        Calculates the emotional drift across a series of snapshots.

        Args:
            snapshots (List[Dict[str, Any]]): A list of dream snapshots.

        Returns:
            Optional[float]: The calculated emotional drift, or None if not enough data.
        """
        if len(snapshots) < 2:
            return None

        velocities = []
        for i in range(1, len(snapshots)):
            prev_snapshot = snapshots[i - 1]
            curr_snapshot = snapshots[i]

            prev_emotion = prev_snapshot.get("emotional_context", {})
            curr_emotion = curr_snapshot.get("emotional_context", {})

            if not prev_emotion or not curr_emotion:
                continue

            prev_vector = np.array(list(EmotionVector(prev_emotion.get("dimensions")).values.values()))
            curr_vector = np.array(list(EmotionVector(curr_emotion.get("dimensions")).values.values()))

            prev_timestamp_str = prev_snapshot.get("timestamp")
            curr_timestamp_str = curr_snapshot.get("timestamp")

            if not prev_timestamp_str or not curr_timestamp_str:
                continue

            prev_timestamp = datetime.fromisoformat(prev_timestamp_str).timestamp()
            curr_timestamp = datetime.fromisoformat(curr_timestamp_str).timestamp()

            time_delta = curr_timestamp - prev_timestamp
            if time_delta == 0:
                time_delta = 1  # Avoid division by zero

            velocity = np.linalg.norm(curr_vector - prev_vector) / time_delta
            velocities.append(velocity)

        return np.mean(velocities) if velocities else None

    def _select_new_narrative(self, emotional_drift: float) -> dict[str, Any]:
        """
        Selects a new dream narrative based on the emotional drift.

        Args:
            emotional_drift (float): The calculated emotional drift.

        Returns:
            Dict[str, Any]: A new dream seed.
        """
        # This is a placeholder implementation.
        # In a real implementation, we would have a more sophisticated way of
        # selecting a new narrative.
        if emotional_drift > 0.8:
            narrative_name = "gentle_descent"
        elif emotional_drift > 0.6:
            narrative_name = "calm_waters"
        else:
            narrative_name = "neutral_ground"

        return {
            "seed_type": "narrative_redirection",
            "narrative_name": narrative_name,
            "emotional_drift": emotional_drift,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _log_redirect(self, snapshot: dict[str, Any], drift_score: float, narrative: dict[str, Any]):
        """
        Logs the redirection event.

        Args:
            snapshot (Dict[str, Any]): The snapshot that triggered the redirection.
            drift_score (float): The drift score that triggered the redirection.
            narrative (Dict[str, Any]): The new narrative that was selected.
        """
        # LUKHAS_TAG: redirect_cause_logging
        emotional_delta = self.emotional_memory.affect_delta(
            "redirect",
            EmotionVector(snapshot.get("emotional_context", {}).get("dimensions")),
            self.emotional_memory.current_emotion,
        )["intensity_change"]

        severity = self.calculate_redirect_severity(drift_score, emotional_delta)
        cause = self._determine_redirect_cause(drift_score)

        snapshot_health_score = self._calculate_snapshot_health_score(drift_score, emotional_delta)

        log_entry = {
            "snapshot_id": snapshot.get("dream_id", "unknown"),
            "drift_score": drift_score,
            "redirect_triggered": True,
            "reason": "emotional velocity spike",
            "cause": cause,
            "linked_reasoning_trace": f"reasoning_trace_{datetime.now(timezone.utc).timestamp()}",
            "new_narrative": narrative,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "emotional_delta": emotional_delta,
            "snapshot_health_score": snapshot_health_score,
        }
        with open(self.redirect_log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def calculate_redirect_severity(self, drift_score: float, emotional_delta: float) -> str:
        """
        Calculates the severity of a redirect.

        Args:
            drift_score (float): The drift score that triggered the redirection.
            emotional_delta (float): The emotional delta that triggered the redirection.

        Returns:
            str: The severity of the redirect.
        """
        # LUKHAS_TAG: redirect_safety
        if drift_score > 0.8 and emotional_delta > 0.5:
            return "high"
        elif drift_score > 0.6 and emotional_delta > 0.3:
            return "medium"
        else:
            return "low"

    def _calculate_snapshot_health_score(self, drift_score: float, emotional_delta: float) -> float:
        """
        Calculates the health score of a snapshot.

        Args:
            drift_score (float): The drift score of the snapshot.
            emotional_delta (float): The emotional delta of the snapshot.

        Returns:
            float: The health score of the snapshot.
        """
        return 1.0 - (drift_score * 0.5 + emotional_delta * 0.5)

    def _determine_redirect_cause(self, drift_score: float) -> str:
        """
        Determines the cause of a redirect.

        Args:
            drift_score (float): The drift score that triggered the redirection.

        Returns:
            str: The cause of the redirect.
        """
        # LUKHAS_TAG: redirect_cause_logging
        harmonizer = DriftHarmonizer()
        harmonizer.record_drift(drift_score)
        suggestion = harmonizer.suggest_realignment()

        if "symbolic grounding" in suggestion:
            return "emotion_stagnation + symbolic friction"
        else:
            return "emotional_velocity_spike"

    def preemptive_stabilize(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Uses forecast score to proactively tune the next dream setup before drift begins.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[Dict[str, Any]]: A new dream seed if stabilization is needed, otherwise None.
        """
        recent_snapshots = self.snapshot_store.get_recent_snapshots(user_id)
        if len(recent_snapshots) < 2:
            return None

        historical_drift = [
            self._calculate_emotional_drift(recent_snapshots[: i + 1]) for i in range(1, len(recent_snapshots))
        ]
        historical_drift = [drift for drift in historical_drift if drift is not None]

        if not historical_drift:
            return None

        forecast = self.forecaster.forecast(historical_drift)
        if forecast["predicted_redirect"]:
            new_narrative = self._select_new_narrative(forecast["forecast_score"])
            self._log_symbolic_commentary(forecast["forecast_score"], new_narrative)
            return new_narrative

        return None

    def _log_symbolic_commentary(self, drift_score: float, narrative: dict[str, Any]):
        """
        Logs the symbolic commentary for a redirect.

        Args:
            drift_score (float): The drift score that triggered the redirection.
            narrative (Dict[str, Any]): The new narrative that was selected.
        """
        commentary = f"This redirection was predicted due to compounding emotional drift (Δ={drift_score:.2f}) and entropy rise. Stabilization is advised."
        with open("dream/logs/redirect_reasoning_commentary.log", "a") as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {commentary}\n")
