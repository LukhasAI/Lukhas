"""Operational ethics swarm colony engine for Guardian integrations."""
from __future__ import annotations

import hashlib
import logging
import statistics
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Deque
from collections.abc import Iterable

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


class EthicsSwarmColony:
    """Adaptive ethics swarm colony used by Guardian integrations."""

    # ΛTAG: ethics_swarm_colony

    def __init__(
        self,
        *,
        max_history: int = 64,
        drift_threshold: float = 0.62,
        escalation_penalty: float = 0.12,
    ) -> None:
        self._signals: Deque[EthicalSignal] = deque(maxlen=max_history)
        self.drift_threshold = max(0.0, min(drift_threshold, 1.0))
        self.escalation_penalty = escalation_penalty
        # ✅ TODO: integrate Guardian feedback scores for adaptive drift thresholds.

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

    def _decision_floor(
        self, decision_type: EthicalDecisionType, risk_level: str
    ) -> float:
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

        positives = [signal.value * signal.weight for signal in self._signals if signal.value >= 0.5]
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
    "EthicalDecisionRequest",
    "EthicalDecisionResponse",
    "EthicalDecisionType",
    "EthicalSignal",
    "EthicsSwarmColony",
]
