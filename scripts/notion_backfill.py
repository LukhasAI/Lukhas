#!/usr/bin/env python3
"""
T4/0.01% Notion Option Backfill
================================

Ensures the Notion database has multi-select options for:
  - Features (from vocab/features.json canonical keys)
  - Tags     (from vocab/tags.json 'allowed')  [optional]

Safe by default:
  - Dry-run unless --apply is passed
  - Appends missing options only (no deletions unless --prune is set)
  - Rate-limited calls
  - Append-only ledger of changes

Env:
  NOTION_TOKEN=<secret>
  NOTION_DATABASE_ID=<db_id>
  NOTION_RATE_LIMIT=3   # ops/sec (optional)

Usage:
  python scripts/notion_backfill.py --features --dry-run
  python scripts/notion_backfill.py --features --tags --apply
  python scripts/notion_backfill.py --features --prune   # removes orphans (careful)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    import requests
except ImportError:
    print("❌ requests not installed: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
VOCAB_FEATURES_PATH = ROOT / "vocab" / "features.json"
VOCAB_TAGS_PATH = ROOT / "vocab" / "tags.json"

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID", "")
NOTION_RATE_LIMIT = float(os.getenv("NOTION_RATE_LIMIT", "3"))

LEDGER = ROOT / "manifests" / ".ledger" / "notion_sync.ndjson"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# Notion color palette for stable hashing
NOTION_COLORS = [
    "default", "gray", "brown", "orange", "yellow",
    "green", "blue", "purple", "pink", "red"
]


def utcnow() -> str:
    """ISO 8601 timestamp with timezone"""
    return datetime.now(timezone.utc).isoformat()


def pick_color(name: str) -> str:
    """Stable color assignment via hash"""
    h = int(hashlib.sha1(name.encode()).hexdigest(), 16)
    return NOTION_COLORS[h % len(NOTION_COLORS)]


def rate_sleep(bucket: List[float]):
    """Simple leaky-bucket rate limiter"""
    now = time.time()
    bucket[:] = [t for t in bucket if now - t < 1.0]
    if len(bucket) >= NOTION_RATE_LIMIT:
        time.sleep(1.0 - (now - min(bucket)))
    bucket.append(time.time())


def append_ledger(rec: Dict[str, Any]):
    """Append record to ledger"""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps(rec) + "\n")


class NotionClient:
    """Rate-limited Notion API client"""

    def __init__(self, token: str, db_id: str):
        if not token or not db_id:
            raise SystemExit("❌ NOTION_TOKEN and NOTION_DATABASE_ID must be set")
        self.db_id = db_id
        self.bucket: List[float] = []

    def _get(self, url: str) -> Dict:
        """Rate-limited GET request"""
        rate_sleep(self.bucket)
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
        return r.json()

    def _patch(self, url: str, payload: Dict[str, Any]) -> Dict:
        """Rate-limited PATCH request"""
        rate_sleep(self.bucket)
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"PATCH {url} failed: {r.status_code} {r.text}")
        return r.json()

    def fetch_db(self) -> Dict:
        """Fetch database schema"""
        return self._get(f"https://api.notion.com/v1/databases/{self.db_id}")

    def update_db_properties(self, props: Dict[str, Any]) -> Dict:
        """Update database property schema"""
        payload = {"properties": props}
        return self._patch(
            f"https://api.notion.com/v1/databases/{self.db_id}",
            payload
        )


def get_multi_select_options(db: Dict, prop_name: str) -> List[Dict]:
    """Extract multi-select options from database schema"""
    props = db.get("properties", {})
    prop = props.get(prop_name)
    if not prop or prop.get("type") != "multi_select":
        return []
    return prop["multi_select"].get("options", [])


def extract_option_names(options: List[Dict]) -> List[str]:
    """Extract option names from Notion options list"""
    return [o["name"] for o in options]


def build_missing_options(current: List[str], desired: List[str]) -> List[Dict]:
    """Build list of options to add"""
    missing = [d for d in desired if d not in current]
    return [{"name": name, "color": pick_color(name)} for name in missing]


def build_prunable_options(current: List[str], desired: List[str]) -> List[str]:
    """Build list of option names to remove"""
    return [c for c in current if c not in desired]


def main():
    ap = argparse.ArgumentParser(
        description="Backfill Notion database multi-select options from controlled vocabulary"
    )
    ap.add_argument(
        "--features",
        action="store_true",
        help="Backfill 'Features' multi-select"
    )
    ap.add_argument(
        "--tags",
        action="store_true",
        help="Backfill 'Tags' multi-select (if present)"
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run)"
    )
    ap.add_argument(
        "--prune",
        action="store_true",
        help="Remove options not in vocab (DANGEROUS - use with caution)"
    )
    args = ap.parse_args()

    if not args.features and not args.tags:
        print("❌ Select at least one: --features and/or --tags")
        sys.exit(2)

    # Load vocabularies
    vocab_features = {}
    vocab_tags = set()

    if args.features:
        if not VOCAB_FEATURES_PATH.exists():
            print(f"❌ Features vocabulary not found: {VOCAB_FEATURES_PATH}")
            sys.exit(1)
        vocab_features = json.loads(VOCAB_FEATURES_PATH.read_text())

    if args.tags:
        if not VOCAB_TAGS_PATH.exists():
            print(f"❌ Tags vocabulary not found: {VOCAB_TAGS_PATH}")
            sys.exit(1)
        vocab_tags = set(json.loads(VOCAB_TAGS_PATH.read_text()).get("allowed", []))

    # Initialize client
    client = NotionClient(NOTION_TOKEN, NOTION_DB_ID)

    # Fetch database schema
    print("🔍 Fetching Notion database schema...")
    db = client.fetch_db()

    plan = []

    # Plan Features updates
    if args.features:
        desired = sorted(list(vocab_features.keys()))
        existing_opts = get_multi_select_options(db, "Features")
        existing = extract_option_names(existing_opts)
        to_add = build_missing_options(existing, desired)
        to_rm = build_prunable_options(existing, desired) if args.prune else []
        plan.append(("Features", to_add, to_rm, existing_opts))

    # Plan Tags updates
    if args.tags:
        desired = sorted(list(vocab_tags))
        existing_opts = get_multi_select_options(db, "Tags")
        if existing_opts or existing_opts == []:  # Property exists
            existing = extract_option_names(existing_opts)
            to_add = build_missing_options(existing, desired)
            to_rm = build_prunable_options(existing, desired) if args.prune else []
            plan.append(("Tags", to_add, to_rm, existing_opts))
        else:
            print("ℹ️  Notion DB has no 'Tags' multi-select property; skipping.")

    # Print plan
    for prop, adds, rms, _ in plan:
        print(f"\n=== {prop} ===")
        print(f"+ add: {len(adds)}")
        for a in adds[:25]:
            print(f"  + {a['name']}  ({a['color']})")
        if len(adds) > 25:
            print(f"  ... and {len(adds) - 25} more")

        if args.prune:
            print(f"- remove: {len(rms)}")
            for n in rms[:25]:
                print(f"  - {n}")
            if len(rms) > 25:
                print(f"  ... and {len(rms) - 25} more")

    if not args.apply:
        print("\nDRY-RUN: no changes applied.")
        for prop, adds, rms, _ in plan:
            append_ledger({
                "ts": utcnow(),
                "action": "notion-backfill-dryrun",
                "property": prop,
                "add_count": len(adds),
                "remove_count": len(rms)
            })
        return

    # Apply changes
    props_payload: Dict[str, Any] = {}

    for prop, adds, rms, existing_opts in plan:
        if not adds and not rms:
            continue

        # Build full options array (Notion requires complete replacement)
        ex_by_name = {o["name"]: o for o in existing_opts}

        # Add new options
        for a in adds:
            ex_by_name[a["name"]] = {"name": a["name"], "color": a["color"]}

        # Prune if requested
        if args.prune:
            for n in rms:
                ex_by_name.pop(n, None)

        props_payload[prop] = {
            "multi_select": {
                "options": list(ex_by_name.values())
            }
        }

    if not props_payload:
        print("\n✅ Nothing to apply - database is up to date.")
        return

    try:
        print("\n🔄 Updating Notion database properties...")
        client.update_db_properties(props_payload)

        append_ledger({
            "ts": utcnow(),
            "action": "notion-backfill-apply",
            "properties": list(props_payload.keys()),
            "status": "success",
            "total_options": sum(
                len(v["multi_select"]["options"])
                for v in props_payload.values()
            )
        })

        print("✅ Notion properties updated successfully.")

    except Exception as e:
        append_ledger({
            "ts": utcnow(),
            "action": "notion-backfill-apply",
            "status": "error",
            "error": str(e)
        })
        print(f"\n❌ Failed to update Notion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
