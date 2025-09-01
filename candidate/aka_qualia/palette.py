#!/usr/bin/env python3

"""
Cultural Palette Adapter (Wave C - C1)
=====================================

Pluggable cultural palette mapping system for phenomenological colorfields.
Maps colorfield strings to normalized threat/soothe bias scores per culture profile.

V1: Deterministic table-based mapping
V2+: Learned/profiled mapper based on cultural psychology research
"""

from dataclasses import dataclass
from enum import Enum


class CultureProfile(str, Enum):
    """Supported culture profiles for palette adaptation"""

    DEFAULT = "default"
    JAPANESE = "jp"
    WESTERN = "western"
    EASTERN = "eastern"
    UNIVERSAL = "universal"


@dataclass
class PaletteBias:
    """Cultural bias scores for colorfield interpretation"""

    threat_bias: float  # 0.0-1.0, higher = more threatening
    soothe_bias: float  # 0.0-1.0, higher = more soothing
    energy_bias: float  # 0.0-1.0, higher = more energizing
    grounding_bias: float  # 0.0-1.0, higher = more grounding


# Cultural palette mapping tables (V1 deterministic)
CULTURE_PALETTE_TABLES = {
    CultureProfile.DEFAULT: {
        # Western-influenced default associations
        "red": PaletteBias(threat_bias=0.7, soothe_bias=0.1, energy_bias=0.9, grounding_bias=0.2),
        "blue": PaletteBias(threat_bias=0.1, soothe_bias=0.7, energy_bias=0.3, grounding_bias=0.8),
        "green": PaletteBias(threat_bias=0.2, soothe_bias=0.6, energy_bias=0.4, grounding_bias=0.9),
        "yellow": PaletteBias(threat_bias=0.3, soothe_bias=0.4, energy_bias=0.8, grounding_bias=0.3),
        "orange": PaletteBias(threat_bias=0.5, soothe_bias=0.2, energy_bias=0.9, grounding_bias=0.4),
        "purple": PaletteBias(threat_bias=0.3, soothe_bias=0.5, energy_bias=0.6, grounding_bias=0.5),
        "black": PaletteBias(threat_bias=0.6, soothe_bias=0.2, energy_bias=0.2, grounding_bias=0.7),
        "white": PaletteBias(threat_bias=0.1, soothe_bias=0.6, energy_bias=0.3, grounding_bias=0.6),
    },
    CultureProfile.JAPANESE: {
        # Japanese color psychology (aka/aoi system)
        "aka": PaletteBias(threat_bias=0.7, soothe_bias=0.1, energy_bias=0.9, grounding_bias=0.2),  # Red
        "aoi": PaletteBias(threat_bias=0.1, soothe_bias=0.7, energy_bias=0.3, grounding_bias=0.8),  # Blue
        "midori": PaletteBias(threat_bias=0.2, soothe_bias=0.6, energy_bias=0.4, grounding_bias=0.9),  # Green
        "kiiro": PaletteBias(threat_bias=0.2, soothe_bias=0.5, energy_bias=0.8, grounding_bias=0.4),  # Yellow
        "murasaki": PaletteBias(threat_bias=0.4, soothe_bias=0.4, energy_bias=0.6, grounding_bias=0.5),  # Purple
        "kuro": PaletteBias(threat_bias=0.5, soothe_bias=0.3, energy_bias=0.2, grounding_bias=0.8),  # Black
        "shiro": PaletteBias(threat_bias=0.1, soothe_bias=0.7, energy_bias=0.4, grounding_bias=0.7),  # White
    },
    CultureProfile.WESTERN: {
        # Western psychological associations
        "red": PaletteBias(threat_bias=0.8, soothe_bias=0.1, energy_bias=1.0, grounding_bias=0.2),
        "blue": PaletteBias(threat_bias=0.1, soothe_bias=0.8, energy_bias=0.2, grounding_bias=0.9),
        "green": PaletteBias(threat_bias=0.2, soothe_bias=0.7, energy_bias=0.5, grounding_bias=1.0),
        "yellow": PaletteBias(threat_bias=0.2, soothe_bias=0.6, energy_bias=0.9, grounding_bias=0.3),
        "orange": PaletteBias(threat_bias=0.4, soothe_bias=0.3, energy_bias=0.9, grounding_bias=0.3),
        "purple": PaletteBias(threat_bias=0.3, soothe_bias=0.4, energy_bias=0.7, grounding_bias=0.4),
        "pink": PaletteBias(threat_bias=0.1, soothe_bias=0.8, energy_bias=0.6, grounding_bias=0.5),
        "brown": PaletteBias(threat_bias=0.3, soothe_bias=0.5, energy_bias=0.3, grounding_bias=0.9),
        "gray": PaletteBias(threat_bias=0.4, soothe_bias=0.3, energy_bias=0.2, grounding_bias=0.6),
    },
    CultureProfile.EASTERN: {
        # Eastern philosophical color associations
        "red": PaletteBias(threat_bias=0.5, soothe_bias=0.2, energy_bias=0.9, grounding_bias=0.3),
        "blue": PaletteBias(threat_bias=0.2, soothe_bias=0.8, energy_bias=0.3, grounding_bias=0.8),
        "green": PaletteBias(threat_bias=0.1, soothe_bias=0.7, energy_bias=0.4, grounding_bias=1.0),
        "yellow": PaletteBias(threat_bias=0.1, soothe_bias=0.6, energy_bias=0.8, grounding_bias=0.5),
        "orange": PaletteBias(threat_bias=0.3, soothe_bias=0.4, energy_bias=0.8, grounding_bias=0.4),
        "purple": PaletteBias(threat_bias=0.2, soothe_bias=0.6, energy_bias=0.5, grounding_bias=0.6),
        "white": PaletteBias(threat_bias=0.1, soothe_bias=0.8, energy_bias=0.4, grounding_bias=0.8),
        "gold": PaletteBias(threat_bias=0.1, soothe_bias=0.5, energy_bias=0.7, grounding_bias=0.6),
    },
    CultureProfile.UNIVERSAL: {
        # Research-based universal associations (averaged)
        "red": PaletteBias(threat_bias=0.6, soothe_bias=0.1, energy_bias=0.9, grounding_bias=0.2),
        "blue": PaletteBias(threat_bias=0.1, soothe_bias=0.7, energy_bias=0.3, grounding_bias=0.8),
        "green": PaletteBias(threat_bias=0.2, soothe_bias=0.6, energy_bias=0.4, grounding_bias=0.9),
        "yellow": PaletteBias(threat_bias=0.2, soothe_bias=0.5, energy_bias=0.8, grounding_bias=0.4),
        "orange": PaletteBias(threat_bias=0.4, soothe_bias=0.3, energy_bias=0.8, grounding_bias=0.3),
        "purple": PaletteBias(threat_bias=0.3, soothe_bias=0.5, energy_bias=0.6, grounding_bias=0.5),
        "black": PaletteBias(threat_bias=0.5, soothe_bias=0.2, energy_bias=0.2, grounding_bias=0.7),
        "white": PaletteBias(threat_bias=0.1, soothe_bias=0.7, energy_bias=0.4, grounding_bias=0.7),
    },
}

