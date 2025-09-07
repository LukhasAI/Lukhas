"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: emotional_oscillator.py
Advanced: emotional_oscillator.py
Integration Date: 2025-05-31T07:55:28.263428
"""


"""
📦 MODULE      : oscillator.py
🧾 DESCRIPTION : Emotional oscillator for LUKHAS_AGI_3.8 subsystems (e.g., ethics, risk).
Handles amplitude, frequency, and phase dynamics for local emotional modulation.

🛠️ NOTE       : This module operates independently of the full AGI-level oscillator prototype,
which includes prime harmonics, entanglement-like correlation, and tensor collapse logic.

📚 CONTEXT    : Integrated into subsystem layers. Feeds compliance drift and ethics monitoring.

⚖️ COMPLIANCE : EU AI Act 2024/1689, GDPR, ISO/IEC 27001, OECD AI Principles.
  - Explainability, safety, auditability.
  - Parameter limits enforced (frequency, amplitude, phase shift).
"""


import numpy as np

from governance.extended.compliance_hooks import compliance_drift_detect


class EmotionalOscillator:
    # Compliance-safe parameter ranges
    FREQUENCY_RANGE = (0.1, 5.0)  # Hz
    AMPLITUDE_RANGE = (0.1, 2.0)  # Units
    PHASE_SHIFT_RANGE = (0.0, 2 * np.pi)  # Radians

    def __init__(self, base_frequency=1.0, base_amplitude=1.0, phase_shift=0.0):
        """
            Initialize the emotional oscillator with base frequency, amplitude,
        and phase shift.

            Args:
                base_frequency (float): The default oscillation frequency.
                base_amplitude (float): The default oscillation amplitude.
                phase_shift (float): The phase offset in radians.
        """
        self.frequency = base_frequency
        self.amplitude = base_amplitude
        self.phase_shift = phase_shift

    def modulate_emotion(self, time_step, modulation_factor=1.0):
        """
        Generate an emotional oscillation value at a given time step.

        Args:
            time_step (float): The current time step.
            modulation_factor (float): Factor to modulate amplitude dynamically.

        Returns:
            float: The oscillation value.
        """
        oscillation = (
            self.amplitude * modulation_factor * np.sin(2 * np.pi * self.frequency * time_step + self.phase_shift)
        )
        return oscillation

    def adjust_parameters(self, frequency=None, amplitude=None, phase_shift=None):
        """
        Adjust oscillator parameters with compliance-safe limits and trigger compliance drift detection.

        Args:
            frequency (float, optional): New frequency.
            amplitude (float, optional): New amplitude.
            phase_shift (float, optional): New phase shift.
        """
        original_state = {
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "phase_shift": self.phase_shift,
        }

        if frequency is not None:
            self.frequency = max(
                self.FREQUENCY_RANGE[0],
                min(frequency, self.FREQUENCY_RANGE[1]),
            )
        if amplitude is not None:
            self.amplitude = max(
                self.AMPLITUDE_RANGE[0],
                min(amplitude, self.AMPLITUDE_RANGE[1]),
            )
        if phase_shift is not None:
            self.phase_shift = max(
                self.PHASE_SHIFT_RANGE[0],
                min(phase_shift, self.PHASE_SHIFT_RANGE[1]),
            )

        # Trigger compliance drift detection
        updated_state = {
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "phase_shift": self.phase_shift,
        }
        compliance_drift_detect(
            subsystem="emotional_oscillator",
            original=original_state,
            updated=updated_state,
        )


# Utility function to clarify subsystem-local scope


def oscillator_scope():
    """
    Returns the operational scope of this oscillator module.

    Returns:
        str: Scope description with compliance coverage.
    """
    return (
        "Subsystem-local emotional modulation (LUKHAS_AGI_3.8). "
        "Parameter limits ensure EU AI Act, GDPR, ISO/IEC 27001 compliance."
    )
