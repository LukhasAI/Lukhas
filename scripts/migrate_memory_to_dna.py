#!/usr/bin/env python3
"""
Backfill legacy memory into DNA Helix with checkpoints.
Idempotent by version; safe to resume.
"""

import argparse
import json
import time
from pathlib import Path

from dna.memory_inmem import (
    InMemoryHelix,
)

# replace with real DNA client when ready
from migration.legacy_jsonl import LegacyJSONL

CKPT_DIR = Path(".lukhas_migration")
CKPT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_FILE = CKPT_DIR / "checkpoint.json"


def load_ckpt():
    if CKPT_FILE.exists():
        try:
            return json.loads(CKPT_FILE.read_text("utf-8"))
        except Exception:
            return {}
    return {}


def save_ckpt(data):
    CKPT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy", default=".lukhas_legacy/memory.jsonl", help="Path to legacy JSONL")
    ap.add_argument("--limit", type=int, default=0, help="Max records (0=all)")
    args = ap.parse_args()

    legacy = LegacyJSONL(args.legacy)
    dna = InMemoryHelix()  # swap to your real Helix client

    ckpt = load_ckpt()
    start_after = ckpt.get("last_key")
    migrated = ckpt.get("migrated", 0)

    t0 = time.time()
    processed = 0
    last_key = start_after or ""
    for rec in legacy.iter_all(start_after=start_after):
        key = rec["key"]
        last_key = key
        dna.write(
            key,
            rec["value"],
            version=int(rec.get("version", 1)),
            strength=float(rec.get("strength", 0.5)),
            meta=rec.get("meta", {}),
        )
        processed += 1
        migrated += 1
        if args.limit and processed >= args.limit:
            break
        if processed % 500 == 0:
            save_ckpt(
                {
                    "last_key": last_key,
                    "migrated": migrated,
                    "ts": int(time.time() * 1000),
                }
            )
    save_ckpt(
        {
            "last_key": last_key,
            "migrated": migrated,
            "ts": int(time.time() * 1000),
        }
    )

    dt = int((time.time() - t0) * 1000)
    print(
        json.dumps(
            {
                "ok": True,
                "processed": processed,
                "migrated_total": migrated,
                "elapsed_ms": dt,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
