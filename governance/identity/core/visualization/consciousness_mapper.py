"""
Consciousness State Mapper for LUKHAS ORB

This module maps various biometric, emotional, and cognitive inputs
to consciousness states for visualization in the LUKHAS ORB.

It integrates with:
- Biometric sensors (heart rate, EEG, eye tracking)
- Emotional analysis (facial expression, voice tone)
- Cognitive load estimation
- Attention monitoring
- Dream state detection

Author: LUKHAS Identity Team
Version: 1.0.0
"""

import math
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import numpy as np


class EmotionalState(Enum):
    """Supported emotional states"""
    JOY = "joy"
    CALM = "calm"
    FOCUS = "focus"
    EXCITEMENT = "excitement"
    STRESS = "stress"
    NEUTRAL = "neutral"
    LOVE = "love"
    TRUST = "trust"
    CURIOSITY = "curiosity"
    CONTEMPLATION = "contemplation"


@dataclass
class BiometricData:
    """Raw biometric sensor data"""
    heart_rate: Optional[float] = None          # BPM
    heart_rate_variability: Optional[float] = None  # ms
    skin_conductance: Optional[float] = None    # microsiemens
    temperature: Optional[float] = None         # Celsius
    eye_movement_velocity: Optional[float] = None  # degrees/second
    pupil_dilation: Optional[float] = None      # mm
    eeg_alpha_power: Optional[float] = None     # μV²
    eeg_beta_power: Optional[float] = None      # μV²
    eeg_gamma_power: Optional[float] = None     # μV²
    eeg_theta_power: Optional[float] = None     # μV²
    breathing_rate: Optional[float] = None      # breaths/minute
    voice_pitch_variance: Optional[float] = None # Hz variance


@dataclass
class CognitiveMetrics:
    """Cognitive and attention metrics"""
    attention_score: float          # 0.0 to 1.0
    cognitive_load: float          # 0.0 to 1.0
    task_engagement: float         # 0.0 to 1.0
    mind_wandering: float         # 0.0 to 1.0
    flow_state: float             # 0.0 to 1.0
    creativity_index: float        # 0.0 to 1.0


@dataclass
class ConsciousnessState:
    """Complete consciousness state representation"""
    consciousness_level: float      # 0.0 to 1.0
    emotional_state: EmotionalState
    emotional_intensity: float      # 0.0 to 1.0
    neural_synchrony: float        # 0.0 to 1.0
    attention_focus: List[str]     # Current focus areas
    stress_level: float           # 0.0 to 1.0
    relaxation_level: float       # 0.0 to 1.0
    authenticity_score: float     # 0.0 to 1.0
    timestamp: float


