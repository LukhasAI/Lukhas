"""
LUKHAS AI Bio Module - Oscillator
Consolidated from 9 variants
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from candidate.utils.time import utc_now

__module__ = "bio.oscillator"
__triad__ = "⚛️🧠🛡️"


def _ensure_utc(timestamp: Optional[datetime] = None) -> datetime:
    """Return a timezone-aware UTC timestamp.

    Some legacy oscillators were storing naive ``datetime`` objects which
    created inconsistencies when coordinating cross-colony bio rhythms.
    This helper guarantees every timestamp recorded by the oscillators is
    normalized to UTC.  It also supports providing a pre-existing timestamp
    (for replay or deterministic testing) and upgrades it to UTC when needed.
    """

    candidate_timestamp = timestamp or utc_now()
    if candidate_timestamp.tzinfo is None:
        # ΛTAG: utc_enforcement
        return candidate_timestamp.replace(tzinfo=timezone.utc)
    return candidate_timestamp.astimezone(timezone.utc)


@dataclass
class OscillatorConfig:
    """Configuration for bio oscillators"""

    frequency: float = 1.0
    amplitude: float = 1.0
    phase: float = 0.0
    enabled: bool = True


class BaseOscillator(ABC):
    """Base class for all bio oscillators"""

    def __init__(self, config: OscillatorConfig = None):
        self.config = config or OscillatorConfig()
        self.state = 0.0
        self.timestamp = _ensure_utc()

    @abstractmethod
    def oscillate(self) -> float:
        """Generate oscillation signal"""
        pass

    def reset(self):
        """Reset oscillator state"""
        self.state = 0.0
        self.timestamp = _ensure_utc()

    def mark_observation(self, observed_at: Optional[datetime] = None) -> datetime:
        """Update the oscillator timestamp to reflect the latest observation.

        Args:
            observed_at: Optional externally supplied timestamp.  When omitted,
                the current UTC time is used.

        Returns:
            The normalized UTC timestamp that was stored.
        """

        self.timestamp = _ensure_utc(observed_at)
        return self.timestamp


class BioOscillator(BaseOscillator):
    """Standard bio oscillator implementation"""

    def oscillate(self) -> float:
        """Generate bio-inspired oscillation"""
        # Placeholder implementation
        self.state += 0.1
        return self.state * self.config.amplitude


class QIOscillator(BaseOscillator):
    """Quantum-enhanced oscillator"""

    def __init__(self, config: OscillatorConfig = None):
        super().__init__(config)
        self.qi_state = 0.0

    def oscillate(self) -> float:
        """Generate quantum-enhanced oscillation"""
        # Placeholder quantum implementation
        self.qi_state += 0.05
        self.state = self.qi_state * self.config.frequency
        return self.state


class PrimeHarmonicOscillator(BaseOscillator):
    """Prime harmonic oscillator implementation"""

    def oscillate(self) -> float:
        """Generate prime harmonic oscillation"""
        # Placeholder implementation
        self.state = (self.state + 0.13) % 1.0  # Using prime 13
        return self.state


class BioOrchestrator:
    """Orchestrates multiple bio oscillators"""

    def __init__(self):
        self.oscillators: dict[str, BaseOscillator] = {}
        self.active = True

    def add_oscillator(self, name: str, oscillator: BaseOscillator):
        """Add an oscillator to the orchestrator"""
        self.oscillators[name] = oscillator

    def step(self) -> dict[str, float]:
        """Step all oscillators forward"""
        results = {}
        if self.active:
            for name, osc in self.oscillators.items():
                results[name] = osc.oscillate()
        return results

    def reset_all(self):
        """Reset all oscillators"""
        for osc in self.oscillators.values():
            osc.reset()


# Singleton orchestrator instance
_orchestrator = None


def get_orchestrator() -> BioOrchestrator:
    """Get or create the bio orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = BioOrchestrator()
        # Add default oscillators
        _orchestrator.add_oscillator("bio", BioOscillator())
        _orchestrator.add_oscillator("quantum", QIOscillator())
        _orchestrator.add_oscillator("prime", PrimeHarmonicOscillator())
    return _orchestrator
