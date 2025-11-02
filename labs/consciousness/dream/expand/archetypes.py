"""
Archetypal Mesh: map dream snapshots to archetypes.
"""

ARCHETYPES = ["Hero", "Shadow", "Trickster"]


def tag(snapshot: dict) -> list[str]:
    return ["Hero"] if snapshot.get("confidence", 0) > 0.5 else ["Shadow"]


def mesh(dreams: list[dict]) -> str:
    return "clash" if any("Hero" in tag(d) for d in dreams) and any("Shadow" in tag(d) for d in dreams) else "harmony"
