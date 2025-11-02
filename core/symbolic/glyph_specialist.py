"""GLYPH specialist consensus evaluation utilities."""
from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

logger = logging.getLogger("Lukhas.GLYPH.Specialist")


@dataclass(frozen=True)
class GlyphSignal:
    """Represents a symbolic consciousness layer measurement."""

    layer_id: str
    driftScore: float
    affect_delta: float
    glyph_markers: Sequence[str] = field(default_factory=list)
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class GlyphConsensusResult:
    """Result of GLYPH consensus evaluation."""

    consensus: bool
    driftScore: float
    affect_delta: float
    agreement_ratio: float
    dissenting_layers: List[str]
    glyph_signature: List[str]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GlyphSpecialist:
    """Perform GLYPH-weighted consensus over consciousness layer signals."""

    def __init__(self, drift_threshold: float = 0.3) -> None:
        self.drift_threshold = drift_threshold
        self._logger = logger

    def evaluate(self, signals: Sequence[GlyphSignal]) -> GlyphConsensusResult:
        """Evaluate consensus across signals using GLYPH weighting."""
        if not signals:
            raise ValueError("signals must not be empty")

        weights = [self._compute_weight(signal) for signal in signals]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        drift_score = sum(s.driftScore * w for s, w in zip(signals, normalized_weights))
        affect_delta = sum(s.affect_delta * w for s, w in zip(signals, normalized_weights))

        dissenting_layers = [s.layer_id for s in signals if s.driftScore > self.drift_threshold]
        agreement_ratio = 1.0 - (len(dissenting_layers) / len(signals))
        glyph_signature = sorted({marker for s in signals for marker in s.glyph_markers})

        consensus = drift_score <= self.drift_threshold and not dissenting_layers

        self._logger.debug(
            "# ΛTAG: glyph_consensus -- evaluated consensus",
            extra={
                "driftScore": drift_score,
                "affect_delta": affect_delta,
                "agreement_ratio": agreement_ratio,
                "dissenting_layers": dissenting_layers,
                "glyph_signature": glyph_signature,
            },
        )

        return GlyphConsensusResult(
            consensus=consensus,
            driftScore=drift_score,
            affect_delta=affect_delta,
            agreement_ratio=agreement_ratio,
            dissenting_layers=dissenting_layers,
            glyph_signature=glyph_signature,
        )

    def _compute_weight(self, signal: GlyphSignal) -> float:
        """Compute GLYPH weighting for a signal."""
        base_weight = 1.0 + abs(signal.affect_delta)
        symbolic_weight = max(1.0, len(signal.glyph_markers) * 0.25)
        # ΛTAG: glyph_weighting
        return base_weight * symbolic_weight

    def update_threshold(self, new_threshold: float) -> None:
        """Update drift threshold used for consensus."""
        if new_threshold <= 0:
            raise ValueError("new_threshold must be positive")
        self.drift_threshold = new_threshold
        self._logger.info(
            "# ΛTAG: glyph_threshold_update -- updated drift threshold",
            extra={"drift_threshold": new_threshold},
        )
        # TODO: sync threshold to distributed GLYPH registry once service hook lands.
