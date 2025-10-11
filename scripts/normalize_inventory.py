#!/usr/bin/env python3
"""
Normalize Module Inventory

Prepares COMPLETE_MODULE_INVENTORY.json for manifest generation by:
1. Renaming lucas/LUCAS → lukhas (legacy name cleanup)
2. Mapping lane → colony (schema v1.1.0 migration)
3. Applying star heuristics from generate_module_manifests.py

Exit 0: Normalization successful
Exit 1: Error during normalization
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "docs/audits/COMPLETE_MODULE_INVENTORY.json"
NORMALIZED_PATH = ROOT / "docs/audits/COMPLETE_MODULE_INVENTORY_normalized.json"

# Star inference rules (from generate_module_manifests.py)
STAR_HINTS = [
    (r"/consciousness/|/awareness/|/dream/|/oneiric/|/creativity/", "🌊 Flow (Consciousness)"),
    (r"/memory/|/rag/|/embeddings/|/kg/", "✦ Trail (Memory)"),
    (r"/identity/|/auth/|/oauth/|/oidc/|/lambda_id/", "⚛️ Anchor (Identity)"),
    (r"/guardian/|/policy/|/ethics/|/constitutional/", "🛡️ Watch (Guardian)"),
    (r"/vision/|/perception/|/visual/|/image/", "🔬 Horizon (Vision)"),
    (r"/bio/|/organic/|/adaptive/|/evolutionary/", "🌱 Living (Bio)"),
    (r"/quantum/|/superposition/|/entanglement/", "🔮 Oracle (Quantum)"),
    (r"/ethics/|/north/|/values/|/alignment/", "⚖️ North (Ethics)"),
    (r"/drift/|/dream/|/imagination/|/creative/", "🌙 Drift (Dream)"),
]

LANE_TO_COLONY = {
    "candidate": "research",
    "lukhas": "core",
    "core": "integration",
    "matriz": "cognitive",
    "products": "production",
}


def guess_star(path: str) -> str:
    """Guess primary star from path using heuristics."""
    for pattern, star in STAR_HINTS:
        if re.search(pattern, path, re.I):
            return star
    return "Supporting"


def normalize_name(name: str) -> str:
    """Normalize lucas/LUCAS to lukhas."""
    # Replace lucas/LUCAS variations
    name = re.sub(r"\blucas\b", "lukhas", name, flags=re.I)
    name = re.sub(r"\bLUCAS\b", "lukhas", name)
    return name


def normalize_entry(entry: dict) -> dict:
    """Normalize a single inventory entry."""
    normalized = entry.copy()

    # Normalize names
    if "fqn" in normalized:
        normalized["fqn"] = normalize_name(normalized["fqn"])
    if "path" in normalized:
        normalized["path"] = normalize_name(normalized["path"])

    # Map lane → colony
    if "lane" in normalized:
        lane = normalized["lane"]
        normalized["colony"] = LANE_TO_COLONY.get(lane, lane)
        # Keep lane for backward compatibility
        # del normalized["lane"]

    # Add star hint if missing
    if "star" not in normalized or normalized["star"] == "Supporting":
        path = normalized.get("path", "")
        normalized["star"] = guess_star(path)

    return normalized


def main():
    """Run inventory normalization."""
    print(f"🔧 Normalizing inventory: {INVENTORY_PATH.relative_to(ROOT)}")

    if not INVENTORY_PATH.exists():
        print(f"❌ ERROR: Inventory not found at {INVENTORY_PATH}")
        return 1

    # Load inventory
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Handle wrapped format (dict with "inventory" key) or raw list
    if isinstance(data, dict) and "inventory" in data:
        inventory = data["inventory"]
        metadata = {k: v for k, v in data.items() if k != "inventory"}
    elif isinstance(data, list):
        inventory = data
        metadata = {}
    else:
        print(f"❌ ERROR: Unexpected format: {type(data).__name__}")
        return 1

    print(f"📦 Loaded {len(inventory)} entries")

    # Normalize each entry
    normalized_inventory = [normalize_entry(entry) for entry in inventory]

    # Write normalized version (preserve metadata if present)
    output_data = metadata.copy() if metadata else {}
    output_data["inventory"] = normalized_inventory

    with open(NORMALIZED_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Wrote normalized inventory to {NORMALIZED_PATH.relative_to(ROOT)}")
    print(f"📊 Normalization stats:")
    print(f"   - Total entries: {len(normalized_inventory)}")

    # Count lucas → lukhas replacements
    lucas_count = sum(
        1 for e in inventory if "lucas" in e.get("fqn", "").lower() or "lucas" in e.get("path", "").lower()
    )
    if lucas_count:
        print(f"   - lucas/LUCAS → lukhas: {lucas_count} entries")

    # Count colony assignments
    colony_count = sum(1 for e in normalized_inventory if "colony" in e)
    print(f"   - Colony assignments: {colony_count}")

    # Count star assignments
    star_dist = {}
    for e in normalized_inventory:
        star = e.get("star", "Supporting")
        star_dist[star] = star_dist.get(star, 0) + 1

    print(f"   - Star distribution:")
    for star, count in sorted(star_dist.items(), key=lambda x: -x[1])[:5]:
        print(f"     • {star}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
