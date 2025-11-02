"""Alternate emotion mapping utilities for Healix integrations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

logger = logging.getLogger("emotion_mapper_alt")


@dataclass(frozen=True)
class EmotionProfile:
    """Symbolic representation of an emotion baseline."""

    stability: float
    similarity_boost: float


# ΛTAG: affect_delta - baseline parameters for tone inference
_DEFAULT_PROFILES: dict[str, EmotionProfile] = {
    "neutral": EmotionProfile(stability=0.6, similarity_boost=0.8),
    "calm": EmotionProfile(stability=0.7, similarity_boost=0.85),
    "curious": EmotionProfile(stability=0.65, similarity_boost=0.9),
    "focused": EmotionProfile(stability=0.55, similarity_boost=0.82),
    "intense": EmotionProfile(stability=0.35, similarity_boost=0.6),
}


class EmotionMapper:
    """Provide tone and intensity utilities for Healix memory records."""

    def __init__(
        self,
        *,
        profiles: Mapping[str, EmotionProfile] | None = None,
        resonance_threshold: float = 0.75,
    ) -> None:
        self._profiles: dict[str, EmotionProfile] = dict(profiles or _DEFAULT_PROFILES)
        self._resonance_threshold = resonance_threshold
        self._baseline_vector: tuple[float, float, float] = (0.5, 0.5, 0.5)
        # ΛTAG: affect_delta - track cumulative emotional drift
        self._cumulative_affect_delta: float = 0.0
        logger.debug(
            "EmotionMapper initialized",
            extra={
                "resonance_threshold": resonance_threshold,
                "profiles": list(self._profiles.keys()),
                "affect_delta": self._cumulative_affect_delta,
            },
        )

    @property
    def resonance_threshold(self) -> float:
        """Return the active resonance threshold."""

        return self._resonance_threshold

    def suggest_tone(self, context: str, record: Mapping[str, Any]) -> str:
        """Suggest a tone for a Healix memory record."""

        explicit_tone = record.get("tone")
        if isinstance(explicit_tone, str):
            logger.debug(
                "Explicit tone retained",
                extra={"tone": explicit_tone, "context": context},
            )
            return explicit_tone

        mood_hint = str(record.get("mood_hint", context)).lower()
        profile = self._profiles.get(mood_hint)
        if profile is None:
            profile = self._profiles.get("neutral")

        affect_delta = self._compute_affect_delta(record.get("emotion_vector"))
        # ΛTAG: affect_delta - update drift for suggested tone
        self._cumulative_affect_delta += abs(affect_delta)
        suggested = mood_hint if mood_hint in self._profiles else "neutral"
        logger.debug(
            "Tone suggested",
            extra={
                "context": context,
                "suggested": suggested,
                "affect_delta": affect_delta,
                "cumulative_affect_delta": self._cumulative_affect_delta,
                "profile_stability": profile.stability,
            },
        )
        return suggested

    def score_intensity(self, record: Mapping[str, Any]) -> float:
        """Score emotional intensity for a Healix memory record."""

        explicit_intensity = record.get("intensity")
        if isinstance(explicit_intensity, (float, int)):
            intensity = max(0.0, min(1.0, float(explicit_intensity)))
            logger.debug(
                "Intensity provided by record",
                extra={"intensity": intensity, "affect_delta": 0.0},
            )
            return intensity

        emotion_vector = record.get("emotion_vector")
        affect_delta = self._compute_affect_delta(emotion_vector)
        profile = self._profiles.get(str(record.get("mood_hint", "neutral")), self._profiles["neutral"])
        intensity = max(0.0, min(1.0, profile.similarity_boost * (1.0 - abs(affect_delta))))
        logger.debug(
            "Intensity inferred",
            extra={
                "intensity": intensity,
                "affect_delta": affect_delta,
                "similarity_boost": profile.similarity_boost,
            },
        )
        return intensity

    def tone_similarity_score(self, target_emotion: str, record: Mapping[str, Any]) -> float:
        """Return similarity between a target emotion and record tone."""

        if not target_emotion:
            return 0.0

        tone = str(record.get("tone") or record.get("mood_hint") or "").lower()
        if not tone:
            return 0.0

        tone_profile = self._profiles.get(tone)
        target_profile = self._profiles.get(target_emotion.lower(), self._profiles.get("neutral"))
        if tone_profile is None or target_profile is None:
            return 0.0

        stability_delta = abs(tone_profile.stability - target_profile.stability)
        similarity = max(0.0, target_profile.similarity_boost - stability_delta)
        logger.debug(
            "Tone similarity computed",
            extra={
                "target": target_emotion,
                "tone": tone,
                "stability_delta": stability_delta,
                "similarity": similarity,
            },
        )
        return similarity

    def _compute_affect_delta(self, emotion_vector: Iterable[float] | None) -> float:
        """Compute a symbolic affect delta between baseline and supplied vector."""

        vector = tuple(float(x) for x in emotion_vector) if emotion_vector else self._baseline_vector
        if len(vector) != len(self._baseline_vector):
            # ✅ TODO: handle high-dimensional vectors once emotion engine exposes them
            vector = vector[: len(self._baseline_vector)]

        affect_delta = sum(abs(v - b) for v, b in zip(vector, self._baseline_vector)) / len(self._baseline_vector)
        return max(0.0, min(1.0, affect_delta))