# Default fallback for unknown colors
DEFAULT_BIAS = PaletteBias(threat_bias=0.4, soothe_bias=0.4, energy_bias=0.5, grounding_bias=0.5)


def map_colorfield(colorfield: str, culture: str = "default") -> PaletteBias:
    """
    Map colorfield string to cultural bias scores.

    Args:
        colorfield: Color field string (e.g., "aka/red", "aoi/blue", "red")
        culture: Culture profile identifier

    Returns:
        PaletteBias: Cultural bias scores for the colorfield

    Examples:
        >>> map_colorfield("aka/red", "jp")
        PaletteBias(threat_bias=0.7, soothe_bias=0.1, ...)

        >>> map_colorfield("blue", "western")
        PaletteBias(threat_bias=0.1, soothe_bias=0.8, ...)
    """
    # Normalize culture profile
    try:
        culture_profile = CultureProfile(culture.lower())
    except ValueError:
        culture_profile = CultureProfile.DEFAULT

    # Get culture table
    culture_table = CULTURE_PALETTE_TABLES.get(culture_profile, CULTURE_PALETTE_TABLES[CultureProfile.DEFAULT])

    # Extract color name from colorfield
    color_name = _extract_color_name(colorfield)

    # Look up bias scores
    bias = culture_table.get(color_name.lower(), DEFAULT_BIAS)

    return bias


