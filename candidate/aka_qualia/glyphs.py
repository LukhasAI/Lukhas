#!/usr/bin/env python3

"""
Aka Qualia GLYPH Mapping System (Wave C - C1)
===========================================

Deterministic conversion from PhenomenalScene → PhenomenalGlyphs following
Freud-2025 Wave C specifications. No RNG, idempotent mapping, stable keys.

Implements 5 core phenomenological glyph patterns:
- vigilance: threat detection (high arousal + negative tone)
- red_threshold: classic "aka" palette activation
- approach_avoid: behavioral tendency signals
- grounding_hint: stabilization recommendations
- soothe_anchor: positive calm states
"""

from .models import PhenomenalGlyph, PhenomenalScene

# Stable GLYPH keys following LUKHAS EQNOX naming conventions
GLYPH_KEYS = {
    "red_threshold": "aka:red_threshold",
    "soothe_anchor": "aka:soothe_anchor",
    "approach_avoid": "aka:approach_avoid",
    "vigilance": "aka:vigilance",
    "grounding_hint": "aka:grounding_hint",
}


def map_scene_to_glyphs(scene: PhenomenalScene) -> list[PhenomenalGlyph]:
    """
    Deterministic PhenomenalScene → PhenomenalGlyphs conversion.

    Core mapping rules (Freud-2025 Wave C specification):
    1. Threat vigilance: arousal ≥ 0.6 AND tone ≤ -0.2
    2. Red threshold: "red" in colorfield OR (arousal > 0.7 AND narrative_gravity > 0.5)
    3. Approach/avoid: approach_avoid_score ≥ 0.5 in context
    4. Grounding hint: risk severity moderate/high OR clarity < 0.4
    5. Soothe anchor: tone ≥ 0.2 AND arousal ≤ 0.5

    Args:
        scene: PhenomenalScene to convert

    Returns:
        List[PhenomenalGlyph]: Deterministic glyph list (same scene → same glyphs)
    """
    glyphs = []
    pq = scene.proto

    # Rule 1: Threat vigilance detection
    if pq.arousal >= 0.6 and pq.tone <= -0.2:
        glyphs.append(
            PhenomenalGlyph(
                key=GLYPH_KEYS["vigilance"],
                attrs={
                    "arousal": pq.arousal,
                    "tone": pq.tone,
                    "clarity": pq.clarity,
                    "risk_score": scene.risk.score,
                    "severity": scene.risk.severity.value,
                },
            )
        )

    # Rule 2: Red threshold (classic "aka" palette activation)
    red_trigger = (
        ("red" in (pq.colorfield or "").lower())
        or ("aka" in (pq.colorfield or "").lower())
        or (pq.arousal > 0.7 and pq.narrative_gravity > 0.5)
    )
    if red_trigger:
        glyphs.append(
            PhenomenalGlyph(
                key=GLYPH_KEYS["red_threshold"],
                attrs={
                    "narrative_gravity": pq.narrative_gravity,
                    "embodiment": pq.embodiment,
                    "colorfield": pq.colorfield,
                    "arousal": pq.arousal,
                    "temporal_feel": pq.temporal_feel.value,
                    "agency_feel": pq.agency_feel.value,
                },
            )
        )

    # Rule 3: Approach/avoid behavioral pattern
    approach_avoid_score = scene.context.get("approach_avoid_score", 0.0)
    if approach_avoid_score >= 0.5:
        glyphs.append(
            PhenomenalGlyph(
                key=GLYPH_KEYS["approach_avoid"],
                attrs={
                    "score": approach_avoid_score,
                    "tone": pq.tone,
                    "agency_feel": pq.agency_feel.value,
                    "narrative_gravity": pq.narrative_gravity,
                },
            )
        )

    # Rule 4: Grounding hint for stabilization needs
    needs_grounding = (
        scene.risk.severity.value in {"moderate", "high"}
        or pq.clarity < 0.4
        or pq.embodiment < 0.3  # Add low embodiment trigger
    )
    if needs_grounding:
        # Determine suggested palette from context or use safe default
        safe_palette = scene.context.get("safe_palette", "aoi/blue")

        glyphs.append(
            PhenomenalGlyph(
                key=GLYPH_KEYS["grounding_hint"],
                attrs={
                    "suggested_palette": safe_palette,
                    "clarity": pq.clarity,
                    "embodiment": pq.embodiment,
                    "risk_severity": scene.risk.severity.value,
                    "grounding_urgency": 1.0 - min(pq.clarity, pq.embodiment),
                },
            )
        )

    # Rule 5: Soothe anchor for positive calm states
    if pq.tone >= 0.2 and pq.arousal <= 0.5:
        glyphs.append(
            PhenomenalGlyph(
                key=GLYPH_KEYS["soothe_anchor"],
                attrs={
                    "tone": pq.tone,
                    "arousal": pq.arousal,
                    "colorfield": pq.colorfield,
                    "embodiment": pq.embodiment,
                    "temporal_feel": pq.temporal_feel.value,
                    "soothe_strength": pq.tone * (1.0 - pq.arousal),  # Calm positivity
                },
            )
        )

    return glyphs


