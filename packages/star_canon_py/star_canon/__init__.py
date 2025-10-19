import functools
import json
from importlib.resources import files
from typing import Dict, List

# ΛTAG: star_canon
def _derive_labels(payload: Dict[str, object]) -> List[str]:
    labels = payload.get("labels")
    if isinstance(labels, list):
        return [str(label) for label in labels]
    stars = payload.get("stars", [])
    if isinstance(stars, list) and stars and isinstance(stars[0], dict):
        derived: List[str] = []
        for entry in stars:
            emoji = str(entry.get("emoji", "")).strip()
            star_id = str(entry.get("id", "")).strip()
            domain = str(entry.get("domain", "")).strip()
            if domain:
                derived.append(f"{emoji} {star_id} ({domain})".strip())
            else:
                derived.append(f"{emoji} {star_id}".strip())
        payload["labels"] = derived
        return derived
    payload["labels"] = []
    return []


@functools.lru_cache()
def canon() -> Dict[str, object]:
    p = files(__package__) / "star_canon.json"
    data: Dict[str, object] = json.loads(p.read_text(encoding="utf-8"))
    _derive_labels(data)
    return data


def normalize(name: str) -> str:
    c = canon()
    labels = set(_derive_labels(c))
    aliases = c.get("aliases", {}) if isinstance(c, dict) else {}
    if name in labels:
        return name
    if isinstance(aliases, dict):
        return str(aliases.get(name, name))
    return name
