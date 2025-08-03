"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: emotional_resonance.py
Advanced: emotional_resonance.py
Integration Date: 2025-05-31T07:55:27.776927
"""

"""
Emotional Resonance System for LUKHAS

This module implements an emotional mapping system that processes input contexts
and maps them to emotional states with appropriate intensities. It integrates with
the memory fold system and provides visualization capabilities for emotional states.

The emotional oscillator mechanism is based on frequency ranges:
- Calm (2-3.5 Hz)
- Empathetic (3.5-5 Hz)
- Balanced (5-6.5 Hz)
- Alert (6.5-8 Hz)
- Urgent (8-10 Hz)

Visual representations use emoji indicators: 🟢, 💙, ⚖️, 🟠, 🔴

Valence-Arousal Model:
- Valence: Negative (-1.0) to Positive (1.0)
- Arousal: Low (0.0) to High (1.0)
"""

import json
import math
import random
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Try importing related modules that might exist in the codebase
try:
    from memory.unified_memory_manager import create_memory_fold, recall_memory_folds
except ImportError:
    print("Warning: memory_fold module not found, memory integration will be limited")

try:
    from v1_AGI.memory.memory_emotion_mapper import EmotionalState
    MEMORY_EMOTION_MAPPER_AVAILABLE = True
except ImportError:
    MEMORY_EMOTION_MAPPER_AVAILABLE = False
    print("Warning: memory_emotion_mapper module not found, using local emotional state")

try:
    from symbolic_world import SymbolicWorld
    SYMBOLIC_WORLD_AVAILABLE = True
except ImportError:
    SYMBOLIC_WORLD_AVAILABLE = False
    print("Warning: symbolic_world module not found, symbolic integration will be limited")

# Emotional state definitions
EMOTIONAL_STATES = {
    "calm": {
        "frequency_range": (2.0, 3.5),
        "visual_cue": "🟢",
        "auditory_cue": "low_hum",
        "description": "Relaxed, peaceful, contemplative state",
        "resonance_pattern": "stable_low",
        "valence": 0.5,
        "arousal": 0.2
    },
    "empathetic": {
        "frequency_range": (3.5, 5.0),
        "visual_cue": "💙",
        "auditory_cue": "soft_chime",
        "description": "Connected, understanding, compassionate state",
        "resonance_pattern": "wave_gentle",
        "valence": 0.7,
        "arousal": 0.4
    },
    "balanced": {
        "frequency_range": (5.0, 6.5),
        "visual_cue": "⚖️",
        "auditory_cue": "neutral_tone",
        "description": "Centered, objective, analytical state",
        "resonance_pattern": "balanced_oscillation",
        "valence": 0.5,
        "arousal": 0.5
    },
    "alert": {
        "frequency_range": (6.5, 8.0),
        "visual_cue": "🟠",
        "auditory_cue": "alert_chime",
        "description": "Focused, attentive, vigilant state",
        "resonance_pattern": "rapid_pulse",
        "valence": 0.3,
        "arousal": 0.8
    },
    "urgent": {
        "frequency_range": (8.0, 10.0),
        "visual_cue": "🔴",
        "auditory_cue": "alarm",
        "description": "Intense, critical, immediate response state",
        "resonance_pattern": "high_intensity_wave",
        "valence": 0.0,
        "arousal": 1.0
    },
    "joyful": {
        "frequency_range": (4.0, 6.0),
        "visual_cue": "😊",
        "auditory_cue": "upbeat_melody",
        "description": "Happy, positive, uplifted state",
        "resonance_pattern": "harmonic_rise",
        "valence": 0.9,
        "arousal": 0.7
    },
    "curious": {
        "frequency_range": (4.5, 6.5),
        "visual_cue": "🤔",
        "auditory_cue": "light_ping",
        "description": "Inquisitive, interested, exploratory state",
        "resonance_pattern": "questioning_pattern",
        "valence": 0.6,
        "arousal": 0.6
    },
    "thoughtful": {
        "frequency_range": (3.0, 4.5),
        "visual_cue": "💭",
        "auditory_cue": "deep_hum",
        "description": "Reflective, contemplative, philosophical state",
        "resonance_pattern": "slow_wave",
        "valence": 0.5,
        "arousal": 0.3
    }
}

# Emotion map for valence-arousal space
VALENCE_AROUSAL_MAP = {
    # Format: (valence_center, arousal_center): "emotion_name"
    (0.9, 0.8): "joyful",
    (0.7, 0.4): "empathetic",
    (0.6, 0.6): "curious", 
    (0.5, 0.3): "thoughtful",
    (0.5, 0.5): "balanced",
    (0.5, 0.2): "calm",
    (0.3, 0.8): "alert",
    (0.0, 1.0): "urgent"
}

class EmotionalResonance:
    """
    Main class for handling emotional mapping and resonance.
    """
    
    def __init__(self, 
                 base_frequency: float = 5.0, 
                 intensity_scale: float = 1.0,
                 symbolic_world: Optional[Any] = None,
                 emotional_state_symbol_name: str = "system_emotional_state"):
        """
        Initialize the emotional resonance system.
        
        Args:
            base_frequency: The default frequency to center around (balanced state)
            intensity_scale: Scaling factor for emotional intensity
            symbolic_world: Optional instance of SymbolicWorld for knowledge graph integration
            emotional_state_symbol_name: Name of the symbol to represent this system's emotion
        """
        self.base_frequency = base_frequency
        self.intensity_scale = intensity_scale
        self.current_state = "balanced"
        self.current_intensity = 0.5
        self.valence = 0.5  # Neutral valence
        self.arousal = 0.5  # Moderate arousal
        self.emotional_history = []
        self.last_update = datetime.now()
        self.emotional_contagion_factor = 0.3  # How much external emotions influence
        self.emotional_inertia = 0.7  # Resistance to emotional change
        
        # SymbolicWorld integration
        self.symbolic_world = symbolic_world if SYMBOLIC_WORLD_AVAILABLE else None
        self.emotional_state_symbol_name = emotional_state_symbol_name
        
        # Voice modulation history for tracking changes over time
        self.voice_modulation_history = []
    
    def map_emotion(self, input_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps input context to an emotional state with intensity.
        
        Args:
            input_context: Dictionary containing contextual information
                theta: Angular orientation (psychological valence)
                freq: Base frequency component (arousal)
                sigma_x, sigma_y: Spread parameters (specificity of emotion)
                amplitude: Overall intensity
                context_tags: List of contextual tags
                valence: Optional direct valence value (-1.0 to 1.0)
                arousal: Optional direct arousal value (0.0 to 1.0)
                external_emotion: Optional external emotion to be influenced by
                
        Returns:
            Dictionary containing emotional state mapping
        """
        # Extract input values or use defaults
        theta = input_context.get("theta", 45)
        freq = input_context.get("freq", 0.6)
        sigma_x = input_context.get("sigma_x", 10)
        sigma_y = input_context.get("sigma_y", 10)
        amplitude = input_context.get("amplitude", 0.7)
        context_tags = input_context.get("context_tags", [])
        
        # Direct valence-arousal inputs if provided
        input_valence = input_context.get("valence")
        input_arousal = input_context.get("arousal")
        
        # External emotion that can influence this system (emotional contagion)
        external_emotion = input_context.get("external_emotion")
        
        # Previous values with inertia applied
        prev_valence = self.valence
        prev_arousal = self.arousal
        
        # Calculate new valence and arousal
        if input_valence is not None and input_arousal is not None:
            # Direct input of valence-arousal values
            new_valence = max(-1.0, min(1.0, input_valence))
            new_arousal = max(0.0, min(1.0, input_arousal))
        else:
            # Calculate from theta and amplitude
            # Normalize theta to 0-360 degrees
            theta_norm = theta % 360
            
            # Theta determines valence:
            # 0° = neutral, 90° = maximum positive, 270° = maximum negative
            calculated_valence = math.cos(math.radians(theta_norm))
            
            # Amplitude and frequency affect arousal
            calculated_arousal = amplitude * (0.5 + 0.5 * freq)
            
            new_valence = calculated_valence
            new_arousal = calculated_arousal
        
        # Apply emotional contagion if external emotion is provided
        if external_emotion and isinstance(external_emotion, dict):
            ext_valence = external_emotion.get("valence", 0.5)
            ext_arousal = external_emotion.get("arousal", 0.5)
            
            # Blend with external emotion based on contagion factor
            new_valence = (1 - self.emotional_contagion_factor) * new_valence + self.emotional_contagion_factor * ext_valence
            new_arousal = (1 - self.emotional_contagion_factor) * new_arousal + self.emotional_contagion_factor * ext_arousal
        
        # Apply emotional inertia (emotions change gradually)
        self.valence = self.emotional_inertia * prev_valence + (1 - self.emotional_inertia) * new_valence
        self.arousal = self.emotional_inertia * prev_arousal + (1 - self.emotional_inertia) * new_arousal
        
        # Normalize valence to -1.0 to 1.0
        self.valence = max(-1.0, min(1.0, self.valence))
        # Convert to 0.0-1.0 range for compatibility
        valence_normalized = (self.valence + 1) / 2
        # Normalize arousal to 0.0 to 1.0
        self.arousal = max(0.0, min(1.0, self.arousal))
        
        # Map valence-arousal to an emotional state
        emotion_state = self._map_valence_arousal_to_emotion(valence_normalized, self.arousal)
        
        # Calculate emotional state parameters
        emotion_frequency = self._get_frequency_for_emotion(emotion_state)
        
        # Calculate intensity based on arousal
        intensity = self.arousal
        
        # Generate resonance pattern based on emotion state
        resonance_pattern = self._generate_resonance_pattern(
            emotion_state, 
            intensity,
            sigma_x,
            sigma_y
        )
        
        # Update current state
        self.current_state = emotion_state
        self.current_intensity = intensity
        
        # Record in emotional history
        timestamp = datetime.now()
        self.emotional_history.append({
            "timestamp": timestamp,
            "state": emotion_state,
            "intensity": intensity,
            "valence": valence_normalized,
            "arousal": self.arousal,
            "context_tags": context_tags,
            "frequency": emotion_frequency
        })
        self.last_update = timestamp
        
        # Create result
        result = {
            "emotional_state": emotion_state,
            "intensity": intensity,
            "frequency": emotion_frequency,
            "visual_cue": EMOTIONAL_STATES[emotion_state]["visual_cue"],
            "auditory_cue": EMOTIONAL_STATES[emotion_state]["auditory_cue"],
            "description": EMOTIONAL_STATES[emotion_state]["description"],
            "resonance_pattern": resonance_pattern,
            "valence": valence_normalized,
            "arousal": self.arousal
        }
        
        # Try to integrate with memory systems if available
        self._integrate_with_memory(emotion_state, intensity, context_tags, timestamp)
        
        return result
    
    def _map_valence_arousal_to_emotion(self, valence: float, arousal: float) -> str:
        """
        Maps a valence-arousal pair to the closest named emotional state.
        
        Args:
            valence: Normalized valence value (0.0 to 1.0)
            arousal: Arousal value (0.0 to 1.0)
            
        Returns:
            The name of the closest emotional state
        """
        # Find closest emotion in valence-arousal space using Euclidean distance
        min_distance = float('inf')
        closest_emotion = "balanced"  # Default
        
        for (v_center, a_center), emotion in VALENCE_AROUSAL_MAP.items():
            distance = math.sqrt((valence - v_center)**2 + (arousal - a_center)**2)
            if distance < min_distance:
                min_distance = distance
                closest_emotion = emotion
        
        return closest_emotion
    
    def _get_frequency_for_emotion(self, emotion_state: str) -> float:
        """
        Get the frequency for a given emotional state, using the middle of its range.
        
        Args:
            emotion_state: The emotional state name
            
        Returns:
            The frequency value
        """
        min_freq, max_freq = EMOTIONAL_STATES[emotion_state]["frequency_range"]
        return (min_freq + max_freq) / 2
    
    def _integrate_with_memory(self, emotion_state: str, intensity: float, 
                              context_tags: List[str], timestamp: datetime) -> None:
        """
        Integrate emotional state with memory systems if available.
        
        Args:
            emotion_state: Current emotional state
            intensity: Emotional intensity
            context_tags: Context tags for memory
            timestamp: Current timestamp
        """
        # Try to create a memory fold if the module is available
        try:
            memory_fold_data = {
                "emotion_tag": emotion_state,
                "intensity": intensity,
                "context": context_tags,
                "timestamp": timestamp.isoformat(),
                "valence": self.valence,
                "arousal": self.arousal
            }
            create_memory_fold(memory_fold_data)
        except (NameError, Exception):
            # Function doesn't exist or failed, just continue
            pass
            
        # Try to integrate with EmotionalState from memory_emotion_mapper if available
        if MEMORY_EMOTION_MAPPER_AVAILABLE:
            try:
                emotional_state = EmotionalState(
                    name=emotion_state,
                    valence=self.valence,
                    arousal=self.arousal,
                    intensity=intensity,
                    timestamp=timestamp
                )
                # Here you might want to pass this to some memory system
            except Exception:
                pass
        
        # Integrate with symbolic world if available
        if self.symbolic_world:
            # Create an emotion event in the symbolic world
            event_symbol_name = f"emotional_event_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
            event_properties = {
                "type": "emotional_event_record",
                "emotion_state_name": emotion_state,
                "intensity": intensity,
                "valence": self.valence,
                "arousal": self.arousal,
                "context_tags": context_tags,
                "timestamp": timestamp.isoformat(),
                "source_module": self.__class__.__name__
            }
            
            # Create the emotion event symbol
            event_symbol = self.symbolic_world.create_symbol(event_symbol_name, event_properties)
            
            # Link to the main emotional state symbol
            if self.emotional_state_symbol_name in self.symbolic_world.symbols:
                main_emotion_symbol = self.symbolic_world.symbols[self.emotional_state_symbol_name]
                self.symbolic_world.link_symbols(
                    event_symbol,
                    main_emotion_symbol,
                    relationship_type="influences_current_state",
                    properties={"influence_timestamp": timestamp.isoformat()}
                )
            else:
                # Create the main emotional state symbol if it doesn't exist
                main_emotion_properties = {
                    "type": "emotional_state_snapshot",
                    "state_name": emotion_state,
                    "intensity": intensity,
                    "valence": self.valence,
                    "arousal": self.arousal,
                    "last_updated_timestamp": timestamp.isoformat(),
                    "source_module": self.__class__.__name__
                }
                main_emotion_symbol = self.symbolic_world.create_symbol(
                    self.emotional_state_symbol_name, 
                    main_emotion_properties
                )
            
            # Link the event to relevant context tags if they exist in the symbolic world
            for tag in context_tags:
                tag_symbol_name = tag.lower().replace(" ", "_").replace("-", "_")
                if tag_symbol_name in self.symbolic_world.symbols:
                    tagged_item_symbol = self.symbolic_world.symbols[tag_symbol_name]
                    self.symbolic_world.link_symbols(
                        event_symbol,
                        tagged_item_symbol,
                        relationship_type="emotionally_associated_with",
                        properties={"association_timestamp": timestamp.isoformat()}
                    )
    
    def _generate_resonance_pattern(self, 
                                   emotion_state: str, 
                                   intensity: float,
                                   sigma_x: float,
                                   sigma_y: float) -> List[float]:
        """
        Generate a resonance pattern based on emotional state and intensity.
        This simulates the "Gabbor resonance engine" concept.
        
        Returns:
            List of values representing the resonance pattern (20 points)
        """
        pattern = []
        pattern_type = EMOTIONAL_STATES[emotion_state]["resonance_pattern"]
        
        # Number of points in the pattern
        num_points = 20
        
        for i in range(num_points):
            x = i / (num_points - 1)  # Normalize to 0-1
            
            if pattern_type == "stable_low":
                # Low amplitude sine wave with minimal variation
                value = 0.3 * intensity * math.sin(2 * math.pi * x) + 0.2
            elif pattern_type == "wave_gentle":
                # Gentle wave pattern with moderate amplitude
                value = 0.5 * intensity * math.sin(3 * math.pi * x) + 0.3
            elif pattern_type == "balanced_oscillation":
                # Regular oscillation centered at midpoint
                value = 0.4 * intensity * math.sin(4 * math.pi * x) + 0.5
            elif pattern_type == "rapid_pulse":
                # More frequent oscillations with higher baseline
                value = 0.3 * intensity * math.sin(6 * math.pi * x) + 0.6
            elif pattern_type == "high_intensity_wave":
                # High frequency, high amplitude pattern
                value = 0.6 * intensity * math.sin(8 * math.pi * x) + 0.7
            elif pattern_type == "harmonic_rise":
                # Rising harmonic pattern for joy
                value = 0.5 * intensity * (math.sin(3 * math.pi * x) + math.sin(5 * math.pi * x)) / 2 + 0.6
            elif pattern_type == "questioning_pattern":
                # Pattern that rises then falls, like a question
                value = 0.4 * intensity * math.sin(3 * math.pi * x * (1 + x)) + 0.5
            elif pattern_type == "slow_wave":
                # Very slow, thoughtful oscillation
        valence_values = [entry.get("valence", 0.5) for entry in relevant_history]
        arousal_values = [entry.get("arousal", 0.5) for entry in relevant_history]
        
        # Calculate valence trend
        if len(valence_values) >= 2:
            valence_start = sum(valence_values[:len(valence_values)//3]) / (len(valence_values)//3 or 1)
            valence_end = sum(valence_values[-len(valence_values)//3:]) / (len(valence_values)//3 or 1)
            if valence_end > valence_start + 0.1:
                valence_trend = "improving"
            elif valence_end < valence_start - 0.1:
                valence_trend = "declining"
            else:
                valence_trend = "stable"
        else:
            valence_trend = "insufficient_data"
            
        # Calculate arousal trend
        if len(arousal_values) >= 2:
            arousal_start = sum(arousal_values[:len(arousal_values)//3]) / (len(arousal_values)//3 or 1)
            arousal_end = sum(arousal_values[-len(arousal_values)//3:]) / (len(arousal_values)//3 or 1)
            if arousal_end > arousal_start + 0.1:
                arousal_trend = "increasing"
            elif arousal_end < arousal_start - 0.1:
                arousal_trend = "decreasing"
            else:
                arousal_trend = "stable"
        else:
            arousal_trend = "insufficient_data"
        
        # Determine overall trend direction
        if len(relevant_history) >= 2:
            # Calculate average frequency for first and last thirds
            third_size = max(1, len(relevant_history) // 3)
            first_third = relevant_history[:third_size]
            last_third = relevant_history[-third_size:]
            
            first_avg_freq = sum(e["frequency"] for e in first_third) / len(first_third)
            last_avg_freq = sum(e["frequency"] for e in last_third) / len(last_third)
            
            if last_avg_freq > first_avg_freq + 0.5:
                trend = "intensifying"
            elif last_avg_freq < first_avg_freq - 0.5:
                trend = "calming"
            else:
                trend = "steady"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "stability": stability,
            "dominant_state": dominant_state,
            "state_distribution": {
                state: count/total for state, count in state_counts.items()
            },
            "valence_trend": valence_trend,
            "arousal_trend": arousal_trend,
            "average_valence": sum(valence_values) / len(valence_values) if valence_values else 0.5,
            "average_arousal": sum(arousal_values) / len(arousal_values) if arousal_values else 0.5
        }
    
    def visualize_emotional_state(self) -> str:
        """
        Create a simple text-based visualization of the current emotional state.
        
        Returns:
            String containing visualization
        """
        state = self.current_state
        intensity = self.current_intensity
        visual_cue = EMOTIONAL_STATES[state]["visual_cue"]
        
        # Create a bar to visualize intensity
        bar_length = 20
        filled = int(bar_length * intensity)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Create valence-arousal visualization
        valence_normalized = (self.valence + 1) / 2  # Convert from -1..1 to 0..1
        valence_bar_length = 10
        valence_midpoint = valence_bar_length // 2
        valence_position = int(valence_normalized * valence_bar_length)
        
        valence_bar = "░" * valence_bar_length
        valence_bar = valence_bar[:valence_position] + "●" + valence_bar[valence_position+1:]
        
        arousal_bar_length = 10
        arousal_position = int(self.arousal * arousal_bar_length)
        arousal_bar = "░" * arousal_bar_length
        arousal_bar = arousal_bar[:arousal_position] + "●" + arousal_bar[arousal_position+1:]
        
        visualization = f"""
Emotional State: {state.upper()} {visual_cue}
Intensity: [{bar}] {intensity:.2f}
Valence:   [-{valence_bar}+] {self.valence:.2f}
Arousal:   [0{arousal_bar}1] {self.arousal:.2f}
Frequency: {self._get_frequency_for_emotion(state):.1f} Hz
Description: {EMOTIONAL_STATES[state]["description"]}
Last Updated: {self.last_update.strftime('%H:%M:%S')}
        """
        
        return visualization
    
    def generate_valence_arousal_plot(self) -> Optional[str]:
        """
        Generate a valence-arousal plot of the emotional state.
        
        Returns:
            Base64 encoded PNG image or None if matplotlib is not available
        """
        try:
            # Create valence-arousal plot
            fig, ax = plt.subplots(figsize=(5, 5))
            
            # Set up the plot
            ax.set_xlim(-1, 1)
            ax.set_ylim(0, 1)
            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
            ax.set_xlabel('Valence')
            ax.set_ylabel('Arousal')
            ax.set_title('Emotional State in Valence-Arousal Space')
            
            # Plot emotion regions
            for (v, a), emotion in VALENCE_AROUSAL_MAP.items():
                v_adjusted = v * 2 - 1  # Convert from 0..1 to -1..1
                ax.scatter(v_adjusted, a, alpha=0.3, s=300)
                ax.annotate(emotion, (v_adjusted, a), fontsize=8)
            
            # Plot current state
            ax.scatter([self.valence], [self.arousal], color='red', s=100)
            ax.annotate(f'Current: {self.current_state}', 
                        (self.valence, self.arousal),
                        xytext=(10, 10),
                        textcoords='offset points',
                        fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
            
            # Add emotional trajectory if history exists
            if len(self.emotional_history) > 1:
                # Get last 10 states or all if less than 10
                history = self.emotional_history[-10:]
                
                # Extract valence and arousal, converting valence from 0..1 to -1..1 if needed
                valences = []
                arousals = []
                
                for entry in history:
                    val = entry.get("valence", 0.5)
                    # Check if valence is already in -1..1 range or needs conversion
                    if 0 <= val <= 1:
                        val = val * 2 - 1  # Convert from 0..1 to -1..1
                    valences.append(val)
                    arousals.append(entry.get("arousal", 0.5))
                
                # Plot the trajectory with increasing opacity
                for i in range(len(valences)-1):
                    alpha = 0.3 + 0.7 * (i / (len(valences)-1))
                    ax.plot(valences[i:i+2], arousals[i:i+2], 'b-', alpha=alpha, linewidth=1.5)
            
            # Save plot to a bytes buffer
            buf = BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            # Convert to base64
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return img_base64
        
        except Exception as e:
            print(f"Error generating emotion plot: {e}")
            return None
    
    def modulate_voice_parameters(self, custom_calibration: Dict[str, float] = None) -> Dict[str, float]:
        """
        Generate voice modulation parameters based on current emotional state.
        Integrates with symbolic world if available to enrich voice modulation.
        
        Args:
            custom_calibration: Optional custom calibration parameters
        
        Returns:
            Dictionary containing voice modulation parameters
        """
        state = self.current_state
        intensity = self.current_intensity
        
        # Default voice parameters
        params = {
            "pitch": 1.0,      # Multiplier for base pitch
            "speed": 1.0,      # Multiplier for speaking speed
            "volume": 1.0,     # Multiplier for volume
            "timbre": 0.5,     # 0-1 scale (soft to harsh)
            "breathiness": 0.2, # 0-1 scale
            "articulation": 0.5, # 0-1 scale (slurred to precise)
            "resonance": 0.5,   # 0-1 scale (thin to resonant)
            "inflection": 0.5,  # 0-1 scale (monotone to expressive)
            "vibrato": 0.0,     # 0-1 scale (amount of vibrato effect)
            "vocal_tension": 0.5 # 0-1 scale (relaxed to tense)
        }
        
        # Adjust parameters based on emotional state
        if state == "calm":
            params["pitch"] = 0.9
            params["speed"] = 0.85
            params["volume"] = 0.8
            params["timbre"] = 0.3
            params["breathiness"] = 0.4
            params["articulation"] = 0.7
            params["resonance"] = 0.6
            params["inflection"] = 0.4
            params["vibrato"] = 0.1
            params["vocal_tension"] = 0.3
        elif state == "empathetic":
            params["pitch"] = 0.95
            params["speed"] = 0.9
            params["volume"] = 0.9
            params["timbre"] = 0.4
            params["breathiness"] = 0.3
            params["articulation"] = 0.6
            params["resonance"] = 0.7
            params["inflection"] = 0.6
            params["vibrato"] = 0.2
            params["vocal_tension"] = 0.4
        elif state == "balanced":
            # Default parameters are already balanced
            pass
        elif state == "alert":
            params["pitch"] = 1.1
            params["speed"] = 1.1
            params["volume"] = 1.2
            params["timbre"] = 0.6
            params["breathiness"] = 0.1
            params["articulation"] = 0.8
            params["resonance"] = 0.5
            params["inflection"] = 0.7
            params["vibrato"] = 0.1
            params["vocal_tension"] = 0.6
        elif state == "urgent":
            params["pitch"] = 1.2
            params["speed"] = 1.3
            params["volume"] = 1.4
            params["timbre"] = 0.6
            params["breathiness"] = 0.1
            params["articulation"] = 0.9
            params["resonance"] = 0.4
            params["inflection"] = 0.8
            params["vibrato"] = 0.05
            params["vocal_tension"] = 0.8
        elif state == "joyful":
            params["pitch"] = 1.15
            params["speed"] = 1.1
            params["volume"] = 1.1
            params["timbre"] = 0.4
            params["breathiness"] = 0.15
            params["articulation"] = 0.7
            params["resonance"] = 0.7
            params["inflection"] = 0.8
            params["vibrato"] = 0.25
            params["vocal_tension"] = 0.3
        elif state == "curious":
            params["pitch"] = 1.05
            params["speed"] = 0.95
            params["volume"] = 0.9
            params["timbre"] = 0.45
            params["breathiness"] = 0.2
            params["articulation"] = 0.65
            params["resonance"] = 0.6
            params["inflection"] = 0.7
            params["vibrato"] = 0.15
            params["vocal_tension"] = 0.4
        elif state == "thoughtful":
            params["pitch"] = 0.9
            params["speed"] = 0.8
            params["volume"] = 0.85
            params["timbre"] = 0.35
            params["breathiness"] = 0.25
            params["articulation"] = 0.7
            params["resonance"] = 0.65
            params["inflection"] = 0.5
            params["vibrato"] = 0.1
            params["vocal_tension"] = 0.3
        
        # Further adjust based on valence and arousal directly
        # Valence affects pitch and timbre
        valence_factor = (self.valence + 1) / 2  # Convert to 0-1 range
        params["pitch"] *= 0.9 + 0.2 * valence_factor  # Higher pitch for positive valence
        params["timbre"] = 0.7 - 0.4 * valence_factor  # Softer timbre for positive valence
        params["inflection"] = 0.3 + 0.5 * valence_factor  # More varied inflection for positive valence
        
        # Arousal affects speed, volume and articulation
        params["speed"] *= 0.8 + 0.4 * self.arousal  # Higher speed for higher arousal
        params["volume"] *= 0.8 + 0.4 * self.arousal  # Higher volume for higher arousal
        params["articulation"] = 0.4 + 0.6 * self.arousal  # More precise articulation with higher arousal
        params["vocal_tension"] = 0.3 + 0.7 * self.arousal  # Higher tension with higher arousal
        
        # Apply intensity scaling
        intensity_factor = 0.5 + 0.5 * intensity
        for param in ["pitch", "speed", "volume"]:
            params[param] = 1.0 + (params[param] - 1.0) * intensity_factor
            
        # Apply custom calibration if provided
        if custom_calibration:
            for param, value in custom_calibration.items():
                if param in params:
                    params[param] = value
        
        # Record voice modulation in history for trend analysis
        timestamp = datetime.now()
        self.voice_modulation_history.append({
            "timestamp": timestamp,
            "parameters": params.copy(),
            "emotional_state": state,
            "valence": self.valence,
            "arousal": self.arousal
        })
        
        # Trim history if it gets too long
        if len(self.voice_modulation_history) > 100:
            self.voice_modulation_history = self.voice_modulation_history[-100:]
        
        # Integrate with symbolic world if available
        if self.symbolic_world and self.emotional_state_symbol_name in self.symbolic_world.symbols:
            voice_params = {f"voice_{k}": v for k, v in params.items()}
            
            # Update the voice parameters on the emotional state symbol
            emotion_symbol = self.symbolic_world.symbols[self.emotional_state_symbol_name]
            for param_name, param_value in voice_params.items():
                emotion_symbol.update_property(param_name, param_value)
            
            # Create a voice modulation event in the symbolic world
            modulation_symbol_name = f"voice_modulation_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
            modulation_properties = {
                "type": "voice_modulation_snapshot",
                "timestamp": timestamp.isoformat(),
                "emotional_state": state,
                "valence": self.valence,
                "arousal": self.arousal,
                "source_module": self.__class__.__name__,
                **voice_params
            }
            
            # Create the symbol and link it to the emotional state
            modulation_symbol = self.symbolic_world.create_symbol(modulation_symbol_name, modulation_properties)
            self.symbolic_world.link_symbols(
                modulation_symbol,
                emotion_symbol,
                relationship_type="expresses_emotion_through_voice",
                properties={"timestamp": timestamp.isoformat()}
            )
        
        return params
    
    def get_emotion_from_context(self, context_text: str) -> Dict[str, Any]:
        """
        Attempt to extract emotional content from text.
        This is a simplified implementation. In a production system, 
        this would use NLP for sentiment analysis.
        
        Args:
            context_text: The text to analyze
            
        Returns:
            Dictionary with valence and arousal values
        """
        # This is a placeholder for a more sophisticated NLP approach
        # In a real implementation, you'd use a proper sentiment analysis model
        
        # Very simplified lexicon approach
        positive_words = ["good", "great", "happy", "excellent", "joy", "love", "wonderful",
                         "amazing", "awesome", "positive", "excited"]
        negative_words = ["bad", "terrible", "sad", "awful", "hate", "angry", "frustrated",
                         "disappointed", "negative", "upset", "worried", "fear"]
        high_arousal = ["excited", "angry", "urgent", "emergency", "critical", "immediately",
                      "now", "danger", "alert", "warning", "rush", "fast"]
        low_arousal = ["calm", "peaceful", "relaxed", "serene", "gentle", "quiet", 
                      "slow", "steady", "stable", "tranquil"]
        
        # Normalize and tokenize
        text = context_text.lower()
        words = text.split()
        
        # Count occurrences
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        high_count = sum(1 for word in words if word in high_arousal)
        low_count = sum(1 for word in words if word in low_arousal)
        
        # Get total counts
        total_valence = pos_count + neg_count
        total_arousal = high_count + low_count
        
        # Calculate valence and arousal
        valence = 0.0
        if total_valence > 0:
            valence = (pos_count - neg_count) / total_valence
        
        arousal = 0.5  # Default moderate arousal
        if total_arousal > 0:
            arousal = (high_count) / total_arousal
        
        return {
            "valence": valence,
            "arousal": arousal,
            "intensity": (abs(valence) + arousal) / 2
        }
    
    def emotional_feedback_loop(self, context_text: str, response_type: str = "text") -> Dict[str, Any]:
        """
        Process text input, extract emotions, and provide appropriate response.
        
        Args:
            context_text: Input text to process
            response_type: Type of response (text, visual, voice)
            
        Returns:
            Dictionary with emotional response data
        """
        # Extract emotional content from input
        extracted_emotion = self.get_emotion_from_context(context_text)
        
        # Update emotional state with the extracted emotion
        input_context = {
            "valence": extracted_emotion["valence"],
            "arousal": extracted_emotion["arousal"],
            "amplitude": extracted_emotion["intensity"],
            "context_tags": ["textual_input"]
        }
        
        emotional_state = self.map_emotion(input_context)
        
        # Generate appropriate response based on response_type
        response_data = {
            "emotional_state": emotional_state["emotional_state"],
            "valence": emotional_state["valence"],
            "arousal": emotional_state["arousal"],
            "intensity": emotional_state["intensity"]
        }
        
        if response_type == "text":
            response_data["response"] = self.visualize_emotional_state()
        elif response_type == "visual":
            response_data["response"] = self.generate_valence_arousal_plot()
        elif response_type == "voice":
            response_data["voice_params"] = self.modulate_voice_parameters()
        
        return response_data