class ConsciousnessMapper:
    """
    Maps biometric and cognitive data to consciousness states
    for LUKHAS ORB visualization
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Calibration settings
        self.baseline_heart_rate = self.config.get("baseline_heart_rate", 70)
        self.baseline_hrv = self.config.get("baseline_hrv", 50)
        self.stress_threshold = self.config.get("stress_threshold", 0.7)

        # State history for smoothing
        self.state_history: List[ConsciousnessState] = []
        self.max_history = 30

        # Emotional state transition matrix
        self.emotion_transitions = {
            EmotionalState.NEUTRAL: [EmotionalState.CALM, EmotionalState.FOCUS, EmotionalState.CURIOSITY],
            EmotionalState.CALM: [EmotionalState.NEUTRAL, EmotionalState.JOY, EmotionalState.CONTEMPLATION],
            EmotionalState.FOCUS: [EmotionalState.NEUTRAL, EmotionalState.EXCITEMENT, EmotionalState.STRESS],
            EmotionalState.JOY: [EmotionalState.EXCITEMENT, EmotionalState.CALM, EmotionalState.LOVE],
            EmotionalState.STRESS: [EmotionalState.FOCUS, EmotionalState.NEUTRAL, EmotionalState.CALM],
            EmotionalState.EXCITEMENT: [EmotionalState.JOY, EmotionalState.FOCUS, EmotionalState.STRESS],
            EmotionalState.LOVE: [EmotionalState.JOY, EmotionalState.TRUST, EmotionalState.CALM],
            EmotionalState.TRUST: [EmotionalState.CALM, EmotionalState.LOVE, EmotionalState.NEUTRAL],
            EmotionalState.CURIOSITY: [EmotionalState.FOCUS, EmotionalState.EXCITEMENT, EmotionalState.CONTEMPLATION],
            EmotionalState.CONTEMPLATION: [EmotionalState.CALM, EmotionalState.CURIOSITY, EmotionalState.NEUTRAL]
        }

    def map_to_consciousness_state(self,
                                  biometrics: BiometricData,
                                  cognitive: CognitiveMetrics,
                                  context: Optional[Dict[str, Any]] = None) -> ConsciousnessState:
        """
        Map biometric and cognitive data to consciousness state

        Args:
            biometrics: Raw biometric sensor data
            cognitive: Cognitive and attention metrics
            context: Optional context information

        Returns:
            ConsciousnessState for ORB visualization
        """
        context = context or {}

        # Calculate consciousness level
        consciousness_level = self._calculate_consciousness_level(biometrics, cognitive)

        # Determine emotional state
        emotional_state, emotional_intensity = self._determine_emotional_state(biometrics, cognitive)

        # Calculate neural synchrony
        neural_synchrony = self._calculate_neural_synchrony(biometrics)

        # Determine attention focus
        attention_focus = self._determine_attention_focus(cognitive, context)

        # Calculate stress and relaxation
        stress_level = self._calculate_stress_level(biometrics, cognitive)
        relaxation_level = self._calculate_relaxation_level(biometrics, cognitive)

        # Calculate authenticity score
        authenticity_score = self._calculate_authenticity_score(biometrics, cognitive)

        # Create consciousness state
        state = ConsciousnessState(
            consciousness_level=consciousness_level,
            emotional_state=emotional_state,
            emotional_intensity=emotional_intensity,
            neural_synchrony=neural_synchrony,
            attention_focus=attention_focus,
            stress_level=stress_level,
            relaxation_level=relaxation_level,
            authenticity_score=authenticity_score,
            timestamp=time.time()
        )

        # Apply smoothing if history exists
        if self.state_history:
            state = self._smooth_state_transition(state)

        # Update history
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

        return state

    def _calculate_consciousness_level(self, biometrics: BiometricData, cognitive: CognitiveMetrics) -> float:
        """Calculate overall consciousness level from inputs"""
        factors = []
        weights = []

        # Cognitive factors (highest weight)
        if cognitive.attention_score is not None:
            factors.append(cognitive.attention_score)
            weights.append(2.0)

        if cognitive.flow_state is not None:
            factors.append(cognitive.flow_state)
            weights.append(1.5)

        if cognitive.task_engagement is not None:
            factors.append(cognitive.task_engagement)
            weights.append(1.5)

        # EEG factors (if available)
        if biometrics.eeg_alpha_power is not None and biometrics.eeg_beta_power is not None:
            # Alpha/Beta ratio indicates relaxed awareness
            alpha_beta_ratio = biometrics.eeg_alpha_power / (biometrics.eeg_beta_power + 0.1)
            normalized_ratio = min(1.0, alpha_beta_ratio / 2.0)  # Normalize to 0-1
            factors.append(normalized_ratio)
            weights.append(1.0)

        if biometrics.eeg_gamma_power is not None:
            # Gamma power indicates high-level cognitive processing
            gamma_normalized = min(1.0, biometrics.eeg_gamma_power / 50.0)
            factors.append(gamma_normalized)
            weights.append(0.8)

        # Heart rate variability (indicates adaptability)
        if biometrics.heart_rate_variability is not None:
            hrv_normalized = min(1.0, biometrics.heart_rate_variability / 100.0)
            factors.append(hrv_normalized)
            weights.append(0.5)

        # Calculate weighted average
        if factors:
            consciousness_level = sum(f * w for f, w in zip(factors, weights)) / sum(weights)
        else:
            consciousness_level = 0.5  # Default to moderate consciousness

        # Apply creativity boost
        if cognitive.creativity_index > 0.7:
            consciousness_level = min(1.0, consciousness_level * 1.2)

        return consciousness_level

    def _determine_emotional_state(self, biometrics: BiometricData,
                                 cognitive: CognitiveMetrics) -> Tuple[EmotionalState, float]:
        """Determine emotional state and intensity from biometrics"""

        # Calculate emotional indicators
        arousal = self._calculate_arousal(biometrics)
        valence = self._calculate_valence(biometrics, cognitive)

        # Map to emotional state using circumplex model
        if arousal > 0.6:
            if valence > 0.6:
                emotion = EmotionalState.JOY if arousal > 0.8 else EmotionalState.EXCITEMENT
            else:
                emotion = EmotionalState.STRESS if valence < 0.4 else EmotionalState.FOCUS
        else:
            if valence > 0.6:
                emotion = EmotionalState.CALM if arousal < 0.3 else EmotionalState.TRUST
            else:
                emotion = EmotionalState.CONTEMPLATION if valence > 0.4 else EmotionalState.NEUTRAL

        # Special cases based on cognitive metrics
        if cognitive.flow_state > 0.8:
            emotion = EmotionalState.FOCUS
        elif cognitive.creativity_index > 0.8:
            emotion = EmotionalState.CURIOSITY

        # Calculate intensity
        intensity = (arousal + abs(valence - 0.5) * 2) / 2

        return emotion, min(1.0, intensity)

    def _calculate_arousal(self, biometrics: BiometricData) -> float:
        """Calculate emotional arousal level"""
        arousal_factors = []

        # Heart rate elevation
        if biometrics.heart_rate is not None:
            hr_elevation = (biometrics.heart_rate - self.baseline_heart_rate) / self.baseline_heart_rate
            arousal_factors.append(min(1.0, max(0.0, hr_elevation + 0.5)))

        # Skin conductance (strong arousal indicator)
        if biometrics.skin_conductance is not None:
            sc_normalized = min(1.0, biometrics.skin_conductance / 20.0)
            arousal_factors.append(sc_normalized)

        # Pupil dilation
        if biometrics.pupil_dilation is not None:
            pupil_normalized = min(1.0, (biometrics.pupil_dilation - 3.0) / 3.0)
            arousal_factors.append(max(0.0, pupil_normalized))

        # Breathing rate
        if biometrics.breathing_rate is not None:
            br_normalized = min(1.0, biometrics.breathing_rate / 30.0)
            arousal_factors.append(br_normalized)

        return sum(arousal_factors) / len(arousal_factors) if arousal_factors else 0.5

    def _calculate_valence(self, biometrics: BiometricData, cognitive: CognitiveMetrics) -> float:
        """Calculate emotional valence (positive/negative)"""
        valence_factors = []

        # HRV (higher = more positive)
        if biometrics.heart_rate_variability is not None:
            hrv_factor = min(1.0, biometrics.heart_rate_variability / self.baseline_hrv)
            valence_factors.append(hrv_factor)

        # Voice pitch variance (moderate = positive)
        if biometrics.voice_pitch_variance is not None:
            pitch_factor = 1.0 - abs(biometrics.voice_pitch_variance - 50) / 100
            valence_factors.append(pitch_factor)

        # Cognitive engagement
        valence_factors.append(cognitive.task_engagement)

        # Flow state (very positive)
        if cognitive.flow_state > 0.5:
            valence_factors.append(cognitive.flow_state)

        # Mind wandering (negative)
        valence_factors.append(1.0 - cognitive.mind_wandering)

        return sum(valence_factors) / len(valence_factors) if valence_factors else 0.5

    def _calculate_neural_synchrony(self, biometrics: BiometricData) -> float:
        """Calculate neural synchrony from EEG data"""
        if not any([biometrics.eeg_alpha_power, biometrics.eeg_beta_power,
                   biometrics.eeg_gamma_power, biometrics.eeg_theta_power]):
            # Estimate from other biometrics
            if biometrics.heart_rate_variability is not None:
                return min(1.0, biometrics.heart_rate_variability / 80.0)
            return 0.5

        # Calculate coherence between frequency bands
        bands = []
        if biometrics.eeg_theta_power is not None:
            bands.append(biometrics.eeg_theta_power)
        if biometrics.eeg_alpha_power is not None:
            bands.append(biometrics.eeg_alpha_power)
        if biometrics.eeg_beta_power is not None:
            bands.append(biometrics.eeg_beta_power)
        if biometrics.eeg_gamma_power is not None:
            bands.append(biometrics.eeg_gamma_power)

        if len(bands) < 2:
            return 0.5

        # Calculate synchrony as inverse of variance
        mean_power = sum(bands) / len(bands)
        variance = sum((b - mean_power) ** 2 for b in bands) / len(bands)
        max_variance = mean_power ** 2  # Maximum possible variance

        synchrony = 1.0 - (variance / (max_variance + 0.1))
        return max(0.0, min(1.0, synchrony))

    def _determine_attention_focus(self, cognitive: CognitiveMetrics, context: Dict[str, Any]) -> List[str]:
        """Determine current attention focus areas"""
        focus_areas = []

        # Primary task focus
        if cognitive.task_engagement > 0.7:
            focus_areas.append("primary_task")

        # Authentication focus
        if context.get("authentication_active", False):
            focus_areas.append("authentication")

        # Creative focus
        if cognitive.creativity_index > 0.6:
            focus_areas.append("creative_exploration")

        # Flow state focus
        if cognitive.flow_state > 0.7:
            focus_areas.append("flow_immersion")

        # Mind wandering
        if cognitive.mind_wandering > 0.6:
            focus_areas.append("internal_reflection")

        # Environmental awareness
        if cognitive.attention_score < 0.3:
            focus_areas.append("environmental_scan")

        # Dream state (from context)
        if context.get("dream_state_active", False):
            focus_areas.append("dream")

        return focus_areas if focus_areas else ["neutral"]

    def _calculate_stress_level(self, biometrics: BiometricData, cognitive: CognitiveMetrics) -> float:
        """Calculate stress level from multiple indicators"""
        stress_factors = []

        # Heart rate elevation
        if biometrics.heart_rate is not None:
            hr_stress = max(0, (biometrics.heart_rate - self.baseline_heart_rate) / 30)
            stress_factors.append(min(1.0, hr_stress))

        # Low HRV indicates stress
        if biometrics.heart_rate_variability is not None:
            hrv_stress = 1.0 - (biometrics.heart_rate_variability / self.baseline_hrv)
            stress_factors.append(max(0.0, hrv_stress))

        # High skin conductance
        if biometrics.skin_conductance is not None:
            sc_stress = min(1.0, biometrics.skin_conductance / 15.0)
            stress_factors.append(sc_stress)

        # Cognitive overload
        stress_factors.append(cognitive.cognitive_load)

        # Low flow state
        stress_factors.append(1.0 - cognitive.flow_state)

        return sum(stress_factors) / len(stress_factors) if stress_factors else 0.3

    def _calculate_relaxation_level(self, biometrics: BiometricData, cognitive: CognitiveMetrics) -> float:
        """Calculate relaxation level"""
        relax_factors = []

        # Low heart rate
        if biometrics.heart_rate is not None:
            hr_relax = max(0, (self.baseline_heart_rate - biometrics.heart_rate) / 20)
            relax_factors.append(min(1.0, hr_relax + 0.5))

        # High HRV
        if biometrics.heart_rate_variability is not None:
            hrv_relax = biometrics.heart_rate_variability / (self.baseline_hrv * 1.5)
            relax_factors.append(min(1.0, hrv_relax))

        # Alpha wave dominance
        if biometrics.eeg_alpha_power is not None and biometrics.eeg_beta_power is not None:
            alpha_dominance = biometrics.eeg_alpha_power / (biometrics.eeg_beta_power + 1.0)
            relax_factors.append(min(1.0, alpha_dominance / 2.0))

        # Low cognitive load
        relax_factors.append(1.0 - cognitive.cognitive_load)

        # Low mind wandering (focused relaxation)
        relax_factors.append(1.0 - cognitive.mind_wandering * 0.5)

        return sum(relax_factors) / len(relax_factors) if relax_factors else 0.5

    def _calculate_authenticity_score(self, biometrics: BiometricData, cognitive: CognitiveMetrics) -> float:
        """Calculate authenticity score for spoofing detection"""
        authenticity_factors = []

        # Micro-variations in heart rate (real humans have natural variability)
        if biometrics.heart_rate_variability is not None:
            hrv_authenticity = 1.0 if 20 < biometrics.heart_rate_variability < 100 else 0.5
            authenticity_factors.append(hrv_authenticity)

        # Natural eye movement patterns
        if biometrics.eye_movement_velocity is not None:
            eye_authenticity = 1.0 if 10 < biometrics.eye_movement_velocity < 500 else 0.3
            authenticity_factors.append(eye_authenticity)

        # Coherent emotional-physiological coupling
        arousal = self._calculate_arousal(biometrics)
        cognitive_arousal = (cognitive.attention_score + cognitive.task_engagement) / 2
        coupling = 1.0 - abs(arousal - cognitive_arousal)
        authenticity_factors.append(coupling)

        # Natural breathing patterns
        if biometrics.breathing_rate is not None:
            breath_authenticity = 1.0 if 12 < biometrics.breathing_rate < 20 else 0.5
            authenticity_factors.append(breath_authenticity)

        return sum(authenticity_factors) / len(authenticity_factors) if authenticity_factors else 0.8

    def _smooth_state_transition(self, new_state: ConsciousnessState) -> ConsciousnessState:
        """Smooth state transitions using history"""
        if not self.state_history:
            return new_state

        # Get recent states (last 3)
        recent_states = self.state_history[-3:]

        # Smooth numerical values
        smoothed_consciousness = (
            new_state.consciousness_level * 0.5 +
            sum(s.consciousness_level for s in recent_states) / len(recent_states) * 0.5
        )

        smoothed_neural_synchrony = (
            new_state.neural_synchrony * 0.6 +
            sum(s.neural_synchrony for s in recent_states) / len(recent_states) * 0.4
        )

        smoothed_stress = (
            new_state.stress_level * 0.7 +
            sum(s.stress_level for s in recent_states) / len(recent_states) * 0.3
        )

        # Check if emotional state should transition
        current_emotion = recent_states[-1].emotional_state
        if new_state.emotional_state != current_emotion:
            # Only transition if new emotion is in allowed transitions
            allowed_transitions = self.emotion_transitions.get(current_emotion, [])
            if new_state.emotional_state not in allowed_transitions:
                # Keep current emotion but update intensity
                new_state.emotional_state = current_emotion
                new_state.emotional_intensity *= 0.8

        # Apply smoothed values
        new_state.consciousness_level = smoothed_consciousness
        new_state.neural_synchrony = smoothed_neural_synchrony
        new_state.stress_level = smoothed_stress

        return new_state

    def calibrate(self, baseline_biometrics: BiometricData):
        """Calibrate mapper with user's baseline biometrics"""
        if baseline_biometrics.heart_rate is not None:
            self.baseline_heart_rate = baseline_biometrics.heart_rate

        if baseline_biometrics.heart_rate_variability is not None:
            self.baseline_hrv = baseline_biometrics.heart_rate_variability