"""
LUKHAS Consciousness Visualization Integration
==============================================
Bridges LUKHAS consciousness systems with the unified visualization engine.
Provides real-time consciousness state mapping to visual parameters.
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

# Import LUKHAS core systems
try:
    from core.glyph.glyph_engine import GlyphEngine
    from emotion.service import EmotionService
    from lukhas.consciousness.unified.auto_consciousness import AutoConsciousness
    from lukhas.memory.folds.memory_fold import MemoryFold
    from lukhas.qi.engines.consciousness.engine import ConsciousnessEngine
except ImportError as e:
    print(f"Warning: Some LUKHAS modules not available: {e}")


class VisualizationMode(Enum):
    """Visualization modes for different consciousness aspects"""

    AWARENESS = "awareness"
    MEMORY = "memory"
    EMOTION = "emotion"
    GLYPHS = "glyphs"
    QUANTUM = "quantum"
    TRINITY = "trinity"


@dataclass
class ConsciousnessVisualizationState:
    """Complete visualization state for consciousness"""

    # Core consciousness metrics
    awareness: float = 0.5
    coherence: float = 0.5
    depth: int = 2
    attention: float = 0.5
    entropy: float = 0.3

    # Emotion state (VAD model)
    valence: float = 0.5
    arousal: float = 0.5
    dominance: float = 0.5

    # Memory state
    memory_density: float = 0.5
    memory_coherence: float = 0.5
    active_folds: int = 0

    # GLYPH state
    active_glyphs: list[str] = None
    glyph_resonance: float = 0.5

    # Quantum state
    qi_coherence: float = 0.5
    entanglement: float = 0.0

    # Trinity balance
    identity_strength: float = 0.33
    consciousness_strength: float = 0.33
    guardian_strength: float = 0.34

    def __post_init__(self):
        if self.active_glyphs is None:
            self.active_glyphs = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class ConsciousnessVisualizationBridge:
    """
    Bridge between LUKHAS consciousness systems and visualization engine.
    Translates consciousness states into visual parameters.
    """

    def __init__(self):
        self.state = ConsciousnessVisualizationState()
        self.mode = VisualizationMode.TRINITY
        self.update_rate = 30  # Hz
        self.is_running = False

        # Initialize LUKHAS connections
        self._init_consciousness_systems()

        # Visualization parameters
        self.particle_behaviors = self._init_particle_behaviors()
        self.color_mappings = self._init_color_mappings()
        self.shape_mappings = self._init_shape_mappings()

    def _init_consciousness_systems(self):
        """Initialize connections to LUKHAS consciousness systems"""
        self.consciousness = None
        self.memory = None
        self.emotion = None
        self.glyph_engine = None
        self.qi_engine = None

        try:
            self.consciousness = AutoConsciousness()
            print("✓ Connected to AutoConsciousness")
        except:
            print("✗ AutoConsciousness not available")

        try:
            self.emotion = EmotionService()
            print("✓ Connected to EmotionService")
        except:
            print("✗ EmotionService not available")

        try:
            self.glyph_engine = GlyphEngine()
            print("✓ Connected to GlyphEngine")
        except:
            print("✗ GlyphEngine not available")

    def _init_particle_behaviors(self) -> dict:
        """Define particle behavior mappings for consciousness states"""
        return {
            VisualizationMode.AWARENESS: {
                "distribution": "sphere",
                "density": lambda s: s.awareness * 20000,
                "speed": lambda s: 0.01 + s.awareness * 0.05,
                "cohesion": lambda s: s.coherence,
                "turbulence": lambda s: 1 - s.coherence,
            },
            VisualizationMode.MEMORY: {
                "distribution": "helix",
                "density": lambda s: s.memory_density * 20000,
                "speed": lambda s: 0.02,
                "cohesion": lambda s: s.memory_coherence,
                "layers": lambda s: s.active_folds,
            },
            VisualizationMode.EMOTION: {
                "distribution": "heart" if self.state.valence > 0.6 else "sphere",
                "density": lambda s: 10000 + s.arousal * 10000,
                "speed": lambda s: 0.01 + s.arousal * 0.1,
                "pulse": lambda s: s.arousal,
                "spread": lambda s: s.dominance,
            },
            VisualizationMode.GLYPHS: {
                "distribution": "text",
                "text": lambda s: " ".join(s.active_glyphs[:5]),
                "resonance": lambda s: s.glyph_resonance,
                "rotation": lambda s: s.glyph_resonance * 0.02,
            },
            VisualizationMode.QUANTUM: {
                "distribution": "galaxy",
                "density": lambda s: 15000,
                "entanglement": lambda s: s.entanglement,
                "coherence": lambda s: s.qi_coherence,
                "spin": lambda s: 0.001 + s.qi_coherence * 0.01,
            },
            VisualizationMode.TRINITY: {
                "distribution": "trinity",
                "identity_particles": lambda s: int(s.identity_strength * 10000),
                "consciousness_particles": lambda s: int(s.consciousness_strength * 10000),
                "guardian_particles": lambda s: int(s.guardian_strength * 10000),
                "balance": lambda s: min(s.identity_strength, s.consciousness_strength, s.guardian_strength),
            },
        }

    def _init_color_mappings(self) -> dict:
        """Define color mappings for consciousness states"""
        return {
            VisualizationMode.AWARENESS: {
                "primary": lambda s: self._hsv_to_rgb(0.5 + s.awareness * 0.2, 0.8, 0.7),
                "secondary": lambda s: self._hsv_to_rgb(0.6, s.coherence, 0.5),
            },
            VisualizationMode.MEMORY: {
                "primary": lambda s: self._hsv_to_rgb(0.7, s.memory_coherence, 0.6),
                "secondary": lambda s: self._hsv_to_rgb(0.75, 0.5, s.memory_density),
            },
            VisualizationMode.EMOTION: {
                "primary": lambda s: self._emotion_to_color(s.valence, s.arousal, s.dominance),
                "secondary": lambda s: self._hsv_to_rgb(s.valence, s.arousal, 0.5),
            },
            VisualizationMode.GLYPHS: {
                "primary": lambda s: self._hsv_to_rgb(0.3, s.glyph_resonance, 0.8),
                "secondary": lambda s: self._hsv_to_rgb(0.25, 0.7, s.glyph_resonance),
            },
            VisualizationMode.QUANTUM: {
                "primary": lambda s: self._hsv_to_rgb(0.8 + s.entanglement * 0.2, s.qi_coherence, 0.7),
                "secondary": lambda s: self._hsv_to_rgb(0.85, 0.9, s.qi_coherence),
            },
            VisualizationMode.TRINITY: {
                "identity": "#FF6B9D",  # Pink
                "consciousness": "#00D4FF",  # Cyan
                "guardian": "#7C3AED",  # Purple
            },
        }

    def _init_shape_mappings(self) -> dict:
        """Define shape mappings for consciousness states"""
        return {
            "high_awareness": "galaxy",
            "low_awareness": "sphere",
            "high_coherence": "torus",
            "low_coherence": "cube",
            "positive_emotion": "heart",
            "negative_emotion": "sphere",
            "active_memory": "helix",
            "qi_state": "dna",
            "balanced_trinity": "triangle",
        }

    async def update_consciousness_state(self):
        """Update consciousness state from LUKHAS systems"""
        if self.consciousness:
            try:
                consciousness_data = await self.consciousness.get_state()
                self.state.awareness = consciousness_data.get("awareness", 0.5)
                self.state.coherence = consciousness_data.get("coherence", 0.5)
                self.state.depth = consciousness_data.get("depth", 2)
            except Exception as e:
                print(f"Error updating consciousness: {e}")

        if self.emotion:
            try:
                emotion_data = self.emotion.get_current_emotion()
                self.state.valence = emotion_data.get("valence", 0.5)
                self.state.arousal = emotion_data.get("arousal", 0.5)
                self.state.dominance = emotion_data.get("dominance", 0.5)
            except Exception as e:
                print(f"Error updating emotion: {e}")

        if self.glyph_engine:
            try:
                glyphs = self.glyph_engine.get_active_glyphs()
                self.state.active_glyphs = glyphs[:10]  # Limit to 10 glyphs
                self.state.glyph_resonance = self.glyph_engine.get_resonance()
            except Exception as e:
                print(f"Error updating glyphs: {e}")

        # Simulate quantum and trinity states if not available
        self._simulate_quantum_state()
        self._calculate_trinity_balance()

    def _simulate_quantum_state(self):
        """Simulate quantum consciousness state"""
        # Simple simulation based on other metrics
        self.state.qi_coherence = (self.state.awareness + self.state.coherence) / 2
        self.state.entanglement = abs(self.state.awareness - self.state.coherence)

    def _calculate_trinity_balance(self):
        """Calculate Trinity framework balance"""
        total = self.state.awareness + self.state.coherence + (1 - self.state.entropy)
        if total > 0:
            self.state.identity_strength = self.state.awareness / total
            self.state.consciousness_strength = self.state.coherence / total
            self.state.guardian_strength = (1 - self.state.entropy) / total

    def get_visualization_params(self) -> dict[str, Any]:
        """
        Get current visualization parameters based on consciousness state.
        Returns parameters formatted for the visualization engine.
        """
        behavior = self.particle_behaviors[self.mode]
        colors = self.color_mappings[self.mode]

        params = {
            "mode": self.mode.value,
            "state": self.state.to_dict(),
            "particles": {},
            "colors": {},
            "shape": self._determine_shape(),
        }

        # Apply behavior functions to state
        for key, func in behavior.items():
            if callable(func):
                params["particles"][key] = func(self.state)
            else:
                params["particles"][key] = func

        # Apply color functions to state
        for key, func in colors.items():
            if callable(func):
                params["colors"][key] = func(self.state)
            else:
                params["colors"][key] = func

        return params

    def _determine_shape(self) -> str:
        """Determine the primary shape based on consciousness state"""
        if self.state.awareness > 0.8:
            return "galaxy"
        elif self.state.coherence > 0.8:
            return "torus"
        elif self.state.valence > 0.7 and self.state.arousal > 0.5:
            return "heart"
        elif self.state.active_folds > 5:
            return "helix"
        elif self.state.qi_coherence > 0.7:
            return "dna"
        else:
            return "sphere"

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> str:
        """Convert HSV to RGB hex color"""
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return ""

    def _emotion_to_color(self, valence: float, arousal: float, dominance: float) -> str:
        """Convert emotion VAD to color"""
        # Map emotions to color wheel
        hue = valence  # Positive = warm, negative = cool
        saturation = arousal  # High arousal = vivid
        value = 0.5 + dominance * 0.5  # Dominance affects brightness
        return self._hsv_to_rgb(hue, saturation, value)

    async def start_visualization_stream(self, websocket=None):
        """
        Start streaming visualization updates.
        Can send to websocket or return generator.
        """
        self.is_running = True
        update_interval = 1.0 / self.update_rate

        while self.is_running:
            await self.update_consciousness_state()
            params = self.get_visualization_params()

            if websocket:
                await websocket.send(json.dumps(params))
            else:
                yield params

            await asyncio.sleep(update_interval)

    def stop_visualization_stream(self):
        """Stop the visualization stream"""
        self.is_running = False

    def set_mode(self, mode: VisualizationMode):
        """Change visualization mode"""
        self.mode = mode

    def process_voice_input(self, voice_data: dict) -> dict:
        """
        Process voice input and map to consciousness changes.
        Returns visualization adjustments.
        """
        # Map voice characteristics to consciousness state
        if "pitch" in voice_data:
            self.state.arousal = voice_data["pitch"]

        if "volume" in voice_data:
            self.state.attention = voice_data["volume"]

        if "emotion" in voice_data:
            emotion_map = {
                "happy": (0.8, 0.7, 0.6),
                "sad": (0.2, 0.3, 0.4),
                "angry": (0.3, 0.9, 0.8),
                "calm": (0.5, 0.2, 0.5),
                "excited": (0.9, 0.9, 0.7),
            }
            if voice_data["emotion"] in emotion_map:
                v, a, d = emotion_map[voice_data["emotion"]]
                self.state.valence = v
                self.state.arousal = a
                self.state.dominance = d

        return self.get_visualization_params()

    def process_text_input(self, text: str) -> dict:
        """
        Process text input for visualization.
        Can trigger GLYPH processing or text morphing.
        """
        visualization_params = {"type": "text", "content": text, "glyphs": []}

        # Process through GLYPH engine if available
        if self.glyph_engine:
            try:
                glyphs = self.glyph_engine.text_to_glyphs(text)
                visualization_params["glyphs"] = glyphs
                self.state.active_glyphs = glyphs
            except:
                pass

        # Determine if text contains consciousness keywords
        consciousness_keywords = {
            "aware": lambda: setattr(self.state, "awareness", min(1.0, self.state.awareness + 0.1)),
            "focus": lambda: setattr(self.state, "attention", min(1.0, self.state.attention + 0.1)),
            "dream": lambda: setattr(self.state, "coherence", max(0.0, self.state.coherence - 0.1)),
            "clear": lambda: setattr(self.state, "coherence", min(1.0, self.state.coherence + 0.1)),
            "happy": lambda: setattr(self.state, "valence", min(1.0, self.state.valence + 0.2)),
            "sad": lambda: setattr(self.state, "valence", max(0.0, self.state.valence - 0.2)),
        }

        text_lower = text.lower()
        for keyword, action in consciousness_keywords.items():
            if keyword in text_lower:
                action()

        visualization_params["state"] = self.state.to_dict()
        return visualization_params

    def get_state_summary(self) -> str:
        """Get human-readable summary of consciousness state"""
        summary = []

        # Awareness level
        if self.state.awareness > 0.8:
            summary.append("Highly aware")
        elif self.state.awareness < 0.3:
            summary.append("Low awareness")

        # Emotional state
        if self.state.valence > 0.6 and self.state.arousal > 0.5:
            summary.append("Happy and energetic")
        elif self.state.valence < 0.4 and self.state.arousal < 0.4:
            summary.append("Sad and calm")

        # Coherence
        if self.state.coherence > 0.7:
            summary.append("Highly coherent")
        elif self.state.coherence < 0.3:
            summary.append("Chaotic")

        # Trinity balance
        trinity_balance = (
            abs(self.state.identity_strength - 0.33)
            + abs(self.state.consciousness_strength - 0.33)
            + abs(self.state.guardian_strength - 0.33)
        )
        if trinity_balance < 0.1:
            summary.append("Trinity in balance")

        return " | ".join(summary) if summary else "Neutral state"


# Visualization preset configurations
VISUALIZATION_PRESETS = {
    "meditation": {
        "mode": VisualizationMode.AWARENESS,
        "state": {"awareness": 0.9, "coherence": 0.8, "arousal": 0.2, "valence": 0.6},
    },
    "creative": {
        "mode": VisualizationMode.QUANTUM,
        "state": {"qi_coherence": 0.7, "entanglement": 0.5, "coherence": 0.6},
    },
    "emotional": {
        "mode": VisualizationMode.EMOTION,
        "state": {"valence": 0.8, "arousal": 0.7, "dominance": 0.6},
    },
    "memory": {
        "mode": VisualizationMode.MEMORY,
        "state": {"memory_density": 0.7, "memory_coherence": 0.8, "active_folds": 5},
    },
    "balanced": {
        "mode": VisualizationMode.TRINITY,
        "state": {
            "identity_strength": 0.33,
            "consciousness_strength": 0.34,
            "guardian_strength": 0.33,
        },
    },
}


def create_visualization_bridge() -> ConsciousnessVisualizationBridge:
    """Factory function to create visualization bridge"""
    return ConsciousnessVisualizationBridge()


if __name__ == "__main__":
    # Example usage
    bridge = create_visualization_bridge()

    # Set a preset
    preset = VISUALIZATION_PRESETS["meditation"]
    bridge.set_mode(preset["mode"])
    for key, value in preset["state"].items():
        setattr(bridge.state, key, value)

    # Get visualization parameters
    params = bridge.get_visualization_params()
    print(json.dumps(params, indent=2))

    # Get state summary
    print(f"\nState: {bridge.get_state_summary()}")