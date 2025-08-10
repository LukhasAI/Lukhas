"""Brand and terminology normalization helpers.

Enforces preferred phrasing in agent-visible outputs:
- Use 'quantum-inspired' instead of 'quantum process/processing/processes'
- Use 'bio-inspired' instead of 'bio process/processing/processes'
- Use 'Lukhas AI' instead of 'Lukhas AGI' (case variants handled)

Intended for lightweight post-processing. Keep replacements conservative.
"""

from __future__ import annotations

import re
from typing import Iterable, Tuple


_REPLACEMENTS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    # Lukhas AGI -> Lukhas AI (various caseings)
    (re.compile(r"\bLUKHAS\s+AGI\b", re.IGNORECASE), "Lukhas AI"),
    # quantum process family -> quantum-inspired
    (
        re.compile(
            r"\bquantum[\s-]?(?:process|processes|processing|proccess|proccesses)\b",
            re.IGNORECASE,
        ),
        "quantum-inspired",
    ),
    # Standalone 'quantum' should default to 'quantum-inspired' unless explicitly
    # followed by accepted qualifiers (inspired, metaphor/metaphors)
    (
        re.compile(
            r"\bquantum\b(?![\s-]?(?:inspired|metaphor|metaphors))",
            re.IGNORECASE,
        ),
        "quantum-inspired",
    ),
    # bio process family -> bio-inspired
    (
        re.compile(
            r"\bbio[\s-]?(?:process|processes|processing)\b",
            re.IGNORECASE,
        ),
        "bio-inspired",
    ),
)


def normalize_output(text: str | None) -> str | None:
    """Apply terminology normalization to plain text.

    Returns the original text if None or not a str.
    """
    if not isinstance(text, str):
        return text
    out = text
    for pat, repl in _REPLACEMENTS:
        out = pat.sub(repl, out)
    # Preserve casing for 'LUKHAS' if it was originally uppercase in the segment.
    # Simple heuristic: if 'LUKHAS' present with AI/AGI, re-upcase.
    out = re.sub(r"\bLukhas AI\b", "LUKHAS AI", out) if "LUKHAS" in text else out
    return out


def normalize_chunk(chunk: str) -> str:
    """Chunk-safe normalization for streaming; best-effort per chunk.

    Note: boundary-spanning phrases might escape normalization.
    """
    return normalize_output(chunk) or ""
