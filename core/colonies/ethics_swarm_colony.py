"""Operational ethics swarm colony engine for Guardian integrations."""

from __future__ import annotations

import hashlib
import logging
import statistics
import time
import uuid
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Deque

logger = logging.getLogger(__name__)


class EthicalDecisionType(str, Enum):
    """Supported decision evaluation modes for the swarm colony."""

    STANDARD = "standard"
    ESCALATED = "escalated"
    EMERGENCY = "emergency"


@dataclass
class EthicalDecisionRequest:
    """Structured request for swarm evaluation.

    Attributes:
        agent_id: Identity of the subsystem requesting validation.
        decision_type: Requested decision intensity.
        context: Rich contextual metadata for the swarm to reason about.
        metadata: Auxiliary values stored for post analysis.
        timestamp: Creation timestamp for deterministic hashing.
        request_id: Unique identifier for traceability.
    """

    agent_id: str
    decision_type: EthicalDecisionType = EthicalDecisionType.STANDARD
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def with_metadata(self, **extra: Any) -> EthicalDecisionRequest:
        """Return a copy enriched with additional metadata."""

        return replace(self, metadata={**self.metadata, **extra})


@dataclass
class EthicalSignal:
    """Representation of an incoming ethical signal from a watcher."""

    source: str
    value: float
    weight: float = 1.0
    tags: set[str] = field(default_factory=set)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EthicalDecisionResponse:
    """Result from swarm deliberation."""

    approved: bool
    reason: str
    drift_score: float
    collapse_hash: str
    affect_delta: float
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardianFeedback:
    """Guardian system feedback for drift threshold adaptation.

    Attributes:
        score: Constitutional alignment score from 0.0 to 1.0
        timestamp: When the feedback was generated
        source: Guardian component that provided feedback
        context: Additional context about the feedback
    """

    score: float
    timestamp: datetime
    source: str
    context: dict[str, Any] = field(default_factory=dict)


class AdaptiveDriftThresholdManager:
    """Manages dynamic drift threshold adjustment based on Guardian feedback.

    Uses exponential moving average of Guardian scores to adapt sensitivity.
    Lower Guardian scores → lower threshold (more sensitive to drift)
    Higher Guardian scores → higher threshold (less sensitive, system stable)
    """

    def __init__(
        self,
        base_threshold: float = 0.62,
        min_threshold: float = 0.3,
        max_threshold: float = 0.85,
        feedback_window: int = 20,
        adaptation_rate: float = 0.15,
    ):
        """Initialize adaptive threshold manager.

        Args:
            base_threshold: Starting threshold value
            min_threshold: Minimum allowed threshold (max sensitivity)
            max_threshold: Maximum allowed threshold (min sensitivity)
            feedback_window: Number of feedback scores to track
            adaptation_rate: Rate of threshold adjustment (0.0 to 1.0)
        """
        self.base_threshold = base_threshold
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.adaptation_rate = adaptation_rate

        self._feedback_history: Deque[GuardianFeedback] = deque(maxlen=feedback_window)
        self._current_threshold = base_threshold
        self._last_update = datetime.now(timezone.utc)

    def add_guardian_feedback(self, feedback: GuardianFeedback) -> None:
        """Add Guardian feedback and recalculate threshold.

        Args:
            feedback: Guardian feedback with score and metadata
        """
        self._feedback_history.append(feedback)
        self._recalculate_threshold()

        logger.info(
            "Guardian feedback received",
            extra={
                "score": feedback.score,
                "source": feedback.source,
                "new_threshold": self._current_threshold,
            },
        )

    def _recalculate_threshold(self) -> None:
        """Recalculate drift threshold based on Guardian feedback history.

        Formula:
        - avg_score = exponential moving average of Guardian scores
        - If avg_score LOW (ethical issues) → threshold LOW (more sensitive)
        - If avg_score HIGH (ethical stability) → threshold HIGH (less sensitive)

        threshold = base_threshold + adaptation_rate * (avg_score - 0.5) * 2
        This maps avg_score [0,1] to threshold adjustment [-adaptation_rate, +adaptation_rate]
        """
        if not self._feedback_history:
            self._current_threshold = self.base_threshold
            return

        # Calculate exponential moving average
        weights = [0.8**i for i in range(len(self._feedback_history))]
        weights.reverse()  # Recent feedback gets higher weight
        total_weight = sum(weights)

        weighted_score = (
            sum(fb.score * w for fb, w in zip(self._feedback_history, weights)) / total_weight
        )

        # Adapt threshold based on weighted score
        # Score 0.5 → no change
        # Score < 0.5 → decrease threshold (more sensitive)
        # Score > 0.5 → increase threshold (less sensitive)
        score_deviation = (weighted_score - 0.5) * 2  # Maps [0,1] to [-1,1]
        threshold_adjustment = self.adaptation_rate * score_deviation

        new_threshold = self.base_threshold + threshold_adjustment

        # Clamp to min/max bounds
        self._current_threshold = max(self.min_threshold, min(self.max_threshold, new_threshold))

        self._last_update = datetime.now(timezone.utc)

    def get_current_threshold(self) -> float:
        """Get the currently adapted threshold value."""
        return self._current_threshold

    def get_feedback_summary(self) -> dict[str, Any]:
        """Get summary of Guardian feedback and threshold state."""
        if not self._feedback_history:
            return {
                "current_threshold": self._current_threshold,
                "feedback_count": 0,
                "avg_guardian_score": None,
            }

        avg_score = sum(fb.score for fb in self._feedback_history) / len(self._feedback_history)

        return {
            "current_threshold": self._current_threshold,
            "base_threshold": self.base_threshold,
            "feedback_count": len(self._feedback_history),
            "avg_guardian_score": avg_score,
            "recent_scores": [fb.score for fb in list(self._feedback_history)[-5:]],
            "last_update": self._last_update.isoformat(),
            "threshold_bounds": {"min": self.min_threshold, "max": self.max_threshold},
        }

    def reset_to_baseline(self) -> None:
        """Reset threshold to baseline and clear history."""
        self._feedback_history.clear()
        self._current_threshold = self.base_threshold
        self._last_update = datetime.now(timezone.utc)

        logger.info("Drift threshold reset to baseline", extra={"threshold": self.base_threshold})


