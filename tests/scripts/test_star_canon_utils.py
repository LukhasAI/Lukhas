import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from star_canon_utils import extract_canon_labels, normalize_star_label  # noqa: E402


def test_extract_canon_labels_prefers_explicit_labels():
    payload = {
        "labels": ["Supporting", "🌊 Flow (Consciousness)"],
        "stars": [
            {"id": "Supporting", "emoji": "🔧", "domain": "Infrastructure/Utilities"},
            {"id": "Flow", "emoji": "🌊", "domain": "Consciousness"},
        ],
    }
    assert extract_canon_labels(payload) == ["Supporting", "🌊 Flow (Consciousness)"]


def test_extract_canon_labels_from_definitions():
    payload = {
        "stars": [
            {"id": "Anchor", "emoji": "⚓", "domain": "Core Infrastructure"},
            {"id": "Trail", "emoji": "✦", "domain": "Memory"},
        ]
    }
    labels = extract_canon_labels(payload)
    assert labels == [
        "⚓ Anchor (Core Infrastructure)",
        "✦ Trail (Memory)",
    ]


def test_normalize_star_label_with_alias():
    payload = {
        "labels": ["Supporting"],
        "aliases": {"🔧 Supporting (Infrastructure/Utilities)": "Supporting"},
    }
    assert normalize_star_label("🔧 Supporting (Infrastructure/Utilities)", payload) == "Supporting"