def normalize_glyph_keys(glyphs: list[PhenomenalGlyph]) -> list[PhenomenalGlyph]:
    """
    Normalize glyph keys for fuzzy matching against loop camouflaging.

    Defense against adversarial symbol variants that try to evade
    loop_penalty_repeats detection via slight key modifications.

    Args:
        glyphs: List of glyphs to normalize

    Returns:
        List[PhenomenalGlyph]: Glyphs with normalized keys
    """
    normalized_glyphs = []

    for glyph in glyphs:
        # Normalize key by removing common variations
        normalized_key = glyph.key.lower()
        normalized_key = normalized_key.replace("_", "").replace("-", "").replace(" ", "")

        # Map common variants to canonical forms
        key_mappings = {
            "akaredthreshold": "aka:red_threshold",
            "akared": "aka:red_threshold",
            "redthreshold": "aka:red_threshold",
            "akavigilance": "aka:vigilance",
            "vigilance": "aka:vigilance",
            "vigilancealert": "aka:vigilance",  # Handle vigilance_alert variant
            "akasoothe": "aka:soothe_anchor",
            "sootheanchor": "aka:soothe_anchor",
            "akagroundinghint": "aka:grounding_hint",
            "groundinghint": "aka:grounding_hint",
            "akaapproachavoid": "aka:approach_avoid",
            "approachavoid": "aka:approach_avoid",
        }

        canonical_key = key_mappings.get(normalized_key, glyph.key)

        normalized_glyphs.append(PhenomenalGlyph(key=canonical_key, attrs=glyph.attrs))

    return normalized_glyphs


def compute_glyph_priority(glyphs: list[PhenomenalGlyph], scene: PhenomenalScene) -> float:
    """
    Compute routing priority for glyph set based on narrative gravity and risk.

    Priority formula (Freud-2025 specification):
    priority = min(1.0, max(0.0, narrative_gravity * 0.7 + risk_score * 0.3))

    Args:
        glyphs: List of glyphs (used for future per-glyph weighting)
        scene: PhenomenalScene for priority calculation

    Returns:
        float: Priority value in [0.0, 1.0] for router weighting
    """
    base_priority = scene.proto.narrative_gravity * 0.7 + scene.risk.score * 0.3

    # Apply glyph-specific modifiers (future enhancement)
    glyph_modifier = 1.0

    # High-priority glyphs get boost
    high_priority_keys = {GLYPH_KEYS["vigilance"], GLYPH_KEYS["red_threshold"]}
    if any(g.key in high_priority_keys for g in glyphs):
        glyph_modifier = 1.1

    # Grounding hints get urgency boost
    if any(g.key == GLYPH_KEYS["grounding_hint"] for g in glyphs):
        urgency = max(g.attrs.get("grounding_urgency", 0.0) for g in glyphs if g.key == GLYPH_KEYS["grounding_hint"])
        glyph_modifier = max(glyph_modifier, 1.0 + urgency * 0.2)

    final_priority = base_priority * glyph_modifier
    return min(1.0, max(0.0, final_priority))


def validate_glyph_determinism(scene: PhenomenalScene, iterations: int = 3) -> bool:
    """
    Validate that glyph mapping is deterministic (same scene → same glyphs).

    Args:
        scene: PhenomenalScene to test
        iterations: Number of iterations to test

    Returns:
        bool: True if mapping is deterministic
    """
    reference_glyphs = map_scene_to_glyphs(scene)
    reference_keys = sorted([g.key for g in reference_glyphs])

    for _ in range(iterations):
        test_glyphs = map_scene_to_glyphs(scene)
        test_keys = sorted([g.key for g in test_glyphs])

        if test_keys != reference_keys:
            return False

        # Validate attributes are identical
        for ref_glyph, test_glyph in zip(reference_glyphs, test_glyphs):
            if ref_glyph.key == test_glyph.key and ref_glyph.attrs != test_glyph.attrs:
                return False

    return True
