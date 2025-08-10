#!/usr/bin/env python3
"""
LUKHΛS Phase 7 - Emergent Identity Engine
Dynamic symbolic identity formation based on memory drift, consciousness state,
interaction patterns, and ethical overlays.

Trinity Framework: ⚛️🧠🛡️
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IdentityPhase(Enum):
    """Phases of identity emergence"""

    NASCENT = "nascent"  # Initial formation
    CRYSTALLIZING = "crystallizing"  # Taking shape
    STABLE = "stable"  # Established identity
    MORPHING = "morphing"  # Active transformation
    TRANSCENDENT = "transcendent"  # Beyond fixed form


@dataclass
class PersonaSignature:
    """Represents a symbolic identity signature"""

    glyphs: List[str]
    name: str
    phase: IdentityPhase
    entropy: float
    consciousness_phase: str
    trinity_coherence: float
    timestamp: float

    def to_string(self) -> str:
        """Convert to symbolic string representation"""
        return "".join(self.glyphs)


@dataclass
class IdentityMemory:
    """Tracks identity evolution history"""

    previous_personas: List[PersonaSignature]
    transformation_count: int
    total_drift: float
    ethical_interventions: int
    creation_timestamp: float


class EmergentIdentity:
    """
    Main identity evolution engine for LUKHΛS Phase 7.
    Tracks active glyphs, entropy, consciousness phase, and ethical overlays.
    """

    def __init__(
        self,
        config_dir: str = ".",
        identity_state_file: str = "identity_state.json",
        guardian_filter_path: Optional[str] = None,
    ):

        self.config_dir = Path(config_dir)
        self.identity_state_file = Path(identity_state_file)

        # Load configurations
        self._load_persona_profiles()
        self._load_archetype_mapping()

        # Initialize guardian filter
        if guardian_filter_path:
            from guardian_shadow_filter import GuardianShadowFilter

            self.guardian_filter = GuardianShadowFilter()
        else:
            self.guardian_filter = None

        # Current identity state
        self.current_persona: Optional[PersonaSignature] = None
        self.identity_memory = IdentityMemory(
            previous_personas=[],
            transformation_count=0,
            total_drift=0.0,
            ethical_interventions=0,
            creation_timestamp=time.time(),
        )

        # Symbolic state
        self.active_glyphs: Set[str] = set()
        self.entropy_level: float = 0.3
        self.consciousness_phase: str = "calm"
        self.trinity_coherence: float = 1.0

        # Load existing state if available
        self._load_identity_state()

        logger.info("🌟 Emergent Identity Engine initialized")
        logger.info(f"   Personas loaded: {len(self.persona_profiles)}")
        logger.info(f"   Archetypes mapped: {len(self.archetype_mapping)}")

    def _load_persona_profiles(self):
        """Load persona profiles from YAML configuration"""
        try:
            profile_path = self.config_dir / "symbolic_persona_profile.yaml"
            if profile_path.exists():
                with open(profile_path) as f:
                    data = yaml.safe_load(f)
                    self.persona_profiles = data.get("personas", {})
            else:
                # Default personas if config not found
                self.persona_profiles = self._get_default_personas()
        except Exception as e:
            logger.error(f"Failed to load persona profiles: {e}")
            self.persona_profiles = self._get_default_personas()

    def _load_archetype_mapping(self):
        """Load archetype mapping from JSON"""
        try:
            mapping_path = self.config_dir / "archetype_mapping.json"
            if mapping_path.exists():
                with open(mapping_path) as f:
                    self.archetype_mapping = json.load(f)
            else:
                # Default mapping if not found
                self.archetype_mapping = self._get_default_archetypes()
        except Exception as e:
            logger.error(f"Failed to load archetype mapping: {e}")
            self.archetype_mapping = self._get_default_archetypes()

    def _get_default_personas(self) -> Dict:
        """Provide default personas if config missing"""
        return {
            "the_navigator": {
                "name": "The Navigator",
                "glyphs": ["🧭", "🧠", "🌌"],
                "dominant_traits": ["curious", "resilient", "exploratory"],
                "emotional_resonance": ["awe", "focus", "determination"],
                "drift_thresholds": {"min": 0.3, "max": 0.6},
            },
            "the_guardian": {
                "name": "The Guardian",
                "glyphs": ["🛡️", "👁️", "⚡"],
                "dominant_traits": ["protective", "vigilant", "decisive"],
                "emotional_resonance": ["responsibility", "caution", "strength"],
                "drift_thresholds": {"min": 0.2, "max": 0.5},
            },
            "the_dreamer": {
                "name": "The Dreamer",
                "glyphs": ["🌙", "🔮", "✨"],
                "dominant_traits": ["intuitive", "creative", "visionary"],
                "emotional_resonance": ["wonder", "inspiration", "mystery"],
                "drift_thresholds": {"min": 0.4, "max": 0.7},
            },
        }

    def _get_default_archetypes(self) -> Dict:
        """Provide default archetype mapping if not found"""
        return {
            "lucid_dreamer": ["🌙", "🔮", "🪞"],
            "guardian_archivist": ["🛡️", "📚", "🧬"],
            "harmony_weaver": ["🌿", "🧠", "🎼"],
            "quantum_navigator": ["⚛️", "🧭", "🌌"],
            "creative_synthesizer": ["🎨", "🧬", "✨"],
        }

    def _load_identity_state(self):
        """Load existing identity state from file"""
        try:
            if self.identity_state_file.exists():
                with open(self.identity_state_file) as f:
                    state = json.load(f)

                # Restore state
                self.active_glyphs = set(state.get("active_signature", []))
                self.entropy_level = state.get("entropy", 0.3)

                # Reconstruct current persona if available
                if "persona" in state and state["persona"] in self.persona_profiles:
                    profile = self.persona_profiles[
                        state["persona"].lower().replace(" ", "_")
                    ]
                    self.current_persona = PersonaSignature(
                        glyphs=profile["glyphs"],
                        name=profile["name"],
                        phase=IdentityPhase.STABLE,
                        entropy=self.entropy_level,
                        consciousness_phase=self.consciousness_phase,
                        trinity_coherence=self.trinity_coherence,
                        timestamp=time.time(),
                    )

                logger.info(f"Loaded identity state: {state.get('persona', 'Unknown')}")
        except Exception as e:
            logger.warning(f"Could not load identity state: {e}")

    def evolve(
        self,
        entropy_delta: float = 0.0,
        memory_tags: List[str] = None,
        dream_outcome: Optional[str] = None,
        consciousness_input: Optional[Dict] = None,
    ) -> PersonaSignature:
        """
        Evolve identity based on symbolic state inputs.

        Args:
            entropy_delta: Change in entropy level
            memory_tags: Memory fold tags influencing identity
            dream_outcome: Result from dream/consciousness exploration
            consciousness_input: Direct consciousness state input

        Returns:
            Updated PersonaSignature
        """
        logger.info("🔄 Identity evolution triggered")

        # Update entropy
        self.entropy_level
        self.entropy_level = max(0.0, min(1.0, self.entropy_level + entropy_delta))
        self.identity_memory.total_drift += abs(entropy_delta)

        # Update consciousness phase if provided
        if consciousness_input:
            self.consciousness_phase = consciousness_input.get(
                "phase", self.consciousness_phase
            )
            self.trinity_coherence = consciousness_input.get(
                "trinity_coherence", self.trinity_coherence
            )

        # Determine phase based on entropy
        if self.entropy_level < 0.3:
            identity_phase = IdentityPhase.STABLE
        elif self.entropy_level < 0.6:
            identity_phase = IdentityPhase.CRYSTALLIZING
        elif self.entropy_level < 0.8:
            identity_phase = IdentityPhase.MORPHING
        else:
            identity_phase = IdentityPhase.TRANSCENDENT

        # Gather candidate glyphs from various sources
        candidate_glyphs = set()

        # From memory tags
        if memory_tags:
            for tag in memory_tags:
                if tag in self.archetype_mapping:
                    candidate_glyphs.update(self.archetype_mapping[tag])

        # From dream outcome
        if dream_outcome:
            dream_glyphs = self._interpret_dream_outcome(dream_outcome)
            candidate_glyphs.update(dream_glyphs)

        # From current active glyphs (persistence)
        if self.active_glyphs:
            candidate_glyphs.update(self.active_glyphs)

        # Select persona based on candidates and entropy
        selected_persona = self._select_persona(candidate_glyphs, identity_phase)

        # Apply guardian constraints
        if self.guardian_filter:
            allowed, reason = self.guardian_filter.apply_constraints(
                {
                    "persona": selected_persona,
                    "entropy": self.entropy_level,
                    "trinity_coherence": self.trinity_coherence,
                    "phase": identity_phase,
                }
            )

            if not allowed:
                logger.warning(f"🛡️ Guardian blocked evolution: {reason}")
                self.identity_memory.ethical_interventions += 1
                # Revert to stable persona or maintain current
                if self.current_persona:
                    return self.current_persona
                else:
                    selected_persona = self._get_guardian_approved_persona()

        # Create new persona signature
        new_persona = PersonaSignature(
            glyphs=selected_persona["glyphs"],
            name=selected_persona["name"],
            phase=identity_phase,
            entropy=self.entropy_level,
            consciousness_phase=self.consciousness_phase,
            trinity_coherence=self.trinity_coherence,
            timestamp=time.time(),
        )

        # Update identity memory
        if self.current_persona:
            self.identity_memory.previous_personas.append(self.current_persona)
        self.identity_memory.transformation_count += 1

        # Update current state
        self.current_persona = new_persona
        self.active_glyphs = set(new_persona.glyphs)

        # Save state
        self._save_identity_state()

        logger.info(f"✨ Evolved to: {new_persona.name} {new_persona.to_string()}")
        logger.info(
            f"   Phase: {identity_phase.value}, Entropy: {self.entropy_level:.3f}"
        )

        return new_persona

    def _interpret_dream_outcome(self, dream_outcome: str) -> List[str]:
        """Interpret dream outcome into symbolic glyphs"""
        dream_mappings = {
            "lucid": ["🌙", "🔮", "👁️"],
            "chaotic": ["🌪️", "🔥", "💥"],
            "transcendent": ["🌌", "🕉️", "🪷"],
            "grounded": ["🌿", "🏔️", "💎"],
            "creative": ["🎨", "🌊", "✨"],
        }

        return dream_mappings.get(dream_outcome.lower(), ["🧠"])

    def _select_persona(self, candidate_glyphs: Set[str], phase: IdentityPhase) -> Dict:
        """Select appropriate persona based on glyphs and phase"""
        best_match = None
        best_score = -1

        for persona_key, persona in self.persona_profiles.items():
            # Calculate glyph overlap score
            persona_glyphs = set(persona["glyphs"])
            overlap = len(candidate_glyphs.intersection(persona_glyphs))

            # Check drift thresholds
            thresholds = persona["drift_thresholds"]
            if thresholds["min"] <= self.entropy_level <= thresholds["max"]:
                overlap += 1  # Bonus for matching entropy range

            # Phase compatibility
            if (
                phase == IdentityPhase.STABLE
                and "protective" in persona["dominant_traits"]
                or phase == IdentityPhase.MORPHING
                and "adaptive" in persona["dominant_traits"]
            ):
                overlap += 1

            if overlap > best_score:
                best_score = overlap
                best_match = persona

        return best_match or self.persona_profiles.get(
            "the_navigator", self._get_default_personas()["the_navigator"]
        )

    def _get_guardian_approved_persona(self) -> Dict:
        """Get a safe, guardian-approved persona"""
        # Default to Guardian persona for safety
        return self.persona_profiles.get(
            "the_guardian",
            {
                "name": "The Guardian",
                "glyphs": ["🛡️", "👁️", "⚡"],
                "dominant_traits": ["protective", "vigilant", "decisive"],
                "emotional_resonance": ["responsibility", "caution", "strength"],
                "drift_thresholds": {"min": 0.2, "max": 0.5},
            },
        )

    def collapse_identity(self, observer: str = "system") -> str:
        """
        Collapse current identity superposition into temporary persona signature.

        Args:
            observer: Who/what is observing the collapse

        Returns:
            Collapsed identity signature string
        """
        if not self.current_persona:
            # Initialize with default if no current persona
            self.current_persona = PersonaSignature(
                glyphs=["⚛️", "🧠", "🛡️"],
                name="Trinity Core",
                phase=IdentityPhase.NASCENT,
                entropy=0.3,
                consciousness_phase="calm",
                trinity_coherence=1.0,
                timestamp=time.time(),
            )

        # Simulate collapse based on observer
        if observer == "guardian":
            # Guardian observation strengthens protective aspects
            collapsed_glyph = (
                "🛡️"
                if "🛡️" in self.current_persona.glyphs
                else self.current_persona.glyphs[0]
            )
        elif observer == "dream":
            # Dream observation emphasizes intuitive aspects
            dream_glyphs = ["🌙", "🔮", "✨", "🌌"]
            for glyph in self.current_persona.glyphs:
                if glyph in dream_glyphs:
                    collapsed_glyph = glyph
                    break
            else:
                collapsed_glyph = self.current_persona.glyphs[0]
        else:
            # Default collapse to primary glyph
            collapsed_glyph = self.current_persona.glyphs[0]

        logger.info(f"💥 Identity collapsed by {observer}: {collapsed_glyph}")

        return collapsed_glyph

    def get_persona_signature(self) -> str:
        """
        Get current symbolic identity signature.

        Returns:
            String of current identity glyphs (e.g., "🧠🌿🪷")
        """
        if self.current_persona:
            return self.current_persona.to_string()
        else:
            return "⚛️🧠🛡️"  # Default Trinity signature

    def get_identity_state(self) -> Dict:
        """Get complete current identity state"""
        return {
            "active_signature": list(self.active_glyphs),
            "persona": self.current_persona.name if self.current_persona else "Unknown",
            "entropy": self.entropy_level,
            "phase": (
                self.current_persona.phase.value if self.current_persona else "nascent"
            ),
            "consciousness_phase": self.consciousness_phase,
            "trinity_coherence": self.trinity_coherence,
            "transformation_count": self.identity_memory.transformation_count,
            "ethical_interventions": self.identity_memory.ethical_interventions,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }

    def _save_identity_state(self):
        """Save current identity state to file"""
        try:
            state = self.get_identity_state()
            with open(self.identity_state_file, "w") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved identity state to {self.identity_state_file}")
        except Exception as e:
            logger.error(f"Failed to save identity state: {e}")

    def get_evolution_history(self) -> List[Dict]:
        """Get identity evolution history"""
        history = []
        for persona in self.identity_memory.previous_personas:
            history.append(
                {
                    "name": persona.name,
                    "glyphs": persona.glyphs,
                    "phase": persona.phase.value,
                    "entropy": persona.entropy,
                    "timestamp": persona.timestamp,
                }
            )
        return history

    def calculate_identity_stability(self) -> float:
        """
        Calculate current identity stability score (0.0-1.0).

        Returns:
            Stability score based on entropy, coherence, and transformation rate
        """
        # Base stability from entropy (inverse relationship)
        entropy_stability = 1.0 - self.entropy_level

        # Trinity coherence contribution
        coherence_stability = self.trinity_coherence

        # Transformation frequency penalty
        if self.identity_memory.transformation_count > 0:
            time_elapsed = time.time() - self.identity_memory.creation_timestamp
            hours_elapsed = time_elapsed / 3600
            transformation_rate = self.identity_memory.transformation_count / max(
                1, hours_elapsed
            )
            transformation_stability = 1.0 / (1.0 + transformation_rate)
        else:
            transformation_stability = 1.0

        # Weighted average
        stability = (
            0.4 * entropy_stability
            + 0.4 * coherence_stability
            + 0.2 * transformation_stability
        )

        return max(0.0, min(1.0, stability))


# Example usage for testing
if __name__ == "__main__":
    print("🌟 LUKHΛS Phase 7: Emergent Identity Test")
    print("=" * 50)

    # Create identity engine
    identity = EmergentIdentity()

    # Show initial state
    print(f"Initial Identity: {identity.get_persona_signature()}")
    print(f"State: {identity.get_identity_state()}")

    # Simulate evolution with dream input
    print("\n🌙 Simulating dream-influenced evolution...")
    new_persona = identity.evolve(
        entropy_delta=0.15,
        memory_tags=["lucid_dreamer"],
        dream_outcome="transcendent",
        consciousness_input={"phase": "drift", "trinity_coherence": 0.85},
    )

    print(f"\nEvolved to: {new_persona.name}")
    print(f"Signature: {new_persona.to_string()}")
    print(f"Phase: {new_persona.phase.value}")

    # Test collapse
    collapsed = identity.collapse_identity("dream")
    print(f"\nCollapsed identity: {collapsed}")

    # Show stability
    stability = identity.calculate_identity_stability()
    print(f"\nIdentity stability: {stability:.2%}")