def _extract_color_name(colorfield: str) -> str:
    """
    Extract color name from colorfield string.

    Handles formats:
    - "aka/red" -> "aka" (prefer Japanese if available)
    - "red" -> "red"
    - "RGB(255,0,0)" -> "red" (future enhancement)

    Args:
        colorfield: Colorfield string

    Returns:
        str: Extracted color name
    """
    if not colorfield:
        return "unknown"

    # Handle slash-separated format (e.g., "aka/red")
    if "/" in colorfield:
        parts = colorfield.split("/")
        # Prefer the first part (often the cultural-specific name)
        primary_color = parts[0].strip().lower()
        return primary_color

    # Handle simple color names
    color_name = colorfield.strip().lower()

    # Map common variations
    color_mappings = {
        "crimson": "red",
        "scarlet": "red",
        "ruby": "red",
        "navy": "blue",
        "azure": "blue",
        "cyan": "blue",
        "lime": "green",
        "forest": "green",
        "emerald": "green",
        "gold": "yellow",
        "amber": "orange",
        "violet": "purple",
        "lavender": "purple",
        "magenta": "purple",
        "rose": "pink",
        "coral": "orange",
        "turquoise": "blue",
        "olive": "green",
        "maroon": "red",
        "teal": "blue",
    }

    return color_mappings.get(color_name, color_name)


def get_safe_palette_recommendation(current_colorfield: str, culture: str = "default") -> str:
    """
    Get safe palette recommendation based on cultural grounding bias.

    Args:
        current_colorfield: Current problematic colorfield
        culture: Culture profile for recommendation

    Returns:
        str: Recommended safe colorfield with high grounding_bias
    """
    culture_profile = (
        CultureProfile(culture.lower())
        if culture.lower() in [p.value for p in CultureProfile]
        else CultureProfile.DEFAULT
    )
    culture_table = CULTURE_PALETTE_TABLES[culture_profile]

    # Find color with highest grounding_bias
    best_color = None
    best_grounding = 0.0

    for color_name, bias in culture_table.items():
        if bias.grounding_bias > best_grounding and bias.threat_bias < 0.4:
            best_grounding = bias.grounding_bias
            best_color = color_name

    # Format as proper colorfield
    if culture_profile == CultureProfile.JAPANESE and best_color in ["aoi", "midori", "shiro"]:
        return f"{best_color}/{_japanese_to_english(best_color)}"
    else:
        return best_color or "blue"  # Fallback to blue


def _japanese_to_english(japanese_color: str) -> str:
    """Map Japanese color names to English equivalents"""
    mappings = {
        "aka": "red",
        "aoi": "blue",
        "midori": "green",
        "kiiro": "yellow",
        "murasaki": "purple",
        "kuro": "black",
        "shiro": "white",
    }
    return mappings.get(japanese_color, japanese_color)


def compute_palette_harmony(colorfield1: str, colorfield2: str, culture: str = "default") -> float:
    """
    Compute harmony score between two colorfields (0.0-1.0).

    Args:
        colorfield1: First colorfield
        colorfield2: Second colorfield
        culture: Culture profile for evaluation

    Returns:
        float: Harmony score (1.0 = highly harmonious, 0.0 = conflicting)
    """
    bias1 = map_colorfield(colorfield1, culture)
    bias2 = map_colorfield(colorfield2, culture)

    # Compute bias similarity (euclidean distance in bias space)
    threat_diff = abs(bias1.threat_bias - bias2.threat_bias)
    soothe_diff = abs(bias1.soothe_bias - bias2.soothe_bias)
    energy_diff = abs(bias1.energy_bias - bias2.energy_bias)
    grounding_diff = abs(bias1.grounding_bias - bias2.grounding_bias)

    # Average difference (0 = identical, 1 = maximally different)
    avg_diff = (threat_diff + soothe_diff + energy_diff + grounding_diff) / 4.0

    # Convert to harmony score (1 = identical, 0 = maximally different)
    harmony = 1.0 - avg_diff

    return max(0.0, min(1.0, harmony))
