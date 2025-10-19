"""Utilities for working with Constellation star canon metadata."""
from __future__ import annotations

from typing import Dict, Iterable, List

# ΛTAG: star_canon
_DEF_KEYS = ("id", "emoji", "domain")


def _derive_label(entry: Dict[str, str]) -> str:
    """Construct the canonical label string from a star definition entry."""
    emoji = (entry.get("emoji") or "").strip()
    star_id = (entry.get("id") or "").strip()
    domain = (entry.get("domain") or "").strip()
    if domain:
        return f"{emoji} {star_id} ({domain})".strip()
    return f"{emoji} {star_id}".strip()


def extract_canon_labels(canon: Dict[str, object]) -> List[str]:
    """Return normalized label strings from a star canon payload."""
    labels = canon.get("labels")
    if isinstance(labels, list):
        return [str(label) for label in labels]
    stars = canon.get("stars", [])
    if isinstance(stars, list) and stars and isinstance(stars[0], dict):
        return [_derive_label(entry) for entry in stars]
    return []


def normalize_star_label(name: str, canon: Dict[str, object]) -> str:
    """Normalize a star name using canon labels and aliases."""
    if not name:
        return name
    labels = set(extract_canon_labels(canon))
    if name in labels:
        return name
    aliases = canon.get("aliases", {})
    if isinstance(aliases, dict):
        return str(aliases.get(name, name))
    return name


def iter_star_definitions(canon: Dict[str, object]) -> Iterable[Dict[str, str]]:
    """Yield structured star definitions if present."""
    stars = canon.get("stars", [])
    if isinstance(stars, list):
        for entry in stars:
            if isinstance(entry, dict) and all(key in entry for key in _DEF_KEYS):
                yield entry

