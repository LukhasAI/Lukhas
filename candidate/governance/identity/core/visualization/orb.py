"""
LUKHAS ORB Dynamic Visualization Engine

This module implements the LUKHAS_ORB - a dynamic visualization that represents
the user's consciousness state, emotional patterns, and authentication status
through real-time visual feedback.

The ORB adapts its appearance based on:
- Consciousness level (0.0 to 1.0)
- Emotional state (joy, calm, focus, stress, etc.)
- Neural synchrony patterns
- Authentication confidence
- Tier access level

Author: LUKHAS Identity Team
Version: 1.0.0
"""
import random
import streamlit as st

import hashlib
import math
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# Color mappings for different states
CONSCIOUSNESS_COLORS = {
    # Consciousness levels (0.0 - 1.0)
    "dormant": (64, 64, 128),  # Deep blue - minimal consciousness
    "awakening": (64, 128, 192),  # Light blue - low consciousness
    "aware": (64, 192, 128),  # Teal - moderate consciousness
    "focused": (128, 192, 64),  # Green - active consciousness
    "heightened": (192, 128, 64),  # Orange - high consciousness
    "transcendent": (255, 215, 0),  # Gold - peak consciousness
}

EMOTIONAL_COLORS = {
    "joy": (255, 223, 0),  # Bright yellow
    "calm": (135, 206, 235),  # Sky blue
    "focus": (0, 191, 255),  # Deep sky blue
    "excitement": (255, 69, 0),  # Red-orange
    "stress": (220, 20, 60),  # Crimson
    "neutral": (192, 192, 192),  # Silver
    "love": (255, 105, 180),  # Hot pink
    "trust": (32, 178, 170),  # Light sea green
}

TIER_AURAS = {
    0: {"color": (128, 128, 128), "name": "Guest", "pattern": "static"},
    1: {"color": (0, 255, 0), "name": "Basic", "pattern": "pulse"},
    2: {"color": (0, 0, 255), "name": "Professional", "pattern": "wave"},
    3: {"color": (128, 0, 128), "name": "Premium", "pattern": "spiral"},
    4: {"color": (255, 0, 255), "name": "Executive", "pattern": "quantum"},
    5: {"color": (255, 215, 0), "name": "Transcendent", "pattern": "fractal"},
}


class OrbPattern(Enum):
    """Visual patterns for ORB animation"""

    STATIC = "static"
    PULSE = "pulse"
    WAVE = "wave"
    SPIRAL = "spiral"
    QUANTUM = "quantum"
    FRACTAL = "fractal"
    DREAM = "dream"


@dataclass
class OrbState:
    """Current state of the LUKHAS ORB"""

    consciousness_level: float  # 0.0 to 1.0
    emotional_state: str
    neural_synchrony: float  # 0.0 to 1.0
    tier_level: int  # 0 to 5
    authentication_confidence: float  # 0.0 to 1.0
    attention_focus: list[str]
    timestamp: float
    user_lambda_id: str

    @property
    def consciousness_category(self) -> str:
        """Get consciousness category based on level"""
        if self.consciousness_level < 0.15:
            return "dormant"
        elif self.consciousness_level < 0.35:
            return "awakening"
        elif self.consciousness_level < 0.55:
            return "aware"
        elif self.consciousness_level < 0.75:
            return "focused"
        elif self.consciousness_level < 0.90:
            return "heightened"
        else:
            return "transcendent"


@dataclass
class OrbVisualization:
    """Visual representation data for the ORB"""

    primary_color: tuple[int, int, int]
    secondary_color: tuple[int, int, int]
    aura_color: tuple[int, int, int]
    size: float  # Base size multiplier
    pulse_rate: float  # Pulses per second
    rotation_speed: float  # Rotations per second
    pattern: OrbPattern
    particle_density: int  # Number of particles
    glow_intensity: float  # 0.0 to 1.0
    fractal_depth: int  # For complex patterns

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "primary_color": list(self.primary_color),
            "secondary_color": list(self.secondary_color),
            "aura_color": list(self.aura_color),
            "size": self.size,
            "pulse_rate": self.pulse_rate,
            "rotation_speed": self.rotation_speed,
            "pattern": self.pattern.value,
            "particle_density": self.particle_density,
            "glow_intensity": self.glow_intensity,
            "fractal_depth": self.fractal_depth,
        }


