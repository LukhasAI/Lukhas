#!/usr/bin/env python3
"""
T4/0.01% Bulk Vocabulary Promotion CLI
========================================

Bulk promote unmapped phrases from review queue to controlled vocabulary.

Supports JSON and CSV mapping files for batch processing.

Usage:
    # Dry run (show what would change)
    python scripts/vocab_bulk_promote.py vocab/promotions.json --dry-run
    python scripts/vocab_bulk_promote.py vocab/promotions.csv --dry-run

    # Apply changes
    python scripts/vocab_bulk_promote.py vocab/promotions.json

    # Allow creating canonicals even if not in queue (use with care)
    python scripts/vocab_bulk_promote.py vocab/promotions.csv --create-missing

JSON format (vocab/promotions.json):
{
  "items": [
    {
      "raw": "temporal stability",
      "to": "temporal.coherence"
    },
    {
      "raw": "phenomenal pipeline",
      "canonical": "phenomenology.pipeline",
      "category": "consciousness",
      "matriz_stage": "thought"
    }
  ]
}

CSV format (vocab/promotions.csv):
Headers: raw,to,canonical,category,constellation,matriz_stage
temporal stability,temporal.coherence,,,,
phenomenal pipeline,,phenomenology.pipeline,consciousness,,thought
"""

from __future__ import annotations
import argparse
import csv
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


def save_json(p: Path, obj: dict):
    """Save JSON with deterministic formatting"""
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def load_mapping(path: Path) -> list[dict]:
    """Load mapping file (JSON or CSV)"""
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text())
        return data.get("items", []) if isinstance(data, dict) else data

    if path.suffix.lower() == ".csv":
        rows = []
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.append({k: (v.strip() if v is not None else "") for k, v in r.items()})
        return rows

    raise SystemExit(f"❌ Unsupported mapping format: {path.suffix}")


def validate_row(row: dict, i: int):
    """Validate single mapping row"""
    raw = (row.get("raw") or "").strip()
    to = (row.get("to") or "").strip()
    canonical = (row.get("canonical") or "").strip()

    if not raw:
        raise ValueError(f"[row {i}] missing 'raw'")

    if bool(to) == bool(canonical):
        raise ValueError(f"[row {i}] must specify exactly one of 'to' or 'canonical'")

    return raw, to, canonical