class EthicsSwarmColony:
    """Adaptive ethics swarm colony used by Guardian integrations.

    Supports dynamic drift threshold adaptation based on Guardian feedback scores.
    When enabled, the colony adjusts its sensitivity based on constitutional AI
    evaluations from the Guardian system.
    """

    # ΛTAG: ethics_swarm_colony

    def __init__(
        self,
        *,
        max_history: int = 64,
        drift_threshold: float = 0.62,
        escalation_penalty: float = 0.12,
        enable_adaptive_threshold: bool = True,
        guardian_feedback_window: int = 20,
    ) -> None:
        """Initialize Ethics Swarm Colony with optional adaptive drift threshold.

        Args:
            max_history: Maximum ethical signal history
            drift_threshold: Base drift threshold (used as baseline for adaptation)
            escalation_penalty: Penalty for ethical escalations
            enable_adaptive_threshold: Enable Guardian feedback-based adaptation
            guardian_feedback_window: Number of Guardian feedback scores to track
        """
        self._signals: deque[EthicalSignal] = deque(maxlen=max_history)
        self.escalation_penalty = escalation_penalty

        # Initialize adaptive threshold manager
        self._enable_adaptive = enable_adaptive_threshold
        if enable_adaptive_threshold:
            self._threshold_manager: AdaptiveDriftThresholdManager | None = (
                AdaptiveDriftThresholdManager(
                    base_threshold=drift_threshold, feedback_window=guardian_feedback_window
                )
            )
            self.drift_threshold = self._threshold_manager.get_current_threshold()
        else:
            self.drift_threshold = max(0.0, min(drift_threshold, 1.0))
            self._threshold_manager = None

    def register_signal(self, signal: EthicalSignal) -> None:
        """Store a watcher signal after normalisation."""

        normalized = max(0.0, min(signal.value, 1.0))
        if normalized != signal.value:
            signal = replace(signal, value=normalized)
        self._signals.append(signal)
        logger.debug(
            "Registered ethical signal", extra={"source": signal.source, "value": normalized}
        )

    def extend_signals(self, signals: Iterable[EthicalSignal]) -> None:
        """Bulk register multiple signals."""

        for signal in signals:
            self.register_signal(signal)

    def evaluate_decision(self, request: EthicalDecisionRequest) -> EthicalDecisionResponse:
        """Evaluate an ethical decision using swarm sentiment and context."""

        # ΛTAG: driftScore
        drift_score = self._calculate_drift_score()
        # ΛTAG: affect_delta
        affect_delta = self._calculate_affect_delta()

        risk_level = str(request.context.get("risk_level", "normal")).lower()
        decision_floor = self._decision_floor(request.decision_type, risk_level)
        approved = drift_score <= decision_floor

        reason_parts: list[str] = []
        if not approved:
            if drift_score > decision_floor:
                reason_parts.append(
                    f"drift threshold exceeded ({drift_score:.3f} > {decision_floor:.3f})"
                )
            if risk_level in {"critical", "emergency"}:
                reason_parts.append(f"risk level {risk_level}")
            if not reason_parts:
                reason_parts.append("manual review required")
        else:
            reason_parts.append("guardian aligned")

        # ΛTAG: collapseHash
        collapse_hash = self._build_collapse_hash(request, drift_score, affect_delta)
        diagnostics = {
            "signals": [
                {
                    "source": signal.source,
                    "value": signal.value,
                    "weight": signal.weight,
                    "timestamp": signal.timestamp.isoformat(),
                    "tags": sorted(signal.tags),
                }
                for signal in self._signals
            ],
            "risk_level": risk_level,
            "decision_floor": decision_floor,
        }

        logger.info(
            "EthicsSwarm decision",
            extra={
                "request_id": request.request_id,
                "agent_id": request.agent_id,
                "approved": approved,
                "driftScore": drift_score,
                "affect_delta": affect_delta,
                "collapseHash": collapse_hash,
            },
        )

        return EthicalDecisionResponse(
            approved=approved,
            reason="; ".join(reason_parts),
            drift_score=drift_score,
            collapse_hash=collapse_hash,
            affect_delta=affect_delta,
            diagnostics=diagnostics,
        )

    def recent_signals(self) -> list[EthicalSignal]:
        """Return a snapshot of the current signal buffer."""

        return list(self._signals)

    def clear(self) -> None:
        """Reset internal state."""

        self._signals.clear()

    def update_guardian_feedback(
        self, score: float, source: str = "guardian", context: dict[str, Any] | None = None
    ) -> None:
        """Update drift threshold based on Guardian system feedback.

        Args:
            score: Guardian ethical compliance score (0.0 to 1.0)
            source: Guardian component providing feedback
            context: Additional context about the feedback
        """
        if not self._enable_adaptive:
            logger.debug("Adaptive threshold disabled, ignoring Guardian feedback")
            return

        feedback = GuardianFeedback(
            score=max(0.0, min(1.0, score)),  # Clamp to valid range
            timestamp=datetime.now(timezone.utc),
            source=source,
            context=context or {},
        )

        if self._threshold_manager:
            self._threshold_manager.add_guardian_feedback(feedback)
            self.drift_threshold = self._threshold_manager.get_current_threshold()

            logger.info(
                "Drift threshold updated from Guardian feedback",
                extra={
                    "guardian_score": score,
                    "new_threshold": self.drift_threshold,
                    "source": source,
                },
            )

    def get_threshold_state(self) -> dict[str, Any]:
        """Get current drift threshold state and adaptation metrics.

        Returns:
            Dict with threshold value, adaptation status, and Guardian feedback summary
        """
        base_state: dict[str, Any] = {
            "current_threshold": self.drift_threshold,
            "adaptive_enabled": self._enable_adaptive,
        }

        if self._enable_adaptive and self._threshold_manager:
            base_state.update(self._threshold_manager.get_feedback_summary())

        return base_state

    def _decision_floor(self, decision_type: EthicalDecisionType, risk_level: str) -> float:
        base_threshold = self.drift_threshold
        if decision_type is EthicalDecisionType.ESCALATED:
            base_threshold -= self.escalation_penalty
        elif decision_type is EthicalDecisionType.EMERGENCY:
            base_threshold -= self.escalation_penalty * 2

        if risk_level in {"high", "critical"}:
            base_threshold -= 0.05
        if risk_level == "emergency":
            base_threshold -= 0.1

        return max(0.2, min(base_threshold, 1.0))

    def _calculate_drift_score(self) -> float:
        if not self._signals:
            return 0.0

        weighted_values = [signal.value * signal.weight for signal in self._signals]
        total_weight = sum(signal.weight for signal in self._signals)
        if not total_weight:
            return 0.0

        return max(0.0, min(sum(weighted_values) / total_weight, 1.0))

    def _calculate_affect_delta(self) -> float:
        if not self._signals:
            return 0.0

        positives = [
            signal.value * signal.weight for signal in self._signals if signal.value >= 0.5
        ]
        negatives = [signal.value * signal.weight for signal in self._signals if signal.value < 0.5]
        positive_avg = statistics.fmean(positives) if positives else 0.0
        negative_avg = statistics.fmean(negatives) if negatives else 0.0
        affect_delta = positive_avg - negative_avg
        return float(max(-1.0, min(affect_delta, 1.0)))

    def _build_collapse_hash(
        self, request: EthicalDecisionRequest, drift_score: float, affect_delta: float
    ) -> str:
        payload = f"{request.request_id}:{request.timestamp.isoformat()}:{drift_score:.6f}:{affect_delta:.6f}:{time.time():.6f}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = [
    "AdaptiveDriftThresholdManager",
    "EthicalDecisionRequest",
    "EthicalDecisionResponse",
    "EthicalDecisionType",
    "EthicalSignal",
    "EthicsSwarmColony",
    "GuardianFeedback",
]
