#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - THETA OSCILLATOR
║ Theta rhythm generation for memory encoding and retrieval
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: theta_oscillator.py
║ Path: memory/hippocampal/theta_oscillator.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import numpy as np
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import math

import structlog

from core.common import get_logger


class OscillationPhase(Enum):
    """Phases of theta oscillation with functional significance"""
    ENCODING = "encoding"      # Peak phase - optimal for encoding
    RETRIEVAL = "retrieval"    # Trough phase - optimal for retrieval
    TRANSITION = "transition"  # Between peak and trough
    QUIET = "quiet"           # Low power state


@dataclass
class ThetaWave:
    """Single theta wave measurement"""
    timestamp: float
    phase: float  # 0 to 2π
    amplitude: float
    frequency: float
    phase_name: OscillationPhase

    def phase_degrees(self) -> float:
        """Get phase in degrees"""
        return math.degrees(self.phase)


class ThetaOscillator:
    """
    Generates theta oscillations (4-8 Hz) for memory processing.
    Coordinates encoding and retrieval based on oscillation phase.
    """

    def __init__(
        self,
        base_frequency: float = 6.0,  # Hz
        frequency_variance: float = 1.0,  # Hz
        base_amplitude: float = 1.0,
        amplitude_modulation: float = 0.3,
        phase_coupling_strength: float = 0.7
    ):
        self.base_frequency = base_frequency
        self.frequency_variance = frequency_variance
        self.base_amplitude = base_amplitude
        self.amplitude_modulation = amplitude_modulation
        self.phase_coupling_strength = phase_coupling_strength

        # Current state
        self.current_phase = 0.0
        self.current_frequency = base_frequency
        self.current_amplitude = base_amplitude
        self.last_update = time.time()

        # Phase-locked loops for synchronization
        self.phase_locked_oscillators: Dict[str, float] = {}

        # Gamma coupling (30-100 Hz nested in theta)
        self.enable_gamma_coupling = True
        self.gamma_frequency = 40.0  # Hz
        self.gamma_phase = 0.0

        # History for analysis
        self.wave_history: List[ThetaWave] = []
        self.max_history = 1000

        # Callbacks for phase-specific events
        self.phase_callbacks: Dict[OscillationPhase, List[Callable]] = {
            phase: [] for phase in OscillationPhase
        }

        # Running state
        self._running = False
        self._oscillation_task = None

        logger.info(
            "ThetaOscillator initialized",
            base_freq=base_frequency,
            freq_variance=frequency_variance
        )

    async def start(self):
        """Start theta oscillation"""
        self._running = True
        self._oscillation_task = asyncio.create_task(self._oscillation_loop())
        logger.info("ThetaOscillator started")

    async def stop(self):
        """Stop theta oscillation"""
        self._running = False
        if self._oscillation_task:
            self._oscillation_task.cancel()
        logger.info("ThetaOscillator stopped")

    def get_current_state(self) -> ThetaWave:
        """Get current oscillation state"""
        return ThetaWave(
            timestamp=time.time(),
            phase=self.current_phase,
            amplitude=self.current_amplitude,
            frequency=self.current_frequency,
            phase_name=self._get_phase_name(self.current_phase)
        )

    def is_encoding_optimal(self) -> bool:
        """Check if current phase is optimal for encoding"""
        phase_name = self._get_phase_name(self.current_phase)
        return phase_name == OscillationPhase.ENCODING

    def is_retrieval_optimal(self) -> bool:
        """Check if current phase is optimal for retrieval"""
        phase_name = self._get_phase_name(self.current_phase)
        return phase_name == OscillationPhase.RETRIEVAL

    def phase_lock(self, oscillator_id: str, target_phase: float = 0.0):
        """
        Phase-lock another oscillator to this theta rhythm.
        Used for synchronizing memory operations across regions.
        """
        self.phase_locked_oscillators[oscillator_id] = target_phase
        logger.debug(
            "Phase-locked oscillator",
            oscillator_id=oscillator_id,
            target_phase=target_phase
        )

    def phase_unlock(self, oscillator_id: str):
        """Remove phase-locking for an oscillator"""
        if oscillator_id in self.phase_locked_oscillators:
            del self.phase_locked_oscillators[oscillator_id]

    def register_phase_callback(
        self,
        phase: OscillationPhase,
        callback: Callable
    ):
        """Register callback for specific oscillation phase"""
        self.phase_callbacks[phase].append(callback)

    def modulate_frequency(self, delta: float):
        """Modulate oscillation frequency (within bounds)"""
        new_freq = self.current_frequency + delta

        # Keep within theta range (4-8 Hz)
        new_freq = max(4.0, min(8.0, new_freq))

        self.current_frequency = new_freq
        logger.debug(f"Frequency modulated to {new_freq:.1f} Hz")

    def modulate_amplitude(self, factor: float):
        """Modulate oscillation amplitude"""
        self.current_amplitude = self.base_amplitude * factor

    def get_gamma_phase(self) -> float:
        """Get nested gamma oscillation phase"""
        if self.enable_gamma_coupling:
            return self.gamma_phase
        return 0.0

    def compute_phase_amplitude_coupling(self) -> float:
        """
        Compute theta-gamma phase-amplitude coupling.
        High gamma amplitude at theta peak indicates good memory encoding.
        """
        if not self.enable_gamma_coupling:
            return 0.0

        # Gamma amplitude is modulated by theta phase
        # Maximum at theta peak (phase = π/2)
        theta_modulation = (1 + np.cos(self.current_phase - np.pi/2)) / 2

        return theta_modulation

    def get_phase_coherence(self, other_phase: float) -> float:
        """
        Calculate phase coherence with another oscillator.
        Returns value between 0 (no coherence) and 1 (perfect coherence).
        """
        phase_diff = abs(self.current_phase - other_phase)
        # Normalize to [0, π]
        phase_diff = min(phase_diff, 2 * np.pi - phase_diff)

        # Convert to coherence (1 when phases match, 0 when opposite)
        coherence = (1 + np.cos(phase_diff)) / 2

        return coherence

    def get_traveling_wave_offset(self, distance: float, wave_speed: float = 5.0) -> float:
        """
        Calculate phase offset for traveling theta waves.
        Used for sequential memory activation across hippocampal regions.

        Args:
            distance: Distance from source (arbitrary units)
            wave_speed: Speed of traveling wave (units/second)

        Returns:
            Phase offset in radians
        """
        # Time delay based on distance and speed
        time_delay = distance / wave_speed

        # Convert to phase offset
        phase_offset = 2 * np.pi * self.current_frequency * time_delay

        return phase_offset % (2 * np.pi)

    async def wait_for_phase(self, target_phase: OscillationPhase, timeout: float = 1.0):
        """
        Wait until oscillator reaches target phase.
        Useful for timing memory operations.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._get_phase_name(self.current_phase) == target_phase:
                return True

            await asyncio.sleep(0.001)  # 1ms resolution

        return False  # Timeout

    def _get_phase_name(self, phase: float) -> OscillationPhase:
        """Map phase angle to functional phase name"""
        # Normalize to [0, 2π]
        phase = phase % (2 * np.pi)

        # Phase mapping (can be adjusted based on empirical data)
        if 0.785 <= phase < 2.356:  # ~π/4 to ~3π/4
            return OscillationPhase.ENCODING
        elif 3.927 <= phase or phase < 0.785:  # ~5π/4 to ~π/4
            return OscillationPhase.RETRIEVAL
        elif 2.356 <= phase < 3.927:  # ~3π/4 to ~5π/4
            return OscillationPhase.TRANSITION
        else:
            return OscillationPhase.QUIET

    async def _oscillation_loop(self):
        """Main oscillation loop"""

        while self._running:
            current_time = time.time()
            dt = current_time - self.last_update

            # Add frequency variation (1/f noise)
            freq_noise = np.random.normal(0, 0.1) * self.frequency_variance
            instantaneous_freq = self.current_frequency + freq_noise
            instantaneous_freq = max(4.0, min(8.0, instantaneous_freq))

            # Update phase
            phase_increment = 2 * np.pi * instantaneous_freq * dt
            self.current_phase = (self.current_phase + phase_increment) % (2 * np.pi)

            # Update gamma phase if enabled
            if self.enable_gamma_coupling:
                gamma_increment = 2 * np.pi * self.gamma_frequency * dt
                self.gamma_phase = (self.gamma_phase + gamma_increment) % (2 * np.pi)

            # Amplitude modulation (breathing)
            amplitude_variation = np.sin(current_time * 0.1) * self.amplitude_modulation
            self.current_amplitude = self.base_amplitude * (1 + amplitude_variation)

            # Update phase-locked oscillators
            for osc_id, target_offset in self.phase_locked_oscillators.items():
                # They should maintain constant phase offset
                # In real implementation, would send sync signal
                pass

            # Record wave
            wave = self.get_current_state()
            self.wave_history.append(wave)
            if len(self.wave_history) > self.max_history:
                self.wave_history.pop(0)

            # Trigger phase callbacks
            phase_name = wave.phase_name
            for callback in self.phase_callbacks.get(phase_name, []):
                try:
                    asyncio.create_task(callback(wave))
                except Exception as e:
                    logger.error(f"Phase callback error: {e}")

            self.last_update = current_time

            # Sleep based on desired resolution (10x oversampling)
            sleep_time = 1.0 / (instantaneous_freq * 10)
            await asyncio.sleep(sleep_time)

    def get_metrics(self) -> Dict[str, Any]:
        """Get oscillator metrics"""

        if self.wave_history:
            recent_waves = self.wave_history[-100:]
            avg_frequency = np.mean([w.frequency for w in recent_waves])
            avg_amplitude = np.mean([w.amplitude for w in recent_waves])

            # Phase distribution
            phase_counts = {phase: 0 for phase in OscillationPhase}
            for wave in recent_waves:
                phase_counts[wave.phase_name] += 1
        else:
            avg_frequency = self.current_frequency
            avg_amplitude = self.current_amplitude
            phase_counts = {phase: 0 for phase in OscillationPhase}

        return {
            "current_phase": self.current_phase,
            "current_phase_degrees": math.degrees(self.current_phase),
            "current_phase_name": self._get_phase_name(self.current_phase).value,
            "current_frequency_hz": self.current_frequency,
            "current_amplitude": self.current_amplitude,
            "average_frequency_hz": avg_frequency,
            "average_amplitude": avg_amplitude,
            "phase_locked_count": len(self.phase_locked_oscillators),
            "gamma_enabled": self.enable_gamma_coupling,
            "gamma_phase": self.gamma_phase if self.enable_gamma_coupling else None,
            "phase_amplitude_coupling": self.compute_phase_amplitude_coupling(),
            "phase_distribution": {
                phase.value: count for phase, count in phase_counts.items()
            }
        }


# Example usage
async def demonstrate_theta_oscillator():
    """Demonstrate theta oscillator functionality"""

    oscillator = ThetaOscillator(
        base_frequency=6.0,
        frequency_variance=0.5
    )

    # Register phase callbacks
    encoding_count = 0
    retrieval_count = 0

    async def on_encoding_phase(wave: ThetaWave):
        nonlocal encoding_count
        encoding_count += 1

    async def on_retrieval_phase(wave: ThetaWave):
        nonlocal retrieval_count
        retrieval_count += 1

    oscillator.register_phase_callback(OscillationPhase.ENCODING, on_encoding_phase)
    oscillator.register_phase_callback(OscillationPhase.RETRIEVAL, on_retrieval_phase)

    await oscillator.start()

    print("=== Theta Oscillator Demonstration ===\n")

    # Monitor for a few cycles
    print("Monitoring theta oscillations for 2 seconds...")

    start_time = time.time()
    phase_samples = []

    while time.time() - start_time < 2.0:
        state = oscillator.get_current_state()
        phase_samples.append((state.phase_degrees(), state.phase_name.value))

        if len(phase_samples) % 20 == 0:
            print(f"Phase: {state.phase_degrees():.1f}° ({state.phase_name.value})")

        await asyncio.sleep(0.01)

    print(f"\nPhase callbacks triggered:")
    print(f"  Encoding phases: {encoding_count}")
    print(f"  Retrieval phases: {retrieval_count}")

    # Test phase-amplitude coupling
    print(f"\nTheta-gamma coupling: {oscillator.compute_phase_amplitude_coupling():.3f}")

    # Test traveling wave
    print("\nTraveling wave phase offsets:")
    for distance in [0, 1, 2, 3]:
        offset = oscillator.get_traveling_wave_offset(distance)
        print(f"  Distance {distance}: {math.degrees(offset):.1f}° offset")

    # Show metrics
    print("\n--- Oscillator Metrics ---")
    metrics = oscillator.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")

    await oscillator.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_theta_oscillator())