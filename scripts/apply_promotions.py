#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

def load_json(p: Path): return json.loads(p.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser(description="Apply star promotions from CSV to manifests.")
    ap.add_argument("--csv", default="docs/audits/star_promotions.csv")
    ap.add_argument("--rules", default="configs/star_rules.json")
    ap.add_argument("--min-confidence", type=float, default=None, help="Override ruleset min_autopromote")
    ap.add_argument("--write", action="store_true", help="Actually write changes")
    ap.add_argument("--backup", action="store_true", help="Create .bak backup next to each manifest")
    args = ap.parse_args()

    rules = load_json(Path(args.rules))
    canonical = set(rules["canonical_stars"])
    deny = set(rules.get("deny", []))
    min_auto = args.min_confidence if args.min_confidence is not None else float(rules["confidence"]["min_autopromote"])

    applied = 0; skipped = 0; errors = 0

    with Path(args.csv).open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            file = Path(row["file"])
            target = row["suggested_star"].strip()
            conf = float(row.get("confidence", 0))
            reason = row.get("reason","")

            if target not in canonical:
                print(f"[SKIP] {file} → {target} not canonical")
                skipped += 1; continue
            if target in deny:
                print(f"[SKIP] {file} → {target} is denied")
                skipped += 1; continue
            if conf < min_auto:
                print(f"[SKIP] {file} → confidence {conf:.2f} < {min_auto:.2f}")
                skipped += 1; continue
            if not file.exists():
                print(f"[SKIP] missing file {file}")
                skipped += 1; continue

            try:
                d = load_json(file)
                align = d.setdefault("constellation_alignment", {})
                current = align.get("primary_star", "Supporting")
                if current == target:
                    print(f"[SKIP] {file} already {target}")
                    skipped += 1; continue
                print(f"[APPLY] {file}: {current} → {target} (conf={conf:.2f}; {reason})")
                align["primary_star"] = target

                meta = d.setdefault("metadata", {})
                tags = meta.setdefault("tags", [])
                if "autopromoted" not in tags:
                    tags.append("autopromoted")

                if args.write:
                    if args.backup:
                        # Backup original before modification
                        orig = json.loads(file.read_text(encoding="utf-8"))
                        Path(str(file)+".bak").write_text(json.dumps(orig, indent=2), encoding="utf-8")
                    file.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
                applied += 1
            except Exception as e:
                print(f"[ERR ] {file}: {e}")
                errors += 1

    print(f"\nSummary: applied={applied} skipped={skipped} errors={errors}")
    if errors: sys.exit(1)

if __name__ == "__main__":
    main()
