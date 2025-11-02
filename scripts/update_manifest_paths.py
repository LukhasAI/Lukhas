#!/usr/bin/env python3
"""
Update JSON manifest path strings safely.

Usage:
  python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/

Walks *.json under --root and rewrites any string values that contain the old prefix.
Skips non-JSON files and preserves formatting (via json.dumps with indent=2).

This is safer than sed because it:
- Only touches JSON files
- Preserves JSON structure
- Won't corrupt malformed paths
- Provides clear reporting
"""
import argparse
import json
import sys
from pathlib import Path


def iter_json_files(root: Path):
    """Yield all .json files under root directory."""
    for p in root.rglob("*.json"):
        yield p


def rewrite_json_strings(obj, old: str, new: str):
    """
    Recursively rewrite string values in JSON structure.

    Replaces all occurrences of 'old' with 'new' in string values.
    Preserves structure for dicts, lists, and other types.
    """
    if isinstance(obj, dict):
        return {k: rewrite_json_strings(v, old, new) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rewrite_json_strings(v, old, new) for v in obj]
    if isinstance(obj, str):
        return obj.replace(old, new)
    return obj


def main():
    ap = argparse.ArgumentParser(description="Update path strings in JSON manifest files")
    ap.add_argument("--root", required=True, help="Root directory to scan")
    ap.add_argument("--from", dest="old", required=True, help="Old path prefix")
    ap.add_argument("--to", dest="new", required=True, help="New path prefix")
    ap.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"❌ Error: Root directory not found: {root}", file=sys.stderr)
        return 2

    total, changed, errors = 0, 0, 0
    changed_files = []

    for jf in iter_json_files(root):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"⚠️  Skipping {jf}: {e}", file=sys.stderr)
            errors += 1
            continue

        new_data = rewrite_json_strings(data, args.old, args.new)
        total += 1

        if new_data != data:
            if args.dry_run:
                print(f"Would update: {jf}")
            else:
                jf.write_text(json.dumps(new_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"✏️  Updated: {jf}")
            changed += 1
            changed_files.append(str(jf))

    print()
    print("=" * 70)
    if args.dry_run:
        print("DRY RUN SUMMARY:")
    else:
        print("SUMMARY:")
    print(f"  Root:         {root}")
    print(f"  Pattern:      {args.old} → {args.new}")
    print(f"  Files scanned: {total}")
    print(f"  Files {'would be ' if args.dry_run else ''}updated:  {changed}")
    if errors:
        print(f"  Errors:       {errors}")
    print("=" * 70)

    if args.dry_run and changed > 0:
        print()
        print("🚀 Run without --dry-run to apply changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
