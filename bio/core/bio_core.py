"""BioCore symbolic integration module for bio-inspired regulation."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)

ClockFn = Callable[[], datetime]


@dataclass
class EnergyBudget:
    """Container for energy budgeting metrics."""

    reserve: float
    homeostatic_target: float
    homeostatic_pressure: float


@dataclass
class CircadianState:
    """Represents circadian rhythm metrics."""

    phase: float
    amplitude: float
    last_update: datetime


@dataclass
class EmotionalSnapshot:
    """Snapshot of emotional state exported to other subsystems."""

    valence: float
    arousal: float
    dominance: float
    driftScore: float
    affect_delta: dict[str, float]
    energy_budget: EnergyBudget
    circadian: CircadianState
    timestamp: datetime

    def as_dict(self) -> dict[str, Any]:
        """Return a serialisable representation."""
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "driftScore": self.driftScore,
            "affect_delta": self.affect_delta,
            "energy_budget": {
                "reserve": self.energy_budget.reserve,
                "homeostatic_target": self.energy_budget.homeostatic_target,
                "homeostatic_pressure": self.energy_budget.homeostatic_pressure,
            },
            "circadian": {
                "phase": self.circadian.phase,
                "amplitude": self.circadian.amplitude,
                "last_update": self.circadian.last_update,
            },
            "timestamp": self.timestamp,
        }


class BioCore:
    """Bio-inspired regulatory core providing emotional and energy context."""

    def __init__(
        self,
        *,
        memory_manager: Any | None = None,
        config: dict[str, Any] | None = None,
        clock: ClockFn | None = None,
    ) -> None:
        self.memory_manager = memory_manager
        self.config = config or {}
        self._clock: ClockFn = clock or (lambda: datetime.now(timezone.utc))
        self._last_update: datetime = self._clock()

        # ΛTAG: affect_delta - maintain emotional shift for symbolic auditing
        self._emotional_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        self._previous_emotional_state = self._emotional_state.copy()
        self._affect_delta = {"valence_delta": 0.0, "arousal_delta": 0.0, "dominance_delta": 0.0}
        # ΛTAG: driftScore - exponential moving average for emotional drift
        self._drift_score = 0.0

        # Energy budgeting configuration
        self._energy_reserve = float(self.config.get("initial_energy", 0.75))
        self._homeostatic_target = float(self.config.get("homeostasis_target", 0.72))
        self._homeostatic_pressure = 0.0
        self._circadian_phase = 0.0
        self._circadian_amplitude = float(self.config.get("circadian_amplitude", 0.35))
        self._circadian_offset = float(self.config.get("circadian_offset", 0.0))

        # ΛTAG: symbolic_trace - log symbolic events for tracing
        self._symbolic_trace: list[dict[str, Any]] = []
        self._trace_limit = int(self.config.get("trace_limit", 256))

        self._abas_hub: Any | None = None
        self._is_initialized = False

        logger.info("BioCore initialized with energy reserve %.2f", self._energy_reserve)
        self._record_trace("init", {"energy_reserve": self._energy_reserve})

        # TODO: Integrate endocrine feedback loops via endocrine module once available.

    async def initialize(self) -> bool:
        """Asynchronously initialize the bio core."""
        if self._is_initialized:
            return True

        # Prime the circadian rhythm
        self.step()
        self._is_initialized = True
        self._record_trace("initialize", {"status": "complete"})
        return True

    def integrate_with_abas(self, abas_hub: Any) -> None:
        """Connect BioCore to the ABAS integration hub."""
        self._abas_hub = abas_hub
        if hasattr(abas_hub, "attach_bio_core"):
            abas_hub.attach_bio_core(self)
        self._record_trace("abas_integrated", {"attached": bool(abas_hub)})

    def step(self, cognitive_load: float = 0.0) -> EmotionalSnapshot:
        """Advance internal state and return the latest emotional snapshot."""
        now = self._clock()
        self._update_energy_budget(now, cognitive_load)
        self._last_update = now
        snapshot = self._build_snapshot(now)
        self._record_trace(
            "step",
            {
                "cognitive_load": cognitive_load,
                "energy_reserve": snapshot.energy_budget.reserve,
                "driftScore": snapshot.driftScore,
            },
        )
        self._notify_abas(snapshot)
        return snapshot

    def record_emotion(
        self,
        *,
        valence: float,
        arousal: float,
        dominance: float | None = None,
        source: str = "direct",
    ) -> EmotionalSnapshot:
        """Record a new emotional state and propagate to integrations."""
        dominance_value = self._emotional_state["dominance"] if dominance is None else dominance
        self._apply_emotional_state(
            valence,
            arousal,
            dominance_value,
            propagate=True,
            source=source,
        )
        return self.step()

    def process_emotional_signal(self, signal: dict[str, Any]) -> EmotionalSnapshot:
        """Process an incoming emotional signal from ABAS or other systems."""
        valence = float(signal.get("valence", self._emotional_state["valence"]))
        arousal = float(signal.get("arousal", self._emotional_state["arousal"]))
        dominance = float(signal.get("dominance", self._emotional_state["dominance"]))
        source = signal.get("source", "signal")
        cognitive_load = float(signal.get("cognitive_load", 0.0))

        self._apply_emotional_state(
            valence,
            arousal,
            dominance,
            propagate=False,
            source=source,
        )
        # Update energetic context with the provided cognitive load
        return self.step(cognitive_load=cognitive_load)

    def sync_from_abas(self, emotional_state: dict[str, Any]) -> EmotionalSnapshot:
        """Synchronize state using ABAS-provided emotional metrics."""
        valence = float(emotional_state.get("valence", self._emotional_state["valence"]))
        arousal = float(emotional_state.get("arousal", self._emotional_state["arousal"]))
        dominance = float(emotional_state.get("dominance", self._emotional_state["dominance"]))
        return self._apply_emotional_state(
            valence,
            arousal,
            dominance,
            propagate=False,
            source="abas",
        )

    def get_emotional_state(self) -> dict[str, Any]:
        """Return the latest emotional snapshot as a dictionary."""
        return self._build_snapshot(self._last_update).as_dict()

    def get_symbolic_trace(self) -> list[dict[str, Any]]:
        """Return a copy of the symbolic trace buffer."""
        return list(self._symbolic_trace)

    # Internal helpers -------------------------------------------------

    def _apply_emotional_state(
        self,
        valence: float,
        arousal: float,
        dominance: float,
        *,
        propagate: bool,
        source: str,
    ) -> EmotionalSnapshot:
        bounded_valence = max(-1.0, min(1.0, valence))
        bounded_arousal = max(0.0, min(1.0, arousal))
        bounded_dominance = max(0.0, min(1.0, dominance))

        prev_state = self._emotional_state.copy()
        self._previous_emotional_state = prev_state
        self._emotional_state = {
            "valence": bounded_valence,
            "arousal": bounded_arousal,
            "dominance": bounded_dominance,
        }
        self._affect_delta = {
            "valence_delta": bounded_valence - prev_state["valence"],
            "arousal_delta": bounded_arousal - prev_state["arousal"],
            "dominance_delta": bounded_dominance - prev_state["dominance"],
        }
        self._drift_score = self._update_drift_score()

        snapshot = self._build_snapshot(self._clock())
        self._record_trace(
            "emotion_update",
            {
                "source": source,
                "valence": bounded_valence,
                "arousal": bounded_arousal,
                "dominance": bounded_dominance,
                "affect_delta": self._affect_delta.copy(),
                "driftScore": self._drift_score,
            },
        )

        if propagate:
            self._notify_abas(snapshot)

        return snapshot

    def _update_drift_score(self) -> float:
        delta_valence = abs(self._affect_delta["valence_delta"])
        delta_arousal = abs(self._affect_delta["arousal_delta"])
        instantaneous_drift = (delta_valence + delta_arousal) / 2.0
        smoothing_factor = float(self.config.get("drift_smoothing", 0.25))
        return (1.0 - smoothing_factor) * self._drift_score + smoothing_factor * instantaneous_drift

    def _update_energy_budget(self, now: datetime, cognitive_load: float) -> None:
        hours = self._hours_since_midnight(now)
        circadian_phase = ((hours / 24.0) + self._circadian_offset) % 1.0
        circadian_wave = math.cos(2 * math.pi * (circadian_phase - 0.5))
        self._circadian_phase = circadian_phase

        # Move reserve toward circadian target while accounting for cognitive load
        target = self._homeostatic_target + self._circadian_amplitude * circadian_wave
        adjustment_rate = float(self.config.get("energy_adjustment_rate", 0.1))
        self._energy_reserve += adjustment_rate * (target - self._energy_reserve)
        load_penalty = max(0.0, min(1.0, abs(cognitive_load) * 0.1))
        self._energy_reserve = self._clamp(self._energy_reserve - load_penalty, 0.0, 1.0)

        self._homeostatic_pressure = target - self._energy_reserve
        logger.debug(
            "BioCore energy update - reserve=%.3f target=%.3f load=%.3f",
            self._energy_reserve,
            target,
            cognitive_load,
        )

    def _build_snapshot(self, timestamp: datetime) -> EmotionalSnapshot:
        energy_budget = EnergyBudget(
            reserve=self._energy_reserve,
            homeostatic_target=self._homeostatic_target,
            homeostatic_pressure=self._homeostatic_pressure,
        )
        circadian = CircadianState(
            phase=self._circadian_phase,
            amplitude=self._circadian_amplitude,
            last_update=timestamp,
        )
        return EmotionalSnapshot(
            valence=self._emotional_state["valence"],
            arousal=self._emotional_state["arousal"],
            dominance=self._emotional_state["dominance"],
            driftScore=self._drift_score,
            affect_delta=self._affect_delta.copy(),
            energy_budget=energy_budget,
            circadian=circadian,
            timestamp=timestamp,
        )

    def _notify_abas(self, snapshot: EmotionalSnapshot) -> None:
        if self._abas_hub is None:
            return
        if hasattr(self._abas_hub, "receive_bio_state"):
            self._abas_hub.receive_bio_state(snapshot.as_dict())

    def _record_trace(self, event: str, payload: dict[str, Any]) -> None:
        trace_entry = {"event": event, "payload": payload, "timestamp": self._clock()}
        self._symbolic_trace.append(trace_entry)
        if len(self._symbolic_trace) > self._trace_limit:
            self._symbolic_trace = self._symbolic_trace[-self._trace_limit :]

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _hours_since_midnight(moment: datetime) -> float:
        local = moment.astimezone(timezone.utc)
        return (
            local.hour
            + local.minute / 60.0
            + local.second / 3600.0
            + local.microsecond / 3_600_000_000.0
        )
