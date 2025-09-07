"""
Prime Harmonic Oscillator implementation.

This module implements the core bio-inspired oscillator that uses prime number ratios
for harmonic synchronization, inspired by biological rhythms and quantum phenomena.
"""
import logging
import math
from typing import Any, Optional

import numpy as np

from .base_oscillator import BaseOscillator, OscillatorConfig

logger = logging.getLogger("PrimeOscillator")


class PrimeHarmonicOscillator(BaseOscillator):
    """
    Core oscillator implementing prime ratio synchronization.

    This oscillator uses prime number ratios to generate harmonically related
    frequencies, enabling complex synchronization patterns similar to biological
    systems.

    Features:
    - Prime-based frequency relationships
    - Harmonic synchronization
    - Phase coherence maintenance
    - Energy-efficient oscillations
    """

    def __init__(
        self,
        base_freq: float = 3.0,
        ratio: float = 1.0,
        config: Optional[OscillatorConfig] = None,
    ):
        """
        Initialize prime harmonic oscillator

        Args:
            base_freq: Base oscillation frequency (Hz)
            ratio: Prime ratio multiplier
            config: Optional oscillator configuration
        """
        super().__init__(freq=base_freq * ratio, config=config)

        self.base_freq = base_freq
        self.ratio = ratio

        # Oscillation state
        self._step = 0.0
        self._index = 0

        # Performance tracking
        self.coherence_history = []
        self.energy_history = []

        self._initialize_oscillation()

    def _initialize_oscillation(self):
        """Set up initial oscillation state"""
        self._step = (2 * math.pi * self._freq) / self._sample_rate
        self._index = 0

    def _post_freq_update(self):
        """Update step size when frequency changes"""
        self._step = (2 * math.pi * self._freq) / self._sample_rate

    def _post_phase_update(self):
        """Normalize phase to radians"""
        self._phase = (self._phase / 360) * 2 * math.pi

    def _post_amplitude_update(self):
        """Handle amplitude changes"""
        self.update_metrics()

    def generate_value(self, time_step: float) -> float:
        """
        Generate oscillation value for given time step

        Args:
            time_step: Time point to generate value for

        Returns:
            float: Oscillation value at time_step
        """
        value = self._amplitude * math.sin(2 * math.pi * self._freq * time_step + self._phase)

        # Track performance
        self._update_history(value)

        return value

    def _update_history(self, value: float):
        """Update performance tracking"""
        # Calculate instantaneous coherence
        coherence = abs(value) / self._amplitude
        self.coherence_history.append(coherence)

        # Calculate energy usage
        energy = (value**2) * self._amplitude
        self.energy_history.append(energy)

        # Keep history bounded
        max_history = 1000
        if len(self.coherence_history) > max_history:
            self.coherence_history = self.coherence_history[-max_history:]
            self.energy_history = self.energy_history[-max_history:]

    def update_metrics(self):
        """Update oscillator performance metrics"""
        if self.coherence_history:
            self.metrics["coherence"] = np.mean(self.coherence_history[-100:])
            self.metrics["energy_efficiency"] = 1.0 / (np.mean(self.energy_history[-100:]) + 1e-6)
            self.metrics["stability"] = 1.0 - np.std(self.coherence_history[-100:])

    def __next__(self) -> float:
        """Generate next oscillation value"""
        value = self.generate_value(self._index / self._sample_rate)
        self._index += 1
        return value

    def get_state(self) -> dict[str, Any]:
        """Get current oscillator state"""
        return {
            "frequency": self._freq,
            "phase": self._phase,
            "amplitude": self._amplitude,
            "metrics": self.metrics,
            "base_frequency": self.base_freq,
            "ratio": self.ratio,
        }