class LUKHASOrb:
    """
    LUKHAS ORB Visualization Engine

    Creates dynamic visual representations of user consciousness state
    for use in authentication and identity visualization.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.current_state: Optional[OrbState] = None
        self.visualization: Optional[OrbVisualization] = None
        self.animation_frame = 0
        self.start_time = time.time()

        # Configuration
        self.enable_particles = self.config.get("enable_particles", True)
        self.enable_aura = self.config.get("enable_aura", True)
        self.enable_fractals = self.config.get("enable_fractals", True)
        self.smoothing_factor = self.config.get("smoothing_factor", 0.15)

        # State history for smooth transitions
        self.state_history: list[OrbState] = []
        self.max_history = 10

    def update_state(self, state: OrbState) -> OrbVisualization:
        """
        Update ORB state and generate new visualization

        Args:
            state: New ORB state

        Returns:
            Updated visualization
        """
        self.current_state = state
        self.state_history.append(state)

        # Keep history limited
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

        # Generate visualization based on current state
        self.visualization = self._generate_visualization(state)
        return self.visualization

    def _generate_visualization(self, state: OrbState) -> OrbVisualization:
        """Generate visualization parameters from state"""

        # Get base colors
        consciousness_color = CONSCIOUSNESS_COLORS.get(state.consciousness_category, CONSCIOUSNESS_COLORS["neutral"])
        emotional_color = EMOTIONAL_COLORS.get(state.emotional_state, EMOTIONAL_COLORS["neutral"])
        tier_info = TIER_AURAS.get(state.tier_level, TIER_AURAS[0])

        # Blend consciousness and emotional colors
        primary_color = self._blend_colors(consciousness_color, emotional_color, 0.7)

        # Secondary color based on neural synchrony
        secondary_color = self._modulate_color(primary_color, state.neural_synchrony)

        # Size based on consciousness level and confidence
        base_size = 1.0 + (state.consciousness_level * 0.5)
        size = base_size * (0.8 + state.authentication_confidence * 0.4)

        # Pulse rate based on emotional state and neural synchrony
        base_pulse = self._get_emotional_pulse_rate(state.emotional_state)
        pulse_rate = base_pulse * (0.5 + state.neural_synchrony * 1.5)

        # Rotation based on consciousness level
        rotation_speed = state.consciousness_level * 2.0

        # Pattern selection based on tier and consciousness
        pattern = self._select_pattern(state)

        # Particle density based on tier and consciousness
        particle_density = int(50 + (state.tier_level * 20) + (state.consciousness_level * 100))

        # Glow intensity based on authentication confidence
        glow_intensity = 0.3 + (state.authentication_confidence * 0.7)

        # Fractal depth for higher tiers
        fractal_depth = 0 if state.tier_level < 3 else (state.tier_level - 2) * 2

        return OrbVisualization(
            primary_color=primary_color,
            secondary_color=secondary_color,
            aura_color=tier_info["color"],
            size=size,
            pulse_rate=pulse_rate,
            rotation_speed=rotation_speed,
            pattern=pattern,
            particle_density=particle_density,
            glow_intensity=glow_intensity,
            fractal_depth=fractal_depth,
        )

    def _blend_colors(
        self, color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float
    ) -> tuple[int, int, int]:
        """Blend two colors with given ratio"""
        return tuple(int(c1 * ratio + c2 * (1 - ratio)) for c1, c2 in zip(color1, color2))

    def _modulate_color(self, base_color: tuple[int, int, int], modulation: float) -> tuple[int, int, int]:
        """Modulate color brightness based on value"""
        factor = 0.5 + modulation * 0.5
        return tuple(min(255, int(c * factor)) for c in base_color)

    def _get_emotional_pulse_rate(self, emotion: str) -> float:
        """Get base pulse rate for emotional state"""
        pulse_rates = {
            "joy": 2.0,
            "excitement": 3.0,
            "stress": 4.0,
            "calm": 0.5,
            "focus": 1.0,
            "neutral": 1.0,
            "love": 1.5,
            "trust": 0.8,
        }
        return pulse_rates.get(emotion, 1.0)

    def _select_pattern(self, state: OrbState) -> OrbPattern:
        """Select animation pattern based on state"""
        tier_info = TIER_AURAS.get(state.tier_level, TIER_AURAS[0])
        base_pattern = tier_info["pattern"]

        # Override with special patterns
        if state.consciousness_level > 0.9:
            return OrbPattern.FRACTAL
        elif state.neural_synchrony > 0.8:
            return OrbPattern.QUANTUM
        elif "dream" in state.attention_focus:
            return OrbPattern.DREAM

        pattern_map = {
            "static": OrbPattern.STATIC,
            "pulse": OrbPattern.PULSE,
            "wave": OrbPattern.WAVE,
            "spiral": OrbPattern.SPIRAL,
            "quantum": OrbPattern.QUANTUM,
            "fractal": OrbPattern.FRACTAL,
        }

        return pattern_map.get(base_pattern, OrbPattern.PULSE)

    def get_animation_frame(self, delta_time: float) -> dict[str, Any]:
        """
        Get current animation frame data

        Args:
            delta_time: Time since last frame

        Returns:
            Frame data for rendering
        """
        if not self.visualization:
            return {}

        self.animation_frame += 1
        elapsed_time = time.time() - self.start_time

        # Calculate current pulse phase
        pulse_phase = (elapsed_time * self.visualization.pulse_rate) % 1.0
        pulse_scale = 1.0 + math.sin(pulse_phase * 2 * math.pi) * 0.1

        # Calculate rotation
        rotation = (elapsed_time * self.visualization.rotation_speed) % 1.0
        rotation_angle = rotation * 360

        # Generate particles if enabled
        particles = []
        if self.enable_particles:
            particles = self._generate_particles(elapsed_time)

        # Generate aura if enabled
        aura_data = {}
        if self.enable_aura:
            aura_data = self._generate_aura(elapsed_time)

        # Pattern-specific animations
        pattern_data = self._generate_pattern_animation(elapsed_time)

        return {
            "frame": self.animation_frame,
            "elapsed_time": elapsed_time,
            "orb": {
                "position": [0, 0, 0],  # Center position
                "scale": self.visualization.size * pulse_scale,
                "rotation": rotation_angle,
                "color": list(self.visualization.primary_color),
                "glow_intensity": self.visualization.glow_intensity,
            },
            "particles": particles,
            "aura": aura_data,
            "pattern": pattern_data,
            "metadata": {
                "consciousness_level": (self.current_state.consciousness_level if self.current_state else 0),
                "pattern_type": self.visualization.pattern.value,
                "tier_level": (self.current_state.tier_level if self.current_state else 0),
            },
        }

    def _generate_particles(self, elapsed_time: float) -> list[dict[str, Any]]:
        """Generate particle positions and properties"""
        particles = []

        for i in range(self.visualization.particle_density):
            # Use deterministic randomness based on particle index
            seed = hashlib.sha256()  #  Changed from MD5 for securityf"{i}{int(elapsed_time}".encode()).hexdigest()
            rand_values = [int(seed[j : j + 2], 16) / 255.0 for j in range(0, 6, 2)]

            # Orbital motion
            angle = (rand_values[0] * 360 + elapsed_time * 30) % 360
            radius = 1.5 + rand_values[1] * 0.5
            height = (rand_values[2] - 0.5) * 0.5

            particle = {
                "id": i,
                "position": [
                    radius * math.cos(math.radians(angle)),
                    height + math.sin(elapsed_time * 2 + i) * 0.1,
                    radius * math.sin(math.radians(angle)),
                ],
                "color": list(self.visualization.secondary_color),
                "size": 0.05 + rand_values[1] * 0.05,
                "opacity": 0.3 + rand_values[2] * 0.7,
            }
            particles.append(particle)

        return particles

    def _generate_aura(self, elapsed_time: float) -> dict[str, Any]:
        """Generate aura effect data"""
        # Aura pulses slightly out of phase with main orb
        aura_phase = (elapsed_time * self.visualization.pulse_rate * 0.8) % 1.0
        aura_scale = 1.5 + math.sin(aura_phase * 2 * math.pi) * 0.2

        return {
            "color": list(self.visualization.aura_color),
            "scale": aura_scale * self.visualization.size,
            "opacity": 0.3 * self.visualization.glow_intensity,
            "blur_radius": 20,
        }

    def _generate_pattern_animation(self, elapsed_time: float) -> dict[str, Any]:
        """Generate pattern-specific animation data"""
        pattern = self.visualization.pattern

        if pattern == OrbPattern.WAVE:
            return {
                "type": "wave",
                "amplitude": 0.1 * self.current_state.neural_synchrony,
                "frequency": 2.0,
                "phase": elapsed_time * 2,
            }
        elif pattern == OrbPattern.SPIRAL:
            return {
                "type": "spiral",
                "turns": 3,
                "speed": self.visualization.rotation_speed,
                "thickness": 0.1,
            }
        elif pattern == OrbPattern.QUANTUM:
            return {
                "type": "quantum",
                "entanglement_nodes": 5,
                "phase_shift": elapsed_time * 0.5,
                "probability_cloud": True,
            }
        elif pattern == OrbPattern.FRACTAL:
            return {
                "type": "fractal",
                "depth": self.visualization.fractal_depth,
                "iteration": int(elapsed_time * 0.5) % 10,
                "complexity": self.current_state.consciousness_level,
            }
        elif pattern == OrbPattern.DREAM:
            return {
                "type": "dream",
                "flow_speed": 0.3,
                "morph_rate": 0.1,
                "dream_symbols": ["∞", "◊", "○", "△", "□"],
            }
        else:
            return {"type": "pulse"}

    def export_state(self) -> dict[str, Any]:
        """Export current ORB state for persistence"""
        if not self.current_state or not self.visualization:
            return {}

        return {
            "state": {
                "consciousness_level": self.current_state.consciousness_level,
                "emotional_state": self.current_state.emotional_state,
                "neural_synchrony": self.current_state.neural_synchrony,
                "tier_level": self.current_state.tier_level,
                "authentication_confidence": self.current_state.authentication_confidence,
                "attention_focus": self.current_state.attention_focus,
                "timestamp": self.current_state.timestamp,
                "user_lambda_id": self.current_state.user_lambda_id,
            },
            "visualization": self.visualization.to_dict(),
            "animation_frame": self.animation_frame,
            "export_timestamp": time.time(),
        }

    def import_state(self, state_data: dict[str, Any]):
        """Import ORB state from persistence"""
        if "state" in state_data:
            state_dict = state_data["state"]
            self.current_state = OrbState(
                consciousness_level=state_dict["consciousness_level"],
                emotional_state=state_dict["emotional_state"],
                neural_synchrony=state_dict["neural_synchrony"],
                tier_level=state_dict["tier_level"],
                authentication_confidence=state_dict["authentication_confidence"],
                attention_focus=state_dict["attention_focus"],
                timestamp=state_dict["timestamp"],
                user_lambda_id=state_dict["user_lambda_id"],
            )

        if self.current_state:
            self.visualization = self._generate_visualization(self.current_state)

        self.animation_frame = state_data.get("animation_frame", 0)
