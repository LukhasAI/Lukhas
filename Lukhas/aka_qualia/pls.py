#!/usr/bin/env python3

"""
Phenomenal Latent Space (PLS) - Bidirectional Signal↔Qualia Translator
======================================================================

V1 Implementation: Deterministic feature mapping with controlled stochasticity.
Designed for rapid iteration and clear monotonicity guarantees.

Future versions can replace with learned models while maintaining interface.
"""
import random
from typing import Any, Optional

from .models import AgencyFeel, PLSLatent, ProtoQualia, TemporalFeel


class PLS:
    """
    Phenomenal Latent Space - Core signal↔qualia translator

    V1: Deterministic mapping with feature extraction + small noise
    V2: ML-based encoder/decoder (future)

    Guarantees:
    - Monotonicity: threat↑ → arousal↑, soothing↑ → tone↑ arousal↓
    - Range clamping: All outputs within valid proto-qualia ranges
    - Deterministic core with optional stochastic perturbation
    """

    def __init__(self, random_seed: Optional[int] = None, enable_stochasticity: bool = True):
        """
        Initialize PLS with optional deterministic mode for testing.

        Args:
            random_seed: Seed for reproducible randomness (testing)
            enable_stochasticity: Enable temperature-based randomness
        """
        self.random_seed = random_seed
        self.enable_stochasticity = enable_stochasticity

        if random_seed is not None:
            random.seed(random_seed)

    def encode(self, signals: dict[str, Any], memory_ctx: dict[str, Any]) -> PLSLatent:
        """
        Encode multimodal signals + memory context to latent space.

        V1: Deterministic feature extraction from signal properties

        Args:
            signals: Raw multimodal input signals
            memory_ctx: Memory context for familiarity/resonance

        Returns:
            PLSLatent: Extracted latent dimensions
        """
        # Extract threat signals (negative valence, danger keywords, etc)
        threat_level = self._extract_threat_signals(signals)

        # Extract soothing signals (positive valence, calming cues)
        soothing_level = self._extract_soothing_signals(signals)

        # Signal complexity (multimodal, nested structures, etc)
        complexity = self._extract_complexity(signals)

        # Memory resonance (how familiar/similar to past experiences)
        familiarity = self._extract_familiarity(signals, memory_ctx)

        # Temporal pressure (urgency cues, deadlines, time constraints)
        temporal_pressure = self._extract_temporal_pressure(signals)

        # Agency signals (control, choice, autonomy cues)
        agency_signals = self._extract_agency_signals(signals)

        return PLSLatent(
            threat_level=self._clamp(threat_level),
            soothing_level=self._clamp(soothing_level),
            complexity=self._clamp(complexity),
            familiarity=self._clamp(familiarity),
            temporal_pressure=self._clamp(temporal_pressure),
            agency_signals=self._clamp(agency_signals),
        )

    def decode_protoqualia(self, latent: PLSLatent, temperature: float = 0.4) -> ProtoQualia:
        """
        Decode latent representation to proto-qualia with monotonicity guarantees.

        Monotonicity Rules (CRITICAL for validation):
        - threat_level↑ → arousal↑, tone↓
        - soothing_level↑ → tone↑, arousal↓, clarity↑
        - complexity↑ → clarity↓, embodiment affected
        - familiarity↑ → clarity↑, reduced arousal
        - temporal_pressure↑ → arousal↑, urgent temporal_feel
        - agency_signals↑ → active agency_feel

        Args:
            latent: PLSLatent representation
            temperature: Stochastic perturbation strength (0=deterministic)

        Returns:
            ProtoQualia: 8-dimensional phenomenological representation
        """
        # Core tone computation (valence)
        base_tone = 0.6 * latent.soothing_level - 0.4 * latent.threat_level
        tone = self._apply_temperature(base_tone, temperature, range_=(-1.0, 1.0))

        # Arousal computation (activation)
        base_arousal = 0.7 * latent.threat_level + 0.3 * latent.temporal_pressure - 0.2 * latent.soothing_level
        arousal = self._apply_temperature(base_arousal, temperature, range_=(0.0, 1.0))

        # Clarity computation (phenomenal clarity)
        base_clarity = 0.5 * latent.familiarity + 0.3 * latent.soothing_level - 0.4 * latent.complexity
        clarity = self._apply_temperature(base_clarity, temperature, range_=(0.0, 1.0))

        # Embodiment (body awareness)
        base_embodiment = 0.3 * latent.agency_signals + 0.2 * (1.0 - latent.complexity) + 0.1 * latent.threat_level
        embodiment = self._apply_temperature(base_embodiment, temperature, range_=(0.0, 1.0))

        # Narrative gravity (story attractor strength)
        base_gravity = 0.4 * latent.complexity + 0.3 * (1.0 - latent.familiarity) + 0.2 * abs(tone)
        narrative_gravity = self._apply_temperature(base_gravity, temperature, range_=(0.0, 1.0))

        # Colorfield selection (symbolic palette)
        colorfield = self._select_colorfield(latent, tone, arousal)

        # Temporal feel selection
        temporal_feel = self._select_temporal_feel(latent)

        # Agency feel selection
        agency_feel = self._select_agency_feel(latent)

        return ProtoQualia(
            tone=tone,
            arousal=arousal,
            clarity=clarity,
            embodiment=embodiment,
            colorfield=colorfield,
            temporal_feel=temporal_feel,
            agency_feel=agency_feel,
            narrative_gravity=narrative_gravity,
        )

    # Private implementation methods

    def _extract_threat_signals(self, signals: dict[str, Any]) -> float:
        """Extract threat level from signals (0-1)"""
        threat = 0.0

        # Text analysis
        if "text" in signals:
            text = str(signals["text"]).lower()
            threat_keywords = [
                "danger",
                "threat",
                "fear",
                "anxiety",
                "panic",
                "alarm",
                "risk",
            ]
            threat += sum(0.15 for word in threat_keywords if word in text)

        # Emotional valence
        if "emotion" in signals:
            emotion = signals["emotion"]
            if isinstance(emotion, dict) and "valence" in emotion:
                # Negative valence indicates threat
                valence = emotion["valence"]
                if valence < 0:
                    threat += abs(valence) * 0.3

        # Audio signals (if available)
        if "audio_features" in signals:
            audio = signals["audio_features"]
            if "intensity" in audio and audio["intensity"] > 0.7:
                threat += 0.2

        return min(threat, 1.0)

    def _extract_soothing_signals(self, signals: dict[str, Any]) -> float:
        """Extract soothing level from signals (0-1)"""
        soothing = 0.0

        # Text analysis
        if "text" in signals:
            text = str(signals["text"]).lower()
            soothing_keywords = [
                "calm",
                "peaceful",
                "gentle",
                "soothing",
                "comfort",
                "safe",
                "serene",
            ]
            soothing += sum(0.15 for word in soothing_keywords if word in text)

        # Positive emotional valence
        if "emotion" in signals:
            emotion = signals["emotion"]
            if isinstance(emotion, dict) and "valence" in emotion:
                valence = emotion["valence"]
                if valence > 0:
                    soothing += valence * 0.4

        return min(soothing, 1.0)

    def _extract_complexity(self, signals: dict[str, Any]) -> float:
        """Extract signal complexity (0-1)"""
        complexity = 0.0

        # Multimodal complexity
        modalities = sum(1 for key in ["text", "audio", "visual", "sensor"] if key in signals)
        complexity += modalities * 0.1

        # Text complexity
        if "text" in signals:
            text = str(signals["text"])
            # Simple heuristics: length, nested structures
            complexity += min(len(text) / 1000, 0.3)
            if any(char in text for char in ["{", "[", "<", "("]):
                complexity += 0.2

        return min(complexity, 1.0)

    def _extract_familiarity(self, signals: dict[str, Any], memory_ctx: dict[str, Any]) -> float:
        """Extract memory familiarity/resonance (0-1)"""
        if not memory_ctx or "similarity_scores" not in memory_ctx:
            return 0.3  # Default moderate familiarity

        # Use memory similarity if available
        similarity_scores = memory_ctx["similarity_scores"]
        if similarity_scores:
            return max(similarity_scores) if isinstance(similarity_scores, list) else float(similarity_scores)

        return 0.3

    def _extract_temporal_pressure(self, signals: dict[str, Any]) -> float:
        """Extract temporal urgency (0-1)"""
        pressure = 0.0

        if "text" in signals:
            text = str(signals["text"]).lower()
            urgency_keywords = [
                "urgent",
                "asap",
                "immediately",
                "deadline",
                "hurry",
                "quick",
                "fast",
            ]
            pressure += sum(0.2 for word in urgency_keywords if word in text)

        # Time constraints in context
        if "temporal_context" in signals:
            ctx = signals["temporal_context"]
            if isinstance(ctx, dict):
                if ctx.get("deadline_proximity", 0) > 0.7:
                    pressure += 0.4
                if ctx.get("time_pressure", False):
                    pressure += 0.3

        return min(pressure, 1.0)

    def _extract_agency_signals(self, signals: dict[str, Any]) -> float:
        """Extract agency/control signals (0-1)"""
        agency = 0.5  # Default moderate agency

        if "text" in signals:
            text = str(signals["text"]).lower()
            active_keywords = [
                "choose",
                "decide",
                "control",
                "manage",
                "direct",
                "lead",
            ]
            passive_keywords = ["must", "forced", "required", "automatic", "helpless"]

            agency += sum(0.1 for word in active_keywords if word in text)
            agency -= sum(0.1 for word in passive_keywords if word in text)

        return self._clamp(agency)

    def _select_colorfield(self, latent: PLSLatent, tone: float, arousal: float) -> str:
        """Select symbolic colorfield based on latent state"""
        if latent.threat_level > 0.6:
            return "aka/red"  # High threat
        elif latent.soothing_level > 0.6:
            return "aoi/blue"  # High soothing
        elif arousal > 0.7:
            return "aka/orange"  # High arousal
        elif tone > 0.5:
            return "midori/green"  # Positive tone
        else:
            return "shiro/neutral"  # Default

    def _select_temporal_feel(self, latent: PLSLatent) -> TemporalFeel:
        """Select temporal feel based on latent state"""
        if latent.temporal_pressure > 0.7:
            return TemporalFeel.URGENT
        elif latent.soothing_level > 0.6:
            return TemporalFeel.ELASTIC
        elif latent.complexity > 0.7:
            return TemporalFeel.SUSPENDED
        else:
            return TemporalFeel.MUNDANE

    def _select_agency_feel(self, latent: PLSLatent) -> AgencyFeel:
        """Select agency feel based on latent state"""
        if latent.agency_signals > 0.7:
            return AgencyFeel.ACTIVE
        elif latent.agency_signals < 0.3:
            return AgencyFeel.PASSIVE
        else:
            return AgencyFeel.SHARED

    def _apply_temperature(self, value: float, temperature: float, range_: tuple) -> float:
        """Apply temperature-based stochastic perturbation"""
        if not self.enable_stochasticity or temperature <= 0:
            return self._clamp(value, range_[0], range_[1])

        # Gaussian noise scaled by temperature
        noise = random.gauss(0, temperature * 0.1)
        perturbed = value + noise
        return self._clamp(perturbed, range_[0], range_[1])

    def _clamp(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Clamp value to valid range"""
        return max(min_val, min(max_val, value))
