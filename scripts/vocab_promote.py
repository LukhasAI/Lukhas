#!/usr/bin/env python3
"""
T4/0.01% Vocabulary Promotion CLI
==================================

Promote unmapped feature phrases from review queue to controlled vocabulary.

Usage:
    # List queue
    python scripts/vocab_promote.py list

    # Create new canonical feature
    python scripts/vocab_promote.py promote "phenomenal pipeline" \\
        --canonical phenomenology.pipeline \\
        --category consciousness \\
        --matriz-stage thought

    # Add as synonym to existing feature
    python scripts/vocab_promote.py promote "temporal stability" \\
        --to temporal.coherence
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "vocab" / "features.json"
QUEUE = ROOT / "manifests" / "review_queue.json"
QUEUE_SCHEMA = ROOT / "schemas" / "review_queue.schema.json"


def load_json(p: Path) -> dict:
    """Load JSON file or return empty dict"""
    return json.loads(p.read_text()) if p.exists() else {}


def save_json(p: Path, data: dict):
    """Save JSON with deterministic formatting"""
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def ensure_unique_canonical(features: dict, canonical: str):
    """Verify canonical key doesn't already exist"""
    if canonical in features:
        print(f"❌ canonical '{canonical}' already exists")
        sys.exit(2)


def add_synonym(features: dict, canonical: str, synonym: str):
    """Add synonym to existing canonical feature"""
    if canonical not in features:
        print(f"❌ canonical '{canonical}' not found; create it first with --canonical")
        sys.exit(2)

    syns = features[canonical].setdefault("synonyms", [])
    if synonym in syns:
        print(f"↔️ synonym already present")
    else:
        syns.append(synonym)


def promote(args):
    """Promote a phrase from review queue to vocabulary"""
    features = load_json(FEATURES) or {}
    queue = load_json(QUEUE) or {"items": []}

    # Validate queue schema
    if QUEUE_SCHEMA.exists():
        validator = Draft202012Validator(json.loads(QUEUE_SCHEMA.read_text()))
        try:
            validator.validate(queue)
        except Exception as e:
            print(f"❌ review_queue invalid: {e}")
            sys.exit(2)

    # Find item (case-insensitive)
    items = queue.get("items", [])
    idx = {i["raw"].lower(): i for i in items}
    key = args.raw.strip().lower()

    if key not in idx:
        print(f"❌ '{args.raw}' not found in review_queue.json")
        sys.exit(1)

    item = idx[key]
    raw_norm = item["raw"].strip()

    if args.canonical:
        # Create new canonical feature
        canonical = args.canonical.strip()
        ensure_unique_canonical(features, canonical)

        features[canonical] = {
            "canonical": canonical,
            "synonyms": [raw_norm],
            "category": args.category or "uncategorized"
        }

        if args.constellation:
            features[canonical]["constellation"] = args.constellation

        if args.matriz_stage:
            features[canonical]["matriz_stage"] = args.matriz_stage

        print(f"✅ created canonical '{canonical}' with synonym '{raw_norm}'")
    else:
        # Add as synonym to existing canonical
        target = args.to.strip()
        if target not in features:
            print(f"❌ target canonical '{target}' not found")
            sys.exit(2)

        add_synonym(features, target, raw_norm)
        print(f"✅ added synonym '{raw_norm}' → '{target}'")

    # Remove item from queue (it's resolved)
    queue["items"] = [i for i in items if i is not item]
    queue["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Write changes
    save_json(FEATURES, features)
    save_json(QUEUE, queue)


def list_queue(args):
    """List all items in review queue"""
    queue = load_json(QUEUE) or {"items": []}

    # Validate queue schema
    if QUEUE_SCHEMA.exists():
        validator = Draft202012Validator(json.loads(QUEUE_SCHEMA.read_text()))
        try:
            validator.validate(queue)
        except Exception as e:
            print(f"❌ review_queue invalid: {e}")
            sys.exit(2)

    if not queue["items"]:
        print("🎉 review_queue is empty")
        return

    # Sort by count desc, last_seen desc
    items = sorted(
        queue["items"],
        key=lambda i: (i.get("count", 1), i.get("last_seen", "")),
        reverse=True
    )

    print(f"📋 Review Queue ({len(items)} items):\n")
    for i in items:
        print(f"- {i['raw']}")
        print(f"  count:{i['count']}  source:{i['source']}  module:{i['module']}")
        if i.get("last_seen"):
            print(f"  last:{i['last_seen']}")
        print()


def main():
    ap = argparse.ArgumentParser(
        description="Promote unmapped features to controlled vocabulary"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # list command
    ls = sub.add_parser("list", help="List review queue")
    ls.set_defaults(func=list_queue)

    # promote command
    pr = sub.add_parser("promote", help="Promote a raw phrase")
    g = pr.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--canonical",
        help="Create a new canonical key (e.g., memory.convergence)"
    )
    g.add_argument(
        "--to",
        help="Add as synonym to existing canonical key"
    )
    pr.add_argument("raw", help="Exact raw phrase as seen in review_queue")
    pr.add_argument("--category", help="Category for new canonical", default=None)
    pr.add_argument("--constellation", help="Optional constellation tag", default=None)
    pr.add_argument(
        "--matriz-stage",
        help="Optional matriz stage",
        dest="matriz_stage",
        default=None
    )
    pr.set_defaults(func=promote)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
