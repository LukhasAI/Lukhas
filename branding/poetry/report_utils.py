"""Utility helpers for poetry analytics outputs."""

from __future__ import annotations

import difflib
import re
from collections import Counter
from collections.abc import Mapping

# ΛTAG: text_tokenization
_TOKEN_PATTERN = re.compile(r"\b[\w\-']+\b")


# ΛTAG: poetic_metrics
# ΛTAG: substitution_analysis

def render_frequency_line(
    word: str,
    count: int,
    *,
    scale: int = 10,
    bar_char: str = "█",
    width: int = 20,
    label: str | None = None,
) -> str:
    """Render a formatted frequency line with severity indicators."""
    if scale <= 0:
        raise ValueError("scale must be positive")
    if count < 0:
        raise ValueError("count cannot be negative")

    bar_units = count // scale if count else 0
    if count > 0 and bar_units == 0:
        bar_units = 1
    bar = bar_char * bar_units

    if count == 0:
        severity = "⚪ none"
    elif count >= scale * 15:
        severity = "⚠️ dominant"
    elif count >= scale * 8:
        severity = "🔶 frequent"
    else:
        severity = "🟢 emerging"

    label_segment = f" [{label}]" if label else ""
    components = [f"{word:<{width}}", f"{count:>5}"]
    if bar:
        components.append(bar)
    components.append(severity + label_segment)
    return " ".join(components)


# ΛTAG: vocabulary_enrichment

def render_enrichment_summary(
    *,
    index: int,
    original: str,
    enriched: str,
    usage_counter: Mapping[str, int],
    highlight_limit: int = 3,
    repetition_threshold: int = 3,
) -> str:
    """Create a human-readable summary of vocabulary enrichment."""
    if highlight_limit <= 0:
        raise ValueError("highlight_limit must be positive")

    substitutions = _extract_substitutions(original, enriched)
    visible_subs = substitutions[:highlight_limit]
    if visible_subs:
        substitution_text = ", ".join(f"{old}→{new}" for old, new in visible_subs)
        remaining = len(substitutions) - len(visible_subs)
        if remaining > 0:
            substitution_text += f" (+{remaining} more)"
    else:
        substitution_text = "none"

    counter = Counter(usage_counter)
    top_entries = counter.most_common(highlight_limit)
    if top_entries:
        usage_text = ", ".join(f"{word}:{count}" for word, count in top_entries)
    else:
        usage_text = "no tracked metaphors"

    flagged = sorted(word for word, count in counter.items() if count >= repetition_threshold)
    flagged_text = f" ⚠️ Overused: {', '.join(flagged)}" if flagged else ""

    return (
        f"Example {index}\n"
        f"  Original: {original}\n"
        f"  Enriched: {enriched}\n"
        f"  ΛSubstitutions: {substitution_text}\n"
        f"  ΛUsage: {usage_text}{flagged_text}"
    )


def _extract_substitutions(original: str, enriched: str) -> list[tuple[str, str]]:
    """Identify substituted phrases between the original and enriched text."""
    original_tokens = _TOKEN_PATTERN.findall(original)
    enriched_tokens = _TOKEN_PATTERN.findall(enriched)

    matcher = difflib.SequenceMatcher(
        a=[token.lower() for token in original_tokens],
        b=[token.lower() for token in enriched_tokens],
    )

    substitutions: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "replace":
            continue
        original_segment = " ".join(original_tokens[i1:i2]).strip()
        new_segment = " ".join(enriched_tokens[j1:j2]).strip()
        if original_segment and new_segment and original_segment != new_segment:
            substitutions.append((original_segment, new_segment))

    return substitutions
