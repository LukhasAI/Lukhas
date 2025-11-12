"""Glyph scalar metrics export."""
from typing import Dict
from .model import Glyph


def export_scalar(glyph: Glyph) -> Dict[str, float]:
    """
    Export attractor/repeller scalars for dashboards.

    Args:
        glyph: Glyph to extract metrics from

    Returns:
        Dictionary with attractor and repeller values
    """
    attractor = glyph.properties.get("attractor", 0.5)
    repeller = glyph.properties.get("repeller", 0.5)

    return {
        "attractor": float(attractor),
        "repeller": float(repeller)
    }


if __name__ == "__main__":
    print("=== Glyph Scalar Export Demo ===\n")

    from .model import Glyph

    glyph = Glyph(
        symbol="⚛",
        meaning="test",
        properties={"attractor": 0.75, "repeller": 0.25}
    )

    scalars = export_scalar(glyph)
    print(f"Glyph {glyph.symbol}:")
    print(f"  Attractor: {scalars['attractor']}")
    print(f"  Repeller: {scalars['repeller']}")
