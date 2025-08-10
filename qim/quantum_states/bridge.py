from __future__ import annotations

# ΛORIGIN_AGENT: CODEX-01
# ΛTASK_ID: C-08
# ΛCOMMIT_WINDOW: postO3-infra-phase2
# ΛPROVED_BY: Human Overseer (Gonzalo)
# ΛUDIT: Emotion-aware collapse hooks implementation
"""Emotion-aware collapse hooks for symbolic cognition."""


from datetime import datetime
from pathlib import Path

import structlog

# TAG:qim
# TAG:quantum_states
# TAG:neuroplastic
# TAG:colony


log = structlog.get_logger(__name__)

# Metrics tracked across collapse events
ΛDRIFT_SCORE: float = 0.0
ΛENTROPY_DELTA: float = 0.0
ΛECHO_CHAIN: list[str] = []

DRIFT_LOG_PATH = Path("ΛDRIFT_LOG.md")


def _append_log(event: str, drift: float, entropy: float) -> None:
    DRIFT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DRIFT_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(
            f"{datetime.utcnow().isoformat()} "
            f"event={event} drift={drift} entropy={entropy}\n"
        )


def record_collapse(event: str, drift: float, entropy: float) -> None:
    """Record a collapse event with emotion-aware metrics."""
    global ΛDRIFT_SCORE, ΛENTROPY_DELTA
    ΛDRIFT_SCORE += drift
    ΛENTROPY_DELTA += entropy
    ΛECHO_CHAIN.append(event)
    _append_log(event, drift, entropy)
    log.info(
        "collapse.record",
        event=event,
        drift=drift,
        entropy=entropy,
        ΛDRIFT_SCORE=ΛDRIFT_SCORE,
        ΛENTROPY_DELTA=ΛENTROPY_DELTA,
        echo_chain_length=len(ΛECHO_CHAIN),
    )


def get_metrics() -> dict:
    """Return current collapse metrics."""
    return {
        "ΛDRIFT_SCORE": ΛDRIFT_SCORE,
        "ΛENTROPY_DELTA": ΛENTROPY_DELTA,
        "ΛECHO_CHAIN": list(ΛECHO_CHAIN),
    }


class CollapseBridge:
    """Bridge class for collapse event coordination and monitoring."""

    def __init__(self):
        self.active_events = []
        self.metrics_history = []

    def record_event(self, event: str, drift: float, entropy: float) -> None:
        """Record a collapse event through the bridge."""
        record_collapse(event, drift, entropy)
        self.active_events.append(
            {
                "event": event,
                "drift": drift,
                "entropy": entropy,
                "timestamp": datetime.utcnow(),
            }
        )

    def get_current_metrics(self) -> dict:
        """Get current collapse metrics through bridge interface."""
        return get_metrics()

    def clear_events(self) -> None:
        """Clear active events."""
        self.active_events.clear()


__all__ = ["record_collapse", "get_metrics", "CollapseBridge"]