def main():
    ap = argparse.ArgumentParser(
        description="Bulk promote review_queue items to controlled vocabulary"
    )
    ap.add_argument(
        "mapping",
        type=str,
        help="JSON or CSV mapping file"
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write any files"
    )
    ap.add_argument(
        "--create-missing",
        action="store_true",
        help="Allow creation even if 'raw' is not in review_queue (use with care)"
    )
    ap.add_argument(
        "--report",
        choices=["md"],
        help="Generate report format (md for Markdown PR changelog)"
    )
    ap.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate mapping file without writing changes"
    )
    args = ap.parse_args()

    # Load existing data
    features = load_json(FEATURES) or {}
    queue = load_json(QUEUE) or {"items": []}

    # Validate queue
    if QUEUE_SCHEMA.exists():
        validator = Draft202012Validator(json.loads(QUEUE_SCHEMA.read_text()))
        try:
            validator.validate(queue)
        except Exception as e:
            print(f"❌ review_queue invalid: {e}")
            sys.exit(2)

    qitems = {i["raw"].lower(): i for i in queue.get("items", [])}
    mapping = load_mapping(Path(args.mapping))

    report = {
        "created": [],
        "synonym_added": [],
        "skipped": [],
        "errors": []
    }

    # Process each row
    for idx, row in enumerate(mapping, start=1):
        try:
            raw, to, canonical = validate_row(row, idx)
            key = raw.lower()

            # Check presence in queue (unless overridden)
            if key not in qitems and not args.create_missing:
                report["skipped"].append({
                    "raw": raw,
                    "reason": "not_in_review_queue"
                })
                continue

            if canonical:
                # Create new canonical or add synonym
                if canonical in features:
                    # Canonical already exists - add 'raw' as synonym if missing
                    syns = features[canonical].setdefault("synonyms", [])
                    if raw in syns:
                        report["skipped"].append({
                            "raw": raw,
                            "canonical": canonical,
                            "reason": "synonym_exists"
                        })
                    else:
                        syns.append(raw)
                        report["synonym_added"].append({
                            "raw": raw,
                            "canonical": canonical
                        })
                else:
                    # Create new canonical
                    features[canonical] = {
                        "canonical": canonical,
                        "synonyms": [raw],
                        "category": (row.get("category") or "uncategorized")
                    }
                    if row.get("constellation"):
                        features[canonical]["constellation"] = row["constellation"]
                    if row.get("matriz_stage"):
                        features[canonical]["matriz_stage"] = row["matriz_stage"]
                    report["created"].append({
                        "canonical": canonical,
                        "raw": raw
                    })
            else:
                # Add as synonym to existing canonical
                target = to
                if target not in features:
                    report["errors"].append({
                        "raw": raw,
                        "to": target,
                        "error": "target_canonical_missing"
                    })
                    continue

                syns = features[target].setdefault("synonyms", [])
                if raw in syns:
                    report["skipped"].append({
                        "raw": raw,
                        "to": target,
                        "reason": "synonym_exists"
                    })
                else:
                    syns.append(raw)
                    report["synonym_added"].append({
                        "raw": raw,
                        "to": target
                    })

            # Remove from queue if present
            if key in qitems:
                queue["items"] = [i for i in queue["items"] if i["raw"].lower() != key]
                qitems.pop(key, None)

        except Exception as e:
            report["errors"].append({
                "row": idx,
                "error": str(e)
            })

    # Validate-only mode - check and exit
    if args.validate_only:
        print("=== Validation Report ===\n")
        print(f"Rows validated: {len(mapping)}")
        print(f"Would create canonicals: {len(report['created'])}")
        print(f"Would add synonyms: {len(report['synonym_added'])}")
        print(f"Would skip: {len(report['skipped'])}")
        print(f"Errors: {len(report['errors'])}")

        if report["errors"]:
            print("\n❌ Validation Errors:")
            for err in report["errors"]:
                print(f"  Row {err.get('row', '?')}: {err.get('error', 'unknown')}")
            sys.exit(1)

        print("\n✅ Mapping file is valid")
        sys.exit(0)

    # Dry run - show report and exit
    if args.dry_run:
        print("=== Dry Run Report ===\n")
        print(json.dumps(report, indent=2))
        print("\nDRY-RUN: no files written")
        sys.exit(0)

    # Write changes
    queue["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_json(FEATURES, features)
    save_json(QUEUE, queue)

    # Summary
    print("=== Bulk Promote Summary ===")
    print(f"Created canonicals  : {len(report['created'])}")
    print(f"Synonyms added      : {len(report['synonym_added'])}")
    print(f"Skipped             : {len(report['skipped'])}")
    print(f"Errors              : {len(report['errors'])}")

    if report["errors"]:
        print("\n❌ Errors:")
        print(json.dumps(report["errors"], indent=2))

    if report["created"]:
        print("\n✅ Created canonicals:")
        for item in report["created"]:
            print(f"  {item['canonical']} <- {item['raw']}")

    if report["synonym_added"]:
        print("\n↔️ Added synonyms:")
        for item in report["synonym_added"]:
            target = item.get("canonical") or item.get("to")
            print(f"  {target} <- {item['raw']}")

    # Generate Markdown report if requested
    if args.report == "md":
        reports_dir = ROOT / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        md_lines = [
            "# 📑 Vocabulary Promotion Report",
            f"_Generated {datetime.now(timezone.utc).isoformat()}_",
            "",
            "## Summary",
            f"- **Created canonicals**: {len(report['created'])}",
            f"- **Synonyms added**: {len(report['synonym_added'])}",
            f"- **Skipped**: {len(report['skipped'])}",
            f"- **Errors**: {len(report['errors'])}",
            ""
        ]

        if report["created"]:
            md_lines.append("## New Canonical Features")
            md_lines.append("")
            for item in report["created"]:
                md_lines.append(f"- **`{item['canonical']}`**")
                md_lines.append(f"  - Synonym: \"{item['raw']}\"")

        if report["synonym_added"]:
            md_lines.append("")
            md_lines.append("## Synonyms Added")
            md_lines.append("")
            for item in report["synonym_added"]:
                target = item.get("canonical") or item.get("to")
                md_lines.append(f"- \"{item['raw']}\" → `{target}`")

        if report["errors"]:
            md_lines.append("")
            md_lines.append("## Errors")
            md_lines.append("")
            for err in report["errors"]:
                md_lines.append(f"- Row {err.get('row', '?')}: {err.get('error', 'unknown')}")

        # Queue status
        remaining = len(queue.get("items", []))
        md_lines.extend([
            "",
            "## Review Queue Status",
            f"- **Remaining items**: {remaining}",
            f"- **Last updated**: {queue.get('updated_at', 'unknown')}"
        ])

        report_path = reports_dir / "vocab_promotion_report.md"
        report_path.write_text("\n".join(md_lines))
        print(f"\n✅ Wrote {report_path}")


if __name__ == "__main__":
    main()
