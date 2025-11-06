#!/usr/bin/env python3
"""T4/0.01% Module Documentation Scaffolder
Deterministic, idempotent, append-only ledger, dry-run by default.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(".")
LEDGER = ROOT / "manifests/.ledger/scaffold.ndjson"
TPL = ROOT / "templates/module"

REQUIRED = [
    "README.md",
    "claude.me",
    "lukhas_context.md",
    "CHANGELOG.md",
    "docs/ARCHITECTURE.md",
    "docs/API.md",
    "docs/GUIDES.md",
]


def load_manifest(p: Path) -> dict:
    """Load module.manifest.json with safe defaults."""
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        print(f"⚠️  Failed to parse {p}: {e}")
        return {}
    d.setdefault("module", p.parent.name)
    d.setdefault("description", "")
    d.setdefault("tags", [])
    d.setdefault("apis", {})
    d.setdefault("testing", {})
    d.setdefault("performance", {})
    return d


def render(s: str, ctx: dict) -> str:
    """Very simple mustache-ish replacer for {{key}}."""

    def sub(m):
        key = m.group(1).strip()
        return str(ctx.get(key, ""))

    return re.sub(r"{{\s*([^}]+)\s*}}", sub, s)


def write_if_missing(dst: Path, content: str, apply: bool) -> bool:
    """Write file only if it doesn't exist. Return True if created."""
    if dst.exists():
        return False
    if not apply:
        print(f"  ~ would create {dst}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return True


def append_ledger(rec: dict):
    """Append record to scaffold ledger (NDJSON)."""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Scaffold module documentation from templates"
    )
    ap.add_argument(
        "--module", help="single module folder (name or path)"
    )
    ap.add_argument(
        "--apply", action="store_true", help="write files (default: dry-run)"
    )
    ap.add_argument(
        "--verbose", "-v", action="store_true", help="verbose output"
    )
    args = ap.parse_args()

    # Discover targets
    targets = []
    if args.module:
        # Try as direct path first
        mdir = ROOT / args.module
        if not mdir.exists():
            # Try finding by name
            manifests = list(ROOT.rglob(f"{args.module}/module.manifest.json"))
            if manifests:
                mdir = manifests[0].parent
            else:
                print(f"❌ Module not found: {args.module}")
                return 1
        targets = [mdir]
    else:
        # All modules with manifests
        targets = sorted([p.parent for p in ROOT.rglob("module.manifest.json")])

    print(f"{'🔧 DRY-RUN' if not args.apply else '✅ APPLY'} mode")
    print(f"Found {len(targets)} module(s) to process\n")

    total_created = 0
    for mdir in targets:
        manifest_path = mdir / "module.manifest.json"
        if not manifest_path.exists():
            continue

        manifest = load_manifest(manifest_path)
        if not manifest:
            continue

        # Build context for template rendering
        module_name = manifest.get("module", mdir.name)
        ctx = {
            "module_title": module_name.replace(".", " ").replace("_", " ").title(),
            "module_fqn": module_name,
            "subtitle": manifest.get("description", "")[:80] or "Module documentation",
            "status": manifest.get("testing", {}).get("status", "stable"),
            "lane": next(
                (t.split(":")[1] for t in manifest.get("tags", []) if t.startswith("lane:")),
                "L2",
            ),
            "constellation": next(
                (
                    t.split(":")[1]
                    for t in manifest.get("tags", [])
                    if t.startswith("constellation:")
                ),
                "unknown",
            ),
            "tags_csv": ",".join(manifest.get("tags", [])[:6]),
            "one_sentence_purpose": (manifest.get("description", "")[:120] or "Purpose TBD."),
            "capability1": "Capability 1 (update from manifest)",
            "capability2": "Capability 2 (update from manifest)",
            "capability3": "Capability 3 (update from manifest)",
            "upstream_modules": "TBD",
            "downstream_modules": "TBD",
            "p95_target": manifest.get("performance", {})
            .get("sla_targets", {})
            .get("latency_p95_ms", "-"),
            "p95_observed": manifest.get("performance", {})
            .get("observed", {})
            .get("latency_p95_ms", "-"),
            "observed_at": manifest.get("performance", {})
            .get("observed", {})
            .get("observed_at", "-"),
            "coverage_target": manifest.get("testing", {}).get("coverage_target", "-"),
            "feature1": "Feature 1",
            "feature2": "Feature 2",
            "api_one": "API entrypoint",
            "event_names": "Event names",
        }

        created = []
        for rel in REQUIRED:
            tpl_path = TPL / rel
            if not tpl_path.exists():
                if args.verbose:
                    print(f"  ⚠️  Template missing: {tpl_path}")
                continue

            tpl_content = tpl_path.read_text(encoding="utf-8")
            out_content = render(tpl_content, ctx)

            if write_if_missing(mdir / rel, out_content, args.apply):
                created.append(rel)
                total_created += 1

        if created:
            if args.apply:
                append_ledger(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "module": module_name,
                        "created": created,
                    }
                )
            status = "✅" if args.apply else "~"
            print(f"{status} {mdir.name}: created {len(created)} files")
            if args.verbose:
                for f in created:
                    print(f"    + {f}")
        else:
            if args.verbose:
                print(f"= {mdir.name}: up-to-date")

    print(f"\n{'Would create' if not args.apply else 'Created'} {total_created} files")
    if not args.apply:
        print("💡 Run with --apply to write files")
    return 0


if __name__ == "__main__":
    exit(main())
